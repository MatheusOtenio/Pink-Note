from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from presentation.components.base_component import BaseComponent
from shared.utils.string_utils import StringUtils

class NoteListComponent(BaseComponent):
    """Component for displaying and managing a list of notes."""
    
    # Define signals
    note_selected = pyqtSignal(int)  # Emitted when a note is selected (note_id)
    note_deleted = pyqtSignal(int)   # Emitted when a note is deleted (note_id)
    note_moved = pyqtSignal(int, int)  # Emitted when a note is moved (note_id, target_folder_id)
    
    def __init__(self, parent=None, controllers=None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent, controllers)
        
        # Current folder ID
        self.current_folder_id = None
        
        # Notes data
        self.notes = []
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Create list widget
        self.list_widget = QListWidget(self)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Set up layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect list widget signals
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_folder(self, folder_id: int):
        """Set the current folder and load its notes.
        
        Args:
            folder_id: The folder ID
        """
        self.current_folder_id = folder_id
        self.refresh()
    
    def refresh(self):
        """Refresh the notes list."""
        if self.current_folder_id is None:
            return
        
        # Clear the list
        self.list_widget.clear()
        
        # Get notes for the current folder
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            self.notes = note_controller.get_notes_by_folder(self.current_folder_id)
            
            # Add notes to the list
            for note in self.notes:
                self._add_note_to_list(note)
    
    def _add_note_to_list(self, note: Dict[str, Any]):
        """Add a note to the list widget.
        
        Args:
            note: The note data
        """
        # Create list item
        item = QListWidgetItem(note['title'])
        item.setData(Qt.UserRole, note['id'])  # Store note ID as user data
        
        # Add a tooltip with a preview of the content
        if note['content']:
            preview = StringUtils.truncate(note['content'], 100)
            item.setToolTip(preview)
        
        # Add item to the list
        self.list_widget.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click event.
        
        Args:
            item: The clicked item
        """
        note_id = item.data(Qt.UserRole)
        self.note_selected.emit(note_id)
    
    def _show_context_menu(self, position):
        """Show context menu for the list item at the given position.
        
        Args:
            position: The position where to show the menu
        """
        # Get the item at the position
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        # Get the note ID
        note_id = item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_note(note_id))
        menu.addAction(delete_action)
        
        # Add move to folder submenu
        move_menu = menu.addMenu("Move to")
        self._populate_move_menu(move_menu, note_id)
        
        # Show the menu
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _populate_move_menu(self, menu: QMenu, note_id: int):
        """Populate the move to folder submenu.
        
        Args:
            menu: The menu to populate
            note_id: The note ID
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Get all folders
        folders = folder_controller.get_all_folders()
        
        # Add folder actions
        for folder in folders:
            # Skip the current folder
            if folder['id'] == self.current_folder_id:
                continue
            
            action = QAction(folder['name'], self)
            action.triggered.connect(lambda checked=False, fid=folder['id']: self._move_note(note_id, fid))
            menu.addAction(action)
    
    def _delete_note(self, note_id: int):
        """Delete a note.
        
        Args:
            note_id: The note ID
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            note_controller = self.controllers.get('note_controller')
            if note_controller and note_controller.delete_note(note_id):
                # Remove the note from the list
                for i in range(self.list_widget.count()):
                    item = self.list_widget.item(i)
                    if item.data(Qt.UserRole) == note_id:
                        self.list_widget.takeItem(i)
                        break
                
                # Emit signal
                self.note_deleted.emit(note_id)
    
    def _move_note(self, note_id: int, target_folder_id: int):
        """Move a note to a different folder.
        
        Args:
            note_id: The note ID
            target_folder_id: The target folder ID
        """
        note_controller = self.controllers.get('note_controller')
        if note_controller and note_controller.move_note(note_id, target_folder_id):
            # Remove the note from the list
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.UserRole) == note_id:
                    self.list_widget.takeItem(i)
                    break
            
            # Emit signal
            self.note_moved.emit(note_id, target_folder_id)
    
    def select_note(self, note_id: int):
        """Select a note in the list.
        
        Args:
            note_id: The note ID
        """
        # Find the item with the given note ID
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == note_id:
                self.list_widget.setCurrentItem(item)
                break