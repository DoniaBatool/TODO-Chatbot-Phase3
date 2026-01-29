# Robust AI Chat Assistant Skill

## Overview

The Robust AI Chat Assistant provides natural language task management through multi-turn conversational workflows. Users can create, update, delete, list, and complete tasks using natural language commands.

## Features

### User Stories Implemented

| Priority | User Story | Description |
|----------|-----------|-------------|
| P1 | US1 Natural Language Task Creation | Multi-turn workflow: title → priority → deadline → description → create |
| P1 | US2 Intent Recognition | Detects ADD, UPDATE, DELETE, LIST, COMPLETE, CANCEL intents |
| P2 | US3 Task Update | Update any field with confirmation |
| P2 | US4 Task Deletion | Delete with safety confirmation |
| P2 | US5 Task Listing | Rich formatting with emojis and human-readable dates |
| P3 | US6 Task Completion | Toggle complete/incomplete status |
| P3 | US7 Natural Language Dates | Parse "tomorrow", "next Friday", "in 3 days" |
| P3 | US8 Priority Keywords | Auto-detect urgent/important → high, someday/later → low |

## Intent Recognition

The assistant recognizes these intents:

```
ADD_TASK      - "add task", "create task", "new task", "remind me to"
UPDATE_TASK   - "update task", "change task", "modify task"
DELETE_TASK   - "delete task", "remove task"
LIST_TASKS    - "show tasks", "list tasks", "my tasks"
COMPLETE_TASK - "mark complete", "finish task", "done with"
CANCEL        - "cancel", "nevermind", "stop", "abort"
```

## Priority Keywords

**High Priority:** urgent, important, critical, ASAP, deadline, now, immediately, soon
**Low Priority:** someday, later, minor, trivial, optional, eventually, maybe
**Medium Priority:** (default) normal, regular, medium

## Natural Language Dates

Supported formats:
- Relative: "tomorrow", "next week", "in 3 days"
- Named: "next Friday", "this Monday"
- Absolute: "January 20", "Jan 20 at 2pm"
- ISO: "2026-02-15", "2026-02-15 14:30"

Validation:
- Rejects past dates with clarification prompt
- Rejects dates >10 years in the future
- Confidence scoring for ambiguous dates

## Multi-Turn Workflows

### Add Task Workflow
```
User: add task to buy milk
Bot: Got it! "Buy milk" - What priority? (high/medium/low)
User: high
Bot: When should this be done by?
User: tomorrow at 5pm
Bot: Any description to add?
User: Get 2% milk from the grocery store
Bot: ✅ Task created! #42: Buy milk (🔴 high priority, due Tomorrow at 5:00 PM)
```

### Update Task Workflow
```
User: update task 5
Bot: Task #5: "Buy groceries" (medium priority)
     What would you like to change?
User: make it high priority and due tomorrow
Bot: Confirm changes to Task #5:
     • Priority: medium → high
     • Due: → Tomorrow
     Proceed? (yes/no)
User: yes
Bot: ✅ Task #5 updated successfully!
```

### Delete Task Workflow
```
User: delete task 3
Bot: Are you sure you want to delete Task #3: "Old task"?
     This cannot be undone. (yes/no)
User: yes
Bot: ✅ Task #3 deleted.
```

## Task Display Formatting

```
📋 You have 3 tasks:

⏳ #1: Buy milk (🔴 high priority) - 📅 Due: Tomorrow at 5:00 PM
⏳ #2: Call mom (🟡 medium priority)
✅ #3: Finish report (🟢 low priority) - Done!
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_task` | Create new task with title, priority, due date, description |
| `update_task` | Update task fields (title, priority, due_date, description, completed) |
| `delete_task` | Delete task by ID with user isolation |
| `list_tasks` | List tasks with optional status/priority filters |
| `complete_task` | Mark task as complete/incomplete |
| `find_task` | Fuzzy search for task by title |

## Architecture

### Components

- **IntentClassifier** (`services/intent_classifier.py`): Pattern-based intent detection
- **ContextManager** (`ai_agent/context_manager.py`): Multi-turn workflow state
- **DateParser** (`utils/date_parser.py`): Natural language date parsing
- **FuzzyMatcher** (`utils/fuzzy_matcher.py`): Task title matching
- **TaskFormatter** (`utils/task_formatter.py`): Rich task display

### State Management

Conversation state stored in PostgreSQL:
- `current_intent`: Active workflow (NEUTRAL, ADDING_TASK, etc.)
- `state_data`: Collected information during workflow
- `target_task_id`: Task being operated on

## Test Coverage

- **644 tests passing**
- 238 edge case tests
- 99 priority detection tests
- 87 date parsing tests
- 28 task completion tests
- 31 task listing tests
- 57 task deletion tests
- 63 task update tests

## Usage

```python
# In chat endpoint
from src.services.intent_classifier import IntentClassifier
from src.ai_agent.context_manager import ContextManager

classifier = IntentClassifier()
result = classifier.classify(user_message, current_intent=conversation.current_intent)

if result.intent_type == Intent.ADD_TASK:
    context_manager.initialize_add_task_state(
        conversation_id=conversation.id,
        user_id=user.id,
        initial_title=result.extracted_entities.get("title")
    )
```

## Configuration

Environment variables:
- `DB_POOL_SIZE`: Database connection pool size (default: 5)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 10)
- `DB_POOL_TIMEOUT`: Connection timeout in seconds (default: 30)

## Related Skills

- `/sp.mcp-tool-builder` - Build MCP tools
- `/sp.chatbot-endpoint` - Stateless chat API
- `/sp.conversation-manager` - Conversation state
- `/sp.edge-case-tester` - Test edge cases
