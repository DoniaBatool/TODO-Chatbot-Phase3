# Data Model: Protected Task API

**Feature**: Protected Task API  
**Branch**: `003-protected-task-api`  
**Date**: 2025-12-10  
**Status**: Complete

## Summary
- **No schema changes required.**
- Ownership is already represented via `tasks.user_id` (FK to users.id).
- Enforcement is done in code: filter queries by authenticated `user_id` and block cross-user access.

## Existing Tables (from Feature 1)
- **tasks**: id (PK), user_id (FK), title, description, completed, created_at, updated_at
- **users**: id (PK), email, name, password_hash (from Feature 2), created_at

## Ownership Enforcement Rules
- All task queries are scoped: `WHERE tasks.user_id = current_user_id`
- For GET/PUT/PATCH/DELETE:
  - Fetch by `id AND user_id`; return 404 if not found for that user.
  - If token user_id ≠ path user_id → 403 Forbidden.
- For POST create:
  - Ignore client-supplied user_id; set user_id from JWT token.

## Error Semantics
- 401: Missing/invalid token (auth failure)
- 403: Cross-user access (token user_id ≠ path/owner)
- 404: Task id not found for the authenticated user

## Notes
- Normalize identifiers (user_id/email) to lowercase before comparison.
- No migrations or model changes needed.
- Aligns with Feature 2 JWT auth; relies on BETTER_AUTH_SECRET.
