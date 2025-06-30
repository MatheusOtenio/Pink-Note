from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

class DateUtils:
    """Utility class for date and time operations."""
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """Get the current date and time.
        
        Returns:
            The current datetime
        """
        return datetime.now()
    
    @staticmethod
    def get_current_date() -> date:
        """Get the current date.
        
        Returns:
            The current date
        """
        return date.today()
    
    @staticmethod
    def format_date(dt: date, format_str: str = '%d/%m/%Y') -> str:
        """Format a date according to the specified format.
        
        Args:
            dt: The date to format
            format_str: The format string (default: '%d/%m/%Y')
            
        Returns:
            The formatted date string
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%d/%m/%Y %H:%M:%S') -> str:
        """Format a datetime according to the specified format.
        
        Args:
            dt: The datetime to format
            format_str: The format string (default: '%d/%m/%Y %H:%M:%S')
            
        Returns:
            The formatted datetime string
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = '%d/%m/%Y') -> Optional[date]:
        """Parse a date string according to the specified format.
        
        Args:
            date_str: The date string to parse
            format_str: The format string (default: '%d/%m/%Y')
            
        Returns:
            The parsed date or None if parsing fails
        """
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            # Try to parse ISO format (YYYY-MM-DD) if the default format fails
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
    
    @staticmethod
    def parse_datetime(datetime_str: str, format_str: str = '%d/%m/%Y %H:%M:%S') -> Optional[datetime]:
        """Parse a datetime string according to the specified format.
        
        Args:
            datetime_str: The datetime string to parse
            format_str: The format string (default: '%d/%m/%Y %H:%M:%S')
            
        Returns:
            The parsed datetime or None if parsing fails
        """
        try:
            return datetime.strptime(datetime_str, format_str)
        except ValueError:
            return None
    
    @staticmethod
    def parse_time(time_str: str, format_str: str = '%H:%M') -> Optional[datetime.time]:
        """Parse a time string according to the specified format.
        
        Args:
            time_str: The time string to parse
            format_str: The format string (default: '%H:%M')
            
        Returns:
            The parsed time or None if parsing fails
        """
        try:
            return datetime.strptime(time_str, format_str).time()
        except ValueError:
            return None
    
    @staticmethod
    def get_month_range(year: int, month: int) -> Tuple[date, date]:
        """Get the start and end dates for a specific month.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            A tuple with the first and last day of the month
        """
        start_date = date(year, month, 1)
        
        # Calculate the last day of the month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def get_week_range(dt: date) -> Tuple[date, date]:
        """Get the start and end dates for the week containing the specified date.
        
        Args:
            dt: The date
            
        Returns:
            A tuple with the first (Monday) and last day (Sunday) of the week
        """
        # Calculate the start of the week (Monday)
        start_date = dt - timedelta(days=dt.weekday())
        
        # Calculate the end of the week (Sunday)
        end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> List[date]:
        """Get a list of all days in a specific month.
        
        Args:
            year: The year
            month: The month (1-12)
            
        Returns:
            A list of dates for each day in the month
        """
        start_date, end_date = DateUtils.get_month_range(year, month)
        
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        
        return days
    
    @staticmethod
    def get_days_in_week(dt: date) -> List[date]:
        """Get a list of all days in the week containing the specified date.
        
        Args:
            dt: The date
            
        Returns:
            A list of dates for each day in the week
        """
        start_date, end_date = DateUtils.get_week_range(dt)
        
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        
        return days
    
    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """Check if two datetimes are on the same day.
        
        Args:
            dt1: The first datetime
            dt2: The second datetime
            
        Returns:
            True if both datetimes are on the same day, False otherwise
        """
        return dt1.date() == dt2.date()
    
    @staticmethod
    def time_elapsed_since(dt: datetime) -> str:
        """Get a human-readable string representing the time elapsed since the specified datetime.
        
        Args:
            dt: The datetime
            
        Returns:
            A string representing the elapsed time (e.g., '2 hours ago', '3 days ago')
        """
        now = datetime.now()
        delta = now - dt
        
        # Calculate the elapsed time in different units
        seconds = delta.total_seconds()
        minutes = seconds // 60
        hours = minutes // 60
        days = delta.days
        
        if days > 0:
            if days == 1:
                return "1 dia atrás"
            else:
                return f"{days} dias atrás"
        elif hours > 0:
            if hours == 1:
                return "1 hora atrás"
            else:
                return f"{int(hours)} horas atrás"
        elif minutes > 0:
            if minutes == 1:
                return "1 minuto atrás"
            else:
                return f"{int(minutes)} minutos atrás"
        else:
            return "agora mesmo"