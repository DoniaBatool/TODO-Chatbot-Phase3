# CLI Contract: Update Task

**Module**: `src/todo/cli.py`  
**Class**: `TodoCLI`  
**Method**: `update_task_interactive`  
**Feature**: F003 - Update Task

## Method Contract

```python
def update_task_interactive(self) -> None:
    """
    Interactive CLI for updating an existing task.
    
    User Interaction Flow:
        1. Display current tasks list
        2. Prompt for task ID
        3. Validate task ID (task exists)
        4. Display current task values
        5. Prompt for new title (optional)
        6. Prompt for new description (optional)
        7. Validate new values if provided
        8. Update task via manager
        9. Display confirmation
        
    Postconditions:
        - Task updated if valid inputs
        - Only provided fields updated
        - Empty input = keep current value
        
    Error Handling:
        - Invalid ID: Show error, return
        - Task not found: Show error, return
        - Invalid values: Show error, return
        - ValueError: Catch and display
    """
```

## Usage Examples

```python
# Current task: ID 1, Title "Buy groceries", Description ""
# User updates both fields

Input:
  Task ID: 1
  New title: Buy groceries and fruits
  New description: Also get apples

Output:
  ✓ Task updated successfully!
  Title: Buy groceries and fruits
  Description: Also get apples
```

## Manager Method Used

```python
manager.update_task(task_id, title=new_title, description=new_desc) -> Optional[Task]
```

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented

