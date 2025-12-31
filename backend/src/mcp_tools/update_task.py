"""MCP Tool: update_task

Updates task title or description for the authenticated user.

This tool enables AI agents to modify task details based on
natural language input.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..models import Task


class UpdateTaskParams(BaseModel):
    """Input parameters for update_task tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
    """

    user_id: str = Field(..., description="User ID for task ownership")
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, description="New task title")
    description: Optional[str] = Field(None, description="New task description")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "task_id": 3,
                "title": "Buy milk and eggs"
            }
        }


class UpdateTaskResult(BaseModel):
    """Result from update_task tool execution.

    Attributes:
        task_id: ID of the updated task
        title: Updated task title
        description: Updated task description
        completed: Task completion status
        updated_at: Timestamp when task was updated
    """

    task_id: int = Field(..., description="ID of the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    updated_at: datetime = Field(..., description="Timestamp of update")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "task_id": 3,
                "title": "Buy milk and eggs",
                "description": "From grocery store",
                "completed": False,
                "updated_at": "2025-12-30T16:30:00Z"
            }
        }


def update_task(db: Session, params: UpdateTaskParams) -> UpdateTaskResult:
    """Update task title or description.

    This is the core MCP tool function that AI agents call to update tasks.

    Args:
        db: Database session
        params: Task update parameters

    Returns:
        UpdateTaskResult with updated task details

    Raises:
        ValueError: If task not found, doesn't belong to user, or no fields provided

    Security:
        - Enforces user isolation: query filters by both user_id AND task_id
        - Returns generic "not found" error (doesn't reveal if task exists for other user)

    Validation:
        - At least one field (title or description) must be provided

    Example:
        >>> params = UpdateTaskParams(
        ...     user_id="user-123",
        ...     task_id=3,
        ...     title="Buy milk and eggs"
        ... )
        >>> result = update_task(db, params)
        >>> assert result.title == "Buy milk and eggs"
    """
    # Validate at least one field provided (T128)
    if params.title is None and params.description is None:
        raise ValueError("At least one field (title or description) must be provided")

    # Query task with user_id AND task_id (T129)
    # This enforces user isolation
    query = select(Task).where(
        Task.id == params.task_id,
        Task.user_id == params.user_id
    )

    try:
        result = db.exec(query).first()
    except Exception as e:
        raise RuntimeError(f"Failed to query task: {str(e)}") from e

    # Handle task not found
    if not result:
        raise ValueError("Task not found")

    task = result

    # Update provided fields (T130)
    if params.title is not None:
        task.title = params.title
    if params.description is not None:
        task.description = params.description

    # Always update timestamp
    task.updated_at = datetime.utcnow()

    # Persist changes
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to update task: {str(e)}") from e

    # Return result (T131)
    return UpdateTaskResult(
        task_id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        updated_at=task.updated_at
    )
