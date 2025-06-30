from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.attachment import Attachment

class AttachmentRepository(ABC):
    """Interface for attachment repository operations."""
    
    @abstractmethod
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Retrieve all attachments for a specific note."""
        pass
    
    @abstractmethod
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Retrieve an attachment by its ID."""
        pass
    
    @abstractmethod
    def add_attachment(self, attachment: Attachment) -> int:
        """Add a new attachment and return its ID."""
        pass
    
    @abstractmethod
    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete an attachment by its ID and return success status."""
        pass
    
    @abstractmethod
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Get the file system path for an attachment."""
        pass