from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Note:
    """Entity representing a note in the system."""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    folder_id: int = 1  # Default to 'Geral' folder
    attachment_ids: List[int] = field(default_factory=list)
    
    def update_content(self, new_content: str) -> None:
        """Update the note content and modification time."""
        self.content = new_content
        self.modified_at = datetime.now()
    
    def update_title(self, new_title: str) -> None:
        """Update the note title and modification time."""
        self.title = new_title
        self.modified_at = datetime.now()
    
    def move_to_folder(self, new_folder_id: int) -> None:
        """Move the note to a different folder."""
        self.folder_id = new_folder_id
        self.modified_at = datetime.now()