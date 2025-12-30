# Research: Frontend Web App (004)

**Feature**: 004-frontend-web-app  
**Branch**: `004-frontend-web-app`  
**Date**: 2025-12-10  
**Status**: Complete

## Goals
Build a Next.js App Router frontend with auth flows and task CRUD, reusing backend API (Feature 1-3) and JWT tokens (Feature 2).

## Decisions
1) **Framework**: Next.js App Router + TypeScript
   - Rationale: Modern routing/layouts, good DX, aligns with monorepo expectations.
2) **Styling**: Tailwind CSS
   - Rationale: Fast UI iteration, responsive utilities.
3) **API Client**: fetch wrapper (`lib/api.ts`)
   - Base URL from `NEXT_PUBLIC_API_URL`
   - Attach `Authorization: Bearer <token>` when token present
   - On 401/403 → clear token, throw AuthError for redirect handling
4) **State/Storage**: localStorage for JWT (MVP)
   - Rationale: Simplicity; tradeoff: XSS risk acknowledged. Upgrade path: HttpOnly cookie if needed.
5) **Auth Flows**: Forms for signup/login with client validation; redirects to `/tasks` after login.
6) **Route Guard**: Client-side check for token; missing token → redirect to `/login`.
7) **Tasks UI**: Fetch on mount; show loading/error/empty; support create/update/complete/delete with refetch.
8) **Error/Loading UX**: Inline alerts, disabled buttons during requests; empty state messaging.

## Edge/Risks
- Token in localStorage susceptible to XSS; mitigate by minimal surface and sanitizing inputs; future improvement: cookies + CSRF.
- Infinite redirect loops on 401/403 avoided via single clear+redirect in api client.
- Network failures: surfaced via Alert and retry.

## References
- Next.js App Router docs
- Tailwind CSS docs
- Fetch API and HTTP auth headers
- Feature 2 JWT auth contract (`/api/auth/login`, `/api/auth/signup`)
- Feature 3 task endpoints with JWT enforcement
