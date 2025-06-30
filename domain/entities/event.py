from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    """Entity representing a calendar event in the system."""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    date: datetime = field(default_factory=datetime.now)
    
    def update_title(self, new_title: str) -> None:
        """Update the event title."""
        self.title = new_title
    
    def update_description(self, new_description: str) -> None:
        """Update the event description."""
        self.description = new_description
    
    def update_date(self, new_date: datetime) -> None:
        """Update the event date."""
        self.date = new_date