from typing import List, Optional

from domain.entities.folder import Folder
from domain.repositories.folder_repository import FolderRepository

class FolderRepositoryImpl(FolderRepository):
    """SQLite implementation of the folder repository."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_folders(self) -> List[Folder]:
        """Retrieve all folders."""
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, parent_id, path FROM folders ORDER BY path")
        
        folders = []
        for row in cursor.fetchall():
            folder = Folder(
                id=row[0],
                name=row[1],
                parent_id=row[2],
                path=row[3]
            )
            folders.append(folder)
        
        return folders
    
    def get_folder_by_id(self, folder_id: int) -> Optional[Folder]:
        """Retrieve a folder by its ID."""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, name, parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return Folder(
            id=row[0],
            name=row[1],
            parent_id=row[2],
            path=row[3]
        )
    
    def get_subfolders(self, parent_id: Optional[int] = None) -> List[Folder]:
        """Retrieve all subfolders of a given parent folder."""
        cursor = self.db.cursor()
        
        if parent_id is None:
            cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id IS NULL ORDER BY name"
            )
        else:
            cursor.execute(
                "SELECT id, name, parent_id, path FROM folders WHERE parent_id = ? ORDER BY name",
                (parent_id,)
            )
        
        folders = []
        for row in cursor.fetchall():
            folder = Folder(
                id=row[0],
                name=row[1],
                parent_id=row[2],
                path=row[3]
            )
            folders.append(folder)
        
        return folders
    
    def create_folder(self, folder: Folder) -> int:
        """Create a new folder and return its ID."""
        cursor = self.db.cursor()
        
        # Check if a folder with the same name already exists at the same level
        if folder.parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL",
                (folder.name,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ?",
                (folder.name, folder.parent_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"A folder named '{folder.name}' already exists at this level")
        
        # Calculate the full path for the new folder
        path = folder.name
        if folder.parent_id is not None:
            cursor.execute("SELECT path FROM folders WHERE id = ?", (folder.parent_id,))
            parent_path = cursor.fetchone()[0]
            path = f"{parent_path}/{folder.name}"
        
        # Insert the new folder
        cursor.execute(
            "INSERT INTO folders (name, parent_id, path) VALUES (?, ?, ?)",
            (folder.name, folder.parent_id, path)
        )
        
        self.db.commit()
        return cursor.lastrowid
    
    def rename_folder(self, folder_id: int, new_name: str) -> bool:
        """Rename a folder and return success status."""
        cursor = self.db.cursor()
        
        # Get the current folder information
        cursor.execute(
            "SELECT parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        
        parent_id, old_path = row
        
        # Check if a folder with the same name already exists at the same level
        if parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                (new_name, folder_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                (new_name, parent_id, folder_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"A folder named '{new_name}' already exists at this level")
        
        # Calculate the new path
        old_name = old_path.split('/')[-1]
        new_path = old_path.replace(old_name, new_name)
        
        # Start a transaction
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Update the folder name and path
            cursor.execute(
                "UPDATE folders SET name = ?, path = ? WHERE id = ?",
                (new_name, new_path, folder_id)
            )
            
            # Update the paths of all subfolders
            cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (f"{old_path}/%",)
            )
            
            for subfolder_id, subfolder_path in cursor.fetchall():
                new_subfolder_path = subfolder_path.replace(old_path, new_path)
                cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder and return success status."""
        cursor = self.db.cursor()
        
        # Check if this is the 'Geral' folder (ID 1), which cannot be deleted
        if folder_id == 1:
            return False
        
        # Get all notes in this folder and its subfolders
        cursor.execute(
            """SELECT n.id 
               FROM notes n 
               JOIN folders f ON n.folder_id = f.id 
               WHERE f.id = ? OR f.path LIKE (SELECT path || '/%' FROM folders WHERE id = ?)""",
            (folder_id, folder_id)
        )
        
        note_ids = [row[0] for row in cursor.fetchall()]
        
        # Start a transaction
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Move all notes to the 'Geral' folder (ID 1)
            for note_id in note_ids:
                cursor.execute(
                    "UPDATE notes SET folder_id = 1 WHERE id = ?",
                    (note_id,)
                )
            
            # Delete the folder (subfolders will be deleted via ON DELETE CASCADE)
            cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def move_folder(self, folder_id: int, new_parent_id: Optional[int]) -> bool:
        """Move a folder to a new parent and return success status."""
        cursor = self.db.cursor()
        
        # Check if this is the 'Geral' folder (ID 1), which cannot be moved
        if folder_id == 1:
            return False
        
        # Get the current folder information
        cursor.execute(
            "SELECT name, parent_id, path FROM folders WHERE id = ?",
            (folder_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        
        name, old_parent_id, old_path = row
        
        # Check if the folder is already at the requested location
        if old_parent_id == new_parent_id:
            return True
        
        # Check if the new parent exists (if not None)
        if new_parent_id is not None:
            cursor.execute("SELECT id FROM folders WHERE id = ?", (new_parent_id,))
            if cursor.fetchone() is None:
                return False
            
            # Check if the new parent is the folder itself or one of its subfolders
            if new_parent_id == folder_id:
                return False
            
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE id = ? AND path LIKE ?",
                (new_parent_id, f"{old_path}/%")
            )
            if cursor.fetchone()[0] > 0:
                return False
        
        # Check if a folder with the same name already exists at the destination
        if new_parent_id is None:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id IS NULL AND id != ?",
                (name, folder_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM folders WHERE name = ? AND parent_id = ? AND id != ?",
                (name, new_parent_id, folder_id)
            )
        
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"A folder named '{name}' already exists at the destination")
        
        # Calculate the new path
        new_path = name
        if new_parent_id is not None:
            cursor.execute("SELECT path FROM folders WHERE id = ?", (new_parent_id,))
            parent_path = cursor.fetchone()[0]
            new_path = f"{parent_path}/{name}"
        
        # Start a transaction
        self.db.execute("BEGIN TRANSACTION")
        
        try:
            # Update the folder's parent and path
            cursor.execute(
                "UPDATE folders SET parent_id = ?, path = ? WHERE id = ?",
                (new_parent_id, new_path, folder_id)
            )
            
            # Update the paths of all subfolders
            cursor.execute(
                "SELECT id, path FROM folders WHERE path LIKE ?",
                (f"{old_path}/%",)
            )
            
            for subfolder_id, subfolder_path in cursor.fetchall():
                new_subfolder_path = subfolder_path.replace(old_path, new_path)
                cursor.execute(
                    "UPDATE folders SET path = ? WHERE id = ?",
                    (new_subfolder_path, subfolder_id)
                )
            
            self.db.execute("COMMIT")
            return True
        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e
    
    def get_folder_note_count(self, folder_id: int) -> int:
        """Get the number of notes in a folder."""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes WHERE folder_id = ?", (folder_id,))
        return cursor.fetchone()[0]