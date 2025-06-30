from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.attachment import Attachment

class AttachmentService(ABC):
    """Interface for attachment-related use cases."""
    
    @abstractmethod
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Get all attachments for a specific note."""
        pass
    
    @abstractmethod
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Get an attachment by its ID."""
        pass
    
    @abstractmethod
    def add_attachment(self, note_id: int, file_path: str) -> int:
        """Add a new attachment to a note and return its ID."""
        pass
    
    @abstractmethod
    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete an attachment by its ID and return success status."""
        pass
    
    @abstractmethod
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Get the file system path for an attachment."""
        pass
    
    @abstractmethod
    def open_attachment(self, attachment_id: int) -> bool:
        """Open an attachment with the system's default application."""
        pass