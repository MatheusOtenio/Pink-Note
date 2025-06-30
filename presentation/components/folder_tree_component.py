from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from presentation.components.base_component import BaseComponent

class FolderTreeComponent(BaseComponent):
    """Component for displaying and managing a tree of folders."""
    
    # Define signals
    folder_selected = pyqtSignal(int)  # Emitted when a folder is selected (folder_id)
    folder_created = pyqtSignal(int)   # Emitted when a folder is created (folder_id)
    folder_renamed = pyqtSignal(int)   # Emitted when a folder is renamed (folder_id)
    folder_deleted = pyqtSignal(int)   # Emitted when a folder is deleted (folder_id)
    folder_moved = pyqtSignal(int, int)  # Emitted when a folder is moved (folder_id, target_folder_id)
    
    def __init__(self, parent=None, controllers=None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent, controllers)
        
        # Current folder ID
        self.current_folder_id = None
        
        # Folder items map (folder_id -> QTreeWidgetItem)
        self.folder_items = {}
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Create tree widget
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Set up layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect tree widget signals
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def refresh(self):
        """Refresh the folder tree."""
        # Clear the tree
        self.tree_widget.clear()
        self.folder_items = {}
        
        # Get folder hierarchy
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            hierarchy = folder_controller.get_folder_hierarchy()
            
            # Build the tree
            for folder in hierarchy:
                self._add_folder_to_tree(folder)
            
            # Expand all items
            self.tree_widget.expandAll()
            
            # Select the current folder if set
            if self.current_folder_id is not None:
                self.select_folder(self.current_folder_id)
    
    def _add_folder_to_tree(self, folder: Dict[str, Any], parent_item: Optional[QTreeWidgetItem] = None):
        """Add a folder to the tree widget.
        
        Args:
            folder: The folder data
            parent_item: The parent tree item (optional)
        """
        # Create tree item
        item = QTreeWidgetItem()
        item.setText(0, folder['name'])
        item.setData(0, Qt.UserRole, folder['id'])  # Store folder ID as user data
        
        # Add note count to the display text if available
        if 'note_count' in folder:
            item.setText(0, f"{folder['name']} ({folder['note_count']})")  
        
        # Add item to the tree
        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree_widget.addTopLevelItem(item)
        
        # Store the item in the map
        self.folder_items[folder['id']] = item
        
        # Add children recursively
        if 'children' in folder:
            for child in folder['children']:
                self._add_folder_to_tree(child, item)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click event.
        
        Args:
            item: The clicked item
            column: The clicked column
        """
        folder_id = item.data(0, Qt.UserRole)
        self.current_folder_id = folder_id
        self.folder_selected.emit(folder_id)
    
    def _show_context_menu(self, position):
        """Show context menu for the tree item at the given position.
        
        Args:
            position: The position where to show the menu
        """
        # Get the item at the position
        item = self.tree_widget.itemAt(position)
        if not item:
            return
        
        # Get the folder ID
        folder_id = item.data(0, Qt.UserRole)
        
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(lambda: self._create_folder(folder_id))
        menu.addAction(new_folder_action)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self._rename_folder(folder_id))
        menu.addAction(rename_action)
        
        # Add move to folder submenu
        move_menu = menu.addMenu("Move to")
        self._populate_move_menu(move_menu, folder_id)
        
        # Add delete action (only if not the root folder)
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller:
            folder = folder_controller.get_folder_by_id(folder_id)
            if folder and not folder.get('is_root', False):
                delete_action = QAction("Delete", self)
                delete_action.triggered.connect(lambda: self._delete_folder(folder_id))
                menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(self.tree_widget.mapToGlobal(position))
    
    def _populate_move_menu(self, menu: QMenu, folder_id: int):
        """Populate the move to folder submenu.
        
        Args:
            menu: The menu to populate
            folder_id: The folder ID
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Get all folders
        folders = folder_controller.get_all_folders()
        
        # Add folder actions
        for folder in folders:
            # Skip the current folder and its descendants
            if folder['id'] == folder_id or self._is_descendant(folder['id'], folder_id):
                continue
            
            action = QAction(folder['name'], self)
            action.triggered.connect(lambda checked=False, fid=folder['id']: self._move_folder(folder_id, fid))
            menu.addAction(action)
        
        # Add move to root action
        action = QAction("Root", self)
        action.triggered.connect(lambda: self._move_folder(folder_id, None))
        menu.addAction(action)
    
    def _is_descendant(self, folder_id: int, potential_ancestor_id: int) -> bool:
        """Check if a folder is a descendant of another folder.
        
        Args:
            folder_id: The folder ID to check
            potential_ancestor_id: The potential ancestor folder ID
            
        Returns:
            True if folder_id is a descendant of potential_ancestor_id, False otherwise
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return False
        
        folder = folder_controller.get_folder_by_id(folder_id)
        if not folder:
            return False
        
        # If this folder's parent is the potential ancestor, it's a descendant
        if folder.get('parent_id') == potential_ancestor_id:
            return True
        
        # If this folder has no parent, it's not a descendant
        if folder.get('parent_id') is None:
            return False
        
        # Recursively check if the parent is a descendant
        return self._is_descendant(folder.get('parent_id'), potential_ancestor_id)
    
    def _create_folder(self, parent_id: int):
        """Create a new folder.
        
        Args:
            parent_id: The parent folder ID
        """
        # Get folder name from user
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller:
                new_folder = folder_controller.create_folder(name, parent_id)
                if new_folder:
                    # Refresh the tree
                    self.refresh()
                    
                    # Emit signal
                    self.folder_created.emit(new_folder['id'])
    
    def _rename_folder(self, folder_id: int):
        """Rename a folder.
        
        Args:
            folder_id: The folder ID
        """
        folder_controller = self.controllers.get('folder_controller')
        if not folder_controller:
            return
        
        # Get the current folder name
        folder = folder_controller.get_folder_by_id(folder_id)
        if not folder:
            return
        
        # Get new name from user
        name, ok = QInputDialog.getText(
            self, "Rename Folder", "New folder name:", text=folder['name']
        )
        
        if ok and name and name != folder['name']:
            if folder_controller.rename_folder(folder_id, name):
                # Update the item text
                item = self.folder_items.get(folder_id)
                if item:
                    item.setText(0, name)
                
                # Emit signal
                self.folder_renamed.emit(folder_id)
    
    def _delete_folder(self, folder_id: int):
        """Delete a folder.
        
        Args:
            folder_id: The folder ID
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this folder? All notes will be moved to the General folder.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            folder_controller = self.controllers.get('folder_controller')
            if folder_controller and folder_controller.delete_folder(folder_id):
                # Refresh the tree
                self.refresh()
                
                # Emit signal
                self.folder_deleted.emit(folder_id)
    
    def _move_folder(self, folder_id: int, target_folder_id: Optional[int]):
        """Move a folder to a different parent folder.
        
        Args:
            folder_id: The folder ID
            target_folder_id: The target folder ID, or None to move to root
        """
        folder_controller = self.controllers.get('folder_controller')
        if folder_controller and folder_controller.move_folder(folder_id, target_folder_id):
            # Refresh the tree
            self.refresh()
            
            # Emit signal
            self.folder_moved.emit(folder_id, target_folder_id or 0)  # Use 0 for root
    
    def select_folder(self, folder_id: int):
        """Select a folder in the tree.
        
        Args:
            folder_id: The folder ID
        """
        item = self.folder_items.get(folder_id)
        if item:
            self.tree_widget.setCurrentItem(item)
            self.current_folder_id = folder_id