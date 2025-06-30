from typing import List, Optional, Dict, Any
import os

from domain.entities.attachment import Attachment
from application.interfaces.attachment_service import AttachmentService
from application.interfaces.note_service import NoteService
from shared.utils.logger import Logger
from shared.constants.app_constants import SUPPORTED_FILE_EXTENSIONS

class AttachmentController:
    """Controller for attachment-related operations in the presentation layer."""
    
    def __init__(self, attachment_service: AttachmentService, note_service: NoteService):
        """Initialize the controller with required services.
        
        Args:
            attachment_service: The attachment service
            note_service: The note service
        """
        self.attachment_service = attachment_service
        self.note_service = note_service
        self.logger = Logger.get_instance()
    
    def get_attachments_for_note(self, note_id: int) -> List[Dict[str, Any]]:
        """Get all attachments for a specific note.
        
        Args:
            note_id: The note ID
            
        Returns:
            A list of dictionaries representing attachments
        """
        try:
            # Validate note exists
            note = self.note_service.get_note_by_id(note_id)
            if not note:
                self.logger.error(f"Cannot get attachments: Note {note_id} not found")
                return []
            
            attachments = self.attachment_service.get_attachments_for_note(note_id)
            return [self._attachment_to_dict(attachment) for attachment in attachments]
        except Exception as e:
            self.logger.error(f"Error getting attachments for note {note_id}: {str(e)}")
            return []
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """Get an attachment by its ID.
        
        Args:
            attachment_id: The attachment ID
            
        Returns:
            A dictionary representing the attachment, or None if not found
        """
        try:
            attachment = self.attachment_service.get_attachment_by_id(attachment_id)
            if attachment:
                return self._attachment_to_dict(attachment)
            return None
        except Exception as e:
            self.logger.error(f"Error getting attachment {attachment_id}: {str(e)}")
            return None
    
    def add_attachment(self, note_id: int, file_path: str) -> Optional[Dict[str, Any]]:
        """Add a new attachment to a note.
        
        Args:
            note_id: The note ID
            file_path: The path to the file to attach
            
        Returns:
            A dictionary representing the added attachment, or None if addition failed
        """
        try:
            # Validate note exists
            note = self.note_service.get_note_by_id(note_id)
            if not note:
                self.logger.error(f"Cannot add attachment: Note {note_id} not found")
                return None
            
            # Validate file exists
            if not os.path.exists(file_path):
                self.logger.error(f"Cannot add attachment: File {file_path} not found")
                return None
            
            # Validate file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in SUPPORTED_FILE_EXTENSIONS:
                self.logger.error(f"Cannot add attachment: Unsupported file extension {file_ext}")
                return None
            
            # Add the attachment
            attachment_id = self.attachment_service.add_attachment(note_id, file_path)
            if attachment_id:
                return self.get_attachment_by_id(attachment_id)
            return None
        except Exception as e:
            self.logger.error(f"Error adding attachment to note {note_id}: {str(e)}")
            return None
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete an attachment.
        
        Args:
            attachment_id: The attachment ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            return self.attachment_service.delete_attachment(attachment_id)
        except Exception as e:
            self.logger.error(f"Error deleting attachment {attachment_id}: {str(e)}")
            return False
    
    def open_attachment(self, attachment_id: int) -> bool:
        """Open an attachment with the default system application.
        
        Args:
            attachment_id: The attachment ID
            
        Returns:
            True if the attachment was opened successfully, False otherwise
        """
        try:
            return self.attachment_service.open_attachment(attachment_id)
        except Exception as e:
            self.logger.error(f"Error opening attachment {attachment_id}: {str(e)}")
            return False
    
    def _attachment_to_dict(self, attachment: Attachment) -> Dict[str, Any]:
        """Convert an Attachment entity to a dictionary.
        
        Args:
            attachment: The Attachment entity
            
        Returns:
            A dictionary representation of the attachment
        """
        return {
            'id': attachment.id,
            'note_id': attachment.note_id,
            'file_path': attachment.file_path,
            'file_name': attachment.file_name,
            'file_type': attachment.file_type,
            'created_at': attachment.created_at.isoformat() if attachment.created_at else None,
            'is_image': attachment.is_image,
            'is_pdf': attachment.is_pdf
        }