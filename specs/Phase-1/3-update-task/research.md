# Research & Technical Decisions: Update Task

**Feature**: F003 - Update Task  
**Date**: 2025-12-09  
**Status**: ✅ Implemented

## Overview

This document captures technical decisions specific to the Update Task feature. Foundational decisions are inherited from Feature 1.

**See**: `specs/1-add-task/research.md` for core technical decisions.

---

## Feature-Specific Decisions

### Decision 1: Partial Update Support

**Decision**: Allow updating title only, description only, or both fields

**Rationale**:
- **Flexibility**: User can change just what needs changing
- **Efficiency**: Don't force re-entering unchanged fields
- **User-friendly**: Skip fields to keep current values
- **Common pattern**: Standard in update operations

**Alternatives Considered**:

**1. Require Both Fields**
- ✅ Pros: Simpler implementation
- ❌ Cons: Poor UX, forces re-entering unchanged data
- **Verdict**: Too restrictive

**2. Full Replacement**
- ✅ Pros: Clear semantics (complete overwrite)
- ❌ Cons: Must re-enter all fields every time
- **Verdict**: Wasteful for user

**Implementation**:
```python
def update_task(self, task_id: int, 
                title: Optional[str] = None,
                description: Optional[str] = None) -> Optional[Task]:
    # Only update provided fields (None = keep current)
    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip()
```

**Trade-offs**:
- ✅ Maximum flexibility
- ✅ Excellent UX
- ⚠️ Slightly more complex (but manageable)

---

### Decision 2: Show Current Values Before Update

**Decision**: Display current task values before prompting for new ones

**Rationale**:
- **Context**: User sees what they're changing
- **Accuracy**: Can verify they're editing the right task
- **Reference**: Don't need to remember current values
- **Standard pattern**: Common in edit operations

**Display Format**:
```
Current Title: Buy groceries
Current Description: Milk, eggs, bread

Enter new values (press Enter to keep current):
New title: [user input or Enter]
New description: [user input or Enter]
```

**Alternatives Considered**:

**1. Don't Show Current Values**
- ✅ Pros: Less output
- ❌ Cons: User can't see what they're changing
- **Verdict**: Poor UX, user flying blind

**2. Pre-fill Input Fields**
- ✅ Pros: Very user-friendly, can edit current text
- ❌ Cons: Not supported in basic input(), requires special libraries
- **Verdict**: Too complex for Phase I console app

**Trade-offs**:
- ✅ Clear and informative
- ✅ Easy to implement
- ⚠️ Slightly more output (acceptable)

---

### Decision 3: Empty Input = Keep Current

**Decision**: Pressing Enter without typing keeps the current value

**Rationale**:
- **Intuitive**: Empty input naturally means "no change"
- **Fast**: Quick skip for unchanged fields
- **Safe**: Won't accidentally delete content
- **Standard**: Common pattern in CLI tools

**User Flow**:
```python
new_title = input("New title: ").strip()
if not new_title:  # Empty input = keep current
    # Don't update title
    pass
else:
    # Update with new value
    task.title = new_title
```

**Alternatives Considered**:

**1. Empty Input = Clear Field**
- ✅ Pros: Simple interpretation
- ❌ Cons: Could accidentally clear important data
- **Verdict**: Too dangerous

**2. Special Keyword (e.g., "SKIP")**
- ✅ Pros: Explicit
- ❌ Cons: More typing, less intuitive
- **Example**: "Type SKIP to keep current value"
- **Verdict**: Unnecessarily verbose

**3. Confirmation for Each Field**
- ✅ Pros: Very safe
- ❌ Cons: Too many prompts, slow
- **Example**: "Keep current title? (y/n)"
- **Verdict**: Too tedious

**Trade-offs**:
- ✅ Fast and intuitive
- ✅ Safe default behavior
- ⚠️ Can't intentionally set field to empty (acceptable, use delete feature)

---

### Decision 4: Same Validation as Add Task

**Decision**: Apply identical validation rules (title 1-200 chars, description max 1000)

**Rationale**:
- **Consistency**: Same rules everywhere
- **Code reuse**: Use Task.__post_init__ validation
- **Predictability**: User knows what to expect
- **Data integrity**: Maintains same constraints

**Inherited from Feature 1**: See `specs/1-add-task/research.md` Decision 3

**Validation Rules**:
- Title: 1-200 characters (non-empty, trimmed)
- Description: 0-1000 characters (trimmed)

**Trade-offs**:
- ✅ Consistent behavior
- ✅ Maintains data quality
- ✅ Code reuse

---

### Decision 5: Task Not Found Handling

**Decision**: Return None and let CLI display friendly error message

**Rationale**:
- **Separation of concerns**: Manager returns None, CLI handles display
- **Flexibility**: CLI can customize error message
- **Type safety**: Optional[Task] makes it explicit
- **Pythonic**: None is standard "not found" pattern

**Implementation**:
```python
# Manager
def update_task(...) -> Optional[Task]:
    task = self.get_task_by_id(task_id)
    if task is None:
        return None  # Not found
    # ... update logic ...
    return task

# CLI
updated = manager.update_task(task_id, ...)
if updated is None:
    print(f"❌ Error: Task with ID {task_id} not found.")
```

**Alternatives Considered**:

**1. Raise Exception**
- ✅ Pros: Forces handling
- ❌ Cons: Heavier than needed, exception for expected case
- **Verdict**: Exceptions for exceptional cases, not missing IDs

**2. Return Boolean**
- ✅ Pros: Simple success/fail
- ❌ Cons: Can't return updated task for confirmation
- **Verdict**: Need task object to show updated values

**Trade-offs**:
- ✅ Clean separation
- ✅ Type-safe
- ✅ Flexible error handling

---

### Decision 6: In-Place Modification

**Decision**: Modify existing Task object directly (not create new one)

**Rationale**:
- **Simplicity**: Direct field assignment
- **Efficiency**: No object creation overhead
- **Identity**: Same object, maintains references
- **Appropriate**: Task is mutable data holder

**Implementation**:
```python
task.title = new_title  # Direct field update
task.description = new_description
```

**Alternatives Considered**:

**1. Create New Task Object**
- ✅ Pros: Immutability pattern, functional style
- ❌ Cons: More complex, need to replace in list, update references
- **Verdict**: Unnecessary for Phase I

**2. Copy-on-Write**
- ✅ Pros: Can implement undo
- ❌ Cons: Much more complex, out of scope
- **Verdict**: Phase II+ feature

**Trade-offs**:
- ✅ Simple and fast
- ✅ Works perfectly for in-memory Phase I
- ⚠️ No undo functionality (acceptable, can re-update)

---

### Decision 7: No Update Timestamp

**Decision**: Do not add "updated_at" timestamp in Phase I

**Rationale**:
- **Simplicity**: Fewer fields to manage
- **Scope**: Not required for Phase I
- **Complexity**: Would need to track on every change
- **Future**: Can add in Phase II when database tracks it

**Note**: Task retains original `created_at`, which never changes

**Trade-offs**:
- ✅ Simpler data model
- ✅ Fewer edge cases
- ⚠️ Can't track when task was last modified (acceptable for Phase I)

---

## Error Handling

### Input Validation Errors

| Error | Action | User Experience |
|-------|--------|-----------------|
| Task not found | Show error, return to menu | Clear message with ID |
| Empty title | Show error, return to menu | "Title cannot be empty" |
| Title too long | Show error, return to menu | Shows character count |
| Description too long | Show error, return to menu | Shows character count |
| Invalid ID | Show error, return to menu | "Please enter a number" |

### No Retry Loop

Unlike Add Task, Update Task does **not** retry on validation errors:
- Return to menu on error
- User can try again from menu

**Rationale**: Update is less common than Add, retry adds complexity for little benefit

---

## Performance Considerations

| Operation | Complexity |
|-----------|------------|
| Find task by ID | O(n) |
| Validate new values | O(1) |
| Update fields | O(1) |
| **Total** | **O(n)** |

**Acceptable**: Linear search is fine for Phase I (< 1000 tasks)

---

## Testing Strategy

### Test Cases

1. **Update title only**: Description unchanged
2. **Update description only**: Title unchanged
3. **Update both**: Both fields changed
4. **Empty inputs**: Keep current values
5. **Task not found**: Error displayed
6. **Invalid title**: Validation error
7. **Invalid description**: Validation error

---

## Lessons Learned

### What Worked Well

- ✅ Partial update is very user-friendly
- ✅ Showing current values helps decision making
- ✅ Empty input = keep current is intuitive

### Future Enhancements

- Add undo functionality (Phase II)
- Add "updated_at" timestamp (Phase II with database)
- Add edit history (Phase II+)

---

**Research Document Version**: 1.0  
**References**: Feature 1 (core decisions)  
**Status**: ✅ Implemented  
**Last Updated**: 2025-12-09

