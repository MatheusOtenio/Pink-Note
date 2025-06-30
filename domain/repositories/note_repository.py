from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.note import Note

class NoteRepository(ABC):
    """Interface for note repository operations."""
    
    @abstractmethod
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Retrieve all notes, optionally filtered by folder ID."""
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Retrieve a note by its ID."""
        pass
    
    @abstractmethod
    def add_note(self, note: Note) -> int:
        """Add a new note and return its ID."""
        pass
    
    @abstractmethod
    def update_note(self, note: Note) -> bool:
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
    def search_notes(self, search_term: str) -> List[Note]:
        """Search for notes containing the search term in title or content."""
        pass