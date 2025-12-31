# Research: Backend API Foundation

**Feature**: Backend API Foundation  
**Branch**: `001-backend-api-foundation`  
**Date**: 2025-12-09  
**Status**: Complete

## Purpose

This document captures technical research and decisions for implementing the FastAPI backend with Neon PostgreSQL database integration. Research focuses on best practices, library selection, and architectural patterns needed for the implementation.

---

## Research Topics

### 1. Neon PostgreSQL Connection and Pooling

**Decision**: Use `psycopg2-binary` with SQLModel's built-in connection pooling

**Rationale**:
- Neon provides standard PostgreSQL connection strings compatible with psycopg2
- SQLModel (built on SQLAlchemy) includes connection pooling via `create_engine()`
- Neon serverless architecture handles scaling automatically on their side
- Connection pooling reduces overhead for repeated database operations

**Configuration Best Practices**:
```python
# Recommended pool settings for Neon
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Min connections
    max_overflow=5,        # Max additional connections
    pool_timeout=30,       # Connection timeout in seconds
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True     # Verify connection health before use
)
```

**Alternatives Considered**:
- `asyncpg` (async driver) - Rejected: Adds complexity for minimal performance gain in MVP
- Direct psycopg3 - Rejected: SQLModel doesn't support it yet
- Connection per request - Rejected: Too slow, connection overhead

**References**:
- [Neon Connection Docs](https://neon.tech/docs/connect/connect-from-any-app)
- [SQLModel Database Docs](https://sqlmodel.tiangolo.com/tutorial/connect/create-connected-tables/)

---

### 2. FastAPI Error Handling Patterns

**Decision**: Use global exception handlers with HTTPException for consistency

**Rationale**:
- FastAPI's `HTTPException` provides consistent error responses
- Global exception handlers catch unexpected errors and format them properly
- Pydantic validation errors are automatically handled by FastAPI
- Custom error response format ensures consistent structure

**Implementation Pattern**:
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )

# Example usage in routes
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
            headers={"X-Error-Code": "TASK_NOT_FOUND"}
        )
    return task
```

**Error Response Format**:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

**Status Code Standards**:
- 200 OK - Successful GET/PUT/PATCH
- 201 Created - Successful POST
- 204 No Content - Successful DELETE
- 400 Bad Request - Invalid input (Pydantic validation)
- 404 Not Found - Resource not found
- 500 Internal Server Error - Unexpected errors
- 503 Service Unavailable - Database connection issues

**Alternatives Considered**:
- Custom error classes - Rejected: HTTPException sufficient for MVP
- Problem Details (RFC 7807) - Deferred: Can add later if needed
- Error codes in headers only - Rejected: Body is more accessible

**References**:
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

### 3. SQLModel Relationship Patterns and Migrations

**Decision**: Use SQLModel relationships with explicit foreign keys, migrations via Alembic

**Rationale**:
- SQLModel provides type-safe ORM with Pydantic integration
- Relationships defined with `Relationship()` for easy navigation
- Foreign keys enforce data integrity at database level
- Alembic (SQLAlchemy's migration tool) handles schema changes

**Relationship Pattern**:
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True)  # UUID from Better Auth
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Index Strategy**:
- `users.email` - Unique index for login lookups
- `tasks.user_id` - Index for filtering tasks by user
- `tasks.completed` - Index for status filtering

**Migration Approach**:
```bash
# Initialize Alembic
alembic init alembic

# Generate migration from SQLModel models
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

**Alternatives Considered**:
- Pure SQLAlchemy - Rejected: SQLModel provides better Pydantic integration
- Django ORM - Rejected: Not compatible with FastAPI
- Raw SQL migrations - Rejected: Alembic provides versioning and rollback
- SQLModel auto-create tables - Rejected: No migration history

**References**:
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

### 4. FastAPI Project Structure Best Practices

**Decision**: Use layered architecture with separation of concerns

**Rationale**:
- Clear separation makes code maintainable and testable
- Follows FastAPI community best practices
- Easy to scale as features are added
- Models, routes, and business logic are separated

**Directory Structure Justification**:
```text
backend/src/
├── main.py          # App creation, middleware, route registration
├── config.py        # Centralized config (Pydantic Settings)
├── db.py            # Database session management
├── models.py        # SQLModel database entities
├── schemas.py       # Pydantic request/response models
├── routes/          # API endpoint handlers
│   ├── health.py
│   └── tasks.py
└── middleware/      # Cross-cutting concerns
    └── error_handler.py
```

**Layer Responsibilities**:
1. **main.py** - Application entry point, CORS, middleware setup
2. **config.py** - Environment variables, app settings
3. **db.py** - Database connection factory, session management
4. **models.py** - Database schema (what's stored)
5. **schemas.py** - API contracts (what's sent/received)
6. **routes/** - HTTP handlers (request → response)
7. **middleware/** - Pre/post processing logic

**Alternatives Considered**:
- Flat structure (all files in root) - Rejected: Hard to navigate
- Domain-driven structure (features/tasks/) - Deferred: Overkill for MVP
- Repository pattern - Rejected: Adds abstraction without clear benefit for CRUD
- Service layer - Deferred: Can add if business logic grows

**References**:
- [FastAPI Project Structure](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)

---

### 5. UV Package Manager Usage

**Decision**: Use UV for dependency management and virtual environment

**Rationale**:
- UV is faster than pip/poetry (Rust-based)
- Compatible with standard Python packaging
- Simpler than Poetry for basic projects
- Recommended in Phase 2 constitution

**Project Setup**:
```bash
# Initialize project with UV
uv init

# Add dependencies
uv add fastapi uvicorn sqlmodel psycopg2-binary python-dotenv pydantic-settings

# Add dev dependencies
uv add --dev pytest pytest-asyncio httpx

# Install dependencies
uv sync

# Run application
uv run uvicorn src.main:app --reload
```

**pyproject.toml Structure**:
```toml
[project]
name = "todo-backend"
version = "0.1.0"
description = "FastAPI backend for Todo application"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.1.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0"
]
```

**Alternatives Considered**:
- Poetry - Rejected: Slower, more complex than needed
- pip + venv - Rejected: UV is faster and more modern
- Pipenv - Rejected: Less active development

**References**:
- [UV Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)

---

### 6. Environment Configuration and Secrets Management

**Decision**: Use Pydantic Settings with .env file for configuration

**Rationale**:
- Type-safe configuration with validation
- Easy to test with override values
- Clear separation of config from code
- .env file for local development, environment variables for production

**Implementation**:
```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # App
    app_name: str = "Todo API"
    debug: bool = False
    
    # API
    api_v1_prefix: str = "/api"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
```

**.env.example** (template for developers):
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
DEBUG=true
API_V1_PREFIX=/api
```

**Security Best Practices**:
- Never commit .env file to git (add to .gitignore)
- Provide .env.example as template
- Use environment variables in production
- Validate required settings on startup
- Fail fast if DATABASE_URL missing

**Alternatives Considered**:
- python-decouple - Rejected: Pydantic Settings more integrated
- Environment variables only - Rejected: .env more convenient for local dev
- Config files (JSON/YAML) - Rejected: Env vars are more deployment-friendly

**References**:
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App Config](https://12factor.net/config)

---

## Summary of Technical Decisions

| Area | Technology/Pattern | Justification |
|------|-------------------|---------------|
| **Database Driver** | psycopg2-binary + SQLModel | Standard PostgreSQL driver with ORM type safety |
| **Connection Pooling** | SQLAlchemy engine pool | Built-in, reliable, configurable |
| **Error Handling** | HTTPException + global handlers | Consistent responses, proper status codes |
| **Data Models** | SQLModel with relationships | Type-safe ORM with Pydantic integration |
| **Migrations** | Alembic | Industry standard, version control for schema |
| **Project Structure** | Layered architecture | Clear separation, maintainable, scalable |
| **Package Manager** | UV | Fast, modern, Python 3.13 compatible |
| **Configuration** | Pydantic Settings + .env | Type-safe, validated, environment-based |

---

## Open Questions / Future Research

- **Caching Strategy**: Consider Redis for GET /tasks if performance becomes an issue (deferred to optimization phase)
- **Rate Limiting**: May need rate limiting middleware for production (deferred to security hardening)
- **API Documentation**: FastAPI auto-generates OpenAPI docs (no additional research needed)
- **Logging Strategy**: Use Python logging module with structured logs (can be added during implementation)

---

## Next Steps

With research complete, proceed to:
1. **Phase 1**: Generate data-model.md (database schema design)
2. **Phase 1**: Create contracts/ (API endpoint specifications)
3. **Phase 1**: Generate quickstart.md (testing scenarios)
4. **Phase 2**: Run `/sp.tasks` to break down implementation tasks

