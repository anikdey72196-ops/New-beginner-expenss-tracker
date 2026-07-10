import pytest
import os
import csv_db
from app import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Patch CSV file paths to use temporary files
    users_file = tmp_path / "users.csv"
    expenses_file = tmp_path / "expenses.csv"

    monkeypatch.setattr(csv_db, 'USERS_FILE', str(users_file))
    monkeypatch.setattr(csv_db, 'EXPENSES_FILE', str(expenses_file))

    # Initialize the CSV files
    csv_db.init_csv()

    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_register_page_get(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_register_page_post(client):
    response = client.post("/register", data={
        "username": "testuser",
        "phonenumber": "1234567890",
        "email": "test@example.com",
        "password": "testpassword",
        "submit": "Sign Up"
    })
    # Should redirect to login on successful registration
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_login_page_get(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_login_page_post_invalid(client):
    response = client.post("/login", data={
        "email": "wrong@example.com",
        "password": "wrongpassword",
        "submit": "Sign In"
    })
    # Redirects back to login on failure
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_login_page_post_valid(client):
    # First register a user
    client.post("/register", data={
        "username": "testuser",
        "phonenumber": "1234567890",
        "email": "test@example.com",
        "password": "testpassword",
        "submit": "Sign Up"
    })

    # Then login
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "testpassword",
        "submit": "Sign In"
    })

    # Redirects to home on success
    assert response.status_code == 302
    assert response.headers["Location"] == "/home"

def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_protected_routes_unauthenticated(client):
    routes = ["/home", "/addexpense", "/edit_expense/123", "/delete_expense/123"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302
        assert response.headers["Location"] == "/login"

def test_home_authenticated(client):
    # Register and login
    client.post("/register", data={
        "username": "testuser",
        "phonenumber": "1234567890",
        "email": "auth@example.com",
        "password": "testpassword",
        "submit": "Sign Up"
    })
    client.post("/login", data={
        "email": "auth@example.com",
        "password": "testpassword",
        "submit": "Sign In"
    })

    response = client.get("/home")
    assert response.status_code == 200

def test_add_expense_authenticated(client):
    # Register and login
    client.post("/register", data={
        "username": "testuser",
        "phonenumber": "1234567890",
        "email": "auth2@example.com",
        "password": "testpassword",
        "submit": "Sign Up"
    })
    client.post("/login", data={
        "email": "auth2@example.com",
        "password": "testpassword",
        "submit": "Sign In"
    })

    # Add expense GET
    response = client.get("/addexpense")
    assert response.status_code == 200

    # Add expense POST
    response = client.post("/addexpense", data={
        "amount": "100.50",
        "category": "Education",
        "date": "2024-01-01",
        "description": "Books"
    })
    # Should redirect to home
    assert response.status_code == 302
    assert response.headers["Location"] == "/home"

def test_edit_delete_expense_authenticated(client):
    # Register and login
    client.post("/register", data={
        "username": "testuser",
        "phonenumber": "1234567890",
        "email": "auth3@example.com",
        "password": "testpassword",
        "submit": "Sign Up"
    })
    client.post("/login", data={
        "email": "auth3@example.com",
        "password": "testpassword",
        "submit": "Sign In"
    })

    # Add expense directly using csv_db to get ID
    import csv_db
    expense_id = csv_db.add_expense("auth3@example.com", "100.50", "Education", "2024-01-01", "Books")

    # Edit expense GET
    response = client.get(f"/edit_expense/{expense_id}")
    assert response.status_code == 200

    # Edit expense POST
    response = client.post(f"/edit_expense/{expense_id}", data={
        "amount": "200.00",
        "category": "Health",
        "date": "2024-01-02",
        "description": "Medicine"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/home"

    # Check if updated in DB
    updated_expense = csv_db.get_expense_by_id(expense_id, "auth3@example.com")
    assert updated_expense['amount'] == "200.00"

    # Delete expense
    response = client.get(f"/delete_expense/{expense_id}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/home"

    # Check if deleted in DB
    deleted_expense = csv_db.get_expense_by_id(expense_id, "auth3@example.com")
    assert deleted_expense is None
