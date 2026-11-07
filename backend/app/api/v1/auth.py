"""
LPU GoCart - Authentication REST Router
Handles user registration, login, JWT token issuance, and profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.models import Profile, Student, Driver
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserProfileResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new student, driver, or admin account."""
    # Check if email is already taken
    existing = db.query(Profile).filter(Profile.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    hashed_pw = get_password_hash(req.password)
    
    # 1. Create base Profile
    profile = Profile(
        email=req.email.lower(),
        full_name=req.full_name,
        phone_number=req.phone_number,
        role=req.role,
        hashed_password=hashed_pw
    )
    db.add(profile)
    db.flush()

    # 2. Create role-specific record
    if req.role == "STUDENT":
        reg_no = req.registration_number or f"LPU{profile.id[:6].upper()}"
        student = Student(
            id=profile.id,
            registration_number=reg_no,
            department=req.department or "Computer Science & Engineering",
            hostel_block=req.hostel_block or "BH-1"
        )
        db.add(student)
    elif req.role == "DRIVER":
        lic_no = req.license_number or f"DL-PB-{profile.id[:6].upper()}"
        driver = Driver(
            id=profile.id,
            license_number=lic_no,
            is_available=True
        )
        db.add(driver)

    db.commit()
    db.refresh(profile)

    # 3. Issue JWT Access Token
    token_data = {
        "sub": profile.id,
        "email": profile.email,
        "role": profile.role,
        "name": profile.full_name
    }
    token = create_access_token(token_data)

    return TokenResponse(
        access_token=token,
        role=profile.role,
        user_id=profile.id,
        full_name=profile.full_name,
        email=profile.email
    )

@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password and receive a JWT token."""
    profile = db.query(Profile).filter(Profile.email == req.email.lower()).first()
    if not profile or not profile.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not verify_password(req.password, profile.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    token_data = {
        "sub": profile.id,
        "email": profile.email,
        "role": profile.role,
        "name": profile.full_name
    }
    token = create_access_token(token_data)

    return TokenResponse(
        access_token=token,
        role=profile.role,
        user_id=profile.id,
        full_name=profile.full_name,
        email=profile.email
    )

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full profile details of the authenticated caller."""
    reg_no, dept, hostel, lic_no, cart_id = None, None, None, None, None

    if current_user.role == "STUDENT" and current_user.student:
        reg_no = current_user.student.registration_number
        dept = current_user.student.department
        hostel = current_user.student.hostel_block
    elif current_user.role == "DRIVER" and current_user.driver:
        lic_no = current_user.driver.license_number
        cart_id = current_user.driver.assigned_cart_id

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        role=current_user.role,
        avatar_url=current_user.avatar_url,
        registration_number=reg_no,
        department=dept,
        hostel_block=hostel,
        license_number=lic_no,
        assigned_cart_id=cart_id
    )

