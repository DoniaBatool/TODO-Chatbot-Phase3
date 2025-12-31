# Data Model: Authentication System

**Feature**: Authentication System  
**Branch**: `002-authentication-system`  
**Date**: 2025-12-10  
**Status**: Complete

## Purpose

This document defines the database schema changes needed for authentication. The primary change is extending the existing User model (from Feature 1) to include password storage for email/password authentication.

---

## Changes from Feature 1

### User Model Extension

**Existing User Model** (from Feature 1):
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: datetime
    tasks: List["Task"] = Relationship(back_populates="user")
```

**Updated User Model** (Feature 2):
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    password_hash: Optional[str] = Field(default=None, max_length=255)  # NEW
    created_at: datetime
    tasks: List["Task"] = Relationship(back_populates="user")
```

**New Field Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `password_hash` | VARCHAR(255) | NULL (for Better Auth compatibility) | bcrypt hashed password (60 chars typical, 255 max for safety) |

**Why Nullable?**
- Better Auth (frontend) may create users via different auth providers (OAuth, magic links)
- Those users won't have password_hash
- Backend signup sets password_hash
- Login endpoint requires password_hash to be present

---

## Database Migration

### Migration: Add password_hash Field

**Migration File**: `002_add_password_hash_to_users.py`

```python
"""Add password_hash to users table

Revision ID: 002_add_password
Revises: a8b1f6de382c
Create Date: 2025-12-10
"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_password'
down_revision = 'a8b1f6de382c'  # Previous migration from Feature 1

def upgrade():
    # Add password_hash column (nullable)
    op.add_column('users',
        sa.Column('password_hash', sa.String(255), nullable=True)
    )

def downgrade():
    # Remove password_hash column
    op.drop_column('users', 'password_hash')
```

**Migration Command**:
```bash
alembic revision --autogenerate -m "Add password_hash to users"
alembic upgrade head
```

---

## Password Hashing Specification

### bcrypt Hash Format

**Example bcrypt hash**:
```
$2b$12$abcdefghijklmnopqrstuv.yz123456789ABCDEFGHIJKLMNOPQRSTUV
│ │  │  │                      │
│ │  │  │                      └─ Hash output (31 chars)
│ │  │  └─ Salt (22 chars, base64)
│ │  └─ Cost factor (12 = 2^12 iterations)
│ └─ bcrypt variant (2b = current)
└─ Hash identifier ($)
```

**Properties**:
- **Length**: 60 characters (fixed)
- **Storage**: VARCHAR(255) for safety margin
- **Format**: Self-contained (includes algorithm, cost, salt)
- **Verification**: Compare plain password against hash using bcrypt.verify()

### Password Validation Rules

**Application Level**:
- Min length: 8 characters
- Max length: 100 characters (bcrypt compatibility)
- No other complexity rules for MVP (can add later)
- Trimmed before hashing (no leading/trailing spaces)

**Database Level**:
- password_hash: VARCHAR(255), nullable

---

## Authentication Data Flow

### Signup Flow

```
User Input (plain password)
        ↓
Validation (8-100 chars)
        ↓
bcrypt.hash(password, rounds=12)
        ↓
Store hash in users.password_hash
        ↓
Return user data (NO password)
```

### Login Flow

```
User Input (email + plain password)
        ↓
Lookup user by email (lowercase)
        ↓
bcrypt.verify(plain_password, user.password_hash)
        ↓
If match: Generate JWT token
        ↓
Return {"token": "eyJ...", "user": {...}}
```

### Token Verification Flow

```
Request Header: "Authorization: Bearer eyJ..."
        ↓
Extract token from header
        ↓
jwt.decode(token, SECRET, algorithm="HS256")
        ↓
Check expiry (exp claim)
        ↓
Extract user_id (sub claim)
        ↓
Inject user_id into route handler
```

---

## Updated SQLModel Implementation

### User Model with Authentication

```python
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    """
    User account with authentication support.
    
    Supports both:
    - Backend email/password auth (password_hash field)
    - Better Auth providers (password_hash can be null)
    """
    
    __tablename__ = "users"
    
    id: str = Field(
        primary_key=True,
        description="UUID (generated on signup or from Better Auth)"
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email (stored in lowercase)"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name"
    )
    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        description="bcrypt hashed password (null for OAuth users)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    
    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Field Changes from Feature 1**:
- ✅ Added: `password_hash` (Optional[str], max 255 chars)
- ✅ Email stored in lowercase for case-insensitive matching

---

## Security Data Storage

### What is Stored in Database

**User Record Example**:
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYLhSG3xZfW",
    "created_at": "2025-12-10T10:00:00Z"
}
```

**What is NEVER Stored**:
- ❌ Plain text passwords
- ❌ Reversible encrypted passwords
- ❌ Password hints or recovery questions

### What is in JWT Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1702252800,
  "exp": 1702857600,
  "iss": "todo-api"
}
```

**JWT Claims**:
- `sub` (subject): user_id
- `email`: user email (for display, not for auth)
- `iat` (issued at): token creation timestamp
- `exp` (expires): expiry timestamp (7 days)
- `iss` (issuer): "todo-api"

---

## Testing Considerations

### Test Data Setup

```python
# Fixture for creating authenticated user
@pytest.fixture
def test_user_with_password(session: Session):
    from src.auth.password import hash_password
    
    user = User(
        id="auth-test-user",
        email="auth@test.com",
        name="Auth Test User",
        password_hash=hash_password("SecurePassword123")
    )
    session.add(user)
    session.commit()
    return user

# Fixture for valid JWT token
@pytest.fixture
def valid_jwt_token(test_user_with_password: User):
    from src.auth.jwt import create_jwt_token
    from src.config import settings
    
    return create_jwt_token(
        test_user_with_password.id,
        test_user_with_password.email,
        settings.better_auth_secret
    )
```

### Edge Cases to Test

1. **Duplicate Email**: Should reject with 400
2. **Case Sensitivity**: user@test.com == USER@TEST.COM
3. **Weak Password**: <8 characters rejected
4. **Empty Password**: Validation error
5. **SQL Injection**: Parameterized queries prevent
6. **Token Expiry**: Expired token rejected with 401
7. **Invalid Token**: Malformed token rejected
8. **Missing Auth Header**: 401 Unauthorized

---

## Performance Considerations

### Password Hashing Performance

**bcrypt Cost Factor 12**:
- Hashing time: ~300ms per password
- Verification time: ~300ms per login
- Total login time: <500ms (acceptable for UX)

**Why 12 Rounds?**
- Security: 2^12 = 4096 iterations
- Industry standard (OWASP recommended minimum)
- Balance between security and performance

**Future Optimization** (if needed):
- Caching authenticated users (Redis)
- Async password hashing (run in thread pool)
- Argon2 migration for faster hashing

---

## Future Enhancements (Out of Scope)

- **Password Reset**: Email-based password reset flow
- **Email Verification**: Verify email before account activation
- **OAuth Providers**: Google, GitHub login via Better Auth
- **Two-Factor Auth**: TOTP or SMS verification
- **Session Management**: Refresh tokens for long-lived sessions
- **Account Deletion**: GDPR compliance features

These enhancements deferred to Phase 3 or security hardening phase.

---

## Summary

**Model Changes**: 1 (User model extended)  
**New Fields**: 1 (password_hash)  
**Migrations**: 1 (add password_hash column)  
**Security**: bcrypt hashing, JWT tokens, shared secret  
**Integration**: Compatible with Better Auth frontend (Feature 4)

**Status**: ✅ Ready for implementation

