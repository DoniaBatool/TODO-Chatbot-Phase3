# Implementation Plan: Protected Task API

**Branch**: `003-protected-task-api` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-protected-task-api/spec.md`

## Summary

Secure all task REST API endpoints with JWT authentication and enforce per-user isolation. All task routes will require a valid JWT token; user_id in the URL/path must match the authenticated user_id from the token. Ownership checks will be applied to all task CRUD operations to prevent cross-user access. No database schema changes are needed; enforcement is done via middleware and query scoping.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: FastAPI (existing), SQLModel (existing), PyJWT (from Feature 2)  
**Storage**: PostgreSQL (Neon) — existing schema, no changes  
**Testing**: pytest, httpx (if used), manual curl/Swagger tests  
**Target Platform**: Linux server (WSL2 dev, container-friendly)  
**Project Type**: Web backend (same backend service as Features 1 & 2)  
**Performance Goals**: Auth overhead < 50ms per request; p95 latency < 500ms  
**Constraints**: Must reject missing/invalid tokens (401) and cross-user access (403)  
**Scale/Scope**: Protect existing task endpoints only (no new models)

## Constitution Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| Spec-driven | ✅ PASS | spec.md defined, checklist passed |
| Backend quality | ✅ PASS | PEP8, type hints, docstrings enforced from previous features |
| Persistence | ✅ PASS | Reuses existing tasks/users tables |
| REST API | ✅ PASS | Same endpoints, now protected |
| Authentication | ✅ PASS | Relies on Feature 2 JWT auth |
| Security | ✅ PASS | Ownership checks, auth required |
| Error handling | ✅ PASS | 401/403/404 with HTTPException |
| Env vars | ✅ PASS | BETTER_AUTH_SECRET already configured |

## Project Structure

### Documentation (this feature)
```
specs/003-protected-task-api/
├── spec.md              # ✅ Feature specification
├── plan.md              # ✅ This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (no schema changes)
├── quickstart.md        # Phase 1 output (testing guide)
├── contracts/           # Phase 1 output
│   └── tasks-protected.yaml
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (reuse existing backend)
```
backend/
├── src/
│   ├── routes/
│   │   ├── tasks.py           # Protect endpoints with auth dependency
│   │   ├── auth.py            # From Feature 2 (JWT issuance)
│   │   └── health.py
│   ├── auth/                  # From Feature 2
│   │   └── dependencies.py    # get_current_user dependency
│   ├── schemas.py             # No changes expected
│   ├── models.py              # No changes expected
│   └── main.py                # Ensure middleware / route wiring
└── tests/                     # Add auth-protected task tests if needed
```

**Structure Decision**: No new modules; reuse Feature 2 auth dependency (`get_current_user`) and enforce in `routes/tasks.py`. No DB/schema changes.

## Complexity Tracking

**Complexity Level**: Low-Medium. Only adds authorization checks to existing routes; no schema changes. Reuses JWT verification from Feature 2.

---

# Research

## Research Topics & Decisions

1) **Authorization Pattern**: Reuse FastAPI dependency `get_current_user` from Feature 2; inject user_id into task routes.  
**Decision**: Use dependency injection instead of middleware class (consistent with Feature 2), minimal code changes.

2) **Ownership Enforcement**:  
**Decision**: Scope all task queries by `user_id == current_user_id`; return 403 when path user_id != token user_id; return 404 when task not found for that user.

3) **Endpoint Protection Strategy**:  
**Decision**: Protect all existing task endpoints: GET list, POST create, GET by id, PUT update, DELETE, PATCH complete. Ignore/override URL user_id with token user_id for creation; strictly compare for reads/updates/deletes.

4) **Error Semantics**:  
**Decision**: 401 for missing/invalid JWT; 403 for user_id mismatch or cross-user access; 404 when task id not found for that user.

5) **Data Model Changes**:  
**Decision**: None. Ownership already captured via tasks.user_id. Only code-level enforcement needed.

---

# Data Model

## Schema Changes

- **None required.** The `tasks` table already has `user_id` FK. Enforcement is via query filtering and authorization checks.

## Ownership Enforcement Rules

- Always filter queries: `WHERE tasks.user_id = current_user_id` for list/get.
- For update/delete/complete: first ensure task exists for the authenticated user; else return 404.
- Reject requests where URL user_id != token user_id with 403.

---

# Quickstart (Testing Plan)

**Prerequisite**: Feature 2 JWT auth working; obtain JWT tokens by signup/login.

### Test Matrix

1) **Missing Token**: Any task endpoint → 401 Unauthorized
2) **Invalid/Expired Token**: Any task endpoint → 401 Unauthorized
3) **User Isolation (403)**:
   - Use user A token on user B path → 403 (e.g., GET /api/userB/tasks)
   - Use user A token on task owned by B → 403 on GET/PUT/PATCH/DELETE
4) **Ownership Success (200/201/204)**:
   - Use user A token on user A path → all CRUD succeed
5) **Not Found (404)**:
   - Task id not found for that user → 404

### Example Commands (curl)

```bash
# Assume TOKEN_A and TOKEN_B from Feature 2 login
USER_A=user-a-id
USER_B=user-b-id

# 1) Missing token (should be 401)
curl -i http://localhost:8000/api/$USER_A/tasks

# 2) Invalid token (should be 401)
curl -i http://localhost:8000/api/$USER_A/tasks \
  -H "Authorization: Bearer invalid.token.here"

# 3) Cross-user access (should be 403)
curl -i http://localhost:8000/api/$USER_B/tasks \
  -H "Authorization: Bearer $TOKEN_A"

# 4) Create task for self (should be 201)
curl -i -X POST http://localhost:8000/api/$USER_A/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title":"My task","description":"Test"}'

# 5) Get own tasks (should be 200)
curl -i http://localhost:8000/api/$USER_A/tasks \
  -H "Authorization: Bearer $TOKEN_A"

# 6) Get specific task (owned) (should be 200)
curl -i http://localhost:8000/api/$USER_A/tasks/1 \
  -H "Authorization: Bearer $TOKEN_A"

# 7) Get someone else's task id (should be 403)
curl -i http://localhost:8000/api/$USER_B/tasks/1 \
  -H "Authorization: Bearer $TOKEN_A"
```

---

# Contracts (to be generated in Phase 1)

- Update existing task API contracts to note JWT requirement and ownership rules. (contracts/tasks-protected.yaml)
- Add security scheme BearerAuth and responses (401, 403) to each task endpoint.

---

# Completion Criteria

- All task endpoints require JWT and return 401 when missing/invalid.
- All task endpoints enforce user_id match; cross-user access returns 403.
- CRUD operations scoped to authenticated user; 404 when task not found for that user.
- No database/schema changes needed.
- Ready for `/sp.tasks` to generate implementation tasks.
