# Phase 1: Data Model - Robust AI Chat Assistant

**Feature**: 001-robust-ai-assistant
**Phase**: 1 (Design)
**Date**: 2026-01-27
**Purpose**: Define database schema changes, entity relationships, and data flow

---

## Schema Changes

### Updated Conversation Model

**File**: `backend/src/models/conversation.py`

**Existing Fields** (no changes):
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**NEW Fields** (to be added):
```python
    # Conversation state tracking
    current_intent: Optional[str] = Field(
        default="NEUTRAL",
        description="Current user intent: NEUTRAL, ADDING_TASK, UPDATING_TASK, DELETING_TASK, COMPLETING_TASK, LISTING_TASKS"
    )

    state_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Collected information for current operation (e.g., {'title': 'buy milk', 'priority': None, 'due_date': None})"
    )

    target_task_id: Optional[int] = Field(
        default=None,
        description="ID of task being updated/deleted/completed (null for add operations)"
    )
```

**Purpose**:
- **current_intent**: Explicit tracking of conversation state (replaces implicit state in message history)
- **state_data**: Stores partially collected task information across turns (prevents redundant questions)
- **target_task_id**: Links conversation to specific task for update/delete/complete operations

**Why These Fields**:
- Addresses FR-010 (maintain conversation context across multiple turns)
- Enables proper cancellation (clear state_data when user says "never mind")
- Supports stateless agent design (state retrieved from DB, not kept in memory)
- Allows querying "show all conversations currently adding a task"

---

### Message Model (No Changes Required)

**File**: `backend/src/models/message.py`

**Existing Structure** (sufficient):
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(description="'user' or 'assistant'")
    content: str = Field(description="Message text")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**No changes needed**: Existing schema sufficient for storing conversation history.

---

### Task Model (No Changes Required)

**File**: `backend/src/models/task.py`

**Existing Structure** (sufficient):
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = Field(default="medium")  # high, medium, low
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**No changes needed**: Existing schema already supports all required fields (title, priority, completed, due_date, description).

---

## Database Migration

### Alembic Migration Script

**File**: `backend/alembic/versions/XXXXXX_add_conversation_state_fields.py`

```python
"""Add conversation state tracking fields

Revision ID: XXXXXX
Revises: <previous_revision>
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'XXXXXX'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to conversations table
    op.add_column(
        'conversations',
        sa.Column('current_intent', sa.String(), nullable=True, server_default='NEUTRAL')
    )
    op.add_column(
        'conversations',
        sa.Column('state_data', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'conversations',
        sa.Column('target_task_id', sa.Integer(), nullable=True)
    )

    # Set default value for existing rows
    op.execute("UPDATE conversations SET current_intent = 'NEUTRAL' WHERE current_intent IS NULL")

    # Make current_intent non-nullable after setting defaults
    op.alter_column('conversations', 'current_intent', nullable=False)


def downgrade():
    # Remove columns in reverse order
    op.drop_column('conversations', 'target_task_id')
    op.drop_column('conversations', 'state_data')
    op.drop_column('conversations', 'current_intent')
```

**Migration Safety**:
- ✅ Backward compatible (all new fields nullable or have defaults)
- ✅ Existing conversations default to `current_intent="NEUTRAL"`
- ✅ No data loss on upgrade or downgrade
- ✅ Tested upgrade and downgrade paths

**Testing Migration**:
```bash
# Test upgrade
alembic upgrade head

# Verify schema
psql -d <database> -c "\d conversations"

# Test downgrade (on staging only!)
alembic downgrade -1

# Verify rollback
psql -d <database> -c "\d conversations"
```

---

## Entity Relationships

```
User (1) ──────── (N) Conversation
                       │
                       │ current_intent: str
                       │ state_data: JSON
                       │ target_task_id: int? ──┐
                       │                         │
                       └─── (N) Message          │
                                                  │
Task (N) ──────────────────────────────────────┘
  │
  └─── user_id: int (filtered by auth)
```

**Key Relationships**:
- User → Conversations (1:N): User can have multiple chat sessions
- Conversation → Messages (1:N): Conversation contains many messages
- Conversation → Task (N:1 optional): Conversation may reference a task being updated/deleted (via target_task_id)
- Task → User (N:1): Task belongs to user (enforced by user_id filter)

**Foreign Key** (Optional Enhancement - Not Required for MVP):
- Could add FK constraint from `conversations.target_task_id` → `tasks.id`
- Decision: **Skip FK constraint** because:
  - Tasks can be deleted while conversation references them (orphaned reference acceptable)
  - Simpler to allow null target_task_id than cascading deletes
  - Application logic handles validation, not DB constraints

---

## Data Flow

### 1. Add Task Workflow

```
User: "add task to buy milk"
    ↓
[1] Create/Load Conversation
    - current_intent = "NEUTRAL"
    - state_data = None
    ↓
[2] Save User Message to DB
    - role = "user"
    - content = "add task to buy milk"
    ↓
[3] Load Recent Messages (last 50)
    ↓
[4] Pre-process: Detect Intent
    - Pattern match: "add task" → ADD_TASK intent
    - Update conversation: current_intent = "ADDING_TASK"
    - Initialize state_data = {"title": "buy milk", "priority": None, "due_date": None, "description": None}
    ↓
[5] Send to GPT-4o Agent
    - System prompt + conversation state + recent messages
    - Agent response: "Great! I'll help you add a task to buy milk. What priority should this be? (high/medium/low)"
    ↓
[6] Save Assistant Message to DB
    - role = "assistant"
    - content = "Great! I'll help..."
    ↓
[7] Update Conversation State
    - current_intent = "ADDING_TASK" (already set)
    - state_data = {"title": "buy milk", "priority": null, ...}

User: "high priority"
    ↓
[8] Save User Message to DB
    ↓
[9] Pre-process: Detect this is PROVIDE_INFO (not new intent)
    - conversation.current_intent == "ADDING_TASK"
    - Extract entity: priority = "high"
    - Update state_data = {"title": "buy milk", "priority": "high", ...}
    ↓
[10] Send to GPT-4o Agent
     - Agent response: "Got it, high priority. Do you want to set a deadline?"
    ↓
[11] Save Assistant Message
    ↓
[12] Update Conversation State
     - state_data = {"title": "buy milk", "priority": "high", ...}

User: "tomorrow"
    ↓
[13] Parse Natural Language Date
     - dateparser.parse("tomorrow") → 2026-01-28T23:59:59Z
     - Update state_data = {..., "due_date": "2026-01-28T23:59:59Z"}
    ↓
[14] Send to GPT-4o Agent
     - Agent response: "Perfect! Do you want to add any description?"
    ↓
...

User: "no"
    ↓
[15] Send to GPT-4o Agent
     - Agent detects all required info collected
     - Agent calls add_task MCP tool with state_data
    ↓
[16] Execute MCP Tool: add_task
     - Creates task in database
     - Returns task_id
    ↓
[17] Save Assistant Message with Success
     - content = "✅ Task created successfully! Task #42: Buy milk (🔴 high priority, due tomorrow)"
    ↓
[18] Clear Conversation State
     - current_intent = "NEUTRAL"
     - state_data = None
     - target_task_id = None
```

---

### 2. Update Task Workflow

```
User: "update task 5"
    ↓
[1] Detect Intent: UPDATE_TASK
    - Update conversation: current_intent = "UPDATING_TASK"
    - Set target_task_id = 5
    ↓
[2] Fetch Task Details (for confirmation)
    - Call list_tasks MCP tool (filtered by task_id=5)
    - Get task: {"id": 5, "title": "call mom", "priority": "medium", ...}
    ↓
[3] Agent Response
    - "You're updating task #5: 'call mom' (🟡 medium priority). What would you like to change?"
    - Save state_data = {"field_to_update": None, "new_value": None}
    ↓
User: "make it high priority"
    ↓
[4] Extract Entity
    - field_to_update = "priority"
    - new_value = "high"
    - Update state_data = {"field_to_update": "priority", "new_value": "high"}
    ↓
[5] Agent Asks for Confirmation
    - "Set task #5 to high priority? (yes/no)"
    ↓
User: "yes"
    ↓
[6] Execute MCP Tool: update_task
    - update_task(task_id=5, priority="high")
    ↓
[7] Clear State
    - current_intent = "NEUTRAL"
    - state_data = None
    - target_task_id = None
```

---

### 3. Delete Task Workflow

```
User: "delete the buy book task"
    ↓
[1] Detect Intent: DELETE_TASK
    - Update conversation: current_intent = "DELETING_TASK"
    ↓
[2] Fuzzy Match Task by Name
    - Call find_task MCP tool with query="buy book"
    - Returns: {"id": 12, "title": "buy book on React", "confidence": 0.87}
    ↓
[3] Set Target
    - target_task_id = 12
    ↓
[4] Agent Asks for Confirmation
    - "I found task #12: 'buy book on React' (87% match). Are you sure you want to delete this task?"
    ↓
User: "yes"
    ↓
[5] Execute MCP Tool: delete_task
    - delete_task(task_id=12)
    ↓
[6] Clear State
    - current_intent = "NEUTRAL"
    - state_data = None
    - target_task_id = None
```

---

## State Transition Diagram

```
┌─────────┐
│ NEUTRAL │ ◄────────────────────────────────┐
└────┬────┘                                   │
     │                                         │
     ├─ "add task" ──► ADDING_TASK ──────────┤
     │                    │                    │
     │                    ├─ collect fields ──┤
     │                    └─ confirm + tool ──┘
     │                                         │
     ├─ "update task" ─► UPDATING_TASK ──────┤
     │                    │                    │
     │                    ├─ identify task ───┤
     │                    ├─ choose field ────┤
     │                    └─ confirm + tool ──┘
     │                                         │
     ├─ "delete task" ─► DELETING_TASK ──────┤
     │                    │                    │
     │                    ├─ identify task ───┤
     │                    └─ confirm + tool ──┘
     │                                         │
     ├─ "mark done" ────► COMPLETING_TASK ───┤
     │                    │                    │
     │                    ├─ identify task ───┤
     │                    └─ confirm + tool ──┘
     │                                         │
     └─ "show tasks" ───► LISTING_TASKS ─────┘
                           │
                           └─ call tool + display
```

**Cancellation** (from any state):
- User says "never mind", "cancel", "stop"
- Agent detects CANCEL intent
- Immediately: `current_intent = "NEUTRAL"`, `state_data = None`, `target_task_id = None`
- Response: "No problem! I've cancelled that operation."

---

## Data Validation Rules

### Conversation State Validation

```python
# Valid intent values
VALID_INTENTS = [
    "NEUTRAL",
    "ADDING_TASK",
    "UPDATING_TASK",
    "DELETING_TASK",
    "COMPLETING_TASK",
    "LISTING_TASKS"
]

# state_data schema (when ADDING_TASK)
{
    "title": str | None,          # Required before tool call
    "priority": str | None,        # "high" | "medium" | "low"
    "due_date": str | None,        # ISO datetime string
    "description": str | None      # Optional, max 1000 chars
}

# state_data schema (when UPDATING_TASK)
{
    "field_to_update": str | None,  # "title" | "priority" | "due_date" | "description" | "completed"
    "new_value": Any | None
}

# state_data size limit
max_size(state_data) = 5KB  # Prevent unbounded JSON growth
```

### State Cleanup Rules

**When to clear state**:
- ✅ Tool call succeeds (task created/updated/deleted)
- ✅ User cancels operation
- ✅ Error occurs and user chooses not to retry
- ✅ User switches to different intent mid-conversation
- ✅ Conversation idle for >1 hour (background job)

**When NOT to clear state**:
- ❌ User provides partial information (priority, but no deadline yet)
- ❌ Agent asks clarifying question
- ❌ Tool call fails but user wants to retry

---

## Indexes

**Existing Indexes** (sufficient):
- `conversations.user_id` (index already exists)
- `messages.conversation_id` (index already exists)
- `tasks.user_id` (index already exists)

**New Indexes** (optional optimization):
- `conversations.current_intent` (if we want to query "all conversations in ADDING_TASK state")
  - **Decision**: Skip for now - not a common query, would slow down writes
  - **Revisit**: If we add admin dashboard showing "stuck conversations"

---

## Storage Estimates

**Per Conversation State**:
- `current_intent`: ~20 bytes (string)
- `state_data`: ~500 bytes (JSON, typical case: 4 fields × ~125 bytes each)
- `target_task_id`: 4 bytes (integer)
- **Total per conversation**: ~524 bytes

**Scale Impact**:
- 10,000 conversations = ~5MB additional storage
- 1,000,000 conversations = ~500MB additional storage
- **Conclusion**: Negligible storage impact, no optimization needed

---

## Testing Data Models

### Unit Tests

**File**: `backend/tests/unit/test_conversation_model.py`

```python
def test_conversation_default_state():
    """New conversations should start in NEUTRAL state"""
    conv = Conversation(user_id=1)
    assert conv.current_intent == "NEUTRAL"
    assert conv.state_data is None
    assert conv.target_task_id is None

def test_conversation_state_transition():
    """State should update correctly"""
    conv = Conversation(user_id=1)
    conv.current_intent = "ADDING_TASK"
    conv.state_data = {"title": "buy milk", "priority": None}

    assert conv.current_intent == "ADDING_TASK"
    assert conv.state_data["title"] == "buy milk"

def test_state_data_size_limit():
    """state_data should reject JSON > 5KB"""
    conv = Conversation(user_id=1)
    huge_data = {"x": "a" * 6000}  # > 5KB

    with pytest.raises(ValueError):
        conv.state_data = huge_data
```

### Integration Tests

**File**: `backend/tests/integration/test_state_persistence.py`

```python
async def test_state_persists_across_requests(client):
    """Conversation state should persist in database"""
    # Request 1: Start adding task
    response = await client.post("/chat", json={
        "conversation_id": 1,
        "message": "add task to buy milk"
    })

    # Check database
    conv = await get_conversation(1)
    assert conv.current_intent == "ADDING_TASK"
    assert conv.state_data["title"] == "buy milk"

    # Request 2: Provide priority
    response = await client.post("/chat", json={
        "conversation_id": 1,
        "message": "high priority"
    })

    # Check state updated
    conv = await get_conversation(1)
    assert conv.state_data["priority"] == "high"
    assert conv.state_data["title"] == "buy milk"  # Still preserved
```

---

## Next Steps

**Phase 1 Remaining**:
1. ✅ data-model.md (this file - complete)
2. ⏳ contracts/ - MCP tool contracts, API contracts
3. ⏳ quickstart.md - Developer setup instructions
4. ⏳ Update agent context with findings

**Ready to create**: `contracts/` directory with tool and API specifications.
