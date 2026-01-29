# API Endpoint Contracts

**Feature**: 001-robust-ai-assistant
**Purpose**: Define HTTP API contracts for chat endpoints
**Date**: 2026-01-27

---

## POST /api/chat

**Purpose**: Send a message to the AI assistant and receive a response

**Authentication**: Required (JWT bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body Schema**:
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": ["integer", "null"],
      "description": "Existing conversation ID to continue, or null to start new conversation"
    },
    "message": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000,
      "description": "User's message to the assistant"
    }
  },
  "required": ["message"]
}
```

**Response Schema** (Success):
```json
{
  "success": true,
  "conversation_id": 123,
  "message": {
    "id": 456,
    "role": "assistant",
    "content": "Great! I'll help you add a task to buy milk. What priority should this be? (high/medium/low)",
    "created_at": "2026-01-27T12:00:00Z"
  },
  "conversation_state": {
    "current_intent": "ADDING_TASK",
    "target_task_id": null
  },
  "tool_calls": []
}
```

**Response Schema** (With Tool Call):
```json
{
  "success": true,
  "conversation_id": 123,
  "message": {
    "id": 457,
    "role": "assistant",
    "content": "✅ Task created successfully! Task #42: Buy milk (🔴 high priority, due tomorrow)",
    "created_at": "2026-01-27T12:05:00Z"
  },
  "conversation_state": {
    "current_intent": "NEUTRAL",
    "target_task_id": null
  },
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "title": "Buy milk",
        "priority": "high",
        "due_date": "2026-01-28T23:59:59Z"
      },
      "result": {
        "success": true,
        "task": {
          "id": 42,
          "title": "Buy milk",
          "priority": "high"
        }
      }
    }
  ]
}
```

**Response Schema** (Error - Validation):
```json
{
  "success": false,
  "error": "Message cannot be empty",
  "code": "VALIDATION_ERROR",
  "status": 400
}
```

**Response Schema** (Error - Unauthorized):
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED",
  "status": 401
}
```

**Response Schema** (Error - Conversation Not Found):
```json
{
  "success": false,
  "error": "Conversation not found or you don't have access",
  "code": "NOT_FOUND",
  "status": 404
}
```

**Response Schema** (Error - AI Agent Failure):
```json
{
  "success": false,
  "error": "AI agent temporarily unavailable. Please try again.",
  "code": "SERVICE_ERROR",
  "status": 503,
  "retry_after": 5
}
```

**Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: Invalid input (empty message, message too long, invalid conversation_id)
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation doesn't exist or doesn't belong to user
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Unexpected server error
- `503 Service Unavailable`: AI agent or database temporarily unavailable

**Rate Limiting**:
- **Limit**: 100 requests per minute per user
- **Response Header** (when limit approached):
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 15
  X-RateLimit-Reset: 1674826800
  ```
- **Response** (when limit exceeded):
  ```json
  {
    "success": false,
    "error": "Rate limit exceeded. Please wait before sending more messages.",
    "code": "RATE_LIMIT_EXCEEDED",
    "status": 429,
    "retry_after": 60
  }
  ```

---

## GET /api/chat/conversations

**Purpose**: List all conversations for the authenticated user

**Authentication**: Required (JWT bearer token)

**Query Parameters**:
```
?limit=20          # Number of conversations to return (default: 20, max: 100)
&offset=0          # Offset for pagination (default: 0)
&status=all        # Filter by status: all, active, archived (default: all)
```

**Response Schema**:
```json
{
  "success": true,
  "conversations": [
    {
      "id": 123,
      "created_at": "2026-01-27T10:00:00Z",
      "updated_at": "2026-01-27T12:00:00Z",
      "message_count": 12,
      "current_intent": "NEUTRAL",
      "last_message": {
        "role": "assistant",
        "content": "Task created successfully!",
        "created_at": "2026-01-27T12:00:00Z"
      }
    },
    {
      "id": 122,
      "created_at": "2026-01-26T14:00:00Z",
      "updated_at": "2026-01-26T15:30:00Z",
      "message_count": 8,
      "current_intent": "NEUTRAL",
      "last_message": {
        "role": "user",
        "content": "show my tasks",
        "created_at": "2026-01-26T15:30:00Z"
      }
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Missing or invalid JWT token
- `400 Bad Request`: Invalid query parameters

---

## GET /api/chat/conversations/{conversation_id}

**Purpose**: Get details of a specific conversation including all messages

**Authentication**: Required (JWT bearer token)

**Path Parameters**:
```
conversation_id (integer): ID of the conversation to retrieve
```

**Query Parameters**:
```
?limit=50          # Number of messages to return (default: 50, max: 100)
&offset=0          # Offset for message pagination
```

**Response Schema**:
```json
{
  "success": true,
  "conversation": {
    "id": 123,
    "user_id": 456,
    "created_at": "2026-01-27T10:00:00Z",
    "updated_at": "2026-01-27T12:00:00Z",
    "current_intent": "NEUTRAL",
    "state_data": null,
    "target_task_id": null
  },
  "messages": [
    {
      "id": 450,
      "role": "user",
      "content": "add task to buy milk",
      "created_at": "2026-01-27T10:00:00Z"
    },
    {
      "id": 451,
      "role": "assistant",
      "content": "Great! I'll help you add a task to buy milk. What priority should this be?",
      "created_at": "2026-01-27T10:00:01Z"
    },
    {
      "id": 452,
      "role": "user",
      "content": "high priority",
      "created_at": "2026-01-27T10:01:00Z"
    }
  ],
  "total_messages": 12,
  "limit": 50,
  "offset": 0
}
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation doesn't exist or doesn't belong to user

---

## DELETE /api/chat/conversations/{conversation_id}

**Purpose**: Delete a conversation and all its messages

**Authentication**: Required (JWT bearer token)

**Path Parameters**:
```
conversation_id (integer): ID of the conversation to delete
```

**Response Schema** (Success):
```json
{
  "success": true,
  "message": "Conversation deleted successfully",
  "deleted_conversation_id": 123,
  "deleted_messages_count": 12
}
```

**Response Schema** (Error):
```json
{
  "success": false,
  "error": "Conversation not found or you don't have access",
  "code": "NOT_FOUND",
  "status": 404
}
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation doesn't exist or doesn't belong to user

**Note**: This is a soft delete - conversation is marked as deleted but not removed from database (for audit purposes).

---

## POST /api/chat/conversations/{conversation_id}/cancel

**Purpose**: Cancel current operation and reset conversation state

**Authentication**: Required (JWT bearer token)

**Path Parameters**:
```
conversation_id (integer): ID of the conversation to reset
```

**Response Schema** (Success):
```json
{
  "success": true,
  "message": "Operation cancelled. Conversation reset to neutral state.",
  "conversation_state": {
    "current_intent": "NEUTRAL",
    "state_data": null,
    "target_task_id": null
  }
}
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation doesn't exist or doesn't belong to user

**Use Case**: Frontend "Cancel" button or user sends "never mind" message

---

## Implementation Details

### Request Flow

```
[Client] ──POST /api/chat──> [FastAPI Endpoint]
                                    ↓
                        [1] Extract JWT, validate user
                                    ↓
                        [2] Load/Create conversation
                                    ↓
                        [3] Save user message to DB
                                    ↓
                        [4] Load recent messages (last 50)
                                    ↓
                        [5] Load conversation state
                                    ↓
                        [6] Pre-process: detect intent
                                    ↓
                        [7] Call AI agent runner
                                    ↓
                        [8] Execute tool calls (if any)
                                    ↓
                        [9] Save assistant message to DB
                                    ↓
                        [10] Update conversation state
                                    ↓
                        [11] Return response to client
```

### User Isolation Enforcement

**At Middleware Level**:
```python
# Extract user_id from JWT
user_id = jwt_decode(request.headers["Authorization"]).user_id
request.state.user_id = user_id
```

**At Route Level**:
```python
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # If conversation_id provided, verify ownership
    if request.conversation_id:
        conversation = await conversation_service.get_conversation(
            conversation_id=request.conversation_id,
            user_id=current_user.id  # Enforce ownership
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Create new conversation if needed
    if not request.conversation_id:
        conversation = await conversation_service.create_conversation(
            user_id=current_user.id
        )

    # All subsequent operations use current_user.id for filtering
    ...
```

**At Service Level**:
```python
# All database queries include user_id filter
async def get_conversation(conversation_id: int, user_id: int):
    return await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)  # Critical filter
    )
```

### Error Handling Strategy

**Validation Errors** (400):
- Empty message
- Message too long (>2000 chars)
- Invalid conversation_id format

**Authentication Errors** (401):
- Missing Authorization header
- Invalid JWT token
- Expired JWT token

**Authorization Errors** (404 instead of 403):
- Conversation doesn't belong to user
- **Why 404**: Avoid leaking existence of conversations to unauthorized users

**Service Errors** (503):
- OpenAI API timeout
- Database connection failure
- Rate limit from OpenAI

**Unexpected Errors** (500):
- Unhandled exceptions
- Logged to error tracking service (Sentry)

### Response Time SLA

**Performance Targets**:
- P50: <2s (median response time)
- P95: <5s (95th percentile)
- P99: <10s (99th percentile)

**Optimization Strategies**:
1. Database connection pooling (size: 10-20)
2. Load recent messages only (limit: 50)
3. Async I/O for all database and API calls
4. Caching for system prompt (in-memory, never expires)
5. Request timeout: 15s (return 503 if exceeded)

---

## Testing Contracts

### Contract Tests

**File**: `backend/tests/contract/test_api_contracts.py`

```python
import pytest
from httpx import AsyncClient

async def test_chat_endpoint_contract_valid():
    """POST /api/chat accepts valid request and returns valid response"""
    async with AsyncClient() as client:
        response = await client.post(
            "/api/chat",
            json={"message": "add task to buy milk"},
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )

    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "success" in data
    assert data["success"] == True
    assert "conversation_id" in data
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert "content" in data["message"]
    assert "conversation_state" in data

async def test_chat_endpoint_enforces_user_isolation():
    """Users cannot access other users' conversations"""
    # User 1 creates conversation
    user1_token = get_test_token(user_id=1)
    response = await client.post(
        "/api/chat",
        json={"message": "hello"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    conversation_id = response.json()["conversation_id"]

    # User 2 tries to access user 1's conversation
    user2_token = get_test_token(user_id=2)
    response = await client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "message": "hi"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    # Should return 404 (not 403 to avoid leaking existence)
    assert response.status_code == 404

async def test_chat_endpoint_validates_message_length():
    """POST /api/chat rejects messages > 2000 characters"""
    long_message = "a" * 2001

    response = await client.post(
        "/api/chat",
        json={"message": long_message},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"

async def test_chat_endpoint_requires_authentication():
    """POST /api/chat returns 401 without valid token"""
    response = await client.post(
        "/api/chat",
        json={"message": "hello"}
        # No Authorization header
    )

    assert response.status_code == 401
```

---

## Frontend Integration

### TypeScript Types

```typescript
// src/types/chat.ts

export interface ChatRequest {
  conversation_id?: number | null;
  message: string;
}

export interface ChatResponse {
  success: boolean;
  conversation_id: number;
  message: {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
  };
  conversation_state: {
    current_intent: string;
    target_task_id: number | null;
  };
  tool_calls: ToolCall[];
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: {
    success: boolean;
    [key: string]: any;
  };
}
```

### API Client

```typescript
// src/services/chatApi.ts

export async function sendMessage(
  message: string,
  conversationId?: number | null
): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to send message');
  }

  return response.json();
}
```

---

## Next Steps

**Phase 1 Remaining**:
1. ✅ data-model.md (complete)
2. ✅ contracts/mcp-tools.md (complete)
3. ✅ contracts/api-endpoints.md (this file - complete)
4. ⏳ quickstart.md - Developer setup
5. ⏳ Update agent context
