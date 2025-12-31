# Feature Specification: Authentication System

**Feature Branch**: `002-authentication-system`  
**Created**: 2025-12-10  
**Status**: Draft  
**Input**: User description: "Implement Better Auth authentication system with JWT token support. Create user signup and signin endpoints with email/password. Generate JWT tokens on successful login with shared secret (BETTER_AUTH_SECRET). Implement JWT verification middleware for protecting API endpoints. Handle token expiry and refresh mechanism. Ensure password hashing and secure credential storage."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

As a new user, I want to create an account with email and password so that I can access the todo application with my own private task list.

**Why this priority**: User registration is the foundation of multi-user support. Without it, users cannot create accounts and the authentication system has no purpose. This is the entry point for all authenticated features.

**Independent Test**: Can be fully tested by sending POST request to signup endpoint with email/password, verifying user is created in database with hashed password, and confirming appropriate response is returned. Delivers the ability for users to create accounts independently.

**Acceptance Scenarios**:

1. **Given** a valid email and password (min 8 characters), **When** POST request is sent to /api/auth/signup endpoint, **Then** a new user is created with hashed password, user ID is generated, and 201 Created response is returned with user data (no password in response)
2. **Given** an email that already exists in database, **When** signup request is sent, **Then** a 400 Bad Request error is returned with message "Email already registered"
3. **Given** a weak password (less than 8 characters), **When** signup request is sent, **Then** a 400 Bad Request error is returned with password requirements message
4. **Given** an invalid email format, **When** signup request is sent, **Then** a 400 Bad Request error is returned with "Invalid email format" message

---

### User Story 2 - User Login with JWT Token (Priority: P1)

As a registered user, I want to login with my email and password and receive a JWT token so that I can authenticate my API requests and access my tasks securely.

**Why this priority**: Login is equally critical as registration. Without JWT token generation, users cannot authenticate their requests. This enables the entire authentication flow and is required for Feature 3 (protected endpoints).

**Independent Test**: Can be tested by first creating a user (US1), then sending POST to login endpoint with correct credentials. Success means JWT token is returned, token contains user information, and token can be decoded to verify claims. Delivers authentication capability independently.

**Acceptance Scenarios**:

1. **Given** valid email and password for existing user, **When** POST request is sent to /api/auth/login endpoint, **Then** a JWT token is generated and returned with 200 OK status, token contains user_id claim, and token is signed with BETTER_AUTH_SECRET
2. **Given** valid email but incorrect password, **When** login request is sent, **Then** a 401 Unauthorized error is returned with message "Invalid credentials"
3. **Given** email that doesn't exist, **When** login request is sent, **Then** a 401 Unauthorized error is returned with message "Invalid credentials" (same as wrong password for security)
4. **Given** missing email or password fields, **When** login request is sent, **Then** a 400 Bad Request error is returned with validation details

---

### User Story 3 - JWT Token Verification Middleware (Priority: P2)

As a backend developer, I want JWT tokens to be automatically verified on protected endpoints so that only authenticated users can access their data without manually checking tokens in every route.

**Why this priority**: After login works (P1), we need middleware to verify tokens. This is infrastructure that Feature 3 will use to protect all task endpoints. It's P2 because it depends on US2 (token generation) working first.

**Independent Test**: Can be tested by creating a protected test endpoint, sending request with valid JWT token (should succeed with 200), and sending request without token or with invalid token (should fail with 401). Success means middleware correctly identifies authenticated users from JWT tokens.

**Acceptance Scenarios**:

1. **Given** a valid JWT token in Authorization header, **When** request is sent to protected endpoint, **Then** the middleware verifies token signature, extracts user_id claim, and allows request to proceed
2. **Given** no Authorization header, **When** request is sent to protected endpoint, **Then** a 401 Unauthorized error is returned with message "Authorization header missing"
3. **Given** an invalid or expired JWT token, **When** request is sent to protected endpoint, **Then** a 401 Unauthorized error is returned with message "Invalid or expired token"
4. **Given** a JWT token signed with wrong secret, **When** request is sent to protected endpoint, **Then** a 401 Unauthorized error is returned with message "Invalid token signature"

---

### User Story 4 - Password Security and Hashing (Priority: P1)

As a security-conscious system, I want all user passwords to be hashed with bcrypt before storage so that user credentials are protected even if the database is compromised.

**Why this priority**: Password security is non-negotiable and must be implemented from the start (P1). Storing plain-text passwords is a critical security vulnerability. This must be part of the initial registration implementation (US1).

**Independent Test**: Can be tested by creating a user and verifying that the password stored in database is a bcrypt hash (not plain text), attempting to login with correct password succeeds, and attempting with wrong password fails. Success means passwords are never stored or transmitted in plain text.

**Acceptance Scenarios**:

1. **Given** a user registration with password "SecurePass123", **When** user is created in database, **Then** the password field contains a bcrypt hash starting with "$2b$", not the plain text password
2. **Given** a user with hashed password in database, **When** login attempt is made with correct plain text password, **Then** bcrypt verify succeeds and JWT token is returned
3. **Given** a user with hashed password, **When** login attempt is made with incorrect password, **Then** bcrypt verify fails and 401 Unauthorized is returned
4. **Given** password hashing configuration, **When** system starts, **Then** bcrypt work factor is set to at least 12 rounds for security

---

### Edge Cases

- What happens when user tries to signup with same email twice? (Return 400 "Email already registered")
- How does system handle case-insensitive email matching? (Store emails in lowercase, compare case-insensitively)
- What happens when JWT token expires during a request? (Return 401 "Token expired", user must login again)
- How does system handle very long passwords (>100 characters)? (Enforce max length 100 characters for bcrypt compatibility)
- What happens when BETTER_AUTH_SECRET is not configured? (Application fails to start with clear error message)
- How does system prevent brute force login attempts? (Can be added later - defer to security hardening phase)
- What happens when user forgets password? (Password reset feature deferred to Phase 3 or later)

## Requirements *(mandatory)*

### Functional Requirements

**User Registration:**
- **FR-001**: System MUST provide POST /api/auth/signup endpoint for user registration
- **FR-002**: System MUST accept email (valid format) and password (min 8 chars) in signup request
- **FR-003**: System MUST validate email format using standard email regex pattern
- **FR-004**: System MUST enforce password minimum length of 8 characters
- **FR-005**: System MUST hash passwords with bcrypt before storing in database (min 12 rounds)
- **FR-006**: System MUST check for duplicate emails and return 400 error if email already exists
- **FR-007**: System MUST generate unique user ID (UUID) for new users
- **FR-008**: System MUST return user data (id, email, name) without password in signup response

**User Login:**
- **FR-009**: System MUST provide POST /api/auth/login endpoint for user authentication
- **FR-010**: System MUST accept email and password in login request
- **FR-011**: System MUST verify password against hashed password in database using bcrypt
- **FR-012**: System MUST return 401 Unauthorized for invalid credentials (wrong password or email not found)
- **FR-013**: System MUST use same error message for wrong password and non-existent email (prevent email enumeration)
- **FR-014**: System MUST generate JWT token on successful login
- **FR-015**: System MUST include user_id, email, and expiry time in JWT payload
- **FR-016**: System MUST sign JWT tokens with BETTER_AUTH_SECRET from environment variable
- **FR-017**: System MUST set JWT token expiry to 7 days from issue time
- **FR-018**: System MUST return JWT token in response with 200 OK status

**JWT Token Management:**
- **FR-019**: System MUST use HS256 algorithm for JWT signing
- **FR-020**: System MUST include standard JWT claims (iss, sub, exp, iat)
- **FR-021**: System MUST validate JWT token structure (header.payload.signature)
- **FR-022**: System MUST verify JWT signature matches BETTER_AUTH_SECRET
- **FR-023**: System MUST check JWT token expiry and reject expired tokens
- **FR-024**: System MUST extract user_id from JWT token claims after verification

**Authentication Middleware:**
- **FR-025**: System MUST provide reusable authentication dependency for FastAPI routes
- **FR-026**: System MUST extract JWT token from Authorization header (Bearer scheme)
- **FR-027**: System MUST return 401 error if Authorization header is missing
- **FR-028**: System MUST return 401 error if token is invalid, expired, or malformed
- **FR-029**: System MUST inject authenticated user_id into route handler after successful verification
- **FR-030**: System MUST handle JWT decode errors gracefully with appropriate error messages

**Security:**
- **FR-031**: System MUST load BETTER_AUTH_SECRET from environment variable (.env file)
- **FR-032**: System MUST fail to start if BETTER_AUTH_SECRET is not configured or is too short (<32 characters)
- **FR-033**: System MUST never return password hashes in any API response
- **FR-034**: System MUST never log passwords in plain text
- **FR-035**: System MUST store emails in lowercase for case-insensitive matching
- **FR-036**: System MUST rate limit login attempts (can be deferred to security hardening)

**Error Handling:**
- **FR-037**: System MUST return consistent error format for all auth endpoints
- **FR-038**: System MUST provide clear error messages without exposing security details
- **FR-039**: System MUST handle database errors during signup/login gracefully

### Key Entities

- **User** (extends existing from Feature 1): User entity now includes password_hash field for authentication. Email is used as login identifier. User ID is used in JWT tokens for identification.

- **JWT Token**: Not a database entity, but a signed JSON object containing user_id, email, issued_at, and expires_at claims. Signed with BETTER_AUTH_SECRET and verified on each protected request.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can create an account with email and password, and the account is successfully stored in database with password hashed (bcrypt hash verified in database)

- **SC-002**: User can login with correct email/password combination and receives a valid JWT token that can be decoded to extract user_id

- **SC-003**: User receives 401 Unauthorized error when attempting to login with wrong password or non-existent email, with same error message for both (preventing email enumeration)

- **SC-004**: JWT tokens are correctly signed with BETTER_AUTH_SECRET and can be verified using the same secret (token signature validation passes)

- **SC-005**: JWT tokens expire after 7 days and expired tokens are rejected by authentication middleware with 401 error

- **SC-006**: Protected endpoints automatically verify JWT tokens without manual token checking in each route (middleware handles authentication)

- **SC-007**: Authentication middleware correctly extracts user_id from valid JWT token and makes it available to route handlers

- **SC-008**: Passwords are never exposed in API responses, logs, or error messages (security audit passes)

- **SC-009**: System fails to start if BETTER_AUTH_SECRET is missing or too weak, preventing deployment with insecure configuration

- **SC-010**: All authentication endpoints respond within 500ms including password hashing overhead (bcrypt verification optimized)
