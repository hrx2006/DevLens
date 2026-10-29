from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    audits = relationship("AuditModel", back_populates="user", cascade="all, delete-orphan")

class AuditModel(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    url = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="completed")
    overall_score = Column(Float, default=0.0)
    seo_score = Column(Float, default=0.0)
    accessibility_score = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    functionality_score = Column(Float, default=0.0)
    ai_source = Column(String, default="Deterministic Fallback Engine", nullable=True)

    user = relationship("UserModel", back_populates="audits")
    category_results = relationship("CategoryResultModel", back_populates="audit", cascade="all, delete-orphan")
    issues = relationship("IssueModel", back_populates="audit", cascade="all, delete-orphan")

class CategoryResultModel(Base):
    __tablename__ = "category_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    category = Column(String, nullable=False)
    score = Column(Float, nullable=False)

    audit = relationship("AuditModel", back_populates="category_results")

class IssueModel(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    evidence = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    user_impact = Column(Text, nullable=True)
    ai_source = Column(String, default="Deterministic Fallback Engine", nullable=True)

    audit = relationship("AuditModel", back_populates="issues")
