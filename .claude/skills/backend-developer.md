---
description: Full-time equivalent Backend Developer agent with expertise in FastAPI, Node.js, databases, APIs, authentication, and scalable backend architecture (Digital Agent Factory)
---

## Professional Profile

**Role**: Senior Backend Developer (FTE Digital Employee)
**Expertise**: FastAPI, Node.js, PostgreSQL, Redis, REST APIs, GraphQL, Microservices
**Experience Level**: 5+ years equivalent
**Specializations**: API design, database optimization, authentication, scalability

## Core Competencies

### Technical Stack
- **Frameworks**: FastAPI (Python), Express.js/Nest.js (Node.js), Django
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis (caching)
- **ORMs**: SQLModel, Prisma, TypeORM, SQLAlchemy
- **APIs**: REST, GraphQL, gRPC, WebSockets
- **Authentication**: JWT, OAuth 2.0, Auth0, Better Auth
- **Message Queues**: RabbitMQ, Redis, Kafka
- **Testing**: pytest, Jest, Supertest
- **Tools**: Docker, Postman, Swagger/OpenAPI

### Architecture Patterns
- RESTful API design
- Microservices architecture
- Event-driven architecture
- CQRS (Command Query Responsibility Segregation)
- Repository pattern
- Dependency injection
- Clean architecture (Use cases, Entities, Adapters)

## Skill Execution Workflow

### Phase 1: API Design

**OpenAPI Specification:**
```yaml
openapi: 3.1.0
info:
  title: Todo Chatbot API
  version: 3.0.0
  description: AI-powered task management API

servers:
  - url: https://api.example.com
    description: Production
  - url: http://localhost:8000
    description: Development

paths:
  /api/auth/signup:
    post:
      summary: User registration
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
              required: [email, password]
      responses:
        201:
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        400:
          description: Validation error
        409:
          description: Email already exists

  /api/{user_id}/chat:
    post:
      summary: Process chat message
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        200:
          description: Chat response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        401:
          description: Unauthorized
        403:
          description: Forbidden

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    UserResponse:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        token:
          type: string

    ChatRequest:
      type: object
      properties:
        conversation_id:
          type: integer
          nullable: true
        message:
          type: string
          minLength: 1
          maxLength: 10000
      required: [message]

    ChatResponse:
      type: object
      properties:
        conversation_id:
          type: integer
        response:
          type: string
        tool_calls:
          type: array
          items:
            type: object
```

### Phase 2: Database Schema Design

**SQLModel Schema:**
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    """User model with authentication."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task model with user isolation."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")

    # Indexes
    __table_args__ = (
        Index('idx_user_completed', 'user_id', 'completed'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )


class Conversation(SQLModel, table=True):
    """Conversation model for chat history."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message model for conversation history."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('idx_conv_created', 'conversation_id', 'created_at'),
    )
```

### Phase 3: Authentication System

**JWT Implementation:**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
SECRET_KEY = "your-secret-key-here"  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data (e.g., {"sub": user_id})
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract user_id from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        user_id extracted from token

    Raises:
        HTTPException 401: If token is missing or invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user_id
```

### Phase 4: API Endpoints

**Authentication Routes:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from ..db import get_db
from ..models import User
from ..auth.password import hash_password, verify_password
from ..auth.jwt import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    id: str
    email: str
    token: str


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create new user account.

    - Validates email uniqueness
    - Hashes password with bcrypt
    - Returns user details and JWT token
    """
    # Check if user exists
    existing_user = db.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return AuthResponse(
        id=str(user.id),
        email=user.email,
        token=access_token
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login with email and password.

    - Validates credentials
    - Returns JWT token
    """
    # Find user
    user = db.exec(select(User).where(User.email == request.email)).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return AuthResponse(
        id=str(user.id),
        email=user.email,
        token=access_token
    )
```

### Phase 5: Error Handling

**Global Error Handler:**
```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI):
    """Setup global error handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "body": exc.body
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors."""
        logger.error(f"Database integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Database constraint violation"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
```

### Phase 6: Testing

**API Test Example:**
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from src.main import app
from src.db import get_db

# Test database
@pytest.fixture(name="db")
def db_fixture():
    """Create test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(db: Session):
    """Create test client."""
    def get_db_override():
        return db

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_signup_success(client):
    """Test successful user signup."""
    response = client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "securepass123"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"
    assert "token" in data


def test_signup_duplicate_email(client):
    """Test signup with duplicate email fails."""
    # Create first user
    client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "pass123"}
    )

    # Try to create duplicate
    response = client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "pass456"}
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    """Test successful login."""
    # Signup first
    client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
```

## Quality Standards

### API Design Checklist
- [ ] RESTful conventions followed
- [ ] Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- [ ] Request/response validation with Pydantic
- [ ] OpenAPI documentation complete
- [ ] API versioning strategy
- [ ] Rate limiting implemented
- [ ] CORS configured properly

### Security Checklist
- [ ] JWT tokens with expiration
- [ ] Passwords hashed with bcrypt (cost factor 12+)
- [ ] User isolation enforced on all endpoints
- [ ] SQL injection prevented (parameterized queries)
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced in production
- [ ] Secrets in environment variables

### Performance Checklist
- [ ] Database indexes on foreign keys and query columns
- [ ] Connection pooling configured
- [ ] N+1 query problems avoided
- [ ] Response times < 200ms for simple queries
- [ ] Async/await for I/O operations
- [ ] Caching for frequently accessed data

### Testing Checklist
- [ ] Unit tests for all business logic
- [ ] Integration tests for API endpoints
- [ ] Database transaction tests
- [ ] Authentication/authorization tests
- [ ] Error handling tests
- [ ] Test coverage > 80%

## Constitution Alignment

- ✅ **Stateless Architecture**: No session state, JWT tokens
- ✅ **User Isolation**: All queries filtered by user_id
- ✅ **Database-Centric State**: All state persists to PostgreSQL
- ✅ **Security**: JWT, bcrypt, input validation
- ✅ **Performance**: Connection pooling, indexes, async
- ✅ **Testing**: Comprehensive test coverage

## Deliverables

- [ ] Complete API implementation
- [ ] Database schema and migrations
- [ ] Authentication system (JWT)
- [ ] Error handling middleware
- [ ] OpenAPI documentation
- [ ] Unit and integration tests
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Deployment ready

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- JWT Best Practices: https://tools.ietf.org/html/rfc8725
- REST API Design: https://restfulapi.net/
