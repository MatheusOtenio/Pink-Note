from datetime import datetime
from typing import List, Optional

from domain.entities.note import Note
from domain.repositories.note_repository import NoteRepository

class NoteRepositoryImpl(NoteRepository):
    """SQLite implementation of the note repository."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Retrieve all notes, optionally filtered by folder ID."""
        cursor = self.db.cursor()
        
        if folder_id is not None:
            cursor.execute(
                "SELECT id, title, content, created_at, modified_at, folder_id FROM notes WHERE folder_id = ? ORDER BY modified_at DESC",
                (folder_id,)
            )
        else:
            cursor.execute(
                "SELECT id, title, content, created_at, modified_at, folder_id FROM notes ORDER BY modified_at DESC"
            )
        
        notes = []
        for row in cursor.fetchall():
            note = Note(
                id=row[0],
                title=row[1],
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
                modified_at=datetime.fromisoformat(row[4]),
                folder_id=row[5]
            )
            notes.append(note)
        
        return notes
    
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Retrieve a note by its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, title, content, created_at, modified_at, folder_id FROM notes WHERE id = ?",
            (note_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        note = Note(
            id=row[0],
            title=row[1],
            content=row[2],
            created_at=datetime.fromisoformat(row[3]),
            modified_at=datetime.fromisoformat(row[4]),
            folder_id=row[5]
        )
        
        # Get attachment IDs for this note
        cursor.execute("SELECT id FROM attachments WHERE note_id = ?", (note_id,))
        attachment_ids = [row[0] for row in cursor.fetchall()]
        note.attachment_ids = attachment_ids
        
        return note
    
    def add_note(self, note: Note) -> int:
        """Add a new note and return its ID."""
        cursor = self.db.cursor()
        
        # Ensure folder_id is set (default to 'Geral' folder with ID 1)
        folder_id = note.folder_id if note.folder_id is not None else 1
        
        cursor.execute(
            "INSERT INTO notes (title, content, created_at, modified_at, folder_id) VALUES (?, ?, ?, ?, ?)",
            (note.title, note.content, note.created_at.isoformat(), note.modified_at.isoformat(), folder_id)
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def update_note(self, note: Note) -> bool:
        """Update an existing note and return success status."""
        if note.id is None:
            return False
        
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE notes SET title = ?, content = ?, modified_at = ? WHERE id = ?",
            (note.title, note.content, note.modified_at.isoformat(), note.id)
        )
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by its ID and return success status."""
        cursor = self.db.cursor()
        
        # First, delete all attachments for this note
        cursor.execute("SELECT id FROM attachments WHERE note_id = ?", (note_id,))
        attachment_ids = [row[0] for row in cursor.fetchall()]
        
        for attachment_id in attachment_ids:
            # Get the file path to delete the physical file
            cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
            file_path = cursor.fetchone()[0]
            
            # Delete the attachment record
            cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            
            # Delete the physical file (this would be handled by a file system service in a real implementation)
            # os.remove(file_path)
        
        # Now delete the note
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def move_note(self, note_id: int, folder_id: int) -> bool:
        """Move a note to a different folder and return success status."""
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE notes SET folder_id = ?, modified_at = ? WHERE id = ?",
            (folder_id, datetime.now().isoformat(), note_id)
        )
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def search_notes(self, criteria) -> List[Note]:
        """Search for notes based on the provided criteria."""
        cursor = self.db.cursor()
        search_term = criteria.search_term
        
        # Apply case sensitivity
        if not criteria.case_sensitive:
            search_term = search_term.lower()
            title_clause = "LOWER(n.title) LIKE ?"
            content_clause = "LOWER(n.content) LIKE ?"
        else:
            title_clause = "n.title LIKE ?"
            content_clause = "n.content LIKE ?"
        
        search_pattern = f"%{search_term}%"
        
        # Build the query based on search criteria
        query = """SELECT n.id, n.title, n.content, n.created_at, n.modified_at, n.folder_id, f.name as folder_name 
                 FROM notes n 
                 JOIN folders f ON n.folder_id = f.id 
                 WHERE """
        
        conditions = []
        params = []
        
        # Add title condition if needed
        if criteria.include_title:
            conditions.append(f"({title_clause})")
            params.append(search_pattern)
        
        # Add content condition if needed
        if criteria.include_content:
            conditions.append(f"({content_clause})")
            params.append(search_pattern)
        
        # Combine conditions with OR
        if conditions:
            query += " OR ".join(conditions)
        else:
            # If no conditions, return empty list
            return []
        
        # Add folder filter if specified
        if criteria.folder_ids:
            placeholders = ", ".join(["?" for _ in criteria.folder_ids])
            query += f" AND n.folder_id IN ({placeholders})"
            params.extend(criteria.folder_ids)
        
        query += " ORDER BY n.modified_at DESC"
        
        cursor.execute(query, params)
        
        notes = []
        for row in cursor.fetchall():
            note = Note(
                id=row[0],
                title=row[1],
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
                modified_at=datetime.fromisoformat(row[4]),
                folder_id=row[5]
            )
            # Add folder name as a property for display purposes
            note.folder_name = row[6]
            notes.append(note)
        
        return notes