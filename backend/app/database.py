"""
Database connection and session management.
Configures SQLAlchemy with PostGIS support.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

from app.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session.
    Ensures session is closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
