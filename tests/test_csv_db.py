from unittest.mock import patch, mock_open, MagicMock
from csv_db import add_user, USERS_FILE

def test_add_user():
    email = "test@example.com"
    name = "Test User"
    password = "password123"

    mocked_open = mock_open()
    mocked_writer = MagicMock()

    with patch('builtins.open', mocked_open), \
         patch('csv.writer', return_value=mocked_writer) as mock_csv_writer:

        add_user(email, name, password)

        # Assert open was called correctly
        mocked_open.assert_called_once_with(USERS_FILE, mode='a', newline='')

        # Assert csv.writer was called with the file object
        mock_csv_writer.assert_called_once_with(mocked_open())

        # Assert writerow was called with the correct data
        mocked_writer.writerow.assert_called_once_with([email, name, password])
