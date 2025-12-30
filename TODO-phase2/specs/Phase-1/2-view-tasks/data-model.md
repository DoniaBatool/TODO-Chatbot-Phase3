# Data Model: View Task List Feature

**Feature**: F002 - View Task List  
**Status**: ✅ Implemented

## Overview

The View Task List feature does not introduce new entities. It displays existing Task entities that are managed by the TaskManager.

## Data Model Reference

This feature uses the **Task entity** defined in Feature 1 (Add Task).

**See**: `specs/1-add-task/data-model.md` for complete Task entity specification.

## Task Entity Summary

```python
@dataclass
class Task:
    id: int              # Unique identifier
    title: str           # Task title (1-200 chars)
    description: str     # Optional description (max 1000 chars)
    completed: bool      # Completion status
    created_at: datetime # Creation timestamp
```

## Data Access Patterns

### Read Operations

This feature performs **read-only** operations on Task entities:

1. **Get All Tasks**
   ```python
   tasks: List[Task] = manager.get_all_tasks()
   ```
   - Returns all tasks in creation order
   - No filtering applied
   - Copy of list (not original)

2. **Get Pending Tasks**
   ```python
   pending: List[Task] = manager.get_pending_tasks()
   ```
   - Filters: `completed == False`
   - Used for summary count

3. **Get Completed Tasks**
   ```python
   completed: List[Task] = manager.get_completed_tasks()
   ```
   - Filters: `completed == True`
   - Used for summary count

## Display Data Flow

```
TaskManager.tasks (List[Task])
    ↓
get_all_tasks() / get_pending_tasks() / get_completed_tasks()
    ↓
List[Task] returned to CLI
    ↓
CLI formats for display:
    - Status icon based on completed field
    - Summary statistics calculated
    - Timestamp formatted
    - Description conditionally shown
    ↓
Display to user
```

## Data Aggregation

### Summary Statistics

The feature calculates three aggregate values:

```python
total_count: int = len(manager.get_all_tasks())
pending_count: int = len(manager.get_pending_tasks())
completed_count: int = len(manager.get_completed_tasks())
```

**Invariant**: `total_count == pending_count + completed_count`

## Display Formatting

### Field Transformations

| Task Field | Display Transformation |
|------------|----------------------|
| `completed` | → Status icon ([○] or [✓]) |
| `completed` | → Status text ("Pending" or "Completed") |
| `created_at` | → Formatted string (YYYY-MM-DD HH:MM:SS) |
| `description` | → Conditionally displayed (only if non-empty) |
| `title` | → Displayed as-is |
| `id` | → Displayed as-is |

### Example Transformation

**Task Object**:
```python
Task(
    id=1,
    title="Buy groceries",
    description="Milk, eggs",
    completed=False,
    created_at=datetime(2025, 12, 9, 14, 30, 0)
)
```

**Display Output**:
```
[○] ID: 1
    Title: Buy groceries
    Description: Milk, eggs
    Status: Pending
    Created: 2025-12-09 14:30:00
```

## Data Invariants

### No Modifications

**Critical Invariant**: This feature is **read-only**. It does not:
- ❌ Create new tasks
- ❌ Modify existing tasks
- ❌ Delete tasks
- ❌ Change task order

### State Consistency

After view operation:
- Task list unchanged
- Task properties unchanged
- Manager state unchanged

## Empty State Handling

When `len(manager.get_all_tasks()) == 0`:
- No task data to display
- Summary statistics: 0, 0, 0
- Special message shown: "No tasks found. Add some tasks to get started!"

## Performance Considerations

### Memory Usage

- **Read operation**: O(n) where n = number of tasks
- **Display operation**: O(n) for formatting
- **No additional storage**: Display is immediate, no caching

### Time Complexity

| Operation | Complexity |
|-----------|------------|
| Get all tasks | O(n) |
| Get pending tasks | O(n) |
| Get completed tasks | O(n) |
| Format display | O(n) |
| **Total** | **O(n)** |

### Scalability

For Phase I in-memory implementation:
- ✅ Handles 100 tasks: Instant
- ✅ Handles 1000 tasks: < 1 second
- ⚠️ Handles 10000+ tasks: May be slow on display

## Related Data Models

**Primary Entity**:
- Task (defined in `specs/1-add-task/data-model.md`)

**No New Entities**: This feature introduces no new data structures.

## Future Enhancements (Out of Scope)

**Phase II+** may add:
- Filtering by status (show only pending/completed)
- Sorting options (by date, title, priority)
- Pagination (show N tasks at a time)
- Search functionality

---

**Data Model Version**: 1.0  
**References**: Feature 1 Task Entity  
**Status**: ✅ Implemented  
**Last Updated**: 2025-12-09

