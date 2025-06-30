import os
import logging
from datetime import datetime
from typing import Optional

class Logger:
    """A simple logger utility for the application.
    
    This class provides a centralized logging mechanism with different
    log levels and output options (console and/or file).
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        """Get or create the singleton logger instance.
        
        Args:
            log_level: The logging level (default: INFO)
            log_to_file: Whether to log to a file (default: True)
            log_dir: Directory for log files (default: 'logs' in the application directory)
            
        Returns:
            The Logger instance
        """
        if cls._instance is None:
            cls._instance = Logger(log_level, log_to_file, log_dir)
        return cls._instance
    
    def __init__(self, log_level: int = logging.INFO, log_to_file: bool = True, log_dir: Optional[str] = None):
        """Initialize the logger.
        
        Args:
            log_level: The logging level (default: INFO)
            log_to_file: Whether to log to a file (default: True)
            log_dir: Directory for log files (default: 'logs' in the application directory)
        """
        self.logger = logging.getLogger('notepad')
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add console handler to logger
        self.logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_to_file:
            if log_dir is None:
                # Default log directory is 'logs' in the application directory
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                log_dir = os.path.join(base_dir, 'logs')
            
            # Ensure log directory exists
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(log_dir, f'notepad_{timestamp}.log')
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            
            # Add file handler to logger
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log a debug message.
        
        Args:
            message: The message to log
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message.
        
        Args:
            message: The message to log
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message.
        
        Args:
            message: The message to log
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message.
        
        Args:
            message: The message to log
        """
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message.
        
        Args:
            message: The message to log
        """
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log an exception message with traceback.
        
        Args:
            message: The message to log
        """
        self.logger.exception(message)