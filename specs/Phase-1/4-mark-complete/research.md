# Research & Technical Decisions: Mark Task Complete

**Feature**: F004 - Mark Complete  
**Date**: 2025-12-09  
**Status**: ✅ Implemented

## Overview

This document captures technical decisions for toggling task completion status. Core decisions are inherited from Feature 1.

**See**: `specs/1-add-task/research.md` for foundational decisions.

---

## Feature-Specific Decisions

### Decision 1: Toggle vs Explicit Set

**Decision**: Toggle completion status (Pending ↔ Completed) rather than explicit set

**Rationale**:
- **Simplicity**: One action for both mark complete and mark incomplete
- **User-friendly**: Natural interaction (toggle what you see)
- **Fewer menu items**: Single option instead of two
- **Discoverable**: User learns toggle behavior quickly

**Behavior**:
```python
# If task.completed == False (Pending)
# Action: Mark as Complete
# Result: task.completed = True

# If task.completed == True (Completed)
# Action: Mark as Incomplete
# Result: task.completed = False
```

**Alternatives Considered**:

**1. Separate Menu Items (Mark Complete / Mark Incomplete)**
- ✅ Pros: Explicit, always clear what will happen
- ❌ Cons: More menu clutter, user must know current state
- **Verdict**: Toggle is more elegant

**2. Always Set to Complete (no toggle)**
- ✅ Pros: Simpler mental model
- ❌ Cons: Can't undo mistakes, need separate "incomplete" feature
- **Verdict**: Toggle provides both directions

**3. Three-State (Pending / In Progress / Complete)**
- ✅ Pros: More granular status
- ❌ Cons: More complex, out of scope for Phase I
- **Verdict**: Binary is sufficient (Phase I requirement)

**Implementation**:
```python
def mark_complete(self, task_id: int, completed: bool = True) -> Optional[Task]:
    task = self.get_task_by_id(task_id)
    if task:
        task.completed = completed  # Direct boolean assignment
    return task
```

**Trade-offs**:
- ✅ Simple and intuitive
- ✅ Single menu option
- ⚠️ Must check current state to know what will happen (acceptable)

---

### Decision 2: Immediate Update (No Confirmation)

**Decision**: Update status immediately without asking for confirmation

**Rationale**:
- **Reversible**: Toggle again to undo
- **Fast**: Common operation, confirmation would slow it down
- **Low risk**: Can't lose data, only change boolean flag
- **Standard**: Most todo apps don't confirm completion

**User Flow**:
```
1. User selects task ID
2. Status immediately toggled
3. Confirmation message shown
4. Done (back to menu)
```

**Alternatives Considered**:

**1. Require Confirmation**
- ✅ Pros: Prevents accidental changes
- ❌ Cons: Slows down common operation, unnecessary for reversible action
- **Verdict**: Confirmation overkill for toggle

**2. Show Current State First**
- ✅ Pros: User sees what will change
- ❌ Cons: Extra step, still not needed
- **Verdict**: Task list already shows current state

**3. Batch Complete (multiple tasks)**
- ✅ Pros: Efficient for many tasks
- ❌ Cons: More complex UI, out of scope
- **Verdict**: Phase II feature

**Trade-offs**:
- ✅ Fast operation
- ✅ Easy to undo (just toggle again)
- ⚠️ Could accidentally mark wrong task (user can fix immediately)

---

### Decision 3: Display Task Title in Confirmation

**Decision**: Show task title in confirmation message

**Rationale**:
- **Verification**: User confirms correct task was updated
- **Feedback**: Clear what just happened
- **Confidence**: User knows operation succeeded
- **Standard pattern**: Good UX practice

**Confirmation Format**:
```
✓ Task marked as completed!
Title: Buy groceries
```

Or:

```
✓ Task marked as pending!
Title: Buy groceries
```

**Alternatives Considered**:

**1. Generic Confirmation**
- ✅ Pros: Simpler
- ❌ Cons: Less informative
- **Example**: "✓ Task updated!"
- **Verdict**: Not specific enough

**2. Show Full Task Details**
- ✅ Pros: Maximum information
- ❌ Cons: Verbose for simple operation
- **Verdict**: Title is sufficient

**Trade-offs**:
- ✅ Informative feedback
- ✅ User verification
- ⚠️ Slightly more output (acceptable)

---

### Decision 4: Show Task List Before Selection

**Decision**: Display current tasks with status before prompting for ID

**Rationale**:
- **Context**: User sees all tasks and their current status
- **Informed choice**: Can decide which task to toggle
- **See current state**: Knows if task is already complete
- **Consistent**: Matches other operation patterns

**Display**:
```
Current tasks:
  [○] 1. Buy groceries
  [✓] 2. Call dentist
  [○] 3. Team meeting

Enter task ID: _
```

**Trade-offs**:
- ✅ User has full context
- ✅ Can see which tasks need toggling
- ⚠️ Extra output for single task (acceptable)

---

### Decision 5: Task Not Found Handling

**Decision**: Return None from manager, display friendly error in CLI

**Rationale**:
- **Separation of concerns**: Manager handles data, CLI handles display
- **Type safety**: Optional[Task] makes failure explicit
- **Flexibility**: CLI can customize error messages
- **Consistent**: Same pattern as other features

**Implementation**:
```python
# Manager
if task is None:
    return None

# CLI
result = manager.mark_complete(task_id)
if result is None:
    print(f"❌ Error: Task with ID {task_id} not found.")
```

**Trade-offs**:
- ✅ Clean code structure
- ✅ Flexible error handling

---

### Decision 6: No Timestamp for Completion

**Decision**: Do not add "completed_at" timestamp in Phase I

**Rationale**:
- **Simplicity**: Binary status is sufficient
- **Scope**: Not required for Phase I
- **Reversible**: Task can be toggled back, timestamp would be misleading
- **Future**: Can add in Phase II if needed

**Note**: Only `created_at` exists (never changes)

**Trade-offs**:
- ✅ Simpler data model
- ✅ Fewer fields to manage
- ⚠️ Can't track when task was completed (acceptable for Phase I)

---

### Decision 7: Boolean Flag (Not Status Enum)

**Decision**: Use simple boolean `completed` field instead of status enum

**Rationale**:
- **Simplicity**: True/False is clearest
- **Sufficient**: Phase I only needs two states
- **Performance**: Boolean is fast and space-efficient
- **Standard**: Common pattern for completion tracking

**Data Type**:
```python
completed: bool  # True = completed, False = pending
```

**Alternatives Considered**:

**1. Status Enum**
- ✅ Pros: Extensible (can add more states later)
- ❌ Cons: Overkill for binary state, more code
- **Example**: `status: Literal["pending", "in_progress", "completed"]`
- **Verdict**: Boolean is sufficient

**2. Integer (0/1/2/3...)**
- ✅ Pros: Can have many states
- ❌ Cons: Less readable, magic numbers
- **Verdict**: Not type-safe, unclear meaning

**Trade-offs**:
- ✅ Crystal clear (True/False)
- ✅ Type-safe
- ✅ Fast operations
- ⚠️ Limited to two states (acceptable for Phase I)

---

## Visual Representation

### Status Icons

**In Task List**:
- Pending: `[○]` (empty circle)
- Completed: `[✓]` (checkmark)

**Inherited from Feature 2**: See `specs/2-view-tasks/research.md` Decision 4

---

## State Machine

```
     ┌──────────────┐
     │   PENDING    │
     │ (False)      │
     └──────┬───────┘
            │
            │ mark_complete(True)
            │
            ▼
     ┌──────────────┐
     │  COMPLETED   │
     │  (True)      │
     └──────┬───────┘
            │
            │ mark_complete(False)
            │
            ▼
     ┌──────────────┐
     │   PENDING    │
     │  (False)     │
     └──────────────┘
```

**Transitions**: Bidirectional, unlimited toggles allowed

---

## Performance

| Operation | Complexity |
|-----------|------------|
| Find task | O(n) |
| Toggle boolean | O(1) |
| **Total** | **O(n)** |

**Acceptable**: Fast for Phase I scale

---

## Testing Strategy

### Test Cases

1. **Mark pending task as complete**: False → True
2. **Mark complete task as pending**: True → False
3. **Multiple toggles**: False → True → False → True
4. **Task not found**: Error message shown
5. **Invalid ID**: Error message shown
6. **Confirmation displays**: Title shown correctly

---

## Lessons Learned

### What Worked Well

- ✅ Toggle is intuitive and fast
- ✅ Immediate update feels responsive
- ✅ Boolean is simple and clear
- ✅ No confirmation needed (reversible)

### Future Enhancements

- Add "completed_at" timestamp (Phase II)
- Add completion history (Phase II+)
- Add progress tracking (percentage of tasks done)
- Add celebration for completing all tasks 🎉

---

**Research Document Version**: 1.0  
**References**: Feature 1, Feature 2  
**Status**: ✅ Implemented  
**Last Updated**: 2025-12-09

