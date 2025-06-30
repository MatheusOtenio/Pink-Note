from typing import List, Optional

from domain.entities.note import Note
from domain.repositories.note_repository import NoteRepository
from domain.value_objects.search_criteria import SearchCriteria
from application.interfaces.note_service import NoteService

class NoteServiceImpl(NoteService):
    """Implementation of the note service use cases."""
    
    def __init__(self, note_repository: NoteRepository):
        self.note_repository = note_repository
    
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Get all notes, optionally filtered by folder ID."""
        return self.note_repository.get_all_notes(folder_id)
    
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Get a note by its ID."""
        return self.note_repository.get_note_by_id(note_id)
    
    def create_note(self, title: str, content: str, folder_id: Optional[int] = None) -> int:
        """Create a new note and return its ID."""
        note = Note(title=title, content=content)
        if folder_id is not None:
            note.folder_id = folder_id
        return self.note_repository.add_note(note)
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Update an existing note and return success status."""
        note = self.note_repository.get_note_by_id(note_id)
        if note is None:
            return False
        
        note.update_title(title)
        note.update_content(content)
        return self.note_repository.update_note(note)
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by its ID and return success status."""
        return self.note_repository.delete_note(note_id)
    
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move a note to a different folder and return success status."""
        return self.note_repository.move_note(note_id, folder_id)
    
    def search_notes(self, criteria: SearchCriteria) -> List[Note]:
        """Search for notes based on the provided criteria."""
        # This is a simplified implementation that delegates to the repository
        # In a more complex system, we might apply additional business logic here
        return self.note_repository.search_notes(criteria)
        
    def get_notes_by_folder(self, folder_id: int) -> List[Note]:
        """Get all notes in a specific folder.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            A list of notes in the folder
        """
        return self.get_all_notes(folder_id=folder_id)