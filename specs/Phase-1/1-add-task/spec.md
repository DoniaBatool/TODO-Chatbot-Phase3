# Feature Specification: Add Task

**Feature ID**: F001  
**Priority**: P1 (Critical)  
**Status**: ✅ Implemented  
**Phase**: Phase I - Console App

## Overview

Enable users to create new todo items through the command-line interface. Each task consists of a required title and an optional description. The system automatically assigns a unique ID and timestamp to each new task.

## Business Context

**Problem**: Users need a quick way to capture tasks and todos as they think of them.

**Solution**: Provide a simple, interactive CLI prompt that captures task title and optional description with automatic ID generation.

**Value**: Reduces friction in task creation, ensuring no ideas are lost.

## User Stories

### US1: Create Task with Title Only
**Priority**: P1

**As a** busy user  
**I want to** create a task with just a title  
**So that** I can quickly capture todos without writing lengthy descriptions

**Acceptance Criteria**:
- User can enter a title when prompted
- System accepts titles between 1-200 characters
- Task is created with default empty description
- System confirms task creation with assigned ID
- Task appears in task list with "Pending" status
- Timestamp is automatically captured

**Definition of Done**:
- [ ] Title prompt displays correctly
- [ ] Title validation works (1-200 chars)
- [ ] Task created successfully in memory
- [ ] Confirmation message shows task ID
- [ ] Task retrievable from task list
- [ ] Unit tests passing

### US2: Create Task with Title and Description
**Priority**: P1

**As a** user managing complex tasks  
**I want to** create a task with both title and description  
**So that** I can add detailed context about what needs to be done

**Acceptance Criteria**:
- User can enter title first, then description
- System accepts descriptions up to 1000 characters
- Both fields are stored correctly
- System confirms task creation with full details
- Description is optional (can be skipped)

**Definition of Done**:
- [ ] Description prompt displays after title
- [ ] Description validation works (max 1000 chars)
- [ ] Both fields stored correctly
- [ ] Confirmation shows both title and description
- [ ] Unit tests passing

### US3: Input Validation with Clear Error Messages
**Priority**: P1

**As a** user  
**I want to** receive clear error messages for invalid input  
**So that** I know how to fix my mistakes and successfully create tasks

**Acceptance Criteria**:
- Empty title shows error: "Title cannot be empty"
- Title > 200 chars shows error with character count
- Description > 1000 chars shows error with character count
- User can retry after each error without losing context
- Leading/trailing whitespace is automatically trimmed

**Definition of Done**:
- [ ] All validation rules implemented
- [ ] Error messages are user-friendly
- [ ] Retry logic works correctly
- [ ] Whitespace trimming functional
- [ ] Unit tests for all edge cases

## Functional Requirements

### FR1: Task ID Generation
- System MUST auto-generate unique integer IDs
- IDs MUST start from 1 and increment sequentially
- IDs MUST NEVER be reused (even after task deletion)
- IDs MUST be assigned at task creation time

### FR2: Timestamp Generation
- System MUST automatically capture creation timestamp
- Format MUST be ISO 8601 compatible
- Timezone MUST be system local time
- Timestamp MUST be immutable after creation

### FR3: Default Values
- `completed`: MUST default to False for new tasks
- `description`: MUST default to empty string if not provided
- `id`: MUST be auto-generated (next available)
- `created_at`: MUST be current timestamp

### FR4: Input Validation Rules

| Field | Min Length | Max Length | Required | Validation |
|-------|-----------|-----------|----------|------------|
| title | 1 char | 200 chars | Yes | Cannot be empty or whitespace-only |
| description | 0 chars | 1000 chars | No | Can be empty |

### FR5: Data Integrity
- Title MUST be trimmed of leading/trailing whitespace
- Description MUST be trimmed of leading/trailing whitespace
- Empty strings after trimming MUST be rejected for title
- Task MUST NOT be created if validation fails

## User Interface Flow

```
1. User selects "Add Task" from main menu
2. System displays: "Enter task title: "
3. User enters title
4. System validates title:
   a. If empty/whitespace → Show error, go to step 2
   b. If > 200 chars → Show error with count, go to step 2
   c. If valid → Continue to step 5
5. System displays: "Enter description (optional, press Enter to skip): "
6. User enters description or presses Enter
7. System validates description:
   a. If > 1000 chars → Show error with count, go to step 5
   b. If valid → Continue to step 8
8. System creates task with:
   - Auto-generated ID (next_id)
   - Trimmed title
   - Trimmed description (or empty string)
   - completed = False
   - created_at = current timestamp
9. System displays confirmation:
   "✓ Task added successfully!"
   "ID: [id]"
   "Title: [title]"
   "[Description: [desc]]" (if provided)
   "Status: Pending"
10. Wait for Enter key
11. Return to main menu
```

## Success Criteria

**Measurable Outcomes**:
- ✅ Task creation completes in < 10 seconds for typical input
- ✅ 100% of valid inputs result in successful task creation
- ✅ 100% of invalid inputs show appropriate error messages
- ✅ Zero data loss - all created tasks are immediately available
- ✅ User can create unlimited tasks (memory permitting)

**Quality Criteria**:
- ✅ All input validation rules enforced
- ✅ Error messages are clear and actionable
- ✅ No crashes or unexpected behavior
- ✅ Timestamps are accurate and consistent

## Data Model

### Task Entity

```python
@dataclass
class Task:
    id: int              # Auto-incremented unique identifier
    title: str           # 1-200 characters, required, trimmed
    description: str     # 0-1000 characters, optional, trimmed
    completed: bool      # Default: False
    created_at: datetime # Auto-generated, immutable
```

**Invariants**:
- `id` > 0 and unique across all tasks
- `title` length ∈ [1, 200] after trimming
- `description` length ∈ [0, 1000] after trimming
- `completed` is always boolean
- `created_at` is set once at creation

## Assumptions

1. **Single User**: Only one user interacting with the CLI at a time
2. **Memory Storage**: Data persists only during program execution
3. **Local Time**: All timestamps in system local timezone
4. **Terminal Support**: Unicode characters display correctly
5. **No Concurrency**: Sequential task creation only

## Dependencies

**Internal**:
- Task model (task.py) with validation
- TaskManager (manager.py) for ID generation and storage
- CLI interface (cli.py) for user interaction

**External**:
- Python 3.13+ standard library (datetime, dataclasses)

## Out of Scope

- ❌ Task editing after creation (separate feature)
- ❌ Task deletion (separate feature)
- ❌ Task prioritization (future phase)
- ❌ Tags or categories (future phase)
- ❌ Due dates (future phase)
- ❌ File persistence (future phase)
- ❌ Multi-user support (future phase)

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Memory overflow with many tasks | High | Low | No file persistence in Phase I |
| Invalid UTF-8 in user input | Medium | Low | Python handles UTF-8 by default |
| User confusion with error messages | Medium | Medium | Clear, actionable error text |
| ID collision | High | Very Low | Sequential ID generation prevents this |

## Testing Strategy

**Unit Tests**:
- Task model validation (empty title, long title, long description)
- Whitespace trimming
- ID generation and uniqueness
- Timestamp generation

**Integration Tests**:
- TaskManager.add_task() with various inputs
- Error handling flow
- Task retrieval after creation

**Manual Tests**:
- Interactive CLI flow end-to-end
- Error message display
- Confirmation message display

## Related Features

**Depends On**: None (foundational feature)

**Blocks**:
- View Task List (F002)
- Update Task (F003)
- Mark Complete (F004)
- Delete Task (F005)

**Related**:
- All other Phase I features depend on this

---

**Specification Version**: 1.0  
**Created**: 2025-12-09  
**Last Updated**: 2025-12-09  
**Status**: ✅ Implemented and Tested

