# Frontend Web App (Feature 004)

Next.js App Router + TypeScript + Tailwind for auth and task management.

## Prerequisites
- Node 18+
- Backend running at `http://localhost:8000` (or set `NEXT_PUBLIC_API_URL`)
- Existing users or ability to signup via UI

## Setup
```bash
cd frontend
npm install
cp .env.example .env   # adjust NEXT_PUBLIC_API_URL if needed
npm run dev
```

## Env
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Flows
- **Signup**: `/signup` → POST `/api/auth/signup`; on success, go to login.
- **Login**: `/login` → POST `/api/auth/login`; stores JWT in localStorage; redirects to `/tasks`.
- **Tasks**: `/tasks` fetches with Authorization header; supports create, update, complete toggle, delete.
- **Auth handling**: 401/403 clears token and redirects to login.

## Testing Checklist
- Signup success + validation errors
- Login success + wrong-cred error
- Tasks list shows only own tasks (backend enforces isolation)
- Create/update/complete/delete flow works; buttons disabled while loading
- Missing/expired token → redirected to login
- Loading/error/empty states visible

## Scripts
- `npm run dev` — start dev server
- `npm run build` — production build
- `npm run start` — start prod server
- `npm run lint` — lint
