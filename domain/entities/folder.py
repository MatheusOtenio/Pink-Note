from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Folder:
    """Entity representing a folder in the hierarchical structure."""
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None  # None for root folders
    path: str = ""  # Full path representation (e.g., "Root/Subfolder/SubSubfolder")
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root-level folder."""
        return self.parent_id is None
    
    def get_folder_name(self) -> str:
        """Get the folder name from the path."""
        if not self.path:
            return self.name
        return self.path.split("/")[-1]
    
    def get_parent_path(self) -> str:
        """Get the parent path."""
        if not self.path or "/" not in self.path:
            return ""
        return "/".join(self.path.split("/")[:-1])