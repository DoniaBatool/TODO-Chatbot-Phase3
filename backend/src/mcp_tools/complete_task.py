"""MCP Tool: complete_task

Marks a task as completed for the authenticated user.

This tool enables AI agents to mark tasks as complete based on
natural language input.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..models import Task


class CompleteTaskParams(BaseModel):
    """Input parameters for complete_task tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        task_id: ID of the task to mark as complete
    """

    user_id: str = Field(..., description="User ID for task ownership")
    task_id: int = Field(..., description="ID of the task to mark as complete")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "task_id": 5
            }
        }


class CompleteTaskResult(BaseModel):
    """Result from complete_task tool execution.

    Attributes:
        task_id: ID of the completed task
        title: Task title
        description: Task description (if any)
        completed: Task completion status (always True)
        updated_at: Timestamp when task was marked complete
    """

    task_id: int = Field(..., description="ID of the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(True, description="Task completion status")
    updated_at: datetime = Field(..., description="Timestamp of completion")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "task_id": 5,
                "title": "Buy milk",
                "description": None,
                "completed": True,
                "updated_at": "2025-12-30T15:45:00Z"
            }
        }


def complete_task(db: Session, params: CompleteTaskParams) -> CompleteTaskResult:
    """Mark a task as completed.

    This is the core MCP tool function that AI agents call to complete tasks.

    Args:
        db: Database session
        params: Task completion parameters

    Returns:
        CompleteTaskResult with updated task details

    Raises:
        ValueError: If task not found or doesn't belong to user

    Security:
        - Enforces user isolation: query filters by both user_id AND task_id
        - Returns generic "not found" error (doesn't reveal if task exists for other user)

    Idempotency:
        - Completing an already-completed task succeeds without error
        - Updates timestamp even if already complete

    Example:
        >>> params = CompleteTaskParams(
        ...     user_id="user-123",
        ...     task_id=5
        ... )
        >>> result = complete_task(db, params)
        >>> assert result.completed is True
    """
    # Query task with user_id AND task_id (T104)
    # This enforces user isolation - users can only complete their own tasks
    query = select(Task).where(
        Task.id == params.task_id,
        Task.user_id == params.user_id
    )

    try:
        result = db.exec(query).first()
    except Exception as e:
        raise RuntimeError(f"Failed to query task: {str(e)}") from e

    # Handle task not found (T107)
    # Returns generic error - doesn't reveal if task exists for other user
    if not result:
        raise ValueError("Task not found")

    task = result

    # Update completed status and timestamp (T105)
    task.completed = True
    task.updated_at = datetime.utcnow()

    # Persist changes
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to update task: {str(e)}") from e

    # Return result (T106)
    return CompleteTaskResult(
        task_id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        updated_at=task.updated_at
    )
