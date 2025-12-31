---
description: Implement JWT-based stateless authentication with FastAPI for scalable, horizontally-scalable APIs (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements JWT-based stateless authentication following Phase 2's proven pattern. Ensures horizontal scalability, stateless design, and secure token management.

### 1. Parse Requirements

Extract from user input or context:
- What entities need authentication? (Users, API endpoints)
- Token expiry duration (default: 7 days)
- Secret key source (environment variable)
- Claims to include (user_id, email, roles?)

### 2. Implement JWT Token Creation

**File**: `src/auth/jwt.py`

```python
from datetime import datetime, timedelta
import jwt
from src.config import settings

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT with standard claims"""
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_expiry_days)

    payload = {
        "sub": user_id,           # Subject (standard claim)
        "email": email,           # Custom claim
        "exp": expires_at,        # Expiry (standard claim)
        "iat": datetime.utcnow(), # Issued at
        "iss": "app-name"         # Issuer
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

def get_token_expiry_seconds() -> int:
    """Get token expiry duration in seconds"""
    return settings.jwt_expiry_days * 24 * 60 * 60
```

### 3. Implement FastAPI Dependency

**File**: `src/auth/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.jwt import verify_jwt_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract user_id from JWT token"""
    token = credentials.credentials

    try:
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload - missing user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### 4. Add Configuration Settings

**File**: `src/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str  # From environment
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate secret length
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")

    model_config = SettingsConfigDict(env_file=".env")
```

### 5. Usage in Protected Routes

**Example**:

```python
from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user)):
    """Protected endpoint requiring JWT"""
    return {"user_id": user_id, "message": "Access granted"}
```

### 6. Login Endpoint

**File**: `src/routes/auth.py`

```python
from src.auth.jwt import create_jwt_token, get_token_expiry_seconds

@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """Authenticate and return JWT"""
    # Verify credentials
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    # Generate token
    access_token = create_jwt_token(user.id, user.email)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expiry_seconds(),
        user=UserResponse.model_validate(user)
    )
```

### 7. Environment Setup

**File**: `.env.example`

```bash
JWT_SECRET=<generate-with-command-below>
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
```

**Generate secret**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8. Create Tests

**File**: `tests/test_jwt.py`

```python
import pytest
from src.auth.jwt import create_jwt_token, verify_jwt_token

def test_jwt_roundtrip():
    """Test token creation and verification"""
    token = create_jwt_token("user-123", "test@example.com")
    payload = verify_jwt_token(token)

    assert payload["sub"] == "user-123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload

def test_invalid_token():
    """Test invalid token raises error"""
    with pytest.raises(Exception):
        verify_jwt_token("invalid-token")
```

## Constitution Alignment

- ✅ **Stateless Architecture**: No server-side session storage
- ✅ **User Isolation**: user_id from token enforced on all operations
- ✅ **Security Standards**: JWT validated on every protected request
- ✅ **Horizontal Scalability**: Any server instance can verify tokens

## Success Criteria

- [ ] JWT token creation and verification working
- [ ] Secret key validated (minimum 32 characters)
- [ ] Protected routes require valid JWT
- [ ] 401 returned for missing/invalid/expired tokens
- [ ] user_id extracted from token and used for all operations
- [ ] Tests passing for token creation, verification, expiry

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 1
- PyJWT Documentation: https://pyjwt.readthedocs.io/
