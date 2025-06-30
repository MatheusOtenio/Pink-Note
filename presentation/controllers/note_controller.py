from typing import List, Optional, Dict, Any

from domain.entities.note import Note
from domain.value_objects.search_criteria import SearchCriteria
from application.interfaces.note_service import NoteService
from application.interfaces.folder_service import FolderService
from shared.utils.logger import Logger

class NoteController:
    """Controller for note-related operations in the presentation layer."""
    
    def __init__(self, note_service: NoteService, folder_service: FolderService):
        """Initialize the controller with required services.
        
        Args:
            note_service: The note service
            folder_service: The folder service
        """
        self.note_service = note_service
        self.folder_service = folder_service
        self.logger = Logger.get_instance()
    
    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes.
        
        Returns:
            A list of dictionaries representing notes
        """
        try:
            notes = self.note_service.get_all_notes()
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error getting all notes: {str(e)}")
            return []
    
    def get_notes_by_folder(self, folder_id: int) -> List[Dict[str, Any]]:
        """Get all notes in a specific folder.
        
        Args:
            folder_id: The folder ID
            
        Returns:
            A list of dictionaries representing notes
        """
        try:
            notes = self.note_service.get_notes_by_folder(folder_id)
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error getting notes for folder {folder_id}: {str(e)}")
            return []
    
    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get a note by its ID.
        
        Args:
            note_id: The note ID
            
        Returns:
            A dictionary representing the note, or None if not found
        """
        try:
            note = self.note_service.get_note_by_id(note_id)
            if note:
                return self._note_to_dict(note)
            return None
        except Exception as e:
            self.logger.error(f"Error getting note {note_id}: {str(e)}")
            return None
    
    def create_note(self, title: str, content: str, folder_id: int) -> Optional[Dict[str, Any]]:
        """Create a new note.
        
        Args:
            title: The note title
            content: The note content
            folder_id: The folder ID
            
        Returns:
            A dictionary representing the created note, or None if creation failed
        """
        try:
            # Validate folder exists
            folder = self.folder_service.get_folder_by_id(folder_id)
            if not folder:
                self.logger.error(f"Cannot create note: Folder {folder_id} not found")
                return None
            
            # Create the note
            note_id = self.note_service.create_note(title, content, folder_id)
            if note_id:
                return self.get_note_by_id(note_id)
            return None
        except Exception as e:
            self.logger.error(f"Error creating note: {str(e)}")
            return None
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Update an existing note.
        
        Args:
            note_id: The note ID
            title: The new title
            content: The new content
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            return self.note_service.update_note(note_id, title, content)
        except Exception as e:
            self.logger.error(f"Error updating note {note_id}: {str(e)}")
            return False
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note.
        
        Args:
            note_id: The note ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            return self.note_service.delete_note(note_id)
        except Exception as e:
            self.logger.error(f"Error deleting note {note_id}: {str(e)}")
            return False
    
    def move_note(self, note_id: int, target_folder_id: int) -> bool:
        """Move a note to a different folder.
        
        Args:
            note_id: The note ID
            target_folder_id: The target folder ID
            
        Returns:
            True if the move was successful, False otherwise
        """
        try:
            # Validate folder exists
            folder = self.folder_service.get_folder_by_id(target_folder_id)
            if not folder:
                self.logger.error(f"Cannot move note: Folder {target_folder_id} not found")
                return False
            
            return self.note_service.move_note(note_id, target_folder_id)
        except Exception as e:
            self.logger.error(f"Error moving note {note_id} to folder {target_folder_id}: {str(e)}")
            return False
    
    def search_notes(self, search_term: str, folder_ids: Optional[List[int]] = None,
                     include_title: bool = True, include_content: bool = True,
                     case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for notes based on criteria.
        
        Args:
            search_term: The search term
            folder_ids: Optional list of folder IDs to search in
            include_title: Whether to search in titles
            include_content: Whether to search in content
            case_sensitive: Whether the search is case sensitive
            
        Returns:
            A list of dictionaries representing matching notes
        """
        try:
            # Create search criteria
            criteria = SearchCriteria(
                search_term=search_term,
                folder_ids=folder_ids or [],
                include_title=include_title,
                include_content=include_content,
                case_sensitive=case_sensitive
            )
            
            # Perform the search
            notes = self.note_service.search_notes(criteria)
            return [self._note_to_dict(note) for note in notes]
        except Exception as e:
            self.logger.error(f"Error searching notes: {str(e)}")
            return []
    
    def _note_to_dict(self, note: Note) -> Dict[str, Any]:
        """Convert a Note entity to a dictionary.
        
        Args:
            note: The Note entity
            
        Returns:
            A dictionary representation of the note
        """
        return {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat() if note.created_at else None,
            'modified_at': note.modified_at.isoformat() if note.modified_at else None,
            'folder_id': note.folder_id,
            'attachment_ids': note.attachment_ids
        }