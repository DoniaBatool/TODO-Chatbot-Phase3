---
description: Implement secure password hashing with bcrypt following industry best practices (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements password security using bcrypt following Phase 2's proven pattern. Ensures passwords are never stored in plain text and are resistant to brute force attacks.

### 1. Install Dependencies

```bash
pip install "passlib[bcrypt]>=1.7.4"
```

### 2. Implement Password Utilities

**File**: `src/auth/password.py`

```python
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """
    Hash password with bcrypt.

    bcrypt automatically:
    - Generates unique salt per password
    - Uses cost factor (default ~12)
    - Returns salt + hash in single string

    Args:
        password: Plain text password from user

    Returns:
        str: bcrypt hash (~60 characters)
    """
    hashed = bcrypt.hash(password)
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    bcrypt.verify:
    - Extracts salt from hashed_password
    - Hashes plain_password with same salt
    - Compares in constant time (timing attack resistant)

    Args:
        plain_password: Plain text password from login attempt
        hashed_password: Stored bcrypt hash from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.verify(plain_password, hashed_password)
```

### 3. Database Model

**File**: `src/models.py`

```python
from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,  # bcrypt output ~60 chars
        description="bcrypt hashed password (null for OAuth users)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # NEVER include password_hash in response schemas
```

### 4. Signup Implementation

**File**: `src/routes/auth.py`

```python
from src.auth.password import hash_password

@router.post("/auth/signup", response_model=UserResponse, status_code=201)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """Register new user with hashed password"""

    # Normalize email
    email_lower = signup_data.email.lower()

    # Check for duplicate
    existing = session.exec(select(User).where(User.email == email_lower)).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    try:
        # Hash password IMMEDIATELY
        password_hashed = hash_password(signup_data.password)

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=email_lower,
            name=signup_data.name,
            password_hash=password_hashed  # Store hash, not plain
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Return user WITHOUT password_hash
        return user

    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Failed to create user: {e}") from e
```

### 5. Login Implementation

**File**: `src/routes/auth.py`

```python
from src.auth.password import verify_password
from src.auth.jwt import create_jwt_token

@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Authenticate user and return JWT"""

    email_lower = login_data.email.lower()

    # Find user
    user = session.exec(select(User).where(User.email == email_lower)).first()

    # User not found
    if not user:
        logger.warning("Login failed: email not found (%s)", email_lower)
        raise HTTPException(401, "Invalid credentials")

    # OAuth user (no password)
    if not user.password_hash:
        logger.warning("Login failed: no password hash (%s)", email_lower)
        raise HTTPException(401, "Invalid credentials")

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning("Login failed: invalid password (%s)", email_lower)
        raise HTTPException(401, "Invalid credentials")

    # Password correct - generate token
    access_token = create_jwt_token(user.id, user.email)

    logger.info("Login success: email=%s id=%s", user.email, user.id)
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expiry_seconds(),
        user=UserResponse.model_validate(user)
    )
```

### 6. Response Schemas - NEVER Return Password Hash

**File**: `src/schemas.py`

```python
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    """Signup request with password validation"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = None

    # Optional: Add password strength validation
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # Add complexity requirements if needed
        return v


class UserResponse(BaseModel):
    """User response - EXCLUDES password_hash"""
    id: str
    email: str
    name: Optional[str]
    created_at: datetime

    # password_hash intentionally NOT included
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str  # Plain text from client


class LoginResponse(BaseModel):
    """Login success response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse  # Does NOT include password_hash
```

### 7. Testing

**File**: `tests/test_password.py`

```python
import pytest
from src.auth.password import hash_password, verify_password

def test_password_hashing():
    """Test password hashing produces different hashes (salt)"""
    password = "test123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different hashes (different salts)
    assert hash1 != hash2

    # Both verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_password_verification():
    """Test verification works correctly"""
    password = "correct_password"
    wrong_password = "wrong_password"

    hashed = hash_password(password)

    # Correct password verifies
    assert verify_password(password, hashed) is True

    # Wrong password fails
    assert verify_password(wrong_password, hashed) is False


def test_password_never_logged():
    """Ensure passwords never appear in logs"""
    # Review logging configuration
    # Ensure password fields not logged even in debug mode
    pass
```

## Security Best Practices

### ✅ DO:
- Hash passwords immediately on receipt
- Use bcrypt (or argon2) for hashing
- Store hash, never plain text
- Verify on backend only
- Use constant-time comparison (bcrypt.verify does this)
- NEVER log passwords (even in debug mode)
- Return 401 for wrong password (same as user not found)

### ❌ DON'T:
- Store plain text passwords
- Send passwords to frontend after hashing
- Include password_hash in API responses
- Log passwords anywhere
- Use weak hashing (MD5, SHA1)
- Send password hashes to client
- Validate passwords on frontend only

## Constitution Alignment

- ✅ **Security Standards**: bcrypt hashing, never plain text
- ✅ **Privacy**: Passwords never exposed in responses or logs
- ✅ **Industry Standards**: Following OWASP guidelines

## Success Criteria

- [ ] passlib[bcrypt] installed
- [ ] hash_password() and verify_password() implemented
- [ ] Passwords hashed immediately on signup
- [ ] password_hash column in User model (nullable for OAuth)
- [ ] password_hash NEVER in UserResponse schema
- [ ] Login verifies password correctly
- [ ] Wrong password returns 401 (same as user not found)
- [ ] Tests verify hashing produces different salts
- [ ] Tests verify correct/wrong password verification
- [ ] Passwords never logged anywhere

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 3
- OWASP: Password Storage - https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- passlib documentation: https://passlib.readthedocs.io/
