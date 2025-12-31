# TaskManager Contract: Add Task Operations

**Module**: `src/todo/manager.py`  
**Class**: `TaskManager`  
**Feature**: F001 - Add Task

## Class Contract

### Constructor

```python
def __init__(self) -> None:
    """
    Initialize task manager with empty task list.
    
    Postconditions:
        - self.tasks is an empty list
        - self.next_id is 1
    """
```

### add_task Method

```python
def add_task(self, title: str, description: str = "") -> Task:
    """
    Create and add a new task to the list.
    
    Args:
        title: Task title (1-200 characters after trimming)
        description: Optional task description (max 1000 characters)
        
    Returns:
        The newly created Task object
        
    Raises:
        ValueError: If title is empty or too long (> 200 chars)
        ValueError: If description is too long (> 1000 chars)
        
    Preconditions:
        - title is a string (can have whitespace)
        - description is a string (can be empty)
        
    Postconditions:
        - New Task object created with:
          - id = current next_id value
          - title = trimmed input title
          - description = trimmed input description  
          - completed = False
          - created_at = current timestamp
        - Task added to self.tasks list
        - self.next_id incremented by 1
        - ID never reused (even if tasks deleted)
        
    Side Effects:
        - Modifies self.tasks (appends new task)
        - Modifies self.next_id (increments)
        
    Invariants:
        - All task IDs in self.tasks are unique
        - Task IDs are sequential (no gaps in new tasks)
        - self.next_id always > maximum task ID in list
    """
```

## Usage Examples

### Successful Task Creation

```python
manager = TaskManager()

# Example 1: Title only
task1 = manager.add_task("Buy groceries")
assert task1.id == 1
assert task1.title == "Buy groceries"
assert task1.description == ""
assert task1.completed == False
assert len(manager.tasks) == 1

# Example 2: Title and description
task2 = manager.add_task("Meeting", "Discuss project updates")
assert task2.id == 2
assert task2.title == "Meeting"
assert task2.description == "Discuss project updates"
assert len(manager.tasks) == 2

# Example 3: Whitespace trimming
task3 = manager.add_task("  Buy milk  ", "  From store  ")
assert task3.id == 3
assert task3.title == "Buy milk"  # Trimmed
assert task3.description == "From store"  # Trimmed
```

### Error Cases

```python
manager = TaskManager()

# Error 1: Empty title
try:
    manager.add_task("")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert str(e) == "Title cannot be empty"

# Error 2: Whitespace-only title
try:
    manager.add_task("   ")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert str(e) == "Title cannot be empty"

# Error 3: Title too long
try:
    long_title = "x" * 201
    manager.add_task(long_title)
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Title too long" in str(e)

# Error 4: Description too long
try:
    long_desc = "x" * 1001
    manager.add_task("Valid title", long_desc)
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Description too long" in str(e)

# Important: Failed operations do NOT increment next_id
# ID remains 1 after all these failures
assert manager.next_id == 1
assert len(manager.tasks) == 0
```

### ID Generation Behavior

```python
manager = TaskManager()

# IDs increment sequentially
task1 = manager.add_task("Task 1")
task2 = manager.add_task("Task 2")
task3 = manager.add_task("Task 3")

assert task1.id == 1
assert task2.id == 2
assert task3.id == 3
assert manager.next_id == 4

# IDs are never reused, even after deletion
manager.delete_task(2)  # Delete task 2
task4 = manager.add_task("Task 4")
assert task4.id == 4  # Not 2!
assert manager.next_id == 5
```

## Contract Validation Tests

Located in: `tests/test_manager.py`

- ✅ `test_add_task_with_title_only`
- ✅ `test_add_task_with_description`
- ✅ `test_multiple_tasks_increment_id`
- ✅ `test_add_task_with_empty_title_raises_error`
- ✅ `test_add_task_with_long_title_raises_error`
- ✅ `test_delete_task_ids_not_reused`

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented and Tested

