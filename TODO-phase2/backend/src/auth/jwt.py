"""JWT token generation and verification utilities."""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.config import settings


def create_jwt_token(user_id: str, email: str) -> str:
    """
    Create a JWT access token for authenticated user.
    
    Args:
        user_id: User unique identifier
        email: User email address
    
    Returns:
        str: Encoded JWT token
    
    Example:
        >>> token = create_jwt_token("user-123", "user@example.com")
        >>> token.startswith("eyJ")
        True
    """
    # Calculate expiry time
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_expiry_days)
    
    # Build JWT payload with standard claims
    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,  # User email (for convenience)
        "exp": expires_at,  # Expiry time
        "iat": datetime.utcnow(),  # Issued at
        "iss": "todo-api"  # Issuer
    }
    
    # Encode token with secret
    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return token


def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
    
    Returns:
        dict: Decoded token payload with claims
    
    Raises:
        ExpiredSignatureError: If token has expired
        InvalidTokenError: If token is invalid or signature doesn't match
    
    Example:
        >>> token = create_jwt_token("user-123", "user@example.com")
        >>> payload = verify_jwt_token(token)
        >>> payload["sub"]
        'user-123'
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
        
    except ExpiredSignatureError as e:
        raise ExpiredSignatureError("Token has expired") from e
        
    except InvalidTokenError as e:
        raise InvalidTokenError("Invalid token") from e


def get_token_expiry_seconds() -> int:
    """
    Get token expiry duration in seconds.
    
    Returns:
        int: Expiry duration in seconds (7 days = 604800 seconds)
    """
    return settings.jwt_expiry_days * 24 * 60 * 60

