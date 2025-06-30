from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class SearchCriteria:
    """Value object representing search criteria for notes."""
    search_term: str
    folder_ids: List[int] = field(default_factory=list)  # Empty list means search all folders
    include_title: bool = True
    include_content: bool = True
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Validate the search criteria."""
        if not self.search_term.strip():
            raise ValueError("Search term cannot be empty")
        
        if not self.include_title and not self.include_content:
            raise ValueError("At least one of include_title or include_content must be True")
    
    @property
    def normalized_search_term(self) -> str:
        """Get the normalized search term based on case sensitivity."""
        if self.case_sensitive:
            return self.search_term
        return self.search_term.lower()