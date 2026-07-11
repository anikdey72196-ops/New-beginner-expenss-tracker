import pytest
import tempfile
import os
import app
import csv_db

@pytest.fixture
def client():
    # Setup temp DBs
    fd_users, path_users = tempfile.mkstemp()
    fd_expenses, path_expenses = tempfile.mkstemp()

    # Save original paths
    orig_users = csv_db.USERS_FILE
    orig_expenses = csv_db.EXPENSES_FILE

    # Patch paths
    csv_db.USERS_FILE = path_users
    csv_db.EXPENSES_FILE = path_expenses

    # Re-init DB
    os.remove(path_users)
    os.remove(path_expenses)
    csv_db.init_csv()

    app.app.config['TESTING'] = True
    app.app.config['WTF_CSRF_ENABLED'] = False

    with app.app.test_client() as client:
        with app.app.app_context():
            yield client

    # Teardown
    os.close(fd_users)
    os.close(fd_expenses)
    os.remove(path_users)
    os.remove(path_expenses)
    csv_db.USERS_FILE = orig_users
    csv_db.EXPENSES_FILE = orig_expenses

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_register_get(client):
    rv = client.get('/register')
    assert rv.status_code == 200
    assert b'Sign Up' in rv.data

def test_register_post(client):
    rv = client.post('/register', data={
        'username': 'testuser',
        'phonenumber': '1234567890',
        'email': 'test@example.com',
        'password': 'password123',
        'submit': 'Sign Up'
    }, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Registered successfully!' in rv.data

    # Verify user was added to DB
    user = csv_db.get_user_by_email('test@example.com')
    assert user is not None
    assert user['name'] == 'testuser'
    assert user['password'] == 'password123'

def test_login_get(client):
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Sign In' in rv.data

def test_login_post_success(client):
    # Register a user first
    client.post('/register', data={
        'username': 'testuser',
        'phonenumber': '1234567890',
        'email': 'testlogin@example.com',
        'password': 'password123',
        'submit': 'Sign Up'
    })

    # Try to login
    rv = client.post('/login', data={
        'email': 'testlogin@example.com',
        'password': 'password123',
        'submit': 'Sign In'
    }, follow_redirects=True)

    assert rv.status_code == 200
    assert b'Logged in successfully!' in rv.data

    # Check session
    with client.session_transaction() as sess:
        assert sess.get('user') == 'testuser'
        assert sess.get('email') == 'testlogin@example.com'

def test_login_post_invalid(client):
    rv = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword',
        'submit': 'Sign In'
    }, follow_redirects=True)

    assert rv.status_code == 200
    assert b'Invalid credentials' in rv.data

    with client.session_transaction() as sess:
        assert sess.get('user') is None

def test_home_unauthenticated(client):
    rv = client.get('/home', follow_redirects=True)
    assert rv.status_code == 200
    assert b'Please login first' in rv.data

def test_home_authenticated(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.get('/home')
    assert rv.status_code == 200
    assert b'testuser' in rv.data

def test_addexpense_unauthenticated(client):
    rv = client.get('/addexpense', follow_redirects=True)
    assert b'Please login first' in rv.data

def test_addexpense_get_authenticated(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.get('/addexpense')
    assert rv.status_code == 200

def test_addexpense_post(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.post('/addexpense', data={
        'amount': '100',
        'category': 'Education',
        'date': '2023-10-01',
        'description': 'Books'
    }, follow_redirects=True)

    assert rv.status_code == 200
    assert b'Expense added successfully!' in rv.data

    expenses = csv_db.get_expenses_by_user('test@example.com')
    assert len(expenses) == 1
    assert expenses[0]['amount'] == '100'
    assert expenses[0]['category'] == 'Education'

def test_edit_expense_unauthenticated(client):
    rv = client.get('/edit_expense/123', follow_redirects=True)
    assert b'Please login first' in rv.data

def test_edit_expense_not_found(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.get('/edit_expense/invalid_id', follow_redirects=True)
    assert b'Expense not found' in rv.data

def test_edit_expense_post(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    # Add an expense to edit
    expense_id = csv_db.add_expense('test@example.com', '100', 'Education', '2023-10-01', 'Books')

    # Get form
    rv = client.get(f'/edit_expense/{expense_id}')
    assert rv.status_code == 200

    # Update expense
    rv = client.post(f'/edit_expense/{expense_id}', data={
        'amount': '200',
        'category': 'Health',
        'date': '2023-10-02',
        'description': 'Medicine'
    }, follow_redirects=True)

    assert rv.status_code == 200
    assert b'Expense updated successfully!' in rv.data

    # Verify update
    expense = csv_db.get_expense_by_id(expense_id, 'test@example.com')
    assert expense['amount'] == '200'
    assert expense['category'] == 'Health'

def test_delete_expense_unauthenticated(client):
    rv = client.get('/delete_expense/123', follow_redirects=True)
    assert b'Please login first' in rv.data

def test_delete_expense_not_found(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.get('/delete_expense/invalid_id', follow_redirects=True)
    assert b'Expense not found or could not be deleted.' in rv.data

def test_delete_expense_success(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    # Add an expense to delete
    expense_id = csv_db.add_expense('test@example.com', '100', 'Education', '2023-10-01', 'Books')

    # Verify expense exists
    assert csv_db.get_expense_by_id(expense_id, 'test@example.com') is not None

    # Delete expense
    rv = client.get(f'/delete_expense/{expense_id}', follow_redirects=True)

    assert rv.status_code == 200
    assert b'Expense deleted successfully!' in rv.data

    # Verify deletion
    assert csv_db.get_expense_by_id(expense_id, 'test@example.com') is None

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['email'] = 'test@example.com'

    rv = client.get('/logout', follow_redirects=True)
    assert rv.status_code == 200
    # assert b'Logged out successfully!' in rv.data # index.html does not render flash messages

    with client.session_transaction() as sess:
        assert 'user' not in sess
        assert 'email' not in sess
