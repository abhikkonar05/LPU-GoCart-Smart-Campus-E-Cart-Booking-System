"""
LPU GoCart - FastAPI Dependency Injection Hub
Provides database sessions, user authentication, and RBAC checks.
Roles: ADMIN, DRIVER, CUSTOMER
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.core.security import decode_access_token
from app.core.config import settings
import logging

logger = logging.getLogger("lpu_gocart.auth")

security_bearer = HTTPBearer(auto_error=False)

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate the incoming Bearer token and return the authenticated User.
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

    user_id = payload.get("sub") or payload.get("id")
    email = payload.get("email")

    if not user_id and not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = None
    if user_id:
        user = db.query(User).filter(User.id == str(user_id)).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user

def require_role(*allowed_roles: str):
    """Factory dependency enforcing Role-Based Access Control (CUSTOMER, DRIVER, ADMIN)."""
    # Normalize roles (allow 'STUDENT' as alias for 'CUSTOMER')
    normalized = set()
    for r in allowed_roles:
        r_upper = r.upper()
        if r_upper == "STUDENT":
            normalized.add("CUSTOMER")
        normalized.add(r_upper)

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.upper()
        if user_role not in normalized and "ADMIN" not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Access requires one of {allowed_roles} roles. Your role is {current_user.role}."
            )
        return current_user
    return role_checker

# Predefined role dependencies
get_current_customer = require_role("CUSTOMER", "STUDENT", "ADMIN")
get_current_student = get_current_customer  # backward-compat alias
get_current_driver = require_role("DRIVER", "ADMIN")
get_current_admin = require_role("ADMIN")
