from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from domain.entities.event import Event
from domain.value_objects.date_range import DateRange

class EventService(ABC):
    """Interface for event-related use cases."""
    
    @abstractmethod
    def get_all_events(self) -> List[Event]:
        """Get all events."""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get an event by its ID."""
        pass
    
    @abstractmethod
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Get all events for a specific date."""
        pass
    
    @abstractmethod
    def get_events_in_range(self, date_range: DateRange) -> List[Event]:
        """Get all events within a date range."""
        pass
    
    @abstractmethod
    def create_event(self, title: str, description: str, event_date: date) -> int:
        """Create a new event and return its ID."""
        pass
    
    @abstractmethod
    def update_event(self, event_id: int, title: str, description: str, event_date: date) -> bool:
        """Update an existing event and return success status."""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by its ID and return success status."""
        pass
    
    @abstractmethod
    def get_dates_with_events(self, date_range: DateRange) -> List[date]:
        """Get all dates within a range that have events."""
        pass