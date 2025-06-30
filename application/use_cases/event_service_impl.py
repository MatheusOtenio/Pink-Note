from datetime import date
from typing import List, Optional, Set

from domain.entities.event import Event
from domain.repositories.event_repository import EventRepository
from domain.value_objects.date_range import DateRange
from application.interfaces.event_service import EventService

class EventServiceImpl(EventService):
    """Implementation of the event service use cases."""
    
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository
    
    def get_all_events(self) -> List[Event]:
        """Get all events."""
        return self.event_repository.get_all_events()
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get an event by its ID."""
        return self.event_repository.get_event_by_id(event_id)
    
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Get all events for a specific date."""
        return self.event_repository.get_events_by_date(event_date)
    
    def get_events_in_range(self, date_range: DateRange) -> List[Event]:
        """Get all events within a date range."""
        all_events = self.event_repository.get_all_events()
        return [event for event in all_events if date_range.contains(event.date.date())]
    
    def create_event(self, title: str, description: str, event_date: date) -> int:
        """Create a new event and return its ID."""
        from datetime import datetime
        # Convert date to datetime for the Event entity
        event_datetime = datetime.combine(event_date, datetime.min.time())
        event = Event(title=title, description=description, date=event_datetime)
        return self.event_repository.add_event(event)
    
    def update_event(self, event_id: int, title: str, description: str, event_date: date) -> bool:
        """Update an existing event and return success status."""
        event = self.event_repository.get_event_by_id(event_id)
        if event is None:
            return False
        
        from datetime import datetime
        # Convert date to datetime for the Event entity
        event_datetime = datetime.combine(event_date, datetime.min.time())
        
        event.update_title(title)
        event.update_description(description)
        event.update_date(event_datetime)
        
        return self.event_repository.update_event(event)
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by its ID and return success status."""
        return self.event_repository.delete_event(event_id)
        
    def get_dates_with_events(self, date_range: DateRange) -> List[date]:
        """Get all dates within a range that have events."""
        events_in_range = self.get_events_in_range(date_range)
        dates_with_events = set(event.date.date() for event in events_in_range)
        return sorted(list(dates_with_events))