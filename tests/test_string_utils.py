import unittest
from shared.utils.string_utils import StringUtils

class TestStringUtils(unittest.TestCase):
    """Test cases for StringUtils class."""
    
    def test_truncate(self):
        """Test the truncate method."""
        # Test normal truncation
        self.assertEqual(StringUtils.truncate("Hello, world!", 5), "Hello...")
        
        # Test no truncation needed
        self.assertEqual(StringUtils.truncate("Hello", 10), "Hello")
        
        # Test custom suffix
        self.assertEqual(StringUtils.truncate("Hello, world!", 5, "..."), "Hello...")
        
        # Test empty string
        self.assertEqual(StringUtils.truncate("", 5), "")
    
    def test_is_empty_or_whitespace(self):
        """Test the is_empty_or_whitespace method."""
        # Test empty string
        self.assertTrue(StringUtils.is_empty_or_whitespace(""))
        
        # Test whitespace string
        self.assertTrue(StringUtils.is_empty_or_whitespace(" \t\n"))
        
        # Test non-empty string
        self.assertFalse(StringUtils.is_empty_or_whitespace("Hello"))
    
    def test_normalize_for_search(self):
        """Test the normalize_for_search method."""
        # Test case insensitive normalization
        self.assertEqual(StringUtils.normalize_for_search("  Hello,  World! "), "hello, world!")
        
        # Test case sensitive normalization
        self.assertEqual(StringUtils.normalize_for_search("  Hello,  World! ", True), "Hello, World!")
        
        # Test empty string
        self.assertEqual(StringUtils.normalize_for_search(""), "")

if __name__ == '__main__':
    unittest.main()