# CLI Contract: View Task List

**Module**: `src/todo/cli.py`  
**Class**: `TodoCLI`  
**Method**: `view_tasks_interactive`  
**Feature**: F002 - View Task List

## Method Contract

```python
def view_tasks_interactive(self) -> None:
    """
    Display all tasks in a formatted list with summary statistics.
    
    Preconditions:
        - self.manager is initialized
        - Terminal supports output formatting
        
    User Interaction Flow:
        1. Display header "ALL TASKS"
        2. Get all tasks from manager
        3. Calculate and display summary:
           - Total task count
           - Pending task count
           - Completed task count
        4. Display separator line
        5. For each task:
           - Show status indicator ([○] or [✓])
           - Show ID, title, description (if any)
           - Show status text (Pending/Completed)
           - Show creation timestamp
        6. If no tasks: Display empty state message
        7. Return to caller
        
    Postconditions:
        - All tasks displayed
        - Summary statistics shown
        - No state changes (read-only operation)
        
    Side Effects:
        - Writes to stdout (display output)
        - No data modifications
        
    Error Handling:
        - No errors expected (read-only)
        - Empty list handled gracefully
    """
```

## Output Specification

### Header Format

```
==================================================
           ALL TASKS
==================================================
```

### Summary Statistics

```
Total Tasks: X
Pending: Y
Completed: Z
```

Where:
- X = Total number of tasks
- Y = Number of incomplete tasks (completed = False)
- Z = Number of completed tasks (completed = True)

### Task Display Format

```
--------------------------------------------------

[STATUS_ICON] ID: task_id
    Title: task_title
    Description: task_description    # Only if description exists
    Status: Pending|Completed
    Created: YYYY-MM-DD HH:MM:SS
```

**Status Icons**:
- `[○]` - Pending task (completed = False)
- `[✓]` - Completed task (completed = True)

### Empty State

When no tasks exist:

```
==================================================
           ALL TASKS
==================================================

No tasks found. Add some tasks to get started!
```

## Usage Examples

### Example 1: Multiple Tasks (Mixed Status)

```python
# Setup
manager.add_task("Buy groceries", "Milk, eggs, bread")
manager.add_task("Call dentist", "Schedule checkup")
manager.mark_complete(1, True)
manager.add_task("Team meeting", "Weekly standup")

# User action
cli.view_tasks_interactive()
```

**Output**:
```
==================================================
           ALL TASKS
==================================================

Total Tasks: 3
Pending: 2
Completed: 1

--------------------------------------------------

[✓] ID: 1
    Title: Buy groceries
    Description: Milk, eggs, bread
    Status: Completed
    Created: 2025-12-09 14:30:00

[○] ID: 2
    Title: Call dentist
    Description: Schedule checkup
    Status: Pending
    Created: 2025-12-09 14:31:00

[○] ID: 3
    Title: Team meeting
    Description: Weekly standup
    Status: Pending
    Created: 2025-12-09 14:32:00
```

### Example 2: Empty Task List

```python
# Setup
manager = TaskManager()  # No tasks

# User action
cli.view_tasks_interactive()
```

**Output**:
```
==================================================
           ALL TASKS
==================================================

No tasks found. Add some tasks to get started!
```

### Example 3: All Completed

```python
# Setup
manager.add_task("Task 1")
manager.add_task("Task 2")
manager.mark_complete(1, True)
manager.mark_complete(2, True)

# User action
cli.view_tasks_interactive()
```

**Output**:
```
==================================================
           ALL TASKS
==================================================

Total Tasks: 2
Pending: 0
Completed: 2

--------------------------------------------------

[✓] ID: 1
    Title: Task 1
    Status: Completed
    Created: 2025-12-09 14:30:00

[✓] ID: 2
    Title: Task 2
    Status: Completed
    Created: 2025-12-09 14:31:00
```

## Implementation Logic

### Summary Calculation

```python
tasks = self.manager.get_all_tasks()
total = len(tasks)
pending = len(self.manager.get_pending_tasks())
completed = len(self.manager.get_completed_tasks())
```

### Status Icon Selection

```python
status_icon = "✓" if task.completed else "○"
status_text = "Completed" if task.completed else "Pending"
```

### Timestamp Formatting

```python
formatted_date = task.created_at.strftime('%Y-%m-%d %H:%M:%S')
```

### Description Display

```python
if task.description:
    print(f"    Description: {task.description}")
```

## Manager Methods Used

```python
self.manager.get_all_tasks() -> List[Task]
self.manager.get_pending_tasks() -> List[Task]
self.manager.get_completed_tasks() -> List[Task]
```

## Integration with Main Menu

```python
# In TodoCLI.run() method
if choice == "2":
    self.view_tasks_interactive()
    input("\nPress Enter to continue...")
    # Returns to main menu
```

## Testing Strategy

**Unit Tests**:
- ✅ Method exists and is callable
- ✅ Manager integration verified

**Manual Tests** (Required):
- ✅ Display with no tasks (empty state)
- ✅ Display with one task
- ✅ Display with multiple tasks
- ✅ Display with mixed status (pending + completed)
- ✅ Display with all pending
- ✅ Display with all completed
- ✅ Summary counts accurate
- ✅ Status icons correct
- ✅ Timestamp formatting correct
- ✅ Description displayed when present
- ✅ Description omitted when empty

## Performance Characteristics

- **Time Complexity**: O(n) where n = number of tasks
- **Space Complexity**: O(1) (no additional storage)
- **Display Time**: < 1 second for 1000 tasks

## Related Contracts

- **Task Model**: See `specs/1-add-task/data-model.md`
- **Manager Contract**: See `specs/1-add-task/contracts/manager_contract.md`

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented and Tested

