from typing import Dict, Any, List, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget, 
                             QPushButton, QLabel, QDialog, QLineEdit, QTextEdit,
                             QTimeEdit, QDateEdit, QFormLayout, QDialogButtonBox,
                             QMessageBox, QMenu, QAction, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QDateTime
from PyQt5.QtGui import QColor, QTextCharFormat
import datetime

from presentation.components.base_component import BaseComponent
from shared.utils import DateUtils

class EventDialog(QDialog):
    """Dialog for creating and editing events."""
    
    def __init__(self, parent=None, event=None):
        """Initialize the dialog.
        
        Args:
            parent: The parent widget
            event: The event data (optional, for editing)
        """
        super().__init__(parent)
        
        self.event = event
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Set dialog properties
        self.setWindowTitle("Event" if self.event else "New Event")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Title input
        self.title_input = QLineEdit(self)
        if self.event:
            self.title_input.setText(self.event.get('title', ''))
        form_layout.addRow("Title:", self.title_input)
        
        # Date input
        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        if self.event and 'date' in self.event:
            event_date = DateUtils.parse_date(self.event['date'])
            self.date_input.setDate(QDate(event_date.year, event_date.month, event_date.day))
        else:
            self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)
        
        # Time input
        self.time_input = QTimeEdit(self)
        if self.event and 'time' in self.event:
            event_time = DateUtils.parse_time(self.event['time'])
            self.time_input.setTime(QTime(event_time.hour, event_time.minute))
        else:
            self.time_input.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_input)
        
        # Description input
        self.description_input = QTextEdit(self)
        if self.event:
            self.description_input.setText(self.event.get('description', ''))
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_event_data(self) -> Dict[str, Any]:
        """Get the event data from the dialog inputs.
        
        Returns:
            A dictionary with the event data
        """
        # Get values from inputs
        title = self.title_input.text().strip()
        date = self.date_input.date().toString(Qt.ISODate)
        time = self.time_input.time().toString("hh:mm")
        description = self.description_input.toPlainText().strip()
        
        # Create event data
        event_data = {
            'title': title,
            'date': date,
            'time': time,
            'description': description
        }
        
        # Add ID if editing
        if self.event and 'id' in self.event:
            event_data['id'] = self.event['id']
        
        return event_data

class CalendarComponent(BaseComponent):
    """Component for displaying and managing a calendar with events."""
    
    # Define signals
    date_selected = pyqtSignal(QDate)  # Emitted when a date is selected
    event_created = pyqtSignal(int)    # Emitted when an event is created (event_id)
    event_updated = pyqtSignal(int)    # Emitted when an event is updated (event_id)
    event_deleted = pyqtSignal(int)    # Emitted when an event is deleted (event_id)
    
    def __init__(self, parent=None, controllers=None):
        """Initialize the component.
        
        Args:
            parent: The parent widget
            controllers: A dictionary of controllers
        """
        super().__init__(parent, controllers)
        
        # Current date
        self.current_date = QDate.currentDate()
        
        # Event data
        self.events_by_date = {}
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Calendar header
        header_layout = QHBoxLayout()
        
        # Month navigation
        self.prev_month_btn = QPushButton("<", self)
        self.prev_month_btn.setFixedWidth(30)
        header_layout.addWidget(self.prev_month_btn)
        
        self.month_label = QLabel(self)
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.month_label)
        
        self.next_month_btn = QPushButton(">", self)
        self.next_month_btn.setFixedWidth(30)
        header_layout.addWidget(self.next_month_btn)
        
        main_layout.addLayout(header_layout)
        
        # Calendar widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        self.calendar.setFixedHeight(300)  # Altura fixa para o calendário
        main_layout.addWidget(self.calendar)
        
        # Events section
        events_layout = QVBoxLayout()
        
        # Events header
        events_header = QHBoxLayout()
        self.events_label = QLabel("Events", self)
        self.events_label.setStyleSheet("font-weight: bold;")
        events_header.addWidget(self.events_label)
        
        # Add event button
        self.add_event_btn = QPushButton("Add Event", self)
        events_header.addWidget(self.add_event_btn)
        events_header.addStretch()
        events_layout.addLayout(events_header)
        
        # Scroll area para eventos do dia
        self.day_events_scroll = QScrollArea(self)
        self.day_events_scroll.setObjectName("dayEventsScrollArea")
        self.day_events_scroll.setWidgetResizable(True)
        self.day_events_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.day_events_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget para conter os eventos
        self.events_container = QWidget()
        self.events_container.setObjectName("dayEventsWidget")
        self.events_container.setLayout(QVBoxLayout())
        self.events_container.layout().setObjectName("dayEventsLayout")
        self.events_container.layout().setContentsMargins(0, 0, 0, 0)
        self.events_container.layout().setSpacing(5)
        self.events_container.layout().addStretch()  # Adiciona espaço em branco no final
        
        # Adiciona o widget de eventos ao scroll area
        self.day_events_scroll.setWidget(self.events_container)
        events_layout.addWidget(self.day_events_scroll)
        
        main_layout.addLayout(events_layout)
        
        # Update UI with current date
        self._update_month_label()
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect calendar signals
        self.calendar.clicked.connect(self._on_date_clicked)
        self.calendar.currentPageChanged.connect(self._on_month_changed)
        
        # Connect navigation buttons
        self.prev_month_btn.clicked.connect(self._on_prev_month)
        self.next_month_btn.clicked.connect(self._on_next_month)
        
        # Connect add event button
        self.add_event_btn.clicked.connect(self._add_event)
    
    def refresh(self):
        """Refresh the calendar display."""
        # Load events for the current month
        self._load_events_for_month()
        
        # Update the calendar display
        self._update_calendar_display()
        
        # Update events for the selected date
        self._update_events_display()
    
    def _update_month_label(self):
        """Update the month label with the current month and year."""
        month_year = self.calendar.monthShown(), self.calendar.yearShown()
        month_name = QDate(month_year[1], month_year[0], 1).toString("MMMM yyyy")
        self.month_label.setText(month_name)
        self.month_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333;")
    
    def _on_date_clicked(self, date: QDate):
        """Handle date click event.
        
        Args:
            date: The clicked date
        """
        self.current_date = date
        self._update_events_display()
        self.date_selected.emit(date)
    
    def _on_month_changed(self, year: int, month: int):
        """Handle month change event.
        
        Args:
            year: The new year
            month: The new month
        """
        self._update_month_label()
        self._load_events_for_month()
        self._update_calendar_display()
    
    def _on_prev_month(self):
        """Navigate to the previous month."""
        self.calendar.showPreviousMonth()
    
    def _on_next_month(self):
        """Navigate to the next month."""
        self.calendar.showNextMonth()
    
    def _load_events_for_month(self):
        """Load events for the current month."""
        event_controller = self.controllers.get('event_controller')
        if not event_controller:
            return
        
        # Get the current month and year
        month = self.calendar.monthShown()
        year = self.calendar.yearShown()
        
        # Get events for the month
        events = event_controller.get_events_for_month(year, month)
        
        # Group events by date
        self.events_by_date = {}
        for event in events:
            date_str = event.get('date')
            if date_str:
                # Normalize date string by removing time part if present
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                
                if date_str not in self.events_by_date:
                    self.events_by_date[date_str] = []
                self.events_by_date[date_str].append(event)
    
    def _update_calendar_display(self):
        """Update the calendar display with event indicators."""
        # Get dates with events
        event_controller = self.controllers.get('event_controller')
        if not event_controller:
            return
        
        # Get the current month and year
        month = self.calendar.monthShown()
        year = self.calendar.yearShown()
        
        # Get dates with events
        dates_with_events = event_controller.get_dates_with_events(year, month)
        
        # Clear all date formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Set format for dates with events
        event_format = QTextCharFormat()
        event_format.setBackground(QColor(200, 230, 255))
        event_format.setForeground(QColor(0, 0, 150))
        event_format.setFontWeight(700)  # Bold font
        
        for date_str in dates_with_events:
            date = QDate.fromString(date_str, Qt.ISODate)
            self.calendar.setDateTextFormat(date, event_format)
    
    def _update_events_display(self):
        """Update the events display for the selected date."""
        # Clear the events container
        self._clear_events_container()
        
        # Get the current date string
        date_str = self.current_date.toString(Qt.ISODate)
        
        # Get events for the date
        events = self.events_by_date.get(date_str, [])
        
        if not events:
            # Show no events message
            label = QLabel("📅 No events for this date", self.events_container)
            label.setStyleSheet("color: gray; font-style: italic; padding: 10px; text-align: center;")
            label.setAlignment(Qt.AlignCenter)
            self.events_container.layout().insertWidget(0, label)
        else:
            # Add event widgets
            for event in events:
                self._add_event_widget(event)
        
        # Adiciona um espaço em branco no final para permitir scroll adequado
        self.events_container.layout().addStretch()
    
    def _clear_events_container(self):
        """Clear the events container."""
        # Remove all widgets from the layout
        layout = self.events_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.spacerItem():
                # Remove spacer items também
                layout.removeItem(item)
    
    def _add_event_widget(self, event: Dict[str, Any]):
        """Add an event widget to the events container.
        
        Args:
            event: The event data
        """
        # Create event widget
        event_widget = QWidget(self.events_container)
        event_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        event_widget.customContextMenuRequested.connect(
            lambda pos, e=event: self._show_event_context_menu(pos, e)
        )
        
        # Set style
        event_widget.setStyleSheet(
            "background-color: #f0f8ff; border-radius: 5px; padding: 5px; border: 1px solid #d0e0f0; margin-bottom: 5px;"
        )
        
        # Create layout
        layout = QVBoxLayout(event_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Add title
        title = event.get('title', '')
        if title:
            title_label = QLabel(title, event_widget)
            title_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(title_label)
        else:
            title_label = QLabel("(No title)", event_widget)
            title_label.setStyleSheet("font-weight: bold; color: gray;")
            layout.addWidget(title_label)
        
        # Add time
        if 'formatted_date' in event:
            formatted_date = event.get('formatted_date', '')
            # Extract time part from formatted date (assuming format is dd/mm/yyyy HH:MM:SS)
            if ' ' in formatted_date:
                time_part = formatted_date.split(' ')[1]
                # Show only hours and minutes
                if ':' in time_part:
                    time_display = ':'.join(time_part.split(':')[:2])
                    time_label = QLabel(f"⏰ {time_display}", event_widget)
                    time_label.setStyleSheet("color: #666;")
                    layout.addWidget(time_label)
        elif 'time' in event:
            time_label = QLabel(f"⏰ {event.get('time', '')}", event_widget)
            time_label.setStyleSheet("color: #666;")
            layout.addWidget(time_label)
        
        # Add description (truncated)
        description = event.get('description', '')
        if description:
            # Truncate description if too long
            max_length = 50
            if len(description) > max_length:
                description = description[:max_length] + '...'
            
            description_label = QLabel(f"📝 {description}", event_widget)
            description_label.setStyleSheet("color: #333; font-size: 9pt;")
            description_label.setWordWrap(True)
            layout.addWidget(description_label)
        
        # Add to container (inserir no início do layout, antes do stretch)
        layout_count = self.events_container.layout().count()
        if layout_count > 0:
            # Insere antes do último item (que deve ser o stretch)
            self.events_container.layout().insertWidget(layout_count - 1, event_widget)
        else:
            # Se o layout estiver vazio, apenas adiciona
            self.events_container.layout().addWidget(event_widget)
    
    def _show_event_context_menu(self, position, event: Dict[str, Any]):
        """Show context menu for the event.
        
        Args:
            position: The position where to show the menu
            event: The event data
        """
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self._edit_event(event))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_event(event))
        menu.addAction(delete_action)
        
        # Show the menu
        sender = self.sender()
        menu.exec_(sender.mapToGlobal(position))
    
    def _add_event(self):
        """Add a new event."""
        # Create dialog
        dialog = EventDialog(self)
        
        # Set the date to the current selected date
        dialog.date_input.setDate(self.current_date)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get event data
            event_data = dialog.get_event_data()
            
            # Validate title
            if not event_data.get('title'):
                QMessageBox.warning(self, "Missing Title", "Please enter a title for the event.")
                return
            
            # Create event
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                # Parse the date string to a date object
                date_str = event_data.get('date')
                time_str = event_data.get('time')
                event_date = None
                
                if date_str:
                    from shared.utils import DateUtils
                    event_date = DateUtils.parse_date(date_str)
                
                # If date parsing failed, use current date
                if event_date is None:
                    from shared.utils import DateUtils
                    event_date = DateUtils.get_current_date()
                
                # Combine date with time if available
                event_datetime = event_date
                if time_str:
                    from shared.utils import DateUtils
                    time_obj = DateUtils.parse_time(time_str)
                    if time_obj and event_date:
                        from datetime import datetime
                        event_datetime = datetime.combine(event_date, time_obj)
                
                event = event_controller.create_event(
                    title=event_data.get('title'),
                    description=event_data.get('description') or '',
                    event_date=event_datetime
                )
                
                if event:
                    # Refresh the calendar
                    self.refresh()
                    
                    # Emit signal
                    self.event_created.emit(event['id'])
    
    def _edit_event(self, event: Dict[str, Any]):
        """Edit an existing event.
        
        Args:
            event: The event data
        """
        # Create dialog
        dialog = EventDialog(self, event)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get event data
            event_data = dialog.get_event_data()
            
            # Validate title
            if not event_data.get('title'):
                QMessageBox.warning(self, "Missing Title", "Please enter a title for the event.")
                return
            
            # Update event
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                # Parse the date string to a date object
                date_str = event_data.get('date')
                time_str = event_data.get('time')
                event_date = None
                
                if date_str:
                    from shared.utils import DateUtils
                    event_date = DateUtils.parse_date(date_str)
                
                # If date parsing failed, use current date
                if event_date is None:
                    from shared.utils import DateUtils
                    event_date = DateUtils.get_current_date()
                
                # Combine date with time if available
                event_datetime = event_date
                if time_str:
                    from shared.utils import DateUtils
                    time_obj = DateUtils.parse_time(time_str)
                    if time_obj and event_date:
                        from datetime import datetime
                        event_datetime = datetime.combine(event_date, time_obj)
                
                updated = event_controller.update_event(
                    event_id=event['id'],
                    title=event_data.get('title'),
                    event_date=event_datetime,
                    description=event_data.get('description') or ''
                )
                
                # Get the updated event data if update was successful
                updated_event = event_controller.get_event_by_id(event['id']) if updated else None
                
                if updated_event:
                    # Refresh the calendar
                    self.refresh()
                    
                    # Emit signal
                    self.event_updated.emit(updated_event['id'])
    
    def _delete_event(self, event: Dict[str, Any]):
        """Delete an event.
        
        Args:
            event: The event data
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this event? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event_controller = self.controllers.get('event_controller')
            if event_controller:
                event_id = event['id']
                if event_controller.delete_event(event_id):
                    # Refresh the calendar
                    self.refresh()
                    
                    # Emit signal
                    self.event_deleted.emit(event_id)