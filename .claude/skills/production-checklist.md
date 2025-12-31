---
description: Comprehensive production readiness validation checklist covering security, performance, monitoring, and deployment (Phase 3)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill provides a comprehensive production readiness checklist and automates verification of critical requirements before production deployment.

### Production Readiness Checklist

## 1. Security Checklist

### Authentication & Authorization
- [ ] JWT tokens validated on all protected routes
- [ ] Secret key is cryptographically strong (32+ bytes)
- [ ] Access tokens expire (recommended: 30 minutes)
- [ ] Refresh tokens implemented (if applicable)
- [ ] User isolation enforced on all endpoints
- [ ] Cross-user data access prevented

**Verification:**
```python
# Test: Invalid token should fail
response = requests.post(
    "http://localhost:8000/api/user-123/chat",
    headers={"Authorization": "Bearer invalid"},
    json={"message": "test"}
)
assert response.status_code == 401

# Test: Mismatched user_id should fail
response = requests.post(
    "http://localhost:8000/api/user-999/chat",
    headers={"Authorization": f"Bearer {user_123_token}"},
    json={"message": "test"}
)
assert response.status_code == 403
```

### Input Validation
- [ ] All user input sanitized
- [ ] SQL injection prevented (SQLModel parameterization)
- [ ] XSS prevention (not applicable for API-only)
- [ ] Message length limits enforced (< 10000 chars)
- [ ] File upload validation (if applicable)

**Verification:**
```python
# Test: SQL injection attempt should fail safely
response = requests.post(
    "/api/user-123/chat",
    headers=auth_headers,
    json={"message": "'; DROP TABLE tasks; --"}
)
# Should not execute SQL, should treat as string
```

### Secrets Management
- [ ] No secrets in code or version control
- [ ] All secrets in environment variables
- [ ] .env files in .gitignore
- [ ] API keys not logged
- [ ] Database passwords not exposed

**Verification:**
```bash
# Check for leaked secrets
git grep -i "sk-" -- "*.py"  # No OpenAI keys
git grep -i "password.*=" -- "*.py"  # No hardcoded passwords
grep -r "SECRET_KEY.*=" src/  # No hardcoded JWT secrets
```

## 2. Performance Checklist

### Response Times
- [ ] Chat endpoint p95 < 3000ms
- [ ] Database queries p95 < 100ms
- [ ] Health endpoint < 100ms
- [ ] Load tested with 100 concurrent users

**Verification:**
```bash
# Load test with Apache Bench
ab -n 1000 -c 100 -H "Authorization: Bearer $TOKEN" \
   -p request.json -T application/json \
   http://localhost:8000/api/user-123/chat

# Check p95 in results
```

### Database
- [ ] Connection pooling configured (pool_size=10, max_overflow=20)
- [ ] Indexes on user_id (all tables)
- [ ] Index on conversation_id (messages)
- [ ] Index on completed (tasks)
- [ ] Index on created_at (messages)
- [ ] Pool health monitoring enabled

**Verification:**
```sql
-- Check indexes exist
\d+ tasks
\d+ conversations
\d+ messages

-- Expected indexes:
-- tasks: idx_tasks_user_id, idx_tasks_completed
-- conversations: idx_conversations_user_id
-- messages: idx_messages_conversation_id, idx_messages_created_at
```

### Caching
- [ ] Static assets cached (if applicable)
- [ ] Database connection pooling active
- [ ] No unnecessary N+1 queries

## 3. Observability Checklist

### Logging
- [ ] Structured JSON logging configured
- [ ] All requests logged with request_id
- [ ] All errors logged with stack traces
- [ ] Performance metrics logged
- [ ] Sensitive data not logged (passwords, tokens)

**Verification:**
```bash
# Check logs are JSON formatted
tail -f logs/app.log | python -m json.tool

# Verify no sensitive data
grep -i "password" logs/app.log  # Should be empty
grep -i "sk-" logs/app.log  # Should be empty
```

### Monitoring
- [ ] Health endpoint returns status
- [ ] Database connection health checked
- [ ] Pool metrics exposed
- [ ] Error rate monitoring (target: < 1%)
- [ ] Response time monitoring

**Verification:**
```bash
# Health check
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", "database": "connected"}
```

### Error Tracking
- [ ] All exceptions caught and logged
- [ ] User-friendly error messages returned
- [ ] Internal errors don't expose stack traces to users
- [ ] Error rate < 1% under normal load

## 4. Deployment Checklist

### Database Migrations
- [ ] Alembic migrations created
- [ ] Migrations tested on staging
- [ ] Rollback plan tested
- [ ] Backward compatible migrations

**Verification:**
```bash
# Test upgrade
alembic upgrade head
alembic current

# Test downgrade
alembic downgrade -1
alembic upgrade head
```

### Environment Configuration
- [ ] .env.production configured
- [ ] All required env vars set
- [ ] CORS origins configured
- [ ] Allowed hosts configured

**Verification:**
```bash
# Check all required vars
python scripts/check_env.py production
```

### Deployment Process
- [ ] CI/CD pipeline configured
- [ ] Automated tests run before deploy
- [ ] Staging environment deployed first
- [ ] Smoke tests run on staging
- [ ] Rollback procedure documented

## 5. API Documentation Checklist

- [ ] OpenAPI schema complete
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Error responses documented
- [ ] Authentication documented
- [ ] Rate limits documented

**Verification:**
```bash
# Export OpenAPI schema
curl http://localhost:8000/openapi.json > openapi.json

# Validate schema
npx @apidevtools/swagger-cli validate openapi.json
```

## 6. Testing Checklist

### Unit Tests
- [ ] All MCP tools have unit tests
- [ ] All services have unit tests
- [ ] Test coverage > 80%

**Verification:**
```bash
pytest --cov=src --cov-report=term-missing
# Target: > 80% coverage
```

### Integration Tests
- [ ] Chat endpoint integration tests
- [ ] Database integration tests
- [ ] Agent integration tests
- [ ] Tool execution tests

### End-to-End Tests
- [ ] User signup → login → chat flow
- [ ] All 5 tools tested via chat
- [ ] Multi-turn conversation tested
- [ ] Error scenarios tested

## 7. OWASP Top 10 Checklist

- [ ] A01:2021 - Broken Access Control: User isolation enforced
- [ ] A02:2021 - Cryptographic Failures: Passwords hashed with bcrypt
- [ ] A03:2021 - Injection: SQL injection prevented (SQLModel)
- [ ] A04:2021 - Insecure Design: Stateless architecture
- [ ] A05:2021 - Security Misconfiguration: No debug mode in production
- [ ] A06:2021 - Vulnerable Components: Dependencies updated
- [ ] A07:2021 - Authentication Failures: JWT with expiration
- [ ] A08:2021 - Software Integrity Failures: Dependencies pinned
- [ ] A09:2021 - Logging Failures: Comprehensive logging
- [ ] A10:2021 - SSRF: No user-controlled URLs fetched

## Automated Verification Script

**File**: `backend/scripts/production_checklist.py`

```python
"""Production readiness verification script."""

import os
import sys
import requests
from sqlalchemy import create_engine, text

def check_environment():
    """Check all required environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "SECRET_KEY",
        "ALLOWED_ORIGINS"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False

    print("✅ All environment variables set")
    return True


def check_database():
    """Check database connection and migrations."""
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        # Check tables exist
        with engine.connect() as conn:
            tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            table_names = {row[0] for row in tables}

        required_tables = {"users", "tasks", "conversations", "messages"}
        missing_tables = required_tables - table_names

        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False

        print("✅ Database connection and tables verified")
        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


def check_health_endpoint():
    """Check health endpoint is accessible."""
    try:
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        response = requests.get(f"{base_url}/api/health", timeout=5)

        if response.status_code != 200:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False

        data = response.json()
        if data.get("status") != "healthy":
            print(f"❌ Health status: {data.get('status')}")
            return False

        print("✅ Health endpoint verified")
        return True

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def check_security():
    """Check security configurations."""
    # Check SECRET_KEY length
    secret_key = os.getenv("SECRET_KEY", "")
    if len(secret_key) < 32:
        print("❌ SECRET_KEY must be at least 32 characters")
        return False

    # Check no secrets in code
    import subprocess
    result = subprocess.run(
        ["git", "grep", "-i", "sk-", "--", "*.py"],
        capture_output=True
    )
    if result.returncode == 0:
        print("❌ Possible API key found in code")
        return False

    print("✅ Security checks passed")
    return True


def main():
    """Run all production readiness checks."""
    print("🔍 Production Readiness Checklist\n")

    checks = [
        ("Environment Variables", check_environment),
        ("Database", check_database),
        ("Health Endpoint", check_health_endpoint),
        ("Security", check_security),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n{name}:")
        results.append(check_fn())

    print("\n" + "="*50)
    if all(results):
        print("🎉 All checks passed! Ready for production.")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python scripts/production_checklist.py
```

## Constitution Alignment

- ✅ **Security**: Comprehensive security validation
- ✅ **Performance**: Performance targets verified
- ✅ **Observability**: Logging and monitoring checked
- ✅ **Deployment**: Safe deployment procedures

## Success Criteria

- [ ] All security checks pass
- [ ] All performance targets met
- [ ] All monitoring configured
- [ ] All tests passing
- [ ] Production checklist script runs successfully
- [ ] No secrets in code or logs
- [ ] Rollback plan tested

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- 12-Factor App: https://12factor.net/
- Production Best Practices: https://fastapi.tiangolo.com/deployment/
