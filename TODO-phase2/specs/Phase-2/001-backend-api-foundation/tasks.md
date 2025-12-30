---
description: "Implementation tasks for Backend API Foundation feature"
---

# Tasks: Backend API Foundation

**Input**: Design documents from `/specs/001-backend-api-foundation/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests are NOT explicitly requested in the spec, so test tasks are excluded. Testing will be done manually using quickstart.md scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Using **backend-only structure** as defined in plan.md:
- Backend code: `backend/src/`
- Tests: `backend/tests/`
- Configuration: `backend/` root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per plan.md (src/, tests/, config files)
- [X] T002 Initialize UV project in backend/ with pyproject.toml
- [X] T003 [P] Add dependencies to pyproject.toml (fastapi, uvicorn, sqlmodel, psycopg2-binary, python-dotenv, pydantic-settings)
- [X] T004 [P] Add dev dependencies to pyproject.toml (pytest, pytest-asyncio, httpx)
- [X] T005 Install dependencies with UV (uv sync)
- [X] T006 [P] Create .env.example file with DATABASE_URL and config variables
- [X] T007 [P] Create .gitignore file with Python patterns (\_\_pycache\_\_, .env, *.pyc, .venv/, etc.)

**Checkpoint**: ✅ Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create config.py with Pydantic Settings for DATABASE_URL and app configuration in backend/src/config.py
- [X] T009 Create db.py with SQLAlchemy engine, connection pooling, and session factory in backend/src/db.py
- [X] T010 Create models.py with User and Task SQLModel entities per data-model.md in backend/src/models.py
- [X] T011 Create schemas.py with Pydantic request/response models (TaskCreate, TaskUpdate, TaskResponse) in backend/src/schemas.py
- [X] T012 Initialize Alembic for database migrations in backend/ (alembic init alembic)
- [X] T013 Generate initial migration for users and tasks tables (alembic revision --autogenerate -m "Create users and tasks tables")
- [X] T014 Create main.py FastAPI application entry point with CORS and middleware setup in backend/src/main.py
- [X] T015 [P] Create middleware/error_handler.py with global exception handlers in backend/src/middleware/error_handler.py
- [X] T016 [P] Create routes/\_\_init\_\_.py to organize route modules in backend/src/routes/\_\_init\_\_.py

**Checkpoint**: ✅ Foundation ready - database models, API structure, error handling complete

---

## Phase 3: User Story 4 - Database Connection and Health Check (Priority: P1) 🎯 Foundation

**Goal**: Establish reliable database connectivity and provide health check endpoint to verify backend is operational

**Independent Test**: Make GET request to /health endpoint and verify database connection status. Success means endpoint returns 200 OK with "connected" database status.

### Implementation for User Story 4 (P1 - Foundation)

- [X] T017 [P] [US4] Create routes/health.py with GET /health endpoint in backend/src/routes/health.py
- [X] T018 [US4] Implement database connectivity check in health endpoint (test connection with simple query)
- [X] T019 [US4] Add health response schema with status, database, version, timestamp fields
- [X] T020 [US4] Handle database connection failures gracefully (return 503 Service Unavailable)
- [X] T021 [US4] Register health route in main.py

**Manual Testing** (per quickstart.md):
- Start server: `uv run uvicorn src.main:app --reload`
- Test: `curl http://localhost:8000/health`
- Verify: Status 200, database "connected"

**Checkpoint**: ✅ Health check working, database connectivity verified

---

## Phase 4: User Story 1 - Task Creation and Retrieval (Priority: P1) 🎯 MVP Core

**Goal**: Implement core CRUD functionality for creating and viewing tasks via REST API

**Independent Test**: POST to /api/tasks to create task, then GET /api/tasks to retrieve all tasks, and GET /api/tasks/{id} for specific task. Success means tasks are persisted and retrievable with correct data.

### Implementation for User Story 1 (P1 - MVP Core)

- [X] T022 [P] [US1] Create routes/tasks.py with APIRouter setup in backend/src/routes/tasks.py
- [X] T023 [P] [US1] Implement POST /api/tasks endpoint (create task) with Pydantic validation
- [X] T024 [P] [US1] Implement GET /api/tasks endpoint (list all tasks) with optional completed filter
- [X] T025 [P] [US1] Implement GET /api/tasks/{id} endpoint (get specific task)
- [X] T026 [US1] Add TaskCreate schema validation (title 1-200 chars, description max 1000 chars) in schemas.py
- [X] T027 [US1] Add TaskResponse schema for API responses in schemas.py
- [X] T028 [US1] Implement database session dependency (get_session) in db.py
- [X] T029 [US1] Add error handling for task not found (404) in task routes
- [X] T030 [US1] Add error handling for invalid input (400) with validation details
- [X] T031 [US1] Add database transaction handling with proper commit/rollback
- [X] T032 [US1] Register task routes in main.py under /api prefix

**Manual Testing** (per quickstart.md):
- Create test user first (see quickstart.md)
- Create task: `http POST localhost:8000/api/tasks title="Test" user_id="test-user-001"`
- List tasks: `http GET localhost:8000/api/tasks`
- Get task: `http GET localhost:8000/api/tasks/1`
- Verify: All endpoints return correct data, timestamps populated

**Checkpoint**: ✅ Core CRUD (Create, Read) fully functional and tested

---

## Phase 5: User Story 2 - Task Updates and Status Management (Priority: P2)

**Goal**: Enable task modification and completion status toggling

**Independent Test**: Create task (using US1), then PUT /api/tasks/{id} to update it, and PATCH /api/tasks/{id}/complete to toggle status. Success means changes persist across GET requests.

### Implementation for User Story 2 (P2 - Updates)

- [X] T033 [P] [US2] Implement PUT /api/tasks/{id} endpoint (update task) in backend/src/routes/tasks.py
- [X] T034 [P] [US2] Implement PATCH /api/tasks/{id}/complete endpoint (toggle completion) in backend/src/routes/tasks.py
- [X] T035 [US2] Add TaskUpdate schema with optional title and description in backend/src/schemas.py
- [X] T036 [US2] Implement updated_at timestamp auto-update on task modification
- [X] T037 [US2] Add validation for update requests (title/description length if provided)
- [X] T038 [US2] Handle task not found (404) for update operations
- [X] T039 [US2] Handle invalid update data (400) with validation errors

**Manual Testing** (per quickstart.md):
- Update task: `http PUT localhost:8000/api/tasks/1 title="Updated Title"`
- Toggle status: `http PATCH localhost:8000/api/tasks/1/complete`
- Verify: Changes persist, updated_at timestamp refreshed

**Checkpoint**: ✅ Task updates and status management working

---

## Phase 6: User Story 3 - Task Deletion (Priority: P3)

**Goal**: Enable task removal from the system

**Independent Test**: Create task (using US1), then DELETE /api/tasks/{id}. Success means task is removed and subsequent GET returns 404.

### Implementation for User Story 3 (P3 - Deletion)

- [X] T040 [P] [US3] Implement DELETE /api/tasks/{id} endpoint in backend/src/routes/tasks.py
- [X] T041 [US3] Return 204 No Content on successful deletion
- [X] T042 [US3] Handle task not found (404) for delete operations
- [X] T043 [US3] Verify task is actually removed from database after delete

**Manual Testing** (per quickstart.md):
- Delete task: `http DELETE localhost:8000/api/tasks/1`
- Verify deleted: `http GET localhost:8000/api/tasks/1` should return 404

**Checkpoint**: ✅ Task deletion working correctly

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation

- [X] T044 [P] Add docstrings to all functions and classes per PEP 8 standards
- [X] T045 [P] Add type hints to all function signatures
- [X] T046 [P] Verify all functions are under 50 lines (refactor if needed)
- [X] T047 [P] Add logging statements for all database operations
- [X] T048 [P] Create backend/README.md with setup instructions and API documentation
- [X] T049 [P] Verify .env.example has all required variables
- [X] T050 Validate all endpoints against OpenAPI spec (contracts/api-endpoints.yaml)
- [X] T051 Test all error scenarios from quickstart.md (empty title, title too long, invalid ID, database failure)
- [X] T052 Verify performance meets targets (<500ms response time per quickstart.md)
- [X] T053 Run linter and fix any issues (ruff or flake8)
- [X] T054 Final manual test of all CRUD operations end-to-end

**Checkpoint**: ✅ Feature complete, documented, and validated

---

## Dependencies & Execution Flow

### Critical Path (Must Complete in Order)

1. **Phase 1** (Setup) → Must complete before Phase 2
2. **Phase 2** (Foundational) → Must complete before Phase 3
3. **Phase 3** (US4 - Health Check) → Must complete to verify infrastructure
4. **Phase 4** (US1 - CRUD Core) → MVP, must complete for basic functionality

### Independent Phases (Can Run in Parallel After Phase 3)

After Phase 3 completes, these can be implemented in any order:
- **Phase 5** (US2 - Updates) - Independent of US3
- **Phase 6** (US3 - Deletion) - Independent of US2
- **Phase 7** (Polish) - Can start when Phase 4 completes

### Parallel Execution Opportunities

**Within Phase 1 (Setup):**
- T003 [P], T004 [P], T006 [P], T007 [P] can run simultaneously

**Within Phase 2 (Foundational):**
- T015 [P], T016 [P] can run after T014

**Within Phase 3 (US4):**
- T017 [P] can start immediately

**Within Phase 4 (US1):**
- T022 [P], T023 [P], T024 [P], T025 [P] can be implemented in parallel

**Within Phase 5 (US2):**
- T033 [P], T034 [P] can be implemented in parallel

**Within Phase 6 (US3):**
- T040 [P] is independent

**Within Phase 7 (Polish):**
- T044 [P], T045 [P], T046 [P], T047 [P], T048 [P], T049 [P] can run simultaneously

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks | Can Start After |
|-------|------------|------------|----------------|----------------|
| Phase 1 | Setup | 7 tasks | 4 parallel | Immediately |
| Phase 2 | Foundational | 9 tasks | 2 parallel | Phase 1 complete |
| Phase 3 | US4 (Health) P1 | 5 tasks | 1 parallel | Phase 2 complete |
| Phase 4 | US1 (CRUD) P1 | 11 tasks | 4 parallel | Phase 3 complete |
| Phase 5 | US2 (Updates) P2 | 7 tasks | 2 parallel | Phase 4 complete |
| Phase 6 | US3 (Delete) P3 | 4 tasks | 1 parallel | Phase 4 complete |
| Phase 7 | Polish | 11 tasks | 6 parallel | Phase 4 complete |
| **TOTAL** | **4 User Stories** | **54 tasks** | **20 parallel** | - |

---

## MVP Definition

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 + Phase 4

- ✅ Project setup and dependencies (Phase 1)
- ✅ Database models and infrastructure (Phase 2)
- ✅ Health check endpoint (Phase 3 - US4)
- ✅ Task creation and retrieval (Phase 4 - US1)

**MVP Task Count**: 32 tasks
**MVP Delivers**: Basic task management with create, list, and retrieve operations plus health monitoring

**Post-MVP Enhancements**:
- Phase 5 (US2): Task updates and status toggling
- Phase 6 (US3): Task deletion
- Phase 7: Polish and documentation

---

## Implementation Strategy

### Recommended Order

1. **Start with MVP** (Phases 1-4)
   - Delivers immediate value
   - Provides working foundation
   - Enables early testing

2. **Add Updates** (Phase 5)
   - Completes task lifecycle management
   - Higher priority than deletion

3. **Add Deletion** (Phase 6)
   - Final CRUD operation
   - Lower priority, can be deferred

4. **Polish** (Phase 7)
   - Throughout implementation
   - Final pass before feature complete

### Incremental Delivery Checkpoints

- ✅ **Checkpoint 1**: Phase 2 complete → Database and models ready
- ✅ **Checkpoint 2**: Phase 3 complete → Health check working
- ✅ **Checkpoint 3**: Phase 4 complete → MVP deliverable (task creation/retrieval)
- ✅ **Checkpoint 4**: Phase 5 complete → Full task management
- ✅ **Checkpoint 5**: Phase 6 complete → Complete CRUD
- ✅ **Checkpoint 6**: Phase 7 complete → Production ready

---

## Success Criteria (from spec.md)

Each phase must validate against corresponding success criteria:

**US4 (Health Check)**:
- SC-006: Health endpoint returns 200 OK with database connectivity status

**US1 (CRUD Core)**:
- SC-001: Can create task with all fields populated correctly
- SC-002: Can retrieve all tasks with correct data structure
- SC-003: Can get specific task by ID
- SC-007: All API endpoints respond within 500ms

**US2 (Updates)**:
- SC-003: Can update task and changes persist
- SC-004: Can toggle completion status

**US3 (Deletion)**:
- SC-004: Deleted tasks are removed from database

**Cross-Cutting (All Phases)**:
- SC-005: Clear error messages for invalid input
- SC-008: Database schema matches data-model.md
- SC-009: Graceful handling of database failures
- SC-010: REST conventions followed

---

## Notes

- **No Authentication**: This feature intentionally excludes authentication per spec.md. JWT authentication will be added in Feature 2.
- **No Tests**: Tests are not explicitly requested in spec.md, so test tasks are excluded. Manual testing via quickstart.md scenarios is sufficient.
- **User Story Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.
- **Parallel Execution**: 20 tasks marked with [P] can run in parallel when dependencies are met.
- **File Paths**: All paths use backend/ prefix per plan.md monorepo structure.

---

**Status**: ✅ Ready for `/sp.implement`

