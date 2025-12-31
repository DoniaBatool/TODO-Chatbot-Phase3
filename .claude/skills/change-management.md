---
description: Manage changes to existing features by creating change subfolders with spec, plan, tasks and automatically updating all affected areas of the project (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill manages changes to existing features, ensuring all project areas are updated consistently and tested.

### 1. Parse Change Request

Extract from user input:
- Target feature (existing feature to change)
- Change description (what needs to be modified)
- Change type (enhancement, bugfix, refactor, breaking)
- Affected areas (estimate based on feature)

**Example input:**
```text
/sp.change-management Add due dates to tasks feature
```

### 2. Identify Existing Feature Structure

Scan project for feature:
- Find spec file: `specs/[feature]/spec.md`
- Find plan file: `specs/[feature]/plan.md`
- Find tasks file: `specs/[feature]/tasks.md`
- Find implementation files (scan code references)
- Find tests (unit, integration, edge cases)
- Find database schema references

**Feature discovery output:**
```text
🔍 Feature Discovery: tasks

📁 Existing Structure:
  - Spec: specs/tasks/spec.md
  - Plan: specs/tasks/plan.md
  - Tasks: specs/tasks/tasks.md
  - Implementation:
    - backend/src/models/task.py
    - backend/src/mcp_tools/add_task_tool.py
    - backend/src/mcp_tools/list_tasks_tool.py
    - backend/src/mcp_tools/update_task_tool.py
  - Tests:
    - tests/test_task_model.py
    - tests/test_task_tools.py
    - tests/edge_cases/test_task_edge_cases.py
  - Database:
    - backend/src/db/models.py (Task table)

🎯 Change Target: Add due dates to tasks
```

### 3. Create Change Subfolder Structure

Create change tracking subfolder:

**Structure: `specs/[feature]/changes/[YYYY-MM-DD]-[change-slug]/`**

```text
specs/tasks/changes/2025-12-30-add-due-dates/
├── change-spec.md           # What's changing and why
├── change-plan.md           # How to implement the change
├── change-tasks.md          # Task breakdown for change
├── impact-analysis.md       # All affected areas
└── rollback-plan.md         # How to revert if needed
```

### 4. Generate Change Specification

**File: `specs/[feature]/changes/[date]-[slug]/change-spec.md`**

```markdown
# Change: Add Due Dates to Tasks

**Feature**: tasks
**Change Type**: enhancement
**Date**: 2025-12-30
**Status**: In Progress

## Change Description

Add optional due_date field to tasks to enable deadline tracking.

## Motivation

Users need to track task deadlines for better time management.

## User Impact

- Users can set due dates when creating tasks
- Users can view tasks sorted by due date
- Overdue tasks highlighted in UI
- No breaking changes to existing tasks

## Acceptance Criteria

- [ ] Tasks can have optional due_date (datetime)
- [ ] Due dates displayed in task list
- [ ] Tasks sortable by due date
- [ ] Overdue tasks visually distinguished
- [ ] Existing tasks unaffected (backward compatible)

## Non-Goals

- Recurring tasks (separate change)
- Reminders/notifications (separate change)
```

### 5. Perform Impact Analysis

Analyze all areas affected by change:

**File: `specs/[feature]/changes/[date]-[slug]/impact-analysis.md`**

```markdown
# Impact Analysis: Add Due Dates to Tasks

## Database Schema Changes

### Task Model (backend/src/models/task.py)
- **Add field**: `due_date: Optional[datetime]`
- **Migration required**: Yes
- **Backward compatible**: Yes (field is optional)

\`\`\`python
# Before
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: Optional[str]
    completed: bool = False

# After
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: Optional[str]
    completed: bool = False
    due_date: Optional[datetime] = None  # NEW FIELD
\`\`\`

## MCP Tools Changes

### add_task_tool.py
- **Change**: Add optional `due_date` parameter
- **Breaking**: No (parameter is optional)
- **Tests affected**: tests/test_add_task_tool.py

### update_task_tool.py
- **Change**: Allow updating due_date
- **Breaking**: No
- **Tests affected**: tests/test_update_task_tool.py

### list_tasks_tool.py
- **Change**: Add sort_by="due_date" option
- **Breaking**: No
- **Tests affected**: tests/test_list_tasks_tool.py

## API Changes

### Chat Endpoint (backend/src/api/chat.py)
- **Change**: None (tools handle due dates)
- **Breaking**: No

## Frontend Changes

### Task Display Component
- **Change**: Show due_date if present
- **Breaking**: No
- **Files**: frontend/src/components/TaskList.tsx

### Task Form Component
- **Change**: Add due_date input field
- **Breaking**: No
- **Files**: frontend/src/components/TaskForm.tsx

## Test Changes

### Unit Tests
- **New tests**: Test due_date parameter in tools
- **Updated tests**: Existing tool tests remain valid
- **Files**: tests/test_task_tools.py

### Integration Tests
- **New tests**: Test sorting by due_date
- **Updated tests**: None
- **Files**: tests/integration/test_task_workflows.py

### Edge Cases
- **New edge cases**:
  - Past due dates
  - Far future due dates
  - Invalid date formats
  - Null/missing due dates
- **Files**: tests/edge_cases/test_task_edge_cases.py

## Documentation Changes

- **README.md**: Update feature list
- **API docs**: Update tool parameters
- **Constitution**: No changes (compatible)
- **User guide**: Add due date usage examples

## Rollback Plan

If change causes issues:
1. Revert database migration
2. Revert code changes (git revert)
3. Redeploy previous version
4. due_date field remains in DB (nullable, harmless)

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Migration fails | Low | High | Test on staging first |
| Frontend breaks | Low | Medium | Backward compatible design |
| Performance impact | Low | Low | Index on due_date |

## Estimated Effort

- Database migration: 1 hour
- MCP tools update: 2 hours
- Frontend update: 3 hours
- Testing (all levels): 3 hours
- **Total**: ~9 hours
```

### 6. Generate Change Tasks

**File: `specs/[feature]/changes/[date]-[slug]/change-tasks.md`**

```markdown
# Tasks: Add Due Dates to Tasks

## Phase 1: Database Changes

- [ ] T001 Add due_date field to Task model
- [ ] T002 Create database migration script
- [ ] T003 Test migration on staging database
- [ ] T004 Add index on due_date for performance

## Phase 2: MCP Tools Update

- [ ] T005 Update add_task tool to accept due_date
- [ ] T006 Update update_task tool for due_date modification
- [ ] T007 Update list_tasks tool with sort_by="due_date"
- [ ] T008 Update tool contracts documentation

## Phase 3: Testing (TDD - Red Phase)

- [ ] T009 Write tests for due_date parameter (should FAIL)
- [ ] T010 Write edge case tests (invalid dates, null, etc.)
- [ ] T011 Write integration test for sorting by due_date

## Phase 4: Implementation (Green Phase)

- [ ] T012 Implement due_date in add_task tool
- [ ] T013 Implement due_date in update_task tool
- [ ] T014 Implement sort_by in list_tasks tool
- [ ] T015 Verify all tests pass

## Phase 5: Frontend Update

- [ ] T016 Add due_date input to TaskForm
- [ ] T017 Display due_date in TaskList
- [ ] T018 Highlight overdue tasks
- [ ] T019 Test frontend with backend

## Phase 6: Edge Case Testing

- [ ] T020 Run /sp.edge-case-tester for due_date feature
- [ ] T021 Verify all edge cases pass
- [ ] T022 Document edge cases tested

## Phase 7: A/B Testing (Optional)

- [ ] T023 Setup A/B test for due date UI variants
- [ ] T024 Monitor user engagement metrics

## Phase 8: Documentation & Deployment

- [ ] T025 Update README and API docs
- [ ] T026 Update user guide with examples
- [ ] T027 Deploy to staging
- [ ] T028 Run full test suite on staging
- [ ] T029 Deploy to production
- [ ] T030 Monitor for issues
```

### 7. Auto-Update All Affected Areas

Automatically update affected files:

**Database Model:**
```python
# Auto-update: backend/src/models/task.py
# Add field with migration script reference
due_date: Optional[datetime] = Field(default=None, description="Task due date")
```

**MCP Tool Schemas:**
```python
# Auto-update: backend/src/mcp_tools/add_task_tool.py
class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None  # AUTO-ADDED
```

**Tests:**
```python
# Auto-update: tests/test_add_task_tool.py
@pytest.mark.asyncio
async def test_add_task_with_due_date():  # AUTO-GENERATED
    """Test adding task with due date"""
    result = await add_task({
        "user_id": "test",
        "title": "Test",
        "due_date": "2025-12-31T23:59:59"
    })
    assert result.due_date is not None
```

**Constitution Check:**
```text
Constitution Impact Analysis:
✓ Stateless Architecture: No impact (due_date stored in DB)
✓ User Isolation: No impact (user_id still enforced)
✓ MCP-First: Compatible (tools updated)
✓ Database-Centric: Aligned (due_date in DB)
✓ Test-First: Enforced (tests written before implementation)

No constitution violations detected.
```

### 8. Create Rollback Plan

**File: `specs/[feature]/changes/[date]-[slug]/rollback-plan.md`**

```markdown
# Rollback Plan: Add Due Dates to Tasks

## Quick Rollback (Emergency)

\`\`\`bash
# 1. Revert code deployment
git revert [commit-hash]
git push origin main

# 2. Redeploy previous version
kubectl rollout undo deployment/backend

# 3. Monitor recovery
kubectl logs -f deployment/backend
\`\`\`

## Database Rollback

\`\`\`sql
-- Remove due_date column (if necessary)
ALTER TABLE tasks DROP COLUMN due_date;
\`\`\`

**Note**: If data was written to due_date, decide:
- Keep column (harmless, nullable)
- Archive data before dropping

## Frontend Rollback

\`\`\`bash
# Redeploy previous frontend version
cd frontend
git revert [commit-hash]
npm run build
vercel --prod
\`\`\`

## Verification After Rollback

- [ ] Application loads without errors
- [ ] Existing features work (add, list, complete, delete tasks)
- [ ] No user data lost
- [ ] Performance normal

## Communication Plan

If rollback required:
1. Post incident notice
2. Explain issue and resolution
3. Provide timeline for fix and re-deployment
```

### 9. Execute Change Workflow

Run standard development workflow with change context:

```bash
# 1. Create feature branch for change
git checkout -b change/add-due-dates

# 2. Run change tasks
/sp.implement specs/tasks/changes/2025-12-30-add-due-dates/change-tasks.md

# 3. Run edge case testing
/sp.edge-case-tester --feature tasks --change add-due-dates

# 4. Run A/B testing (if applicable)
/sp.ab-testing --feature tasks --test due-date-ui

# 5. Commit and create PR
/sp.git.commit_pr "feat: add due dates to tasks"
```

### 10. Display Change Management Summary

```text
✅ Change Management Initiated: Add Due Dates to Tasks

📁 Change Tracking:
  - Change Spec: specs/tasks/changes/2025-12-30-add-due-dates/change-spec.md
  - Impact Analysis: specs/tasks/changes/2025-12-30-add-due-dates/impact-analysis.md
  - Change Tasks: specs/tasks/changes/2025-12-30-add-due-dates/change-tasks.md
  - Rollback Plan: specs/tasks/changes/2025-12-30-add-due-dates/rollback-plan.md

🔄 Affected Areas (Auto-Updated):
  ✓ Database: Task model (due_date field added)
  ✓ MCP Tools: 3 tools updated (add, update, list)
  ✓ Tests: 12 tests auto-generated
  ✓ Frontend: 2 components updated
  ✓ Documentation: README, API docs updated

✅ Constitution Compliance:
  ✓ No violations detected
  ✓ Backward compatible
  ✓ Test-driven approach enforced
  ✓ Stateless architecture preserved

📋 Next Steps:
  1. Review impact analysis
  2. Run: /sp.implement specs/tasks/changes/.../change-tasks.md
  3. Execute TDD workflow (Red → Green → Refactor)
  4. Run edge case testing
  5. Deploy to staging
  6. Monitor and validate
  7. Deploy to production

⏱️ Estimated Effort: 9 hours
```

## Change Management Best Practices

1. **Always create change subfolder** - Never modify original specs directly
2. **Impact analysis first** - Understand all affected areas before coding
3. **Backward compatibility** - Avoid breaking existing functionality
4. **Rollback plan ready** - Always have escape hatch
5. **Test all affected areas** - Not just the changed code
6. **Update all documentation** - Keep project coherent

## Success Criteria

- [ ] Change subfolder created with all artifacts
- [ ] Impact analysis identifies all affected areas
- [ ] All affected files auto-updated
- [ ] Tests auto-generated for changes
- [ ] Rollback plan documented
- [ ] Constitution compliance verified
- [ ] No breaking changes (unless explicitly stated)
- [ ] Documentation updated

## Notes

- Used when modifying existing features
- Ensures changes don't break existing functionality
- Maintains project coherence across all areas
- Terminal shows comprehensive change impact
- Part of TDD approach per constitution
