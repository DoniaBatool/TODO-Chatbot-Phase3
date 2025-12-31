"""FastAPI authentication dependencies for JWT verification."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.auth.jwt import verify_jwt_token

# HTTPBearer security scheme for extracting tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and verify JWT token.
    
    Extracts JWT token from Authorization header, verifies signature,
    checks expiry, and returns authenticated user_id.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
    
    Returns:
        str: Authenticated user_id from JWT token
    
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    
    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    # Extract token from credentials
    token = credentials.credentials
    
    try:
        # Verify token and get payload
        payload = verify_jwt_token(token)
        
        # Extract user_id from 'sub' claim
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload - missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

