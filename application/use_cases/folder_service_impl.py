from typing import List, Optional, Tuple

from domain.entities.folder import Folder
from domain.repositories.folder_repository import FolderRepository
from application.interfaces.folder_service import FolderService

class FolderServiceImpl(FolderService):
    """Implementation of the folder service use cases."""
    
    def __init__(self, folder_repository: FolderRepository):
        self.folder_repository = folder_repository
    
    def get_all_folders(self) -> List[Folder]:
        """Get all folders."""
        return self.folder_repository.get_all_folders()
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Get a folder by its ID."""
        return self.folder_repository.get_folder_by_id(folder_id)
    
    def get_folder_hierarchy(self) -> List[Tuple[Folder, int]]:
        """Get the folder hierarchy as a list of (folder, depth) tuples."""
        folders = self.folder_repository.get_all_folders()
        result = []
        
        # First, find all root folders (parent_id is None)
        root_folders = [f for f in folders if f.parent_id is None]
        
        # Process each root folder and its children recursively
        for root_folder in root_folders:
            self._add_folder_with_depth(result, root_folder, 0, folders)
        
        return result
    
    def _add_folder_with_depth(self, result: List[Tuple[Folder, int]], folder: Folder, depth: int, all_folders: List[Folder]) -> None:
        """Helper method to recursively build the folder hierarchy."""
        result.append((folder, depth))
        
        # Find all children of this folder
        children = [f for f in all_folders if f.parent_id == folder.id]
        
        # Process each child recursively
        for child in children:
            self._add_folder_with_depth(result, child, depth + 1, all_folders)
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Create a new folder and return its ID."""
        folder = Folder(name=name, parent_id=parent_id)
        return self.folder_repository.create_folder(folder)
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Rename a folder and return success status."""
        return self.folder_repository.rename_folder(folder_id, new_name)
    
    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder and return success status."""
        return self.folder_repository.delete_folder(folder_id)
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move a folder to a new parent and return success status."""
        return self.folder_repository.move_folder(folder_id, new_parent_id)
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Get the number of notes in a folder."""
        return self.folder_repository.get_folder_note_count(folder_id)