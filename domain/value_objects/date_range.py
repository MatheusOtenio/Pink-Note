from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator, List

@dataclass(frozen=True)
class DateRange:
    """Value object representing a range of dates."""
    start_date: date
    end_date: date
    
    def __post_init__(self):
        """Validate that start_date is before or equal to end_date."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
    
    def contains(self, check_date: date) -> bool:
        """Check if a date is within this range."""
        return self.start_date <= check_date <= self.end_date
    
    def days(self) -> int:
        """Get the number of days in this range."""
        return (self.end_date - self.start_date).days + 1
    
    def iterate_days(self) -> Iterator[date]:
        """Iterate through all days in this range."""
        current = self.start_date
        while current <= self.end_date:
            yield current
            current += timedelta(days=1)
    
    def to_list(self) -> List[date]:
        """Convert the range to a list of dates."""
        return list(self.iterate_days())