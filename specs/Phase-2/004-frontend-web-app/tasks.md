# Tasks - Feature 004: Frontend Web App

Status: Complete  
Branch: `004-frontend-web-app`

## Phase 1 - Setup & Tooling
- [X] T001 Create Next.js (App Router) project scaffolding in `frontend/` with TypeScript
- [X] T002 Add Tailwind CSS setup (config, globals, postcss) and base layout styling
- [X] T003 Add env sample `.env.example` with `NEXT_PUBLIC_API_URL`
- [X] T004 Add lint/format scripts and ensure project builds locally

## Phase 2 - API Client & Auth Store
- [X] T005 Implement `lib/api.ts` with base URL, JSON helpers, and Authorization header injection from stored token
- [X] T006 Handle 401/403 globally in api client (clear session + redirect to login)
- [X] T007 Implement simple auth store/hook (token + user info) backed by localStorage with `login`, `logout`, `setToken`

## Phase 3 - Auth Pages
- [X] T008 Build `/signup` page: email/password form, client validation, POST `/api/auth/signup`, show success message/redirect hint
- [X] T009 Build `/login` page: email/password form, client validation, POST `/api/auth/login`, store token, redirect to `/tasks`
- [X] T010 Show inline errors for failed auth; disable submit while loading
- [X] T011 Add shared form components (Input, Button) and error helper text

## Phase 4 - Route Guard & Layout
- [X] T012 Implement client-side guard for protected routes (check token, redirect to `/login` if missing)
- [X] T013 Add authenticated layout/nav with logout action that clears token and redirects to login
- [X] T014 Add initial redirect logic for `/` (e.g., to `/tasks` if logged in else `/login`)

## Phase 5 - Tasks Page (CRUD)
- [X] T015 Implement `/tasks` page: fetch tasks on load with loading/empty/error states
- [X] T016 Implement create task form with client validation and refresh list on success
- [X] T017 Implement update/edit flow for a task (title/description) with refresh
- [X] T018 Implement complete/uncomplete toggle via PATCH `/api/tasks/{id}/complete`
- [X] T019 Implement delete task action with confirmation and refresh
- [X] T020 Build `TaskItem` and `TaskForm` components; reuse buttons/inputs

## Phase 6 - UX/State & Styling
- [X] T021 Add toasts/alerts for success/error and retry on failures
- [X] T022 Ensure buttons disable during pending requests to prevent duplicates
- [X] T023 Responsive layout for mobile/desktop; sensible spacing/typography

## Phase 7 - Docs & Testing
- [X] T024 Add frontend README/quickstart steps (env, install, dev server, tests)
- [X] T025 Manual test script: signup/login, token attach, CRUD flows, 401/403 handling, loading/error/empty states

## Phase 8 - Polish
- [X] T026 Run lint/format; fix any issues\n+- [X] T027 Final sanity check: 401/403 triggers logout; tasks page only after login
