# Research: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2025-12-30
**Status**: Completed

## Research Overview

This document captures all research findings, technology evaluations, and decisions made during the planning phase for the AI-powered todo chatbot feature.

## Research Questions & Findings

### 1. AI Agent Framework Selection

**Question**: Which AI agent framework should we use for orchestrating task management operations?

**Options Evaluated**:

1. **OpenAI Agents SDK** ⭐ SELECTED
   - **Pros**:
     - Official SDK from OpenAI
     - Direct integration with GPT-4
     - Built-in tool calling support
     - Simpler API, less boilerplate
     - Active development and support
   - **Cons**:
     - Vendor lock-in to OpenAI
     - Fewer community extensions
   - **Best Use Case**: Straightforward agent workflows with tool orchestration

2. **LangChain**
   - **Pros**:
     - Provider-agnostic (supports multiple LLMs)
     - Rich ecosystem of integrations
     - Advanced features (memory, chains, retrieval)
   - **Cons**:
     - More complex setup
     - Steeper learning curve
     - Overkill for simple tool orchestration
   - **Best Use Case**: Complex workflows with multiple LLMs, RAG, advanced memory

3. **Custom Implementation**
   - **Pros**:
     - Full control
     - No external dependencies
   - **Cons**:
     - Requires parsing tool calls manually
     - More code to maintain
     - Reinventing the wheel
   - **Best Use Case**: Highly specific requirements not met by existing frameworks

**Decision**: Use OpenAI Agents SDK

**Rationale**:
- Constitution mandates OpenAI Agents SDK (Phase 3 principle VIII)
- Our use case is straightforward: interpret natural language → call MCP tools → generate response
- No need for multi-LLM support or advanced RAG features
- Simpler codebase with official SDK
- Faster development time

**References**:
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- Constitution Section VIII: OpenAI Agents SDK Integration

---

### 2. MCP Tool Architecture

**Question**: How should we structure MCP tools for task operations?

**Options Evaluated**:

1. **Single Tool with Action Parameter** ("task_manager")
   - Structure: `task_manager(action="add", user_id=5, title="...")`
   - **Pros**: Fewer tools to register
   - **Cons**: Complex parameter validation, harder to test, less clear to agent

2. **Separate Tool Per Operation** ⭐ SELECTED
   - Structure: `add_task(user_id, title)`, `list_tasks(user_id, status)`, etc.
   - **Pros**: Clear separation, easy to test, agent-friendly descriptions, simpler parameters
   - **Cons**: More tools to register (5 tools vs 1)

3. **Hybrid Approach** (CRUD tool + specialized tools)
   - Structure: `task_crud(action)` + `search_tasks(query)`
   - **Pros**: Balance between simplicity and specialization
   - **Cons**: Inconsistent pattern, still complex

**Decision**: Separate tool per operation (5 tools total)

**Rationale**:
- Constitution mandates MCP-First Tool Architecture (Principle III)
- Clear tool descriptions improve agent intent recognition
- Easier to write unit tests (one test file per tool)
- Simpler parameter validation (each tool has focused parameters)
- Aligns with Phase 2 reusable intelligence skills

**Tools Defined**:
1. `add_task(user_id, title, description?)`
2. `list_tasks(user_id, status?)`
3. `complete_task(user_id, task_id)`
4. `update_task(user_id, task_id, title?, description?)`
5. `delete_task(user_id, task_id)`

**References**:
- [MCP SDK Best Practices](https://github.com/modelcontextprotocol/sdk)
- Constitution Section III: MCP-First Tool Architecture

---

### 3. Conversation State Management

**Question**: How should we store and retrieve conversation history?

**Options Evaluated**:

1. **In-Memory Sessions**
   - Store conversation history in server memory (e.g., Redis, dict)
   - **Pros**: Fast retrieval, no DB queries
   - **Cons**: Violates stateless architecture, lost on server restart, doesn't scale horizontally

2. **Database-Backed History** ⭐ SELECTED
   - Store all messages in PostgreSQL Conversations + Messages tables
   - **Pros**: Stateless, survives restarts, enables horizontal scaling, single source of truth
   - **Cons**: DB query on each request

3. **Hybrid (DB + Cache)**
   - Store in DB, cache recent conversations in Redis
   - **Pros**: Performance optimization
   - **Cons**: Cache invalidation complexity, violates "no in-memory state for critical data"

**Decision**: Database-backed history (no caching)

**Rationale**:
- Constitution mandates stateless architecture (Principle I - NON-NEGOTIABLE)
- Constitution mandates database-centric state (Principle IV)
- Server restarts MUST NOT lose conversation context
- With proper indexing, DB queries are <100ms (acceptable for p95 < 3s target)
- Conversation history limited to 50 messages (query performance acceptable)

**Database Schema**:
- `conversations` table: `id, user_id, created_at, updated_at`
- `messages` table: `id, conversation_id, user_id, role, content, created_at`
- Indexes: `user_id`, `conversation_id`, `created_at`

**References**:
- Constitution Section I: Stateless Architecture
- Constitution Section IV: Database-Centric State Management

---

### 4. Conversation History Limit

**Question**: How many messages should we include in agent context?

**Options Evaluated**:

| Option | Pros | Cons | Performance | Context Quality |
|--------|------|------|-------------|-----------------|
| 10 messages | Fast queries | Insufficient context | Excellent (<50ms) | Poor |
| 20 messages | Good balance? | Still limited | Very Good (<75ms) | Fair |
| 50 messages ⭐ | Rich context | More DB load | Good (<100ms) | Excellent |
| 100 messages | Maximum context | Slow queries | Fair (~200ms) | Excellent |
| Unlimited | Complete history | Query timeout risk | Poor (>500ms) | Excellent |

**Decision**: 50 messages (last 50 in conversation)

**Rationale**:
- Typical task management conversations are <30 messages
- 50 messages provide sufficient context for complex conversations
- Database query with LIMIT 50 and index on created_at: ~100ms (meets p95 target)
- Balances context quality with performance
- OpenAI token limits (8k-128k tokens) easily accommodate 50 messages

**Query Optimization**:
```sql
SELECT * FROM messages
WHERE conversation_id = $1 AND user_id = $2
ORDER BY created_at DESC
LIMIT 50
```
- Index on (conversation_id, created_at) → fast retrieval
- User_id check ensures security

**References**:
- [PostgreSQL Query Performance](https://www.postgresql.org/docs/current/indexes.html)
- OpenAI API Token Limits

---

### 5. User Isolation Strategy

**Question**: How do we prevent users from accessing others' conversations and tasks?

**Options Evaluated**:

1. **Application-Level Filtering**
   - Add `WHERE user_id = {authenticated_user}` to all queries
   - **Pros**: Simple, flexible
   - **Cons**: Risk of missing filter in one query = data leakage

2. **Row-Level Security (RLS) in PostgreSQL** ⭐ BEST PRACTICE (Future Enhancement)
   - Database enforces user_id filtering automatically
   - **Pros**: Database-level guarantee, impossible to bypass
   - **Cons**: Complex setup, Neon may have limitations

3. **Application + Tests** ⭐ SELECTED FOR PHASE 3
   - Application-level WHERE clauses + comprehensive security tests
   - **Pros**: Simpler implementation, testable
   - **Cons**: Relies on correct implementation

**Decision**: Application-level filtering with mandatory user_id parameter and security tests

**Rationale**:
- Constitution mandates user isolation (Principle V - NON-NEGOTIABLE)
- All MCP tools MUST receive user_id as required parameter
- All database queries MUST filter by user_id
- Security tests verify no cross-user access
- RLS is future enhancement (Phase 4+)

**Implementation Pattern**:
```python
# Every query MUST include user_id filter
tasks = db.query(Task).filter(Task.user_id == authenticated_user_id).all()

# MCP tools signature
def add_task(user_id: int, title: str, description: str | None = None):
    # user_id is REQUIRED parameter
    ...
```

**Security Tests**:
- Attempt to access another user's conversation → 404 Not Found
- Attempt to modify another user's task via tool → Task Not Found
- JWT token for user A + URL /api/B/chat → 403 Forbidden

**References**:
- Constitution Section V: User Isolation & Security
- Phase 2 Intelligence Object: User Isolation with Ownership Enforcement

---

### 6. Error Handling for AI Agent

**Question**: How should we handle agent failures and timeouts?

**Options Evaluated**:

1. **Silent Failure (Return Empty Response)**
   - **Pros**: Simple
   - **Cons**: Confusing to users, no feedback

2. **Retry with Exponential Backoff**
   - **Pros**: Handles transient failures
   - **Cons**: Increased latency, may still fail

3. **Graceful Degradation with User-Friendly Message** ⭐ SELECTED
   - **Pros**: Clear user feedback, maintains trust
   - **Cons**: Doesn't auto-recover

**Decision**: Graceful degradation with friendly error messages

**Rationale**:
- Constitution mandates graceful error handling (FR-010)
- User experience: prefer clear communication over silent failures
- Logging: all errors logged with full context for debugging
- Never expose raw exceptions to users

**Error Message Examples**:
- Agent timeout → "I'm having trouble processing your request. Please try again."
- Tool failure → "I couldn't complete that action. Please try again or check your task list."
- Ambiguous input → "I'm not sure what you mean. Could you clarify?"

**Logging Strategy**:
```python
logger.error(
    "Agent execution failed",
    extra={
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message": user_message,
        "error": str(exception),
        "traceback": traceback.format_exc()
    }
)
```

**References**:
- Constitution Section IX: Observability & Debugging
- Spec FR-010: Graceful error handling

---

### 7. Performance Optimization Strategy

**Question**: How do we meet p95 < 3s response time target with AI agent + database queries?

**Breakdown**:
- Database query (fetch history): ~100ms
- OpenAI agent execution: ~1.5-2s
- MCP tool execution: ~50-100ms
- Database write (store messages): ~50ms
- Total: ~1.7-2.3s (within target)

**Optimizations**:

1. **Database Indexing**
   - Index on user_id (all tables)
   - Index on conversation_id (messages)
   - Index on created_at (messages) for ordering
   - Expected: <100ms for history fetch

2. **Connection Pooling**
   - SQLModel engine: pool_size=10, max_overflow=20
   - Reuse connections across requests
   - Handles 100+ concurrent users

3. **Async Request Handling**
   - FastAPI async endpoints
   - Non-blocking I/O for database and OpenAI API calls

4. **Agent Model Selection**
   - GPT-4o: Fastest, good quality (~1.5s)
   - GPT-4-turbo: Slower but higher quality (~2s)
   - Decision: Start with GPT-4o, monitor quality

5. **Conversation History Limit**
   - 50 messages max (reduces query time and token count)

**Decision**: Implement all 5 optimizations

**Rationale**:
- Constitution mandates p95 < 3s (FR-015)
- Multi-faceted approach addresses all bottlenecks
- Database optimizations proven in Phase 2
- Agent model tunable via environment variable

**Monitoring**:
- Track p95 response time in production
- Alert if p95 > 2.5s (buffer before hitting 3s limit)

**References**:
- Constitution Non-Functional Requirements: Performance Standards
- Phase 2 Intelligence Object: Connection Pooling

---

### 8. Frontend Integration (OpenAI ChatKit)

**Question**: How should the frontend integrate with the chat API?

**Options Evaluated**:

1. **Custom React Chat UI**
   - Build from scratch with React components
   - **Pros**: Full customization
   - **Cons**: Development time, accessibility concerns, mobile optimization

2. **OpenAI ChatKit (Hosted)** ⭐ SELECTED
   - Use hosted ChatKit with domain allowlist configuration
   - **Pros**: Zero frontend code, automatic mobile support, accessibility built-in
   - **Cons**: Limited customization, requires domain allowlist setup

3. **Third-Party Chat Libraries** (e.g., react-chat-widget)
   - Use existing React chat libraries
   - **Pros**: Faster than custom, some customization
   - **Cons**: Not AI-native, may need adapters

**Decision**: OpenAI ChatKit (hosted)

**Rationale**:
- Constitution mandates ChatKit (Technology Stack Standards)
- Zero frontend development required (focus on backend)
- Automatic mobile optimization
- Built-in accessibility features
- Easy integration (just configure domain allowlist)

**Implementation**:
- Frontend: Single page at `/app/chat/page.tsx`
- ChatKit config: Point to backend `/api/{user_id}/chat` endpoint
- Authentication: Pass JWT token in Authorization header

**Configuration**:
```env
NEXT_PUBLIC_CHATKIT_CONFIG={"endpoint": "https://api.yourdomain.com/api/{user_id}/chat", "domain": "yourdomain.com"}
```

**References**:
- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- Constitution Required Technologies

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | 0.104+ | Async support, proven in Phase 2 |
| AI Agent SDK | OpenAI Agents SDK | Latest | Constitution mandate, official SDK |
| MCP Tools | Official MCP SDK | Latest | Constitution mandate, standard protocol |
| ORM | SQLModel | 0.0.14+ | Type-safe, proven in Phase 2 |
| Database | Neon PostgreSQL | Serverless | Hackathon requirement, serverless |
| Authentication | Better Auth (JWT) | Existing | Phase 2 foundation, proven |
| Frontend | OpenAI ChatKit | Hosted | Constitution mandate, zero-code UI |
| Testing | pytest, httpx | Latest | Async support, proven in Phase 2 |

---

## Best Practices Identified

### 1. MCP Tool Development
- **Single Responsibility**: Each tool does one thing well
- **Typed Parameters**: Use Pydantic models for validation
- **User ID Mandatory**: Every tool requires user_id parameter
- **Idempotency**: Where possible (e.g., completing already-completed task = no-op)
- **Error Messages**: User-friendly, never raw exceptions
- **Testing**: Unit tests for each tool (happy path + errors)

### 2. AI Agent Prompt Engineering
- **System Prompt**: Clear role definition and capabilities
- **Tool Descriptions**: Specific use cases and trigger phrases
- **Few-Shot Examples**: Include in system prompt for common patterns
- **Clarification Strategy**: Ask questions for ambiguous input
- **Confirmation Pattern**: Always confirm actions ("I've added 'Buy milk' to your tasks")

### 3. Database Operations
- **Atomic Transactions**: Wrap conversation + message creation together
- **Index Strategy**: user_id, conversation_id, created_at
- **Query Limits**: LIMIT 50 for conversation history
- **Connection Pooling**: Reuse connections, handle concurrency
- **User Filtering**: ALWAYS include WHERE user_id = {authenticated_user}

### 4. Security
- **JWT Validation**: Every request validates token
- **User ID Matching**: Token user_id MUST match URL user_id
- **Input Sanitization**: Prevent SQL injection (SQLModel handles this)
- **Error Exposure**: Never show raw errors to users
- **Audit Logging**: Log all user actions with user_id context

---

## Integration Patterns

### Pattern 1: Stateless Request Cycle

```
1. Request arrives: POST /api/{user_id}/chat
2. Validate JWT → extract authenticated_user_id
3. Validate URL user_id == authenticated_user_id
4. Fetch conversation history from DB (last 50 messages)
5. Initialize agent with tools + history
6. Agent processes user message → calls MCP tools
7. MCP tools query/modify database (filtered by user_id)
8. Agent generates response
9. Store user message + assistant response in DB
10. Return response to client
11. Server forgets everything (stateless)
```

### Pattern 2: MCP Tool Execution

```
1. Agent decides to call tool (e.g., add_task)
2. Agent constructs parameters: {"user_id": 5, "title": "Buy milk"}
3. MCP SDK validates parameters against schema
4. Tool function executes: database INSERT with user_id
5. Tool returns result: {"task_id": 42, "title": "Buy milk", ...}
6. Agent receives result
7. Agent incorporates result into response: "I've added 'Buy milk' to your tasks."
```

### Pattern 3: Error Recovery

```
1. Agent encounters error (e.g., OpenAI API timeout)
2. Log error with full context (user_id, conversation_id, stack trace)
3. Return user-friendly message: "I'm having trouble processing your request."
4. Preserve conversation state (error doesn't corrupt DB)
5. User retries → fresh request cycle
```

---

## Alternatives Considered & Rejected

| Decision Point | Rejected Alternative | Why Rejected |
|---------------|---------------------|--------------|
| Agent Framework | LangChain | Too complex for simple tool orchestration |
| Tool Architecture | Single "task_manager" tool | Harder to test, less clear to agent |
| State Management | In-memory sessions | Violates stateless principle |
| History Limit | Unlimited messages | Query performance risk |
| User Isolation | Row-Level Security (RLS) | Overkill for Phase 3, future enhancement |
| Error Handling | Silent failures | Poor user experience |
| Frontend | Custom React UI | Development time, ChatKit is better |

---

## Open Questions & Future Research

### Phase 3 Scope (No Action Required)
- ✅ All decisions made for Phase 3 implementation

### Future Enhancements (Phase 4+)
1. **Multi-language Support**: Research NLP for non-English languages
2. **Voice Commands**: Investigate speech-to-text integration
3. **Advanced Context**: Research RAG for retrieving past conversations
4. **Proactive Suggestions**: Research how agent can suggest tasks based on patterns
5. **Row-Level Security**: Implement database-level user isolation

---

## References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- [MCP SDK Best Practices](https://github.com/modelcontextprotocol/sdk)
- [PostgreSQL Query Optimization](https://www.postgresql.org/docs/current/indexes.html)
- [FastAPI Async Patterns](https://fastapi.tiangolo.com/async/)
- Phase 2 Documentation: `/docs/reverse-engineered/intelligence-object.md`
- Project Constitution: `/.specify/memory/constitution.md`

---

**Research Status**: ✅ Complete
**All Decisions Made**: Yes
**Ready for Phase 1**: Yes (data-model.md, contracts, quickstart.md)
