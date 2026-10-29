import time
from fastapi.testclient import TestClient
from app.main import app
from app.services.pdf_service import pdf_service
from app.db.models import AuditModel, IssueModel, CategoryResultModel
from datetime import datetime, timezone

client = TestClient(app)

def test_pdf_service_generates_valid_pdf():
    audit = AuditModel(
        id=999,
        url="https://testsite.example.com",
        created_at=datetime.now(timezone.utc),
        status="completed",
        overall_score=78.5,
        seo_score=85.0,
        accessibility_score=70.0,
        performance_score=90.0,
        security_score=65.0,
        functionality_score=80.0
    )
    issue1 = IssueModel(
        id=1,
        audit_id=999,
        category="Security",
        title="Missing CSP",
        description="No CSP header.",
        severity="High",
        priority=80,
        evidence="Header absent",
        recommendation="Add CSP header",
        ai_explanation="Explains CSP",
        root_cause="Config missing",
        user_impact="XSS vulnerability"
    )
    audit.issues = [issue1]
    audit.category_results = [
        CategoryResultModel(audit_id=999, category="Security", score=65.0)
    ]

    pdf_bytes = pdf_service.generate_audit_pdf(audit)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

def test_pdf_export_endpoint_ownership():
    ts = int(time.time() * 1000)
    email = f"pdfuser_{ts}@example.com"
    pwd = "StrongPassword123!"

    reg = client.post("/api/auth/register", json={
        "full_name": "PDF User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Audit
    audit_res = client.post("/api/audits", json={"url": "demo.local"}, headers=headers)
    audit_id = audit_res.json()["id"]

    # Export PDF as Owner
    export_res = client.get(f"/api/audits/{audit_id}/export-pdf", headers=headers)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "application/pdf"
    assert export_res.content.startswith(b"%PDF")

    # Unauthenticated export attempt
    unauth_client = TestClient(app)
    anon_res = unauth_client.get(f"/api/audits/{audit_id}/export-pdf")
    assert anon_res.status_code == 401
