# Data Model: Backend API Foundation

**Feature**: Backend API Foundation  
**Branch**: `001-backend-api-foundation`  
**Date**: 2025-12-09  
**Status**: Complete

## Purpose

This document defines the database schema, entities, relationships, and constraints for the Todo application backend. The schema is designed to support multi-user task management with proper data isolation and integrity.

---

## Database Technology

- **DBMS**: PostgreSQL 15+ (Neon Serverless)
- **ORM**: SQLModel 0.0.14+
- **Migration Tool**: Alembic 1.13+
- **Connection Pooling**: SQLAlchemy engine (via SQLModel)

---

## Entity Relationship Diagram

```text
┌─────────────────────────┐
│        users            │
├─────────────────────────┤
│ id (PK) : VARCHAR(255)  │◄─────────┐
│ email : VARCHAR(255)    │          │
│ name : VARCHAR(255)     │          │ One-to-Many
│ created_at : TIMESTAMP  │          │ (One user has many tasks)
└─────────────────────────┘          │
                                     │
                                     │
┌─────────────────────────┐          │
│        tasks            │          │
├─────────────────────────┤          │
│ id (PK) : SERIAL        │          │
│ user_id (FK) : VARCHAR  │──────────┘
│ title : VARCHAR(200)    │
│ description : TEXT      │
│ completed : BOOLEAN     │
│ created_at : TIMESTAMP  │
│ updated_at : TIMESTAMP  │
└─────────────────────────┘
```

---

## Entity Definitions

### 1. User Entity

**Purpose**: Represents a user account in the system. Managed by Better Auth (to be implemented in Feature 2).

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR(255) | PRIMARY KEY | User unique identifier (UUID from Better Auth) |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address for login |
| `name` | VARCHAR(255) | NULL | User display name (optional) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email` (for login lookups)

**Constraints**:
- `email` must be unique across all users
- `id` is provided by Better Auth (UUID format)

**Relationships**:
- One User → Many Tasks (via `tasks.user_id`)

**Notes**:
- This table structure is prepared for Feature 2 (Authentication System)
- For Feature 1 testing, dummy user records can be inserted manually
- Better Auth will manage user creation, updates, and password hashing in Feature 2

---

### 2. Task Entity

**Purpose**: Represents a todo item belonging to a specific user.

**Table Name**: `tasks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing task identifier |
| `user_id` | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Owner of the task |
| `title` | VARCHAR(200) | NOT NULL, LENGTH >= 1 | Task title (required, 1-200 chars) |
| `description` | TEXT | NULL, LENGTH <= 1000 | Task description (optional, max 1000 chars) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for filtering tasks by user)
- INDEX on `completed` (for status filtering)
- COMPOSITE INDEX on `(user_id, completed)` (for user-specific status queries)

**Foreign Keys**:
- `user_id` → `users.id` (ON DELETE CASCADE)
  - When a user is deleted, all their tasks are automatically deleted

**Constraints**:
- `title` length: 1-200 characters (enforced at application and database level)
- `description` length: max 1000 characters (enforced at application level)
- `user_id` must reference valid user in `users` table

**Validation Rules** (Application Level):
- `title` cannot be empty string or whitespace only
- `title` must be trimmed before storage
- `description` can be null or empty
- `completed` defaults to false on creation

**Automatic Timestamps**:
- `created_at`: Set automatically on INSERT (database default)
- `updated_at`: Updated automatically on UPDATE (application trigger)

---

## SQLModel Implementation

### User Model

```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    """User account managed by Better Auth."""
    
    __tablename__ = "users"
    
    id: str = Field(
        primary_key=True,
        description="UUID from Better Auth"
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    
    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Task Model

```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    """Todo task belonging to a user."""
    
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing task ID"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID"
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")
```

---

## Migration Strategy

### Initial Migration (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate initial migration from SQLModel models
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Migration File Example

```python
# alembic/versions/001_create_users_and_tasks.py
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_completed', 'tasks', ['completed'])
    op.create_index('ix_tasks_user_id_completed', 'tasks', ['user_id', 'completed'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

---

## Data Validation

### Application-Level Validation (Pydantic Schemas)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class TaskCreate(BaseModel):
    """Request schema for creating a task."""
    
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()
    
    @validator('description')
    def description_length(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v

class TaskUpdate(BaseModel):
    """Request schema for updating a task."""
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and (not v or v.strip() == ""):
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v
```

---

## Query Patterns

### Common Query Examples

```python
from sqlmodel import Session, select
from datetime import datetime

# Get all tasks for a user
def get_user_tasks(session: Session, user_id: str):
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()

# Get completed tasks for a user
def get_completed_tasks(session: Session, user_id: str):
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    return session.exec(statement).all()

# Create a new task
def create_task(session: Session, user_id: str, title: str, description: Optional[str] = None):
    task = Task(
        user_id=user_id,
        title=title,
        description=description
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Update a task
def update_task(session: Session, task_id: int, title: Optional[str] = None, description: Optional[str] = None):
    task = session.get(Task, task_id)
    if not task:
        return None
    
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Delete a task
def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True
```

---

## Performance Considerations

### Index Strategy

**Purpose**: Optimize common query patterns

| Index | Columns | Query Pattern | Expected Speedup |
|-------|---------|---------------|------------------|
| `ix_users_email` | email (UNIQUE) | Login lookups | 100x faster than full scan |
| `ix_tasks_user_id` | user_id | Filter tasks by user | 50x faster for user's tasks |
| `ix_tasks_completed` | completed | Filter by status | 10x faster for status queries |
| `ix_tasks_user_id_completed` | user_id, completed | User's tasks by status | 100x faster for combined filter |

### Connection Pooling

**Configuration** (in db.py):
```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Minimum 5 connections
    max_overflow=5,        # Up to 10 total connections
    pool_timeout=30,       # Wait 30s for available connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True     # Verify connection health
)
```

**Rationale**:
- Avoids connection overhead for each request
- Neon serverless handles scaling on their side
- Pool size of 10 total is sufficient for MVP

---

## Data Integrity Rules

### Referential Integrity

1. **User → Task**: CASCADE DELETE
   - When user is deleted, all their tasks are automatically removed
   - Prevents orphaned tasks in database

2. **Foreign Key Validation**:
   - Cannot create task with invalid user_id
   - Database rejects INSERT/UPDATE with non-existent user_id

### Consistency Rules

1. **Timestamps**:
   - `created_at` is immutable (set once on creation)
   - `updated_at` is updated on every modification
   - Both timestamps use UTC timezone

2. **Title Validation**:
   - Cannot be NULL (database constraint)
   - Cannot be empty (application validation)
   - Must be 1-200 characters (database constraint + application validation)

3. **Completion Status**:
   - Defaults to FALSE (not completed)
   - Can be toggled via PATCH endpoint
   - Cannot be NULL

---

## Testing Considerations

### Test Data Setup

```python
# Fixture for creating test user
@pytest.fixture
def test_user(session: Session):
    user = User(
        id="test-user-uuid",
        email="test@example.com",
        name="Test User"
    )
    session.add(user)
    session.commit()
    return user

# Fixture for creating test task
@pytest.fixture
def test_task(session: Session, test_user: User):
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description"
    )
    session.add(task)
    session.commit()
    return task
```

### Edge Cases to Test

1. **Empty Title**: Should be rejected (validation error)
2. **Title > 200 chars**: Should be rejected (validation error)
3. **Description > 1000 chars**: Should be rejected (validation error)
4. **Invalid user_id**: Should be rejected (foreign key violation)
5. **Delete user with tasks**: Tasks should be cascade deleted
6. **Concurrent updates**: Last write wins (updated_at timestamp tracking)

---

## Future Enhancements (Out of Scope for Feature 1)

- **Priority field**: Add `priority` enum (low, medium, high)
- **Tags/Categories**: Many-to-many relationship with tags table
- **Due dates**: Add `due_date` TIMESTAMP field
- **Recurring tasks**: Add recurrence pattern support
- **Task ordering**: Add `order` INTEGER field for custom sorting
- **Soft deletes**: Add `deleted_at` TIMESTAMP for archiving instead of hard delete

These enhancements are deferred to Phase 5 (Advanced Features).

---

## Summary

**Tables Created**: 2 (users, tasks)  
**Relationships**: 1 (One-to-Many: User → Tasks)  
**Indexes**: 4 (email, user_id, completed, composite)  
**Foreign Keys**: 1 (tasks.user_id → users.id with CASCADE DELETE)  
**Constraints**: Title length (1-200), Description length (max 1000)

**Status**: ✅ Ready for implementation

