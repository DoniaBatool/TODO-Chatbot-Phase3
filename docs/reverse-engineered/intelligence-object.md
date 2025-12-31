# Reusable Intelligence: Phase 2 Todo Application

**Version**: 1.0 (Extracted from Codebase)
**Date**: 2025-12-30
**Source**: phase2-reference/

## Overview

This document captures the reusable intelligence embedded in Phase 2—patterns, decisions, and expertise worth preserving and applying to Phase 3 and future projects.

---

## Extracted Skills

### Skill 1: JWT-Based Stateless Authentication

**Persona**: You are a backend engineer designing scalable authentication systems that work across multiple servers without session affinity.

**Questions to ask before implementing JWT authentication**:
- What information needs to be in the token payload? (user_id, email, roles?)
- How long should tokens be valid? (Security vs UX trade-off)
- Do we need refresh tokens or just access tokens?
- Where will the secret key be stored? (Environment variable, secrets manager?)
- What happens when tokens expire? (Re-login, automatic refresh?)
- Should tokens be revokable? (Blacklist required?)

**Principles**:
- **Stateless by design**: No server-side session storage, all auth state in token
- **Short expiry for security**: Access tokens 7-15 days max, shorter for sensitive apps
- **Secure secret storage**: Minimum 32 characters, stored in environment variables
- **Standard claims**: Use `sub` for user_id, include `exp`, `iat`, `iss`
- **HTTPS only**: Never send tokens over unencrypted connections
- **Bearer scheme**: Use `Authorization: Bearer <token>` header

**Implementation Pattern** (from phase2-reference/backend/src/auth/jwt.py):
```python
from datetime import datetime, timedelta
import jwt

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT with standard claims"""
    expires_at = datetime.utcnow() + timedelta(days=7)

    payload = {
        "sub": user_id,       # Subject (standard claim)
        "email": email,       # Custom claim
        "exp": expires_at,    # Expiry (standard claim)
        "iat": datetime.utcnow(),  # Issued at
        "iss": "todo-api"     # Issuer
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
```

**FastAPI Dependency Integration**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract user_id from JWT token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token")
    return user_id

# Usage in route
@app.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
```

**When to apply**:
- All multi-user REST APIs
- Microservices architectures (shared secret across services)
- Mobile/SPA applications (no cookies, token in storage)
- Stateless backends that need horizontal scaling

**Contraindications**:
- Server-rendered apps where sessions are easier (consider cookies)
- Apps requiring instant token revocation (need Redis blacklist)
- Very short-lived sessions (session tokens may be simpler)

---

### Skill 2: User Isolation with Ownership Enforcement

**Persona**: You are a security-focused engineer preventing horizontal privilege escalation by enforcing data isolation at the database query level.

**Questions to ask before implementing user isolation**:
- What entity is owned by users? (tasks, documents, orders?)
- How is ownership represented? (user_id foreign key?)
- At what layer is isolation enforced? (Database query, business logic, API?)
- What happens when user tries to access other user's data? (403, 404, silent filter?)
- Are there any cross-user operations allowed? (admin access, sharing?)
- Is audit logging required for access attempts?

**Principles**:
- **Filter at query level**: Never fetch data, then filter in code—filter in WHERE clause
- **user_id from JWT, never request**: Ignore client-supplied user_id for security
- **Explicit ownership checks**: For single-record operations, verify ownership explicitly
- **403 vs 404**: Return 403 Forbidden (not 404) to avoid information leakage
- **Log security events**: Log all ownership violations with both user IDs
- **Index user_id**: Performance critical for user-scoped queries

**Implementation Pattern** (from phase2-reference/backend/src/routes/tasks.py):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

# List tasks - scope query to authenticated user
@router.get("/tasks")
async def list_tasks(
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """List tasks for authenticated user only"""
    # Build query scoped to authenticated user
    statement = select(Task).where(Task.user_id == current_user_id)

    # Execute - only returns this user's tasks
    tasks = session.exec(statement).all()
    return tasks


# Get single task - explicit ownership check
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Get task with ownership verification"""
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        raise HTTPException(404, "Task not found")

    # Check ownership
    if task.user_id != current_user_id:
        # Log security event
        logger.warning(
            "Forbidden access: user=%s attempted task_id=%s owned_by=%s",
            current_user_id, task_id, task.user_id
        )
        # Return 403 Forbidden (not 404 to avoid info leak)
        raise HTTPException(403, "Forbidden: Task does not belong to you")

    return task


# Create task - user_id from JWT, never from request
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Create task for authenticated user"""
    # SECURITY: Always use authenticated user_id
    # Ignore any user_id in request body
    task = Task(
        user_id=current_user_id,  # From JWT, not client
        title=task_data.title,
        description=task_data.description
    )

    session.add(task)
    session.commit()
    return task
```

**Database Schema Requirements**:
```sql
-- user_id column in all user-owned tables
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    completed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Critical: Index user_id for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Optionally: Composite index for common filters
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

**When to apply**:
- All multi-tenant SaaS applications
- Any system with user-owned data
- B2C applications with privacy requirements
- Healthcare, financial, or regulated industries

**Contraindications**:
- Single-user applications
- Admin-only tools (but still log access)

---

### Skill 3: Password Security with bcrypt

**Persona**: You are a security engineer protecting user credentials with industry-standard cryptographic hashing.

**Questions to ask before implementing password security**:
- What hashing algorithm to use? (bcrypt, argon2, scrypt?)
- What cost factor/work factor? (Higher = slower = more secure, but UX impact)
- Is salt generation automatic? (bcrypt does this)
- Where are passwords validated? (backend only, never frontend)
- Are password complexity requirements needed?
- Is password history tracking required? (prevent reuse)

**Principles**:
- **Never store plain text**: Hash passwords immediately on receipt
- **Use bcrypt**: Industry standard, slow by design, automatic salting
- **Cost factor tuning**: Default (10-12) is good, increase over time
- **Verify on backend only**: Never send hashed password to client
- **Constant-time comparison**: bcrypt verify prevents timing attacks
- **Never log passwords**: Not even in debug logs

**Implementation Pattern** (from phase2-reference/backend/src/auth/password.py):
```python
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    # bcrypt automatically:
    # - Generates unique salt per password
    # - Uses cost factor (configurable, default ~12)
    # - Returns salt + hash in single string
    hashed = bcrypt.hash(password)
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # bcrypt.verify:
    # - Extracts salt from hashed_password
    # - Hashes plain_password with same salt
    # - Compares in constant time (timing attack resistant)
    return bcrypt.verify(plain_password, hashed_password)

# Usage in signup
def signup(email: str, password: str):
    password_hash = hash_password(password)
    user = User(email=email, password_hash=password_hash)
    db.save(user)
    # Never return password or hash
    return UserResponse(id=user.id, email=user.email)

# Usage in login
def login(email: str, password: str):
    user = db.get_user_by_email(email)
    if not user or not user.password_hash:
        raise AuthenticationError("Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid credentials")

    # Password correct - generate token
    token = create_jwt_token(user.id, user.email)
    return {"access_token": token}
```

**Schema Considerations**:
```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True)
    password_hash: Optional[str] = Field(
        default=None,  # Nullable for OAuth users
        max_length=255  # bcrypt output is ~60 chars
    )
    # NEVER include password_hash in response schemas

# Response schema (excludes password_hash)
class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    # password_hash intentionally excluded
```

**When to apply**:
- All user authentication systems
- Any system storing sensitive credentials
- Password-based login flows

**Alternatives considered**:
- **Argon2**: Winner of Password Hashing Competition, more modern
  - Pros: More resistant to GPU/ASIC attacks
  - Cons: Less mature ecosystem, newer standard
  - Recommendation: Use for new projects if library support good
- **scrypt**: Memory-hard function
  - Pros: Good security properties
  - Cons: Less common than bcrypt
- **PBKDF2**: Older standard
  - Pros: Widely supported
  - Cons: Weaker than bcrypt/argon2, not recommended

---

### Skill 4: Pydantic DTOs for Input Validation

**Persona**: You are a backend engineer using declarative validation to prevent invalid data from entering your system.

**Questions to ask before implementing validation**:
- What are valid values for each field? (type, range, format, length)
- Should validation be declarative (Pydantic) or imperative (manual checks)?
- What error messages should users see? (Technical vs user-friendly)
- Are there custom validators needed? (email uniqueness, business rules)
- Should validation happen at API layer, business layer, or both?

**Principles**:
- **Validate early**: API layer, before business logic
- **Declarative over imperative**: Use Pydantic Field constraints
- **Type safety**: Leverage Python type hints
- **Custom validators**: Use `@field_validator` for complex rules
- **Separate request/response schemas**: Don't mix input DTOs and database models
- **Clear error messages**: Pydantic provides detailed validation errors

**Implementation Pattern** (from phase2-reference/backend/src/schemas.py):
```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class TaskCreate(BaseModel):
    """Request DTO for creating task - input validation"""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Custom validator: reject whitespace-only titles"""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()  # Clean whitespace

    @field_validator("description")
    @classmethod
    def description_length(cls, v: Optional[str]) -> Optional[str]:
        """Ensure description doesn't exceed limit"""
        if v and len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v


class TaskResponse(BaseModel):
    """Response DTO for task - output shaping"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    # Allow conversion from SQLModel (ORM mode)
    model_config = {"from_attributes": True}


class SignupRequest(BaseModel):
    """Signup request with email validation"""
    email: EmailStr  # Automatic email format validation
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = Field(default=None, max_length=255)

    # Could add custom validator for password strength
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Enforce password complexity"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # Optional: Add complexity requirements
        # if not any(c.isupper() for c in v):
        #     raise ValueError("Password must contain uppercase")
        return v
```

**FastAPI Integration** (automatic validation):
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,  # Pydantic validates automatically
    session: Session = Depends(get_session)
):
    # If we reach here, validation passed
    # FastAPI returns 422 automatically if invalid
    task = Task(**task_data.model_dump())
    session.add(task)
    session.commit()
    return task  # Pydantic serializes to TaskResponse
```

**Error Response Example** (automatic from FastAPI + Pydantic):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

**When to apply**:
- All FastAPI/Pydantic-based APIs
- Any system with strict input requirements
- Type-safe Python applications

**Benefits**:
- Automatic validation before route handler
- Clear, structured error messages
- Type hints for IDE support
- Self-documenting API (via OpenAPI schema generation)

---

### Skill 5: Database Connection Pooling

**Persona**: You are a backend engineer optimizing database access for concurrent requests without overwhelming the database.

**Questions to ask before implementing connection pooling**:
- How many concurrent users/requests expected? (determines pool size)
- What is database connection limit? (Neon free tier: 100 connections)
- What is acceptable wait time for a connection? (timeout setting)
- How long should connections be reused? (recycle time)
- How to detect stale connections? (pre-ping)
- What happens when pool exhausted? (overflow vs error)

**Principles**:
- **Pool size formula**: Start with `2 * CPU cores`, tune based on load
- **Max overflow**: Allow temporary overflow (2x pool size) for spikes
- **Connection recycling**: Recycle connections after 1 hour (prevents stale connections)
- **Pre-ping**: Test connection before use (detect database restarts)
- **Timeout**: 30s wait for connection (fail fast if pool exhausted)
- **Monitor pool usage**: Log pool metrics to detect sizing issues

**Implementation Pattern** (from phase2-reference/backend/src/db.py):
```python
from sqlmodel import create_engine, Session
from contextlib import contextmanager

# Configuration
DATABASE_URL = "postgresql://user:pass@host:5432/db"
POOL_SIZE = 10          # Baseline connections
MAX_OVERFLOW = 20       # Additional connections under load
POOL_TIMEOUT = 30       # Seconds to wait for connection
POOL_RECYCLE = 3600     # Recycle connections after 1 hour

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,

    # Connection pool settings
    pool_size=POOL_SIZE,         # Maintain 10 connections
    max_overflow=MAX_OVERFLOW,   # Allow up to 30 total (10 + 20)
    pool_timeout=POOL_TIMEOUT,   # Wait 30s for connection
    pool_recycle=POOL_RECYCLE,   # Recycle after 1 hour

    # Health check
    pool_pre_ping=True,          # Test connection before use

    # Debugging (disable in production)
    echo=False                   # Don't log SQL
)

# FastAPI dependency for session management
def get_session():
    """Provide database session from pool"""
    with Session(engine) as session:
        yield session
        # Session automatically closed (returned to pool)

# Usage in route
@app.get("/tasks")
async def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks
    # Connection returned to pool automatically
```

**Connection Lifecycle**:
```
1. Request arrives → FastAPI calls get_session()
2. get_session() gets connection from pool (or creates if needed)
3. Session used for database operations
4. End of request → Session closed (connection returned to pool)
5. Connection reused for next request
```

**Pool Sizing Guidelines**:
```python
# Conservative (low traffic)
pool_size = 5
max_overflow = 5
# Total: 10 connections max

# Moderate (typical web app)
pool_size = 10
max_overflow = 20
# Total: 30 connections max

# High traffic (needs tuning)
pool_size = 20
max_overflow = 30
# Total: 50 connections max

# Formula
# pool_size = expected_concurrent_requests / avg_request_duration_seconds
# If 100 req/s, avg 0.1s per request → 100 * 0.1 = 10 pool size
```

**Monitoring Pool Health**:
```python
# Log pool statistics (add to health endpoint)
from sqlalchemy import pool

@app.get("/health")
async def health_check():
    pool_status = engine.pool.status()
    # Returns: "Pool size: 10  Connections in pool: 8
    #           Current Overflow: 2 Current Checked out connections: 2"

    return {
        "database": "connected",
        "pool_status": pool_status
    }
```

**When to apply**:
- All database-backed web applications
- APIs with moderate-to-high traffic
- Long-running applications

**Contraindications**:
- Serverless functions (use connection per invocation, not pool)
- Very low traffic (overhead not justified)
- Single-threaded applications

---

### Skill 6: Transaction Management with Rollback

**Persona**: You are a database engineer ensuring data consistency through atomic operations and proper error handling.

**Questions to ask before implementing transactions**:
- What operations must be atomic? (all-or-nothing)
- What is the scope of a transaction? (single request, multi-step operation?)
- How to handle errors? (rollback, retry, propagate?)
- Are nested transactions needed? (savepoints)
- What isolation level is required? (read committed, serializable?)
- Should commits be explicit or automatic?

**Principles**:
- **Atomicity**: Group related operations in single transaction
- **Explicit rollback**: Always rollback on error
- **Short transactions**: Minimize lock time
- **Handle exceptions**: Try/except with rollback in except block
- **Commit explicitly**: Don't rely on auto-commit in production code
- **Refresh after commit**: Get updated object from database

**Implementation Pattern** (from phase2-reference/backend/src/routes/tasks.py):
```python
from sqlmodel import Session
from fastapi import Depends, HTTPException

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create task with transaction management"""
    try:
        # Start transaction (implicit)
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description
        )

        session.add(task)

        # Commit transaction (explicit)
        session.commit()

        # Refresh to get database-generated values (id, timestamps)
        session.refresh(task)

        return task

    except Exception as e:
        # Rollback on any error
        session.rollback()

        # Log error for debugging
        logger.error(f"Failed to create task: {e}")

        # Return error to client
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        ) from e
```

**Multi-Step Transaction Example**:
```python
@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session)
):
    """Create order with inventory update - both must succeed"""
    try:
        # Step 1: Check inventory
        product = session.get(Product, order_data.product_id)
        if product.stock < order_data.quantity:
            raise HTTPException(400, "Insufficient stock")

        # Step 2: Create order
        order = Order(
            user_id=user_id,
            product_id=order_data.product_id,
            quantity=order_data.quantity
        )
        session.add(order)

        # Step 3: Update inventory
        product.stock -= order_data.quantity
        session.add(product)

        # Commit all changes atomically
        session.commit()
        session.refresh(order)

        return order

    except HTTPException:
        # Re-raise HTTP exceptions (business logic errors)
        session.rollback()
        raise
    except Exception as e:
        # Rollback and wrap database errors
        session.rollback()
        raise HTTPException(500, f"Order creation failed: {e}") from e
```

**When to apply**:
- All database write operations
- Multi-step operations that must be atomic
- Operations with side effects (inventory updates, payments)

**Benefits**:
- Data consistency (no partial updates)
- Error recovery (rollback to clean state)
- ACID guarantees

---

## Architecture Decision Records (Inferred)

### ADR-001: JWT Tokens over Server-Side Sessions

**Status**: Accepted (inferred from implementation)

**Context**:
The application requires user authentication with:
- Horizontal scalability (multiple backend instances)
- Support for future mobile clients
- Stateless backend design

**Decision**: Use JWT tokens for authentication instead of server-side sessions

**Rationale** (evidence from codebase):
1. **No session storage**: No Redis/Memcached session store in codebase
   - Location: Absence of session storage configuration
   - Pattern: JWT created and verified, no session lookup

2. **Stateless authentication**:
   - Location: phase2-reference/backend/src/auth/jwt.py
   - Pattern: All auth state in token, no server memory

3. **Horizontal scaling enabled**:
   - No session affinity required
   - Any backend instance can verify any token

**Consequences**:

**Positive**:
- Stateless (easy horizontal scaling)
- No database/cache lookups for auth
- Works across web and mobile
- Self-contained (all info in token)

**Negative**:
- Cannot revoke tokens before expiry (mitigation: short TTL)
- Larger payload in each request (vs session cookie)
- Compromised secret invalidates all tokens

**Mitigations Observed**:
- 7-day expiry (balance security and UX)
- Secret validation at startup (minimum 32 chars)
- HTTPS only (inferred from production deployment)

---

### ADR-002: SQLModel over SQLAlchemy + Pydantic

**Status**: Accepted (inferred from implementation)

**Context**:
Need ORM for database access with:
- Type hints for IDE support
- Input/output validation
- FastAPI integration
- Reduced boilerplate

**Decision**: Use SQLModel (combines SQLAlchemy + Pydantic) instead of separate SQLAlchemy and Pydantic models

**Rationale** (evidence from codebase):
1. **Single model definition**: Database models also serve as schemas
   - Location: phase2-reference/backend/src/models.py
   - Pattern: `class User(SQLModel, table=True)` used for both ORM and validation

2. **Type hints throughout**:
   - All fields have type annotations
   - IDE autocomplete works

3. **Automatic validation**:
   - Pydantic validation built into models
   - FastAPI integration seamless

**Consequences**:

**Positive**:
- Less code (no duplicate models)
- Type safety
- Automatic validation
- Excellent FastAPI integration

**Negative**:
- Less separation of concerns (DB schema == API schema)
- Harder to version API independently of database
- Newer library (less mature than SQLAlchemy alone)

**Mitigations Observed**:
- Separate response schemas (TaskResponse) exclude sensitive fields
- Can add DTO layer if needed for API versioning

---

### ADR-003: Neon PostgreSQL over Traditional PostgreSQL Hosting

**Status**: Accepted (inferred from deployment)

**Context**:
Need cloud database with:
- Serverless scaling
- Generous free tier
- PostgreSQL compatibility
- Low maintenance

**Decision**: Use Neon Serverless PostgreSQL instead of traditional RDS/managed PostgreSQL

**Rationale**:
- **Serverless**: Auto-scaling, pay-per-use
- **Free tier**: Sufficient for Phase 2
- **PostgreSQL compatibility**: Standard tools work
- **Low ops**: No server management

**Consequences**:

**Positive**:
- Zero ops (no server maintenance)
- Cost-effective (free tier + scale to zero)
- Fast setup (minutes vs hours)

**Negative**:
- Vendor lock-in (Neon-specific)
- Connection limits on free tier
- Cold start latency (mitigated by connection pooling)

---

## Code Patterns & Conventions

### Pattern 1: FastAPI Dependency Injection

**Observed in**: All route handlers

**Structure**:
```python
# Define reusable dependencies
def get_session():
    with Session(engine) as session:
        yield session

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify JWT, return user_id
    return user_id

# Inject into routes
@router.get("/tasks")
async def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    # session and user_id automatically provided
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
```

**Benefits**:
- Testability (can mock dependencies)
- Reusability (share logic across routes)
- Clean separation (auth logic not in handler)

---

### Pattern 2: DTO Separation (Request/Response Schemas)

**Observed in**: All API endpoints

**Structure**:
```python
# Request DTO (input validation)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str]

# Response DTO (output shaping)
class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    completed: bool
    created_at: datetime
    model_config = {"from_attributes": True}

# Database Model (persistence)
class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: str
    description: Optional[str]
    completed: bool
    password_hash: Optional[str]  # Internal only

# Route
@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    task = Task(**task_data.model_dump())
    # ...
    return task  # Automatically converted to TaskResponse
```

**Benefits**:
- Security (exclude password_hash from response)
- API versioning (change response without changing DB)
- Validation (different rules for input vs output)

---

## Lessons Learned

### What Worked Well

**1. FastAPI + SQLModel Stack**
- **Why**: Minimal boilerplate, excellent DX, automatic validation
- **Evidence**: Clean code in routes/, schemas.py
- **Benefit**: Fast development, type safety, self-documenting API

**2. User Isolation Enforced at Query Level**
- **Why**: Security critical, filtered in database not code
- **Evidence**: All task queries have `.where(Task.user_id == current_user_id)`
- **Benefit**: Zero cross-user data leakage

**3. Connection Pooling**
- **Why**: Performance, handles concurrent requests efficiently
- **Evidence**: Engine configuration in db.py
- **Benefit**: Stable under load, no connection exhaustion

**4. Pydantic Validation**
- **Why**: Declarative, automatic, clear error messages
- **Evidence**: Schemas in schemas.py with validators
- **Benefit**: Input validation without boilerplate

### What Could Be Improved

**1. No Refresh Token Mechanism**
- **Issue**: Only access tokens, no refresh tokens
- **Impact**: Users must re-login every 7 days
- **Recommendation**: Implement refresh token rotation (15min access, 30day refresh)

**2. No Rate Limiting**
- **Issue**: Auth endpoints vulnerable to brute force
- **Impact**: Security risk
- **Recommendation**: Add slowapi or similar for rate limiting

**3. No Pagination**
- **Issue**: Task list returns all tasks (no limit)
- **Impact**: Performance degrades with many tasks
- **Recommendation**: Add pagination (cursor or offset-based)

**4. No Metrics/Observability**
- **Issue**: Only basic logging, no metrics
- **Impact**: Blind to production issues
- **Recommendation**: Add Prometheus metrics, Sentry for errors

### What to Avoid in Future Projects

**1. No Email Verification**
- **Why bad**: Users can register with invalid emails
- **Alternative**: Send verification email on signup (sendgrid, postmark)

**2. Mixing Database Models and API Schemas**
- **Why bad**: Couples database to API contract
- **Alternative**: Separate DTOs even with SQLModel (demonstrated with UserResponse)

**3. No API Versioning**
- **Why bad**: Breaking changes break clients
- **Alternative**: Version API routes (/api/v1/, /api/v2/)

---

## Reusability Assessment

### Components Reusable As-Is

**1. JWT Authentication Pattern** → Portable to any FastAPI project
- Files: `auth/jwt.py`, `auth/dependencies.py`
- Usage: Drop into new project, change secret

**2. Connection Pooling Configuration** → Portable to any SQLModel project
- Files: `db.py`
- Usage: Copy engine setup

**3. User Isolation Pattern** → Portable to any multi-tenant app
- Pattern: `.where(entity.user_id == current_user_id)`
- Usage: Apply to all user-owned entities

**4. Transaction Management** → Portable to any database app
- Pattern: try/commit/rollback pattern
- Usage: Wrap all write operations

### Patterns Worth Generalizing

**1. FastAPI Dependency Injection** → Create skill/template
- Generalizable to: Authentication, database sessions, configuration

**2. Pydantic Validation DTOs** → Create code generator
- Input: Database model
- Output: CreateDTO, UpdateDTO, ResponseDTO

**3. User Ownership Enforcement** → Create decorator
```python
@enforce_ownership(Task, "task_id")
async def update_task(task_id: int, user_id: str = Depends(get_current_user)):
    # Ownership check automatic
```

### Phase 3 Application (AI Chatbot)

These patterns will be directly applicable to Phase 3:

**1. JWT Authentication** → Reuse for chatbot API
**2. User Isolation** → Apply to Conversation and Message models
**3. Connection Pooling** → Essential for stateless AI backend
**4. DTO Validation** → Validate chatbot message inputs
**5. Transaction Management** → Atomic conversation + message creation

**New Patterns for Phase 3**:
- MCP tool definitions (wrap task operations as tools)
- OpenAI Agents SDK integration (AI orchestration)
- Conversation state management (database-centric, stateless)
- Tool invocation logging (audit trail)

---

**Intelligence Extraction Complete**: This document provides a comprehensive knowledge base extracted from Phase 2, ready for application to Phase 3 and beyond. Each pattern includes decision context, implementation details, and practical guidance for reuse.
