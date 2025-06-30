from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
                             QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
import os
import datetime

from presentation.components.base_component import BaseComponent
from shared.constants import SUPPORTED_ATTACHMENT_EXTENSIONS

class NoteEditorComponent(BaseComponent):
    """Component for editing notes and managing attachments."""
    
    # Define signals
    note_saved = pyqtSignal(int)  # Emitted when a note is saved (note_id)
    note_deleted = pyqtSignal(int)  # Emitted when a note is deleted (note_id)
    
    def __init__(self, parent=None, controllers=None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent, controllers)
        
        # Current note data
        self.current_note = None
        self.current_folder_id = None
        self.is_new_note = False
        self.attachments = []
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title input
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Note Title")
        self.title_input.setStyleSheet("font-size: 16px; padding: 5px;")
        main_layout.addWidget(self.title_input)
        
        # Content editor
        self.content_editor = QTextEdit(self)
        self.content_editor.setPlaceholderText("Write your note here...")
        self.content_editor.setStyleSheet("font-size: 14px; padding: 5px;")
        main_layout.addWidget(self.content_editor)
        
        # Attachments section
        attachment_layout = QVBoxLayout()
        
        # Attachments header
        attachment_header = QHBoxLayout()
        attachment_label = QLabel("Attachments", self)
        attachment_label.setStyleSheet("font-weight: bold;")
        attachment_header.addWidget(attachment_label)
        
        # Add attachment button
        self.add_attachment_btn = QPushButton("Add File", self)
        attachment_header.addWidget(self.add_attachment_btn)
        attachment_header.addStretch()
        attachment_layout.addLayout(attachment_header)
        
        # Attachments list
        self.attachments_list = QListWidget(self)
        self.attachments_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.attachments_list.setMaximumHeight(100)
        attachment_layout.addWidget(self.attachments_list)
        
        main_layout.addLayout(attachment_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setStyleSheet("padding: 5px 15px;")
        buttons_layout.addWidget(self.save_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.setStyleSheet("padding: 5px 15px;")
        buttons_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Status label
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # Set initial state
        self.clear_editor()
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect buttons
        self.save_btn.clicked.connect(self._save_note)
        self.delete_btn.clicked.connect(self._delete_note)
        self.add_attachment_btn.clicked.connect(self._add_attachment)
        
        # Connect attachment list signals
        self.attachments_list.itemDoubleClicked.connect(self._open_attachment)
        self.attachments_list.customContextMenuRequested.connect(self._show_attachment_context_menu)
        
        # Connect editor signals for auto-save functionality
        self.title_input.textChanged.connect(self._update_status)
        self.content_editor.textChanged.connect(self._update_status)
    
    def set_folder(self, folder_id: int):
        """Set the current folder ID.
        
        Args:
            folder_id: The folder ID
        """
        self.current_folder_id = folder_id
    
    def load_note(self, note_id: int):
        """Load a note into the editor.
        
        Args:
            note_id: The note ID
        """
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        # Get the note
        note = note_controller.get_note_by_id(note_id)
        if not note:
            return
        
        # Set the current note
        self.current_note = note
        self.is_new_note = False
        
        # Update UI
        self.title_input.setText(note.get('title', ''))
        self.content_editor.setText(note.get('content', ''))
        self.delete_btn.setEnabled(True)
        
        # Load attachments
        self._load_attachments(note_id)
        
        # Update status
        self._update_status()
    
    def new_note(self):
        """Create a new note in the editor."""
        # Clear the editor
        self.clear_editor()
        
        # Set as new note
        self.is_new_note = True
        self.current_note = None
        
        # Enable editing
        self.title_input.setEnabled(True)
        self.content_editor.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(False)
        
        # Set focus to title
        self.title_input.setFocus()
        
        # Update status
        self._update_status()
    
    def clear_editor(self):
        """Clear the editor."""
        # Clear inputs
        self.title_input.clear()
        self.content_editor.clear()
        self.attachments_list.clear()
        
        # Disable editing
        self.title_input.setEnabled(False)
        self.content_editor.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.add_attachment_btn.setEnabled(False)
        
        # Clear current note
        self.current_note = None
        self.is_new_note = False
        self.attachments = []
        
        # Update status
        self.status_label.setText("No note selected")
    
    def _save_note(self):
        """Save the current note."""
        # Get note data
        title = self.title_input.text().strip()
        content = self.content_editor.toPlainText()
        
        # Validate title
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title for the note.")
            self.title_input.setFocus()
            return
        
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        # Save note
        if self.is_new_note:
            # Create new note
            if self.current_folder_id is None:
                QMessageBox.warning(self, "No Folder Selected", "Please select a folder for the note.")
                return
            
            note = note_controller.create_note(
                title=title,
                content=content,
                folder_id=self.current_folder_id
            )
            
            if note:
                self.current_note = note
                self.is_new_note = False
                self.delete_btn.setEnabled(True)
                self.add_attachment_btn.setEnabled(True)
                
                # Emit signal
                self.note_saved.emit(note['id'])
        else:
            # Update existing note
            # Make sure current_note is a dictionary and has an id
            if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
                # If current_note is invalid, create a new note instead
                if self.current_folder_id is None:
                    QMessageBox.warning(self, "No Folder Selected", "Please select a folder for the note.")
                    return
                
                note = note_controller.create_note(
                    title=title,
                    content=content,
                    folder_id=self.current_folder_id
                )
                
                if note:
                    self.current_note = note
                    self.is_new_note = False
                    self.delete_btn.setEnabled(True)
                    self.add_attachment_btn.setEnabled(True)
                    
                    # Emit signal
                    self.note_saved.emit(note['id'])
            else:
                # Update the existing note
                note = note_controller.update_note(
                    note_id=self.current_note['id'],
                    title=title,
                    content=content
                )
                
                if note:
                    self.current_note = note
                    
                    # Emit signal
                    self.note_saved.emit(note['id'])
        
        # Update status
        self._update_status(saved=True)
    
    def _delete_note(self):
        """Delete the current note."""
        if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this note? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            note_controller = self.controllers.get('note_controller')
            if note_controller:
                note_id = self.current_note['id']
                if note_controller.delete_note(note_id):
                    # Clear the editor
                    self.clear_editor()
                    
                    # Emit signal
                    self.note_deleted.emit(note_id)
    
    def _load_attachments(self, note_id: int):
        """Load attachments for a note.
        
        Args:
            note_id: The note ID
        """
        attachment_controller = self.controllers.get('attachment_controller')
        if not attachment_controller:
            return
        
        # Clear the list
        self.attachments_list.clear()
        
        # Get attachments
        self.attachments = attachment_controller.get_attachments_for_note(note_id)
        
        # Add to list
        for attachment in self.attachments:
            item = QListWidgetItem(attachment.get('file_name', 'Unnamed Attachment'))
            item.setData(Qt.UserRole, attachment['id'])
            self.attachments_list.addItem(item)
        
        # Enable add attachment button
        self.add_attachment_btn.setEnabled(True)
    
    def _add_attachment(self):
        """Add an attachment to the current note."""
        if not self.current_note or not isinstance(self.current_note, dict) or 'id' not in self.current_note:
            return
        
        # Create filter string for file dialog
        filter_str = "All Files (*.*);;"
        # Create a filter for supported attachments
        ext_list = " ".join(f"*.{ext.lstrip('.')}" for ext in SUPPORTED_ATTACHMENT_EXTENSIONS)
        filter_str += f"Supported Files ({ext_list});;"
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Attachment",
            "",
            filter_str
        )
        
        if file_path and os.path.exists(file_path):
            attachment_controller = self.controllers.get('attachment_controller')
            if attachment_controller:
                # Add attachment
                attachment = attachment_controller.add_attachment(
                    note_id=self.current_note['id'],
                    file_path=file_path
                )
                
                if attachment:
                    # Add to list
                    item = QListWidgetItem(attachment.get('file_name', 'Unnamed Attachment'))
                    item.setData(Qt.UserRole, attachment['id'])
                    self.attachments_list.addItem(item)
                    
                    # Update attachments list
                    self.attachments.append(attachment)
    
    def _open_attachment(self, item: QListWidgetItem):
        """Open an attachment.
        
        Args:
            item: The list item representing the attachment
        """
        attachment_id = item.data(Qt.UserRole)
        attachment_controller = self.controllers.get('attachment_controller')
        if attachment_controller:
            attachment_controller.open_attachment(attachment_id)
    
    def _show_attachment_context_menu(self, position):
        """Show context menu for the attachment at the given position.
        
        Args:
            position: The position where to show the menu
        """
        # Get the item at the position
        item = self.attachments_list.itemAt(position)
        if not item:
            return
        
        # Get the attachment ID
        attachment_id = item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self._open_attachment(item))
        menu.addAction(open_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_attachment(attachment_id))
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(self.attachments_list.mapToGlobal(position))
    
    def _delete_attachment(self, attachment_id: int):
        """Delete an attachment.
        
        Args:
            attachment_id: The attachment ID
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this attachment? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            attachment_controller = self.controllers.get('attachment_controller')
            if attachment_controller and attachment_controller.delete_attachment(attachment_id):
                # Remove from list
                for i in range(self.attachments_list.count()):
                    item = self.attachments_list.item(i)
                    if item.data(Qt.UserRole) == attachment_id:
                        self.attachments_list.takeItem(i)
                        break
                
                # Update attachments list
                self.attachments = [a for a in self.attachments if a['id'] != attachment_id]
    
    def _update_status(self, saved=False):
        """Update the status label.
        
        Args:
            saved: Whether the note was just saved
        """
        if self.current_note:
            if saved:
                self.status_label.setText(f"Saved at {datetime.datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_label.setText("Editing note")
        elif self.is_new_note:
            self.status_label.setText("Creating new note")
        else:
            self.status_label.setText("No note selected")