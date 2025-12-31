"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text

from src.db import get_session
from src.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint to verify API and database connectivity.
    
    Returns:
        HealthResponse: System status including database connectivity
    
    Raises:
        HTTPException: 503 if database is unavailable
    """
    # Test database connectivity
    try:
        # Simple query to test connection
        session.exec(text("SELECT 1"))
        database_status = "connected"
        overall_status = "healthy"
    except Exception as e:
        database_status = "disconnected"
        overall_status = "unhealthy"
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from e
    
    return HealthResponse(
        status=overall_status,
        database=database_status,
        version="1.0.0",
        timestamp=datetime.utcnow()
    )

