from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db.models import UserModel
from app.config import settings
from app.core.security import decode_access_token

def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT from:
    1. Authorization: Bearer <token> header
    2. HttpOnly Cookie: devlens_token
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            return token

    cookie_token = request.cookies.get(settings.COOKIE_NAME)
    if cookie_token:
        return cookie_token.strip()

    return None

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Strict authentication dependency.
    Raises 401 if unauthenticated, token expired, or user not found.
    """
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or is deactivated.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[UserModel]:
    """
    Optional authentication dependency for endpoints that support both
    guest demonstration and authenticated users.
    """
    token = extract_token_from_request(request)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        return None

    return user
