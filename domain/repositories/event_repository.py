from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.entities.event import Event

class EventRepository(ABC):
    """Interface for event repository operations."""
    
    @abstractmethod
    def get_all_events(self) -> List[Event]:
        """Retrieve all events."""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Retrieve an event by its ID."""
        pass
    
    @abstractmethod
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Retrieve all events for a specific date."""
        pass
    
    @abstractmethod
    def add_event(self, event: Event) -> int:
        """Add a new event and return its ID."""
        pass
    
    @abstractmethod
    def update_event(self, event: Event) -> bool:
        """Update an existing event and return success status."""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by its ID and return success status."""
        pass