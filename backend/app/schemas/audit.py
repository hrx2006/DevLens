from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class AuditRequest(BaseModel):
    url: str

class IssueSchema(BaseModel):
    id: Optional[int] = None
    category: str
    title: str
    description: Optional[str] = None
    severity: str  # Critical, High, Medium, Low, Info
    priority: int  # 0-100
    evidence: Optional[str] = None
    recommendation: Optional[str] = None
    ai_explanation: Optional[str] = None
    root_cause: Optional[str] = None
    user_impact: Optional[str] = None
    ai_source: Optional[str] = "Deterministic Fallback Engine"

    model_config = ConfigDict(from_attributes=True)

class CategoryResultSchema(BaseModel):
    category: str
    score: float

    model_config = ConfigDict(from_attributes=True)

class AuditResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    url: str
    created_at: datetime
    status: str
    overall_score: float
    seo_score: float
    accessibility_score: float
    performance_score: float
    security_score: float = 0.0
    functionality_score: float = 0.0
    ai_source: Optional[str] = "Deterministic Fallback Engine"
    category_results: List[CategoryResultSchema] = []
    issues: List[IssueSchema] = []

    model_config = ConfigDict(from_attributes=True)

class AuditSummaryResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    url: str
    created_at: datetime
    status: str
    overall_score: float
    seo_score: Optional[float] = 0.0
    accessibility_score: Optional[float] = 0.0
    performance_score: Optional[float] = 0.0
    security_score: Optional[float] = 0.0
    functionality_score: Optional[float] = 0.0
    issues_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class AuditPaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuditSummaryResponse]
