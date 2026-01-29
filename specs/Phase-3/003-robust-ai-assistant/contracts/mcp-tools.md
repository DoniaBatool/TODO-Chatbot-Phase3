# MCP Tool Contracts

**Feature**: 001-robust-ai-assistant
**Purpose**: Define contracts for all MCP tools used by the AI agent
**Date**: 2026-01-27

---

## Tool Contract Format

Each tool contract defines:
- **Tool Name**: Unique identifier
- **Purpose**: What the tool does
- **Input Schema**: Required and optional parameters
- **Output Schema**: Success and error responses
- **User Isolation**: How user_id is enforced
- **Error Handling**: Expected error scenarios
- **Examples**: Sample inputs and outputs

---

## 1. add_task

**Purpose**: Create a new task for the authenticated user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title (required)"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "default": "medium",
      "description": "Task priority level"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 datetime string (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Additional task details (optional)"
    }
  },
  "required": ["title"]
}
```

**Output Schema** (Success):
```json
{
  "success": true,
  "task": {
    "id": 123,
    "user_id": 456,
    "title": "Buy milk",
    "priority": "high",
    "due_date": "2026-01-28T23:59:59Z",
    "description": null,
    "completed": false,
    "created_at": "2026-01-27T10:00:00Z",
    "updated_at": "2026-01-27T10:00:00Z"
  },
  "message": "Task created successfully"
}
```

**Output Schema** (Error):
```json
{
  "success": false,
  "error": "Validation error: title cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

**User Isolation**:
- user_id injected by backend runner (not part of tool input)
- Task created with `task.user_id = current_user.id`
- Agent never sees or provides user_id

**Error Scenarios**:
- `VALIDATION_ERROR`: Empty title, invalid priority, invalid date format
- `DATABASE_ERROR`: Connection failure, constraint violation
- `UNAUTHORIZED`: User not authenticated (handled by middleware)

**Example Call**:
```python
# Agent calls
result = add_task(
    title="Buy milk",
    priority="high",
    due_date="2026-01-28T23:59:59Z",
    description=None
)

# Backend runner injects user_id before execution
result = await task_service.create_task(
    user_id=current_user.id,  # Injected
    title="Buy milk",
    priority="high",
    due_date="2026-01-28T23:59:59Z",
    description=None
)
```

---

## 2. list_tasks

**Purpose**: Retrieve all tasks or filtered subset for authenticated user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter tasks by completion status"
    },
    "task_id": {
      "type": "integer",
      "description": "Get specific task by ID (optional)"
    }
  },
  "required": []
}
```

**Output Schema** (Success):
```json
{
  "success": true,
  "tasks": [
    {
      "id": 123,
      "user_id": 456,
      "title": "Buy milk",
      "priority": "high",
      "due_date": "2026-01-28T23:59:59Z",
      "description": null,
      "completed": false,
      "created_at": "2026-01-27T10:00:00Z",
      "updated_at": "2026-01-27T10:00:00Z"
    },
    {
      "id": 124,
      "title": "Call mom",
      "priority": "medium",
      "due_date": null,
      "description": "Discuss weekend plans",
      "completed": true,
      "created_at": "2026-01-26T14:00:00Z",
      "updated_at": "2026-01-27T09:00:00Z"
    }
  ],
  "count": 2
}
```

**Output Schema** (Error):
```json
{
  "success": false,
  "error": "Task not found",
  "code": "NOT_FOUND"
}
```

**User Isolation**:
- All queries filtered by `tasks.user_id = current_user.id`
- Agent cannot see other users' tasks
- If task_id provided, verify ownership before returning

**Error Scenarios**:
- `NOT_FOUND`: Requested task_id doesn't exist or doesn't belong to user
- `DATABASE_ERROR`: Connection failure

**Example Call**:
```python
# Agent calls: Get all pending tasks
result = list_tasks(status="pending")

# Backend adds user filter
result = await task_service.get_tasks(
    user_id=current_user.id,  # Injected
    status="pending"
)

# Agent calls: Get specific task (for confirmation before delete)
result = list_tasks(task_id=5)

# Backend verifies ownership
result = await task_service.get_task(
    task_id=5,
    user_id=current_user.id  # Injected - will return 404 if not owner
)
```

---

## 3. update_task

**Purpose**: Update one or more fields of an existing task

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "description": "ID of task to update (required)"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "New task title (optional)"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "New priority level (optional)"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "New due date or null to remove (optional)"
    },
    "description": {
      "type": ["string", "null"],
      "maxLength": 1000,
      "description": "New description or null to remove (optional)"
    },
    "completed": {
      "type": "boolean",
      "description": "Mark task as complete/incomplete (optional)"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema** (Success):
```json
{
  "success": true,
  "task": {
    "id": 123,
    "user_id": 456,
    "title": "Buy milk",
    "priority": "high",
    "due_date": "2026-01-28T23:59:59Z",
    "description": "From Whole Foods",
    "completed": false,
    "created_at": "2026-01-27T10:00:00Z",
    "updated_at": "2026-01-27T11:30:00Z"
  },
  "message": "Task updated successfully",
  "fields_updated": ["priority", "description"]
}
```

**Output Schema** (Error):
```json
{
  "success": false,
  "error": "Task not found or you don't have permission",
  "code": "NOT_FOUND"
}
```

**User Isolation**:
- Verify `task.user_id == current_user.id` before update
- Reject update if user doesn't own task
- Return 404 instead of 403 to avoid leaking task existence

**Error Scenarios**:
- `NOT_FOUND`: Task doesn't exist or user doesn't own it
- `VALIDATION_ERROR`: Empty title, invalid priority, invalid date
- `NO_CHANGES`: No fields provided to update (warning, not error)
- `DATABASE_ERROR`: Connection failure, constraint violation

**Example Call**:
```python
# Agent calls: Update priority only
result = update_task(
    task_id=5,
    priority="high"
)

# Backend verifies ownership
task = await task_service.get_task(task_id=5, user_id=current_user.id)
if not task:
    return {"success": false, "error": "Task not found", "code": "NOT_FOUND"}

result = await task_service.update_task(
    task_id=5,
    user_id=current_user.id,  # Injected for double-check
    priority="high"
)

# Agent calls: Remove deadline
result = update_task(
    task_id=5,
    due_date=null  # Explicitly set to null
)
```

---

## 4. delete_task

**Purpose**: Permanently delete a task

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "description": "ID of task to delete (required)"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema** (Success):
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "deleted_task_id": 123
}
```

**Output Schema** (Error):
```json
{
  "success": false,
  "error": "Task not found or you don't have permission",
  "code": "NOT_FOUND"
}
```

**User Isolation**:
- Verify `task.user_id == current_user.id` before deletion
- Reject deletion if user doesn't own task
- Return 404 instead of 403 to avoid leaking task existence

**Error Scenarios**:
- `NOT_FOUND`: Task doesn't exist or user doesn't own it
- `DATABASE_ERROR`: Connection failure, foreign key constraint violation

**Example Call**:
```python
# Agent calls
result = delete_task(task_id=5)

# Backend verifies ownership before deletion
task = await task_service.get_task(task_id=5, user_id=current_user.id)
if not task:
    return {"success": false, "error": "Task not found", "code": "NOT_FOUND"}

result = await task_service.delete_task(
    task_id=5,
    user_id=current_user.id  # Injected for double-check
)
```

---

## 5. complete_task

**Purpose**: Toggle task completion status (alias for update_task with completed field)

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "integer",
      "description": "ID of task to mark complete/incomplete (required)"
    },
    "completed": {
      "type": "boolean",
      "default": true,
      "description": "true to mark complete, false to mark incomplete"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema** (Success):
```json
{
  "success": true,
  "task": {
    "id": 123,
    "title": "Buy milk",
    "completed": true,
    "updated_at": "2026-01-27T12:00:00Z"
  },
  "message": "Task marked as complete"
}
```

**User Isolation**:
- Same as update_task (verify ownership)

**Error Scenarios**:
- Same as update_task

**Example Call**:
```python
# Agent calls: Mark task complete
result = complete_task(task_id=5, completed=true)

# Internally calls update_task
result = update_task(task_id=5, completed=true)

# Agent calls: Mark task incomplete (revert)
result = complete_task(task_id=5, completed=false)
```

---

## 6. find_task

**Purpose**: Search for tasks by fuzzy matching title/name

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "description": "Search query (partial title, keywords, etc.)"
    },
    "threshold": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "default": 0.6,
      "description": "Minimum similarity score (0-1) to return match"
    }
  },
  "required": ["query"]
}
```

**Output Schema** (Success - Single Match):
```json
{
  "success": true,
  "match_type": "single",
  "task": {
    "id": 123,
    "title": "Buy milk from store",
    "priority": "high",
    "due_date": null,
    "description": null,
    "completed": false
  },
  "confidence": 0.87,
  "message": "Found 1 matching task"
}
```

**Output Schema** (Success - Multiple Matches):
```json
{
  "success": true,
  "match_type": "multiple",
  "tasks": [
    {
      "id": 123,
      "title": "Buy milk from store",
      "confidence": 0.87
    },
    {
      "id": 124,
      "title": "Milk delivery subscription",
      "confidence": 0.78
    }
  ],
  "message": "Found 2 matching tasks. Please specify which one."
}
```

**Output Schema** (No Match):
```json
{
  "success": false,
  "match_type": "none",
  "error": "No tasks found matching 'milk'",
  "code": "NOT_FOUND",
  "suggestion": "Try listing all tasks with list_tasks()"
}
```

**User Isolation**:
- Search only within `tasks.user_id = current_user.id`
- Never return tasks from other users

**Fuzzy Matching Logic**:
- Use rapidfuzz library
- Algorithm: Levenshtein distance + token sort ratio
- Return matches with confidence >= threshold
- If single match >= 0.7: return single
- If multiple matches >= 0.6: return all as multiple
- If no matches >= threshold: return NOT_FOUND

**Error Scenarios**:
- `NOT_FOUND`: No tasks match the query above threshold
- `VALIDATION_ERROR`: Empty query string
- `DATABASE_ERROR`: Connection failure

**Example Call**:
```python
# Agent calls: Find "milk" task
result = find_task(query="milk")

# Returns single match (87% confidence)
{
  "success": true,
  "match_type": "single",
  "task": {"id": 123, "title": "Buy milk from store"},
  "confidence": 0.87
}

# Agent calls: Find "call" task (ambiguous)
result = find_task(query="call")

# Returns multiple matches
{
  "success": true,
  "match_type": "multiple",
  "tasks": [
    {"id": 5, "title": "Call mom", "confidence": 0.95},
    {"id": 12, "title": "Call dentist", "confidence": 0.92}
  ]
}

# Agent response to user: "I found 2 tasks: Call mom (ID 5) and Call dentist (ID 12). Which one?"
```

---

## Tool Registration for AI Agent

**File**: `backend/src/ai_agent/agent.py`

```python
from backend.src.mcp_tools import (
    add_task,
    list_tasks,
    update_task,
    delete_task,
    complete_task,
    find_task
)

# Register tools with OpenAI Agents SDK
tools = [
    {
        "name": "add_task",
        "description": "Create a new task for the user. Use after collecting title, priority (optional), due_date (optional), and description (optional).",
        "function": add_task,
        "parameters": add_task.schema  # JSON schema from above
    },
    {
        "name": "list_tasks",
        "description": "Retrieve user's tasks. Use when user asks to 'show my tasks' or when you need to display a specific task before deletion/update.",
        "function": list_tasks,
        "parameters": list_tasks.schema
    },
    {
        "name": "update_task",
        "description": "Update one or more fields of an existing task. Use after getting confirmation from user.",
        "function": update_task,
        "parameters": update_task.schema
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task. ALWAYS ask for confirmation before calling this tool.",
        "function": delete_task,
        "parameters": delete_task.schema
    },
    {
        "name": "complete_task",
        "description": "Mark a task as complete or incomplete. Use when user says 'mark done', 'complete', 'finished', etc.",
        "function": complete_task,
        "parameters": complete_task.schema
    },
    {
        "name": "find_task",
        "description": "Search for tasks by partial title or keywords using fuzzy matching. Use when user mentions a task by name instead of ID (e.g., 'the milk task', 'update shopping').",
        "function": find_task,
        "parameters": find_task.schema
    }
]
```

---

## Contract Compliance Testing

**File**: `backend/tests/contract/test_mcp_tool_contracts.py`

```python
import pytest
from pydantic import ValidationError

def test_add_task_contract_valid():
    """add_task accepts valid inputs"""
    result = add_task(title="Buy milk", priority="high")
    assert result["success"] == True
    assert result["task"]["title"] == "Buy milk"

def test_add_task_contract_invalid_title():
    """add_task rejects empty title"""
    with pytest.raises(ValidationError):
        add_task(title="", priority="high")

def test_add_task_contract_invalid_priority():
    """add_task rejects invalid priority"""
    with pytest.raises(ValidationError):
        add_task(title="Buy milk", priority="urgent")

def test_list_tasks_returns_only_user_tasks():
    """list_tasks enforces user isolation"""
    # Create tasks for two users
    create_task(user_id=1, title="User 1 task")
    create_task(user_id=2, title="User 2 task")

    # Request as user 1
    result = list_tasks(user_id=1)
    assert result["count"] == 1
    assert result["tasks"][0]["title"] == "User 1 task"

def test_find_task_fuzzy_matching():
    """find_task returns tasks above confidence threshold"""
    create_task(user_id=1, title="Buy milk from store")

    # Exact match
    result = find_task(query="Buy milk from store")
    assert result["confidence"] == 1.0

    # Partial match
    result = find_task(query="milk")
    assert result["confidence"] >= 0.7
    assert result["task"]["title"] == "Buy milk from store"

    # Typo tolerance
    result = find_task(query="mlik")  # typo
    assert result["confidence"] >= 0.6

def test_delete_task_requires_ownership():
    """delete_task rejects deletion of other user's task"""
    task = create_task(user_id=1, title="User 1 task")

    # Try to delete as user 2
    result = delete_task(task_id=task.id, user_id=2)
    assert result["success"] == False
    assert result["code"] == "NOT_FOUND"

    # Verify task still exists
    task = get_task(task_id=task.id, user_id=1)
    assert task is not None
```

---

## Tool Usage Guidelines for Agent

**When to use which tool**:

| User Intent | Tool(s) to Call | Order |
|-------------|----------------|-------|
| "add task to buy milk" | `add_task` | After collecting all info + confirmation |
| "show my tasks" | `list_tasks(status="all")` | Immediately |
| "show pending tasks" | `list_tasks(status="pending")` | Immediately |
| "delete task 5" | `list_tasks(task_id=5)` → confirm → `delete_task` | 1. Get details, 2. Delete after yes |
| "delete the milk task" | `find_task(query="milk")` → confirm → `delete_task` | 1. Find task, 2. Delete after yes |
| "update task 3 to high priority" | `update_task` | After confirmation |
| "change the milk task to high priority" | `find_task` → `update_task` | 1. Find task ID, 2. Update |
| "mark task 7 as done" | `complete_task` | After confirmation |
| "complete the milk task" | `find_task` → `complete_task` | 1. Find task ID, 2. Complete |

**Never do**:
- ❌ Call `delete_task` without confirmation
- ❌ Use `list_tasks` when user mentions task by name (use `find_task` instead)
- ❌ Call tools without required parameters
- ❌ Respond "Done!" without actually calling the tool

---

## Next Steps

**Phase 1 Remaining**:
1. ✅ data-model.md (complete)
2. ✅ contracts/mcp-tools.md (this file - complete)
3. ⏳ contracts/api-endpoints.md - Chat API contract
4. ⏳ quickstart.md - Developer setup
5. ⏳ Update agent context
