import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user_and_login(prefix: str):
    ts = int(time.time() * 1000)
    email = f"{prefix}_{ts}@example.com"
    pwd = "SecurePassword123!"
    reg_res = client.post("/api/auth/register", json={
        "full_name": f"{prefix.capitalize()} Auditor",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    token = data["access_token"]
    return email, pwd, token

def test_direct_api_access_blocked_without_auth():
    """Test F: Verify all protected endpoints reject unauthenticated requests with HTTP 401."""
    unauth = TestClient(app)

    # 1. Start an audit
    res_start = unauth.post("/api/audits", json={"url": "demo.local"})
    assert res_start.status_code == 401
    assert "credentials not provided" in res_start.json()["detail"].lower()

    # 2. Read audit history
    res_list = unauth.get("/api/audits")
    assert res_list.status_code == 401

    # 3. Read audit by ID
    res_detail = unauth.get("/api/audits/1")
    assert res_detail.status_code == 401

    # 4. Rerun audit
    res_rerun = unauth.post("/api/audits/1/rerun")
    assert res_rerun.status_code == 401

    # 5. Delete audit
    res_del = unauth.delete("/api/audits/1")
    assert res_del.status_code == 401

    # 6. Export PDF report
    res_pdf = unauth.get("/api/audits/1/export-pdf")
    assert res_pdf.status_code == 401

    # 7. User profile
    res_profile = unauth.get("/api/auth/me")
    assert res_profile.status_code == 401

    # 8. Password change
    res_pwd = unauth.put("/api/auth/password", json={
        "current_password": "OldPassword123!",
        "new_password": "NewPassword123!",
        "confirm_new_password": "NewPassword123!"
    })
    assert res_pwd.status_code == 401

def test_registration_flow_and_duplicate_handling():
    """Test B: Verify registration validation, duplicate email prevention, and session cookie."""
    ts = int(time.time() * 1000)
    email = f"register_flow_{ts}@example.com"
    pwd = "ValidPassword123!"

    # Successful registration
    reg = client.post("/api/auth/register", json={
        "full_name": "Test Registrar",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    assert reg.status_code == 201
    assert "access_token" in reg.json()
    assert "devlens_token" in reg.cookies

    # Duplicate registration attempt
    dup = client.post("/api/auth/register", json={
        "full_name": "Test Registrar Duplicate",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    assert dup.status_code == 400
    assert "already exists" in dup.json()["detail"].lower()

def test_login_success_and_invalid_credentials_denial():
    """Test C: Valid credentials succeed, invalid credentials denied."""
    email, pwd, _ = create_user_and_login("auth_user")

    # Correct credentials
    success = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert success.status_code == 200
    assert "access_token" in success.json()

    # Wrong password
    failure = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword999!"})
    assert failure.status_code == 401
    assert "invalid email or password" in failure.json()["detail"].lower()

def test_session_refresh_via_cookie_and_token():
    """Test H: Verify session verification via /api/auth/me using token and cookie."""
    email, pwd, token = create_user_and_login("session_refresh")

    # Using Bearer header
    res_token = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_token.status_code == 200
    assert res_token.json()["email"] == email.lower()

    # Using HttpOnly Cookie
    client.cookies.set("devlens_token", token)
    res_cookie = client.get("/api/auth/me")
    assert res_cookie.status_code == 200
    assert res_cookie.json()["email"] == email.lower()

