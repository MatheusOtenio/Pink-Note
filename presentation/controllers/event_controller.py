from datetime import date, datetime
from typing import List, Optional, Dict, Any

from domain.entities.event import Event
from domain.value_objects.date_range import DateRange
from application.interfaces.event_service import EventService
from shared.utils.logger import Logger
from shared.utils.date_utils import DateUtils

class EventController:
    """Controller for event-related operations in the presentation layer."""
    
    def __init__(self, event_service: EventService):
        """Initialize the controller with required services.
        
        Args:
            event_service: The event service
        """
        self.event_service = event_service
        self.logger = Logger.get_instance()
        self.date_utils = DateUtils()
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all events.
        
        Returns:
            A list of dictionaries representing events
        """
        try:
            events = self.event_service.get_all_events()
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Error getting all events: {str(e)}")
            return []
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get an event by its ID.
        
        Args:
            event_id: The event ID
            
        Returns:
            A dictionary representing the event, or None if not found
        """
        try:
            event = self.event_service.get_event_by_id(event_id)
            if event:
                return self._event_to_dict(event)
            return None
        except Exception as e:
            self.logger.error(f"Error getting event {event_id}: {str(e)}")
            return None
    
    def get_events_by_date(self, event_date: date) -> List[Dict[str, Any]]:
        """Get all events for a specific date.
        
        Args:
            event_date: The date
            
        Returns:
            A list of dictionaries representing events
        """
        try:
            events = self.event_service.get_events_by_date(event_date)
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Error getting events for date {event_date}: {str(e)}")
            return []
    
    def get_events_in_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get all events within a date range.
        
        Args:
            start_date: The start date
            end_date: The end date
            
        Returns:
            A list of dictionaries representing events
        """
        try:
            # Create date range
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Get events in range
            events = self.event_service.get_events_in_range(date_range)
            return [self._event_to_dict(event) for event in events]
        except Exception as e:
            self.logger.error(f"Error getting events in range {start_date} to {end_date}: {str(e)}")
            return []
    
    def get_events_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get all events for a specific month.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            A list of dictionaries representing events
        """
        try:
            # Get the start and end dates for the month
            start_date, end_date = self.date_utils.get_month_range(year, month)
            
            # Get events in the month range
            return self.get_events_in_range(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting events for month {month}/{year}: {str(e)}")
            return []
    
    def get_events_for_week(self, week_date: date) -> List[Dict[str, Any]]:
        """Get all events for the week containing the specified date.
        
        Args:
            week_date: A date in the desired week
            
        Returns:
            A list of dictionaries representing events
        """
        try:
            # Get the start and end dates for the week
            start_date, end_date = self.date_utils.get_week_range(week_date)
            
            # Get events in the week range
            return self.get_events_in_range(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting events for week of {week_date}: {str(e)}")
            return []
    
    def create_event(self, title: str, description: str, event_date: date) -> Optional[Dict[str, Any]]:
        """Create a new event.
        
        Args:
            title: The event title
            description: The event description
            event_date: The event date
            
        Returns:
            A dictionary representing the created event, or None if creation failed
        """
        try:
            # Convert date to datetime if needed
            event_datetime = event_date
            if isinstance(event_date, date) and not isinstance(event_date, datetime):
                # Convert to datetime at midnight
                event_datetime = datetime.combine(event_date, datetime.min.time())
            
            # Create the event
            event_id = self.event_service.create_event(title, description, event_datetime)
            if event_id:
                return self.get_event_by_id(event_id)
            return None
        except Exception as e:
            self.logger.error(f"Error creating event: {str(e)}")
            return None
    
    def update_event(self, event_id: int, title: str, description: str, event_date: date) -> bool:
        """Update an existing event.
        
        Args:
            event_id: The event ID
            title: The new title
            description: The new description
            event_date: The new event date
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Convert date to datetime if needed
            event_datetime = event_date
            if isinstance(event_date, date) and not isinstance(event_date, datetime):
                # Convert to datetime at midnight
                event_datetime = datetime.combine(event_date, datetime.min.time())
            
            return self.event_service.update_event(event_id, title, description, event_datetime)
        except Exception as e:
            self.logger.error(f"Error updating event {event_id}: {str(e)}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event.
        
        Args:
            event_id: The event ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            return self.event_service.delete_event(event_id)
        except Exception as e:
            self.logger.error(f"Error deleting event {event_id}: {str(e)}")
            return False
    
    def get_dates_with_events(self, year: int, month: int) -> List[str]:
        """Get all dates in a month that have events.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            A list of date strings in ISO format (YYYY-MM-DD)
        """
        try:
            # Get the start and end dates for the month
            start_date, end_date = self.date_utils.get_month_range(year, month)
            
            # Create date range
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Get dates with events
            dates = self.event_service.get_dates_with_events(date_range)
            
            # Convert to ISO format strings
            return [date.isoformat() for date in dates]
        except Exception as e:
            self.logger.error(f"Error getting dates with events for {month}/{year}: {str(e)}")
            return []
    
    def _event_to_dict(self, event: Event) -> Dict[str, Any]:
        """Convert an Event entity to a dictionary.
        
        Args:
            event: The Event entity
            
        Returns:
            A dictionary representation of the event
        """
        return {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat() if event.date else None,
            'formatted_date': self.date_utils.format_datetime(event.date) if event.date else None
        }