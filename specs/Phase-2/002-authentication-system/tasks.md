---
description: "Implementation tasks for Authentication System feature"
---

# Tasks: Authentication System

**Input**: Design documents from `/specs/002-authentication-system/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests are NOT explicitly requested, manual testing via quickstart.md

**Organization**: Tasks grouped by user story for independent implementation

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story label (US1, US2, US3, US4)
- Exact file paths included

---

## Phase 1: Setup (Authentication Infrastructure)

**Purpose**: Install dependencies and configure authentication framework

- [X] T001 Add authentication dependencies to backend/pyproject.toml (pyjwt, passlib[bcrypt], email-validator, python-multipart)
- [X] T002 Install new dependencies with UV (uv pip install pyjwt passlib[bcrypt] email-validator python-multipart)
- [X] T003 [P] Update backend/.env.example with BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRY_DAYS
- [X] T004 [P] Update backend/src/config.py to add better_auth_secret, jwt_algorithm, jwt_expiry_days fields
- [X] T005 Add secret validation to config.py (min 32 chars, fail startup if missing)
- [X] T006 [P] Create backend/src/auth/__init__.py module

**Checkpoint**: ✅ Dependencies installed, configuration ready

---

## Phase 2: Foundational (Core Auth Utilities)

**Purpose**: Build password hashing and JWT token utilities

- [X] T007 [P] Create backend/src/auth/password.py with passlib CryptContext setup
- [X] T008 [P] Implement hash_password() function in password.py (bcrypt with 12 rounds)
- [X] T009 [P] Implement verify_password() function in password.py
- [X] T010 [P] Create backend/src/auth/jwt.py for JWT token management
- [X] T011 [P] Implement create_jwt_token() function in jwt.py (HS256, 7-day expiry, standard claims)
- [X] T012 [P] Implement verify_jwt_token() function in jwt.py (decode, verify signature, check expiry)
- [X] T013 [P] Add JWT exception handling (ExpiredSignatureError, InvalidTokenError)

**Checkpoint**: ✅ Password hashing and JWT utilities ready

---

## Phase 3: Database Migration (User Model Update)

**Purpose**: Add password_hash field to User model

- [X] T014 Update backend/src/models.py to add password_hash field to User model (Optional[str], max_length=255)
- [X] T015 Generate Alembic migration for password_hash field (alembic revision --autogenerate -m "Add password_hash to users")
- [X] T016 Review generated migration file and fix any type issues (replace sqlmodel types with sa.String)
- [X] T017 Apply migration to database (alembic upgrade head)
- [X] T018 Verify password_hash column exists in users table

**Checkpoint**: ✅ User model extended, database schema updated

---

## Phase 4: User Story 4 - Password Security (Priority: P1)

**Goal**: Ensure all passwords are hashed with bcrypt before storage

**Independent Test**: Create user and verify password is bcrypt hash ($2b$12$...), login with correct password succeeds, login with wrong password fails

### Implementation for User Story 4 (P1 - Security)

- [X] T019 [P] [US4] Add password validation to SignupRequest schema in backend/src/schemas.py (min 8 chars, max 100 chars)
- [X] T020 [P] [US4] Test password hashing utilities (verify hash format, verify password matching)
- [X] T021 [US4] Implement password trimming before hashing (remove leading/trailing spaces)
- [X] T022 [US4] Add password complexity helper function (for future enhancements)

**Manual Testing**:
- Hash password: Import hash_password and verify output starts with $2b$12$
- Verify password: Test correct and incorrect passwords
- Check length: 60 characters

**Checkpoint**: ✅ Password security implemented and tested

---

## Phase 5: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts with email/password

**Independent Test**: POST to /api/auth/signup with valid email/password, verify user created in database with hashed password, verify 201 response with user data (no password)

### Implementation for User Story 1 (P1 - Registration)

- [X] T023 [P] [US1] Create backend/src/schemas.py auth schemas (SignupRequest, UserResponse)
- [X] T024 [P] [US1] Add EmailStr validation to signup request
- [X] T025 [P] [US1] Create backend/src/routes/auth.py with APIRouter
- [X] T026 [US1] Implement POST /api/auth/signup endpoint in routes/auth.py
- [X] T027 [US1] Add UUID generation for new users (import uuid)
- [X] T028 [US1] Add duplicate email check before creating user
- [X] T029 [US1] Hash password before storing in database
- [X] T030 [US1] Store email in lowercase for case-insensitive matching
- [X] T031 [US1] Return user data without password_hash in response
- [X] T032 [US1] Add error handling for duplicate email (400 "Email already registered")
- [X] T033 [US1] Add error handling for invalid email format (400 with validation details)
- [X] T034 [US1] Register auth routes in backend/src/main.py under /api/auth prefix

**Manual Testing** (per quickstart.md):
- Signup: `curl -X POST http://localhost:8000/api/auth/signup -d '{"email":"test@test.com","password":"Test123456"}'`
- Verify: Check database for user with hashed password
- Test duplicate: Try same email again (should get 400)

**Checkpoint**: ✅ User registration working

---

## Phase 6: User Story 2 - User Login with JWT (Priority: P1) 🎯 MVP

**Goal**: Enable users to login and receive JWT tokens

**Independent Test**: POST to /api/auth/login with correct credentials, receive JWT token, decode token to verify user_id claim

### Implementation for User Story 2 (P1 - Login)

- [X] T035 [P] [US2] Create LoginRequest and LoginResponse schemas in backend/src/schemas.py
- [X] T036 [P] [US2] Implement POST /api/auth/login endpoint in backend/src/routes/auth.py
- [X] T037 [US2] Add user lookup by email (case-insensitive) in login endpoint
- [X] T038 [US2] Verify password using bcrypt in login endpoint
- [X] T039 [US2] Generate JWT token on successful password verification
- [X] T040 [US2] Include user_id (sub), email, exp, iat, iss claims in JWT payload
- [X] T041 [US2] Return token with user data in LoginResponse
- [X] T042 [US2] Add error handling for invalid credentials (401, same message for wrong password/email)
- [X] T043 [US2] Add error handling for missing password_hash (user without password can't login)

**Manual Testing** (per quickstart.md):
- Login: `curl -X POST http://localhost:8000/api/auth/login -d '{"email":"test@test.com","password":"Test123456"}'`
- Save token from response
- Decode token to verify claims
- Test wrong password (should get 401)

**Checkpoint**: ✅ Login working, JWT tokens generated

---

## Phase 7: User Story 3 - JWT Verification Middleware (Priority: P2)

**Goal**: Automatic JWT token verification for protected endpoints

**Independent Test**: Create protected test endpoint, access with valid token (200), access without token (401), access with invalid token (401)

### Implementation for User Story 3 (P2 - Middleware)

- [X] T044 [P] [US3] Create backend/src/auth/dependencies.py for FastAPI dependencies
- [X] T045 [US3] Implement get_current_user() dependency function in dependencies.py
- [X] T046 [US3] Add HTTPBearer security scheme for token extraction
- [X] T047 [US3] Extract token from Authorization header (Bearer scheme)
- [X] T048 [US3] Verify JWT token using verify_jwt_token() from jwt.py
- [X] T049 [US3] Extract user_id from token payload (sub claim)
- [X] T050 [US3] Handle missing Authorization header (401 "Authorization header missing")
- [X] T051 [US3] Handle invalid/expired tokens (401 "Invalid or expired token")
- [X] T052 [US3] Handle token decode errors gracefully
- [X] T053 [P] [US3] Implement GET /api/auth/me endpoint (get current authenticated user)
- [X] T054 [US3] Use get_current_user dependency in /api/auth/me endpoint
- [X] T055 [US3] Return current user data based on user_id from JWT

**Manual Testing** (per quickstart.md):
- Login to get token
- Test protected endpoint: `curl http://localhost:8000/api/auth/me -H "Authorization: Bearer <token>"`
- Test without token (should get 401)
- Test with fake token (should get 401)

**Checkpoint**: ✅ JWT middleware working, protected endpoints secure

---

## Phase 8: Polish & Integration

**Purpose**: Final improvements and documentation

- [X] T056 [P] Add comprehensive docstrings to all auth functions
- [X] T057 [P] Add type hints to all auth module functions
- [X] T058 [P] Add logging for authentication events (signup, login success/failure)
- [X] T059 [P] Update backend/README.md with authentication setup instructions
- [X] T060 [P] Create example .env with strong BETTER_AUTH_SECRET
- [X] T061 Validate auth endpoints against OpenAPI spec (contracts/auth-endpoints.yaml)
- [X] T062 Test all error scenarios from quickstart.md (10 scenarios)
- [X] T063 Verify bcrypt work factor is 12 rounds
- [X] T064 Verify JWT token expiry is 7 days
- [X] T065 Test authentication flow end-to-end (signup → login → protected endpoint)

**Checkpoint**: ✅ Authentication system complete and validated

---

## Dependencies & Execution Flow

### Critical Path

1. **Phase 1** (Setup) → Must complete before Phase 2
2. **Phase 2** (Foundational) → Must complete before Phase 3
3. **Phase 3** (Migration) → Must complete before Phase 4
4. **Phase 4** (US4 - Password Security) → Foundation for US1, US2
5. **Phase 5** (US1 - Registration) → Can test independently
6. **Phase 6** (US2 - Login) → Depends on US1 (need users to login)
7. **Phase 7** (US3 - Middleware) → Depends on US2 (need tokens to verify)

### Independent Phases

After Phase 4 completes:
- **Phase 5** (US1) and **Phase 6** (US2) can be developed in parallel
- **Phase 7** (US3) requires Phase 6 complete (need JWT tokens)
- **Phase 8** (Polish) can start when Phase 7 completes

### Parallel Execution Opportunities

**Within Phase 1**: T003 [P], T004 [P], T006 [P] - 3 tasks  
**Within Phase 2**: T007-T013 [P] - 7 tasks (all auth utilities)  
**Within Phase 4**: T019 [P], T020 [P] - 2 tasks  
**Within Phase 5**: T023 [P], T024 [P], T025 [P] - 3 tasks  
**Within Phase 6**: T035 [P], T036 [P] - 2 tasks  
**Within Phase 7**: T044 [P], T053 [P] - 2 tasks  
**Within Phase 8**: T056-T060 [P] - 5 tasks

**Total Parallel**: 24 tasks can run simultaneously

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks | Can Start After |
|-------|------------|------------|----------------|-----------------|
| Phase 1 | Setup | 6 tasks | 3 parallel | Immediately |
| Phase 2 | Foundational | 7 tasks | 7 parallel | Phase 1 |
| Phase 3 | Migration | 5 tasks | 0 parallel | Phase 2 |
| Phase 4 | US4 (Security) P1 | 4 tasks | 2 parallel | Phase 3 |
| Phase 5 | US1 (Signup) P1 | 12 tasks | 3 parallel | Phase 4 |
| Phase 6 | US2 (Login) P1 | 9 tasks | 2 parallel | Phase 5 |
| Phase 7 | US3 (Middleware) P2 | 12 tasks | 2 parallel | Phase 6 |
| Phase 8 | Polish | 10 tasks | 5 parallel | Phase 7 |
| **TOTAL** | **4 User Stories** | **65 tasks** | **24 parallel** | - |

---

## MVP Definition

**Minimum Viable Product** = Phase 1-7

- ✅ Dependencies and configuration (Phase 1)
- ✅ Password hashing and JWT utilities (Phase 2)
- ✅ Database migration (Phase 3)
- ✅ Password security (Phase 4)
- ✅ User signup (Phase 5)
- ✅ User login with JWT tokens (Phase 6)
- ✅ JWT verification middleware (Phase 7)

**MVP Task Count**: 55 tasks
**MVP Delivers**: Complete authentication system with signup, login, and JWT protection

**Post-MVP**:
- Phase 8: Documentation and validation

---

## Implementation Strategy

### Recommended Order

1. **Dependencies & Config** (Phases 1-2)
   - Install libraries
   - Setup configuration
   - Build utilities

2. **Database Extension** (Phase 3)
   - Extend User model
   - Run migration
   
3. **MVP Core** (Phases 4-7)
   - Password security
   - User registration
   - User login
   - JWT middleware

4. **Polish** (Phase 8)
   - Documentation
   - Final testing

### Incremental Delivery Checkpoints

- ✅ **Checkpoint 1**: Phase 2 complete → Auth utilities ready (hash, JWT)
- ✅ **Checkpoint 2**: Phase 3 complete → Database ready for passwords
- ✅ **Checkpoint 3**: Phase 5 complete → User signup working
- ✅ **Checkpoint 4**: Phase 6 complete → Login and JWT tokens working
- ✅ **Checkpoint 5**: Phase 7 complete → Protected endpoints secured
- ✅ **Checkpoint 6**: Phase 8 complete → Production ready

---

## Success Criteria Mapping

**US4 (Password Security)**:
- SC-001: Passwords hashed with bcrypt before storage
- SC-008: Passwords never exposed in responses

**US1 (Registration)**:
- SC-001: Account creation with hashed password
- SC-003: Invalid credentials rejected (duplicate email)

**US2 (Login)**:
- SC-002: JWT token received on successful login
- SC-004: Token signature verified with BETTER_AUTH_SECRET
- SC-005: Token expiry set to 7 days

**US3 (Middleware)**:
- SC-006: Automatic token verification on protected endpoints
- SC-007: user_id extracted from token and available to routes
- SC-010: Auth operations complete within 500ms

---

## Notes

- **Extends Feature 1**: Builds on existing backend structure
- **No Tests**: Manual testing via quickstart.md sufficient
- **User Story Organization**: Enables independent testing of each story
- **Security First**: Password security (US4) before registration (US1)
- **65 Tasks Total**: Comprehensive authentication implementation
- **24 Parallel**: Significant parallelization opportunities

---

**Status**: ✅ Ready for `/sp.implement`

