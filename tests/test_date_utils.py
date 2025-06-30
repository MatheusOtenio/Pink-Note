import unittest
from datetime import datetime, date, timedelta
from shared.utils.date_utils import DateUtils

class TestDateUtils(unittest.TestCase):
    """Test cases for DateUtils class."""
    
    def test_format_date(self):
        """Test the format_date method."""
        # Create a test date
        test_date = date(2023, 5, 15)
        
        # Test default format
        self.assertEqual(DateUtils.format_date(test_date), "15/05/2023")
        
        # Test custom format
        self.assertEqual(DateUtils.format_date(test_date, "%Y-%m-%d"), "2023-05-15")
    
    def test_parse_date(self):
        """Test the parse_date method."""
        # Test default format
        parsed_date = DateUtils.parse_date("15/05/2023")
        self.assertEqual(parsed_date, date(2023, 5, 15))
        
        # Test custom format
        parsed_date = DateUtils.parse_date("2023-05-15", "%Y-%m-%d")
        self.assertEqual(parsed_date, date(2023, 5, 15))
        
        # Test invalid date
        self.assertIsNone(DateUtils.parse_date("invalid date"))
    
    def test_get_month_range(self):
        """Test the get_month_range method."""
        # Test for May 2023
        start_date, end_date = DateUtils.get_month_range(2023, 5)
        
        self.assertEqual(start_date, date(2023, 5, 1))
        self.assertEqual(end_date, date(2023, 5, 31))
        
        # Test for February 2023 (non-leap year)
        start_date, end_date = DateUtils.get_month_range(2023, 2)
        
        self.assertEqual(start_date, date(2023, 2, 1))
        self.assertEqual(end_date, date(2023, 2, 28))
        
        # Test for February 2024 (leap year)
        start_date, end_date = DateUtils.get_month_range(2024, 2)
        
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

if __name__ == '__main__':
    unittest.main()