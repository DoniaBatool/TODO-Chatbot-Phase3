# Feature Specification: Protected Task API

**Feature Branch**: `003-protected-task-api`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: Secure all task REST API endpoints with JWT authentication. Enforce user isolation so each user only sees and modifies their own tasks. Add JWT verification middleware to task routes, ensure user_id in URL matches token user_id, and return 401/403 for unauthorized requests.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated Task Access (Priority: P1)

As an authenticated user, I want all task endpoints to require my JWT token so that only authorized users can access the task API.

**Why this priority**: Without authentication, tasks are exposed to unauthenticated users. This is the core requirement to secure the task service after Feature 2.

**Independent Test**: Call any task endpoint without JWT → get 401; call with valid JWT → succeed; call with invalid/expired JWT → 401.

**Acceptance Scenarios**:

1. **Given** a request without Authorization header, **When** calling GET /api/{user_id}/tasks, **Then** a 401 Unauthorized is returned.
2. **Given** a request with an invalid or expired JWT, **When** calling POST /api/{user_id}/tasks, **Then** a 401 Unauthorized is returned.

---

### User Story 2 - User Isolation for Tasks (Priority: P1)

As an authenticated user, I want to only see and modify my own tasks so that my data is isolated from other users.

**Why this priority**: Data isolation is critical for multi-user security. Without it, users could view or modify others’ tasks.

**Independent Test**: Use JWT for user A to fetch user B’s tasks → 403 Forbidden; Use JWT for user A to fetch own tasks → succeed.

**Acceptance Scenarios**:

1. **Given** a valid JWT for user A and a request to GET /api/userB/tasks, **When** user_id does not match token user_id, **Then** a 403 Forbidden is returned.
2. **Given** a valid JWT for user A and a request to DELETE /api/userB/tasks/5, **Then** a 403 Forbidden is returned.
3. **Given** a valid JWT for user A and a request to GET /api/userA/tasks, **Then** a 200 OK with only user A’s tasks is returned.

---

### User Story 3 - Task Ownership Enforcement (Priority: P1)

As a backend system, I want every task CRUD operation to verify ownership so that users cannot read/update/delete tasks they do not own.

**Why this priority**: Ownership checks must be enforced on every CRUD operation to prevent horizontal privilege escalation.

**Independent Test**: Create tasks for two users, attempt cross-user access on GET/PUT/PATCH/DELETE → 403 for non-owners, 200 for owners.

**Acceptance Scenarios**:

1. **Given** user A’s JWT and task owned by user B, **When** GET /api/userA/tasks/{id} where id belongs to B, **Then** a 403 Forbidden is returned.
2. **Given** user A’s JWT, **When** PUT/PATCH/DELETE on a task owned by B, **Then** a 403 Forbidden is returned.
3. **Given** user A’s JWT, **When** any CRUD on A’s own tasks, **Then** the operation succeeds (200/201/204 as appropriate).

---

### Edge Cases

- Missing Authorization header → 401 Unauthorized
- Invalid/expired JWT token → 401 Unauthorized
- Token user_id mismatch with URL user_id → 403 Forbidden
- Task not found for given ID → 404 Not Found
- Tasks belonging to another user → 403 Forbidden
- Email/user_id casing differences (normalize to lowercase)
- Large task lists with filtering still scoped to user_id

## Requirements *(mandatory)*

### Functional Requirements

**Authentication Enforcement:**
- **FR-001**: All task endpoints MUST require JWT token via Authorization Bearer header
- **FR-002**: System MUST return 401 Unauthorized for missing or invalid JWT tokens
- **FR-003**: System MUST decode JWT and extract user_id (sub claim) for every task request

**User Isolation:**
- **FR-004**: System MUST enforce that URL path user_id matches the authenticated user_id from token
- **FR-005**: System MUST return 403 Forbidden when token user_id does not match URL user_id
- **FR-006**: System MUST scope all task queries to authenticated user_id (no cross-user access)

**Ownership Checks:**
- **FR-007**: System MUST check ownership on all task CRUD operations (GET one, PUT, PATCH, DELETE)
- **FR-008**: System MUST return 403 Forbidden when attempting to read/update/delete tasks owned by another user
- **FR-009**: System MUST return 404 Not Found when task does not exist for the authenticated user

**Endpoints Protection:**
- **FR-010**: Protect GET /api/{user_id}/tasks to return only user’s tasks
- **FR-011**: Protect POST /api/{user_id}/tasks to create tasks for authenticated user only (user_id derived from JWT)
- **FR-012**: Protect GET /api/{user_id}/tasks/{id} with ownership check
- **FR-013**: Protect PUT /api/{user_id}/tasks/{id} with ownership check
- **FR-014**: Protect DELETE /api/{user_id}/tasks/{id} with ownership check
- **FR-015**: Protect PATCH /api/{user_id}/tasks/{id}/complete with ownership check

**Security & Validation:**
- **FR-016**: System MUST normalize identifiers (user_id/email) to lowercase when comparing ownership
- **FR-017**: System MUST not trust user_id from path/body; always derive from JWT token
- **FR-018**: System MUST return consistent error messages (401 for auth issues, 403 for authorization)
- **FR-019**: System SHOULD log authentication/authorization failures
- **FR-020**: System MUST maintain existing task validation rules (title length, etc.)

### Key Entities

- **Task**: (Existing) Ownership enforced via user_id filtering and authorization checks. No schema changes required.
- **Authenticated User Context**: Derived from JWT token (user_id, email), used to scope all task operations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All task endpoints return 401 when JWT is missing or invalid
- **SC-002**: All task endpoints return 403 when JWT user_id does not match URL user_id
- **SC-003**: Users only see their own tasks in GET /api/{user_id}/tasks (0 tasks from others)
- **SC-004**: Cross-user access attempts on task CRUD return 403; same-user operations succeed (200/201/204)
- **SC-005**: Task ownership enforced for all CRUD operations (read/update/delete)
- **SC-006**: Error responses are consistent (401 for auth, 403 for authorization, 404 for missing task)
