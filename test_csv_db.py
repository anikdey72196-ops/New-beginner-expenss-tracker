import unittest
from unittest.mock import patch
import csv_db

class TestCsvDb(unittest.TestCase):
    @patch('csv_db.get_expenses_by_user')
    def test_get_dashboard_stats_invalid_amount(self, mock_get_expenses):
        # Setup mock to return an invalid amount (non-float string)
        mock_get_expenses.return_value = [
            {'amount': 'invalid', 'category': 'Health', 'date': '2023-01-01'}
        ]

        # This should not raise a ValueError, it should handle the exception and set amount to 0.0
        stats = csv_db.get_dashboard_stats('test@example.com')

        # Verify the structure and some expected values based on the logic
        self.assertIn('overall_score', stats)
        self.assertEqual(stats['overall_score'], 6.0) # 5.0 + 1 for Health
        self.assertEqual(stats['last_month_total'], 0.0)

if __name__ == '__main__':
    unittest.main()
