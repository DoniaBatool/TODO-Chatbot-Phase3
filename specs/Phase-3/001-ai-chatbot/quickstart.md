# Quickstart: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot | **Phase**: 3 | **Status**: Planning Complete

## 🚀 What is This?

An AI-powered conversational interface that lets users manage tasks through natural language. Instead of filling forms, users chat with an AI assistant to add, view, complete, update, and delete tasks.

```
User: "Add task to buy milk"
Bot:  "I've added 'Buy milk' to your tasks."

User: "Show my pending tasks"
Bot:  "You have 2 pending tasks: 1. Buy milk, 2. Call mom"

User: "I finished buying milk"
Bot:  "Great! I've marked 'Buy milk' as complete."
```

## 📋 Quick Facts

| Aspect | Details |
|--------|---------|
| **Endpoint** | `POST /api/{user_id}/chat` |
| **Authentication** | JWT token (Better Auth from Phase 2) |
| **AI Engine** | OpenAI Agents SDK with GPT-4o |
| **MCP Tools** | 5 tools: add_task, list_tasks, complete_task, update_task, delete_task |
| **Database** | Neon PostgreSQL (2 new tables: conversations, messages) |
| **Frontend** | OpenAI ChatKit (hosted, zero-code) |
| **Architecture** | Stateless (all state in database) |
| **Performance** | p95 < 3s response time |

## 🏗️ Architecture at a Glance

```
┌─────────────────┐
│  User (ChatKit) │
└────────┬────────┘
         │ POST /api/{user_id}/chat
         ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (Stateless)        │
│  ┌──────────────────────────────┐   │
│  │ 1. JWT Validation            │   │
│  │ 2. Fetch Conversation History│◄──┼─── PostgreSQL
│  │ 3. Initialize AI Agent       │   │    (conversations,
│  │ 4. Agent → MCP Tools          │   │     messages, tasks)
│  │ 5. Store Messages            │───┼──►
│  │ 6. Return Response           │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

## 🎯 Use Cases

1. **Add Task**: "Remember to call mom tomorrow" → Creates task
2. **List Tasks**: "What's on my todo list?" → Shows all tasks
3. **Complete Task**: "I finished task 5" → Marks task complete
4. **Update Task**: "Change task 3 to 'Buy groceries and fruit'" → Updates title
5. **Delete Task**: "Remove the milk task" → Deletes task

## 📁 File Structure

```
backend/src/
├── models.py                  # ← ADD: Conversation, Message models
├── mcp_tools/                 # ← NEW: 5 MCP tools
│   ├── add_task.py
│   ├── list_tasks.py
│   ├── complete_task.py
│   ├── update_task.py
│   └── delete_task.py
├── ai_agent/                  # ← NEW: OpenAI Agents SDK integration
│   ├── agent.py               # Agent initialization
│   ├── tools.py               # Tool registration
│   └── runner.py              # Agent execution
├── services/                  # ← NEW: Business logic
│   └── conversation_service.py
└── routes/
    └── chat.py                # ← NEW: Chat endpoint

backend/alembic/versions/
└── [timestamp]_add_conversation_message_tables.py  # ← NEW migration

frontend/app/chat/
└── page.tsx                   # ← NEW: ChatKit integration

specs/Phase-3/001-ai-chatbot/
├── spec.md                    # ✅ Requirements
├── plan.md                    # ✅ Architecture
├── research.md                # ✅ Decisions
├── data-model.md              # ✅ Database schema
├── quickstart.md              # ✅ This file
├── contracts/                 # ✅ API & tool specs
│   ├── chat-endpoint.yaml
│   ├── add_task_tool.yaml
│   ├── list_tasks_tool.yaml
│   ├── complete_task_tool.yaml
│   ├── update_task_tool.yaml
│   └── delete_task_tool.yaml
└── tasks.md                   # ⏳ Next: Run /sp.tasks
```

## 🛠️ Development Workflow

### 1. Planning (✅ DONE)
- [x] Spec written (spec.md)
- [x] Plan created (plan.md)
- [x] Research completed (research.md)
- [x] Data model designed (data-model.md)
- [x] Contracts defined (contracts/)
- [x] Quickstart written (you're reading it!)

### 2. Task Breakdown (⏳ NEXT)
```bash
# Run this command to generate tasks.md:
/sp.tasks
```

### 3. Implementation (TDD)
1. **Red**: Write failing tests
2. **Green**: Implement minimal code to pass
3. **Refactor**: Clean up, optimize

### 4. Testing
- Unit tests: Each MCP tool
- Integration tests: Agent + tools
- E2E tests: Full chat flow
- Edge cases: Automatic via `/sp.edge-case-tester`

### 5. Deployment
```bash
# Run migration
alembic upgrade head

# Set environment variables
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://...

# Start server
uvicorn src.main:app --reload
```

## 🔑 Key Contracts

### Chat API Request
```json
POST /api/5/chat
Authorization: Bearer <jwt-token>

{
  "conversation_id": 123,  // Optional: resume existing
  "message": "Add task to buy milk"
}
```

### Chat API Response
```json
{
  "conversation_id": 123,
  "response": "I've added 'Buy milk' to your tasks.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {"user_id": 5, "title": "Buy milk"},
      "result": {"task_id": 42, "title": "Buy milk", "completed": false}
    }
  ]
}
```

### MCP Tool Example (add_task)
```python
def add_task(user_id: int, title: str, description: str | None = None) -> dict:
    """
    Create a new task for the authenticated user.

    Args:
        user_id: Owner of the task (from JWT)
        title: Task title (1-200 chars, required)
        description: Optional task description

    Returns:
        {"task_id": int, "title": str, "description": str | None,
         "completed": bool, "created_at": str}
    """
    # Implementation in backend/src/mcp_tools/add_task.py
```

## 🔒 Security Checklist

- ✅ JWT validation on every request
- ✅ User ID in URL must match token user ID
- ✅ All database queries filter by `user_id`
- ✅ MCP tools require `user_id` parameter
- ✅ Cross-user access returns 404 (not 403) to prevent enumeration
- ✅ SQL injection prevented (SQLModel parameterized queries)
- ✅ Input sanitization before AI processing

## 📊 Database Schema (New Tables)

```sql
-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## 🎓 Learning Resources

### OpenAI Agents SDK
- [Official Documentation](https://platform.openai.com/docs/guides/agents)
- [Tool Calling Guide](https://platform.openai.com/docs/guides/function-calling)

### MCP Protocol
- [MCP SDK Repository](https://github.com/modelcontextprotocol/sdk)
- [MCP Best Practices](https://github.com/modelcontextprotocol/sdk/blob/main/docs/best-practices.md)

### Phase 2 Foundation
- See `docs/reverse-engineered/intelligence-object.md` for reusable patterns:
  - JWT authentication
  - User isolation
  - Connection pooling
  - Transaction management

## 🧪 Testing Examples

### Unit Test (MCP Tool)
```python
def test_add_task_creates_task():
    # Arrange
    user_id = 5
    title = "Buy milk"

    # Act
    result = add_task(user_id=user_id, title=title)

    # Assert
    assert result["title"] == "Buy milk"
    assert result["completed"] is False
    assert "task_id" in result
```

### Integration Test (Agent + Tools)
```python
async def test_agent_adds_task_from_natural_language():
    # Arrange
    user_message = "Add task to buy milk"

    # Act
    response = await run_agent(user_id=5, message=user_message)

    # Assert
    assert "added" in response.lower()
    assert "buy milk" in response.lower()
    # Verify task exists in database
    task = db.query(Task).filter(Task.title == "Buy milk").first()
    assert task is not None
```

### E2E Test (Full Chat Flow)
```python
async def test_chat_endpoint_creates_task(client):
    # Arrange
    headers = {"Authorization": f"Bearer {jwt_token}"}
    payload = {"message": "Add task to buy milk"}

    # Act
    response = await client.post("/api/5/chat", json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "buy milk" in data["response"].lower()
```

## 🚨 Common Pitfalls

### ❌ DON'T: Store State in Memory
```python
# WRONG: Session-based conversation storage
conversation_history = {}  # Lost on server restart

# CORRECT: Database-backed conversation storage
messages = db.query(Message).filter(
    Message.conversation_id == conv_id
).all()
```

### ❌ DON'T: Skip User ID Validation
```python
# WRONG: Trust user_id from URL without validation
tasks = db.query(Task).filter(Task.user_id == path_user_id).all()

# CORRECT: Validate JWT token and match user_id
if authenticated_user_id != path_user_id:
    raise HTTPException(status_code=403, detail="Forbidden")
tasks = db.query(Task).filter(Task.user_id == authenticated_user_id).all()
```

### ❌ DON'T: Expose Raw Errors to Users
```python
# WRONG: Raw exception to user
except Exception as e:
    return {"error": str(e)}  # Exposes internals

# CORRECT: User-friendly message, log full error
except Exception as e:
    logger.error(f"Agent failed: {e}", exc_info=True)
    return {"detail": "An error occurred. Please try again."}
```

## 📈 Performance Targets

| Metric | Target | Optimization |
|--------|--------|--------------|
| Chat response time (p95) | < 3s | Async I/O, connection pooling |
| DB query time (p95) | < 100ms | Indexes on user_id, conversation_id |
| Conversation history fetch | < 100ms | LIMIT 50, index on created_at |
| Concurrent users | 100+ | Stateless architecture, horizontal scaling |

## 🔄 Deployment Checklist

### Pre-Deployment
- [ ] Run Alembic migration: `alembic upgrade head`
- [ ] Verify conversations and messages tables created
- [ ] Set required environment variables (see below)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify Better Auth JWT validation works

### Environment Variables
```bash
# Required
export OPENAI_API_KEY=sk-...
export OPENAI_AGENT_MODEL=gpt-4o
export DATABASE_URL=postgresql://user:password@host:5432/db
export BETTER_AUTH_SECRET=<32-char-minimum-secret>

# Optional Performance Tuning (Production)
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=20
export DB_POOL_TIMEOUT=30
```

### Deployment
- [ ] Deploy backend to staging environment
- [ ] Test chat endpoint with curl/Postman
- [ ] Run load test: `python backend/tests/load_test.py`
- [ ] Verify p95 < 3000ms (performance target)
- [ ] Configure ChatKit domain allowlist (if using frontend)
- [ ] Deploy frontend with ChatKit integration
- [ ] Run smoke tests (add, list, complete, update, delete tasks)
- [ ] Monitor logs for errors and performance metrics

### Production Readiness
- [ ] Structured JSON logging enabled
- [ ] Performance logging active (all services)
- [ ] Connection pool optimized (10 baseline + 20 overflow)
- [ ] Error handling with user-friendly messages
- [ ] Input sanitization active (10,000 char limit)
- [ ] Security audit complete (user isolation, JWT validation)
- [ ] Health endpoint includes pool status: `GET /health`
- [ ] Load testing complete (100 concurrent requests)

## 🎯 Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create implementation breakdown
2. **Review ADR Candidates**: 5 architectural decisions identified in plan.md
3. **Write Tests**: TDD approach - tests first, then implementation
4. **Implement**: Follow task order in tasks.md
5. **Edge Case Testing**: Automatic via `/sp.edge-case-tester` after implementation
6. **Deploy**: Staging environment first, then production

## 📞 Support

- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/](./contracts/)
- **Constitution**: `/.specify/memory/constitution.md`

---

**Quickstart Status**: ✅ Complete
**Ready for**: Task breakdown (`/sp.tasks`)
