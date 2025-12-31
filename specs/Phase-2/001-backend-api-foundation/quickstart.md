# Quickstart Guide: Backend API Foundation

**Feature**: Backend API Foundation  
**Branch**: `001-backend-api-foundation`  
**Date**: 2025-12-09

## Purpose

This quickstart guide provides step-by-step instructions for setting up, running, and testing the Backend API Foundation feature. It includes database setup, API testing scenarios, and common troubleshooting tips.

---

## Prerequisites

- **Python**: 3.13+ installed
- **UV**: Package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **PostgreSQL**: Neon Serverless account (free tier available at https://neon.tech)
- **Git**: Version control
- **HTTPie or curl**: For API testing (optional: Postman, Insomnia)

---

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
# Navigate to project root
cd /home/donia_batool/phase-2

# Checkout feature branch
git checkout 001-backend-api-foundation

# Navigate to backend directory
cd backend
```

### 2. Install Dependencies

```bash
# Initialize UV project (if not already done)
uv init

# Install dependencies
uv sync

# Verify installation
uv run python --version  # Should show Python 3.13+
```

### 3. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Neon database URL
nano .env
```

**.env file content**:
```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# App
DEBUG=true
API_V1_PREFIX=/api

# Neon Connection Pool Settings (optional, has defaults)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
```

**Getting Neon Database URL**:
1. Go to https://neon.tech and create account
2. Create new project (free tier)
3. Copy connection string from dashboard
4. Replace `DATABASE_URL` in `.env` file

### 4. Initialize Database

```bash
# Initialize Alembic (first time only)
uv run alembic init alembic

# Generate initial migration
uv run alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migrations
uv run alembic upgrade head

# Verify tables created
uv run python -c "from src.db import engine; from sqlmodel import text; with engine.connect() as conn: print(conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\'')).fetchall())"
```

### 5. Create Test User (For Feature 1 Testing)

```bash
# Insert test user manually (Better Auth will handle this in Feature 2)
uv run python -c "
from src.db import get_session
from src.models import User
from datetime import datetime

with get_session() as session:
    user = User(
        id='test-user-001',
        email='test@example.com',
        name='Test User',
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    print(f'Test user created: {user.id}')
"
```

### 6. Run the Server

```bash
# Development mode with auto-reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Server should start at: http://localhost:8000
# OpenAPI docs available at: http://localhost:8000/docs
```

---

## Testing Scenarios

### Scenario 1: Health Check

**Purpose**: Verify API and database connectivity

```bash
# Using curl
curl http://localhost:8000/health

# Using HTTPie
http GET localhost:8000/health

# Expected Response (200 OK):
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2025-12-09T10:30:00Z"
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ `status` is "healthy"
- ✅ `database` is "connected"

---

### Scenario 2: Create Task

**Purpose**: Test task creation with valid data

```bash
# Using curl
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "user_id": "test-user-001"
  }'

# Using HTTPie
http POST localhost:8000/api/tasks \
  title="Buy groceries" \
  description="Milk, eggs, bread" \
  user_id="test-user-001"

# Expected Response (201 Created):
{
  "id": 1,
  "user_id": "test-user-001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

**Success Criteria**:
- ✅ Status code 201
- ✅ Task has auto-generated `id`
- ✅ `completed` defaults to `false`
- ✅ Timestamps are populated

---

### Scenario 3: List All Tasks

**Purpose**: Retrieve all tasks from database

```bash
# Using curl
curl http://localhost:8000/api/tasks

# Using HTTPie
http GET localhost:8000/api/tasks

# Expected Response (200 OK):
[
  {
    "id": 1,
    "user_id": "test-user-001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-09T10:00:00Z",
    "updated_at": "2025-12-09T10:00:00Z"
  }
]
```

**Success Criteria**:
- ✅ Status code 200
- ✅ Returns array of tasks
- ✅ Empty array if no tasks exist

---

### Scenario 4: Get Specific Task

**Purpose**: Retrieve task by ID

```bash
# Using curl
curl http://localhost:8000/api/tasks/1

# Using HTTPie
http GET localhost:8000/api/tasks/1

# Expected Response (200 OK):
{
  "id": 1,
  "user_id": "test-user-001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ Returns correct task data
- ✅ Returns 404 if task doesn't exist

---

### Scenario 5: Update Task

**Purpose**: Modify existing task

```bash
# Using curl
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and fruits",
    "description": "Milk, eggs, bread, apples, bananas"
  }'

# Using HTTPie
http PUT localhost:8000/api/tasks/1 \
  title="Buy groceries and fruits" \
  description="Milk, eggs, bread, apples, bananas"

# Expected Response (200 OK):
{
  "id": 1,
  "user_id": "test-user-001",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": false,
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T11:30:00Z"  # Note: timestamp updated
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ Task data is updated
- ✅ `updated_at` timestamp is refreshed
- ✅ Returns 404 if task doesn't exist

---

### Scenario 6: Toggle Task Completion

**Purpose**: Mark task as complete or incomplete

```bash
# Using curl
curl -X PATCH http://localhost:8000/api/tasks/1/complete

# Using HTTPie
http PATCH localhost:8000/api/tasks/1/complete

# Expected Response (200 OK):
{
  "id": 1,
  "user_id": "test-user-001",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": true,  # Toggled to true
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T11:45:00Z"
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ `completed` status is toggled
- ✅ Can be toggled multiple times
- ✅ Returns 404 if task doesn't exist

---

### Scenario 7: Delete Task

**Purpose**: Remove task from database

```bash
# Using curl
curl -X DELETE http://localhost:8000/api/tasks/1

# Using HTTPie
http DELETE localhost:8000/api/tasks/1

# Expected Response (204 No Content):
# (Empty response body)
```

**Success Criteria**:
- ✅ Status code 204
- ✅ Task is removed from database
- ✅ Subsequent GET returns 404
- ✅ Returns 404 if task already deleted

---

### Scenario 8: Filter Tasks by Completion Status

**Purpose**: Retrieve only completed or pending tasks

```bash
# Get only pending tasks
curl "http://localhost:8000/api/tasks?completed=false"
http GET "localhost:8000/api/tasks?completed=false"

# Get only completed tasks
curl "http://localhost:8000/api/tasks?completed=true"
http GET "localhost:8000/api/tasks?completed=true"

# Expected Response (200 OK):
[
  # Only tasks matching filter status
]
```

**Success Criteria**:
- ✅ Returns only tasks with matching `completed` status
- ✅ Works with both `true` and `false` values

---

## Error Testing Scenarios

### Test 1: Empty Title Validation

```bash
# Should fail with 400 Bad Request
http POST localhost:8000/api/tasks \
  title="" \
  user_id="test-user-001"

# Expected Response (400):
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title cannot be empty or whitespace",
      "type": "value_error"
    }
  ]
}
```

### Test 2: Title Too Long

```bash
# Title > 200 characters should fail
http POST localhost:8000/api/tasks \
  title="$(python -c 'print("a" * 201)')" \
  user_id="test-user-001"

# Expected Response (400):
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

### Test 3: Invalid Task ID

```bash
# Non-existent task should return 404
http GET localhost:8000/api/tasks/99999

# Expected Response (404):
{
  "detail": "Task 99999 not found",
  "error_code": "TASK_NOT_FOUND"
}
```

### Test 4: Database Connection Failure

```bash
# Stop database or use invalid DATABASE_URL
# Health check should return 503
http GET localhost:8000/health

# Expected Response (503):
{
  "detail": "Database connection failed",
  "error_code": "DATABASE_UNAVAILABLE"
}
```

---

## OpenAPI Documentation

FastAPI automatically generates interactive API documentation:

**Swagger UI** (Recommended):
- URL: http://localhost:8000/docs
- Interactive API testing interface
- Try out endpoints directly from browser

**ReDoc** (Alternative):
- URL: http://localhost:8000/redoc
- Clean, readable API documentation

---

## Automated Testing

### Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_tasks_crud.py

# Run specific test
uv run pytest tests/test_tasks_crud.py::test_create_task
```

### Test Categories

1. **Health Tests** (`tests/test_health.py`)
   - Database connectivity
   - API status
   
2. **CRUD Tests** (`tests/test_tasks_crud.py`)
   - Create task
   - Read tasks (list and get)
   - Update task
   - Delete task
   - Toggle completion
   
3. **Validation Tests** (`tests/test_validation.py`)
   - Empty title rejection
   - Title length validation
   - Description length validation
   - Invalid user_id handling

---

## Troubleshooting

### Issue: Database Connection Error

**Symptom**: `connection refused` or `could not translate host name`

**Solution**:
1. Verify Neon database URL in `.env` is correct
2. Check internet connectivity
3. Verify Neon project is not paused (free tier auto-pauses after inactivity)
4. Test connection: `psql $DATABASE_URL`

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in backend directory
cd backend

# Reinstall dependencies
uv sync

# Verify Python path
uv run python -c "import sys; print(sys.path)"
```

### Issue: Migration Errors

**Symptom**: Alembic migration fails or tables not created

**Solution**:
```bash
# Reset database (WARNING: deletes all data)
uv run alembic downgrade base
uv run alembic upgrade head

# Or manually drop tables in Neon console and re-run migrations
```

### Issue: Port Already in Use

**Symptom**: `Address already in use` when starting server

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uv run uvicorn src.main:app --reload --port 8001
```

---

## Next Steps

After successfully testing Feature 1, proceed to:

1. **Feature 2**: Authentication System (`/sp.specify` for Feature 2)
   - Implement Better Auth
   - Add JWT token generation and verification

2. **Feature 3**: Protected Task API
   - Secure endpoints with JWT authentication
   - Enforce user isolation

3. **Feature 4**: Frontend Web Application
   - Build Next.js UI
   - Integrate with backend API

---

## Performance Validation

### Expected Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Health check response time | <100ms | `time curl http://localhost:8000/health` |
| Create task | <200ms | `time curl -X POST ... /api/tasks` |
| List tasks (10 items) | <300ms | `time curl http://localhost:8000/api/tasks` |
| Update task | <200ms | `time curl -X PUT ... /api/tasks/1` |
| Delete task | <150ms | `time curl -X DELETE ... /api/tasks/1` |

### Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test 100 requests with 10 concurrent connections
ab -n 100 -c 10 http://localhost:8000/health

# Expected: All requests successful, avg response time <500ms
```

---

## Summary

This quickstart guide covered:
- ✅ Project setup and dependencies
- ✅ Database configuration and migrations
- ✅ Server startup and verification
- ✅ 8 positive test scenarios (CRUD operations)
- ✅ 4 error test scenarios (validation and error handling)
- ✅ Automated testing setup
- ✅ Troubleshooting common issues

**Feature 1 Status**: Ready for `/sp.tasks` command to generate implementation tasks.

