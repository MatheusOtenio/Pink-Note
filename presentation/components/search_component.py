from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from presentation.components.base_component import BaseComponent
from shared.utils import StringUtils

class SearchComponent(BaseComponent):
    """Component for searching notes."""
    
    # Define signals
    search_performed = pyqtSignal(list)  # Emitted when a search is performed (results)
    note_selected = pyqtSignal(int)      # Emitted when a note is selected (note_id)
    
    def __init__(self, parent=None, controllers=None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent, controllers)
        
        # Search results
        self.search_results = []
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search input layout
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.setStyleSheet("padding: 5px;")
        search_layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton("Search", self)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # Results label
        self.results_label = QLabel("Enter a search term above", self)
        self.results_label.setStyleSheet("color: gray; font-style: italic; margin-top: 5px;")
        main_layout.addWidget(self.results_label)
        
        # Results list
        self.results_list = QListWidget(self)
        self.results_list.setStyleSheet("margin-top: 5px;")
        main_layout.addWidget(self.results_list)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect search button
        self.search_button.clicked.connect(self._perform_search)
        
        # Connect search input enter key
        self.search_input.returnPressed.connect(self._perform_search)
        
        # Connect results list
        self.results_list.itemClicked.connect(self._on_result_clicked)
    
    def _perform_search(self):
        """Perform the search using the current input."""
        # Get search term
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.results_label.setText("Enter a search term above")
            self.results_list.clear()
            self.search_results = []
            return
        
        # Perform search
        note_controller = self.controllers.get('note_controller')
        if note_controller:
            # Perform search with default options
            # Search in both title and content, case-insensitive, all folders
            self.search_results = note_controller.search_notes(
                search_term=search_term,
                folder_ids=None,  # Search in all folders
                include_title=True,
                include_content=True,
                case_sensitive=False
            )
            
            # Update results label
            count = len(self.search_results)
            if count == 0:
                self.results_label.setText(f"No results found for '{search_term}'")
            elif count == 1:
                self.results_label.setText(f"1 result found for '{search_term}'")
            else:
                self.results_label.setText(f"{count} results found for '{search_term}'")
            
            # Update results list
            self._update_results_list()
            
            # Emit signal
            self.search_performed.emit(self.search_results)
    
    def _update_results_list(self):
        """Update the results list with the current search results."""
        # Clear the list
        self.results_list.clear()
        
        # Add results to the list
        for result in self.search_results:
            self._add_result_to_list(result)
    
    def _add_result_to_list(self, result: Dict[str, Any]):
        """Add a search result to the list.
        
        Args:
            result: The search result data
        """
        # Create list item
        item = QListWidgetItem()
        
        # Set item text
        title = result.get('title', 'Untitled')
        folder_name = result.get('folder_name', '')
        
        # Create display text
        display_text = title
        if folder_name:
            display_text += f" (in {folder_name})"
        
        item.setText(display_text)
        
        # Store note ID as user data
        item.setData(Qt.UserRole, result.get('id'))
        
        # Add item to the list
        self.results_list.addItem(item)
    
    def _on_result_clicked(self, item: QListWidgetItem):
        """Handle result item click event.
        
        Args:
            item: The clicked item
        """
        # Get note ID
        note_id = item.data(Qt.UserRole)
        
        # Emit signal
        self.note_selected.emit(note_id)
    
    def clear_search(self):
        """Clear the search input and results."""
        self.search_input.clear()
        self.results_list.clear()
        self.results_label.setText("Enter a search term above")
        self.search_results = []