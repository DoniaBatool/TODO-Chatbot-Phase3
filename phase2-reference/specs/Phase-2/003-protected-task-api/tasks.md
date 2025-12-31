---
description: "Implementation tasks for Protected Task API feature"
---

# Tasks: Protected Task API

**Input**: Design documents from `/specs/003-protected-task-api/`
**Prerequisites**: spec.md ✅, plan.md ✅, research (embedded) ✅, quickstart (embedded) ✅, contracts (to update)

**Tests**: Manual testing via quickstart curl/Swagger; automated tests optional

**Organization**: Tasks grouped by user story (US1 auth enforcement, US2 isolation, US3 ownership)

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel
- **[Story]**: US1 (auth required), US2 (isolation), US3 (ownership)

---

## Phase 1: Preparation (Existing Auth Integration)
- [X] T001 Confirm Feature 2 auth dependency available (backend/src/auth/dependencies.py:get_current_user)
- [X] T002 [P] Import get_current_user into backend/src/routes/tasks.py
- [X] T003 [P] Ensure BETTER_AUTH_SECRET present in .env (already from Feature 2)

**Checkpoint**: Auth dependency ready to use in task routes

---

## Phase 2: Protect Task Endpoints (US1 - Auth Required)
- [X] T004 [US1] Add dependency injection (current_user_id = Depends(get_current_user)) to all task route handlers
- [X] T005 [US1] Enforce 401 for missing/invalid tokens (handled by dependency) – validate wiring
- [X] T006 [P] [US1] Update task router prefix/use to ensure auth applies to: list, create, get, update, delete, complete

**Checkpoint**: All task endpoints require JWT (401 on missing/invalid token)

---

## Phase 3: User Isolation (US2 - Path user_id vs token user)
- [X] T007 [US2] Validate URL user_id matches token user_id at start of each handler; return 403 on mismatch
- [X] T008 [P] [US2] Normalize identifiers to lowercase before comparison
- [X] T009 [US2] For create task: override any provided user_id with token user_id (ignore path/body user_id)

**Checkpoint**: Cross-user access blocked (403)

---

## Phase 4: Ownership Enforcement (US3 - CRUD checks)
- [X] T010 [US3] List tasks: filter query by authenticated user_id only
- [X] T011 [US3] Get task by id: fetch by id AND user_id; return 404 if not found
- [X] T012 [US3] Update task (PUT): fetch by id AND user_id; 404 if not found; then update
- [X] T013 [US3] Toggle complete (PATCH): fetch by id AND user_id; 404 if not found; then toggle
- [X] T014 [US3] Delete task: fetch by id AND user_id; 404 if not found; then delete
- [X] T015 [P] [US3] Ensure response codes remain: 200/201 for success, 204 for delete, 404 for not-found-per-user

**Checkpoint**: Ownership enforced on all CRUD operations

---

## Phase 5: Error Semantics & Consistency
- [X] T016 [P] Add consistent 401/403/404 messages (auth vs authorization vs not found)
- [X] T017 [P] Keep validation errors unchanged (title length, etc.)
- [X] T018 [P] Add minimal logging for 403/404 in tasks routes (optional)

**Checkpoint**: Errors consistent and secure

---

## Phase 6: Contracts & Documentation
- [X] T019 [P] Update contracts/tasks-protected.yaml: add BearerAuth security scheme and 401/403 responses to all task endpoints
- [X] T020 [P] Add notes on user_id matching and ownership to endpoint descriptions
- [X] T021 Update backend/README.md to mention task endpoints now require JWT and are user-scoped

**Checkpoint**: Docs/specs aligned with protected behavior

---

## Phase 7: Testing (Manual)
- [X] T022 Manual test: missing token → 401 (any task endpoint)
- [X] T023 Manual test: invalid/expired token → 401
- [X] T024 Manual test: cross-user path (user A token on user B path) → 403
- [X] T025 Manual test: cross-user task id (user A token on task owned by B) → 403
- [X] T026 Manual test: own tasks list/create/get/update/delete/complete → 200/201/204
- [X] T027 Manual test: not-found task id for user → 404

**Checkpoint**: Behavior verified

---

## Phase 8: Polish
- [X] T028 [P] Add docstrings to updated task handlers (auth/ownership notes)
- [X] T029 [P] Ensure type hints intact after changes
- [X] T030 [P] Quick lint pass on modified files (tasks.py)

**Checkpoint**: Ready for release

---

## MVP Definition
- Phases 1–7 deliver protected task API (auth required, isolation, ownership)

## Notes
- No database/schema changes needed
- Relies on Feature 2 JWT auth; ensure server running with BETTER_AUTH_SECRET
- Path user_id should not be trusted; token user_id is source of truth
