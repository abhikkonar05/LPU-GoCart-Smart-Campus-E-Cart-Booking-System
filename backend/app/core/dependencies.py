"""
LPU GoCart - FastAPI Dependency Injection Hub
Provides database sessions, Supabase clients, user authentication, and RBAC checks.
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db, SessionLocal
from app.database.models.models import Profile, Student, Driver
from app.core.security import decode_access_token
from app.core.config import settings
import logging

logger = logging.getLogger("lpu_gocart.auth")

security_bearer = HTTPBearer(auto_error=False)

def get_supabase_client():
    """Retrieve Supabase Client instance if credentials are valid."""
    try:
        from supabase import create_client, Client
        if settings.SUPABASE_URL and "your-project" not in settings.SUPABASE_URL:
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception as e:
        logger.warning(f"Supabase client initialization skipped: {e}")
    return None

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Profile:
    """
    Validate the incoming Bearer token and return the authenticated Profile.
    Accepts both local FastAPI JWTs and Supabase Auth JWTs.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # User ID can be in 'sub' or 'id'
    user_id = payload.get("sub") or payload.get("id")
    email = payload.get("email")

    if not user_id and not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Lookup user profile in database
    user = None
    if user_id:
        user = db.query(Profile).filter(Profile.id == user_id).first()
    if not user and email:
        user = db.query(Profile).filter(Profile.email == email).first()

    if not user:
        # If user exists in Supabase Auth but not yet in local DB, auto-create profile
        user = Profile(
            id=user_id or payload.get("id"),
            email=email or f"user_{user_id[:8]}@lpu.in",
            full_name=payload.get("user_metadata", {}).get("full_name") or payload.get("name") or "LPU Rider",
            role=payload.get("user_metadata", {}).get("role") or payload.get("role") or "STUDENT"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

def require_role(*allowed_roles: str):
    """Factory dependency enforcing Role-Based Access Control (STUDENT, DRIVER, ADMIN)."""
    def role_checker(current_user: Profile = Depends(get_current_user)) -> Profile:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Access requires one of {allowed_roles} roles. Your role is {current_user.role}."
            )
        return current_user
    return role_checker

# Predefined role dependencies
get_current_student = require_role("STUDENT", "ADMIN")
get_current_driver = require_role("DRIVER", "ADMIN")
get_current_admin = require_role("ADMIN")

