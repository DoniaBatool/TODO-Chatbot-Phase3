# Implementation Plan: Full-Stack Todo Application (Phase 2)

**Version**: 1.0 (Reverse Engineered)
**Date**: 2025-12-30
**Source**: phase2-reference/ codebase

## Architecture Overview

**Architectural Style**: Three-Layer REST API + Client-Server Web Application

**Reasoning**:
- Separation of concerns between frontend (presentation), backend (business logic), and database (persistence)
- RESTful API enables future mobile clients or integrations
- Stateless backend allows horizontal scaling
- Clear boundaries make testing and maintenance easier

**Diagram (ASCII)**:
```
┌─────────────────────────────────────────────────┐
│              Frontend (Next.js)                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Auth Pages   │  │ Tasks Page   │             │
│  │ /login       │  │ /tasks       │             │
│  │ /signup      │  │              │             │
│  └──────────────┘  └──────────────┘             │
│         │                   │                    │
│         └───────┬───────────┘                    │
│                 │ HTTP + JSON                    │
│           ┌─────▼─────┐                          │
│           │ API Client│  (JWT injection)         │
│           └───────────┘                          │
└─────────────────┼───────────────────────────────┘
                  │ HTTPS
┌─────────────────▼───────────────────────────────┐
│          Backend API (FastAPI)                   │
│  ┌───────────────────────────────────────────┐  │
│  │          Presentation Layer               │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐      │  │
│  │  │ Auth   │  │ Tasks  │  │ Health │      │  │
│  │  │ Routes │  │ Routes │  │        │      │  │
│  │  └────────┘  └────────┘  └────────┘      │  │
│  │       │           │                        │  │
│  │       │           │ (depends on)           │  │
│  │  ┌────▼───────────▼────┐                  │  │
│  │  │ Auth Middleware     │  (JWT verify)    │  │
│  │  └─────────────────────┘                  │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │        Business Logic Layer               │  │
│  │  ┌────────────┐  ┌──────────────┐        │  │
│  │  │ JWT Utils  │  │ Password     │        │  │
│  │  │            │  │ Utils        │        │  │
│  │  └────────────┘  └──────────────┘        │  │
│  │  ┌─────────────────────────────┐         │  │
│  │  │ Input Validation (Pydantic) │         │  │
│  │  └─────────────────────────────┘         │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │          Data Access Layer                │  │
│  │  ┌───────────────┐ ┌────────────────┐    │  │
│  │  │ User Model    │ │ Task Model     │    │  │
│  │  │ (SQLModel)    │ │ (SQLModel)     │    │  │
│  │  └───────────────┘ └────────────────┘    │  │
│  │           │                │               │  │
│  │           └────────┬───────┘               │  │
│  │                    │                        │  │
│  │           ┌────────▼────────┐              │  │
│  │           │ Database Engine │              │  │
│  │           │ (SQLModel +     │              │  │
│  │           │  Connection     │              │  │
│  │           │  Pool)          │              │  │
│  │           └─────────────────┘              │  │
│  └───────────────────────────────────────────┘  │
└─────────────────┼───────────────────────────────┘
                  │ PostgreSQL Wire Protocol
┌─────────────────▼───────────────────────────────┐
│     Database (Neon PostgreSQL)                   │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ users        │  │ tasks        │             │
│  │ - id (PK)    │  │ - id (PK)    │             │
│  │ - email      │  │ - user_id(FK)│             │
│  │ - password   │  │ - title      │             │
│  │   _hash      │  │ - description│             │
│  │ - name       │  │ - completed  │             │
│  │ - created_at │  │ - created_at │             │
│  └──────────────┘  │ - updated_at │             │
│                     └──────────────┘             │
└──────────────────────────────────────────────────┘
```

## Layer Structure

### Layer 1: Frontend (Presentation)
- **Responsibility**: User interface, form handling, API communication
- **Components**:
  - `app/login/page.tsx` - Login form
  - `app/signup/page.tsx` - Registration form
  - `app/tasks/page.tsx` - Task management interface
  - `lib/api-client.ts` - Centralized API communication
  - `components/` - Reusable UI components
- **Dependencies**: → Backend API (HTTP/JSON)
- **Technology**: Next.js 15 (App Router), React 18, TypeScript, Tailwind CSS

### Layer 2: Backend Presentation Layer (API Routes)
- **Responsibility**: HTTP request handling, input validation, response formatting
- **Components**:
  - `src/routes/auth.py` - Authentication endpoints (/auth/signup, /login, /me)
  - `src/routes/tasks.py` - Task CRUD endpoints (/tasks/*)
  - `src/routes/health.py` - Health check endpoint
  - `src/middleware/error_handler.py` - Global error handling
  - `src/middleware/` - CORS, error handlers
- **Dependencies**: → Business Logic Layer, → Auth Middleware
- **Technology**: FastAPI routers, Pydantic validation

### Layer 3: Backend Business Logic Layer
- **Responsibility**: Authentication logic, password hashing, JWT token management
- **Components**:
  - `src/auth/jwt.py` - JWT creation and verification
  - `src/auth/password.py` - Password hashing/verification (bcrypt)
  - `src/auth/dependencies.py` - FastAPI dependency for auth
  - `src/schemas.py` - Pydantic request/response models
- **Dependencies**: → Data Layer
- **Technology**: PyJWT, passlib[bcrypt], Pydantic

### Layer 4: Backend Data Access Layer
- **Responsibility**: Database models, ORM, connection management
- **Components**:
  - `src/models.py` - User and Task SQLModel definitions
  - `src/db.py` - Database engine, session management
  - `src/config.py` - Configuration from environment variables
  - `alembic/` - Database migrations
- **Dependencies**: → PostgreSQL Database
- **Technology**: SQLModel, psycopg2-binary, Alembic

### Layer 5: Database (Persistence)
- **Responsibility**: Data persistence, relational integrity, indexing
- **Components**:
  - `users` table - User accounts
  - `tasks` table - Todo tasks with foreign key to users
  - Indexes on user_id, completed, email
- **Technology**: Neon PostgreSQL (Serverless Postgres 14+)

## Design Patterns Applied

### Pattern 1: Dependency Injection (FastAPI)
- **Location**: All route handlers
- **Purpose**: Inject database session and authenticated user_id into handlers
- **Implementation**:
```python
# phase2-reference/backend/src/routes/tasks.py:19-24
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),  # Injected
    current_user_id: str = Depends(get_current_user),  # Injected
):
```
- **Benefits**: Testability (can mock dependencies), clean separation of concerns

### Pattern 2: DTO (Data Transfer Object) with Pydantic
- **Location**: src/schemas.py
- **Purpose**: Separate API contracts from database models, validate input/output
- **Implementation**:
```python
# Request DTOs (input validation)
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Response DTOs (output shaping)
class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    completed: bool
    created_at: datetime
    model_config = {"from_attributes": True}  # Allow SQLModel conversion
```
- **Benefits**: Input validation, API versioning flexibility, security (exclude password_hash)

### Pattern 3: Security Middleware (JWT Verification)
- **Location**: src/auth/dependencies.py
- **Purpose**: Centralize authentication logic, enforce security on protected routes
- **Implementation**:
```python
# phase2-reference/backend/src/auth/dependencies.py:13-75
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = verify_jwt_token(token)  # Raises exception if invalid
    return payload.get("sub")  # Return user_id
```
- **Benefits**: Single point of auth logic, declarative security (just add `Depends(get_current_user)`)

### Pattern 4: Connection Pooling
- **Location**: src/db.py
- **Purpose**: Reuse database connections, handle concurrency efficiently
- **Implementation**:
```python
# phase2-reference/backend/src/db.py (inferred from config)
engine = create_engine(
    settings.database_url,
    pool_size=5,         # Baseline connections
    max_overflow=5,      # Additional connections under load
    pool_timeout=30,     # Wait time for connection
    pool_pre_ping=True   # Verify connection before use
)
```
- **Benefits**: Performance (avoid connection overhead), reliability (pre-ping catches stale connections)

### Pattern 5: Configuration from Environment
- **Location**: src/config.py
- **Purpose**: 12-factor app compliance, environment-specific settings
- **Implementation**:
```python
# phase2-reference/backend/src/config.py:6-55
class Settings(BaseSettings):
    database_url: str
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```
- **Benefits**: No hardcoded secrets, easy deployment to different environments

### Pattern 6: Transaction Management
- **Location**: Route handlers
- **Purpose**: Ensure atomicity, handle rollback on errors
- **Implementation**:
```python
# phase2-reference/backend/src/routes/tasks.py:39-58
try:
    task = Task(user_id=current_user_id, title=task_data.title)
    session.add(task)
    session.commit()     # Commit if successful
    session.refresh(task)
    return task
except Exception as e:
    session.rollback()   # Rollback on error
    raise HTTPException(...)
```
- **Benefits**: Data consistency, automatic rollback on failure

## Data Flow

### Request Flow (Synchronous) - Create Task Example

1. **Frontend**: User fills form, clicks "Add Task"
   - `app/tasks/page.tsx`: Form submission → API call

2. **API Client**: Inject JWT token
   - `lib/api-client.ts`: Add `Authorization: Bearer <token>` header

3. **Network**: HTTPS POST to backend
   - Request: `POST /api/tasks` with JSON body `{title, description}`

4. **Backend - CORS Middleware**: Validate origin
   - `main.py`: Check CORS, allow request

5. **Backend - Route Handler**: Extract inputs
   - `routes/tasks.py`: Route matched, dependencies injected

6. **Auth Dependency**: Verify JWT
   - `auth/dependencies.py`: Extract token → verify signature → return user_id

7. **Input Validation**: Validate request body
   - Pydantic validates `TaskCreate` schema (title length, etc.)

8. **Database Session**: Get connection from pool
   - `db.py`: Provide session from connection pool

9. **Business Logic**: Create task model
   - `routes/tasks.py`: Create `Task` object with user_id from JWT (ignore client input)

10. **Database**: Insert record
    - SQLModel generates INSERT SQL, execute via session

11. **Transaction**: Commit changes
    - `session.commit()` → Database persists task

12. **Response**: Return created task
    - `TaskResponse` schema formats output (excludes sensitive fields)

13. **Frontend**: Update UI
    - API client receives response → update React state → UI re-renders

### Authentication Flow (Login Example)

1. **Frontend**: User submits login form
   - `app/login/page.tsx`: Email + password

2. **Backend**: Validate credentials
   - `routes/auth.py`: Find user by email (lowercase)

3. **Password Verification**: Check password hash
   - `auth/password.py`: `verify_password()` uses bcrypt

4. **JWT Generation**: Create access token
   - `auth/jwt.py`: Create token with `{sub: user_id, email, exp, iat, iss}`

5. **Response**: Return token + user data
   - `LoginResponse` schema with token, expires_in, user

6. **Frontend**: Store token
   - Save token in browser (localStorage/cookie)

7. **Subsequent Requests**: Include token
   - All API calls include `Authorization: Bearer <token>`

## Technology Stack

### Language & Runtime

**Backend**:
- **Choice**: Python 3.13
- **Rationale**:
  - Rapid development with FastAPI
  - Rich ecosystem for web APIs (SQLModel, Pydantic, PyJWT)
  - Type hints for IDE support and validation
  - Async support for high concurrency

**Frontend**:
- **Choice**: TypeScript 5.6
- **Rationale**:
  - Type safety reduces runtime errors
  - Better IDE autocomplete and refactoring
  - Catches bugs at compile time

### Web Frameworks

**Backend**:
- **Choice**: FastAPI 0.109+
- **Rationale**:
  - Automatic OpenAPI/Swagger docs
  - Pydantic validation built-in
  - Dependency injection system
  - Async support for high performance
  - Excellent developer experience

**Frontend**:
- **Choice**: Next.js 15 (App Router)
- **Rationale**:
  - React 18 with Server Components
  - Built-in routing
  - TypeScript support
  - Excellent performance (optimization)
  - Large community and ecosystem

### Database

**Choice**: Neon PostgreSQL (Serverless Postgres)
- **Rationale**:
  - ACID compliance for data integrity
  - Relational data (Users ↔ Tasks) fits well
  - JSON support for flexibility
  - Mature, battle-tested
  - Neon: Serverless, auto-scaling, generous free tier

### ORM/Data Layer

**Choice**: SQLModel 0.0.14
- **Rationale**:
  - Combines SQLAlchemy (ORM) + Pydantic (validation)
  - Type hints for IDE support
  - Automatic validation
  - FastAPI integration
  - Less boilerplate than SQLAlchemy alone

### Authentication

**Choice**: PyJWT 2.8+ (JWT tokens)
- **Rationale**:
  - Stateless authentication (no server-side sessions)
  - Scales horizontally (no session affinity needed)
  - Standard approach for API authentication
  - Works across web and future mobile apps

**Choice**: passlib[bcrypt] 1.7+ (password hashing)
- **Rationale**:
  - Industry standard for password hashing
  - Slow hashing defeats brute force
  - Salting defeats rainbow tables
  - Automatic cost factor tuning

### Styling

**Choice**: Tailwind CSS 3.4
- **Rationale**:
  - Utility-first CSS for rapid development
  - Small bundle size (only used classes)
  - Responsive design built-in
  - Excellent Next.js integration

### Database Migrations

**Choice**: Alembic 1.13+
- **Rationale**:
  - Standard migration tool for SQLAlchemy/SQLModel
  - Version control for database schema
  - Auto-generate migrations from model changes
  - Rollback capability

### HTTP Client

**Choice**: Next.js built-in fetch (frontend)
- **Rationale**:
  - Native browser API
  - Async/await support
  - No additional dependencies

### Validation

**Choice**: Pydantic 2.x (backend), Zod could be added (frontend)
- **Rationale**:
  - Declarative validation
  - Type coercion
  - Clear error messages
  - FastAPI integration

## Module Breakdown

### Backend Modules

**Module: src/auth**
- **Purpose**: Authentication and authorization logic
- **Key Files**:
  - `jwt.py` - Token creation/verification
  - `password.py` - Password hashing/verification
  - `dependencies.py` - FastAPI auth dependency
- **Dependencies**: PyJWT, passlib, config
- **Complexity**: Medium
- **Lines of Code**: ~200

**Module: src/routes**
- **Purpose**: API endpoint handlers
- **Key Files**:
  - `auth.py` - Signup, login, /me endpoints
  - `tasks.py` - Task CRUD endpoints
  - `health.py` - Health check
- **Dependencies**: models, schemas, auth, db
- **Complexity**: High (business logic)
- **Lines of Code**: ~400

**Module: src/**
- **Purpose**: Core application setup and models
- **Key Files**:
  - `main.py` - FastAPI app initialization
  - `models.py` - User/Task SQLModel definitions
  - `schemas.py` - Pydantic request/response schemas
  - `db.py` - Database connection management
  - `config.py` - Settings from environment
- **Dependencies**: FastAPI, SQLModel, Pydantic
- **Complexity**: Medium
- **Lines of Code**: ~400

**Module: src/middleware**
- **Purpose**: Request/response middleware
- **Key Files**:
  - `error_handler.py` - Global error handling
- **Dependencies**: FastAPI
- **Complexity**: Low
- **Lines of Code**: ~50

**Module: alembic**
- **Purpose**: Database migrations
- **Key Files**:
  - `env.py` - Alembic configuration
  - `versions/` - Migration scripts
- **Dependencies**: Alembic, SQLModel
- **Complexity**: Low
- **Lines of Code**: ~100

### Frontend Modules

**Module: app/**
- **Purpose**: Next.js pages (routes)
- **Key Files**:
  - `login/page.tsx` - Login page
  - `signup/page.tsx` - Signup page
  - `tasks/page.tsx` - Tasks management page
- **Dependencies**: React, API client
- **Complexity**: Medium
- **Lines of Code**: ~500

**Module: lib/**
- **Purpose**: Shared utilities
- **Key Files**:
  - `api-client.ts` - Centralized API communication
- **Dependencies**: fetch API
- **Complexity**: Low
- **Lines of Code**: ~100

**Module: components/**
- **Purpose**: Reusable React components
- **Key Files**: Task cards, forms, buttons
- **Dependencies**: React, Tailwind
- **Complexity**: Low
- **Lines of Code**: ~200

## Regeneration Strategy

### Option 1: Specification-First Rebuild
**Steps**:
1. Start with `spec.md` (requirements and intent)
2. Apply extracted patterns from `intelligence-object.md`
3. Implement with modern best practices (fill gaps identified)
4. Test-driven development using acceptance criteria from spec

**Improvements to make**:
- Add refresh token mechanism
- Implement password reset flow
- Add email verification
- Add rate limiting on auth endpoints
- Implement pagination for task lists
- Add comprehensive error boundaries (frontend)
- Add metrics instrumentation
- Generate comprehensive API docs

**Timeline**: 4-6 weeks with 1-2 developers

### Option 2: Incremental Refactoring (Strangler Pattern)
**Steps**:
1. Create new implementation alongside existing code
2. Route new traffic to new system (feature flag)
3. Gradual migration of features one at a time
4. Parallel run to validate equivalence
5. Cutover when confidence high

**Timeline**: 8-12 weeks (safer, zero downtime)

## Improvement Opportunities

### Technical Improvements

**1. Replace Separate Frontend/Backend with Monorepo**
- **Rationale**: Simpler deployment, shared TypeScript types, better DX
- **Effort**: Medium
- **Tools**: Turborepo, pnpm workspaces

**2. Add Redis for Token Blacklist**
- **Rationale**: Enable server-side logout
- **Effort**: Low
- **Benefits**: Better security

**3. Add Email Service Integration (SendGrid/Postmark)**
- **Rationale**: Enable email verification, password reset
- **Effort**: Medium
- **Benefits**: Production-ready auth

**4. Implement Refresh Token Rotation**
- **Rationale**: Better security, user experience (auto re-auth)
- **Effort**: Medium
- **Benefits**: Industry standard

### Architectural Improvements

**1. Introduce Event Sourcing for Task History**
- **Enables**: Audit trail, undo functionality, analytics
- **Effort**: High
- **Trade-off**: Complexity vs auditability

**2. Add GraphQL Layer**
- **Enables**: Flexible queries, reduce over-fetching
- **Effort**: Medium
- **Trade-off**: Learning curve, added layer

**3. Microservices Architecture**
- **Separate**: Auth service, Task service, Notification service
- **Enables**: Independent scaling, tech diversity
- **Effort**: Very High
- **Trade-off**: Complexity vs scalability (overkill for current scale)

### Operational Improvements

**1. CI/CD Pipeline**
- **Tools**: GitHub Actions, GitLab CI
- **Stages**: Lint → Test → Build → Deploy
- **Effort**: Low
- **Benefits**: Automated quality checks, faster deployment

**2. Infrastructure as Code**
- **Tools**: Terraform, Pulumi
- **Enables**: Reproducible infrastructure, version control
- **Effort**: Medium

**3. Monitoring Dashboards**
- **Tools**: Grafana + Prometheus (metrics), Sentry (errors)
- **Effort**: Low
- **Benefits**: Production observability

**4. Load Testing**
- **Tools**: k6, Locust
- **Purpose**: Validate performance under load
- **Effort**: Low
- **Benefits**: Confidence in scalability

---

**Plan Completeness**: This plan documents the actual architecture discovered in Phase 2 codebase, providing a blueprint for regeneration with improvements. All technology choices are rationalized based on observed patterns and industry best practices.
