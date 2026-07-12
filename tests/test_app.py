import pytest
from app import app as flask_app
from extensions import db
from models import User, Expense

@pytest.fixture
def client():
    # Configure app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Setup database
    with flask_app.app_context():
        db.create_all()

    with flask_app.test_client() as client:
        yield client
        
    # Teardown database
    with flask_app.app_context():
        db.drop_all()

def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_register_page_get(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_register_page_post(client):
    response = client.post("/register", data={
        "username": "testuser",
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
        "username": "wronguser",
        "password": "wrongpassword",
        "submit": "Sign In"
    })
    # Redirects back to login on failure (flash message shown)
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_login_page_post_valid(client):
    # First register a user
    client.post("/register", data={
        "username": "testuser",
        "password": "testpassword",
        "submit": "Sign Up"
    })

    # Then login
    response = client.post("/login", data={
        "username": "testuser",
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
    routes = ["/home", "/addexpense", "/edit_expense/1"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302
        assert response.headers["Location"] == "/login"

    # Delete requires POST
    response = client.post("/delete_expense/1")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_home_authenticated(client):
    # Register and login
    client.post("/register", data={"username": "testuser", "password": "testpassword", "submit": "Sign Up"})
    client.post("/login", data={"username": "testuser", "password": "testpassword", "submit": "Sign In"})

    response = client.get("/home")
    assert response.status_code == 200

def test_add_expense_authenticated(client):
    client.post("/register", data={"username": "testuser", "password": "testpassword", "submit": "Sign Up"})
    client.post("/login", data={"username": "testuser", "password": "testpassword", "submit": "Sign In"})

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
    client.post("/register", data={"username": "testuser", "password": "testpassword", "submit": "Sign Up"})
    client.post("/login", data={"username": "testuser", "password": "testpassword", "submit": "Sign In"})

    # Add expense via API to get an ID
    client.post("/addexpense", data={
        "amount": "100.50",
        "category": "Education",
        "date": "2024-01-01",
        "description": "Books"
    })
    
    with flask_app.app_context():
        expense = Expense.query.filter_by(description="Books").first()
        expense_id = expense.id

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
    with flask_app.app_context():
        updated_expense = Expense.query.get(expense_id)
        assert updated_expense.amount == 200.0

    # Delete expense
    response = client.post(f"/delete_expense/{expense_id}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/home"

    # Check if deleted in DB
    with flask_app.app_context():
        deleted_expense = Expense.query.get(expense_id)
        assert deleted_expense is None
