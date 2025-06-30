import os
import sqlite3
from datetime import datetime

class DatabaseInitializer:
    """Class responsible for initializing the SQLite database."""
    
    def __init__(self, db_path):
        """Initialize with the database file path."""
        self.db_path = db_path
        self.connection = None
    
    def initialize_database(self):
        """Create the database and tables if they don't exist."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to the database (creates it if it doesn't exist)
        self.connection = sqlite3.connect(self.db_path)
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self._create_tables()
        
        # Initialize with default data if needed
        self._initialize_default_data()
        
        return self.connection
    
    def _create_tables(self):
        """Create all required tables."""
        cursor = self.connection.cursor()
        
        # Create folders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            path TEXT NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        )
        """)
        
        # Create notes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL,
            folder_id INTEGER NOT NULL,
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
        )
        """)
        
        # Create attachments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """)
        
        # Create events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        """)
        
        self.connection.commit()
    
    def _initialize_default_data(self):
        """Initialize the database with default data if it's empty."""
        cursor = self.connection.cursor()
        
        # Check if the folders table is empty
        cursor.execute("SELECT COUNT(*) FROM folders")
        folder_count = cursor.fetchone()[0]
        
        if folder_count == 0:
            # Create the default 'Geral' (General) folder
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO folders (name, parent_id, path) VALUES (?, ?, ?)",
                ("Geral", None, "/Geral")
            )
            
            # Create a welcome note in the General folder
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, modified_at, folder_id) VALUES (?, ?, ?, ?, ?)",
                (
                    "Bem-vindo ao NotePad",
                    "Bem-vindo ao seu novo aplicativo de notas! Este é um exemplo de nota.",
                    now,
                    now,
                    1  # ID of the General folder
                )
            )
            
            self.connection.commit()