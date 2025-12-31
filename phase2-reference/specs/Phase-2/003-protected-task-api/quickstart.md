# Quickstart Guide: Protected Task API

**Feature**: Protected Task API  
**Branch**: `003-protected-task-api`  
**Date**: 2025-12-10

## Purpose
Test JWT protection and ownership enforcement on all task endpoints.

## Prerequisites
- Feature 2 authentication working (signup/login) ✅
- BETTER_AUTH_SECRET configured ✅
- Server running at http://localhost:8000
- Users exist (e.g., alice@example.com, bob@example.com)

## Get Tokens (login)
```bash
# Alice
ALICE_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"SecurePassword123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Bob
BOB_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"BobPassword123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

## Test Scenarios

### 1) Missing Token → 401
```bash
curl -i http://localhost:8000/api/tasks
```

### 2) Invalid Token → 401
```bash
curl -i http://localhost:8000/api/tasks -H "Authorization: Bearer invalid.token"
```

### 3) Create Tasks (per user)
```bash
# Alice creates
task_a=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Alice Task","description":"owned by alice"}')

echo "$task_a" | python3 -m json.tool

# Bob creates
task_b=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Bob Task","description":"owned by bob"}')

echo "$task_b" | python3 -m json.tool
```

### 4) List Own Tasks (200)
```bash
curl -s http://localhost:8000/api/tasks -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool
curl -s http://localhost:8000/api/tasks -H "Authorization: Bearer $BOB_TOKEN" | python3 -m json.tool
```

### 5) Cross-User Access (403)
```bash
# Bob tries to get Alice task id=1 (example)
curl -i http://localhost:8000/api/tasks/1 -H "Authorization: Bearer $BOB_TOKEN"
```

### 6) Not Found (404)
```bash
curl -i http://localhost:8000/api/tasks/9999 -H "Authorization: Bearer $BOB_TOKEN"
```

### 7) Update/Delete Own Task (200/204)
```bash
# Assuming Bob's task id is 4
curl -s -X PUT http://localhost:8000/api/tasks/4 \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Bob Task Updated"}' | python3 -m json.tool

curl -i -X DELETE http://localhost:8000/api/tasks/4 \
  -H "Authorization: Bearer $BOB_TOKEN"
```

## Expected Results
- 401 for missing/invalid token
- 403 for cross-user access (token user_id ≠ task owner)
- 404 when task id not found for that user
- 200/201/204 for same-user CRUD operations

## Swagger UI
- URL: http://localhost:8000/docs
- Authorize with Bearer token (top right) then try task endpoints

## Notes
- user_id is derived from JWT, not trusted from client/path
- No schema changes needed; enforcement is in code
