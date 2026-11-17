"""
LPU GoCart - Central Application Configuration
Loads environment variables using Pydantic Settings.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "LPU GoCart API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    LOG_LEVEL: str = "info"

    # Core Security & JWT
    SECRET_KEY: str = "super-secret-lpu-gocart-signing-key-change-in-production"
    JWT_SECRET_KEY: str = "super-secret-lpu-gocart-signing-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours

    # Database
    DATABASE_URL: str = "sqlite:///./lpu_gocart.db"

    # URLs & CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Payment Gateway ('demo' or 'razorpay')
    PAYMENT_MODE: str = "demo"
    RAZORPAY_KEY_ID: str = "rzp_test_placeholder_key_id"
    RAZORPAY_KEY_SECRET: str = "rzp_test_placeholder_secret"

    # Business Rules
    SEAT_LOCK_DURATION_MINUTES: int = 5
    GPS_UPDATE_INTERVAL: int = 5
    GPS_UPDATE_FREQUENCY_SECONDS: int = 5
    QR_TICKET_SECRET: str = "lpu-gocart-qr-verification-secret-key-2026"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
