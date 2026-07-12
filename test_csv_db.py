import os
from unittest.mock import patch, mock_open
import csv_db

def test_init_csv_both_files_exist():
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('csv.writer') as mock_writer:

        mock_exists.return_value = True

        csv_db.init_csv()

        mock_exists.assert_any_call(csv_db.USERS_FILE)
        mock_exists.assert_any_call(csv_db.EXPENSES_FILE)
        mock_file.assert_not_called()
        mock_writer.assert_not_called()

def test_init_csv_neither_file_exists():
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('csv.writer') as mock_writer:

        mock_exists.return_value = False
        mock_writer_instance = mock_writer.return_value

        csv_db.init_csv()

        mock_exists.assert_any_call(csv_db.USERS_FILE)
        mock_exists.assert_any_call(csv_db.EXPENSES_FILE)

        assert mock_file.call_count == 2
        mock_file.assert_any_call(csv_db.USERS_FILE, mode='w', newline='')
        mock_file.assert_any_call(csv_db.EXPENSES_FILE, mode='w', newline='')

        assert mock_writer_instance.writerow.call_count == 2
        mock_writer_instance.writerow.assert_any_call(['email', 'name', 'password'])
        mock_writer_instance.writerow.assert_any_call(['id', 'email', 'amount', 'category', 'date', 'description'])

def test_init_csv_only_users_file_exists():
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('csv.writer') as mock_writer:

        def side_effect(path):
            if path == csv_db.USERS_FILE:
                return True
            return False
        mock_exists.side_effect = side_effect
        mock_writer_instance = mock_writer.return_value

        csv_db.init_csv()

        mock_exists.assert_any_call(csv_db.USERS_FILE)
        mock_exists.assert_any_call(csv_db.EXPENSES_FILE)

        assert mock_file.call_count == 1
        mock_file.assert_called_once_with(csv_db.EXPENSES_FILE, mode='w', newline='')

        assert mock_writer_instance.writerow.call_count == 1
        mock_writer_instance.writerow.assert_called_once_with(['id', 'email', 'amount', 'category', 'date', 'description'])

def test_init_csv_only_expenses_file_exists():
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('csv.writer') as mock_writer:

        def side_effect(path):
            if path == csv_db.EXPENSES_FILE:
                return True
            return False
        mock_exists.side_effect = side_effect
        mock_writer_instance = mock_writer.return_value

        csv_db.init_csv()

        mock_exists.assert_any_call(csv_db.USERS_FILE)
        mock_exists.assert_any_call(csv_db.EXPENSES_FILE)

        assert mock_file.call_count == 1
        mock_file.assert_called_once_with(csv_db.USERS_FILE, mode='w', newline='')

        assert mock_writer_instance.writerow.call_count == 1
        mock_writer_instance.writerow.assert_called_once_with(['email', 'name', 'password'])
