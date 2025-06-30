from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from domain.entities.folder import Folder

class FolderService(ABC):
    """Interface for folder-related use cases."""
    
    @abstractmethod
    def get_all_folders(self) -> List[Folder]:
        """Get all folders."""
        pass
    
    @abstractmethod
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Get a folder by its ID."""
        pass
    
    @abstractmethod
    def get_folder_hierarchy(self) -> List[Tuple[Folder, int]]:
        """Get the folder hierarchy as a list of (folder, depth) tuples."""
        pass
    
    @abstractmethod
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Create a new folder and return its ID."""
        pass
    
    @abstractmethod
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Rename a folder and return success status."""
        pass
    
    @abstractmethod
    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder and return success status."""
        pass
    
    @abstractmethod
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move a folder to a new parent and return success status."""
        pass
    
    @abstractmethod
    def get_folder_note_count(self, folder_id: int) -> int:
        """Get the number of notes in a folder."""
        pass