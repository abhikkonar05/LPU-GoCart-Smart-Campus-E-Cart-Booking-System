"""
LPU GoCart - Security & Cryptographic Utilities
Handles password hashing (bcrypt), JWT issuance and verification, and HMAC signatures.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import bcrypt
import hmac
import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    if not hashed_password or not plain_password:
        return False
    try:
        # Truncate to 72 bytes as required by bcrypt
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash from a plain password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT token containing user identity and role.
    Compatible with Supabase JWT format and local API tokens.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "iss": "lpu-gocart-api"
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        # First attempt decoding using our internal secret key
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        # Fallback: Check if token is signed with Supabase JWT Secret or anon key
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            return payload
        except JWTError:
            return None

def generate_qr_ticket_token(booking_code: str, student_id: str, trip_id: str) -> str:
    """
    Generate a tamper-proof cryptographic signature for boarding QR tickets.
    Uses HMAC-SHA256 to ensure tickets cannot be forged or manipulated.
    """
    message = f"{booking_code}:{student_id}:{trip_id}".encode("utf-8")
    signature = hmac.new(settings.QR_TICKET_SECRET.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"LPU-TICKET:{booking_code}:{signature[:16]}"

def verify_qr_ticket_token(token_str: str, booking_code: str, student_id: str, trip_id: str) -> bool:
    """Verify validity of a student boarding pass QR token."""
    expected = generate_qr_ticket_token(booking_code, student_id, trip_id)
    return hmac.compare_digest(token_str, expected)

