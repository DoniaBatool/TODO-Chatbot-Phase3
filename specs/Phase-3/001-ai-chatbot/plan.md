# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-ai-chatbot` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/Phase-3/001-ai-chatbot/spec.md`

## Summary

Build an AI-powered conversational interface for task management using OpenAI Agents SDK and MCP tools. Users interact via natural language to perform CRUD operations on tasks. The system is stateless with database-backed conversation history, enforcing strict user isolation and following TDD practices.

**Technical Approach**: FastAPI backend with OpenAI Agents SDK orchestrating MCP tools. Conversation state persists in PostgreSQL (Neon). Each chat request: authenticate → fetch history → run agent → execute tools → store updates → respond. No server memory; horizontal scaling enabled.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, OpenAI Agents SDK, Official MCP SDK, SQLModel 0.0.14+, python-jose[cryptography], bcrypt
**Storage**: Neon Serverless PostgreSQL (existing from Phase 2)
**Testing**: pytest, pytest-asyncio, httpx for async tests
**Target Platform**: Linux server (Docker container, stateless deployment)
**Project Type**: Web application (backend API + frontend ChatKit)
**Performance Goals**: p95 < 3s response time, 100+ concurrent users, <100ms DB queries
**Constraints**: Stateless architecture (no server memory), user isolation mandatory, 50 message history limit
**Scale/Scope**: 1000+ users, 5 MCP tools, 2 new database tables (Conversation, Message)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### ✅ Stateless Architecture (NON-NEGOTIABLE)
- **Compliance**: All conversation state in database. Server restarts do not lose context.
- **Implementation**: Each request fetches history from DB, processes, stores updates, returns response.
- **Verification**: Integration test simulates server restart mid-conversation.

### ✅ AI-Native Development
- **Compliance**: OpenAI Agents SDK orchestrates all task operations via MCP tools.
- **Implementation**: Agent receives user message + conversation history → interprets intent → calls tools → generates response.
- **Verification**: Agent can add/list/complete/update/delete tasks through natural language.

### ✅ MCP-First Tool Architecture
- **Compliance**: All task operations exposed as MCP tools with typed parameters.
- **Tools**: `add_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task`
- **Implementation**: Each tool is stateless, receives user_id, returns JSON.
- **Verification**: Unit tests for each tool; agent integration tests.

### ✅ Database-Centric State Management
- **Compliance**: Conversations and Messages tables store all chat history.
- **Implementation**:
  - Conversation: `id, user_id, created_at, updated_at`
  - Message: `id, conversation_id, user_id, role, content, created_at`
- **Verification**: Database queries return conversation history after server restart.

### ✅ User Isolation & Security (NON-NEGOTIABLE)
- **Compliance**: JWT authentication on `/api/{user_id}/chat` endpoint. All queries filter by user_id.
- **Implementation**:
  - Endpoint validates JWT token
  - All MCP tools require user_id parameter
  - Database queries: `WHERE user_id = {authenticated_user_id}`
- **Verification**: Security tests verify users cannot access others' data.

### ✅ Natural Language Understanding
- **Compliance**: Agent interprets intents; asks clarifying questions for ambiguity.
- **Implementation**: OpenAI Agents SDK with tool descriptions and few-shot examples.
- **Verification**: Test cases for ambiguous commands ("buy" → "What would you like to buy?").

### ✅ Test-First Development (NON-NEGOTIABLE)
- **Compliance**: TDD workflow: write tests → fail → implement → pass.
- **Implementation**:
  - Unit tests for each MCP tool
  - Integration tests for agent workflows
  - E2E tests for chat endpoint
- **Verification**: All tests pass before merge.

### ✅ OpenAI Agents SDK Integration
- **Compliance**: Use official SDK for agent orchestration.
- **Implementation**: Agent initialized with tools, system prompt, and conversation history.
- **Verification**: Agent successfully calls tools and generates responses.

### ✅ Observability & Debugging
- **Compliance**: Structured logging for all requests, tool calls, and errors.
- **Implementation**: Log user_id, conversation_id, tool_name, parameters, execution_time.
- **Verification**: Logs contain sufficient context for debugging.

## Project Structure

### Documentation (this feature)

```text
specs/Phase-3/001-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-endpoint.yaml
│   ├── add_task_tool.yaml
│   ├── list_tasks_tool.yaml
│   ├── complete_task_tool.yaml
│   ├── update_task_tool.yaml
│   └── delete_task_tool.yaml
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models.py                    # EXTENDED: Add Conversation, Message models
│   ├── db.py                        # EXISTING: Database session management
│   ├── config.py                    # EXISTING: Environment configuration
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py                   # EXISTING: JWT validation
│   │   └── dependencies.py          # EXISTING: get_current_user_id
│   ├── mcp_tools/                   # NEW: MCP tool implementations
│   │   ├── __init__.py
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── update_task.py
│   │   └── delete_task.py
│   ├── ai_agent/                    # NEW: OpenAI Agents SDK integration
│   │   ├── __init__.py
│   │   ├── agent.py                 # Agent initialization and configuration
│   │   ├── tools.py                 # MCP tool registration
│   │   └── runner.py                # Agent execution logic
│   ├── services/                    # NEW: Business logic services
│   │   ├── __init__.py
│   │   └── conversation_service.py  # Conversation CRUD operations
│   └── routes/
│       ├── __init__.py
│       ├── auth.py                  # EXISTING: Login/signup
│       ├── tasks.py                 # EXISTING: Task CRUD (Phase 2)
│       ├── health.py                # EXISTING: Health check
│       └── chat.py                  # NEW: POST /api/{user_id}/chat
├── alembic/
│   └── versions/
│       └── [timestamp]_add_conversation_message_tables.py  # NEW migration
└── tests/
    ├── test_mcp_tools/              # NEW: Unit tests for MCP tools
    │   ├── test_add_task.py
    │   ├── test_list_tasks.py
    │   ├── test_complete_task.py
    │   ├── test_update_task.py
    │   └── test_delete_task.py
    ├── test_ai_agent/               # NEW: Agent integration tests
    │   ├── test_agent_intent.py
    │   └── test_agent_tools.py
    ├── test_routes/
    │   └── test_chat.py             # NEW: E2E tests for chat endpoint
    └── test_services/
        └── test_conversation_service.py  # NEW: Conversation service tests

frontend/
├── .env.example                     # EXTENDED: Add NEXT_PUBLIC_CHATKIT_CONFIG
└── app/
    └── chat/
        └── page.tsx                 # NEW: ChatKit integration page
```

**Structure Decision**: Web application structure (Option 2) selected. Backend API serves stateless chat endpoint. Frontend uses hosted OpenAI ChatKit (configured via domain allowlist, no local hosting required). Existing Phase 2 backend extended with new models, MCP tools, agent logic, and chat route.

## Complexity Tracking

> No constitution violations. All requirements align with stateless, MCP-first, user-isolated architecture.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       | N/A        | N/A                                 |

## Architecture Overview

### High-Level Flow

```
User (ChatKit UI)
    ↓ POST /api/{user_id}/chat { conversation_id?, message }
    ↓ + JWT token in Authorization header
Backend FastAPI
    ↓ 1. Validate JWT → extract user_id from token
    ↓ 2. Validate user_id in URL matches token user_id
    ↓ 3. Fetch conversation history (last 50 messages) from DB
    ↓ 4. Initialize OpenAI Agent with tools + history
    ↓ 5. Agent interprets user message → determines intent
    ↓ 6. Agent calls MCP tools (add_task, list_tasks, etc.)
    ↓    MCP Tools query/modify Tasks table (filtered by user_id)
    ↓ 7. Agent generates natural language response
    ↓ 8. Store user message + assistant response in Messages table
    ↓ 9. Update conversation.updated_at timestamp
    ↓ 10. Return { conversation_id, response, tool_calls[] }
User sees response in ChatKit
```

### Three-Layer Architecture

**Layer 1: API Gateway (FastAPI Routes)**
- Endpoint: `POST /api/{user_id}/chat`
- Responsibilities: JWT validation, request/response formatting, error handling
- Dependencies: auth/dependencies.py (get_current_user_id)

**Layer 2: Business Logic (Services + AI Agent)**
- ConversationService: CRUD for Conversations and Messages
- AI Agent: Intent interpretation, tool orchestration, response generation
- MCP Tools: Stateless functions wrapping task operations

**Layer 3: Data Access (SQLModel ORM)**
- Models: Conversation, Message, Task (existing)
- Database: Neon PostgreSQL with connection pooling
- Migrations: Alembic for schema changes

### Design Patterns

1. **Dependency Injection (FastAPI)**
   - JWT validation via `Depends(get_current_user_id)`
   - Database session via `Depends(get_db)`
   - Reusable across endpoints

2. **Stateless Request Handling**
   - Each request is independent
   - Fetch state from DB → process → store updates → return
   - No server memory (sessions, caches) for critical data

3. **Tool-Based Architecture (MCP)**
   - Each task operation is a separate tool
   - Typed parameters, JSON responses
   - Agent-agnostic (can swap AI provider)

4. **Transaction Management**
   - Database writes in try/commit/rollback blocks
   - Atomic operations (conversation + message creation together)

5. **DTO Separation (Pydantic)**
   - Request DTOs: ChatRequest
   - Response DTOs: ChatResponse
   - Separate from database models

6. **Connection Pooling**
   - SQLModel engine with pool_size=10, max_overflow=20
   - Handles concurrent requests efficiently

## Database Schema Changes

### New Tables

**Conversation**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_conversations_user_id (user_id)
);
```

**Message**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_user_id (user_id),
    INDEX idx_messages_created_at (created_at)
);
```

**Migration Strategy**
- Alembic migration: `add_conversation_message_tables`
- Backward compatible (no changes to existing tables)
- Indexes on user_id, conversation_id, created_at for query performance

### Existing Tables (No Changes)

**Task** (from Phase 2)
```sql
-- No schema changes required
-- MCP tools will query this table with user_id filtering
```

**User** (from Phase 2)
```sql
-- No schema changes required
-- JWT authentication uses existing user table
```

## MCP Tool Specifications

### Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

**Parameters**:
```python
{
    "user_id": int,          # Required: Owner of the task
    "title": str,            # Required: Task title (1-200 chars)
    "description": str | None  # Optional: Task description
}
```

**Returns**:
```python
{
    "task_id": int,
    "title": str,
    "description": str | None,
    "completed": bool,  # Always False for new tasks
    "created_at": str   # ISO 8601 timestamp
}
```

**Error Cases**:
- Invalid user_id → "User not found"
- Missing title → "Title is required"
- Title too long → "Title must be 200 characters or less"

### Tool 2: list_tasks

**Purpose**: Retrieve tasks for the authenticated user with optional filtering

**Parameters**:
```python
{
    "user_id": int,           # Required: Owner of the tasks
    "status": str | None      # Optional: "all" | "pending" | "completed"
}
```

**Returns**:
```python
{
    "tasks": [
        {
            "task_id": int,
            "title": str,
            "description": str | None,
            "completed": bool,
            "created_at": str
        },
        ...
    ],
    "count": int
}
```

**Error Cases**:
- Invalid user_id → "User not found"
- Invalid status value → "Status must be 'all', 'pending', or 'completed'"

### Tool 3: complete_task

**Purpose**: Mark a task as completed

**Parameters**:
```python
{
    "user_id": int,   # Required: Owner of the task
    "task_id": int    # Required: ID of task to complete
}
```

**Returns**:
```python
{
    "task_id": int,
    "title": str,
    "completed": bool,  # Always True after completion
    "updated_at": str
}
```

**Error Cases**:
- Task not found → "Task not found"
- Task belongs to different user → "Task not found" (security: don't reveal existence)
- Task already completed → Idempotent success (no error)

### Tool 4: update_task

**Purpose**: Update task title and/or description

**Parameters**:
```python
{
    "user_id": int,           # Required: Owner of the task
    "task_id": int,           # Required: ID of task to update
    "title": str | None,      # Optional: New title
    "description": str | None # Optional: New description
}
```

**Returns**:
```python
{
    "task_id": int,
    "title": str,
    "description": str | None,
    "completed": bool,
    "updated_at": str
}
```

**Error Cases**:
- Task not found → "Task not found"
- Task belongs to different user → "Task not found"
- No fields provided → "At least one field (title or description) must be provided"

### Tool 5: delete_task

**Purpose**: Permanently delete a task

**Parameters**:
```python
{
    "user_id": int,   # Required: Owner of the task
    "task_id": int    # Required: ID of task to delete
}
```

**Returns**:
```python
{
    "task_id": int,
    "deleted": bool,  # Always True
    "title": str      # Title of deleted task for confirmation
}
```

**Error Cases**:
- Task not found → "Task not found"
- Task belongs to different user → "Task not found"

## AI Agent Configuration

### System Prompt

```
You are a helpful task management assistant. Users can ask you to:
- Add tasks (e.g., "Add task to buy milk")
- View tasks (e.g., "Show my tasks", "What's pending?")
- Complete tasks (e.g., "Mark task 5 as done", "I finished buying milk")
- Update tasks (e.g., "Change task 3 to 'Buy groceries'")
- Delete tasks (e.g., "Delete task 7", "Remove the milk task")

When user intent is unclear, ask clarifying questions.
Always confirm actions with friendly, natural language.
Use the provided tools to perform task operations.
```

### Tool Descriptions

```python
tools = [
    {
        "name": "add_task",
        "description": "Create a new task. Use when user wants to add, create, or remember something.",
        "parameters": {...}
    },
    {
        "name": "list_tasks",
        "description": "List tasks with optional filtering. Use when user asks to see, show, or list tasks.",
        "parameters": {...}
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed. Use when user says they finished or completed a task.",
        "parameters": {...}
    },
    {
        "name": "update_task",
        "description": "Update task title or description. Use when user wants to change, edit, or modify a task.",
        "parameters": {...}
    },
    {
        "name": "delete_task",
        "description": "Delete a task permanently. Use when user wants to remove or delete a task.",
        "parameters": {...}
    }
]
```

### Conversation History Format

```python
messages = [
    {"role": "user", "content": "Add task to buy milk"},
    {"role": "assistant", "content": "I've added 'Buy milk' to your tasks."},
    {"role": "user", "content": "Show my tasks"},
    {"role": "assistant", "content": "You have 1 pending task:\n1. Buy milk"},
    ...
]
# Limit to last 50 messages per request
```

## API Contract

### Endpoint: POST /api/{user_id}/chat

**Authentication**: JWT token in `Authorization: Bearer <token>` header

**Request**:
```json
{
    "conversation_id": 123,  // Optional: Resume existing conversation
    "message": "Add task to buy milk"
}
```

**Response** (Success - 200):
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

**Response** (Error - 401 Unauthorized):
```json
{
    "detail": "Invalid or expired token"
}
```

**Response** (Error - 403 Forbidden):
```json
{
    "detail": "User ID in URL does not match authenticated user"
}
```

**Response** (Error - 500 Internal Server Error):
```json
{
    "detail": "An error occurred while processing your request. Please try again."
}
```

## Error Handling Strategy

### User-Facing Errors (Graceful)
- **Agent Timeout**: "I'm having trouble processing your request. Please try again."
- **Tool Failure**: "I couldn't complete that action. Please try again or check your task list."
- **Ambiguous Input**: "I'm not sure what you mean. Could you clarify?"

### Internal Errors (Logged, Not Exposed)
- OpenAI API errors → Log full error, return generic message to user
- Database connection errors → Retry with exponential backoff, log failure
- MCP tool exceptions → Log stack trace, return user-friendly message

### Security Errors
- JWT validation failure → 401 Unauthorized
- User ID mismatch → 403 Forbidden
- SQL injection attempt → Sanitize input, log security event

## Performance Optimization

### Database Query Optimization
- Index on `user_id` for all tables (conversations, messages, tasks)
- Index on `conversation_id` for messages table
- Index on `created_at` for message ordering
- Limit conversation history to 50 messages (LIMIT clause)

### Connection Pooling
- SQLModel engine: `pool_size=10, max_overflow=20`
- Reuse connections across requests
- Handle concurrent requests efficiently

### Caching Strategy
- **NO caching for critical data** (violates stateless principle)
- OpenAI API responses NOT cached (conversation-specific)
- Database queries executed fresh each request

### Response Time Targets
- Database query: <100ms (p95)
- OpenAI Agent execution: <2s (p95)
- Total request: <3s (p95)

## Testing Strategy

### Unit Tests (pytest)
- Each MCP tool: happy path, error cases, edge cases
- ConversationService: CRUD operations, user isolation
- Database models: field validation, relationships

### Integration Tests
- Agent + MCP tools: Verify agent can call tools correctly
- Agent intent interpretation: Test natural language → tool mapping
- Database transactions: Verify atomic operations

### E2E Tests (httpx async client)
- POST /api/{user_id}/chat: Full request/response cycle
- Authentication: JWT validation, user ID mismatch
- Conversation continuity: Resume conversation after "restart"
- Multi-turn conversations: Context retention across messages

### Edge Case Tests (Automatic via /sp.edge-case-tester)
- Empty message
- Extremely long message (>1000 chars)
- Ambiguous commands
- Non-existent task operations
- Concurrent requests
- Agent timeout
- Special characters and emojis
- Cross-user access attempts

### Performance Tests
- Load test: 100 concurrent users
- Response time: p95 < 3s verification
- Database connection pool under load

### Security Tests
- JWT validation: Invalid token, expired token
- User isolation: Verify users cannot access others' data
- Input sanitization: SQL injection prevention
- Authorization: User ID mismatch between token and URL

## Deployment Considerations

### Environment Variables
```bash
# Existing from Phase 2
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=...
JWT_ALGORITHM=HS256

# New for Phase 3
OPENAI_API_KEY=sk-...
OPENAI_AGENT_MODEL=gpt-4o  # Or gpt-4-turbo, etc.
CHATKIT_DOMAIN_ALLOWLIST=yourdomain.com
```

### Migration Execution
```bash
# Run Alembic migration to create conversation and message tables
alembic upgrade head
```

### Stateless Deployment
- Docker container with no persistent storage
- Horizontal scaling: Multiple instances behind load balancer
- Database connection pooling handles concurrent requests
- No session state in server memory

### Monitoring & Observability
- Structured logging: JSON format with user_id, conversation_id, tool_calls
- Metrics: Request count, response time, error rate, tool invocation count
- Alerts: p95 > 3s, error rate > 1%, database connection pool exhausted

## Risks & Mitigation

### Risk 1: OpenAI API Rate Limits
- **Mitigation**: Implement exponential backoff, fallback to clarification prompt
- **Monitoring**: Track API usage, set up alerts for approaching limits

### Risk 2: Agent Misinterprets Intent
- **Mitigation**: Improve system prompt with examples, ask clarifying questions
- **Monitoring**: Log intent mismatches, collect user feedback

### Risk 3: Database Performance Degradation
- **Mitigation**: Indexes on user_id, conversation_id, created_at; limit history to 50 messages
- **Monitoring**: Database query time metrics, slow query log

### Risk 4: Cross-User Data Leakage
- **Mitigation**: Mandatory user_id filtering on all queries, security tests
- **Monitoring**: Audit logs for suspicious access patterns

### Risk 5: Agent Timeout Under Load
- **Mitigation**: Async request handling, timeout limits, graceful error messages
- **Monitoring**: Track agent execution time, timeout frequency

## Architecture Decision Records (ADRs)

### ADR Candidates (To Be Created After Plan Approval)

1. **OpenAI Agents SDK vs LangChain**
   - Decision: Use OpenAI Agents SDK
   - Rationale: Official SDK, direct integration, simpler for this use case
   - Alternatives: LangChain (more complex, overkill for our needs)

2. **Stateless Conversation Management**
   - Decision: Store all conversation history in database, fetch on each request
   - Rationale: Enables horizontal scaling, aligns with constitution
   - Alternatives: Server-side sessions (violates stateless principle)

3. **MCP Tool Architecture**
   - Decision: Separate tool per task operation (add, list, complete, update, delete)
   - Rationale: Clear separation of concerns, easy to test, agent-friendly
   - Alternatives: Single "task_manager" tool (too complex, harder to debug)

4. **Conversation History Limit (50 Messages)**
   - Decision: Fetch last 50 messages per request
   - Rationale: Balance between context and performance; typical conversations < 50 messages
   - Alternatives: Unlimited (performance risk), 20 messages (insufficient context)

5. **JWT Authentication at Chat Endpoint**
   - Decision: Reuse existing Better Auth JWT validation
   - Rationale: Consistency with Phase 2, proven security model
   - Alternatives: API keys (less secure), OAuth (overkill)

**Suggestion**: After plan approval, run `/sp.adr` for each decision above to document rationale and tradeoffs.

## Next Steps

1. **Review this plan**: Verify architecture aligns with requirements
2. **Create ADRs**: Document significant decisions (5 ADRs suggested above)
3. **Generate tasks**: Run `/sp.tasks` to create implementation breakdown
4. **TDD Implementation**: Write tests → fail → implement → pass
5. **Deploy & Monitor**: Deploy to staging, verify performance targets

---

**Plan Status**: Ready for review and tasks generation
**Estimated Complexity**: Medium-High (new tables, AI integration, 5 MCP tools, agent setup)
**Constitution Compliance**: ✅ All gates passed
