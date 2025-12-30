---
id: 0004
title: Protected Task API Implementation
stage: green
date: 2025-12-10
surface: agent
model: claude-sonnet-4.5
feature: 003-protected-task-api
branch: 003-protected-task-api
user: donia_batool
command: /sp.implement
labels: ["phase-2", "tasks", "authorization", "jwt", "implementation"]
links:
  spec: /home/donia_batool/phase-2/specs/003-protected-task-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-protected-task-api/tasks.md
  - specs/003-protected-task-api/contracts/tasks-protected.yaml
  - backend/src/routes/tasks.py
  - backend/src/schemas.py
  - backend/README.md
  - backend/.env (uses BETTER_AUTH_SECRET from Feature 2)
  - backend/.env.example
  - history/prompts/003-protected-task-api/0001-protected-task-api-spec.spec.prompt.md
  - history/prompts/003-protected-task-api/0002-protected-task-api-plan.plan.prompt.md
  - history/prompts/003-protected-task-api/0003-protected-task-api-tasks.tasks.prompt.md
tests:
  - Manual curl tests: missing token 401, invalid token 401, cross-user 403, own tasks success, not-found 404
---

## Prompt

User requested `/sp.implement` for Feature 3: Protect all task endpoints with JWT and enforce user isolation/ownership.

## Response snapshot

**Implemented & Tested**
- Added JWT auth dependency to all task routes (`get_current_user`)
- Scoped all list/get/update/delete/complete queries by user_id
- Enforced ownership: 403 on cross-user access, 404 when task not found for user
- Removed user_id from TaskCreate input; server sets user_id from token
- Added logging for forbidden/not-found cases
- Updated README to note tasks require JWT and are user-scoped
- Added contracts/tasks-protected.yaml with BearerAuth and 401/403 responses

**Manual Tests (curl)**
- Missing token on tasks → 401 ✅
- Invalid token → 401 ✅
- Cross-user access to task id → 403 ✅ (Alice token on Bob task)
- Own tasks list/create → 200/201 ✅
- Not-found task id for user → 404 ✅
- Bob task created and visible only to Bob

## Outcome

- ✅ Impact: Task API now secured with JWT and strict ownership. Users can access only their tasks; cross-user attempts receive 403, missing/invalid tokens receive 401. No schema changes required.
- 🧪 Tests: Manual verification of auth, isolation, ownership, and error semantics (401/403/404) performed.
- 📁 Files: tasks.py updated with auth dependency and ownership checks; schemas.py TaskCreate updated; README updated; contracts added; tasks.md updated (all tasks completed).
- 🔁 Next prompts: Integrate with Feature 4 frontend (uses same JWT). Optionally add automated tests later.
- 🧠 Reflection: Small, focused change leveraging Feature 2 auth. Ownership enforced via query scoping and checks; security behavior matches spec.

## Evaluation notes (flywheel)

- Failure modes: Initial server not running during tests; restarted and verified. curl token parsing fixed after server restart.
- Graders: PASS (manual tests confirmed).
- Next experiment: Start Feature 4 (/sp.specify) for frontend integration.
