# Implementation Plan: Mark Complete

**Feature**: F004  
**Status**: ✅ Implemented

## Manager Method

```python
def mark_complete(self, task_id: int, completed: bool = True) -> Optional[Task]:
    task = self.get_task_by_id(task_id)
    if task is None:
        return None
    
    task.completed = completed
    return task
```

## CLI Method

```python
def mark_complete_interactive(self) -> None:
    # Show current tasks with status
    # Get task ID
    # Toggle completion status
    # Show confirmation
```

---

**Status**: ✅ Complete

