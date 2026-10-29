from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.config import settings
from app.db.database import get_db
from app.db.models import UserModel, AuditModel, CategoryResultModel, IssueModel
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest, UserResponse, AuthResponse
from app.schemas.audit import AuditRequest, AuditResponse, AuditSummaryResponse, AuditPaginationResponse
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, get_current_user_optional
from app.services.auth_service import auth_service
from app.crawler.crawler import Crawler, validate_url, CrawlResult
from app.crawler.ssrf import is_safe_url
from app.scanners.seo import SEOScanner
from app.scanners.accessibility import AccessibilityScanner
from app.scanners.performance import PerformanceScanner
from app.scanners.security import SecurityScanner
from app.scanners.functionality import FunctionalityScanner
from app.services.ai_service import ai_service
from app.services.priority_engine import priority_engine
from app.services.demo_service import get_demo_html
from app.services.pdf_service import pdf_service

router = APIRouter(prefix="/api")

# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(reg_data: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, reg_data)
    token = create_access_token(subject=user.email, user_id=user.id)
    
    # Set HttpOnly, SameSite Session Cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        message="Registration completed successfully.",
        access_token=token
    )

@router.post("/auth/login", response_model=AuthResponse)
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, login_data)
    token = create_access_token(subject=user.email, user_id=user.id)

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        message="Login successful.",
        access_token=token
    )

@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    return {"message": "Logged out successfully."}

@router.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.put("/auth/password")
def change_password(
    pwd_data: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_service.change_password(db, current_user, pwd_data)
    return {"message": "Password changed successfully."}

# ============================================================================
# Demo Target Endpoint
# ============================================================================

@router.get("/demo-target", response_class=Response)
def get_demo_page():
    return Response(content=get_demo_html(), media_type="text/html")

# ============================================================================
# Audit Endpoints (with Strict Data Isolation & 5 Scanners)
# ============================================================================

async def _execute_audit_pipeline(target_url: str, user_id: Optional[int], db: Session) -> AuditModel:
    url = target_url.strip()
    is_demo = url.lower() in ["http://demo.local", "https://demo.local", "demo", "demo.local"]

    if is_demo:
        crawl_result = CrawlResult(
            url="https://demo.local",
            status_code=200,
            title="",  # Missing title
            html=get_demo_html(),
            links=["https://demo.local/more-info", "https://demo.local/broken-404"],
            images=[
                {"src": "https://via.placeholder.com/600x400", "alt": None, "loading": None},
                {"src": "https://via.placeholder.com/300x200", "alt": "", "loading": None},
                {"src": "http://insecure.example.com/logo.png", "alt": "Insecure Logo", "loading": None},
                {"src": "https://via.placeholder.com/150", "alt": None, "loading": None},
                {"src": "https://via.placeholder.com/150", "alt": None, "loading": None},
                {"src": "https://via.placeholder.com/150", "alt": None, "loading": None},
                {"src": "https://via.placeholder.com/150", "alt": None, "loading": None}
            ],
            response_time=1.4,
            headers={
                "server": "DevLens-DemoServer/1.0",
                "content-type": "text/html; charset=utf-8"
                # Intentionally missing HSTS, CSP, X-Content-Type-Options, X-Frame-Options
            },
            final_url="https://demo.local"
        )
    else:
        if not validate_url(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format. Please enter a valid HTTP/HTTPS website URL."
            )

        safe, reason = is_safe_url(url)
        if not safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security rejection: URL target violates SSRF policy ({reason})."
            )

        crawler = Crawler()
        try:
            crawl_result = await crawler.crawl(url)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Crawl aborted by SSRF protection: {str(e)}"
            )
        except TimeoutError as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=str(e)
            )
        except ConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Crawl execution error: {str(e)}"
            )

    # 1. Execute All 5 Deterministic Technical Scanners
    seo_scanner = SEOScanner()
    access_scanner = AccessibilityScanner()
    perf_scanner = PerformanceScanner()
    sec_scanner = SecurityScanner()
    func_scanner = FunctionalityScanner()

    seo_score, seo_findings = seo_scanner.scan(crawl_result)
    access_score, access_findings = access_scanner.scan(crawl_result)
    perf_score, perf_findings = perf_scanner.scan(crawl_result)
    sec_score, sec_findings = sec_scanner.scan(crawl_result)
    func_score, func_findings = func_scanner.scan(crawl_result)

    # 2. Combine and normalize findings across all categories
    all_scanner_findings = (
        seo_findings +
        access_findings +
        perf_findings +
        sec_findings +
        func_findings
    )
    all_findings_dicts = [f.to_dict() for f in all_scanner_findings]

    # 3. Enhance findings through AI Reasoning (Gemini or deterministic evidence fallback)
    ai_results = await ai_service.analyze_findings(crawl_result.final_url, all_findings_dicts)
    ai_issues_map = {issue["title"]: issue for issue in ai_results.get("analyzed_issues", [])}

    # 4. Calculate Overall Health Score
    overall_score = priority_engine.calculate_overall_health(
        seo_score=seo_score,
        accessibility_score=access_score,
        performance_score=perf_score,
        security_score=sec_score,
        functionality_score=func_score
    )

    ai_source_engine = ai_results.get("ai_source", "Deterministic Fallback Engine")

    # 5. Persist to Database with Owner User ID
    audit_db = AuditModel(
        user_id=user_id,
        url=crawl_result.url,
        created_at=datetime.now(timezone.utc),
        status="completed",
        overall_score=overall_score,
        seo_score=seo_score,
        accessibility_score=access_score,
        performance_score=perf_score,
        security_score=sec_score,
        functionality_score=func_score,
        ai_source=ai_source_engine
    )
    db.add(audit_db)
    db.commit()
    db.refresh(audit_db)

    # Save Category Results
    category_models = [
        CategoryResultModel(audit_id=audit_db.id, category="SEO", score=seo_score),
        CategoryResultModel(audit_id=audit_db.id, category="Accessibility", score=access_score),
        CategoryResultModel(audit_id=audit_db.id, category="Performance", score=perf_score),
        CategoryResultModel(audit_id=audit_db.id, category="Security", score=sec_score),
        CategoryResultModel(audit_id=audit_db.id, category="Functionality", score=func_score),
    ]
    db.add_all(category_models)

    # Save Issues with Priority and AI Interpretation
    issue_models = []
    for f in all_scanner_findings:
        p_score = priority_engine.calculate_priority(f.severity, f.category)
        ai_data = ai_issues_map.get(f.title, {})

        issue_item = IssueModel(
            audit_id=audit_db.id,
            category=f.category,
            title=f.title,
            description=f.description,
            severity=f.severity,
            priority=p_score,
            evidence=f.evidence,
            recommendation=ai_data.get("recommendation") or f.recommendation,
            ai_explanation=ai_data.get("ai_explanation") or f.description,
            root_cause=ai_data.get("root_cause") or "Based on scanner evidence.",
            user_impact=ai_data.get("user_impact") or "Impacts site reliability and user experience.",
            ai_source=ai_data.get("ai_source") or ai_source_engine
        )
        issue_models.append(issue_item)

    db.add_all(issue_models)
    db.commit()
    db.refresh(audit_db)

    return audit_db

@router.post("/audits", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    request: AuditRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit = await _execute_audit_pipeline(request.url, current_user.id, db)
    return audit

@router.get("/audits", response_model=List[AuditSummaryResponse])
def list_audits(
    q: Optional[str] = Query(None, description="Search query by URL"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Strict Isolation: Only return audits owned by the authenticated user
    query = db.query(AuditModel).filter(AuditModel.user_id == current_user.id)

    if q and q.strip():
        query = query.filter(AuditModel.url.ilike(f"%{q.strip()}%"))

    audits = query.order_by(AuditModel.created_at.desc()).all()
    
    # Enrich summary with issues count
    summaries = []
    for a in audits:
        summary = AuditSummaryResponse(
            id=a.id,
            user_id=a.user_id,
            url=a.url,
            created_at=a.created_at,
            status=a.status,
            overall_score=a.overall_score,
            seo_score=a.seo_score,
            accessibility_score=a.accessibility_score,
            performance_score=a.performance_score,
            security_score=a.security_score,
            functionality_score=a.functionality_score,
            issues_count=len(a.issues)
        )
        summaries.append(summary)

    return summaries

@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit_detail(
    audit_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit = db.query(AuditModel).filter(AuditModel.id == audit_id).first()
    # Strict Ownership Authorization Check:
    # Returns 404 rather than 403 to prevent audit existence enumeration
    if not audit or audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    return audit

@router.delete("/audits/{audit_id}")
def delete_audit(
    audit_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit = db.query(AuditModel).filter(AuditModel.id == audit_id).first()
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    if audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    db.delete(audit)
    db.commit()
    return {"message": f"Audit #{audit_id} deleted successfully."}

@router.post("/audits/{audit_id}/rerun", response_model=AuditResponse)
async def rerun_audit(
    audit_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_audit = db.query(AuditModel).filter(AuditModel.id == audit_id).first()
    if not existing_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    if existing_audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    new_audit = await _execute_audit_pipeline(existing_audit.url, current_user.id, db)
    return new_audit

@router.get("/audits/{audit_id}/export-pdf")
def export_audit_pdf(
    audit_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audit = db.query(AuditModel).filter(AuditModel.id == audit_id).first()
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    # Strict Authorization Verification
    if audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found."
        )

    try:
        pdf_bytes = pdf_service.generate_audit_pdf(audit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF audit report: {str(e)}"
        )

    filename = f"devlens-audit-{audit.id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
