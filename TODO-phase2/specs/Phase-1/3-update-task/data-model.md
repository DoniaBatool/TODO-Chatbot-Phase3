# Data Model: Update Task Feature

**Feature**: F003 - Update Task  
**Status**: ✅ Implemented

## Data Model Reference

This feature **modifies** the existing Task entity defined in Feature 1.

**See**: `specs/1-add-task/data-model.md` for complete Task entity specification.

## Mutable Fields

The following Task fields can be updated:

| Field | Mutable | Validation |
|-------|---------|------------|
| `id` | ❌ No | Immutable (never changes) |
| `title` | ✅ Yes | 1-200 chars, non-empty, trimmed |
| `description` | ✅ Yes | Max 1000 chars, can be empty, trimmed |
| `completed` | ❌ No | Use Feature 4 (Mark Complete) |
| `created_at` | ❌ No | Immutable (never changes) |

## Update Operations

### Partial Update Support

```python
# Update title only (description unchanged)
manager.update_task(task_id, title="New title")

# Update description only (title unchanged)
manager.update_task(task_id, description="New description")

# Update both
manager.update_task(task_id, title="New title", description="New desc")
```

### Data Flow

```
User Input (CLI)
    ↓
Get task by ID
    ↓
Show current values
    ↓
Get new values (optional)
    ↓
Validate new values
    ↓
Update task fields
    ↓
Task modified in-place
```

## Validation Rules

Same as Feature 1 (Add Task):
- Title: 1-200 chars, non-empty, trimmed
- Description: Max 1000 chars, trimmed

---

**Data Model Version**: 1.0  
**References**: Feature 1 Task Entity  
**Status**: ✅ Implemented

