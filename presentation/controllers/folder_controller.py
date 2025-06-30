from typing import List, Optional, Dict, Any, Tuple

from domain.entities.folder import Folder
from application.interfaces.folder_service import FolderService
from shared.utils.logger import Logger

class FolderController:
    """Controller for folder-related operations in the presentation layer."""
    
    def __init__(self, folder_service: FolderService):
        """Initialize the controller with required services.
        
        Args:
            folder_service: The folder service
        """
        self.folder_service = folder_service
        self.logger = Logger.get_instance()
    
    def get_all_folders(self) -> List[Dict[str, Any]]:
        """Get all folders.
        
        Returns:
            A list of dictionaries representing folders
        """
        try:
            folders = self.folder_service.get_all_folders()
            return [self._folder_to_dict(folder) for folder in folders]
        except Exception as e:
            self.logger.error(f"Error getting all folders: {str(e)}")
            return []
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Dict[str, Any]]:
        """Get a folder by its ID.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            A dictionary representing the folder, or None if not found
        """
        try:
            folder = self.folder_service.get_folder_by_id(folder_id)
            if folder:
                return self._folder_to_dict(folder)
            return None
        except Exception as e:
            self.logger.error(f"Error getting folder {folder_id}: {str(e)}")
            return None
    
    def get_folder_hierarchy(self) -> List[Dict[str, Any]]:
        """Get the folder hierarchy.
        
        Returns:
            A list of dictionaries representing the folder hierarchy
        """
        try:
            hierarchy = self.folder_service.get_folder_hierarchy()
            return self._process_hierarchy(hierarchy)
        except Exception as e:
            self.logger.error(f"Error getting folder hierarchy: {str(e)}")
            return []
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Create a new folder.
        
        Args:
            name: The folder name
            parent_id: The parent folder ID (optional)
            
        Returns:
            A dictionary representing the created folder, or None if creation failed
        """
        try:
            # Validate parent folder if provided
            if parent_id is not None:
                parent = self.folder_service.get_folder_by_id(parent_id)
                if not parent:
                    self.logger.error(f"Cannot create folder: Parent folder {parent_id} not found")
                    return None
            
            # Create the folder
            folder_id = self.folder_service.create_folder(name, parent_id)
            if folder_id:
                return self.get_folder_by_id(folder_id)
            return None
        except Exception as e:
            self.logger.error(f"Error creating folder: {str(e)}")
            return None
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Rename a folder.
        
        Args:
            folder_id: The folder ID
            new_name: The new folder name
            
        Returns:
            True if the rename was successful, False otherwise
        """
        try:
            return self.folder_service.rename_folder(folder_id, new_name)
        except Exception as e:
            self.logger.error(f"Error renaming folder {folder_id}: {str(e)}")
            return False
    
    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            return self.folder_service.delete_folder(folder_id)
        except Exception as e:
            self.logger.error(f"Error deleting folder {folder_id}: {str(e)}")
            return False
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move a folder to a different parent folder.
        
        Args:
            folder_id: The folder ID
            new_parent_id: The new parent folder ID, or None to move to root
            
        Returns:
            True if the move was successful, False otherwise
        """
        try:
            # Validate new parent folder if provided
            if new_parent_id is not None:
                parent = self.folder_service.get_folder_by_id(new_parent_id)
                if not parent:
                    self.logger.error(f"Cannot move folder: Parent folder {new_parent_id} not found")
                    return False
                
                # Check if new_parent_id is a descendant of folder_id (which would create a cycle)
                if self._is_descendant(new_parent_id, folder_id):
                    self.logger.error(f"Cannot move folder: Would create a cycle in the folder hierarchy")
                    return False
            
            return self.folder_service.move_folder(folder_id, new_parent_id)
        except Exception as e:
            self.logger.error(f"Error moving folder {folder_id} to parent {new_parent_id}: {str(e)}")
            return False
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Get the number of notes in a folder.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            The number of notes in the folder
        """
        try:
            return self.folder_service.get_folder_note_count(folder_id)
        except Exception as e:
            self.logger.error(f"Error getting note count for folder {folder_id}: {str(e)}")
            return 0
    
    def _folder_to_dict(self, folder: Folder) -> Dict[str, Any]:
        """Convert a Folder entity to a dictionary.
        
        Args:
            folder: The Folder entity
            
        Returns:
            A dictionary representation of the folder
        """
        return {
            'id': folder.id,
            'name': folder.name,
            'parent_id': folder.parent_id,
            'path': folder.path,
            'is_root': folder.is_root
        }
    
    def _process_hierarchy(self, hierarchy: List[Tuple[Folder, int]]) -> List[Dict[str, Any]]:
        """Process the folder hierarchy to add additional information.
        
        Args:
            hierarchy: The folder hierarchy from the service as a list of (folder, depth) tuples
            
        Returns:
            The processed folder hierarchy
        """
        result = []
        
        for folder, depth in hierarchy:
            folder_dict = self._folder_to_dict(folder)
            folder_dict['depth'] = depth
            folder_dict['note_count'] = self.get_folder_note_count(folder_dict['id'])
            
            # Children are processed separately in the tree component
            
            result.append(folder_dict)
        
        return result
    
    def _is_descendant(self, folder_id: int, potential_ancestor_id: int) -> bool:
        """Check if a folder is a descendant of another folder.
        
        Args:
            folder_id: The folder ID to check
            potential_ancestor_id: The potential ancestor folder ID
            
        Returns:
            True if folder_id is a descendant of potential_ancestor_id, False otherwise
        """
        folder = self.folder_service.get_folder_by_id(folder_id)
        if not folder:
            return False
        
        # If this folder's parent is the potential ancestor, it's a descendant
        if folder.parent_id == potential_ancestor_id:
            return True
        
        # If this folder has no parent, it's not a descendant
        if folder.parent_id is None:
            return False
        
        # Recursively check if the parent is a descendant
        return self._is_descendant(folder.parent_id, potential_ancestor_id)