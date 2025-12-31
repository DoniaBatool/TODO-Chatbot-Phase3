---
description: Setup comprehensive structured logging infrastructure with user context, request IDs, and error tracking (Phase 3)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill sets up structured JSON logging across all backend services with user_id, conversation_id, request_id tracking, and integration with log aggregation tools.

### 1. Parse Requirements

Extract from user input or context:
- Services to instrument (all routes, services, MCP tools, agent)
- Log levels (INFO for operations, ERROR for failures)
- Context to track (user_id, conversation_id, request_id, tool_name)
- Integration targets (CloudWatch, DataDog, Elasticsearch)

### 2. Install Dependencies

```bash
pip install python-json-logger asgi-correlation-id
```

Add to `backend/pyproject.toml`:
```toml
[tool.poetry.dependencies]
python-json-logger = "^2.0.7"
asgi-correlation-id = "^4.3.0"
```

### 3. Create Logging Configuration

**File**: `backend/src/logging_config.py`

```python
"""Comprehensive structured logging configuration."""

import logging
import sys
from pythonjsonlogger import jsonlogger
from typing import Dict, Any


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log records."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record['timestamp'] = self.formatTime(record, self.datefmt)

        # Add level name
        log_record['level'] = record.levelname

        # Add logger name
        log_record['logger'] = record.name

        # Add source file and line number
        log_record['source'] = f"{record.filename}:{record.lineno}"

        # Add function name
        log_record['function'] = record.funcName


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured JSON logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured root logger
    """
    # Create custom JSON formatter
    formatter = CustomJsonFormatter(
        fmt='%(message)s',  # All fields added by add_fields
        datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
    )

    # Console handler (stdout for CloudWatch/Docker compatibility)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(console_handler)

    # Silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return root_logger
```

### 4. Add Request ID Middleware

**File**: `backend/src/middleware/request_context.py`

```python
"""Request context middleware for tracking request IDs."""

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Request
import logging
from typing import Callable

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next: Callable):
    """
    Middleware to log all requests with context.

    Logs:
    - Request method and path
    - Request ID (correlation ID)
    - User ID (from auth)
    - Response status code
    - Response time
    """
    import time
    from asgi_correlation_id import correlation_id

    start_time = time.time()

    # Extract user_id from auth if available
    user_id = None
    if hasattr(request.state, "user_id"):
        user_id = request.state.user_id

    # Get request ID
    request_id = correlation_id.get()

    # Log incoming request
    logger.info(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "user_id": user_id,
            "query_params": str(request.query_params)
        }
    )

    # Process request
    response = await call_next(request)

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Log response
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "user_id": user_id,
            "status_code": response.status_code,
            "response_time_ms": round(response_time_ms, 2)
        }
    )

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    return response
```

### 5. Integrate Middleware in FastAPI

**File**: `backend/src/main.py`

```python
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
from .logging_config import setup_logging
from .middleware.request_context import log_requests

# Setup logging first
setup_logging(log_level="INFO")

app = FastAPI(title="Todo Chatbot API")

# Add correlation ID middleware (generates request IDs)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    generator=lambda: str(uuid.uuid4()),
    validator=None,
    transformer=lambda a: a,
)

# Add request logging middleware
app.middleware("http")(log_requests)

# Rest of app setup...
```

### 6. Add Structured Logging to Chat Endpoint

**File**: `backend/src/routes/chat.py`

```python
import logging
from asgi_correlation_id import correlation_id

logger = logging.getLogger(__name__)

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Process chat message with structured logging."""

    # Get request ID from correlation_id
    request_id = correlation_id.get()

    logger.info(
        "Processing chat request",
        extra={
            "request_id": request_id,
            "user_id": user_id,
            "conversation_id": request.conversation_id,
            "message_length": len(request.message)
        }
    )

    try:
        # Implementation...

        logger.info(
            "Chat request completed successfully",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "tool_calls_count": len(executed_tools)
            }
        )

        return ChatResponse(...)

    except HTTPException as e:
        logger.warning(
            "Chat request failed - HTTP exception",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "status_code": e.status_code,
                "detail": e.detail
            }
        )
        raise

    except Exception as e:
        logger.error(
            "Chat request failed - internal error",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True  # Include stack trace
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message"
        )
```

### 7. Add Structured Logging to MCP Tools

**File**: `backend/src/mcp_tools/add_task.py` (and all tools)

```python
import logging

logger = logging.getLogger(__name__)

def add_task(db: Session, params: AddTaskParams) -> AddTaskResult:
    """Create task with structured logging."""

    logger.info(
        "MCP tool invoked",
        extra={
            "tool_name": "add_task",
            "user_id": params.user_id,
            "title": params.title
        }
    )

    try:
        # Implementation...

        logger.info(
            "MCP tool completed",
            extra={
                "tool_name": "add_task",
                "user_id": params.user_id,
                "task_id": task.id,
                "status": "success"
            }
        )

        return AddTaskResult(...)

    except Exception as e:
        logger.error(
            "MCP tool failed",
            extra={
                "tool_name": "add_task",
                "user_id": params.user_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise
```

### 8. Add Structured Logging to AI Agent

**File**: `backend/src/ai_agent/runner.py`

```python
import logging

logger = logging.getLogger(__name__)

async def run_agent(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]],
    tools: List[Dict[str, Any]]
) -> AgentResponse:
    """Run agent with structured logging."""

    logger.info(
        "Agent execution started",
        extra={
            "user_id": user_id,
            "message_length": len(message),
            "history_length": len(conversation_history),
            "tools_count": len(tools)
        }
    )

    try:
        # Agent execution...

        logger.info(
            "Agent execution completed",
            extra={
                "user_id": user_id,
                "tool_calls": [tc.get("tool") for tc in agent_response.tool_calls],
                "response_length": len(agent_response.response)
            }
        )

        return agent_response

    except Exception as e:
        logger.error(
            "Agent execution failed",
            extra={
                "user_id": user_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise
```

### 9. Testing

**File**: `backend/tests/test_structured_logging.py`

```python
import pytest
import json
from fastapi.testclient import TestClient
from src.main import app


def test_request_logging_includes_request_id(client, caplog):
    """Test that request logging includes request ID."""

    response = client.get("/api/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    # Check logs contain request ID
    logs = [json.loads(record.message) for record in caplog.records]
    assert any("request_id" in log for log in logs)


def test_structured_log_format(caplog):
    """Test that logs are in JSON format with required fields."""

    logger = logging.getLogger("test")
    logger.info("Test message", extra={"user_id": "user-123", "operation": "test"})

    # Parse log as JSON
    log_record = caplog.records[0]

    # Verify structured fields exist
    assert hasattr(log_record, "user_id")
    assert log_record.user_id == "user-123"
    assert hasattr(log_record, "operation")


@pytest.mark.asyncio
async def test_error_logging_includes_stack_trace(client, caplog):
    """Test that errors include stack traces."""

    # Trigger an error
    response = client.post(
        "/api/user-123/chat",
        json={"message": "test"},
        headers={"Authorization": "Bearer invalid"}
    )

    # Should have error logs with exc_info
    error_logs = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_logs) > 0
    assert any(r.exc_info for r in error_logs)
```

## Example Log Output

**Incoming Request:**
```json
{
  "timestamp": "2025-12-30T20:30:15.123Z",
  "level": "INFO",
  "logger": "src.middleware.request_context",
  "source": "request_context.py:42",
  "function": "log_requests",
  "message": "Incoming request",
  "request_id": "a7f3e8b1-4c2d-4e9a-b1c3-7f8e9a1b2c3d",
  "method": "POST",
  "path": "/api/user-123/chat",
  "user_id": "user-123",
  "query_params": ""
}
```

**Tool Execution:**
```json
{
  "timestamp": "2025-12-30T20:30:15.456Z",
  "level": "INFO",
  "logger": "src.mcp_tools.add_task",
  "source": "add_task.py:65",
  "function": "add_task",
  "message": "MCP tool invoked",
  "tool_name": "add_task",
  "user_id": "user-123",
  "title": "Buy milk"
}
```

**Error with Stack Trace:**
```json
{
  "timestamp": "2025-12-30T20:30:16.789Z",
  "level": "ERROR",
  "logger": "src.routes.chat",
  "source": "chat.py:182",
  "function": "chat",
  "message": "Chat request failed - internal error",
  "request_id": "a7f3e8b1-4c2d-4e9a-b1c3-7f8e9a1b2c3d",
  "user_id": "user-123",
  "error_type": "ValueError",
  "error_message": "Invalid message format",
  "exc_info": "Traceback (most recent call last):\\n  File..."
}
```

## Constitution Alignment

- ✅ **Observability**: Comprehensive logging of all operations
- ✅ **User Isolation**: user_id in every log
- ✅ **Debugging**: Request IDs for tracing across services
- ✅ **Production Ready**: JSON format for log aggregation
- ✅ **Error Handling**: Stack traces for debugging

## Success Criteria

- [ ] `logging_config.py` with CustomJsonFormatter created
- [ ] `request_context.py` middleware for request ID tracking
- [ ] All routes log with request_id, user_id, operation
- [ ] All MCP tools log invocation and completion
- [ ] AI agent logs execution with context
- [ ] Errors include exc_info (stack traces)
- [ ] Request IDs in response headers (X-Request-ID)
- [ ] Tests verify JSON format and required fields
- [ ] Log aggregation ready (CloudWatch, DataDog, etc.)

## References

- Python JSON Logger: https://github.com/madzak/python-json-logger
- ASGI Correlation ID: https://github.com/snok/asgi-correlation-id
- 12-Factor App Logs: https://12factor.net/logs
