---
description: Implement declarative input validation with Pydantic DTOs for FastAPI applications (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements Pydantic-based input/output validation following Phase 2's pattern. Ensures type safety, automatic validation, and clean API contracts.

### 1. Understand DTO Pattern

**DTO = Data Transfer Object**

Separate schemas for different purposes:
- **Request DTOs**: Input validation (TaskCreate, TaskUpdate)
- **Response DTOs**: Output shaping (TaskResponse, UserResponse)
- **Database Models**: Persistence (Task, User with SQLModel)

### 2. Create Request DTO - Input Validation

**File**: `src/schemas.py`

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class TaskCreate(BaseModel):
    """
    Request schema for creating task.
    Validates input before it reaches business logic.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Custom validator: reject whitespace-only titles"""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()  # Clean whitespace

    @field_validator("description")
    @classmethod
    def description_not_too_long(cls, v: Optional[str]) -> Optional[str]:
        """Ensure description within limit"""
        if v and len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v


class TaskUpdate(BaseModel):
    """
    Request schema for updating task.
    All fields optional (partial update).
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided"""
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Title cannot be empty if provided")
        return v.strip() if v else v
```

### 3. Create Response DTO - Output Shaping

**File**: `src/schemas.py`

```python
from datetime import datetime

class TaskResponse(BaseModel):
    """
    Response schema for task data.
    Shapes output, excludes sensitive fields.
    """

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    # Enable conversion from SQLModel
    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """
    Response schema for user data.
    EXCLUDES password_hash for security.
    """

    id: str
    email: str
    name: Optional[str]
    created_at: datetime

    # password_hash intentionally excluded
    model_config = {"from_attributes": True}
```

### 4. Use in FastAPI Routes

**Automatic Validation**:

```python
from fastapi import APIRouter, HTTPException
from src.schemas import TaskCreate, TaskResponse

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,  # Pydantic validates automatically
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    """
    Create task endpoint.

    FastAPI automatically:
    1. Validates request body against TaskCreate schema
    2. Returns 422 if validation fails
    3. Provides detailed error messages
    4. Converts response to TaskResponse format
    """

    # If we reach here, validation passed
    task = Task(
        user_id=user_id,
        **task_data.model_dump()  # Convert DTO to dict
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Automatically serialized to TaskResponse
    return task
```

### 5. Validation Error Response

**Automatic from FastAPI + Pydantic**:

Request:
```json
{
  "title": "",
  "description": "This is a very long description..." // > 1000 chars
}
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "title"],
      "msg": "Title cannot be empty or whitespace",
      "input": ""
    },
    {
      "type": "value_error",
      "loc": ["body", "description"],
      "msg": "Description cannot exceed 1000 characters",
      "input": "This is a very long description..."
    }
  ]
}
```

### 6. Complex Validation Examples

**Email Validation**:

```python
from pydantic import EmailStr

class SignupRequest(BaseModel):
    email: EmailStr  # Automatic email format validation
    password: str = Field(min_length=8)
    name: Optional[str] = None
```

**Nested Models**:

```python
class Address(BaseModel):
    street: str
    city: str
    zipcode: str = Field(pattern=r'^\d{5}$')

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    address: Optional[Address] = None
```

**List Validation**:

```python
class BulkTaskCreate(BaseModel):
    tasks: List[TaskCreate] = Field(
        min_length=1,
        max_length=100,
        description="Batch create up to 100 tasks"
    )
```

**Custom Validators with Dependencies**:

```python
from pydantic import model_validator

class TaskCreate(BaseModel):
    title: str
    priority: int = Field(ge=1, le=5)
    due_date: Optional[datetime] = None

    @model_validator(mode='after')
    def check_due_date_in_future(self):
        """Validate due_date is in future"""
        if self.due_date and self.due_date < datetime.utcnow():
            raise ValueError("Due date must be in the future")
        return self
```

### 7. Testing Validation

**File**: `tests/test_schemas.py`

```python
import pytest
from pydantic import ValidationError
from src.schemas import TaskCreate

def test_task_create_valid():
    """Test valid task creation"""
    task = TaskCreate(
        title="Buy milk",
        description="Get 2% milk"
    )
    assert task.title == "Buy milk"
    assert task.description == "Get 2% milk"


def test_task_create_empty_title():
    """Test empty title raises error"""
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(title="   ", description="Test")

    errors = exc_info.value.errors()
    assert any("empty" in str(e["msg"]).lower() for e in errors)


def test_task_create_title_too_long():
    """Test title length validation"""
    with pytest.raises(ValidationError):
        TaskCreate(title="x" * 201)  # Exceeds 200 char limit


def test_task_create_description_optional():
    """Test description is optional"""
    task = TaskCreate(title="Test")
    assert task.description is None
```

## Benefits of DTOs

**Type Safety**:
- IDE autocomplete
- Compile-time error detection (with type checkers)
- Clear contracts

**Security**:
- Exclude sensitive fields (password_hash)
- Validate before business logic
- Prevent injection attacks

**API Versioning**:
- Change response without changing DB
- Multiple response formats (v1, v2)
- Backward compatibility

**Documentation**:
- Auto-generated OpenAPI schema
- Clear field descriptions
- Example values

## Constitution Alignment

- ✅ **Security Standards**: Input validation prevents injection
- ✅ **API Contracts**: Clear request/response schemas
- ✅ **Type Safety**: Pydantic enforces types
- ✅ **Observability**: Validation errors logged

## Success Criteria

- [ ] Request DTOs created for all inputs (Create, Update)
- [ ] Response DTOs exclude sensitive fields (password_hash)
- [ ] Field constraints defined (min/max length, patterns)
- [ ] Custom validators for complex rules
- [ ] FastAPI routes use Pydantic schemas
- [ ] 422 returned for validation failures
- [ ] Validation error messages clear and actionable
- [ ] Tests verify validation rules
- [ ] model_config = {"from_attributes": True} for SQLModel conversion

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 4
- Pydantic Documentation: https://docs.pydantic.dev/
- FastAPI Validation: https://fastapi.tiangolo.com/tutorial/body/
