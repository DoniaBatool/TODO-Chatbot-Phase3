# CLI Contract: Mark Task Complete

**Module**: `src/todo/cli.py`  
**Class**: `TodoCLI`  
**Method**: `mark_complete_interactive`  
**Feature**: F004 - Mark Complete

## Method Contract

```python
def mark_complete_interactive(self) -> None:
    """
    Interactive CLI for toggling task completion status.
    
    User Interaction Flow:
        1. Display current tasks with status
        2. Prompt for task ID
        3. Validate task ID (task exists)
        4. Toggle completion status
        5. Display confirmation with new status
        
    Postconditions:
        - Task.completed toggled
        - Pending → Completed (False → True)
        - Completed → Pending (True → False)
        
    Error Handling:
        - Invalid ID: Show error, return
        - Task not found: Show error, return
    """
```

## Toggle Behavior

```python
# Current state: completed = False (Pending)
# After toggle: completed = True (Completed)

# Current state: completed = True (Completed)
# After toggle: completed = False (Pending)
```

## Usage Examples

### Example 1: Mark as Complete

```python
# Task 1: completed = False

Input: Task ID: 1
Output:
  ✓ Task marked as completed!
  Title: Buy groceries

# Now: Task 1: completed = True
```

### Example 2: Mark as Incomplete

```python
# Task 1: completed = True

Input: Task ID: 1
Output:
  ✓ Task marked as pending!
  Title: Buy groceries

# Now: Task 1: completed = False
```

## Manager Method Used

```python
manager.mark_complete(task_id, completed=not task.completed) -> Optional[Task]
```

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented

