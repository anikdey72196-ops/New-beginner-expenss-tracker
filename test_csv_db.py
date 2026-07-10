import os
import csv
import pytest
import csv_db

def test_get_user_by_email_file_not_exists(tmp_path, monkeypatch):
    """Test when USERS_FILE does not exist"""
    test_file = tmp_path / "missing_users.csv"
    monkeypatch.setattr(csv_db, "USERS_FILE", str(test_file))

    assert csv_db.get_user_by_email("test@example.com") is None

def test_get_user_by_email_user_exists(tmp_path, monkeypatch):
    """Test when user exists in USERS_FILE"""
    test_file = tmp_path / "users.csv"
    monkeypatch.setattr(csv_db, "USERS_FILE", str(test_file))

    # Create file with a user
    with open(test_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "name", "password"])
        writer.writerow(["test@example.com", "Test User", "password123"])
        writer.writerow(["other@example.com", "Other User", "pass456"])

    user = csv_db.get_user_by_email("test@example.com")

    assert user is not None
    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"
    assert user["password"] == "password123"

def test_get_user_by_email_user_not_found(tmp_path, monkeypatch):
    """Test when user does not exist in USERS_FILE"""
    test_file = tmp_path / "users.csv"
    monkeypatch.setattr(csv_db, "USERS_FILE", str(test_file))

    # Create file with users but not the target
    with open(test_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "name", "password"])
        writer.writerow(["other@example.com", "Other User", "pass456"])

    user = csv_db.get_user_by_email("missing@example.com")

    assert user is None
