# Feature Specification: Update Task

**Feature ID**: F003  
**Priority**: P2 (High)  
**Status**: ✅ Implemented  
**Depends On**: F001 (Add Task), F002 (View Tasks)

## Overview

Modify existing task title and/or description. Users can update task details after creation.

## User Stories

### US1: Update Task Title and/or Description
**As a** user  
**I want to** modify task details  
**So that** I can correct mistakes or add more information

**Acceptance Criteria**:
- User selects task by ID
- Can update title (1-200 chars)
- Can update description (max 1000 chars)
- Can skip fields to keep current value
- Validation same as Add Task

## Functional Requirements

- FR1: Select task by ID
- FR2: Display current values
- FR3: Prompt for new values (optional)
- FR4: Validate new values
- FR5: Update only provided fields
- FR6: Show confirmation

## Success Criteria

- ✅ Task details updated correctly
- ✅ Validation enforced
- ✅ Partial updates supported (title only or description only)
- ✅ Task not found handled gracefully

---

**Version**: 1.0  
**Status**: ✅ Implemented

