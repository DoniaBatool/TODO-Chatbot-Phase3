"""Database connection and session management."""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine
from src.config import settings


# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connection health before use
    echo=settings.debug,  # Log SQL queries in debug mode
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    Yields:
        Session: Database session that auto-commits and rolls back on error
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """
    Context manager for getting database session outside FastAPI.
    
    Usage:
        with get_session_context() as session:
            # Use session here
            pass
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session

