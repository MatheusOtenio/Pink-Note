from datetime import date, datetime
from typing import List, Optional

from domain.entities.event import Event
from domain.repositories.event_repository import EventRepository

class EventRepositoryImpl(EventRepository):
    """SQLite implementation of the event repository."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_events(self) -> List[Event]:
        """Retrieve all events."""
        cursor = self.db.cursor()
        cursor.execute("SELECT id, title, description, date FROM events ORDER BY date")
        
        events = []
        for row in cursor.fetchall():
            event = Event(
                id=row[0],
                title=row[1],
                description=row[2],
                date=datetime.fromisoformat(row[3])
            )
            events.append(event)
        
        return events
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Retrieve an event by its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, title, description, date FROM events WHERE id = ?",
            (event_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return Event(
            id=row[0],
            title=row[1],
            description=row[2],
            date=datetime.fromisoformat(row[3])
        )
    
    def get_events_by_date(self, event_date: date) -> List[Event]:
        """Retrieve all events for a specific date."""
        cursor = self.db.cursor()
        
        # Convert date to string in ISO format (YYYY-MM-DD)
        date_str = event_date.isoformat()
        
        # Use date() function in SQLite to extract the date part from the datetime string
        cursor.execute(
            "SELECT id, title, description, date FROM events WHERE date(date) = ? ORDER BY date",
            (date_str,)
        )
        
        events = []
        for row in cursor.fetchall():
            event = Event(
                id=row[0],
                title=row[1],
                description=row[2],
                date=datetime.fromisoformat(row[3])
            )
            events.append(event)
        
        return events
    
    def add_event(self, event: Event) -> int:
        """Add a new event and return its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, date) VALUES (?, ?, ?)",
            (event.title, event.description, event.date.isoformat())
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def update_event(self, event: Event) -> bool:
        """Update an existing event and return success status."""
        if event.id is None:
            return False
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE events SET title = ?, description = ?, date = ? WHERE id = ?",
            (event.title, event.description, event.date.isoformat(), event.id)
        )
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by its ID and return success status."""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        self.db.commit()
        return cursor.rowcount > 0