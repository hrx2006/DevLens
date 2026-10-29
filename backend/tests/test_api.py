import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_headers():
    ts = int(time.time() * 1000)
    email = f"api_test_{ts}@example.com"
    pwd = "ApiPassword123!"
    reg_res = client.post("/api/auth/register", json={
        "full_name": "API Test User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "DevLens AI"
    assert "SEO" in data["active_scanners"]

def test_unauthenticated_audit_requests_rejected():
    """Verify that unauthenticated audit operations are rejected with HTTP 401."""
    # 1. Start audit without auth -> 401
    post_res = client.post("/api/audits", json={"url": "demo.local"})
    assert post_res.status_code == 401

    # 2. List audits without auth -> 401
    list_res = client.get("/api/audits")
    assert list_res.status_code == 401

    # 3. Get audit detail without auth -> 401
    get_res = client.get("/api/audits/999")
    assert get_res.status_code == 401

def test_demo_audit_flow_authenticated():
    headers = get_auth_headers()
    response = client.post("/api/audits", json={"url": "demo.local"}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://demo.local"
    assert data["overall_score"] >= 0.0
    assert len(data["issues"]) > 0

def test_invalid_url_rejection_authenticated():
    headers = get_auth_headers()
    response = client.post("/api/audits", json={"url": "invalid_url_format"}, headers=headers)
    assert response.status_code == 400
    assert "Invalid URL" in response.json()["detail"]
