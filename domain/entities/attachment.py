from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Attachment:
    """Entity representing a file attachment for a note."""
    id: Optional[int] = None
    note_id: int = 0
    file_path: str = ""
    file_name: str = ""
    file_type: str = ""  # e.g., "pdf", "image", etc.
    created_at: datetime = datetime.now()
    
    @property
    def is_pdf(self) -> bool:
        """Check if the attachment is a PDF file."""
        return self.file_type.lower() == "pdf"
    
    @property
    def is_image(self) -> bool:
        """Check if the attachment is an image file."""
        image_types = ["jpg", "jpeg", "png", "gif", "bmp"]
        return self.file_type.lower() in image_types