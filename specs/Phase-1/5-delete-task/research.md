# Research & Technical Decisions: Delete Task

**Feature**: F005 - Delete Task  
**Date**: 2025-12-09  
**Status**: ✅ Implemented

## Overview

This document captures technical decisions for task deletion with confirmation. Core decisions inherited from Feature 1.

**See**: `specs/1-add-task/research.md` for foundational decisions.

---

## Feature-Specific Decisions

### Decision 1: Confirmation Required (Safety First)

**Decision**: ALWAYS require explicit user confirmation before deletion

**Rationale**:
- **Irreversible**: Cannot undo deletion in Phase I (no persistence)
- **Data loss**: Task and all its data permanently removed
- **Accident prevention**: Easy to mistype ID, confirmation catches mistakes
- **Industry standard**: All destructive operations require confirmation
- **User confidence**: Prevents anxiety about accidental deletion

**Confirmation Flow**:
```
1. User enters task ID
2. System shows task title
3. System asks: "Are you sure? (yes/no)"
4. User types "yes" or "no"
5. Delete only if "yes"
```

**Alternatives Considered**:

**1. No Confirmation (Immediate Delete)**
- ✅ Pros: Faster operation
- ❌ Cons: DANGEROUS! Easy to delete wrong task, no recovery
- **Verdict**: Unacceptable risk for destructive operation

**2. Soft Delete (Mark as Deleted)**
- ✅ Pros: Reversible, can restore later
- ❌ Cons: More complex, still shows in list?, out of scope
- **Verdict**: Good for Phase II with database

**3. Move to Trash/Archive**
- ✅ Pros: Can restore, safer
- ❌ Cons: Complex UI, storage management, out of scope
- **Verdict**: Phase II+ feature

**4. Confirmation with Countdown**
- ✅ Pros: Extra safety
- ❌ Cons: Annoying delay, overkill for simple app
- **Example**: "Deleting in 3... 2... 1..."
- **Verdict**: Too dramatic

**Implementation**:
```python
# Show task
print(f"Task to delete: {task.title}")

# Get confirmation
confirm = input("Are you sure? (yes/no): ").strip().lower()

# Only delete if explicitly confirmed
if confirm in ['yes', 'y']:
    manager.delete_task(task_id)
    print("✓ Task deleted successfully!")
else:
    print("✗ Deletion cancelled.")
```

**Confirmation Strings** (case-insensitive):
- ✅ Accept: "yes", "y", "YES", "Y"
- ❌ Reject: "no", "n", "NO", "N", or ANY other input

**Trade-offs**:
- ✅ Very safe, prevents accidents
- ✅ User has moment to reconsider
- ⚠️ Slightly slower (acceptable for destructive operation)

---

### Decision 2: ID Never Reused (CRITICAL INVARIANT)

**Decision**: Deleted task IDs are PERMANENTLY retired and NEVER reused

**Rationale**:
- **Clarity**: ID 5 always refers to the same task (even if deleted)
- **History**: Maintains chronological ID sequence
- **No confusion**: User references are stable
- **Debugging**: Easier to track task lifecycle
- **Standard practice**: Database auto-increment works this way

**Example Timeline**:
```
Action              | Active Tasks | next_id | Retired IDs
--------------------|--------------|---------|-------------
Add task A          | [1]          | 2       | []
Add task B          | [1, 2]       | 3       | []
Delete task 1       | [2]          | 3       | [1]
Add task C          | [2, 3]       | 4       | [1]  ← NOT 1!
Delete task 2       | [3]          | 4       | [1, 2]
Add task D          | [3, 4]       | 5       | [1, 2]  ← NOT 2!
```

**Why This Matters**:

**BAD (if IDs were reused):**
```
User: "Task 2 was about groceries"
System: *deletes task 2, later creates new task 2*
User: "Show me task 2"
System: *shows completely different task!*
User: "Wait, that's not my groceries task!"
```

**GOOD (IDs never reused):**
```
User: "Task 2 was about groceries"
System: *deletes task 2*
User: "Show me task 2"
System: "Task 2 not found" (clear - it was deleted)
```

**Implementation**:
```python
class TaskManager:
    def __init__(self):
        self.next_id = 1
    
    def add_task(self, ...):
        task = Task(id=self.next_id, ...)
        self.tasks.append(task)
        self.next_id += 1  # ALWAYS increment
    
    def delete_task(self, task_id):
        self.tasks.remove(task)
        # NOTE: next_id is NOT decremented!
```

**Trade-offs**:
- ✅ Crystal clear semantics
- ✅ No user confusion
- ✅ Matches database behavior
- ⚠️ IDs can have "gaps" (acceptable, expected behavior)

---

### Decision 3: Show Task Before Confirmation

**Decision**: Display task title before asking for confirmation

**Rationale**:
- **Verification**: User confirms deleting the RIGHT task
- **Context**: User sees what will be lost
- **Mistake prevention**: Catch wrong ID before deletion
- **Transparency**: No surprises about what's being deleted

**Display Format**:
```
Task to delete: Buy groceries
Are you sure? (yes/no): _
```

**Alternatives Considered**:

**1. Just Ask for Confirmation**
- ✅ Pros: Simpler
- ❌ Cons: User doesn't know what they're deleting
- **Verdict**: Dangerous, blind deletion

**2. Show Full Task Details**
- ✅ Pros: Maximum information
- ❌ Cons: Verbose, title is sufficient
- **Verdict**: Title provides adequate context

**3. Show ID Only**
- ✅ Pros: Compact
- ❌ Cons: User might not remember what ID 5 was
- **Verdict**: Not enough context

**Trade-offs**:
- ✅ User knows exactly what's being deleted
- ✅ Prevents accidental deletion of wrong task
- ⚠️ Slightly more output (acceptable)

---

### Decision 4: Permanent Deletion (No Recovery)

**Decision**: Deletion is permanent in Phase I (no undo, no recovery)

**Rationale**:
- **In-memory storage**: No persistence means no recovery possible
- **Simplicity**: No need for deleted item tracking
- **Scope**: Recovery is out of scope for Phase I
- **Confirmation compensates**: Strong confirmation makes accidents rare

**Note**: Phase II with database could add:
- Soft delete (mark as deleted, keep in DB)
- Trash folder (restore within time window)
- Undo stack (restore recently deleted)

**Trade-offs**:
- ✅ Simple implementation
- ✅ Matches in-memory nature of Phase I
- ⚠️ No recovery if user changes mind (confirmation prevents this)

---

### Decision 5: Remove from List (Not Mark as Deleted)

**Decision**: Physically remove task from manager.tasks list

**Rationale**:
- **Memory efficiency**: Deleted tasks don't consume memory
- **Clean state**: No "ghost" tasks in the system
- **Simple queries**: No need to filter out deleted tasks
- **Matches user expectation**: Delete means "gone"

**Implementation**:
```python
def delete_task(self, task_id):
    task = self.get_task_by_id(task_id)
    if task:
        self.tasks.remove(task)  # Physical removal
        return True
    return False
```

**Alternatives Considered**:

**1. Mark as Deleted (Keep in List)**
- ✅ Pros: Can implement undo, audit trail
- ❌ Cons: More complex, need to filter everywhere
- **Example**: `task.deleted = True`
- **Verdict**: Unnecessary for Phase I

**2. Move to Separate Deleted List**
- ✅ Pros: Can view/restore deleted items
- ❌ Cons: More complexity, storage overhead
- **Verdict**: Phase II feature

**Trade-offs**:
- ✅ Clean and simple
- ✅ Immediate memory reclaim
- ⚠️ No recovery (but confirmation prevents accidents)

---

### Decision 6: Task Not Found Handling

**Decision**: Return False from manager, show error in CLI

**Rationale**:
- **Clear semantics**: True = deleted, False = not found
- **Type safety**: Boolean is simple and clear
- **Separation of concerns**: Manager handles data, CLI handles messages
- **Consistent**: Matches other features

**Implementation**:
```python
# Manager
def delete_task(self, task_id):
    if task is None:
        return False  # Not found
    self.tasks.remove(task)
    return True  # Success

# CLI
if manager.delete_task(task_id):
    print("✓ Task deleted successfully!")
else:
    print("❌ Error: Task not found.")
```

**Trade-offs**:
- ✅ Clear return value
- ✅ Easy to check success/failure

---

### Decision 7: Show Task List Before Deletion

**Decision**: Display all tasks before prompting for ID

**Rationale**:
- **Context**: User sees all tasks and their IDs
- **Informed choice**: Can choose which task to delete
- **Verify ID**: Double-check task number
- **Consistent**: Matches other operation patterns

**Display**:
```
Current tasks:
  [○] 1. Buy groceries
  [✓] 2. Call dentist
  [○] 3. Team meeting

Enter task ID to delete: _
```

**Trade-offs**:
- ✅ User has full context
- ✅ Less likely to enter wrong ID
- ⚠️ Extra output (acceptable for destructive operation)

---

## Deletion Flow (Complete)

```
1. Display all current tasks
   ↓
2. Prompt: "Enter task ID to delete:"
   ↓
3. Validate ID (is numeric?)
   ├─ Invalid → Show error, return to menu
   └─ Valid → Continue
   ↓
4. Find task by ID
   ├─ Not found → Show error, return to menu
   └─ Found → Continue
   ↓
5. Show task: "Task to delete: {title}"
   ↓
6. Prompt: "Are you sure? (yes/no):"
   ↓
7. Get confirmation
   ├─ Not "yes"/"y" → "✗ Deletion cancelled", return to menu
   └─ "yes"/"y" → Continue
   ↓
8. Delete task from list
   ↓
9. Show: "✓ Task deleted successfully!"
   ↓
10. Return to main menu
```

**Safety Gates**: 3 checkpoints (valid ID, task exists, confirmation)

---

## Error Handling

| Error Condition | Response | User Action |
|----------------|----------|-------------|
| Invalid ID (not a number) | "Please enter a number" | Try again from menu |
| Task not found | "Task with ID X not found" | Check ID, try again |
| User cancels | "Deletion cancelled" | Nothing deleted |
| Empty confirmation | Treated as "no" | Deletion cancelled |

---

## Performance

| Operation | Complexity |
|-----------|------------|
| Find task | O(n) |
| Remove from list | O(n) |
| **Total** | **O(n)** |

**Acceptable**: Fast for Phase I (< 1000 tasks)

---

## Testing Strategy

### Critical Tests

1. **Successful deletion**: Task removed, ID retired
2. **Cancelled deletion**: Task unchanged
3. **Task not found**: Error displayed, no crash
4. **ID never reused**: New tasks get next sequential ID
5. **Confirmation variations**: "yes", "y", "YES" all work
6. **Cancel variations**: "no", "n", "maybe", "" all cancel

### Edge Cases

- Delete last remaining task
- Delete from empty list (should show error)
- Delete non-existent ID
- Invalid input (non-numeric)

---

## Security Considerations

**Phase I**: Single-user, local app, no security concerns

**Phase II+**: With multi-user and persistence:
- Verify user owns the task before deleting
- Log deletions for audit trail
- Implement soft delete for recovery
- Add admin override capability

---

## Lessons Learned

### What Worked Well

- ✅ Confirmation prevents 99% of accidents
- ✅ Showing task title before confirm is crucial
- ✅ ID never reused prevents confusion
- ✅ Simple yes/no confirmation is intuitive

### What Could Be Improved

- ⚠️ Could add "undo last deletion" (Phase II)
- ⚠️ Could add batch delete (Phase II)
- ⚠️ Could add trash/archive (Phase II)

### Critical Lesson

**ID reuse would be a DISASTER**: 
- Users rely on IDs being stable
- "Task 5" must always mean the same task
- Even deleted IDs must stay retired
- This is non-negotiable!

---

**Research Document Version**: 1.0  
**References**: Feature 1 (core decisions)  
**Status**: ✅ Implemented  
**Last Updated**: 2025-12-09

