---
description: Enforce user isolation with ownership checks at database query level to prevent horizontal privilege escalation (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements user isolation following Phase 2's security pattern. Ensures users can only access their own data through database-level filtering and explicit ownership checks.

### 1. Parse Requirements

Extract from user input:
- What entities are user-owned? (Tasks, Conversations, Messages)
- What operations need ownership checks? (GET, PUT, PATCH, DELETE)
- Should return 403 or 404 for unauthorized access? (403 recommended)
- Is audit logging required for violations?

### 2. Database Schema Requirements

**Ensure user_id column exists**:

```python
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    user_id: str = Field(
        foreign_key="users.id",
        index=True,  # CRITICAL: Index for performance
        description="Owner user ID"
    )
    title: str
    completed: bool = False
    # ... other fields
```

**Create index** (if not auto-generated):
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

### 3. List Operations - Query Scoping

**Pattern**: Filter at query level, not in code

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from src.auth.dependencies import get_current_user

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    completed: Optional[bool] = Query(default=None),
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """List tasks - automatically scoped to authenticated user"""

    # Build query scoped to authenticated user
    statement = select(Task).where(Task.user_id == current_user_id)

    # Apply optional filters
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    # Execute - only returns this user's tasks
    tasks = session.exec(statement).all()
    return tasks
```

**NEVER do this** (filtering after fetch):
```python
# ❌ WRONG - Fetches all users' data then filters
all_tasks = session.exec(select(Task)).all()
user_tasks = [t for t in all_tasks if t.user_id == current_user_id]
```

### 4. Single Record - Explicit Ownership Check

**Pattern**: Fetch → Check existence → Check ownership → Return or 403

```python
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Get single task with ownership verification"""

    # Fetch task
    task = session.get(Task, task_id)

    # Check existence
    if not task:
        logger.warning("Task not found: user=%s task_id=%s", current_user_id, task_id)
        raise HTTPException(404, f"Task {task_id} not found")

    # Check ownership
    if task.user_id != current_user_id:
        logger.warning(
            "SECURITY: Forbidden access - user=%s attempted task_id=%s owned_by=%s",
            current_user_id, task_id, task.user_id
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Task does not belong to you"
        )

    return task
```

### 5. Create Operations - user_id from JWT

**Pattern**: Always use authenticated user_id, ignore client input

```python
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Create task - user_id from JWT, not client"""

    # SECURITY: Always use authenticated user_id
    # Ignore any user_id in request body
    task = Task(
        user_id=current_user_id,  # From JWT token
        title=task_data.title,
        description=task_data.description
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### 6. Update/Delete Operations - Ownership Check

**Pattern**: Same as GET single record

```python
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Update task with ownership check"""

    task = session.get(Task, task_id)

    # Existence check
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")

    # Ownership check
    if task.user_id != current_user_id:
        logger.warning(
            "SECURITY: Forbidden update - user=%s task_id=%s owned_by=%s",
            current_user_id, task_id, task.user_id
        )
        raise HTTPException(403, "Forbidden: Task does not belong to you")

    # Update allowed
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Delete task with ownership check"""

    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(404, f"Task {task_id} not found")

    if task.user_id != current_user_id:
        logger.warning(
            "SECURITY: Forbidden delete - user=%s task_id=%s owned_by=%s",
            current_user_id, task_id, task.user_id
        )
        raise HTTPException(403, "Forbidden: Task does not belong to you")

    session.delete(task)
    session.commit()
    return None  # 204 No Content
```

### 7. Testing - User Isolation Verification

**File**: `tests/test_user_isolation.py`

```python
import pytest
from httpx import AsyncClient

async def test_user_cannot_access_other_user_tasks(client: AsyncClient):
    """Test user isolation - users can't see each other's tasks"""

    # Create user A and their task
    user_a_token = await create_user_and_login(client, "a@test.com")
    task_a = await create_task(client, user_a_token, "Task A")

    # Create user B
    user_b_token = await create_user_and_login(client, "b@test.com")

    # User B tries to access User A's task - should get 403
    response = await client.get(
        f"/api/tasks/{task_a['id']}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )

    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


async def test_list_tasks_returns_only_user_tasks(client: AsyncClient):
    """Test list returns only authenticated user's tasks"""

    # User A creates 2 tasks
    user_a_token = await create_user_and_login(client, "a@test.com")
    await create_task(client, user_a_token, "Task A1")
    await create_task(client, user_a_token, "Task A2")

    # User B creates 3 tasks
    user_b_token = await create_user_and_login(client, "b@test.com")
    await create_task(client, user_b_token, "Task B1")
    await create_task(client, user_b_token, "Task B2")
    await create_task(client, user_b_token, "Task B3")

    # User A lists tasks - should see only 2
    response_a = await client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert len(response_a.json()) == 2

    # User B lists tasks - should see only 3
    response_b = await client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    assert len(response_b.json()) == 3
```

## Constitution Alignment

- ✅ **User Isolation & Security**: Enforced at database query level
- ✅ **Security Standards**: No cross-user data leakage
- ✅ **Observability**: Security violations logged with user IDs
- ✅ **Database-Centric**: user_id indexed for performance

## Success Criteria

- [ ] user_id column exists on all user-owned tables
- [ ] user_id indexed for query performance
- [ ] List operations filter by user_id in WHERE clause
- [ ] Single record operations check ownership explicitly
- [ ] Create operations use user_id from JWT (ignore client input)
- [ ] 403 Forbidden returned for ownership violations
- [ ] Security violations logged with both user IDs
- [ ] Tests verify zero cross-user data leakage

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 2
- OWASP: Broken Access Control - https://owasp.org/Top10/A01_2021-Broken_Access_Control/
