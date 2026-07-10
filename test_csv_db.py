import unittest
import os
import tempfile
import csv_db
import datetime
from unittest.mock import patch

class BuggyDate(datetime.date):
    def replace(self, *args, **kwargs):
        raise ValueError("Simulated replace error")

class TestCsvDb(unittest.TestCase):
    def setUp(self):
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.users_file = os.path.join(self.temp_dir.name, 'users.csv')
        self.expenses_file = os.path.join(self.temp_dir.name, 'expenses.csv')

        # Override the file paths in csv_db
        csv_db.USERS_FILE = self.users_file
        csv_db.EXPENSES_FILE = self.expenses_file

        # Initialize files
        csv_db.init_csv()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_csv(self):
        self.assertTrue(os.path.exists(self.users_file))
        self.assertTrue(os.path.exists(self.expenses_file))

    def test_init_csv_already_exists(self):
        # calling it again shouldn't break anything
        csv_db.init_csv()
        self.assertTrue(os.path.exists(self.users_file))
        self.assertTrue(os.path.exists(self.expenses_file))

    def test_add_and_get_user(self):
        csv_db.add_user('test@example.com', 'Test User', 'password123')
        user = csv_db.get_user_by_email('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], 'test@example.com')
        self.assertEqual(user['name'], 'Test User')
        self.assertEqual(user['password'], 'password123')

    def test_get_nonexistent_user(self):
        user = csv_db.get_user_by_email('nobody@example.com')
        self.assertIsNone(user)

    def test_get_user_no_file(self):
        os.remove(self.users_file)
        user = csv_db.get_user_by_email('nobody@example.com')
        self.assertIsNone(user)

    def test_add_and_get_expense(self):
        expense_id = csv_db.add_expense('test@example.com', '100.0', 'Food', '2023-01-01', 'Lunch')
        self.assertIsNotNone(expense_id)

        expense = csv_db.get_expense_by_id(expense_id, 'test@example.com')
        self.assertIsNotNone(expense)
        self.assertEqual(expense['amount'], '100.0')
        self.assertEqual(expense['category'], 'Food')

        expenses = csv_db.get_expenses_by_user('test@example.com')
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0]['id'], expense_id)

    def test_get_expense_no_file(self):
        os.remove(self.expenses_file)
        expense = csv_db.get_expense_by_id('some_id', 'test@example.com')
        self.assertIsNone(expense)

    def test_get_expenses_by_user_no_file(self):
        os.remove(self.expenses_file)
        expenses = csv_db.get_expenses_by_user('test@example.com')
        self.assertEqual(expenses, [])

    def test_update_expense(self):
        expense_id = csv_db.add_expense('test@example.com', '100.0', 'Food', '2023-01-01', 'Lunch')

        updated = csv_db.update_expense(expense_id, 'test@example.com', '150.0', 'Dinner', '2023-01-02', 'Dinner time')
        self.assertTrue(updated)

        expense = csv_db.get_expense_by_id(expense_id, 'test@example.com')
        self.assertEqual(expense['amount'], '150.0')
        self.assertEqual(expense['category'], 'Dinner')
        self.assertEqual(expense['date'], '2023-01-02')
        self.assertEqual(expense['description'], 'Dinner time')

    def test_update_expense_nonexistent(self):
        updated = csv_db.update_expense('fake_id', 'test@example.com', '150.0', 'Dinner', '2023-01-02', 'Dinner time')
        self.assertFalse(updated)

    def test_update_expense_no_file(self):
        os.remove(self.expenses_file)
        updated = csv_db.update_expense('fake_id', 'test@example.com', '150.0', 'Dinner', '2023-01-02', 'Dinner time')
        self.assertFalse(updated)

    def test_update_expense_other_expenses_preserved(self):
        exp1 = csv_db.add_expense('test@example.com', '100.0', 'Food', '2023-01-01', 'Lunch')
        exp2 = csv_db.add_expense('test@example.com', '200.0', 'Food', '2023-01-02', 'Dinner')

        updated = csv_db.update_expense(exp1, 'test@example.com', '150.0', 'Food', '2023-01-01', 'Lunch')
        self.assertTrue(updated)

        # Verify exp2 is still there
        expense = csv_db.get_expense_by_id(exp2, 'test@example.com')
        self.assertEqual(expense['amount'], '200.0')

    def test_delete_expense(self):
        expense_id = csv_db.add_expense('test@example.com', '100.0', 'Food', '2023-01-01', 'Lunch')
        deleted = csv_db.delete_expense(expense_id, 'test@example.com')
        self.assertTrue(deleted)

        expense = csv_db.get_expense_by_id(expense_id, 'test@example.com')
        self.assertIsNone(expense)

    def test_delete_expense_other_expenses_preserved(self):
        exp1 = csv_db.add_expense('test@example.com', '100.0', 'Food', '2023-01-01', 'Lunch')
        exp2 = csv_db.add_expense('test@example.com', '200.0', 'Food', '2023-01-02', 'Dinner')

        deleted = csv_db.delete_expense(exp1, 'test@example.com')
        self.assertTrue(deleted)

        # Verify exp2 is still there
        expense = csv_db.get_expense_by_id(exp2, 'test@example.com')
        self.assertEqual(expense['amount'], '200.0')

    def test_delete_expense_nonexistent(self):
        deleted = csv_db.delete_expense('fake_id', 'test@example.com')
        self.assertFalse(deleted)

    def test_delete_expense_no_file(self):
        os.remove(self.expenses_file)
        deleted = csv_db.delete_expense('fake_id', 'test@example.com')
        self.assertFalse(deleted)

    def test_get_dashboard_stats(self):
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')

        csv_db.add_expense('test@example.com', '50.0', 'Education', today_str, 'Books')
        csv_db.add_expense('test@example.com', '20.0', 'Shopping', today_str, 'Clothes')

        stats = csv_db.get_dashboard_stats('test@example.com')

        self.assertIn('overall_score', stats)
        self.assertIn('today_score', stats)
        self.assertIn('last_month_total', stats)
        self.assertIn('daily_avg_score', stats)

    def test_get_dashboard_stats_no_expenses(self):
        stats = csv_db.get_dashboard_stats('test@example.com')
        self.assertEqual(stats['overall_score'], 5.0)
        self.assertEqual(stats['today_score'], 50)
        self.assertEqual(stats['last_month_total'], 0.0)
        self.assertEqual(stats['daily_avg_score'], 5.0)

    def test_get_dashboard_stats_invalid_data(self):
        # Adding an expense with invalid amount and date
        csv_db.add_expense('test@example.com', 'invalid_amount', 'Education', 'invalid_date', 'Books')

        stats = csv_db.get_dashboard_stats('test@example.com')

        # Valid category should still bump the score
        self.assertTrue(stats['overall_score'] > 5.0)
        # The amount exception will be caught and treated as 0.0
        # The date exception will be caught and treated as today
        self.assertTrue(stats['today_score'] > 50)

    def test_get_dashboard_stats_score_clamping(self):
        today_str = datetime.date.today().strftime('%Y-%m-%d')

        # Add lots of bad expenses to drive score below 0
        for _ in range(20):
            csv_db.add_expense('test@example.com', '10.0', 'Shopping', today_str, 'Junk')

        stats = csv_db.get_dashboard_stats('test@example.com')
        self.assertEqual(stats['overall_score'], 0.0)
        self.assertEqual(stats['today_score'], 0)

        # Add lots of good expenses to drive score above max
        for _ in range(20):
            csv_db.add_expense('test2@example.com', '10.0', 'Education', today_str, 'Books')

        stats2 = csv_db.get_dashboard_stats('test2@example.com')
        self.assertEqual(stats2['overall_score'], 10.0)
        self.assertEqual(stats2['today_score'], 100)

    def test_get_dashboard_stats_last_month(self):
        today = datetime.date.today()
        # Calculate a date from last month
        first_of_this_month = today.replace(day=1)
        last_month_date = first_of_this_month - datetime.timedelta(days=15)
        last_month_str = last_month_date.strftime('%Y-%m-%d')

        csv_db.add_expense('test@example.com', '100.0', 'Education', last_month_str, 'Books')

        stats = csv_db.get_dashboard_stats('test@example.com')
        self.assertEqual(stats['last_month_total'], 100.0)

    @patch('csv_db.datetime')
    def test_get_dashboard_stats_last_month_exception(self, mock_datetime):
        # We need to simulate the exception block
        # mock_datetime.date.today.return_value = BuggyDate(2023, 1, 15)
        mock_datetime.date.today.return_value = BuggyDate(2023, 1, 15)
        # Also need strptime
        mock_datetime.datetime.strptime = datetime.datetime.strptime
        mock_datetime.timedelta = datetime.timedelta

        csv_db.add_expense('test@example.com', '100.0', 'Education', '2023-01-15', 'Books')

        stats = csv_db.get_dashboard_stats('test@example.com')
        self.assertEqual(stats['last_month_total'], 100.0)

if __name__ == '__main__':
    unittest.main()
