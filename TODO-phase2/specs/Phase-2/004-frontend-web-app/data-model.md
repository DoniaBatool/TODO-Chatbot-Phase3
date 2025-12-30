# Data Model: Frontend Web App (004)

**Feature**: 004-frontend-web-app  
**Branch**: `004-frontend-web-app`  
**Date**: 2025-12-10  
**Status**: Complete

## Purpose
Describe the frontend-facing data shapes; no backend schema changes.

## Entities (frontend models)
- **AuthUser**: id (string), email (string), name (optional)
- **Token**: access_token (string), token_type (string="bearer")
- **Task**: id (number), title (string 1-200), description (string ≤1000, optional), completed (bool), created_at (ISO, optional), updated_at (ISO, optional)

## Sources
- Auth endpoints (Feature 2):
  - POST `/api/auth/signup` -> SignupResponse { id, email, name? }
  - POST `/api/auth/login` -> LoginResponse { access_token, token_type, user }
- Task endpoints (Feature 1 + Feature 3 protection):
  - GET `/api/tasks` -> Task[] scoped to user
  - POST `/api/tasks` -> Task
  - GET `/api/tasks/{id}` -> Task (owned)
  - PUT `/api/tasks/{id}` -> Task
  - PATCH `/api/tasks/{id}/complete` -> Task
  - DELETE `/api/tasks/{id}` -> 204

## Validation (client-side)
- Email must be valid format.
- Password min length 8.
- Task title required, 1-200 chars; description optional ≤1000 chars.

## Storage
- JWT stored in localStorage under `todo_token` (MVP). Cleared on logout or 401/403.

## Notes
- Ownership/isolation enforced by backend; frontend ensures token attached.
- No additional client-side schema beyond the above shapes.
