# Feature Specification: View Task List

**Feature ID**: F002  
**Priority**: P1 (Critical)  
**Status**: ✅ Implemented  
**Phase**: Phase I - Console App  
**Depends On**: F001 (Add Task)

## Overview

Display all tasks in a formatted list showing their status, details, and summary statistics. Users can see pending vs completed tasks at a glance.

## User Stories

### US1: View All Tasks
**Priority**: P1

**As a** user  
**I want to** see all my tasks in one view  
**So that** I can review everything I need to do

**Acceptance Criteria**:
- Display summary: Total, Pending, Completed counts
- Show each task with: ID, title, description (if any), status, created date
- Status indicators: [○] pending, [✓] completed
- Tasks displayed in creation order
- Empty list shows friendly message

### US2: Task Status Indicators
**Priority**: P1

**As a** user  
**I want to** quickly identify completed vs pending tasks  
**So that** I can focus on what needs to be done

**Acceptance Criteria**:
- Pending tasks: [○] icon
- Completed tasks: [✓] icon
- Visual separation between tasks
- Summary counts at top

## Functional Requirements

### FR1: Display Format
```
==================================================
           ALL TASKS
==================================================

Total Tasks: X
Pending: Y
Completed: Z

--------------------------------------------------

[○] ID: 1
    Title: Task title
    Description: Task description (if exists)
    Status: Pending
    Created: 2025-12-09 14:30:00

[✓] ID: 2
    Title: Completed task
    Status: Completed
    Created: 2025-12-09 14:31:00
```

### FR2: Summary Statistics
- Total task count
- Pending task count  
- Completed task count

### FR3: Empty State
When no tasks exist:
```
No tasks found. Add some tasks to get started!
```

## Success Criteria

- ✅ All tasks displayed correctly
- ✅ Status indicators accurate
- ✅ Summary counts correct
- ✅ Display time < 1 second
- ✅ Handles 0 to 1000+ tasks

## Dependencies

**Required**: F001 (Add Task) - tasks must exist to view

**Enables**: All other features (need to see tasks to update/complete/delete)

---

**Version**: 1.0  
**Status**: ✅ Implemented

