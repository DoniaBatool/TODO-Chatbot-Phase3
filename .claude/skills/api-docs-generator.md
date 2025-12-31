---
description: Generate comprehensive OpenAPI documentation and docstrings for all backend endpoints, services, and MCP tools (Phase 3)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill automatically generates OpenAPI documentation, adds comprehensive docstrings to all functions, and creates API reference documentation.

### 1. Parse Requirements

Extract from user input or context:
- Endpoints to document (all FastAPI routes)
- Functions to document (services, MCP tools, utilities)
- Documentation format (OpenAPI 3.1, Google-style docstrings)
- Examples to include (request/response samples)

### 2. Configure OpenAPI in FastAPI

**File**: `backend/src/main.py`

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Todo Chatbot API",
    description="AI-powered conversational task management system with natural language processing",
    version="3.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"
)


def custom_openapi():
    """
    Custom OpenAPI schema with enhanced documentation.

    Returns:
        dict: OpenAPI 3.1 schema with full API documentation
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Todo Chatbot API",
        version="3.0.0",
        description="""
        ## Overview
        AI-powered todo application with conversational interface using OpenAI Agents SDK.

        ## Features
        - 🤖 Natural language task management
        - 💬 Conversation history with context
        - 🔒 User isolation and JWT authentication
        - 📊 5 MCP tools: add, list, complete, update, delete tasks
        - ⚡ Stateless architecture with database-centric state

        ## Authentication
        All endpoints require JWT Bearer token except `/auth/signup` and `/auth/login`.

        Include token in Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ## Rate Limiting
        - Authenticated: 100 requests/minute
        - Unauthenticated: 10 requests/minute

        ## Performance
        - p95 response time: < 3s for chat endpoint
        - p95 query time: < 100ms for database operations
        - Concurrent users: 100+ simultaneous sessions
        """,
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "User authentication and authorization"
            },
            {
                "name": "chat",
                "description": "Conversational AI interface for task management"
            },
            {
                "name": "tasks",
                "description": "Direct task management endpoints (legacy)"
            },
            {
                "name": "health",
                "description": "Health checks and system status"
            }
        ]
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token from /auth/login or /auth/signup"
        }
    }

    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
```

### 3. Add Comprehensive Endpoint Documentation

**File**: `backend/src/routes/chat.py`

```python
@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    summary="Process chat message",
    description="""
    Process a natural language message and execute corresponding task operations.

    This endpoint:
    1. Validates user authentication (JWT token required)
    2. Enforces user isolation (user_id must match JWT)
    3. Creates or resumes conversation
    4. Fetches last 50 messages for context
    5. Runs AI agent with OpenAI Agents SDK
    6. Executes tool calls (add_task, list_tasks, etc.)
    7. Stores user message and assistant response
    8. Returns natural language response with tool execution results

    ## Natural Language Examples

    **Add task:**
    - "Add task to buy milk"
    - "Remind me to call mom"
    - "Create task: finish quarterly report"

    **List tasks:**
    - "Show my tasks"
    - "What do I need to do?"
    - "List pending tasks"

    **Complete task:**
    - "Mark task 5 as complete"
    - "I finished buying milk"
    - "Done with task 3"

    **Update task:**
    - "Change task 3 to Buy milk and eggs"
    - "Update task 2 description to include deadline"

    **Delete task:**
    - "Delete task 7"
    - "Remove the milk task"

    ## Performance
    - p95 response time: < 3s
    - Includes: DB fetch (50 messages) + AI inference + tool execution + DB writes

    ## Error Handling
    - 401: Missing or invalid JWT token
    - 403: user_id in path doesn't match JWT user_id
    - 404: conversation_id not found for this user
    - 500: Internal error (agent failure, DB error)
    """,
    responses={
        200: {
            "description": "Chat message processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": 42,
                        "response": "I've added 'Buy milk' to your tasks.",
                        "tool_calls": [
                            {
                                "tool": "add_task",
                                "params": {"title": "Buy milk"},
                                "result": {
                                    "task_id": 15,
                                    "title": "Buy milk",
                                    "description": None,
                                    "completed": False,
                                    "created_at": "2025-12-30T20:45:00Z"
                                }
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Missing or invalid JWT token",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        403: {
            "description": "Forbidden - user_id mismatch",
            "content": {
                "application/json": {
                    "example": {"detail": "Cannot access chat for other users"}
                }
            }
        },
        404: {
            "description": "Conversation not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Conversation 123 not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process chat message"}
                }
            }
        }
    },
    tags=["chat"]
)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process chat message and return AI assistant response.

    Args:
        user_id: User ID from URL path (must match JWT user_id)
        request: Chat request with message and optional conversation_id
        current_user_id: Authenticated user ID from JWT token
        db: Database session dependency

    Returns:
        ChatResponse with conversation_id, assistant response, and tool calls

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If path user_id doesn't match JWT user_id
        HTTPException 404: If conversation_id not found for user
        HTTPException 500: If internal error occurs

    Example:
        Request:
        ```json
        {
            "message": "Add task to buy milk"
        }
        ```

        Response:
        ```json
        {
            "conversation_id": 1,
            "response": "I've added 'Buy milk' to your tasks.",
            "tool_calls": [
                {
                    "tool": "add_task",
                    "params": {"title": "Buy milk"},
                    "result": {
                        "task_id": 15,
                        "title": "Buy milk",
                        "completed": false
                    }
                }
            ]
        }
        ```
    """
    # Implementation...
```

### 4. Add Docstrings to All MCP Tools

**File**: `backend/src/mcp_tools/add_task.py`

```python
def add_task(db: Session, params: AddTaskParams) -> AddTaskResult:
    """
    Create a new task for the authenticated user.

    This is the core MCP tool function that AI agents call to create tasks
    based on natural language input. Enforces user isolation and validates
    all input parameters.

    Args:
        db: SQLModel database session for persistence
        params: Task creation parameters with user_id and title

    Returns:
        AddTaskResult containing created task details with ID and timestamp

    Raises:
        ValueError: If title is empty or exceeds 200 characters
        ValueError: If description exceeds 1000 characters
        RuntimeError: If database operation fails

    Security:
        - Enforces user isolation via params.user_id
        - No cross-user data access possible
        - All queries filter by user_id

    Performance:
        - Single INSERT operation
        - p95 execution time: < 50ms
        - Indexed on user_id for efficient queries

    Example:
        >>> from sqlmodel import Session
        >>> params = AddTaskParams(
        ...     user_id="user-123",
        ...     title="Buy milk",
        ...     description="From grocery store"
        ... )
        >>> result = add_task(db, params)
        >>> print(result.task_id)
        15
        >>> print(result.title)
        'Buy milk'

    MCP Tool Registration:
        Registered in `src/ai_agent/tools.py` as "add_task" with:
        - Description: Natural language task creation
        - Parameters: user_id (required), title (required), description (optional)
        - Returns: Task object with id, title, description, completed, timestamps
    """
    # Implementation...
```

### 5. Add Docstrings to Services

**File**: `backend/src/services/conversation_service.py`

```python
class ConversationService:
    """
    Service for managing conversations and messages with user isolation.

    Provides database operations for:
    - Creating new conversations
    - Fetching conversation history
    - Adding messages to conversations
    - Updating conversation timestamps

    All operations enforce user isolation - users can only access their own
    conversations and messages.

    Attributes:
        db: SQLModel database session

    Example:
        >>> from sqlmodel import Session
        >>> service = ConversationService(db)
        >>> conversation = service.create_conversation("user-123")
        >>> service.add_message(
        ...     conversation.id,
        ...     "user-123",
        ...     "user",
        ...     "Add task to buy milk"
        ... )
    """

    def __init__(self, db: Session):
        """
        Initialize conversation service.

        Args:
            db: SQLModel database session for persistence
        """
        self.db = db

    def create_conversation(self, user_id: str) -> Conversation:
        """
        Create a new conversation for the user.

        Args:
            user_id: ID of the user creating the conversation

        Returns:
            Conversation: Newly created conversation with ID and timestamp

        Raises:
            RuntimeError: If database operation fails

        Example:
            >>> conversation = service.create_conversation("user-123")
            >>> print(conversation.id)
            1
            >>> print(conversation.user_id)
            'user-123'
        """
        # Implementation...
```

### 6. Generate API Documentation Files

**File**: `backend/docs/api/README.md`

```markdown
# Todo Chatbot API Documentation

## Base URL

```
Production: https://api.example.com
Staging: https://staging-api.example.com
Local: http://localhost:8000
```

## Authentication

All endpoints except `/auth/signup` and `/auth/login` require JWT authentication.

### Get Token

```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Use Token

```bash
curl -X POST http://localhost:8000/api/user-123/chat \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add task to buy milk"
  }'
```

## Endpoints

### Chat API

#### POST /api/{user_id}/chat

Process natural language message for task management.

... (rest of documentation)
```

### 7. Export OpenAPI Schema

**Script**: `backend/scripts/export_openapi.py`

```python
"""Export OpenAPI schema to JSON file."""

import json
from pathlib import Path
from src.main import app

# Get OpenAPI schema
openapi_schema = app.openapi()

# Write to file
output_path = Path("docs/api/openapi.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"OpenAPI schema exported to {output_path}")
```

Run: `python -m backend.scripts.export_openapi`

## Constitution Alignment

- ✅ **Documentation**: Comprehensive API and code documentation
- ✅ **Developer Experience**: Clear examples and error descriptions
- ✅ **Maintainability**: Docstrings for all public functions
- ✅ **OpenAPI Standard**: Industry-standard API documentation

## Success Criteria

- [ ] FastAPI app configured with custom OpenAPI schema
- [ ] All endpoints have summary, description, examples, error responses
- [ ] All MCP tools have comprehensive docstrings
- [ ] All services have class and method docstrings
- [ ] OpenAPI schema includes authentication details
- [ ] Swagger UI accessible at /docs
- [ ] ReDoc accessible at /redoc
- [ ] API documentation in docs/api/README.md
- [ ] OpenAPI JSON exported to docs/api/openapi.json

## References

- FastAPI OpenAPI: https://fastapi.tiangolo.com/tutorial/metadata/
- OpenAPI 3.1 Spec: https://spec.openapis.org/oas/latest.html
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
