# Implementation Tasks: Full-Stack Todo Application (Phase 2)

**Version**: 1.0 (Reverse Engineered)
**Date**: 2025-12-30
**Source**: phase2-reference/ codebase

## Overview

This task breakdown represents how to rebuild Phase 2 from scratch using the specification and plan.

**Estimated Timeline**: 4-6 weeks
**Team Size**: 1-2 full-stack developers

---

## Phase 1: Project Setup & Infrastructure

**Timeline**: Week 1, Days 1-2
**Dependencies**: None

### Task 1.1: Backend Project Initialization
- [ ] Create backend directory structure
- [ ] Initialize Python project with `pyproject.toml`
- [ ] Configure Python 3.13 as minimum version
- [ ] Add dependencies:
  ```toml
  fastapi>=0.109.0
  uvicorn[standard]>=0.27.0
  sqlmodel>=0.0.14
  psycopg2-binary>=2.9.9
  python-dotenv>=1.0.0
  pydantic-settings>=2.1.0
  alembic>=1.13.0
  PyJWT>=2.8.0
  passlib[bcrypt]>=1.7.4
  python-multipart>=0.0.6
  email-validator>=2.1.0
  ```
- [ ] Add dev dependencies:
  ```toml
  pytest>=7.4.0
  pytest-asyncio>=0.23.0
  httpx>=0.26.0
  ruff>=0.1.0
  ```
- [ ] Configure Ruff for linting (line-length=88, target=py313)
- [ ] Configure pytest settings (asyncio_mode=auto)
- [ ] Create `.gitignore` (Python, env files, IDE files)
- [ ] Create `README.md` with setup instructions

### Task 1.2: Frontend Project Initialization
- [ ] Create frontend directory
- [ ] Initialize Next.js 15 project with TypeScript
  ```bash
  npx create-next-app@latest --typescript --app --tailwind --eslint
  ```
- [ ] Configure dependencies in `package.json`:
  ```json
  {
    "next": "15.1.11",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "clsx": "2.1.1"
  }
  ```
- [ ] Configure TypeScript (`tsconfig.json`)
- [ ] Configure Tailwind CSS
- [ ] Configure ESLint
- [ ] Create `.gitignore` (node_modules, .next, env files)

### Task 1.3: Database Setup (Neon PostgreSQL)
- [ ] Sign up for Neon account (https://neon.tech)
- [ ] Create new project: "todo-app-phase2"
- [ ] Get connection string (DATABASE_URL)
- [ ] Test connection from local machine
  ```bash
  psql "<connection-string>"
  ```
- [ ] Document connection string format in README

### Task 1.4: Environment Configuration
- [ ] Create `.env.example` files (backend and frontend)
- [ ] Backend `.env` variables:
  ```
  DATABASE_URL=postgresql://...
  BETTER_AUTH_SECRET=<generate-with-python>
  JWT_ALGORITHM=HS256
  JWT_EXPIRY_DAYS=7
  CORS_ORIGINS=http://localhost:3000
  DEBUG=true
  ```
- [ ] Generate secret:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Frontend `.env.local` variables:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
- [ ] Document all environment variables in README
- [ ] Add validation in config.py for minimum secret length (32 chars)

---

## Phase 2: Backend - Database Layer

**Timeline**: Week 1, Days 3-5
**Dependencies**: Phase 1 complete

### Task 2.1: Configuration Module
- [ ] Create `src/config.py`
- [ ] Define `Settings` class with Pydantic BaseSettings:
  - database_url (required)
  - db_pool_size (default=5)
  - db_max_overflow (default=5)
  - db_pool_timeout (default=30)
  - app_name (default="Todo API")
  - debug (default=False)
  - api_v1_prefix (default="/api")
  - cors_origins (default="*")
  - better_auth_secret (required)
  - jwt_algorithm (default="HS256")
  - jwt_expiry_days (default=7)
- [ ] Add `model_config` for .env file loading
- [ ] Add validation in `__init__` for secret length
- [ ] Add `cors_origins_list` property to parse comma-separated origins
- [ ] Create global `settings` instance
- [ ] Write unit tests for Settings validation

### Task 2.2: Database Models
- [ ] Create `src/models.py`
- [ ] Define `User` model (SQLModel, table=True):
  ```python
  - id: str (PK, UUID)
  - email: str (unique, indexed, max 255)
  - name: Optional[str] (max 255)
  - password_hash: Optional[str] (max 255)
  - created_at: datetime (auto)
  - tasks: Relationship to Task
  ```
- [ ] Define `Task` model (SQLModel, table=True):
  ```python
  - id: Optional[int] (PK, auto-increment)
  - user_id: str (FK to users.id, indexed)
  - title: str (1-200 chars)
  - description: Optional[str] (max 1000)
  - completed: bool (default False, indexed)
  - created_at: datetime (auto)
  - updated_at: datetime (auto)
  - user: Relationship to User
  ```
- [ ] Add docstrings to all models and fields
- [ ] Add cascade delete on User → Tasks relationship

### Task 2.3: Database Engine & Session Management
- [ ] Create `src/db.py`
- [ ] Create SQLModel engine with connection pooling:
  ```python
  engine = create_engine(
      settings.database_url,
      pool_size=settings.db_pool_size,
      max_overflow=settings.db_max_overflow,
      pool_timeout=settings.db_pool_timeout,
      pool_recycle=3600,
      pool_pre_ping=True,
      echo=settings.debug
  )
  ```
- [ ] Define `get_session()` dependency:
  ```python
  def get_session():
      with Session(engine) as session:
          yield session
  ```
- [ ] Export engine and get_session

### Task 2.4: Database Migrations (Alembic)
- [ ] Initialize Alembic:
  ```bash
  alembic init alembic
  ```
- [ ] Configure `alembic/env.py`:
  - Import SQLModel.metadata
  - Set target_metadata = SQLModel.metadata
  - Configure database URL from settings
- [ ] Configure `alembic.ini`:
  - Remove hardcoded sqlalchemy.url (use env.py)
- [ ] Create initial migration:
  ```bash
  alembic revision --autogenerate -m "Initial schema - users and tasks"
  ```
- [ ] Review generated migration script
- [ ] Add indexes manually if not auto-generated:
  - users.email (unique)
  - tasks.user_id
  - tasks.completed
- [ ] Apply migration:
  ```bash
  alembic upgrade head
  ```
- [ ] Verify tables created in Neon dashboard
- [ ] Document migration workflow in README

---

## Phase 3: Backend - Authentication & Security

**Timeline**: Week 2
**Dependencies**: Phase 2 complete

### Task 3.1: Password Utilities
- [ ] Create `src/auth/password.py`
- [ ] Implement `hash_password(password: str) -> str`:
  - Use passlib.hash.bcrypt
  - Return bcrypt hash
- [ ] Implement `verify_password(plain: str, hashed: str) -> bool`:
  - Use passlib verify
  - Return True/False
- [ ] Write unit tests:
  - Test hashing produces different hash each time (salt)
  - Test verification works for correct password
  - Test verification fails for wrong password

### Task 3.2: JWT Utilities
- [ ] Create `src/auth/jwt.py`
- [ ] Implement `create_jwt_token(user_id: str, email: str) -> str`:
  - Calculate expiry: datetime.utcnow() + timedelta(days=settings.jwt_expiry_days)
  - Build payload: {sub, email, exp, iat, iss: "todo-api"}
  - Encode with PyJWT: jwt.encode(payload, secret, algorithm)
  - Return token string
- [ ] Implement `verify_jwt_token(token: str) -> dict`:
  - Decode with PyJWT: jwt.decode(token, secret, algorithms=[...])
  - Return payload dict
  - Raise ExpiredSignatureError if expired
  - Raise InvalidTokenError if invalid
- [ ] Implement `get_token_expiry_seconds() -> int`:
  - Return settings.jwt_expiry_days * 24 * 60 * 60
- [ ] Write unit tests:
  - Test token creation and verification round-trip
  - Test expired token raises ExpiredSignatureError
  - Test invalid token raises InvalidTokenError
  - Test token contains correct claims

### Task 3.3: Authentication Dependency
- [ ] Create `src/auth/dependencies.py`
- [ ] Define HTTPBearer security scheme:
  ```python
  security = HTTPBearer()
  ```
- [ ] Implement `get_current_user` dependency:
  ```python
  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(security)
  ) -> str:
      token = credentials.credentials
      try:
          payload = verify_jwt_token(token)
          user_id = payload.get("sub")
          if not user_id:
              raise HTTPException(401, "Invalid token payload")
          return user_id
      except ExpiredSignatureError:
          raise HTTPException(401, "Token has expired")
      except InvalidTokenError:
          raise HTTPException(401, "Invalid token")
  ```
- [ ] Write integration tests:
  - Test valid token returns user_id
  - Test missing token returns 401
  - Test invalid token returns 401
  - Test expired token returns 401

### Task 3.4: Pydantic Schemas - Authentication
- [ ] Create/update `src/schemas.py`
- [ ] Define `SignupRequest`:
  ```python
  - email: EmailStr
  - password: str (min_length=8, max_length=100)
  - name: Optional[str] (max_length=255)
  ```
- [ ] Define `LoginRequest`:
  ```python
  - email: EmailStr
  - password: str
  ```
- [ ] Define `UserResponse`:
  ```python
  - id: str
  - email: str
  - name: Optional[str]
  - created_at: datetime
  - model_config = {"from_attributes": True}
  ```
- [ ] Define `LoginResponse`:
  ```python
  - access_token: str
  - token_type: str (default="bearer")
  - expires_in: int
  - user: UserResponse
  ```
- [ ] Write schema validation tests

---

## Phase 4: Backend - API Routes (Authentication)

**Timeline**: Week 2-3
**Dependencies**: Phase 3 complete

### Task 4.1: Authentication Routes
- [ ] Create `src/routes/auth.py`
- [ ] Create APIRouter with tag="Authentication"
- [ ] Implement `POST /auth/signup`:
  - Accept SignupRequest
  - Convert email to lowercase
  - Check if email already exists → 400 if duplicate
  - Generate UUID for user_id
  - Hash password with bcrypt
  - Create User model
  - Save to database
  - Return UserResponse (201 Created)
  - Log signup success with user_id
- [ ] Implement `POST /auth/login`:
  - Accept LoginRequest
  - Convert email to lowercase
  - Find user by email → 401 if not found
  - Check password_hash exists → 401 if null
  - Verify password → 401 if invalid
  - Create JWT token
  - Return LoginResponse with token and user data
  - Log login success
- [ ] Implement `GET /auth/me` (protected):
  - Use `Depends(get_current_user)` to get user_id
  - Get user from database → 404 if not found
  - Return UserResponse
- [ ] Add error handling with try/except
- [ ] Add logging for all auth events
- [ ] Write API tests for all endpoints

### Task 4.2: Health Check Route
- [ ] Create `src/routes/health.py`
- [ ] Create APIRouter
- [ ] Implement `GET /health`:
  - Test database connection
  - Return HealthResponse:
    ```python
    {
      "status": "healthy",
      "database": "connected",
      "version": "0.1.0",
      "timestamp": datetime.utcnow()
    }
    ```
  - Return 503 if database unreachable
- [ ] Write test for health endpoint

---

## Phase 5: Backend - Task API (Protected Routes)

**Timeline**: Week 3
**Dependencies**: Phase 4 complete

### Task 5.1: Task Schemas
- [ ] Add to `src/schemas.py`:
- [ ] Define `TaskCreate`:
  ```python
  - title: str (min_length=1, max_length=200)
  - description: Optional[str] (max_length=1000)
  - @validator for title: strip whitespace, reject empty
  ```
- [ ] Define `TaskUpdate`:
  ```python
  - title: Optional[str] (min_length=1, max_length=200)
  - description: Optional[str] (max_length=1000)
  - @validator for title: strip, reject empty if provided
  ```
- [ ] Define `TaskResponse`:
  ```python
  - id: int
  - user_id: str
  - title: str
  - description: Optional[str]
  - completed: bool
  - created_at: datetime
  - updated_at: datetime
  - model_config = {"from_attributes": True}
  ```
- [ ] Write schema validation tests

### Task 5.2: Task Routes - Create & List
- [ ] Create `src/routes/tasks.py`
- [ ] Create APIRouter with tag="Tasks"
- [ ] Implement `POST /tasks` (protected):
  - Accept TaskCreate, session, current_user_id
  - Create Task with user_id from JWT (ignore any client input)
  - Save to database
  - Return TaskResponse (201)
  - Handle errors with rollback
- [ ] Implement `GET /tasks` (protected):
  - Accept optional query param: completed (bool)
  - Get session and current_user_id
  - Build query: select(Task).where(Task.user_id == current_user_id)
  - If completed filter provided: add .where(Task.completed == completed)
  - Execute query
  - Return List[TaskResponse]
  - Handle errors
- [ ] Write API tests:
  - Test create task with valid data
  - Test create ignores client-supplied user_id
  - Test list returns only user's tasks
  - Test filter by completed works

### Task 5.3: Task Routes - Get, Update, Delete
- [ ] Implement `GET /tasks/{task_id}` (protected):
  - Get task by ID
  - Return 404 if not found
  - Return 403 if user_id mismatch
  - Log forbidden access attempts
  - Return TaskResponse
- [ ] Implement `PUT /tasks/{task_id}` (protected):
  - Get task by ID → 404 if not exists
  - Check ownership → 403 if mismatch
  - Update title if provided in TaskUpdate
  - Update description if provided
  - Set updated_at = datetime.utcnow()
  - Commit changes
  - Return TaskResponse
- [ ] Implement `DELETE /tasks/{task_id}` (protected):
  - Get task by ID → 404 if not exists
  - Check ownership → 403 if mismatch
  - Delete task from database
  - Commit
  - Return 204 No Content
- [ ] Write API tests:
  - Test get task owned by user
  - Test get task not owned returns 403
  - Test update task owned by user
  - Test update task not owned returns 403
  - Test delete task owned by user
  - Test delete task not owned returns 403

### Task 5.4: Task Routes - Toggle Completion
- [ ] Implement `PATCH /tasks/{task_id}/complete` (protected):
  - Get task by ID → 404 if not exists
  - Check ownership → 403 if mismatch
  - Toggle completed field: task.completed = not task.completed
  - Set updated_at = datetime.utcnow()
  - Commit
  - Return TaskResponse
- [ ] Write API tests:
  - Test toggle from false to true
  - Test toggle from true to false
  - Test toggle not owned task returns 403

---

## Phase 6: Backend - FastAPI Application Setup

**Timeline**: Week 3, Day 5
**Dependencies**: Phase 5 complete

### Task 6.1: Main Application File
- [ ] Create `src/main.py`
- [ ] Create FastAPI app:
  ```python
  app = FastAPI(
      title=settings.app_name,
      description="Todo API - Phase 2 Hackathon",
      version="0.1.0",
      debug=settings.debug
  )
  ```
- [ ] Add CORS middleware:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins_list,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"]
  )
  ```
- [ ] Create `src/middleware/error_handler.py`:
  - Define `setup_error_handlers(app)` function
  - Add global exception handler for HTTPException
  - Add global exception handler for generic Exception
  - Log all errors
  - Return consistent error responses
- [ ] Call `setup_error_handlers(app)` in main.py
- [ ] Register routers:
  ```python
  app.include_router(health.router)
  app.include_router(auth.router, prefix=settings.api_v1_prefix)
  app.include_router(tasks.router, prefix=settings.api_v1_prefix)
  ```
- [ ] Add root endpoint `GET /`:
  ```python
  @app.get("/")
  async def root():
      return {
          "message": "Todo API - Backend Foundation",
          "version": "0.1.0",
          "docs": "/docs"
      }
  ```

### Task 6.2: Run & Test Backend
- [ ] Create `run.sh` script:
  ```bash
  #!/bin/bash
  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
  ```
- [ ] Make executable: `chmod +x run.sh`
- [ ] Start backend: `./run.sh`
- [ ] Test in browser: http://localhost:8000
- [ ] Test docs: http://localhost:8000/docs
- [ ] Test health: http://localhost:8000/health
- [ ] Manual API tests with curl or Postman:
  - POST /api/auth/signup
  - POST /api/auth/login
  - GET /api/auth/me (with token)
  - POST /api/tasks (with token)
  - GET /api/tasks (with token)

---

## Phase 7: Frontend - API Client & Auth

**Timeline**: Week 4
**Dependencies**: Backend complete

### Task 7.1: API Client Utility
- [ ] Create `lib/api-client.ts`
- [ ] Define base URL from environment:
  ```typescript
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  ```
- [ ] Implement `apiClient` function:
  - Accept (endpoint, method, body, requiresAuth)
  - Get token from localStorage if requiresAuth
  - Build headers with Content-Type and Authorization
  - Call fetch with full URL
  - Parse response JSON
  - Handle errors:
    - 401: Clear token, redirect to login
    - 4xx/5xx: Throw error with message
  - Return response data
- [ ] Export convenience methods:
  ```typescript
  export const api = {
    post: (endpoint, body, requiresAuth) => apiClient(...),
    get: (endpoint, requiresAuth) => apiClient(...),
    put: (endpoint, body, requiresAuth) => apiClient(...),
    patch: (endpoint, body, requiresAuth) => apiClient(...),
    delete: (endpoint, requiresAuth) => apiClient(...)
  }
  ```

### Task 7.2: Auth Pages - Signup
- [ ] Create `app/signup/page.tsx`
- [ ] Build signup form with useState:
  - Email input (type="email", required)
  - Password input (type="password", required, minLength=8)
  - Name input (optional)
  - Submit button
- [ ] Handle form submission:
  - Call `api.post('/api/auth/signup', {email, password, name})`
  - On success: Redirect to login with success message
  - On error: Display error message
  - Show loading state during API call
- [ ] Add client-side validation:
  - Email format
  - Password minimum length
- [ ] Add Tailwind styling:
  - Centered form
  - Input styling
  - Button styling
  - Error message styling
- [ ] Add link to login page

### Task 7.3: Auth Pages - Login
- [ ] Create `app/login/page.tsx`
- [ ] Build login form:
  - Email input
  - Password input
  - Submit button
- [ ] Handle form submission:
  - Call `api.post('/api/auth/login', {email, password})`
  - On success:
    - Store access_token in localStorage
    - Redirect to /tasks
  - On error: Display error message
  - Show loading state
- [ ] Add Tailwind styling
- [ ] Add link to signup page
- [ ] Test login flow end-to-end

### Task 7.4: Route Protection Middleware
- [ ] Create `middleware.ts` at root:
  ```typescript
  export function middleware(request: NextRequest) {
    const token = request.cookies.get('token')
    const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                       request.nextUrl.pathname.startsWith('/signup')
    const isProtectedPage = request.nextUrl.pathname.startsWith('/tasks')

    if (isProtectedPage && !token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }

    if (isAuthPage && token) {
      return NextResponse.redirect(new URL('/tasks', request.url))
    }
  }

  export const config = {
    matcher: ['/tasks/:path*', '/login', '/signup']
  }
  ```
- [ ] Alternative: Use client-side check in page component
- [ ] Test protected route redirect

---

## Phase 8: Frontend - Task Management UI

**Timeline**: Week 4-5
**Dependencies**: Phase 7 complete

### Task 8.1: Tasks Page - List View
- [ ] Create `app/tasks/page.tsx`
- [ ] Add useEffect to fetch tasks on mount:
  ```typescript
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await api.get('/api/tasks', true)
        setTasks(data)
      } catch (error) {
        setError(error.message)
      }
    }
    fetchTasks()
  }, [])
  ```
- [ ] Render task list:
  - Map over tasks array
  - Display each task with:
    - Title
    - Description
    - Completed checkbox
    - Edit button
    - Delete button
  - Show empty state if no tasks
- [ ] Add logout button:
  - Clear token from localStorage
  - Redirect to login
- [ ] Add Tailwind styling:
  - Container layout
  - Task cards
  - Buttons
  - Empty state

### Task 8.2: Tasks Page - Create Task
- [ ] Add "Add Task" form above task list:
  - Title input
  - Description textarea
  - Submit button
- [ ] Handle form submission:
  ```typescript
  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      const newTask = await api.post('/api/tasks', {title, description}, true)
      setTasks([...tasks, newTask])
      setTitle('')
      setDescription('')
    } catch (error) {
      setError(error.message)
    }
  }
  ```
- [ ] Clear form after successful creation
- [ ] Show success feedback
- [ ] Handle validation errors

### Task 8.3: Tasks Page - Update Task
- [ ] Add inline edit functionality:
  - Click title/description to edit
  - Show input/textarea with current value
  - Save on Enter or blur
  - Cancel on Escape
- [ ] Implement update handler:
  ```typescript
  const handleUpdate = async (taskId, updates) => {
    try {
      const updated = await api.put(`/api/tasks/${taskId}`, updates, true)
      setTasks(tasks.map(t => t.id === taskId ? updated : t))
    } catch (error) {
      setError(error.message)
    }
  }
  ```
- [ ] Add optimistic UI update
- [ ] Handle errors (revert on failure)

### Task 8.4: Tasks Page - Toggle Completion
- [ ] Add checkbox for completion status
- [ ] Implement toggle handler:
  ```typescript
  const handleToggle = async (taskId) => {
    try {
      const updated = await api.patch(`/api/tasks/${taskId}/complete`, {}, true)
      setTasks(tasks.map(t => t.id === taskId ? updated : t))
    } catch (error) {
      setError(error.message)
    }
  }
  ```
- [ ] Add visual feedback (strikethrough completed tasks)
- [ ] Add optimistic update

### Task 8.5: Tasks Page - Delete Task
- [ ] Add delete button for each task
- [ ] Add confirmation dialog:
  ```typescript
  const handleDelete = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return

    try {
      await api.delete(`/api/tasks/${taskId}`, true)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (error) {
      setError(error.message)
    }
  }
  ```
- [ ] Add optimistic update
- [ ] Show success feedback

### Task 8.6: Tasks Page - Filter by Completion
- [ ] Add filter buttons: All | Pending | Completed
- [ ] Implement filter state:
  ```typescript
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  ```
- [ ] Fetch filtered tasks:
  ```typescript
  const fetchTasks = async () => {
    const endpoint = filter === 'all'
      ? '/api/tasks'
      : `/api/tasks?completed=${filter === 'completed'}`
    const data = await api.get(endpoint, true)
    setTasks(data)
  }
  ```
- [ ] Update UI when filter changes
- [ ] Style active filter button

---

## Phase 9: Testing & Quality Assurance

**Timeline**: Week 5-6
**Dependencies**: All features implemented

### Task 9.1: Backend Unit Tests
- [ ] Write tests for auth utilities:
  - `test_password_hashing_and_verification()`
  - `test_jwt_token_creation_and_verification()`
  - `test_jwt_token_expiry()`
- [ ] Write tests for models:
  - `test_user_model_creation()`
  - `test_task_model_creation()`
  - `test_user_task_relationship()`
- [ ] Write tests for schemas:
  - `test_signup_request_validation()`
  - `test_task_create_validation()`
- [ ] Run tests: `pytest -v`
- [ ] Check coverage: `pytest --cov=src --cov-report=term-missing`
- [ ] Aim for 80%+ coverage

### Task 9.2: Backend Integration Tests
- [ ] Write API tests for auth flow:
  - `test_signup_success()`
  - `test_signup_duplicate_email()`
  - `test_login_success()`
  - `test_login_invalid_credentials()`
  - `test_get_me_authenticated()`
  - `test_get_me_unauthenticated()`
- [ ] Write API tests for task CRUD:
  - `test_create_task_authenticated()`
  - `test_create_task_unauthenticated()`
  - `test_list_tasks_user_isolation()`
  - `test_update_task_ownership()`
  - `test_delete_task_ownership()`
  - `test_toggle_completion()`
- [ ] Use pytest fixtures for test data
- [ ] Use httpx.AsyncClient for API tests

### Task 9.3: End-to-End Tests
- [ ] Manual testing checklist:
  - [ ] User signup with valid data
  - [ ] User signup with duplicate email
  - [ ] User login with valid credentials
  - [ ] User login with invalid credentials
  - [ ] Access /tasks without login (redirect to login)
  - [ ] Create task after login
  - [ ] List tasks shows only user's tasks
  - [ ] Update task title and description
  - [ ] Toggle task completion
  - [ ] Delete task with confirmation
  - [ ] Filter tasks by completion status
  - [ ] Logout clears session
- [ ] Optionally: Playwright/Cypress tests for critical flows

### Task 9.4: Security Testing
- [ ] Verify user isolation:
  - [ ] Create 2 users with different emails
  - [ ] User A creates task
  - [ ] User B cannot access User A's task (403)
- [ ] Verify JWT validation:
  - [ ] Invalid token returns 401
  - [ ] Expired token returns 401
  - [ ] Missing token returns 401
- [ ] Verify password security:
  - [ ] Password never returned in API responses
  - [ ] Password hash cannot be read via API
- [ ] SQL injection tests:
  - [ ] Try SQL in email field (should be safe via ORM)
  - [ ] Try SQL in task title (should be safe)

### Task 9.5: Performance Testing
- [ ] Load test with k6 or Locust:
  - [ ] Signup endpoint: 10 req/s for 1 min
  - [ ] Login endpoint: 20 req/s for 1 min
  - [ ] Create task: 50 req/s for 1 min
  - [ ] List tasks: 100 req/s for 1 min
- [ ] Check p95 latency < 500ms
- [ ] Check database connection pool usage
- [ ] Identify bottlenecks

---

## Phase 10: Deployment & Documentation

**Timeline**: Week 6
**Dependencies**: Testing complete

### Task 10.1: Backend Deployment (Vercel/Railway/Render)
- [ ] Choose platform (Vercel Functions, Railway, Render)
- [ ] Configure environment variables on platform
- [ ] Deploy backend
- [ ] Test deployed API endpoints
- [ ] Update CORS origins for production frontend URL

### Task 10.2: Frontend Deployment (Vercel)
- [ ] Push frontend to GitHub
- [ ] Connect to Vercel
- [ ] Configure environment variables:
  - NEXT_PUBLIC_API_URL=<backend-url>
- [ ] Deploy frontend
- [ ] Test production app

### Task 10.3: Documentation
- [ ] Update README.md:
  - [ ] Project description
  - [ ] Features list
  - [ ] Tech stack
  - [ ] Setup instructions (backend + frontend)
  - [ ] Environment variables documentation
  - [ ] API endpoints documentation
  - [ ] Testing instructions
  - [ ] Deployment instructions
- [ ] Create API documentation:
  - [ ] Use FastAPI auto-generated docs
  - [ ] Add comprehensive docstrings
  - [ ] Export OpenAPI schema
- [ ] Create CONTRIBUTING.md
- [ ] Add LICENSE file

### Task 10.4: Final Validation
- [ ] Check all acceptance criteria from spec.md
- [ ] Verify all functional requirements implemented
- [ ] Verify all security requirements met
- [ ] Run full test suite
- [ ] Performance test production deployment
- [ ] User acceptance testing
- [ ] Fix any critical bugs
- [ ] Tag release: `v1.0.0`

---

## Summary

**Total Estimated Effort**: 4-6 weeks
- Week 1: Setup, database, initial backend
- Week 2-3: Authentication, task API
- Week 4-5: Frontend UI, integration
- Week 5-6: Testing, deployment, documentation

**Critical Path**:
1. Database setup
2. Authentication system
3. Protected task API
4. Frontend integration
5. Testing
6. Deployment

**Team Composition**:
- 1 full-stack developer: 6 weeks
- 2 developers (1 backend, 1 frontend): 4 weeks with parallel work

**Risks**:
- Database connection issues (mitigation: test early)
- JWT security vulnerabilities (mitigation: follow best practices, security review)
- CORS configuration (mitigation: document clearly)
- Performance under load (mitigation: load testing, connection pooling)

**Success Metrics**:
- All 12 functional requirements implemented
- 80%+ test coverage
- < 500ms API response time
- Zero cross-user data leakage
- Production deployment successful
