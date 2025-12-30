# Quick Start: Delete Task

## Usage

```bash
# Select option 5
Enter your choice (1-6): 5

# View tasks
Current tasks:
  [○] 1. Buy groceries
  [○] 2. Call dentist
  [○] 3. Team meeting

# Enter task ID
Enter task ID to delete: 2

# Confirmation
Task to delete: Call dentist
Are you sure? (yes/no): yes

# Result
✓ Task deleted successfully!

# If cancelled:
Are you sure? (yes/no): no
✗ Deletion cancelled.
```

## Important Note

**IDs are NEVER reused!**

```bash
# Before: tasks 1, 2, 3
# Delete task 2
# After: tasks 1, 3
# Add new task → gets ID 4 (NOT 2!)
```

---

**Feature**: ✅ Working

