import re
from typing import List, Optional

class StringUtils:
    """Utility class for string operations."""
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate a string to a maximum length and add a suffix if truncated.
        
        Args:
            text: The string to truncate
            max_length: The maximum length
            suffix: The suffix to add if truncated (default: '...')
            
        Returns:
            The truncated string
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def is_empty_or_whitespace(text: Optional[str]) -> bool:
        """Check if a string is None, empty, or contains only whitespace.
        
        Args:
            text: The string to check
            
        Returns:
            True if the string is None, empty, or contains only whitespace, False otherwise
        """
        return text is None or text.strip() == ''
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from a text by removing common words and punctuation.
        
        Args:
            text: The text to extract keywords from
            min_length: The minimum length of a keyword (default: 3)
            
        Returns:
            A list of keywords
        """
        if StringUtils.is_empty_or_whitespace(text):
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and replace with spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Common Portuguese stop words to filter out
        stop_words = {
            'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até',
            'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do',
            'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram', 'éramos',
            'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes', 'eu', 'foi',
            'fomos', 'for', 'foram', 'fosse', 'fossem', 'fui', 'há', 'isso', 'isto', 'já', 'lhe',
            'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito',
            'na', 'não', 'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos',
            'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por',
            'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sejam', 'sem', 'será',
            'serão', 'seu', 'seus', 'só', 'somos', 'sou', 'sua', 'suas', 'também', 'te', 'tem',
            'tém', 'temos', 'tenho', 'teu', 'teus', 'tu', 'tua', 'tuas', 'um', 'uma', 'você',
            'vocês', 'vos', 'vosso', 'vossos'
        }
        
        # Filter out stop words and words shorter than min_length
        keywords = [word for word in words if word not in stop_words and len(word) >= min_length]
        
        return keywords
    
    @staticmethod
    def normalize_for_search(text: str, case_sensitive: bool = False) -> str:
        """Normalize a string for search purposes.
        
        Args:
            text: The string to normalize
            case_sensitive: Whether to preserve case (default: False)
            
        Returns:
            The normalized string
        """
        if StringUtils.is_empty_or_whitespace(text):
            return ''
        
        # Remove extra whitespace
        normalized = ' '.join(text.split())
        
        # Convert to lowercase if not case sensitive
        if not case_sensitive:
            normalized = normalized.lower()
        
        return normalized
    
    @staticmethod
    def highlight_matches(text: str, search_term: str, case_sensitive: bool = False) -> str:
        """Highlight matches of a search term in a text using HTML.
        
        Args:
            text: The text to search in
            search_term: The search term to highlight
            case_sensitive: Whether the search is case sensitive (default: False)
            
        Returns:
            The text with matches highlighted using HTML span tags
        """
        if StringUtils.is_empty_or_whitespace(text) or StringUtils.is_empty_or_whitespace(search_term):
            return text
        
        # Escape HTML special characters
        escaped_text = StringUtils.escape_html(text)
        
        # Prepare the search term for regex
        escaped_search = re.escape(search_term)
        
        # Create the regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(f'({escaped_search})', flags)
        
        # Replace matches with highlighted version
        highlighted = pattern.sub(r'<span class="highlight">\1</span>', escaped_text)
        
        return highlighted
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters in a string.
        
        Args:
            text: The string to escape
            
        Returns:
            The escaped string
        """
        if StringUtils.is_empty_or_whitespace(text):
            return ''
        
        # Replace HTML special characters with their escaped versions
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text