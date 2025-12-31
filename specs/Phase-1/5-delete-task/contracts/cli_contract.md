# CLI Contract: Delete Task

**Module**: `src/todo/cli.py`  
**Class**: `TodoCLI`  
**Method**: `delete_task_interactive`  
**Feature**: F005 - Delete Task

## Method Contract

```python
def delete_task_interactive(self) -> None:
    """
    Interactive CLI for deleting a task with confirmation.
    
    User Interaction Flow:
        1. Display current tasks
        2. Prompt for task ID
        3. Validate task ID (task exists)
        4. Show task to be deleted
        5. Prompt for confirmation (yes/no)
        6. If confirmed: Delete task
        7. If not confirmed: Cancel
        8. Display result message
        
    Postconditions:
        - Task removed from list (if confirmed)
        - Task unchanged (if not confirmed)
        - ID never reused (important!)
        
    Error Handling:
        - Invalid ID: Show error, return
        - Task not found: Show error, return
        - Confirmation required: yes/y or no/n
    """
```

## Confirmation Requirement

**Critical Safety Feature**: Deletion is **irreversible**, so confirmation is mandatory.

```python
# Valid confirmations (case-insensitive)
Confirm: "yes", "y", "YES", "Y"
Cancel: "no", "n", "NO", "N", or any other input
```

## Usage Examples

### Example 1: Confirmed Deletion

```python
Input:
  Task ID: 1
  Task to delete: Buy groceries
  Are you sure? (yes/no): yes

Output:
  ✓ Task deleted successfully!

# Task removed from manager.tasks
```

### Example 2: Cancelled Deletion

```python
Input:
  Task ID: 1
  Task to delete: Buy groceries
  Are you sure? (yes/no): no

Output:
  ✗ Deletion cancelled.

# Task still exists in manager.tasks
```

### Example 3: Task Not Found

```python
Input:
  Task ID: 999

Output:
  ❌ Error: Task with ID 999 not found.
```

## Important: ID Never Reused

**Critical Invariant**: After deletion, the task ID is **NEVER reused**.

```python
# Before deletion: tasks with IDs 1, 2, 3
# manager.next_id = 4

manager.delete_task(2)  # Delete task 2

# After deletion: tasks with IDs 1, 3
# manager.next_id = 4  (NOT decreased!)

new_task = manager.add_task("New task")
# new_task.id = 4  (NOT 2!)
```

**Why?** Prevents confusion and maintains ID history integrity.

## Manager Method Used

```python
manager.delete_task(task_id) -> bool
# Returns True if deleted, False if not found
```

## Deletion Behavior

```python
# Task removal from list
self.tasks.remove(task)

# ID generator NOT affected
# self.next_id remains unchanged (never decremented)
```

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented

