# Implementation Plan: Update Task

**Feature**: F003  
**Status**: ✅ Implemented

## Manager Method

```python
def update_task(self, task_id: int, title: Optional[str] = None, 
                description: Optional[str] = None) -> Optional[Task]:
    task = self.get_task_by_id(task_id)
    if task is None:
        return None
    
    if title is not None:
        # Validate and update title
        task.title = title.strip()
    
    if description is not None:
        # Validate and update description
        task.description = description.strip()
    
    return task
```

## CLI Method

```python
def update_task_interactive(self) -> None:
    # Show current tasks
    # Get task ID from user
    # Show current values
    # Get new values (optional)
    # Update task via manager
    # Show confirmation
```

---

**Status**: ✅ Complete

