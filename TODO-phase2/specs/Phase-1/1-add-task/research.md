# Research & Technical Decisions: Add Task Feature

**Feature**: F001 - Add Task  
**Date**: 2025-12-09  
**Status**: ✅ Decisions Implemented

## Overview

This document captures the technical research and design decisions made during the implementation of the Add Task feature. Each decision includes the rationale, alternatives considered, and trade-offs.

---

## Decision 1: Task Data Structure

### Decision
Use Python `dataclass` for the Task model

### Rationale
- **Automatic methods**: `__init__`, `__repr__`, `__eq__` generated automatically
- **Type hints**: First-class support with runtime type checking available
- **Validation hook**: `__post_init__` method perfect for validation logic
- **Clean syntax**: Reduces boilerplate significantly vs regular class
- **Immutability support**: Can use `frozen=True` if needed later
- **Standard library**: No external dependencies

### Alternatives Considered

**1. Named Tuple**
- ✅ Pros: Immutable, lightweight
- ❌ Cons: No validation, harder to add methods, tuple indexing confusing
- **Verdict**: Too limited for our needs

**2. Regular Python Class**
- ✅ Pros: Maximum flexibility
- ❌ Cons: Lots of boilerplate (`__init__`, `__repr__`, etc.)
- **Verdict**: Too much code for simple data holder

**3. Dictionary**
- ✅ Pros: Simple, flexible
- ❌ Cons: No type safety, no validation, error-prone
- **Verdict**: Too error-prone for production code

**4. Pydantic Model**
- ✅ Pros: Advanced validation, serialization
- ❌ Cons: External dependency, overkill for Phase I
- **Verdict**: Save for Phase II (web API)

### Implementation
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        # Validation logic here
        pass
```

### Trade-offs
- ✅ Clean, readable code
- ✅ Type-safe with hints
- ✅ Easy to test
- ⚠️ Slightly slower than named tuple (negligible for our use case)

---

## Decision 2: ID Generation Strategy

### Decision
Sequential auto-increment starting from 1

### Rationale
- **Simple**: Easy to understand and implement
- **Predictable**: IDs are 1, 2, 3, ... in order
- **User-friendly**: Short, readable IDs for CLI display
- **No collisions**: Single-threaded access guarantees uniqueness
- **Debugging**: Easy to track task creation order

### Alternatives Considered

**1. UUID (Universally Unique Identifier)**
- ✅ Pros: Globally unique, no coordination needed
- ❌ Cons: Long (36 chars), not user-friendly for CLI, overkill
- **Example**: `550e8400-e29b-41d4-a716-446655440000`
- **Verdict**: Too complex for Phase I

**2. Random Numbers**
- ✅ Pros: No sequential dependency
- ❌ Cons: Collision risk, harder to debug, unpredictable
- **Verdict**: Unnecessary risk for no benefit

**3. Timestamp-based (Unix epoch)**
- ✅ Pros: Sortable by creation time
- ❌ Cons: Not guaranteed unique if multiple tasks created in same millisecond
- **Example**: `1702134000`
- **Verdict**: Potential collision issues

**4. Hash-based (from title)**
- ✅ Pros: Deterministic from content
- ❌ Cons: Collision risk, changes if title edited
- **Verdict**: Fragile and unreliable

### Implementation
```python
class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
        self.next_id: int = 1
    
    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(id=self.next_id, title=title, description=description)
        self.tasks.append(task)
        self.next_id += 1  # Never reused
        return task
```

### Trade-offs
- ✅ Simple and reliable
- ✅ Perfect for single-user, single-threaded CLI
- ⚠️ Wouldn't scale to distributed system (but not needed for Phase I)
- ⚠️ IDs reveal task creation order (acceptable for our use case)

---

## Decision 3: Validation Approach

### Decision
Validation in Task `__post_init__` method with ValueError exceptions

### Rationale
- **Fail fast**: Invalid tasks never exist
- **Centralized**: All validation in one place
- **Automatic**: Runs on every task creation
- **Clear errors**: ValueError with descriptive messages
- **Pythonic**: Standard pattern for dataclass validation

### Alternatives Considered

**1. Validation in TaskManager**
- ✅ Pros: Keeps Task simple
- ❌ Cons: Task objects can be invalid, validation spread across codebase
- **Verdict**: Violates data integrity principles

**2. Property Setters**
- ✅ Pros: Validates on field changes
- ❌ Cons: More complex, tasks are immutable after creation in our design
- **Verdict**: Unnecessary complexity

**3. External Validator Function**
- ✅ Pros: Reusable, testable in isolation
- ❌ Cons: Extra function call, can be bypassed
- **Verdict**: Doesn't guarantee validation happens

**4. Pydantic Validators**
- ✅ Pros: Sophisticated validation, good error messages
- ❌ Cons: External dependency, overkill for Phase I
- **Verdict**: Save for Phase II

### Implementation
```python
def __post_init__(self) -> None:
    # Validate title
    if not self.title or len(self.title.strip()) == 0:
        raise ValueError("Title cannot be empty")
    if len(self.title) > 200:
        raise ValueError("Title too long (max 200 characters)")
    
    # Validate description
    if len(self.description) > 1000:
        raise ValueError("Description too long (max 1000 characters)")
    
    # Sanitize
    self.title = self.title.strip()
    self.description = self.description.strip()
```

### Trade-offs
- ✅ Guarantees valid tasks
- ✅ Clear error messages
- ✅ Easy to test
- ⚠️ Mutable fields after validation (could use frozen=True if needed)

---

## Decision 4: Error Handling Strategy

### Decision
Try-except in CLI layer, ValueError from model/manager layers

### Rationale
- **Separation of concerns**: Model validates, CLI displays errors
- **User-friendly**: CLI translates exceptions to readable messages
- **Clean propagation**: Manager doesn't catch, just propagates
- **Testable**: Can test validation without CLI

### Alternatives Considered

**1. Return None on Error**
- ✅ Pros: No exceptions
- ❌ Cons: Unclear why it failed, easy to forget to check
- **Verdict**: Too error-prone

**2. Custom Exception Types**
- ✅ Pros: Fine-grained error handling
- ❌ Cons: Overkill for Phase I, more code to maintain
- **Example**: `TitleTooLongError`, `EmptyTitleError`
- **Verdict**: Unnecessary for simple validation

**3. Status/Result Objects**
- ✅ Pros: Explicit success/failure
- ❌ Cons: Verbose, un-Pythonic for validation
- **Example**: `Result[Task, ValidationError]`
- **Verdict**: Over-engineering

### Implementation

**Model Layer** (task.py):
```python
raise ValueError("Title cannot be empty")  # Validate and raise
```

**Manager Layer** (manager.py):
```python
task = Task(id=self.next_id, title=title, ...)  # Propagates ValueError
```

**CLI Layer** (cli.py):
```python
try:
    task = self.manager.add_task(title, description)
    print("✓ Task added successfully!")
except ValueError as e:
    print(f"❌ Error: {e}")  # User-friendly display
```

### Trade-offs
- ✅ Clear error flow
- ✅ User-friendly messages
- ✅ Easy to debug
- ⚠️ Exceptions have performance cost (but negligible for CLI)

---

## Decision 5: Input Sanitization

### Decision
Automatic whitespace trimming in Task `__post_init__`

### Rationale
- **User-friendly**: Users don't have to worry about extra spaces
- **Data quality**: Consistent storage format
- **Validation simplicity**: Check length after trimming
- **Transparent**: Happens automatically, no manual calls

### Alternatives Considered

**1. Trim in CLI Before Passing**
- ✅ Pros: CLI controls sanitization
- ❌ Cons: Task can still be created with whitespace from other code
- **Verdict**: Doesn't protect the model

**2. Don't Trim Automatically**
- ✅ Pros: Preserves exact user input
- ❌ Cons: "  Task  " vs "Task" treated differently, confusing
- **Verdict**: Bad UX

**3. Validation Without Trimming**
- ✅ Pros: Simple validation logic
- ❌ Cons: "   " would pass as non-empty, bad data quality
- **Verdict**: Data integrity issue

### Implementation
```python
def __post_init__(self) -> None:
    # ... validation ...
    self.title = self.title.strip()
    self.description = self.description.strip()
```

### Trade-offs
- ✅ Better data quality
- ✅ User-friendly
- ⚠️ Modifies input (documented in contract)

---

## Decision 6: CLI Validation Loops

### Decision
Retry loop for invalid input, don't exit or crash

### Rationale
- **Resilient**: User can fix mistakes without restarting
- **User-friendly**: Clear error + immediate retry
- **No data loss**: User doesn't have to re-enter previous valid input
- **Standard pattern**: Common in interactive CLI apps

### Alternatives Considered

**1. Exit on Error**
- ✅ Pros: Simple implementation
- ❌ Cons: Terrible UX, forces restart
- **Verdict**: Unacceptable UX

**2. Single Retry Then Exit**
- ✅ Pros: Prevents infinite loops if automation goes wrong
- ❌ Cons: Arbitrary limit, still bad UX
- **Verdict**: Doesn't solve the problem

**3. Store Invalid Input and Pre-fill**
- ✅ Pros: User can edit instead of re-type
- ❌ Cons: Complex implementation for CLI
- **Verdict**: Nice to have, but complex for Phase I

### Implementation
```python
# Title validation loop
while True:
    title = input("Enter task title: ").strip()
    if not title:
        print("❌ Error: Title cannot be empty")
        continue  # Retry
    if len(title) > 200:
        print(f"❌ Error: Title too long ({len(title)}/200 characters)")
        continue  # Retry
    break  # Valid, exit loop
```

### Trade-offs
- ✅ Excellent UX
- ✅ Resilient
- ⚠️ Possible infinite loop if automation fails (acceptable for interactive CLI)

---

## Decision 7: Timestamp Format

### Decision
Python `datetime.now()` with ISO 8601 serialization

### Rationale
- **Standard**: ISO 8601 is universal
- **Sortable**: Lexicographic sort matches chronological
- **Readable**: Human-readable when formatted
- **No external deps**: Built into Python
- **Future-proof**: Compatible with databases (Phase II)

### Alternatives Considered

**1. Unix Timestamp (Epoch Seconds)**
- ✅ Pros: Compact, fast comparisons
- ❌ Cons: Not human-readable, timezone ambiguous
- **Example**: `1702134000`
- **Verdict**: Bad for CLI display

**2. String Timestamp**
- ✅ Pros: Simple
- ❌ Cons: No timezone info, hard to compare/sort
- **Example**: "2025-12-09 14:30:00"
- **Verdict**: Loses timezone info

**3. UTC Timestamp**
- ✅ Pros: Unambiguous timezone
- ❌ Cons: Confusing for single-user local app
- **Verdict**: Overkill for Phase I

### Implementation
```python
from datetime import datetime

@dataclass
class Task:
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            ...
            "created_at": self.created_at.isoformat()
        }
```

### Trade-offs
- ✅ Standard format
- ✅ Easy to work with
- ⚠️ Local time only (acceptable for single-user CLI)

---

## Performance Considerations

### In-Memory List Performance
- **Add Task**: O(1) - append to list
- **Get All Tasks**: O(n) - iterate list
- **Get by ID**: O(n) - linear search

**Analysis**:
- For Phase I (< 1000 tasks expected), O(n) is acceptable
- Future optimization (Phase II+): Use dict for O(1) lookups

### Memory Usage
- **Task Object**: ~200 bytes each
- **1000 tasks**: ~200 KB
- **10000 tasks**: ~2 MB

**Analysis**: Negligible memory usage for console app

---

## Security Considerations

### Input Validation
- ✅ Length limits prevent memory attacks
- ✅ Type hints prevent type confusion
- ✅ Sanitization prevents data corruption

### No Security Concerns for Phase I
- Single-user local application
- No network access
- No file system access
- No authentication needed

**Future (Phase II+)**:
- Add authentication
- Validate against SQL injection
- Add CSRF protection

---

## Testing Strategy Decisions

### Test Framework: pytest
**Why**:
- Industry standard for Python
- Excellent fixtures and assertions
- Plugin ecosystem (pytest-cov)
- Simple, Pythonic syntax

### Coverage Target: 80%+
**Why**:
- 100% coverage unrealistic for CLI (interactive)
- 80% covers critical business logic
- Focus on model and manager layers

### Test Organization
- `test_task.py`: Model validation
- `test_manager.py`: CRUD operations  
- `test_cli.py`: Structure tests (manual for interactive)

---

## Lessons Learned

### What Worked Well
- ✅ Dataclass with `__post_init__` validation
- ✅ Sequential ID generation
- ✅ Retry loops in CLI
- ✅ Clear separation of concerns

### What Could Be Improved
- ⚠️ CLI testing requires manual effort (could add input mocking)
- ⚠️ No undo functionality (could add command history)

### Decisions to Revisit in Phase II
- Consider Pydantic for API validation
- Add database for persistence
- Implement proper ID strategy for distributed system

---

**Research Document Version**: 1.0  
**Completed**: 2025-12-09  
**Status**: ✅ All Decisions Implemented

