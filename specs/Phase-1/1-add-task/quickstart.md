# Quick Start Guide: Add Task Feature

**Feature**: F001 - Add Task  
**Target Audience**: Developers, QA Engineers, End Users  
**Estimated Time**: 5 minutes

## Prerequisites

- ✅ Python 3.13+ installed
- ✅ UV package manager installed
- ✅ Virtual environment activated
- ✅ All dependencies installed (`uv pip install -e ".[dev]"`)

## Quick Usage

### Option 1: Run the Application

```bash
# Navigate to project root
cd /home/donia_batool/todo

# Activate virtual environment (if not already)
source .venv/bin/activate

# Run the application
python -m todo.main
```

### Option 2: Use Installed Command

```bash
# After installation
todo
```

## Step-by-Step Usage

### 1. Start the Application

```bash
$ python -m todo.main

🎯 Welcome to Todo List Manager!

==================================================
           TODO LIST MANAGER
==================================================
1. Add Task
2. View All Tasks
3. Update Task
4. Mark Task Complete/Incomplete
5. Delete Task
6. Exit
==================================================

Enter your choice (1-6): 
```

### 2. Select "Add Task" (Option 1)

```
Enter your choice (1-6): 1
```

### 3. Enter Task Title

```
==================================================
           ADD NEW TASK
==================================================

Enter task title: Buy groceries
```

### 4. Enter Description (Optional)

```
Enter description (optional, press Enter to skip): Milk, eggs, bread, and coffee
```

### 5. See Confirmation

```
✓ Task added successfully!
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread, and coffee
Status: Pending

Press Enter to continue...
```

### 6. Return to Menu

Press Enter to return to the main menu. Your task is now saved in memory!

## Common Scenarios

### Scenario 1: Quick Task (Title Only)

```bash
Enter your choice (1-6): 1
Enter task title: Call dentist
Enter description (optional, press Enter to skip): [Press Enter]

✓ Task added successfully!
ID: 1
Title: Call dentist
Status: Pending
```

**Use Case**: Capturing quick todos without details

---

### Scenario 2: Detailed Task

```bash
Enter your choice (1-6): 1
Enter task title: Team meeting
Enter description (optional, press Enter to skip): Weekly standup - discuss sprint progress and blockers

✓ Task added successfully!
ID: 2
Title: Team meeting
Description: Weekly standup - discuss sprint progress and blockers
Status: Pending
```

**Use Case**: Tasks requiring context and details

---

### Scenario 3: Error Handling - Empty Title

```bash
Enter task title: [Press Enter without typing]
❌ Error: Title cannot be empty

Enter task title: Valid task title
Enter description (optional, press Enter to skip): [Press Enter]

✓ Task added successfully!
ID: 1
Title: Valid task title
Status: Pending
```

**Result**: System prompts again, no crash

---

### Scenario 4: Error Handling - Title Too Long

```bash
Enter task title: [Type 201+ characters]
❌ Error: Title too long (205/200 characters)

Enter task title: Shorter title
Enter description (optional, press Enter to skip): [Press Enter]

✓ Task added successfully!
ID: 1
Title: Shorter title
Status: Pending
```

**Result**: Clear error with character count, prompt again

---

### Scenario 5: Multiple Tasks in Sequence

```bash
# First task
Enter your choice (1-6): 1
Enter task title: Task 1
Enter description (optional, press Enter to skip): Description 1
✓ Task added successfully!
ID: 1
Press Enter to continue...

# Second task
Enter your choice (1-6): 1
Enter task title: Task 2
Enter description (optional, press Enter to skip): Description 2
✓ Task added successfully!
ID: 2
Press Enter to continue...

# Third task
Enter your choice (1-6): 1
Enter task title: Task 3
Enter description (optional, press Enter to skip): Description 3
✓ Task added successfully!
ID: 3
Press Enter to continue...
```

**Result**: IDs increment automatically (1, 2, 3...)

---

### Scenario 6: Whitespace Trimming

```bash
Enter task title:    Task with spaces    
Enter description (optional, press Enter to skip):    Description with spaces    

✓ Task added successfully!
ID: 1
Title: Task with spaces          # Spaces trimmed automatically
Description: Description with spaces  # Spaces trimmed automatically
Status: Pending
```

**Result**: Leading/trailing spaces removed automatically

## Testing the Feature

### Manual Test Checklist

- [ ] **Test 1**: Add task with title only
- [ ] **Test 2**: Add task with title and description
- [ ] **Test 3**: Try to add task with empty title (should show error)
- [ ] **Test 4**: Try to add task with 201+ char title (should show error)
- [ ] **Test 5**: Try to add task with 1001+ char description (should show error)
- [ ] **Test 6**: Add task with leading/trailing spaces (should trim)
- [ ] **Test 7**: Add 3 tasks in sequence (IDs should be 1, 2, 3)
- [ ] **Test 8**: Verify confirmation message displays task details
- [ ] **Test 9**: Press Enter to return to menu
- [ ] **Test 10**: Verify task appears in "View All Tasks" (Feature F002)

### Run Automated Tests

```bash
# All tests
pytest

# Specific tests for Add Task
pytest tests/test_task.py -v
pytest tests/test_manager.py::TestTaskManagerAddTask -v

# With coverage
pytest --cov=todo --cov-report=term-missing
```

**Expected**: All tests pass ✅

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'todo'"

**Solution**: Install the package in editable mode
```bash
cd /home/donia_batool/todo
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Issue: "Command 'todo' not found"

**Solution**: Make sure virtual environment is activated
```bash
source .venv/bin/activate
```

Or run directly:
```bash
python -m todo.main
```

### Issue: Tests fail with import errors

**Solution**: Install test dependencies
```bash
uv pip install -e ".[dev]"
```

### Issue: Application crashes on startup

**Solution**: Check Python version
```bash
python --version  # Should be 3.13+
```

## Integration with Other Features

### Add Task + View Tasks (F002)

```bash
# Add some tasks
1. Add Task → "Buy groceries"
1. Add Task → "Call dentist"
1. Add Task → "Team meeting"

# View all tasks
2. View All Tasks

# Output:
==================================================
           ALL TASKS
==================================================

Total Tasks: 3
Pending: 3
Completed: 0

--------------------------------------------------

[○] ID: 1
    Title: Buy groceries
    Status: Pending
    Created: 2025-12-09 14:30:00

[○] ID: 2
    Title: Call dentist
    Status: Pending
    Created: 2025-12-09 14:31:15

[○] ID: 3
    Title: Team meeting
    Status: Pending
    Created: 2025-12-09 14:32:45
```

### Data Lifecycle

```
Add Task (F001)
    ↓
Task Created in Memory
    ↓
├→ View Tasks (F002)     ← See the task
├→ Update Task (F003)    ← Modify title/description
├→ Mark Complete (F004)  ← Toggle completion
└→ Delete Task (F005)    ← Remove from list
```

## Performance Notes

- **Task Creation Time**: < 1 second (instant)
- **Memory Per Task**: ~200 bytes
- **Recommended Max Tasks**: 10,000 (Phase I in-memory limit)
- **Task IDs**: Sequential from 1 to N

## Quick Reference

### Valid Inputs

| Field | Min | Max | Required | Example |
|-------|-----|-----|----------|---------|
| Title | 1 char | 200 chars | Yes | "Buy groceries" |
| Description | 0 chars | 1000 chars | No | "Milk, eggs, bread" |

### Task States

- **Pending**: `completed = False` (default)
- **Completed**: `completed = True` (after F004)

### Error Messages

| Error | Message | Action |
|-------|---------|--------|
| Empty title | "❌ Error: Title cannot be empty" | Retry with non-empty title |
| Title too long | "❌ Error: Title too long (X/200 characters)" | Retry with shorter title |
| Description too long | "❌ Error: Description too long (X/1000 characters)" | Retry with shorter description |

## Next Steps

After successfully adding tasks:

1. **View Tasks** (F002) - See all your tasks
2. **Update Task** (F003) - Modify task details
3. **Mark Complete** (F004) - Mark tasks as done
4. **Delete Task** (F005) - Remove unwanted tasks

## Additional Resources

- **Full Specification**: `specs/1-add-task/spec.md`
- **Implementation Plan**: `specs/1-add-task/plan.md`
- **Task Breakdown**: `specs/1-add-task/tasks.md`
- **Data Model**: `specs/1-add-task/data-model.md`
- **API Contracts**: `specs/1-add-task/contracts/`
- **Test Coverage Report**: `htmlcov/index.html` (after running tests with `--cov-report=html`)

---

**Quick Start Version**: 1.0  
**Last Updated**: 2025-12-09  
**Status**: ✅ Feature Complete

