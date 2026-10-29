import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user_and_login(prefix: str):
    ts = int(time.time() * 1000)
    email = f"{prefix}_{ts}@example.com"
    pwd = "StrongPassword123!"
    reg_res = client.post("/api/auth/register", json={
        "full_name": f"{prefix.upper()} User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    return email, token

def test_strict_cross_user_isolation():
    # 1. Register User A and User B
    email_a, token_a = create_user_and_login("user_a")
    email_b, token_b = create_user_and_login("user_b")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. User A creates an audit
    res_a = client.post("/api/audits", json={"url": "demo.local"}, headers=headers_a)
    assert res_a.status_code == 201
    audit_a_id = res_a.json()["id"]

    # 3. User B creates an audit
    res_b = client.post("/api/audits", json={"url": "demo.local"}, headers=headers_b)
    assert res_b.status_code == 201
    audit_b_id = res_b.json()["id"]

    assert audit_a_id != audit_b_id

    # 4. User A can view their own audit
    view_a = client.get(f"/api/audits/{audit_a_id}", headers=headers_a)
    assert view_a.status_code == 200
    assert view_a.json()["id"] == audit_a_id

    # 5. User B can view their own audit
    view_b = client.get(f"/api/audits/{audit_b_id}", headers=headers_b)
    assert view_b.status_code == 200
    assert view_b.json()["id"] == audit_b_id

    # 6. User A CANNOT access User B's audit -> Returns 404 (prevents ID enumeration)
    cross_view = client.get(f"/api/audits/{audit_b_id}", headers=headers_a)
    assert cross_view.status_code == 404

    # 7. User A CANNOT delete User B's audit -> Returns 404
    cross_delete = client.delete(f"/api/audits/{audit_b_id}", headers=headers_a)
    assert cross_delete.status_code == 404

    # 8. User A CANNOT rerun User B's audit -> Returns 404
    cross_rerun = client.post(f"/api/audits/{audit_b_id}/rerun", headers=headers_a)
    assert cross_rerun.status_code == 404

    # 9. User A CANNOT export User B's audit report as PDF -> Returns 404
    cross_export = client.get(f"/api/audits/{audit_b_id}/export-pdf", headers=headers_a)
    assert cross_export.status_code == 404

    # 10. Audit History isolation: User A's list only contains User A's audits
    history_a = client.get("/api/audits", headers=headers_a)
    assert history_a.status_code == 200
    ids_in_a = [item["id"] for item in history_a.json()]
    assert audit_a_id in ids_in_a
    assert audit_b_id not in ids_in_a

    # 11. User B's list only contains User B's audits
    history_b = client.get("/api/audits", headers=headers_b)
    assert history_b.status_code == 200
    ids_in_b = [item["id"] for item in history_b.json()]
    assert audit_b_id in ids_in_b
    assert audit_a_id not in ids_in_b

def test_delete_own_audit_succeeds():
    email_a, token_a = create_user_and_login("delete_test")
    headers = {"Authorization": f"Bearer {token_a}"}

    create_res = client.post("/api/audits", json={"url": "demo.local"}, headers=headers)
    audit_id = create_res.json()["id"]

    del_res = client.delete(f"/api/audits/{audit_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify audit is gone
    get_res = client.get(f"/api/audits/{audit_id}", headers=headers)
    assert get_res.status_code == 404
