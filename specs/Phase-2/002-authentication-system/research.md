# Research: Authentication System

**Feature**: Authentication System  
**Branch**: `002-authentication-system`  
**Date**: 2025-12-10  
**Status**: Complete

## Purpose

This document captures technical research and decisions for implementing JWT-based authentication with user registration, login, and token verification. Research focuses on security best practices, library selection, and integration patterns.

---

## Research Topics

### 1. JWT Library Selection for Python

**Decision**: Use **PyJWT** for JWT token management

**Rationale**:
- Most popular JWT library for Python (40M+ downloads/month)
- Active maintenance and security updates
- Simple, focused API (encode/decode tokens)
- Supports all standard JWT algorithms (HS256, RS256, etc.)
- Excellent documentation and community support
- Type hints support for Python 3.13+

**Implementation Pattern**:
```python
import jwt
from datetime import datetime, timedelta

# Generate token
def create_jwt_token(user_id: str, email: str, secret: str) -> str:
    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7),  # Expires in 7 days
        "iat": datetime.utcnow(),  # Issued at
        "iss": "todo-api"  # Issuer
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# Verify token
def verify_jwt_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
```

**Alternatives Considered**:
- **python-jose** - Rejected: More complex, includes unused features (JWE)
- **authlib** - Rejected: Too heavy, includes OAuth/OIDC features not needed
- **Custom JWT** - Rejected: Security risk, don't roll your own crypto

**References**:
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [JWT.io](https://jwt.io/)

---

### 2. Password Hashing Library Selection

**Decision**: Use **passlib** with bcrypt backend

**Rationale**:
- passlib provides high-level password hashing API
- Supports multiple algorithms (bcrypt, argon2, scrypt)
- Handles salt generation automatically
- Compatible with Better Auth password hashing
- Easy to switch algorithms if needed

**Implementation Pattern**:
```python
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Security Settings**:
- **Algorithm**: bcrypt
- **Work factor**: 12 rounds (default in passlib)
- **Salt**: Auto-generated per password
- **Max password length**: 100 characters (bcrypt limit is 72 bytes)

**Alternatives Considered**:
- **bcrypt library directly** - Rejected: passlib provides better API
- **argon2** - Deferred: bcrypt sufficient for MVP, argon2 for future
- **PBKDF2** - Rejected: bcrypt is more secure

**References**:
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

### 3. FastAPI Authentication Middleware Pattern

**Decision**: Use FastAPI's **Depends** pattern with dependency injection

**Rationale**:
- FastAPI native pattern for authentication
- Clean, reusable across routes
- Automatic OpenAPI documentation for auth
- Exception handling built-in
- Type-safe with type hints

**Implementation Pattern**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to extract and verify JWT token.
    Returns user_id if valid, raises 401 if invalid.
    """
    token = credentials.credentials
    
    try:
        payload = verify_jwt_token(token, settings.better_auth_secret)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

# Usage in routes:
@router.get("/protected-endpoint")
async def protected_route(user_id: str = Depends(get_current_user)):
    # user_id is automatically extracted from JWT
    return {"user_id": user_id}
```

**Alternatives Considered**:
- **Custom middleware class** - Rejected: Depends pattern is simpler
- **Decorator pattern** - Rejected: Less FastAPI-idiomatic
- **Manual token extraction** - Rejected: Not DRY, error-prone

**References**:
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [FastAPI OAuth2 with Password](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

### 4. Better Auth Integration Strategy

**Decision**: Backend provides **JWT verification compatible with Better Auth**

**Rationale**:
- Better Auth is frontend library (JavaScript/TypeScript)
- Frontend (Feature 4) will use Better Auth for UI and token management
- Backend needs to verify JWT tokens that Better Auth generates
- Shared BETTER_AUTH_SECRET enables token verification

**Architecture**:
```
┌─────────────────────┐         ┌─────────────────────┐
│   Next.js Frontend  │         │  FastAPI Backend    │
│                     │         │                     │
│  Better Auth        │  JWT    │  PyJWT Verify       │
│  (generates tokens) │────────▶│  (verifies tokens)  │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘
         │                               │
         │      BETTER_AUTH_SECRET       │
         └───────────(shared)────────────┘
```

**For Feature 2 (Backend Only)**:
- Backend implements its own signup/login endpoints
- Backend generates JWT tokens with same secret
- When Feature 4 (Frontend) is added, frontend Better Auth can also generate tokens
- Backend verifies tokens from either source (same secret, same algorithm)

**Configuration**:
```python
# Backend config.py
class Settings(BaseSettings):
    better_auth_secret: str  # Must be same as frontend
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7
```

**Alternatives Considered**:
- Separate backend auth library - Rejected: Redundant with Better Auth
- OAuth2 flow - Deferred: Simple JWT sufficient for MVP
- Session-based auth - Rejected: JWT is stateless and scales better

**References**:
- [Better Auth Documentation](https://www.better-auth.com/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

### 5. Email Validation Strategy

**Decision**: Use **email-validator** library for robust email validation

**Rationale**:
- Validates email format according to RFC standards
- Checks DNS records for domain validity (optional)
- Better than regex for edge cases
- Lightweight and fast
- Used by Pydantic for email validation

**Implementation**:
```python
from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr  # Pydantic uses email-validator
    password: str
    name: Optional[str] = None
```

**Alternatives Considered**:
- Regex validation - Rejected: Misses edge cases
- No validation - Rejected: Poor UX and data quality
- DNS check - Deferred: Adds latency, can enable later

**References**:
- [email-validator PyPI](https://pypi.org/project/email-validator/)
- [Pydantic Email Types](https://docs.pydantic.dev/latest/api/types/#pydantic.types.EmailStr)

---

### 6. User Model Extension Strategy

**Decision**: Add `password_hash` field to existing User model via migration

**Rationale**:
- User model already exists from Feature 1
- SQLModel supports model extension
- Alembic migration adds new column
- Backward compatible (nullable initially)

**Migration Strategy**:
```python
# New migration: 002_add_password_hash.py
def upgrade():
    op.add_column('users', 
        sa.Column('password_hash', sa.String(255), nullable=True)
    )
    
    # Future: Make nullable=False after Better Auth integration
```

**Updated User Model**:
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    password_hash: Optional[str] = Field(default=None, max_length=255)  # NEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: List["Task"] = Relationship(back_populates="user")
```

**Alternatives Considered**:
- Separate auth table - Rejected: Adds unnecessary join
- Store in JSON field - Rejected: Not type-safe
- Keep User unchanged - Rejected: Need password storage

---

## Summary of Technical Decisions

| Area | Technology/Pattern | Justification |
|------|-------------------|---------------|
| **JWT Library** | PyJWT | Industry standard, simple API, well-maintained |
| **Password Hashing** | passlib[bcrypt] | High-level API, bcrypt algorithm, 12 rounds |
| **Middleware** | FastAPI Depends | Native pattern, type-safe, auto-docs |
| **Better Auth Integration** | Shared JWT secret | Frontend/backend use same secret for tokens |
| **Email Validation** | email-validator (via Pydantic) | RFC-compliant, used by Pydantic EmailStr |
| **User Model** | Extend existing with password_hash | Alembic migration, backward compatible |

---

## Security Considerations

**Secret Management**:
- BETTER_AUTH_SECRET must be strong (min 32 characters)
- Loaded from environment variable only
- Never logged or exposed in responses
- Application fails to start if missing

**Password Security**:
- bcrypt with 12 rounds (2^12 iterations)
- Automatic salt generation
- Max 100 character passwords (bcrypt limit)
- Never store or log plain text passwords

**JWT Security**:
- HS256 algorithm (symmetric signing)
- 7 day expiry (configurable)
- Standard claims (sub, exp, iat, iss)
- Signature verification on every request

**Attack Prevention**:
- Same error for wrong password vs non-existent user (prevent enumeration)
- Lowercase email storage (prevent case-sensitivity bypass)
- Password complexity can be added (deferred to security hardening)
- Rate limiting can be added (deferred to production deployment)

---

## Next Steps

With research complete, proceed to:
1. **Phase 1**: Update data-model.md (add password_hash field)
2. **Phase 1**: Create contracts/ (auth endpoints specification)
3. **Phase 1**: Generate quickstart.md (signup/login testing)
4. **Phase 2**: Run `/sp.tasks` to break down implementation
