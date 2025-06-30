import os
import json
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the application.
    
    This class is responsible for loading, accessing, and managing
    application configuration settings.
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file_path: Path to the configuration file (optional)
        """
        self.config: Dict[str, Any] = {}
        self.config_file_path = config_file_path
        
        # Default configuration values
        self._set_defaults()
        
        # Load configuration from file if provided
        if config_file_path and os.path.exists(config_file_path):
            self._load_from_file(config_file_path)
    
    def _set_defaults(self):
        """Set default configuration values."""
        # Get the application's base directory
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Database settings
        self.config['db_path'] = os.path.join(base_dir, 'data', 'notepad.db')
        
        # Storage settings
        self.config['storage_path'] = os.path.join(base_dir, 'data', 'attachments')
        
        # UI settings
        self.config['theme'] = 'light'
        self.config['font_size'] = 12
        
        # Ensure data directories exist
        os.makedirs(os.path.dirname(self.config['db_path']), exist_ok=True)
        os.makedirs(self.config['storage_path'], exist_ok=True)
    
    def _load_from_file(self, file_path: str):
        """Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
        """
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                # Update the configuration with values from the file
                self.config.update(file_config)
        except (json.JSONDecodeError, IOError) as e:
            from shared.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Error loading configuration from {file_path}: {e}")
    
    def save_to_file(self, file_path: str):
        """Save the current configuration to a JSON file.
        
        Args:
            file_path: Path where to save the configuration
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            from shared.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Error saving configuration to {file_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value if the key doesn't exist
            
        Returns:
            The configuration value or the default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            A dictionary with all configuration values
        """
        return self.config.copy()
        
    def load(self):
        """Load configuration from the file specified during initialization.
        
        If no file path was provided during initialization, this method does nothing.
        """
        if self.config_file_path and os.path.exists(self.config_file_path):
            self._load_from_file(self.config_file_path)