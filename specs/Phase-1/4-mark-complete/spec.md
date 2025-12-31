# Feature Specification: Mark Task Complete

**Feature ID**: F004  
**Priority**: P2 (High)  
**Status**: ✅ Implemented  
**Depends On**: F001 (Add Task), F002 (View Tasks)

## Overview

Toggle task completion status. Mark tasks as done or revert to pending.

## User Stories

### US1: Mark Task as Complete
**As a** user  
**I want to** mark tasks as complete  
**So that** I can track my progress

**Acceptance Criteria**:
- User selects task by ID
- Status toggles: Pending ↔ Completed
- Confirmation shown
- Task appears correctly in list

## Functional Requirements

- FR1: Select task by ID
- FR2: Toggle completed field
- FR3: Show new status
- FR4: Update visible immediately

## Success Criteria

- ✅ Status toggles correctly
- ✅ Pending → Completed works
- ✅ Completed → Pending works
- ✅ Task not found handled

---

**Version**: 1.0  
**Status**: ✅ Implemented

