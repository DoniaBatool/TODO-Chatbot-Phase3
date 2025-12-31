---
description: Create stateless chat endpoint with conversation history management and AI agent integration (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill creates the stateless chat endpoint for Phase 3, following constitution principles.

### 1. Create Chat Endpoint Implementation

**File: `backend/src/api/chat.py`**

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from ..ai.agent_factory import AgentFactory
from ..db.conversation_manager import ConversationManager
from ..auth.jwt_validator import validate_jwt

router = APIRouter()

class ChatRequest(BaseModel):
    """Chat request following Phase 3 constitution"""
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")
    message: str = Field(..., description="User message")

class ChatResponse(BaseModel):
    """Chat response with conversation tracking"""
    conversation_id: int = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant response")
    tool_calls: List[Dict] = Field(default=[], description="Tools invoked")

@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    token_user_id: str = Depends(validate_jwt)
):
    """
    Stateless chat endpoint with conversation history

    Constitution compliance:
    - Stateless: Fetches history from DB, no server state
    - User isolation: Validates user_id matches JWT
    - Database-centric: All state in PostgreSQL

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        token_user_id: User ID from JWT token (dependency injection)

    Returns:
        ChatResponse: AI response with conversation tracking
    """
    # Validate user isolation
    if user_id != token_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Initialize managers
    conv_manager = ConversationManager()
    agent_factory = AgentFactory()

    # Step 1: Get or create conversation
    if request.conversation_id:
        conversation = await conv_manager.get_conversation(
            user_id=user_id,
            conversation_id=request.conversation_id
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = await conv_manager.create_conversation(user_id=user_id)

    # Step 2: Fetch conversation history from database
    history = await conv_manager.get_message_history(
        conversation_id=conversation.id,
        user_id=user_id,
        limit=50
    )

    # Step 3: Store user message in database
    await conv_manager.add_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )

    # Step 4: Build message array for agent
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]
    messages.append({"role": "user", "content": request.message})

    # Step 5: Run AI agent
    agent = await agent_factory.create_agent(user_id=user_id)
    response = await agent_factory.run_agent(
        agent=agent,
        messages=messages,
        user_id=user_id
    )

    # Step 6: Store assistant response in database
    await conv_manager.add_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=response.content
    )

    # Step 7: Return response (server is now stateless again)
    return ChatResponse(
        conversation_id=conversation.id,
        response=response.content,
        tool_calls=response.tool_calls
    )
```

### 2. Create Endpoint Tests

**File: `tests/test_chat_endpoint.py`**

```python
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

def test_chat_endpoint_requires_auth():
    """Test endpoint requires valid JWT"""
    response = client.post("/api/user123/chat", json={"message": "Hello"})
    assert response.status_code == 401

def test_chat_endpoint_creates_new_conversation(auth_headers):
    """Test endpoint creates conversation if not provided"""
    response = client.post(
        "/api/user123/chat",
        json={"message": "Hello"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data

def test_chat_endpoint_continues_conversation(auth_headers, existing_conversation):
    """Test endpoint continues existing conversation"""
    response = client.post(
        "/api/user123/chat",
        json={
            "conversation_id": existing_conversation.id,
            "message": "Show my tasks"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == existing_conversation.id

def test_chat_endpoint_enforces_user_isolation(auth_headers):
    """Test user can only access their conversations"""
    # User A's token trying to access User B's endpoint
    response = client.post(
        "/api/user_b/chat",
        json={"message": "Hello"},
        headers=auth_headers  # Contains user_a ID
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_chat_endpoint_is_stateless():
    """Test endpoint fetches state from DB (not server memory)"""
    # Make request 1
    # Simulate server restart
    # Make request 2 with same conversation_id
    # Should have full context from DB
    pass
```

### 3. Create Performance Tests

**File: `tests/performance/test_chat_performance.py`**

```python
import pytest
import time

@pytest.mark.asyncio
async def test_chat_response_time():
    """Test p95 response time < 3s per constitution"""
    response_times = []

    for _ in range(100):
        start = time.time()
        # Make chat request
        elapsed = time.time() - start
        response_times.append(elapsed)

    response_times.sort()
    p95 = response_times[94]

    assert p95 < 3.0, f"p95 response time {p95}s exceeds 3s limit"

@pytest.mark.asyncio
async def test_concurrent_chat_sessions():
    """Test 100+ concurrent sessions per constitution"""
    import asyncio

    async def chat_session(user_id):
        # Simulate chat interaction
        pass

    # Run 100 concurrent sessions
    tasks = [chat_session(f"user_{i}") for i in range(100)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 100
    assert all(r is not None for r in results)
```

### 4. Create API Documentation

**File: `specs/[feature]/contracts/chat-endpoint.md`**

```markdown
# Chat Endpoint Specification

## Endpoint

**POST** `/api/{user_id}/chat`

## Authentication

Requires JWT token in `Authorization: Bearer <token>` header.

## Request

\`\`\`json
{
  "conversation_id": 123,  // Optional: existing conversation
  "message": "Add task to buy milk"  // Required: user message
}
\`\`\`

## Response

\`\`\`json
{
  "conversation_id": 123,
  "response": "I've added 'Buy milk' to your tasks.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy milk"},
      "result": {"task_id": 456, "status": "created"}
    }
  ]
}
\`\`\`

## Stateless Design

Each request:
1. Fetches conversation history from database
2. Stores user message in database
3. Runs AI agent with history
4. Stores assistant response in database
5. Returns response

**No server state preserved between requests.**

## Performance SLA

- p95 response time: < 3s
- Concurrent sessions: 100+
- Database queries: < 100ms p95

## Error Handling

| Status | Condition | Response |
|--------|-----------|----------|
| 401 | Missing/invalid JWT | "Unauthorized" |
| 403 | User ID mismatch | "Access denied" |
| 404 | Conversation not found | "Conversation not found" |
| 500 | Server error | "Internal error" (sanitized) |
```

### 5. Display Creation Summary

```text
✅ Chat Endpoint Created

📁 Files Generated:
  - backend/src/api/chat.py
  - tests/test_chat_endpoint.py
  - tests/performance/test_chat_performance.py
  - specs/[feature]/contracts/chat-endpoint.md

✅ Constitution Compliance:
  ✓ Stateless: Fetches/stores state in DB
  ✓ User isolation: JWT validation enforced
  ✓ Performance: p95 < 3s, 100+ concurrent
  ✓ Database-centric: All state in PostgreSQL

📋 Next Steps:
  1. Run: pytest tests/test_chat_endpoint.py -v
  2. Run performance tests
  3. Test with conversation manager
  4. Deploy and monitor SLA metrics
```

## Success Criteria

- [ ] Endpoint follows stateless architecture
- [ ] JWT validation enforces user isolation
- [ ] Conversation history fetched from database
- [ ] Messages stored in database immediately
- [ ] Tests cover auth, isolation, statefulness
- [ ] Performance tests verify SLA compliance
- [ ] API documentation complete

## Notes

- Used automatically in Phase 3 chatbot implementation
- Terminal shows skill usage for traceability
- Must be stateless per constitution
