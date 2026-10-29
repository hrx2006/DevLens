import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import ai_service

client = TestClient(app)

def test_workflow_a_full_audit_lifecycle():
    """
    Workflow A:
    Register -> Login -> Submit URL -> Complete Audit -> View Findings -> Export PDF.
    """
    ts = int(time.time() * 1000)
    email = f"workflow_a_{ts}@example.com"
    pwd = "AuditPassword123!"

    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "full_name": "Workflow A Tester",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login verification
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd
    })
    assert login_res.status_code == 200

    # 3. Submit URL (Demo Target)
    audit_res = client.post("/api/audits", json={"url": "demo.local"}, headers=headers)
    assert audit_res.status_code == 201
    audit_data = audit_res.json()
    audit_id = audit_data["id"]
    assert audit_data["status"] == "completed"
    assert 0 <= audit_data["overall_score"] <= 100

    # 4. View Findings
    detail_res = client.get(f"/api/audits/{audit_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["issues"]) > 0
    assert any(iss["category"] == "SEO" for iss in detail_data["issues"])
    assert any(iss["category"] == "Security" for iss in detail_data["issues"])
    assert any(iss["category"] == "Accessibility" for iss in detail_data["issues"])
    assert any(iss["category"] == "Performance" for iss in detail_data["issues"])
    assert any(iss["category"] == "Functionality" for iss in detail_data["issues"])

    # 5. Export PDF
    pdf_res = client.get(f"/api/audits/{audit_id}/export-pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

def test_workflow_b_session_persistence_and_history():
    """
    Workflow B:
    Login -> Run Audit -> Logout -> Login Again -> View Audit History.
    """
    ts = int(time.time() * 1000)
    email = f"workflow_b_{ts}@example.com"
    pwd = "PersistPassword123!"

    # Setup user
    client.post("/api/auth/register", json={
        "full_name": "Workflow B User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })

    # 1. Login
    login1 = client.post("/api/auth/login", json={"email": email, "password": pwd})
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Run Audit
    run_res = client.post("/api/audits", json={"url": "demo.local"}, headers=headers1)
    assert run_res.status_code == 201
    audit_id = run_res.json()["id"]

    # 3. Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # 4. Login Again
    login2 = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 5. View Audit History
    hist_res = client.get("/api/audits", headers=headers2)
    assert hist_res.status_code == 200
    history_ids = [item["id"] for item in hist_res.json()]
    assert audit_id in history_ids

def test_workflow_c_cross_user_isolation():
    """
    Workflow C:
    Create two users -> Generate separate audits -> Verify neither user can access the other's records.
    """
    ts = int(time.time() * 1000)
    user1_email = f"user1_{ts}@example.com"
    user2_email = f"user2_{ts}@example.com"
    pwd = "IsolationPassword123!"

    reg1 = client.post("/api/auth/register", json={"full_name": "User 1", "email": user1_email, "password": pwd, "confirm_password": pwd})
    token1 = reg1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    reg2 = client.post("/api/auth/register", json={"full_name": "User 2", "email": user2_email, "password": pwd, "confirm_password": pwd})
    token2 = reg2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    audit1 = client.post("/api/audits", json={"url": "demo.local"}, headers=headers1).json()["id"]
    audit2 = client.post("/api/audits", json={"url": "demo.local"}, headers=headers2).json()["id"]

    # User 1 cannot view User 2's audit
    assert client.get(f"/api/audits/{audit2}", headers=headers1).status_code == 404
    # User 2 cannot view User 1's audit
    assert client.get(f"/api/audits/{audit1}", headers=headers2).status_code == 404

    # User 1 cannot export User 2's PDF
    assert client.get(f"/api/audits/{audit2}/export-pdf", headers=headers1).status_code == 404
    # User 2 cannot export User 1's PDF
    assert client.get(f"/api/audits/{audit1}/export-pdf", headers=headers2).status_code == 404

    # User 1 cannot delete User 2's audit
    assert client.delete(f"/api/audits/{audit2}", headers=headers1).status_code == 404

def test_workflow_d_deterministic_scanning_without_ai():
    """
    Workflow D:
    Disable AI configuration -> Run Audit -> Verify deterministic scanning and fallback explanations work.
    """
    ts = int(time.time() * 1000)
    email = f"workflow_d_{ts}@example.com"
    pwd = "FallbackPassword123!"
    reg = client.post("/api/auth/register", json={
        "full_name": "Workflow D Tester", "email": email, "password": pwd, "confirm_password": pwd
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # Temporarily ensure AI API key is empty
    orig_key = ai_service.api_key
    ai_service.api_key = ""

    try:
        res = client.post("/api/audits", json={"url": "demo.local"}, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "completed"
        assert len(data["issues"]) > 0

        # Verify fallback explanations are populated
        for iss in data["issues"]:
            assert iss["recommendation"]
            assert iss["root_cause"]
            assert iss["user_impact"]
            assert "Deterministic Fallback Engine" in (iss.get("ai_source") or "Deterministic Fallback Engine")
    finally:
        ai_service.api_key = orig_key

def test_workflow_e_prohibited_and_invalid_urls_rejection():
    """
    Workflow E:
    Submit invalid or prohibited URLs -> Verify safe rejection.
    """
    ts = int(time.time() * 1000)
    email = f"workflow_e_{ts}@example.com"
    pwd = "RejectPassword123!"
    reg = client.post("/api/auth/register", json={
        "full_name": "Workflow E Tester", "email": email, "password": pwd, "confirm_password": pwd
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    prohibited_urls = [
        "http://127.0.0.1:8000/admin",
        "http://localhost:3000",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/private",
        "http://192.168.1.1/",
        "ftp://example.com/file",
        "file:///etc/passwd",
        "not-a-valid-url",
        "http://example.com:99999",  # Port out of range
    ]

    for bad_url in prohibited_urls:
        resp = client.post("/api/audits", json={"url": bad_url}, headers=headers)
        assert resp.status_code == 400, f"Expected 400 rejection for prohibited URL: {bad_url}"
