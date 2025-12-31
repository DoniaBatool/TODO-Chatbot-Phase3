# Feature Specification: Full-Stack Todo Application (Phase 2)

**Version**: 1.0 (Reverse Engineered)
**Date**: 2025-12-30
**Source**: phase2-reference/ codebase
**Status**: Reverse Engineered from Implementation

## Problem Statement

Users need a modern, web-based todo application that allows them to manage their tasks from any device with secure, multi-user support. The console application from Phase 1 is limited to single-user, local-only access. Phase 2 addresses this by providing a full-stack web application with user authentication, secure task management, and a responsive web interface.

## System Intent

**Target Users**: Individuals who want to manage their todo lists online with secure access

**Core Value Proposition**:
- Access tasks from anywhere via web browser
- Secure multi-user support with user isolation
- Modern, intuitive web interface
- Reliable data persistence in cloud database

**Key Capabilities**:
- User registration and authentication
- Secure, isolated task management per user
- Full CRUD operations on tasks (Create, Read, Update, Delete)
- Task completion tracking
- Filter tasks by completion status
- Responsive web UI with form validation

## Functional Requirements

### Requirement 1: User Registration
- **What**: Users can create accounts with email and password
- **Why**: Enable multi-user support with secure authentication
- **Inputs**:
  - Email address (valid email format)
  - Password (minimum 8 characters)
  - Name (optional)
- **Outputs**:
  - User account created with unique UUID
  - Success confirmation
- **Side Effects**:
  - User record created in database
  - Password hashed with bcrypt before storage
  - Email normalized to lowercase
- **Success Criteria**:
  - User can register with unique email
  - Duplicate email returns error
  - Password never stored in plain text
  - User receives confirmation

### Requirement 2: User Login
- **What**: Registered users can log in with email/password credentials
- **Why**: Authenticate users before granting access to their tasks
- **Inputs**:
  - Email address
  - Password (plain text from user)
- **Outputs**:
  - JWT access token (7-day expiry)
  - Token type: Bearer
  - Expiry duration in seconds
  - User profile data
- **Side Effects**:
  - JWT token generated with user_id and email claims
  - Login event logged
- **Success Criteria**:
  - Valid credentials return access token
  - Invalid credentials return 401 error
  - Token can be used for subsequent authenticated requests
  - Token expires after 7 days

### Requirement 3: User Profile Access
- **What**: Authenticated users can retrieve their profile information
- **Why**: Verify authentication status and display user information
- **Inputs**:
  - Valid JWT token in Authorization header
- **Outputs**:
  - User ID, email, name, creation timestamp
- **Side Effects**: None
- **Success Criteria**:
  - Authenticated request returns user data
  - Unauthenticated request returns 401
  - Password hash never returned in response

### Requirement 4: Create Task
- **What**: Authenticated users can create new tasks with title and optional description
- **Why**: Enable users to add items to their todo list
- **Inputs**:
  - Task title (1-200 characters, required)
  - Task description (0-1000 characters, optional)
  - JWT token for authentication
- **Outputs**:
  - Created task with auto-generated ID
  - User ID (from JWT)
  - Completion status (false by default)
  - Created and updated timestamps
- **Side Effects**:
  - Task record created in database
  - Task automatically linked to authenticated user
  - Client-supplied user_id ignored (security measure)
- **Success Criteria**:
  - Task created with correct user_id from token
  - Title validation enforced (no empty/whitespace-only)
  - Description length enforced
  - Returns 201 Created with full task object

### Requirement 5: List Tasks
- **What**: Authenticated users can retrieve all their tasks with optional filtering
- **Why**: View todo list and track progress
- **Inputs**:
  - JWT token for authentication
  - Optional filter: completed (true/false/null for all)
- **Outputs**:
  - Array of tasks belonging to authenticated user
  - Tasks include: id, title, description, completed, timestamps
- **Side Effects**: None (read-only)
- **Success Criteria**:
  - Returns only tasks for authenticated user (user isolation)
  - Filter by completion status works correctly
  - Empty array returned if no tasks
  - No cross-user data leakage

### Requirement 6: Get Single Task
- **What**: Authenticated users can retrieve a specific task by ID
- **Why**: View full details of a single task
- **Inputs**:
  - Task ID (integer)
  - JWT token for authentication
- **Outputs**:
  - Single task object with all fields
- **Side Effects**: None
- **Success Criteria**:
  - Returns task if owned by authenticated user
  - Returns 404 if task doesn't exist
  - Returns 403 if task owned by different user
  - Ownership logged for security audit

### Requirement 7: Update Task
- **What**: Authenticated users can modify task title and/or description
- **Why**: Correct mistakes or update task details
- **Inputs**:
  - Task ID
  - Updated title (optional, 1-200 chars)
  - Updated description (optional, 0-1000 chars)
  - JWT token
- **Outputs**:
  - Updated task object
  - Updated timestamp reflects modification time
- **Side Effects**:
  - Task record updated in database
  - updated_at timestamp changed to current time
- **Success Criteria**:
  - Only task owner can update
  - 403 for non-owners
  - 404 if task doesn't exist
  - Partial updates supported (can update title without description)
  - Validation enforced on updated fields

### Requirement 8: Toggle Task Completion
- **What**: Authenticated users can mark tasks as complete or incomplete
- **Why**: Track task completion status
- **Inputs**:
  - Task ID
  - JWT token
- **Outputs**:
  - Task with toggled completed status
  - Updated timestamp
- **Side Effects**:
  - Task completed field toggled (true ↔ false)
  - updated_at timestamp changed
- **Success Criteria**:
  - Completion status toggled correctly
  - Only task owner can toggle
  - Returns updated task object
  - idempotent operation (can toggle multiple times)

### Requirement 9: Delete Task
- **What**: Authenticated users can permanently delete tasks
- **Why**: Remove completed or unwanted tasks
- **Inputs**:
  - Task ID
  - JWT token
- **Outputs**:
  - 204 No Content on success
- **Side Effects**:
  - Task permanently removed from database
  - Cascade deletion if relationships exist
- **Success Criteria**:
  - Task deleted only if owned by user
  - 403 for non-owners
  - 404 if task doesn't exist
  - Returns 204 with empty body
  - Operation logged for audit

### Requirement 10: Web UI - Authentication Pages
- **What**: Web interface for user signup and login
- **Why**: Provide user-friendly access to authentication
- **Inputs**:
  - Form inputs for email, password, name
- **Outputs**:
  - Visual feedback on success/error
  - Redirect to tasks page on success
- **Side Effects**:
  - JWT token stored in browser (cookie or localStorage)
  - User redirected to protected routes
- **Success Criteria**:
  - Forms validate input client-side
  - Server errors displayed clearly
  - Success redirects to tasks page
  - Loading states shown during API calls

### Requirement 11: Web UI - Task Management
- **What**: Web interface for CRUD operations on tasks
- **Why**: Provide intuitive task management experience
- **Inputs**:
  - Task forms (title, description)
  - Click interactions for complete/delete
- **Outputs**:
  - Real-time UI updates on task changes
  - Visual feedback for operations
- **Side Effects**:
  - API calls to backend
  - UI state updated with responses
  - Optimistic updates for better UX
- **Success Criteria**:
  - All task operations accessible via UI
  - Inline editing for task updates
  - Completion toggle works instantly
  - Delete requires confirmation
  - Empty state shown when no tasks

### Requirement 12: Web UI - Route Protection
- **What**: Protected routes require authentication
- **Why**: Prevent unauthorized access to user tasks
- **Inputs**:
  - Current authentication status (JWT presence)
- **Outputs**:
  - Redirect to login if unauthenticated
  - Access granted if authenticated
- **Side Effects**:
  - Navigation intercepted on unauthenticated access
  - User redirected to login page
- **Success Criteria**:
  - /tasks route requires auth
  - Redirect preserves intended destination
  - Login success redirects to original destination

## Non-Functional Requirements

### Performance
**Observed Patterns**:
- Database connection pooling implemented (pool_size=10, max_overflow=20)
- Connection recycling after 1 hour prevents stale connections
- Pre-ping health check before using connections
- Async handlers for non-blocking I/O

**Target**:
- API response time < 500ms for CRUD operations (observed)
- Support 50+ concurrent users (connection pool capacity)
- Frontend page load < 2s

### Security
**Observed Patterns**:
- JWT token-based authentication
- bcrypt password hashing (cost factor: default)
- User isolation enforced on all task operations
- Input validation with Pydantic schemas
- CORS configured for frontend origin
- Email normalization (lowercase) for case-insensitive matching

**Standards**:
- JWT tokens signed with HS256 algorithm
- 7-day token expiry enforced
- Authorization header required on protected endpoints
- 401 for authentication failures
- 403 for authorization failures
- SQL injection prevented via SQLModel ORM
- Password never returned in API responses

### Reliability
**Observed Patterns**:
- Database transaction management (commit/rollback)
- Global error handlers in FastAPI
- Logging for authentication/authorization events
- Connection pool timeout (30s) prevents hanging requests

**SLA**:
- Database transactions ensure data consistency
- Graceful error handling (no uncaught exceptions)
- Structured logging for debugging

### Scalability
**Observed Patterns**:
- Stateless API design (JWT eliminates session storage)
- PostgreSQL as persistent data store
- Connection pooling for efficient DB access
- RESTful API enables horizontal scaling

**Load Capacity**:
- Connection pool supports 30 concurrent connections (10 + 20 overflow)
- Stateless design allows multiple backend instances

### Observability
**Observed Patterns**:
- Python logging module with structured messages
- Health check endpoint (/health)
- User ID and action logged for security events
- Error logging with exception details

**Monitoring**:
- Health endpoint monitors: database connection, API version
- Authentication failures logged with user email
- Ownership violations logged with user IDs

## System Constraints

### External Dependencies
- **Database**: Neon PostgreSQL (Serverless Postgres)
- **Authentication**: PyJWT for token handling
- **Password Hashing**: passlib with bcrypt
- **Email Validation**: email-validator library
- **Frontend Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS

### Data Formats
- **API Requests/Responses**: JSON
- **Timestamps**: ISO 8601 format (UTC)
- **Email**: Lowercase, validated format
- **User IDs**: UUID v4 format
- **Task IDs**: Auto-incrementing integers

### Deployment Context
- **Backend**: Python 3.13, FastAPI, Uvicorn
- **Frontend**: Next.js, React 18, TypeScript
- **Database**: Neon Serverless PostgreSQL
- **Environment**: Serverless-compatible architecture

### Compliance Requirements
- **Data Isolation**: User can only access own tasks (GDPR-aligned)
- **Password Security**: bcrypt hashing, never stored plain text
- **Audit Trail**: Authentication events logged

## Non-Goals & Out of Scope

**Explicitly excluded** (inferred from missing implementation):
- Multi-factor authentication (MFA)
- OAuth/social login providers
- Password reset/recovery functionality
- Email verification on signup
- Task sharing between users
- Task priorities or tags
- Due dates and reminders
- Task categories or projects
- Recurring tasks
- Task search functionality
- Bulk operations (select multiple tasks)
- Export tasks (CSV, JSON)
- Real-time collaboration
- Mobile applications (iOS/Android)
- Offline mode
- Task history/audit log visible to users
- User profile editing
- Account deletion
- Session management (logout invalidates token)

## Known Gaps & Technical Debt

### Gap 1: Token Refresh Mechanism
- **Issue**: No refresh token implementation
- **Evidence**: Only access tokens generated (phase2-reference/backend/src/auth/jwt.py:12-47)
- **Impact**: Users must re-login after 7 days
- **Recommendation**: Implement refresh token rotation with longer expiry

### Gap 2: Password Strength Validation
- **Issue**: Only length validation (8+ characters), no complexity requirements
- **Evidence**: SignupRequest schema (phase2-reference/backend/src/schemas.py:89-92)
- **Impact**: Weak passwords allowed
- **Recommendation**: Require uppercase, number, special character

### Gap 3: Rate Limiting
- **Issue**: No rate limiting on authentication endpoints
- **Evidence**: No rate limiting middleware in codebase
- **Impact**: Vulnerable to brute force attacks
- **Recommendation**: Add rate limiting (e.g., 5 attempts per minute)

### Gap 4: Email Verification
- **Issue**: No email verification on signup
- **Evidence**: User created without verification (phase2-reference/backend/src/routes/auth.py:51-69)
- **Impact**: Users can register with invalid/unowned emails
- **Recommendation**: Send verification email with confirmation link

### Gap 5: Password Reset
- **Issue**: No password reset functionality
- **Evidence**: No reset endpoints in codebase
- **Impact**: Users locked out if password forgotten
- **Recommendation**: Implement email-based password reset flow

### Gap 6: Logout Functionality
- **Issue**: No server-side token invalidation
- **Evidence**: JWT stateless, no blacklist implementation
- **Impact**: Tokens valid until expiry even after logout
- **Recommendation**: Implement token blacklist in Redis

### Gap 7: API Documentation
- **Issue**: No OpenAPI/Swagger documentation generated
- **Evidence**: FastAPI docs enabled but not comprehensive
- **Impact**: Frontend developers must read code for API contracts
- **Recommendation**: Add comprehensive docstrings for auto-generation

### Gap 8: Pagination
- **Issue**: Task list returns all tasks (no pagination)
- **Evidence**: GET /tasks returns all without limit (phase2-reference/backend/src/routes/tasks.py:61-94)
- **Impact**: Performance degrades with many tasks
- **Recommendation**: Add pagination (limit/offset or cursor-based)

### Gap 9: Frontend Error Handling
- **Issue**: Limited error boundary implementation
- **Evidence**: Basic error handling in API client
- **Impact**: Uncaught errors may crash UI
- **Recommendation**: Add React Error Boundaries

### Gap 10: Metrics and Monitoring
- **Issue**: No metrics collection (Prometheus, StatsD)
- **Evidence**: Only basic logging present
- **Impact**: Blind to production performance issues
- **Recommendation**: Add metrics instrumentation

## Success Criteria

### Functional Success
- [x] Users can register with email/password
- [x] Users can log in and receive JWT token
- [x] Authenticated users can create tasks
- [x] Authenticated users can view their tasks
- [x] Authenticated users can update tasks
- [x] Authenticated users can mark tasks complete/incomplete
- [x] Authenticated users can delete tasks
- [x] User isolation enforced (no cross-user access)
- [x] Web UI provides all authentication and task management features
- [x] Route protection prevents unauthorized access

### Non-Functional Success
- [x] API response time < 500ms for CRUD operations
- [x] Passwords hashed with bcrypt
- [x] JWT authentication enforced on protected routes
- [x] Database transactions ensure consistency
- [x] Connection pooling for performance
- [x] CORS configured for frontend access
- [x] Health check endpoint available
- [x] Error handling prevents crashes

### Security Success
- [x] Zero cross-user data leakage (user isolation enforced)
- [x] Passwords never stored in plain text
- [x] JWT tokens required for task access
- [x] Ownership validated on all task operations
- [x] 401 returned for authentication failures
- [x] 403 returned for authorization failures
- [x] SQL injection prevented via ORM
- [x] Input validation on all endpoints

## Acceptance Tests

### Test 1: User Registration
**Given**: A new user with unique email
**When**: POST /api/auth/signup with email, password, name
**Then**:
- 201 Created returned
- User object with id, email, name, created_at
- Password hash not in response
- User can immediately login

### Test 2: User Login
**Given**: Registered user with valid credentials
**When**: POST /api/auth/login with email, password
**Then**:
- 200 OK returned
- Response contains access_token, token_type=bearer, expires_in, user object
- Token can be decoded to extract user_id

### Test 3: Create Task
**Given**: Authenticated user with valid JWT
**When**: POST /api/tasks with title, description
**Then**:
- 201 Created returned
- Task created with user_id from JWT (not from request body)
- completed=false by default
- Timestamps populated

### Test 4: User Isolation
**Given**: Two users (A and B) with tasks
**When**: User A requests User B's tasks
**Then**:
- User A sees only their own tasks
- GET /api/tasks with A's token returns only A's tasks
- Attempt to access B's task by ID returns 403

### Test 5: Task Ownership Enforcement
**Given**: User A owns task 1, User B owns task 2
**When**: User A attempts to update task 2
**Then**:
- 403 Forbidden returned
- Task 2 unchanged
- Security event logged

### Test 6: Token Expiry
**Given**: JWT token older than 7 days
**When**: Request with expired token
**Then**:
- 401 Unauthorized returned
- Error message indicates token expired

### Test 7: Web UI Authentication Flow
**Given**: Unauthenticated user
**When**: Navigate to /tasks
**Then**:
- Redirected to /login
- After successful login, redirected to /tasks
- Tasks page shows user's tasks

### Test 8: Task CRUD via Web UI
**Given**: Authenticated user on tasks page
**When**: Create, update, complete, delete tasks via UI
**Then**:
- All operations reflected in UI immediately
- Backend state matches UI state
- Error messages shown for validation failures

---

**Regeneration Viability**: This specification is complete enough to rebuild Phase 2 from scratch. All functional requirements, security constraints, and success criteria are documented. The spec follows the "what" and "why" without prescribing "how", enabling alternative implementations while preserving intent.

**Next Steps**:
1. Use this spec as input for `plan.md` (architecture design)
2. Generate `tasks.md` (implementation breakdown)
3. Extract `intelligence-object.md` (reusable patterns)
