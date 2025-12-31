# Research: Protected Task API

**Feature**: Protected Task API  
**Branch**: `003-protected-task-api`  
**Date**: 2025-12-10  
**Status**: Complete

## Purpose
Secure existing task endpoints by enforcing JWT authentication and per-user isolation. Leverage Feature 2 (Authentication) without schema changes.

## Research Topics & Decisions

### 1) Authorization Pattern
- **Decision**: Reuse FastAPI dependency `get_current_user` from Feature 2.
- **Rationale**: Native, concise, reusable; already tested in auth feature.
- **Usage**: Inject `current_user_id: str = Depends(get_current_user)` in all task handlers.

### 2) Ownership Enforcement
- **Decision**: Scope all task queries by `user_id == current_user_id`; return 403 when token user_id ≠ path user_id.
- **Rationale**: Prevent horizontal privilege escalation; path user_id is not trusted.
- **Semantics**: 403 for cross-user access; 404 when task not found for that user.

### 3) Endpoint Protection Strategy
- **Decision**: Protect all task endpoints: list, create, get, update, delete, complete.
- **Create**: Ignore client user_id; always set from token.
- **Read/Update/Delete/Complete**: Fetch by id AND user_id.

### 4) Error Semantics
- **Decision**: 
  - 401 Unauthorized → missing/invalid/expired token (handled by auth dependency)
  - 403 Forbidden → token user_id does not match resource/user
  - 404 Not Found → task id not found for authenticated user
- **Rationale**: Clear separation between auth, authorization, and existence.

### 5) Data Model Changes
- **Decision**: None. Use existing `tasks.user_id` FK; enforce in queries.
- **Rationale**: Ownership already modeled; only code-level enforcement needed.

## References
- FastAPI Security (Depends + HTTPBearer)
- JWT auth from Feature 2 (PyJWT, get_current_user)
- OWASP: Broken Access Control (enforce per-resource ownership)
