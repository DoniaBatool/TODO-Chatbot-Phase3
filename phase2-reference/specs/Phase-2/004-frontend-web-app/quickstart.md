# Quickstart: Frontend Web App (004)

**Feature**: 004-frontend-web-app  
**Branch**: `004-frontend-web-app`  
**Date**: 2025-12-10

## Setup
```bash
cd frontend
npm install
cp .env.example .env  # set NEXT_PUBLIC_API_URL if backend not on localhost:8000
npm run dev
```

Open http://localhost:3000

## Flows to Test
1) **Signup**
   - Go to `/signup`
   - Enter email/password (>=8 chars)
   - Expect success message → redirected/prompted to login

2) **Login**
   - Go to `/login`
   - Enter valid creds
   - Expect redirect to `/tasks` and token stored (localStorage `todo_token`)

3) **Tasks CRUD** (token auto attached)
   - `/tasks` loads list → shows loading then tasks
   - Create task → appears in list
   - Edit task → updated text appears
   - Complete/uncomplete → badge toggles
   - Delete → item removed

4) **Error/State Handling**
   - Wrong password on login → inline error
   - Remove token (localStorage) then refresh `/tasks` → redirect to `/login`
   - Backend returns 401/403 (e.g., expired token) → auto logout + redirect
   - No tasks → empty state message

## Env
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Notes
- API client adds `Authorization: Bearer <token>` when token exists.
- 401/403 clears token and redirects to login.
- Buttons/forms disable during network calls to prevent duplicates.
