import unittest
from unittest.mock import patch, mock_open, MagicMock
import csv_db
import uuid

class TestCsvDb(unittest.TestCase):

    @patch('csv_db.csv.writer')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv_db.uuid.uuid4')
    def test_add_expense(self, mock_uuid4, mock_open_file, mock_csv_writer):
        # Setup mock UUID
        fake_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_uuid4.return_value = fake_uuid

        # Setup mock writer
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance

        # Define test inputs
        email = 'test@example.com'
        amount = 100.50
        category = 'Food'
        date = '2023-10-01'
        description = 'Lunch'

        # Call the function
        result = csv_db.add_expense(email, amount, category, date, description)

        # Assertions
        mock_uuid4.assert_called_once()
        mock_open_file.assert_called_once_with(csv_db.EXPENSES_FILE, mode='a', newline='')
        mock_csv_writer.assert_called_once_with(mock_open_file())
        mock_writer_instance.writerow.assert_called_once_with([
            str(fake_uuid), email, amount, category, date, description
        ])

        self.assertEqual(result, str(fake_uuid))

if __name__ == '__main__':
    unittest.main()
