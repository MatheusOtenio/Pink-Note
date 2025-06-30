from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.note import Note
from domain.value_objects.search_criteria import SearchCriteria

class NoteService(ABC):
    """Interface for note-related use cases."""
    
    @abstractmethod
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Get all notes, optionally filtered by folder ID."""
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Get a note by its ID."""
        pass
    
    @abstractmethod
    def create_note(self, title: str, content: str, folder_id: Optional[int] = None) -> int:
        """Create a new note and return its ID."""
        pass
    
    @abstractmethod
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Update an existing note and return success status."""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by its ID and return success status."""
        pass
    
    @abstractmethod
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move a note to a different folder and return success status."""
        pass
    
    @abstractmethod
    def search_notes(self, criteria: SearchCriteria) -> List[Note]:
        """Search for notes based on the provided criteria."""
        pass