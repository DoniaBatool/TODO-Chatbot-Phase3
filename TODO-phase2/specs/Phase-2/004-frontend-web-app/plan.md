# Implementation Plan: Frontend Web App

**Feature**: 004-frontend-web-app  
**Branch**: `004-frontend-web-app`  
**Status**: Draft  
**Tech**: Next.js 14/16 App Router, TypeScript, Tailwind CSS, fetch/axios, JWT storage (localStorage or cookie), Vercel-compatible.

## Architecture & Scope
- App Router with layouts; pages: `/login`, `/signup`, `/tasks` (protected). Optional landing `/` redirects based on auth.
- UI components: forms (inputs, buttons), task list items, toasts/loading/empty states.
- API client in `lib/api.ts`: base URL from `NEXT_PUBLIC_API_URL`, attaches Authorization header when token present.
- Auth session stored in localStorage (MVP). Consider cookie/HttpOnly later; on 401/403, clear and redirect to login.
- Styling: Tailwind CSS, responsive layouts.

## Constraints & Invariants
- Do not change backend contracts; reuse existing endpoints.
- Token must be sent on all protected routes; missing/invalid token → logout + redirect.
- Client-side validation for email/password and task title length.
- Keep diff minimal; no backend edits.

## Tasks / Steps
1) **Setup**: Initialize Next.js app (if not already); add Tailwind; add env `NEXT_PUBLIC_API_URL` sample.
2) **API Client**: `lib/api.ts` with helper `apiFetch` (or axios) that injects token, handles 401/403 (logout redirect), parses JSON, throws typed errors.
3) **Auth Store/Hook**: Simple hook or context to manage token + user info; load from localStorage; helpers `login`, `logout`, `setToken`.
4) **Signup Page**: Form with email/password; client validation; POST `/api/auth/signup`; on success show message/redirect to login.
5) **Login Page**: Form; POST `/api/auth/login`; store token; redirect to `/tasks`; handle invalid creds error.
6) **Route Guard**: Protect `/tasks` by checking token on client; if missing, redirect to `/login`.
7) **Tasks Page**: Fetch tasks on mount with token; show loading, empty state, error with retry. Allow create/update/complete/delete via buttons/forms; optimistic or refetch after mutation.
8) **Components**: Reusable `Button`, `Input`, `TaskItem`, `TaskForm`, `Toast/Alert` for errors.
9) **UX States**: Disable submit while loading; show inline errors; empty-state card when no tasks.
10) **Testing/Docs**: Update README or quickstart for frontend; manual test checklist (auth + task flows).

## Data Contracts (frontend usage)
- Auth endpoints: `/api/auth/signup`, `/api/auth/login`, `/api/auth/me` (token check).
- Task endpoints: `/api/tasks` (GET, POST), `/api/tasks/{id}` (GET, PUT, DELETE), `/api/tasks/{id}/complete` (PATCH).
- Token storage: `localStorage.setItem('token', ...)`; Authorization header `Bearer <token>`.

## Risks & Mitigations
- Token storage in localStorage → XSS risk; keep minimal scope and sanitize; consider HttpOnly cookies later.
- 401/403 loops → central handler to logout once and redirect.
- Network errors → show toast/retry; avoid silent failures.

## Acceptance Checks
- Can signup/login and see tasks page with data.
- All task calls include Authorization header when logged in.
- 401/403 triggers logout + redirect to login.
- Loading/error/empty states visible as defined.
- Mobile layout usable (basic responsive checks).
