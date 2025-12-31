# Data Model: Delete Task Feature

**Feature**: F005 - Delete Task  
**Status**: ✅ Implemented

## Data Model Reference

This feature **removes** Task entities from the TaskManager.

**See**: `specs/1-add-task/data-model.md` for complete Task entity specification.

## Deletion Operation

### What Happens

```python
# Before deletion
manager.tasks = [Task(id=1, ...), Task(id=2, ...), Task(id=3, ...)]
manager.next_id = 4

# Delete task with ID 2
manager.delete_task(2)

# After deletion
manager.tasks = [Task(id=1, ...), Task(id=3, ...)]
manager.next_id = 4  # UNCHANGED!
```

## Critical Invariant: ID Never Reused

**Most Important Rule**: Deleted task IDs are **NEVER reused**.

### Why This Matters

```python
# Scenario 1: Without this rule (BAD)
tasks = [Task(id=1), Task(id=2), Task(id=3)]
delete(2)
new_task = add_task("New")  # Gets ID 2 (CONFUSING!)
# User thinks "task 2" is old task, but it's new!

# Scenario 2: With this rule (GOOD)
tasks = [Task(id=1), Task(id=2), Task(id=3)]
delete(2)
new_task = add_task("New")  # Gets ID 4 (CLEAR!)
# No confusion, ID 2 is permanently retired
```

### Implementation

```python
class TaskManager:
    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if task is None:
            return False
        
        self.tasks.remove(task)
        # NOTE: self.next_id is NOT decremented!
        return True
```

## Data Flow

```
User requests deletion (task_id)
    ↓
Find task by ID
    ↓
Task found? ──No──> Return False
    │
   Yes
    ↓
Show task for confirmation
    ↓
User confirms? ──No──> Cancel
    │
   Yes
    ↓
Remove from manager.tasks list
    ↓
Task object deleted (garbage collected)
    ↓
ID permanently retired (never reused)
```

## Memory Impact

After deletion:
- Task object removed from list
- Python garbage collector frees memory
- No references to task remain
- **Data is permanently lost** (in-memory, Phase I)

## ID Sequence After Deletions

### Example Timeline

```
Action              | Tasks (IDs)    | next_id
--------------------|----------------|--------
Initial             | []             | 1
Add "Task A"        | [1]            | 2
Add "Task B"        | [1, 2]         | 3
Add "Task C"        | [1, 2, 3]      | 4
Delete task 2       | [1, 3]         | 4  ← Unchanged!
Add "Task D"        | [1, 3, 4]      | 5  ← Not 2!
Delete task 1       | [3, 4]         | 5  ← Unchanged!
Add "Task E"        | [3, 4, 5]      | 6  ← Not 1!
```

**Result**: IDs 1 and 2 are **permanently retired**.

## Comparison with Other Operations

| Operation | Modifies Task | Removes Task | Reuses ID |
|-----------|--------------|--------------|-----------|
| Add Task | ➕ Creates | No | No |
| View Tasks | No | No | No |
| Update Task | ✏️ Yes | No | No |
| Mark Complete | ✏️ Yes (status) | No | No |
| **Delete Task** | **🗑️ Removes** | **✅ Yes** | **❌ Never** |

## Future Considerations

**Phase II+** might add:
- Soft delete (mark as deleted, keep in database)
- Undo functionality (restore deleted tasks)
- Trash/recycle bin feature
- Permanent vs temporary deletion

**Phase I**: Hard delete (permanent removal)

---

**Data Model Version**: 1.0  
**References**: Feature 1 Task Entity  
**Status**: ✅ Implemented  
**Last Updated**: 2025-12-09

