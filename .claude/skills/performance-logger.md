---
description: Add performance monitoring and execution time logging to backend services with structured JSON output (Phase 3)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill adds execution time logging to all backend services (chat endpoint, MCP tools, AI agent runner, conversation service) with structured JSON output for observability and performance monitoring.

### 1. Parse Requirements

Extract from user input or context:
- Services to instrument (chat endpoint, MCP tools, agent runner, services)
- Logging format (JSON structured logging)
- Metrics to capture (duration_ms, operation_name, user_id, timestamp, status)
- Performance targets (p95 < 3s for chat, p95 < 100ms for DB queries)

### 2. Install Dependencies

```bash
pip install python-json-logger
```

Add to `backend/pyproject.toml`:
```toml
[tool.poetry.dependencies]
python-json-logger = "^2.0.7"
```

### 3. Create Performance Logging Utilities

**File**: `backend/src/utils/performance.py`

```python
"""Performance monitoring utilities."""

import time
import logging
from functools import wraps
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def log_execution_time(operation_name: str):
    """
    Decorator to log execution time of functions.

    Usage:
        @log_execution_time("add_task_operation")
        def add_task(db, params):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error": str(e)
                    }
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "Performance metric",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error": str(e)
                    }
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


@contextmanager
def track_performance(operation_name: str, user_id: str = None):
    """
    Context manager to track performance of code blocks.

    Usage:
        with track_performance("fetch_conversation_history", user_id="user-123"):
            messages = service.get_conversation_history(conv_id, user_id)
    """
    start_time = time.time()
    extra = {
        "operation": operation_name,
        "user_id": user_id
    }
    try:
        yield
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Performance metric",
            extra={**extra, "duration_ms": round(duration_ms, 2), "status": "success"}
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Performance metric",
            extra={**extra, "duration_ms": round(duration_ms, 2), "status": "error", "error": str(e)}
        )
        raise
```

### 4. Add Performance Logging to Chat Endpoint

**File**: `backend/src/routes/chat.py`

```python
from ..utils.performance import log_execution_time, track_performance

@router.post("/{user_id}/chat", response_model=ChatResponse)
@log_execution_time("chat_endpoint")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Process chat message with performance tracking."""
    try:
        # Existing validation...

        # Track conversation history fetch
        with track_performance("fetch_conversation_history", user_id):
            history_messages = conversation_service.get_conversation_history(
                conversation_id,
                user_id,
                limit=50
            )

        # Track agent execution
        with track_performance("run_ai_agent", user_id):
            agent_response = await run_agent(
                user_id=user_id,
                message=request.message,
                conversation_history=conversation_history,
                tools=tools
            )

        # Rest of implementation...

    except Exception as e:
        # Error handling...
```

### 5. Add Performance Logging to MCP Tools

**File**: `backend/src/mcp_tools/add_task.py` (and all other tools)

```python
from ..utils.performance import log_execution_time

@log_execution_time("mcp_tool_add_task")
def add_task(db: Session, params: AddTaskParams) -> AddTaskResult:
    """Create a new task with performance tracking."""
    # Existing implementation...
```

Apply to all MCP tools:
- `list_tasks.py` - `@log_execution_time("mcp_tool_list_tasks")`
- `complete_task.py` - `@log_execution_time("mcp_tool_complete_task")`
- `update_task.py` - `@log_execution_time("mcp_tool_update_task")`
- `delete_task.py` - `@log_execution_time("mcp_tool_delete_task")`

### 6. Add Performance Logging to AI Agent Runner

**File**: `backend/src/ai_agent/runner.py`

```python
from ..utils.performance import track_performance

async def run_agent(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]],
    tools: List[Dict[str, Any]]
) -> AgentResponse:
    """Run AI agent with performance tracking."""

    with track_performance("agent_initialization", user_id):
        # Agent setup...

    with track_performance("agent_execution", user_id):
        # Agent run...

    with track_performance("agent_tool_calls", user_id):
        # Tool execution...
```

### 7. Add Performance Logging to ConversationService

**File**: `backend/src/services/conversation_service.py`

```python
from ..utils.performance import log_execution_time

class ConversationService:

    @log_execution_time("get_conversation_history")
    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: str,
        limit: int = 50
    ) -> List[Message]:
        """Fetch conversation history with performance tracking."""
        # Existing implementation...

    @log_execution_time("create_conversation")
    def create_conversation(self, user_id: str) -> Conversation:
        """Create conversation with performance tracking."""
        # Existing implementation...

    @log_execution_time("add_message")
    def add_message(
        self,
        conversation_id: int,
        user_id: str,
        role: str,
        content: str
    ) -> Message:
        """Add message with performance tracking."""
        # Existing implementation...
```

### 8. Configure Structured JSON Logging

**File**: `backend/src/logging_config.py`

```python
"""Structured JSON logging configuration."""

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure structured JSON logging for production."""

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger"
        }
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    return root_logger
```

**File**: `backend/src/main.py`

```python
from .logging_config import setup_logging

# Setup logging at app startup
setup_logging()

app = FastAPI(title="Todo Chatbot API")
```

### 9. Performance Metrics Endpoint

**File**: `backend/src/routes/health.py`

```python
@router.get("/metrics")
async def performance_metrics():
    """
    Return performance metrics summary.

    In production, integrate with monitoring tools like:
    - Prometheus
    - DataDog
    - New Relic
    - CloudWatch
    """
    return {
        "status": "metrics_available",
        "note": "Check logs for structured performance data",
        "format": "JSON structured logging",
        "metrics": [
            "chat_endpoint - p95 target < 3000ms",
            "mcp_tool_* - per-tool execution time",
            "run_ai_agent - agent execution time",
            "fetch_conversation_history - p95 target < 100ms"
        ]
    }
```

### 10. Testing

**File**: `backend/tests/test_performance_logging.py`

```python
import pytest
from unittest.mock import patch
from src.utils.performance import log_execution_time, track_performance


def test_log_execution_time_decorator_sync(caplog):
    """Test execution time logging for sync functions."""

    @log_execution_time("test_operation")
    def sync_function():
        return "result"

    result = sync_function()

    assert result == "result"
    assert "Performance metric" in caplog.text
    assert "test_operation" in caplog.text
    assert "duration_ms" in caplog.text


@pytest.mark.asyncio
async def test_log_execution_time_decorator_async(caplog):
    """Test execution time logging for async functions."""

    @log_execution_time("async_test_operation")
    async def async_function():
        return "async_result"

    result = await async_function()

    assert result == "async_result"
    assert "Performance metric" in caplog.text
    assert "async_test_operation" in caplog.text


def test_track_performance_context_manager(caplog):
    """Test performance tracking context manager."""

    with track_performance("database_query", user_id="user-123"):
        # Simulate some work
        pass

    assert "Performance metric" in caplog.text
    assert "database_query" in caplog.text
    assert "user-123" in caplog.text


def test_performance_logging_on_error(caplog):
    """Test that errors are logged with performance metrics."""

    @log_execution_time("error_operation")
    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        failing_function()

    assert "Performance metric" in caplog.text
    assert "status" in caplog.text
    assert "error" in caplog.text
```

## Example Log Output

**Successful Operation:**
```json
{
  "timestamp": "2025-12-30T20:15:30.123Z",
  "level": "INFO",
  "logger": "src.routes.chat",
  "message": "Performance metric",
  "operation": "chat_endpoint",
  "duration_ms": 2450.75,
  "status": "success"
}
```

**With User Context:**
```json
{
  "timestamp": "2025-12-30T20:15:30.456Z",
  "level": "INFO",
  "logger": "src.services.conversation_service",
  "message": "Performance metric",
  "operation": "fetch_conversation_history",
  "user_id": "user-123",
  "duration_ms": 85.32,
  "status": "success"
}
```

**Error Case:**
```json
{
  "timestamp": "2025-12-30T20:15:31.789Z",
  "level": "ERROR",
  "logger": "src.ai_agent.runner",
  "message": "Performance metric",
  "operation": "run_ai_agent",
  "user_id": "user-456",
  "duration_ms": 5020.45,
  "status": "error",
  "error": "OpenAI API timeout"
}
```

## Constitution Alignment

- ✅ **Observability**: Structured logging enables performance monitoring
- ✅ **Performance Standards**: Tracks p95 < 3s for chat, p95 < 100ms for DB
- ✅ **User Isolation**: user_id included in performance logs
- ✅ **Stateless Architecture**: No state, just logging
- ✅ **Production Ready**: JSON format for log aggregation tools

## Success Criteria

- [ ] `performance.py` utility created with decorators and context managers
- [ ] Chat endpoint decorated with `@log_execution_time`
- [ ] All MCP tools instrumented with performance logging
- [ ] AI agent runner tracks execution time
- [ ] ConversationService methods log performance
- [ ] JSON structured logging configured
- [ ] All logs include operation name, duration_ms, status
- [ ] Tests verify logging for success and error cases
- [ ] Performance targets documented (p95 < 3s, p95 < 100ms)

## References

- Phase 3 Constitution: `.specify/memory/constitution.md` - Principle IX (Observability)
- Python JSON Logger: https://github.com/madzak/python-json-logger
- FastAPI Logging: https://fastapi.tiangolo.com/tutorial/middleware/
