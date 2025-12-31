# Quickstart Guide: Authentication System

**Feature**: Authentication System  
**Branch**: `002-authentication-system`  
**Date**: 2025-12-10

## Purpose

This quickstart guide provides step-by-step instructions for testing the authentication system including user signup, login with JWT tokens, and protected endpoint access.

---

## Prerequisites

- **Feature 1** complete and tested ✅
- **Database** already configured (Neon PostgreSQL)
- **Server** running at http://localhost:8000

---

## Setup Instructions (New Dependencies)

### 1. Install Authentication Dependencies

```bash
cd /home/donia_batool/phase-2/backend
source .venv/bin/activate

# Install new dependencies
uv pip install pyjwt passlib[bcrypt] email-validator python-multipart
```

### 2. Update Environment Variables

Add to `backend/.env`:

```bash
# Authentication (add these lines)
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
```

**⚠️ IMPORTANT**: Generate a strong secret for production:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run Migration (Add password_hash field)

```bash
cd /home/donia_batool/phase-2/backend
source .venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Add password_hash to users"

# Apply migration
alembic upgrade head

# Verify column added
python3 -c "from src.db import engine; from sqlmodel import text; with engine.connect() as conn: print(conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \\'users\\'') ).fetchall())"
```

---

## Testing Scenarios

### Scenario 1: User Signup

**Purpose**: Test user registration with email/password

```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123",
    "name": "Alice Johnson"
  }'

# Expected Response (201 Created):
{
  "id": "uuid-generated",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2025-12-10T10:00:00Z"
}
```

**Success Criteria**:
- ✅ Status code 201
- ✅ User ID is generated (UUID format)
- ✅ Email stored in lowercase
- ✅ Password NOT in response
- ✅ User created in database with password_hash (bcrypt)

---

### Scenario 2: User Login

**Purpose**: Test authentication and JWT token generation

```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }'

# Expected Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "uuid",
    "email": "alice@example.com",
    "name": "Alice Johnson"
  }
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ JWT token returned
- ✅ Token can be decoded
- ✅ User information included
- ✅ expires_in is 604800 (7 days in seconds)

---

### Scenario 3: Verify JWT Token (Get Current User)

**Purpose**: Test JWT token verification

```bash
# First, save the token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Then use it to get current user
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected Response (200 OK):
{
  "id": "uuid",
  "email": "alice@example.com",
  "name": "Alice Johnson",
  "created_at": "2025-12-10T10:00:00Z"
}
```

**Success Criteria**:
- ✅ Status code 200
- ✅ Token verified successfully
- ✅ User data returned
- ✅ No password in response

---

### Scenario 4: Decode JWT Token (Verify Structure)

**Purpose**: Manually verify JWT token contains correct claims

```bash
# Save token from login
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Decode token (Python)
python3 -c "
import jwt
token = '$TOKEN'
secret = 'your-secret-from-env'
payload = jwt.decode(token, secret, algorithms=['HS256'])
print('User ID:', payload.get('sub'))
print('Email:', payload.get('email'))
print('Expires:', payload.get('exp'))
print('Issued:', payload.get('iat'))
"
```

**Expected Output**:
```
User ID: 550e8400-e29b-41d4-a716-446655440000
Email: alice@example.com
Expires: 1702857600
Issued: 1702252800
```

---

## Error Testing Scenarios

### Test 1: Duplicate Email

```bash
# Try to signup with same email again
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "AnotherPass123",
    "name": "Alice Clone"
  }'

# Expected Response (400):
{
  "detail": "Email already registered",
  "error_code": "EMAIL_EXISTS"
}
```

### Test 2: Weak Password

```bash
# Password < 8 characters
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "weak"
  }'

# Expected Response (400):
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters"
    }
  ]
}
```

### Test 3: Invalid Email Format

```bash
# Invalid email
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "password": "SecurePass123"
  }'

# Expected Response (400):
{
  "detail": "Invalid email format"
}
```

### Test 4: Wrong Password on Login

```bash
# Correct email, wrong password
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "WrongPassword"
  }'

# Expected Response (401):
{
  "detail": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS"
}
```

### Test 5: Non-existent User Login

```bash
# Email doesn't exist
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SomePassword"
  }'

# Expected Response (401):
{
  "detail": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS"
}
```

**Note**: Same error message as wrong password (security best practice)

### Test 6: Missing Authorization Header

```bash
# Try protected endpoint without token
curl http://localhost:8000/api/auth/me

# Expected Response (401):
{
  "detail": "Not authenticated"
}
```

### Test 7: Invalid JWT Token

```bash
# Use fake/malformed token
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid.token.here"

# Expected Response (401):
{
  "detail": "Invalid or expired token",
  "error_code": "INVALID_TOKEN"
}
```

---

## Complete Testing Workflow

### End-to-End Authentication Flow

```bash
# 1. Signup new user
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "name": "Test User"
  }')

echo "Signup Response:"
echo $SIGNUP_RESPONSE | python3 -m json.tool

# 2. Login to get token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }')

echo "Login Response:"
echo $LOGIN_RESPONSE | python3 -m json.tool

# 3. Extract token
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"

# 4. Use token to access protected endpoint
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Password Verification in Database

### Check Password is Hashed

```bash
cd /home/donia_batool/phase-2/backend
source .venv/bin/activate

# Query database to see password_hash
python3 -c "
from src.db import get_session_context
from src.models import User

with get_session_context() as session:
    user = session.query(User).filter(User.email == 'alice@example.com').first()
    if user:
        print(f'Email: {user.email}')
        print(f'Password Hash: {user.password_hash}')
        print(f'Hash starts with \$2b\$: {user.password_hash.startswith(\"\$2b\$\")}')
    else:
        print('User not found')
"
```

**Expected Output**:
```
Email: alice@example.com
Password Hash: $2b$12$abcd...xyz (60 character bcrypt hash)
Hash starts with $2b$: True
```

**Verification**:
- ✅ password_hash is bcrypt format ($2b$12$...)
- ✅ NOT plain text password
- ✅ 60 characters long

---

## Swagger UI Testing

### Open Interactive Docs

**URL**: http://172.22.97.7:8000/docs

### Test Authentication Endpoints

**1. Test Signup:**
- Click **POST /api/auth/signup**
- Click **"Try it out"**
- Enter request body:
```json
{
  "email": "swagger@example.com",
  "password": "SwaggerTest123",
  "name": "Swagger User"
}
```
- Click **"Execute"**
- Verify 201 response with user data

**2. Test Login:**
- Click **POST /api/auth/login**
- Click **"Try it out"**
- Enter credentials:
```json
{
  "email": "swagger@example.com",
  "password": "SwaggerTest123"
}
```
- Click **"Execute"**
- **COPY** the `access_token` from response

**3. Test Protected Endpoint:**
- Click **GET /api/auth/me**
- Click **"Try it out"**
- Click 🔒 **"Authorize"** button (top right)
- Enter: `Bearer <paste-token-here>`
- Click **"Authorize"**
- Click **"Close"**
- Click **"Execute"** on /api/auth/me
- Verify you get your user data!

---

## Performance Testing

### Expected Metrics

| Operation | Target | Notes |
|-----------|--------|-------|
| Signup (with bcrypt) | <500ms | Includes password hashing |
| Login (with bcrypt) | <500ms | Includes password verification |
| Token generation | <50ms | JWT encoding |
| Token verification | <50ms | JWT decoding and validation |

### Load Test (Optional)

```bash
# Test signup endpoint
ab -n 10 -c 1 -p signup.json -T application/json \
  http://localhost:8000/api/auth/signup

# Note: Use c=1 (sequential) because bcrypt is CPU-intensive
```

---

## Troubleshooting

### Issue: "BETTER_AUTH_SECRET not configured"

**Solution**:
```bash
# Add to .env
echo "BETTER_AUTH_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> backend/.env
```

### Issue: "Email already registered"

**Solution**: Email already exists in database. Either:
- Use different email
- Delete existing user from database
- Test login instead of signup

### Issue: "Invalid credentials" on login

**Solution**:
- Verify email is correct
- Verify password is correct (case-sensitive)
- Check user was created via signup first

### Issue: "Invalid token" on protected endpoints

**Solution**:
- Verify token is fresh (not expired)
- Verify BETTER_AUTH_SECRET is same as when token was generated
- Check Authorization header format: `Bearer <token>` (note the space)

---

## Next Steps

After authentication testing complete:

1. **Feature 3**: Protected Task API
   - Use authentication middleware on task endpoints
   - Enforce user isolation (users only see their tasks)

2. **Feature 4**: Frontend Web App
   - Integrate Better Auth in Next.js
   - Use JWT tokens from backend
   - Build signup/login UI

---

## Summary

This quickstart covered:
- ✅ Dependency installation (PyJWT, passlib, email-validator)
- ✅ Environment configuration (BETTER_AUTH_SECRET)
- ✅ Database migration (password_hash field)
- ✅ 3 positive test scenarios (signup, login, protected endpoint)
- ✅ 7 error test scenarios (validation and auth failures)
- ✅ Password hash verification
- ✅ Swagger UI interactive testing

**Feature 2 Status**: Ready for `/sp.tasks` command to generate implementation tasks.

