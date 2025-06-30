from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget

class BaseComponent(QWidget):
    """Base class for all UI components in the presentation layer.
    
    This class provides common functionality for UI components, such as
    access to controllers and event handling.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, controllers: Optional[Dict[str, Any]] = None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent)
        self.controllers = controllers or {}
        
        # Initialize UI
        self._init_ui()
        
        # Connect signals and slots
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the UI components.
        
        This method should be overridden by subclasses to set up their UI.
        """
        pass
    
    def _connect_signals(self):
        """Connect signals and slots.
        
        This method should be overridden by subclasses to connect their signals and slots.
        """
        pass
    
    def refresh(self):
        """Refresh the component's data and UI.
        
        This method should be overridden by subclasses to refresh their data and UI.
        """
        pass