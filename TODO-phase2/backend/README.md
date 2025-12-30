# Todo Backend API

FastAPI backend for Todo application - Phase 2 Hackathon

## Features

- REST API for task management (CRUD operations)
- Authentication (signup, login, JWT-protected endpoint)
- SQLModel ORM with PostgreSQL
- Neon Serverless Database integration
- Pydantic validation
- Health check endpoint
- Task endpoints now require JWT and are scoped to the authenticated user

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Neon database URL
```

3. Run migrations:
```bash
uv run alembic upgrade head
```

4. Start server:
```bash
uv run uvicorn src.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

- Signup: `POST /api/auth/signup`
- Login: `POST /api/auth/login`
- Current user (protected): `GET /api/auth/me` (Authorization: Bearer <token>)

## Environment Variables

```
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# App
DEBUG=true
API_V1_PREFIX=/api

# Auth (Feature 2)
BETTER_AUTH_SECRET=generate-with-python-secrets-token_urlsafe-32
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── db.py                # Database connection
│   ├── models.py            # SQLModel entities
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/              # API endpoints
│   └── middleware/          # Error handling
├── tests/                   # Test files
└── alembic/                 # Database migrations
```

## Tech Stack

- Python 3.13+
- FastAPI
- SQLModel
- PostgreSQL (Neon Serverless)
- UV (package manager)
- Alembic (migrations)

