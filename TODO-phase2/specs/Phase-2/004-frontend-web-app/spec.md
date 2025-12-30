# Feature Specification: Frontend Web App

**Feature Branch**: `004-frontend-web-app`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: Create Next.js 16+ web application with App Router, TypeScript, Tailwind CSS, and Better Auth integration. Implement signup/signin UI, task management UI (CRUD), attach JWT tokens to API calls, handle loading/error states, and ensure responsive design.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authentication UI (Priority: P1)
As a user, I want to signup/signin via a clean UI so that I can get authenticated and receive a JWT for API access.

**Why this priority**: Without auth UI, users cannot access their tasks. Core entry point.

**Independent Test**: Fill signup form → success message, user created; login form → success, token stored; invalid credentials → error shown.

**Acceptance Scenarios**:
1. **Given** valid email/password, **When** signup form is submitted, **Then** user sees success and is prompted to login or auto-logged-in.
2. **Given** valid credentials, **When** login form is submitted, **Then** JWT is stored (localStorage/cookie) and user is redirected to tasks.
3. **Given** wrong credentials, **When** login form is submitted, **Then** an inline error is shown (no redirect).

---

### User Story 2 - Task Management UI (Priority: P1)
As an authenticated user, I want to view, create, update, complete, and delete my tasks in a responsive UI so that I can manage my todos.

**Why this priority**: Core product value—managing tasks across devices.

**Independent Test**: After login, tasks page lists only my tasks; create/update/delete/complete actions work and reflect immediately.

**Acceptance Scenarios**:
1. **Given** a valid token, **When** opening Tasks page, **Then** only the user’s tasks are shown with loading state then data.
2. **Given** the create form filled, **When** submitted, **Then** task appears in the list without page reload.
3. **Given** a task row, **When** clicking complete/delete/edit, **Then** action succeeds and UI updates.

---

### User Story 3 - API Integration & Token Handling (Priority: P1)
As an authenticated user, I want all API calls to automatically include my JWT token so that my requests are authorized without manual steps.

**Why this priority**: Security/usability; avoids broken flows and ensures isolation.

**Independent Test**: Network calls from frontend include Authorization: Bearer <token>; missing/expired token triggers logout + redirect to login.

**Acceptance Scenarios**:
1. **Given** a valid stored token, **When** fetching tasks, **Then** Authorization header is set and API returns 200 with data.
2. **Given** an expired/invalid token, **When** any API call is made, **Then** user is logged out and redirected to login with a message.
3. **Given** no token present, **When** accessing protected pages, **Then** user is redirected to login.

---

### User Story 4 - UX/State (Priority: P2)
As a user, I want clear loading/error/empty states so that I understand what’s happening while interacting with tasks.

**Why this priority**: Usability and trust; reduces confusion.

**Independent Test**: Simulate slow network or failures; UI shows spinner, error toast, and retry; empty list shows an empty state.

**Acceptance Scenarios**:
1. **Given** slow API, **When** loading tasks, **Then** a spinner/skeleton is shown until data arrives.
2. **Given** API error, **When** fetching tasks, **Then** an error message/toast is shown with retry option.
3. **Given** no tasks, **When** viewing tasks, **Then** an empty state message is shown.

---

### Edge Cases
- Invalid/expired token from frontend → auto logout + redirect to login
- API 401/403 responses → clear user session and redirect
- Network failure → show retry option
- Duplicate form submissions → disable button while loading
- Large task lists → pagination or lazy loading (deferred if not needed)
- Form validation on client side (email format, min password length)

## Requirements *(mandatory)*

### Functional Requirements

**Authentication UI:**
- **FR-001**: Provide signup and signin forms (email/password)
- **FR-002**: Validate email format and password min length client-side
- **FR-003**: On successful login, store JWT token (localStorage or cookie)
- **FR-004**: On logout or token failure, clear token and redirect to login

**API Client & Token Handling:**
- **FR-005**: Centralized API client attaches Authorization: Bearer <token> to all protected requests
- **FR-006**: Handle 401/403 responses by clearing session and redirecting to login
- **FR-007**: Configurable API base URL via env (NEXT_PUBLIC_API_URL)

**Tasks UI:**
- **FR-008**: List tasks for authenticated user (GET /api/tasks)
- **FR-009**: Create task (POST /api/tasks)
- **FR-010**: Update task (PUT /api/tasks/{id})
- **FR-011**: Complete/uncomplete task (PATCH /api/tasks/{id}/complete)
- **FR-012**: Delete task (DELETE /api/tasks/{id})
- **FR-013**: Client-side validation: title 1-200 chars, description optional ≤1000 chars

**UX/State:**
- **FR-014**: Show loading states for data fetches and form submissions
- **FR-015**: Show error messages/toasts on API failures
- **FR-016**: Show empty state when no tasks exist
- **FR-017**: Responsive design (mobile and desktop)
- **FR-018**: Disable submit buttons while requests in-flight to prevent duplicates

**Styling & Structure:**
- **FR-019**: Use Tailwind CSS for styling
- **FR-020**: Use App Router (Next.js 16+) and TypeScript
- **FR-021**: Organize code: `/app` for pages, `/components` for UI, `/lib/api.ts` for API client

### Key Entities

- **Task (frontend model)**: id, title, description, completed, created_at, updated_at
- **Auth Session**: JWT token and user info stored client-side

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Users can signup/signin and reach tasks page within 3 seconds of form submit (normal network)
- **SC-002**: All task API calls include Authorization header when user is logged in
- **SC-003**: 401/403 responses trigger logout + redirect consistently
- **SC-004**: Task list renders only the user’s tasks (matches backend isolation)
- **SC-005**: UI shows appropriate loading/error/empty states for tasks fetches
- **SC-006**: Forms enforce client-side validation (email format, password length, title length)
