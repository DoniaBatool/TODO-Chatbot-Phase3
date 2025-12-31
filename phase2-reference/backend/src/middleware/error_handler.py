"""Global error handling middleware."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup global exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Handle all unhandled exceptions.
        
        Returns a 500 Internal Server Error with sanitized error message.
        """
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """
        Handle Pydantic validation errors.
        
        Returns a 400 Bad Request with validation details.
        """
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.errors(),
                "error_code": "VALIDATION_ERROR"
            }
        )

