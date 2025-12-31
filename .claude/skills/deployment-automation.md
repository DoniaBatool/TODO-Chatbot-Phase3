---
description: Automate deployment workflow with Alembic migrations, environment setup, and staging/production deployment (Phase 3)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill automates the complete deployment workflow including database migrations, environment configuration, deployment to staging/production, and post-deployment verification.

### 1. Run Alembic Migrations

**Step 1: Generate Migration**
```bash
cd backend
alembic revision --autogenerate -m "add_conversations_and_messages_tables"
```

**Step 2: Review Migration File**
Check `backend/alembic/versions/XXXX_add_conversations_and_messages_tables.py`

**Step 3: Run Migration on Staging**
```bash
# Set staging database URL
export DATABASE_URL="postgresql://user:pass@staging-db-host:5432/dbname"

# Run migration
alembic upgrade head

# Verify tables created
alembic current
alembic history
```

### 2. Environment Configuration

**File**: `backend/.env.example` (template)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_AGENT_MODEL=gpt-4o

# JWT
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

**Staging Setup:**
```bash
cp .env.example .env.staging
# Edit .env.staging with staging values
```

**Production Setup:**
```bash
cp .env.example .env.production
# Edit .env.production with production values
```

### 3. Deploy to Staging

**Using Docker:**

**File**: `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Copy application
COPY . .

# Run migrations and start server
CMD poetry run alembic upgrade head && poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Deploy:**
```bash
# Build image
docker build -t todo-chatbot-api:staging .

# Run container
docker run -d \
  --name todo-chatbot-staging \
  -p 8000:8000 \
  --env-file .env.staging \
  todo-chatbot-api:staging

# Check logs
docker logs -f todo-chatbot-staging
```

### 4. Deploy to Production

**Using Fly.io:**

**File**: `backend/fly.toml`
```toml
app = "todo-chatbot-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[deploy]
  release_command = "poetry run alembic upgrade head"
```

**Deploy:**
```bash
# Login
fly auth login

# Create app
fly apps create todo-chatbot-api

# Set secrets
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set DATABASE_URL=postgresql://...
fly secrets set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
fly deploy

# Check status
fly status
fly logs
```

### 5. Post-Deployment Verification

**Health Check:**
```bash
# Check health endpoint
curl https://todo-chatbot-api.fly.dev/api/health

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "version": "3.0.0"
}
```

**Database Verification:**
```bash
# Check tables exist
psql $DATABASE_URL -c "\dt"

# Expected tables:
# - users
# - tasks
# - conversations
# - messages
```

**API Test:**
```bash
# Test auth
curl -X POST https://todo-chatbot-api.fly.dev/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Test chat (with token from signup)
curl -X POST https://todo-chatbot-api.fly.dev/api/user-123/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to test deployment"}'
```

### 6. Rollback Plan

**Alembic Downgrade:**
```bash
# Show current version
alembic current

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123def456

# Rollback to base
alembic downgrade base
```

**Application Rollback:**
```bash
# Using Docker
docker stop todo-chatbot-production
docker run -d \
  --name todo-chatbot-production \
  -p 8000:8000 \
  --env-file .env.production \
  todo-chatbot-api:previous-version

# Using Fly.io
fly releases
fly deploy --image registry.fly.io/todo-chatbot-api:previous-sha
```

### 7. Deployment Checklist Script

**File**: `backend/scripts/deploy.sh`
```bash
#!/bin/bash
set -e

echo "🚀 Todo Chatbot Deployment Script"
echo ""

# Parse arguments
ENVIRONMENT=${1:-staging}
echo "Environment: $ENVIRONMENT"

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
  export $(cat .env.$ENVIRONMENT | xargs)
else
  echo "❌ .env.$ENVIRONMENT not found"
  exit 1
fi

# Step 1: Run tests
echo "✅ Running tests..."
poetry run pytest

# Step 2: Run migrations
echo "✅ Running database migrations..."
alembic upgrade head

# Step 3: Verify migrations
echo "✅ Verifying migrations..."
alembic current

# Step 4: Deploy application
if [ "$ENVIRONMENT" = "production" ]; then
  echo "✅ Deploying to production..."
  fly deploy
else
  echo "✅ Deploying to staging..."
  docker-compose -f docker-compose.staging.yml up -d
fi

# Step 5: Health check
echo "✅ Running health checks..."
sleep 5
curl -f http://localhost:8000/api/health || exit 1

echo ""
echo "🎉 Deployment complete!"
```

**Usage:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh staging
./scripts/deploy.sh production
```

## Constitution Alignment

- ✅ **Automation**: Repeatable deployment process
- ✅ **Safety**: Migrations run before deployment
- ✅ **Rollback**: Clear rollback procedures
- ✅ **Verification**: Post-deployment health checks

## Success Criteria

- [ ] Alembic migrations run successfully on staging
- [ ] conversations and messages tables created
- [ ] Environment variables configured
- [ ] Application deployed to staging
- [ ] Health check returns 200 OK
- [ ] API endpoints accessible
- [ ] Production deployment successful
- [ ] Rollback plan documented and tested

## References

- Alembic: https://alembic.sqlalchemy.org/
- Fly.io: https://fly.io/docs/
- Docker: https://docs.docker.com/
