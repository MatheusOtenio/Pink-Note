from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QPushButton, QToolBar, 
                             QAction, QStatusBar, QMessageBox, QMenu, QDialog,
                             QLabel, QLineEdit, QFormLayout, QDialogButtonBox,
                             QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence
import os
import sys

from presentation.components import (
    NoteListComponent, FolderTreeComponent, NoteEditorComponent,
    CalendarComponent, SearchComponent
)
from shared.di import Container
from shared.config import Config
from shared.utils.logger import Logger
from shared.constants import APP_NAME, APP_VERSION

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None, config=None):
        """Initialize the dialog.
        
        Args:
            parent: The parent widget
            config: The application configuration
        """
        super().__init__(parent)
        
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Set dialog properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Database path input
        self.db_path_input = QLineEdit(self)
        self.db_path_input.setText(self.config.get('database_path'))
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_input)
        db_path_btn = QPushButton("Browse", self)
        db_path_btn.clicked.connect(self._browse_db_path)
        db_path_layout.addWidget(db_path_btn)
        form_layout.addRow("Database Path:", db_path_layout)
        
        # Storage path input
        self.storage_path_input = QLineEdit(self)
        self.storage_path_input.setText(self.config.get('storage_path'))
        storage_path_layout = QHBoxLayout()
        storage_path_layout.addWidget(self.storage_path_input)
        storage_path_btn = QPushButton("Browse", self)
        storage_path_btn.clicked.connect(self._browse_storage_path)
        storage_path_layout.addWidget(storage_path_btn)
        form_layout.addRow("Storage Path:", storage_path_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _browse_db_path(self):
        """Browse for database path."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Database File",
            self.db_path_input.text(),
            "SQLite Database (*.db);;All Files (*.*)"
        )
        
        if path:
            self.db_path_input.setText(path)
    
    def _browse_storage_path(self):
        """Browse for storage path."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Storage Directory",
            self.storage_path_input.text()
        )
        
        if path:
            self.storage_path_input.setText(path)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get the settings from the dialog inputs.
        
        Returns:
            A dictionary with the settings
        """
        return {
            'database_path': self.db_path_input.text(),
            'storage_path': self.storage_path_input.text()
        }

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize logger
        self.logger = Logger.get_instance()
        self.logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Load configuration
        self.config = Config()
        self.config.load()
        
        # Initialize dependency container
        self.container = Container(self.config.get_all())
        
        # Initialize controllers
        self.controllers = {
            'note_controller': self.container.get_note_controller(),
            'folder_controller': self.container.get_folder_controller(),
            'event_controller': self.container.get_event_controller(),
            'attachment_controller': self.container.get_attachment_controller()
        }
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Refresh components
        self.refresh_all()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 600)
        
        # Create central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create left panel (folders and notes)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create folder tree
        self.folder_tree = FolderTreeComponent(controllers=self.controllers)
        left_layout.addWidget(self.folder_tree)
        
        # Create note list
        self.note_list = NoteListComponent(controllers=self.controllers)
        left_layout.addWidget(self.note_list)
        
        # Add left panel to splitter
        self.main_splitter.addWidget(left_panel)
        
        # Create right panel (tabs)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)
        
        # Create note editor tab
        self.note_editor = NoteEditorComponent(controllers=self.controllers)
        self.tabs.addTab(self.note_editor, "Note")
        
        # Create calendar tab
        self.calendar = CalendarComponent(controllers=self.controllers)
        self.tabs.addTab(self.calendar, "Calendar")
        
        # Create search tab
        self.search = SearchComponent(controllers=self.controllers)
        self.tabs.addTab(self.search, "Search")
        
        # Add right panel to splitter
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter sizes
        self.main_splitter.setSizes([300, 700])
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_toolbar(self):
        """Create the application toolbar."""
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # New note action
        new_note_action = QAction("New Note", self)
        new_note_action.setShortcut(QKeySequence.New)
        new_note_action.triggered.connect(self.new_note)
        toolbar.addAction(new_note_action)
        
        # New folder action
        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(self.new_folder)
        toolbar.addAction(new_folder_action)
        
        toolbar.addSeparator()
        
        # New event action
        new_event_action = QAction("New Event", self)
        new_event_action.triggered.connect(self.new_event)
        toolbar.addAction(new_event_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def connect_signals(self):
        """Connect component signals."""
        # Connect folder tree signals
        self.folder_tree.folder_selected.connect(self.on_folder_selected)
        
        # Connect note list signals
        self.note_list.note_selected.connect(self.on_note_selected)
        
        # Connect note editor signals
        self.note_editor.note_saved.connect(self.on_note_saved)
        self.note_editor.note_deleted.connect(self.on_note_deleted)
        
        # Connect search signals
        self.search.note_selected.connect(self.on_search_note_selected)
    
    def refresh_all(self):
        """Refresh all components."""
        self.folder_tree.refresh()
        self.calendar.refresh()
    
    def on_folder_selected(self, folder_id):
        """Handle folder selection.
        
        Args:
            folder_id: The selected folder ID
        """
        # Update note list
        self.note_list.set_folder(folder_id)
        
        # Update note editor
        self.note_editor.set_folder(folder_id)
        
        # Update status
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            folder = folder_controller.get_folder_by_id(folder_id)
            if folder:
                self.status_bar.showMessage(f"Folder: {folder['name']}")
    
    def on_note_selected(self, note_id):
        """Handle note selection.
        
        Args:
            note_id: The selected note ID
        """
        # Switch to note tab
        self.tabs.setCurrentWidget(self.note_editor)
        
        # Load note in editor
        self.note_editor.load_note(note_id)
        
        # Update status
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            note = note_controller.get_note_by_id(note_id)
            if note:
                self.status_bar.showMessage(f"Note: {note['title']}")
    
    def on_search_note_selected(self, note_id):
        """Handle note selection from search results.
        
        Args:
            note_id: The selected note ID
        """
        # Get the note
        note_controller = self.controllers.get('note_controller')
        if not note_controller:
            return
        
        note = note_controller.get_note_by_id(note_id)
        if not note:
            return
        
        # Select the folder
        folder_id = note.get('folder_id')
        if folder_id:
            self.folder_tree.select_folder(folder_id)
        
        # Select the note
        self.note_list.select_note(note_id)
    
    def on_note_saved(self, note_id):
        """Handle note save.
        
        Args:
            note_id: The saved note ID
        """
        # Refresh note list
        self.note_list.refresh()
        
        # Update status
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            note = note_controller.get_note_by_id(note_id)
            if note:
                self.status_bar.showMessage(f"Note saved: {note['title']}")
    
    def on_note_deleted(self, note_id):
        """Handle note deletion.
        
        Args:
            note_id: The deleted note ID
        """
        # Refresh note list
        self.note_list.refresh()
        
        # Update status
        self.status_bar.showMessage("Note deleted")
    
    def new_note(self):
        """Create a new note."""
        # Check if a folder is selected
        if self.folder_tree.current_folder_id is None:
            QMessageBox.warning(
                self,
                "No Folder Selected",
                "Please select a folder before creating a new note."
            )
            return
        
        # Switch to note tab
        self.tabs.setCurrentWidget(self.note_editor)
        
        # Create new note in editor
        self.note_editor.new_note()
    
    def new_folder(self):
        """Create a new folder."""
        # Get parent folder ID
        parent_id = self.folder_tree.current_folder_id
        
        # Get folder name
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller:
                folder = folder_controller.create_folder(name, parent_id)
                if folder:
                    # Refresh folder tree
                    self.folder_tree.refresh()
                    
                    # Update status
                    self.status_bar.showMessage(f"Folder created: {name}")
    
    def new_event(self):
        """Create a new event."""
        # Switch to calendar tab
        self.tabs.setCurrentWidget(self.calendar)
        
        # Trigger add event
        self.calendar._add_event()
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self, self.config)
        if dialog.exec_() == QDialog.Accepted:
            # Get settings
            settings = dialog.get_settings()
            
            # Update configuration
            for key, value in settings.items():
                self.config.set(key, value)
            
            # Save configuration
            self.config.save()
            
            # Show restart message
            QMessageBox.information(
                self,
                "Settings Updated",
                "Settings have been updated. Some changes may require a restart to take effect."
            )
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            "<p>A note-taking application with calendar and event management.</p>"
            "<p>Created for Software Engineering course project.</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event.
        
        Args:
            event: The close event
        """
        # Log application exit
        self.logger.info(f"Exiting {APP_NAME} v{APP_VERSION}")
        
        # Accept the event
        event.accept()