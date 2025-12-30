# CLI Contract: Add Task Interface

**Module**: `src/todo/cli.py`  
**Class**: `TodoCLI`  
**Method**: `add_task_interactive`  
**Feature**: F001 - Add Task

## Method Contract

```python
def add_task_interactive(self) -> None:
    """
    Interactive CLI for adding a new task.
    Handles user input, validation, and error display.
    
    Preconditions:
        - self.manager is initialized
        - Terminal supports input() function
        - User can type and press Enter
        
    User Interaction Flow:
        1. Display header "=== ADD NEW TASK ==="
        2. Prompt "Enter task title: "
        3. Read user input
        4. Validate title:
           - If empty/whitespace: Display error, go to step 2
           - If > 200 chars: Display error with count, go to step 2
           - If valid: Continue to step 5
        5. Prompt "Enter description (optional, press Enter to skip): "
        6. Read user input
        7. Validate description:
           - If > 1000 chars: Display error with count, go to step 5
           - If valid: Continue to step 8
        8. Call self.manager.add_task(title, description)
        9. Display success confirmation with task details
        
    Postconditions:
        - New task created in manager (if inputs valid)
        - User sees confirmation message
        - Method returns (control back to caller)
        
    Side Effects:
        - Writes to stdout (prompts, messages)
        - Reads from stdin (user input)
        - Modifies self.manager.tasks (via add_task)
        
    Error Handling:
        - ValueError from manager.add_task: Caught and displayed as error message
        - Invalid input: Re-prompt without crash
        - No exceptions propagate to caller
    """
```

## User Interface Specification

### Output Messages

**Header**:
```
==================================================
           ADD NEW TASK
==================================================
```

**Prompts**:
```
Enter task title: [cursor here]
Enter description (optional, press Enter to skip): [cursor here]
```

**Success Confirmation**:
```
✓ Task added successfully!
ID: [task_id]
Title: [task_title]
Description: [task_description]  # Only if description provided
Status: Pending
```

**Error Messages**:
```
❌ Error: Title cannot be empty
❌ Error: Title too long ([count]/200 characters)
❌ Error: Description too long ([count]/1000 characters)
❌ Error: [unexpected error message]
```

### User Input Examples

**Example 1: Title only**
```
Enter task title: Buy groceries
Enter description (optional, press Enter to skip): [Enter]

✓ Task added successfully!
ID: 1
Title: Buy groceries
Status: Pending
```

**Example 2: Title and description**
```
Enter task title: Meeting
Enter description (optional, press Enter to skip): Discuss project updates

✓ Task added successfully!
ID: 1
Title: Meeting
Description: Discuss project updates
Status: Pending
```

**Example 3: Empty title error**
```
Enter task title: [Enter]
❌ Error: Title cannot be empty

Enter task title: Buy milk
Enter description (optional, press Enter to skip): [Enter]

✓ Task added successfully!
ID: 1
Title: Buy milk
Status: Pending
```

**Example 4: Title too long**
```
Enter task title: [201 characters]
❌ Error: Title too long (201/200 characters)

Enter task title: Shorter title
Enter description (optional, press Enter to skip): [Enter]

✓ Task added successfully!
ID: 1
Title: Shorter title
Status: Pending
```

**Example 5: Description too long**
```
Enter task title: Valid title
Enter description (optional, press Enter to skip): [1001 characters]
❌ Error: Description too long (1001/1000 characters)

Enter description (optional, press Enter to skip): Shorter description

✓ Task added successfully!
ID: 1
Title: Valid title
Description: Shorter description
Status: Pending
```

## Behavioral Contracts

### Loop Behavior

**Title Validation Loop**:
```python
# Pseudocode
while True:
    title = input("Enter task title: ").strip()
    if not title:
        print("❌ Error: Title cannot be empty")
        continue  # Retry
    if len(title) > 200:
        print(f"❌ Error: Title too long ({len(title)}/200 characters)")
        continue  # Retry
    break  # Valid title, exit loop
```

**Description Validation Loop**:
```python
# Pseudocode
while True:
    description = input("Enter description (optional, press Enter to skip): ").strip()
    if len(description) > 1000:
        print(f"❌ Error: Description too long ({len(description)}/1000 characters)")
        continue  # Retry
    break  # Valid description (or empty), exit loop
```

### Exception Handling

```python
try:
    task = self.manager.add_task(title, description)
    # Display success message
except ValueError as e:
    print(f"❌ Error: {e}")
    # No task created, method returns
```

## Integration with Main Menu

```python
# In TodoCLI.run() method
while True:
    self.display_menu()
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        self.add_task_interactive()  # Call add task
        input("\nPress Enter to continue...")  # Pause
        # Loop continues, menu redisplays
```

## Testing Strategy

**Unit Tests** (tests/test_cli.py):
- ✅ Method exists and is callable
- ✅ Manager integration (task manager accessible)

**Manual Tests** (Required):
- ✅ Title-only task creation
- ✅ Title + description creation
- ✅ Empty title error and retry
- ✅ Long title error and retry
- ✅ Long description error and retry
- ✅ Whitespace trimming
- ✅ Return to menu after completion
- ✅ Multiple tasks in sequence

---

**Contract Version**: 1.0  
**Status**: ✅ Implemented and Tested

