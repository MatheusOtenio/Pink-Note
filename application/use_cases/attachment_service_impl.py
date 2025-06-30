import os
import subprocess
from datetime import datetime
from typing import List, Optional

from domain.entities.attachment import Attachment
from domain.repositories.attachment_repository import AttachmentRepository
from application.interfaces.attachment_service import AttachmentService

class AttachmentServiceImpl(AttachmentService):
    """Implementation of the attachment service use cases."""
    
    def __init__(self, attachment_repository: AttachmentRepository):
        self.attachment_repository = attachment_repository
    
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Get all attachments for a specific note."""
        return self.attachment_repository.get_attachments_for_note(note_id)
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Get an attachment by its ID."""
        # This method might not be directly available in the repository
        # We can implement it by filtering the results of get_attachments_for_note
        attachments = self.attachment_repository.get_attachments_for_note(None)  # Get all attachments
        for attachment in attachments:
            if attachment.id == attachment_id:
                return attachment
        return None
    
    def add_attachment(self, note_id: int, file_path: str) -> int:
        """Add a new attachment to a note and return its ID."""
        # Extract file name and type from the path
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_name)[1].lstrip('.')
        
        # Create a new attachment entity
        attachment = Attachment(
            note_id=note_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            created_at=datetime.now()
        )
        
        return self.attachment_repository.add_attachment(attachment)
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete an attachment by its ID and return success status."""
        return self.attachment_repository.delete_attachment(attachment_id)
    
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Get the file system path for an attachment."""
        return self.attachment_repository.get_attachment_path(attachment_id)
    
    def open_attachment(self, attachment_id: int) -> bool:
        """Open an attachment with the system's default application."""
        path = self.get_attachment_path(attachment_id)
        if not path or not os.path.exists(path):
            return False
        
        try:
            # Use the appropriate command based on the operating system
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS and Linux
                if 'darwin' in os.uname().sysname.lower():  # macOS
                    subprocess.call(['open', path])
                else:  # Linux
                    subprocess.call(['xdg-open', path])
            return True
        except Exception:
            return False