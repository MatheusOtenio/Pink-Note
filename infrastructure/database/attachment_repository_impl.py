import os
from datetime import datetime
from typing import List, Optional

from domain.entities.attachment import Attachment
from domain.repositories.attachment_repository import AttachmentRepository

class AttachmentRepositoryImpl(AttachmentRepository):
    """SQLite implementation of the attachment repository."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_attachments_for_note(self, note_id: int) -> List[Attachment]:
        """Retrieve all attachments for a specific note."""
        cursor = self.db.cursor()
        
        if note_id is None:
            # Get all attachments if note_id is None
            cursor.execute(
                "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments ORDER BY created_at DESC"
            )
        else:
            cursor.execute(
                "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments WHERE note_id = ? ORDER BY created_at DESC",
                (note_id,)
            )
        
        attachments = []
        for row in cursor.fetchall():
            attachment = Attachment(
                id=row[0],
                note_id=row[1],
                file_path=row[2],
                file_name=row[3],
                file_type=row[4],
                created_at=datetime.fromisoformat(row[5])
            )
            attachments.append(attachment)
        
        return attachments
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Retrieve an attachment by its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, note_id, file_path, file_name, file_type, created_at FROM attachments WHERE id = ?",
            (attachment_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return Attachment(
            id=row[0],
            note_id=row[1],
            file_path=row[2],
            file_name=row[3],
            file_type=row[4],
            created_at=datetime.fromisoformat(row[5])
        )
    
    def add_attachment(self, attachment: Attachment) -> int:
        """Add a new attachment and return its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO attachments (note_id, file_path, file_name, file_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                attachment.note_id,
                attachment.file_path,
                attachment.file_name,
                attachment.file_type,
                attachment.created_at.isoformat()
            )
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def delete_attachment(self, attachment_id: int) -> bool:
        """Delete an attachment by its ID and return success status."""
        cursor = self.db.cursor()
        
        # Get the file path to delete the physical file
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        
        file_path = row[0]
        
        # Delete the attachment record
        cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        
        # Delete the physical file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                # Log the error but continue with the database deletion
                pass
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """Get the file system path for an attachment."""
        cursor = self.db.cursor()
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return row[0]