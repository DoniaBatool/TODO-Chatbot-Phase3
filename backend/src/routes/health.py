"""Health check endpoint."""

from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text

from src.db import get_session, engine
from src.schemas import HealthResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint to verify API and database connectivity.

    Returns:
        HealthResponse: System status including database connectivity and pool metrics

    Raises:
        HTTPException: 503 if database is unavailable
    """
    # Test database connectivity
    try:
        # Simple query to test connection
        session.exec(text("SELECT 1"))
        database_status = "connected"
        overall_status = "healthy"

        # Get connection pool status for monitoring
        pool_status = engine.pool.status()
        logger.info(f"Pool health: {pool_status}")

    except Exception as e:
        database_status = "disconnected"
        overall_status = "unhealthy"
        pool_status = None
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from e

    return HealthResponse(
        status=overall_status,
        database=database_status,
        version="1.0.0",
        timestamp=datetime.utcnow(),
        pool_status=pool_status
    )

