import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_registration_success():
    email = f"user_{pytest.importorskip('time').time()}@example.com"
    payload = {
        "full_name": "Test Engineer",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == email.lower()
    assert data["user"]["full_name"] == "Test Engineer"
    assert "access_token" in data
    assert "devlens_token" in response.cookies

def test_duplicate_email_registration_rejected():
    email = "duplicate_test@example.com"
    payload = {
        "full_name": "Original User",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    # First registration
    client.post("/api/auth/register", json=payload)
    # Duplicate attempt
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_weak_password_rejected():
    payload = {
        "full_name": "Short Pass User",
        "email": "shortpass@example.com",
        "password": "short",
        "confirm_password": "short"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code in [400, 422]

def test_mismatched_password_rejected():
    payload = {
        "full_name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "DifferentPassword123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "passwords do not match" in response.json()["detail"].lower()

def test_login_success_and_invalid_credentials():
    email = f"logintest_{pytest.importorskip('time').time()}@example.com"
    reg_payload = {
        "full_name": "Login User",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    client.post("/api/auth/register", json=reg_payload)

    # Valid Login
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
    assert "devlens_token" in login_resp.cookies

    # Invalid Password (generic error without disclosing user existence)
    bad_login = client.post("/api/auth/login", json={
        "email": email,
        "password": "WrongPassword999!"
    })
    assert bad_login.status_code == 401
    assert "invalid email or password" in bad_login.json()["detail"].lower()

def test_protected_endpoints_require_auth():
    unauth_client = TestClient(app)
    unauth_resp = unauth_client.get("/api/auth/me")
    assert unauth_resp.status_code == 401
    assert "authentication credentials not provided" in unauth_resp.json()["detail"].lower()

def test_logout_clears_session():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert "logged out" in response.json()["message"].lower()
