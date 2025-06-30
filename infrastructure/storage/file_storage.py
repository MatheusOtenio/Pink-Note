import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, Tuple

class FileStorage:
    """Class responsible for handling file storage operations."""
    
    def __init__(self, base_storage_path):
        """Initialize with the base storage directory path."""
        self.base_storage_path = base_storage_path
        
        # Ensure the storage directory exists
        os.makedirs(self.base_storage_path, exist_ok=True)
    
    def save_file(self, source_path: str, note_id: int) -> Tuple[str, str, str]:
        """Save a file to the storage directory and return its path, name, and type.
        
        Args:
            source_path: The path to the source file
            note_id: The ID of the note this file is attached to
            
        Returns:
            Tuple containing (file_path, file_name, file_type)
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Create a directory for the note's attachments if it doesn't exist
        note_dir = os.path.join(self.base_storage_path, f"note_{note_id}")
        os.makedirs(note_dir, exist_ok=True)
        
        # Get file name and extension
        file_name = os.path.basename(source_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Generate a unique filename to avoid collisions
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}{file_ext}"
        
        # Destination path
        dest_path = os.path.join(note_dir, unique_filename)
        
        # Copy the file
        shutil.copy2(source_path, dest_path)
        
        # Determine file type
        file_type = self._get_file_type(file_ext)
        
        return dest_path, file_name, file_type
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from the storage directory.
        
        Args:
            file_path: The path to the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            
            # Check if the directory is empty and remove it if it is
            dir_path = os.path.dirname(file_path)
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                
            return True
        except OSError:
            return False
    
    def _get_file_type(self, extension: str) -> str:
        """Determine the file type based on its extension.
        
        Args:
            extension: The file extension including the dot (e.g., '.pdf')
            
        Returns:
            A string representing the file type
        """
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
        document_extensions = [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"]
        spreadsheet_extensions = [".xls", ".xlsx", ".csv", ".ods"]
        presentation_extensions = [".ppt", ".pptx", ".odp"]
        
        if extension in image_extensions:
            return "image"
        elif extension in document_extensions:
            return "document"
        elif extension in spreadsheet_extensions:
            return "spreadsheet"
        elif extension in presentation_extensions:
            return "presentation"
        else:
            return "other"