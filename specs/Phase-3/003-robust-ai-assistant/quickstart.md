# Quick Start Guide - Robust AI Chat Assistant

**Feature**: 001-robust-ai-assistant
**Purpose**: Get developers up and running with the enhanced AI chat assistant
**Date**: 2026-01-27

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+ installed
- ✅ Node.js 18+ and npm installed
- ✅ PostgreSQL database running (local or Neon cloud)
- ✅ OpenAI API key with GPT-4o access
- ✅ Git repository cloned
- ✅ Basic familiarity with FastAPI, Next.js, and PostgreSQL

---

## Environment Setup

### 1. Backend Setup

**Navigate to backend directory**:
```bash
cd backend
```

**Create and activate virtual environment**:
```bash
# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

**Install dependencies** (including new packages):
```bash
pip install -r requirements.txt
```

**New dependencies added for this feature**:
- `dateparser==1.2.0` - Natural language date parsing
- `rapidfuzz==3.6.0` - Fast fuzzy string matching
- `pytest-mock==3.12.0` - Mocking framework for tests

**Configure environment variables**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required environment variables**:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_chatbot

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Performance monitoring
ENABLE_STRUCTURED_LOGGING=true
ENABLE_PERFORMANCE_LOGGING=true
```

---

### 2. Database Migration

**Run Alembic migration** to add conversation state fields:

```bash
# Generate migration (if not already generated)
alembic revision --autogenerate -m "Add conversation state tracking fields"

# Apply migration
alembic upgrade head

# Verify migration
alembic current
# Should show: <revision_id> (head)
```

**Verify database schema**:
```bash
psql -d todo_chatbot -c "\d conversations"
```

**Expected columns** (new fields added):
```
 id               | integer               |
 user_id          | integer               |
 created_at       | timestamp             |
 updated_at       | timestamp             |
 current_intent   | character varying     |  ← NEW
 state_data       | json                  |  ← NEW
 target_task_id   | integer               |  ← NEW
```

**Rollback (if needed)**:
```bash
# Rollback last migration
alembic downgrade -1

# Verify rollback
alembic current
```

---

### 3. Run Backend Development Server

**Start server**:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify server is running**:
```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
{"status": "healthy", "timestamp": "2026-01-27T12:00:00Z"}
```

**Access API documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 4. Frontend Setup

**Navigate to frontend directory** (in new terminal):
```bash
cd frontend
```

**Install dependencies**:
```bash
npm install
```

**Configure environment variables**:
```bash
# Copy example env file
cp .env.local.example .env.local

# Edit .env.local
nano .env.local
```

**Required environment variables**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG=true
```

**Start development server**:
```bash
npm run dev
```

**Verify frontend is running**:
- Open browser: http://localhost:3000
- You should see the chat interface

---

## Testing the Feature

### Manual Testing Workflow

**1. Create a test user and get JWT token**:
```bash
# Using httpie (or curl)
http POST http://localhost:8000/api/auth/register \
  email="test@example.com" \
  password="testpassword123"

# Login to get token
http POST http://localhost:8000/api/auth/login \
  email="test@example.com" \
  password="testpassword123"

# Save token
export JWT_TOKEN="<token_from_response>"
```

**2. Start a conversation**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="add task to buy milk"
```

**Expected response**:
```json
{
  "success": true,
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "Great! I'll help you add a task to buy milk. What priority should this be? (high/medium/low)"
  },
  "conversation_state": {
    "current_intent": "ADDING_TASK",
    "target_task_id": null
  }
}
```

**3. Continue conversation (provide priority)**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  conversation_id:=1 \
  message="high priority"
```

**4. Complete the task creation**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  conversation_id:=1 \
  message="tomorrow"

http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  conversation_id:=1 \
  message="no description needed"
```

**Expected final response**:
```json
{
  "success": true,
  "message": {
    "content": "✅ Task created successfully! Task #1: Buy milk (🔴 high priority, due tomorrow)"
  },
  "conversation_state": {
    "current_intent": "NEUTRAL"
  },
  "tool_calls": [
    {
      "tool": "add_task",
      "result": {"success": true, "task": {"id": 1, "title": "Buy milk"}}
    }
  ]
}
```

**5. Test other workflows**:

**Update task**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="update task 1 to medium priority"
```

**Delete task**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="delete task 1"
# Responds with confirmation request
# Then confirm:
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  conversation_id:=1 \
  message="yes"
```

**List tasks**:
```bash
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="show my tasks"
```

**Fuzzy task matching**:
```bash
# Create a task first
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="add task to buy milk from whole foods"

# Then search by partial name
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="update the milk task to low priority"
```

---

### Automated Testing

**Run all tests**:
```bash
cd backend
pytest tests/ -v
```

**Run specific test categories**:
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Contract tests only
pytest tests/contract/ -v

# Edge case tests
pytest tests/edge_cases/ -v
```

**Run with coverage**:
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

**View coverage report**:
```bash
# Open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Expected coverage targets**:
- Overall: 95%+
- AI agent logic: 90%+
- MCP tools: 100%
- API endpoints: 95%+

---

## Debugging Guide

### Common Issues and Solutions

#### Issue 1: Migration fails with "column already exists"

**Error**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution**:
```bash
# Check current migration state
alembic current

# If migration was partially applied, rollback and retry
alembic downgrade -1
alembic upgrade head
```

---

#### Issue 2: OpenAI API key invalid

**Error**:
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution**:
```bash
# Verify API key is set correctly
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If invalid, regenerate key at https://platform.openai.com/api-keys
```

---

#### Issue 3: Intent detection not working

**Symptom**: "delete task" being treated as task title

**Debug steps**:
```bash
# Check conversation state in database
psql -d todo_chatbot -c "SELECT id, current_intent, state_data FROM conversations WHERE id = 1;"

# Check system prompt is correct
# File: backend/src/ai_agent/agent.py
# Look for: "INTENT DETECTION" section

# Check pre-processing logic
# File: backend/src/services/intent_classifier.py
# Verify patterns match correctly

# Enable debug logging
# In .env: ENABLE_DEBUG_LOGGING=true
```

---

#### Issue 4: Database connection pool exhausted

**Error**:
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solution**:
```bash
# Increase pool size in database configuration
# File: backend/src/db.py
# Change: pool_size=5 → pool_size=10
# Change: max_overflow=10 → max_overflow=20

# Or use environment variable:
# In .env: DATABASE_POOL_SIZE=10
```

---

#### Issue 5: Fuzzy matching not finding tasks

**Symptom**: find_task returns "No tasks found"

**Debug steps**:
```python
# Test fuzzy matching directly
from rapidfuzz import fuzz

query = "milk"
title = "Buy milk from store"

score = fuzz.ratio(query.lower(), title.lower())
print(f"Score: {score}")  # Should be > 60

# Test token_sort_ratio (handles word order)
score = fuzz.token_sort_ratio(query.lower(), title.lower())
print(f"Token Sort Score: {score}")  # Should be higher

# Adjust threshold if needed
# File: backend/src/utils/fuzzy_matcher.py
# Change: threshold=0.6 → threshold=0.5
```

---

### Logging and Monitoring

**Enable structured logging**:
```bash
# In .env
ENABLE_STRUCTURED_LOGGING=true
LOG_LEVEL=DEBUG
```

**View logs**:
```bash
# Real-time logs
tail -f logs/app.log

# Filter for errors
grep ERROR logs/app.log

# Filter for specific conversation
grep "conversation_id=123" logs/app.log
```

**Log format** (JSON):
```json
{
  "timestamp": "2026-01-27T12:00:00Z",
  "level": "INFO",
  "message": "Tool called successfully",
  "context": {
    "user_id": 456,
    "conversation_id": 123,
    "tool": "add_task",
    "execution_time_ms": 234
  }
}
```

---

## Performance Monitoring

**Check response times**:
```bash
# Enable performance logging
# In .env: ENABLE_PERFORMANCE_LOGGING=true

# View performance metrics
grep "execution_time_ms" logs/app.log | jq '.context.execution_time_ms' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count "ms"}'
```

**Expected performance**:
- Intent classification: <50ms
- Date parsing: <100ms
- Fuzzy matching: <50ms
- Total chat response: <2s (p50), <5s (p95)

---

## Development Workflow

### Making Changes

**1. Create a feature branch**:
```bash
git checkout -b fix/improve-intent-detection
```

**2. Write tests first (TDD)**:
```bash
# Create test file
touch backend/tests/unit/test_improved_intent_detection.py

# Write failing tests
pytest tests/unit/test_improved_intent_detection.py
# Tests should FAIL (red)
```

**3. Implement feature**:
```bash
# Modify code
nano backend/src/services/intent_classifier.py

# Run tests again
pytest tests/unit/test_improved_intent_detection.py
# Tests should PASS (green)
```

**4. Refactor**:
```bash
# Improve code quality while keeping tests passing
# Run all tests to ensure no regressions
pytest tests/ -v
```

**5. Commit and push**:
```bash
git add .
git commit -m "fix: improve intent detection for edge cases"
git push origin fix/improve-intent-detection
```

**6. Create pull request**:
```bash
# Use GitHub CLI
gh pr create --title "Fix: Improve intent detection" --body "Addresses #123"
```

---

### Code Quality Checks

**Run linter**:
```bash
# Backend (Python)
cd backend
black src/ tests/  # Format code
flake8 src/ tests/  # Check style
mypy src/  # Type checking

# Frontend (TypeScript)
cd frontend
npm run lint
npm run type-check
```

**Run tests with coverage**:
```bash
pytest tests/ --cov=src --cov-report=term --cov-fail-under=95
```

**Pre-commit checks** (recommended):
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Manually run pre-commit
pre-commit run --all-files
```

---

## Useful Commands Reference

### Database

```bash
# Connect to database
psql -d todo_chatbot

# List all conversations
SELECT id, user_id, current_intent FROM conversations;

# View conversation state
SELECT id, current_intent, state_data FROM conversations WHERE id = 1;

# Clear conversation state (for testing)
UPDATE conversations SET current_intent = 'NEUTRAL', state_data = NULL, target_task_id = NULL WHERE id = 1;

# Count messages per conversation
SELECT conversation_id, COUNT(*) as message_count FROM messages GROUP BY conversation_id;
```

### API Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "add task to buy milk"}'

# Test with httpie (recommended - prettier output)
http POST http://localhost:8000/api/chat \
  "Authorization: Bearer $JWT_TOKEN" \
  message="add task to buy milk"

# Test with Python requests
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/chat',
    headers={'Authorization': 'Bearer $JWT_TOKEN'},
    json={'message': 'add task to buy milk'}
)
print(response.json())
"
```

---

## Next Steps

**After setup is complete**:

1. ✅ **Read the specification**: `specs/Phase-3/001-robust-ai-assistant/spec.md`
2. ✅ **Review technical research**: `specs/001-robust-ai-assistant/research.md`
3. ✅ **Understand data model changes**: `specs/001-robust-ai-assistant/data-model.md`
4. ✅ **Study tool contracts**: `specs/001-robust-ai-assistant/contracts/mcp-tools.md`
5. ⏳ **Implement the feature**: Follow `/sp.tasks` generated task breakdown (coming next)
6. ⏳ **Write tests first**: Use TDD approach - tests before code
7. ⏳ **Create skill**: Add to `.claude/skills/robust-ai-assistant/`
8. ⏳ **Update constitution**: Add skill requirement to `.specify/memory/constitution.md`

---

## Getting Help

**Resources**:
- **Specification**: `specs/Phase-3/001-robust-ai-assistant/spec.md`
- **Implementation Plan**: `specs/001-robust-ai-assistant/plan.md`
- **API Contracts**: `specs/001-robust-ai-assistant/contracts/api-endpoints.md`
- **Project Constitution**: `.specify/memory/constitution.md`
- **Backend Guide**: `backend/CLAUDE.md`
- **Frontend Guide**: `frontend/CLAUDE.md`

**Need help?**
- Check existing tests for examples
- Review MCP tool implementations in `backend/src/mcp_tools/`
- Consult FastAPI docs: https://fastapi.tiangolo.com
- OpenAI Agents SDK docs: https://platform.openai.com/docs/agents

---

**Happy coding! 🚀**
