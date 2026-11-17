"""
LPU GoCart - Database Engine & Connection Session Management
Supports Render PostgreSQL pooling and automated local SQLite fallback.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("lpu_gocart.database")

Base = declarative_base()

def get_database_url() -> str:
    """Determine database URL: PostgreSQL or local SQLite fallback."""
    db_url = settings.DATABASE_URL.strip() if settings.DATABASE_URL else ""
    
    # If empty or explicitly sqlite
    if not db_url or "sqlite" in db_url:
        logger.info("[DB] Using local SQLite database (lpu_gocart.db)")
        return "sqlite:///./lpu_gocart.db"
    
    # Ensure SQLAlchemy uses psycopg 3 driver for PostgreSQL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and "+" not in db_url.split("://")[0]:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
    logger.info("[DB] Connecting to PostgreSQL database")
    return db_url

DATABASE_URL = get_database_url()

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI Dependency for database session management with auto-close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
