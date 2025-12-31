# Data Model: Mark Complete Feature

**Feature**: F004 - Mark Complete  
**Status**: ✅ Implemented

## Data Model Reference

This feature **toggles** the `completed` field of the Task entity.

**See**: `specs/1-add-task/data-model.md` for complete Task entity specification.

## Modified Field

### completed: bool

**Purpose**: Tracks task completion status

**States**:
- `False` → Task is pending (not done)
- `True` → Task is completed (done)

**Operation**: Toggle between states

```python
task.completed = not task.completed  # Toggle
# OR
task.completed = True   # Mark complete
task.completed = False  # Mark incomplete
```

## State Transitions

```
┌─────────┐                    ┌───────────┐
│ Pending │ ──mark_complete──> │ Completed │
│ (False) │ <─mark_incomplete─ │  (True)   │
└─────────┘                    └───────────┘
```

## Immutable Fields

All other Task fields remain unchanged:
- ❌ `id` - Never changes
- ❌ `title` - Not modified
- ❌ `description` - Not modified
- ❌ `created_at` - Never changes

## Data Flow

```
User selects task by ID
    ↓
Get current completion status
    ↓
Toggle: completed = !completed
    ↓
Task state updated in-place
    ↓
Display new status
```

## Visual Impact

**In Task List Display**:
- Before: `[○] 1. Buy groceries` (Pending)
- After:  `[✓] 1. Buy groceries` (Completed)

---

**Data Model Version**: 1.0  
**References**: Feature 1 Task Entity  
**Status**: ✅ Implemented

