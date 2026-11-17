"""
LPU GoCart - Authentication REST Router
Handles user registration, login, JWT token issuance, and profile retrieval.
Roles: ADMIN, DRIVER, CUSTOMER
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User, Cart
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserProfileResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new customer, driver, or admin account."""
    clean_email = req.email.strip().lower()
    
    # Check if email is already taken
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Normalize role
    role = req.role.strip().upper()
    if role in ("STUDENT", "CUSTOMER"):
        role = "CUSTOMER"
    elif role not in ("CUSTOMER", "DRIVER", "ADMIN"):
        role = "CUSTOMER"

    hashed_pw = get_password_hash(req.password)
    
    # Create User
    user = User(
        email=clean_email,
        full_name=req.full_name.strip(),
        phone_number=req.phone_number.strip() if req.phone_number else None,
        role=role,
        hashed_password=hashed_pw,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Issue JWT Access Token
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name
    }
    token = create_access_token(token_data)

    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password and receive a JWT token."""
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact system administrator."
        )

    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name
    }
    token = create_access_token(token_data)

    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full profile details of the authenticated caller."""
    cart_id = None
    if current_user.role == "DRIVER":
        assigned_cart = db.query(Cart).filter(Cart.driver_id == current_user.id).first()
        if assigned_cart:
            cart_id = assigned_cart.id

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        role=current_user.role,
        avatar_url=None,
        assigned_cart_id=cart_id
    )
