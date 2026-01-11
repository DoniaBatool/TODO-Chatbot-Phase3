"""MCP Tool: update_task

Updates task title, description, or priority for the authenticated user.

This tool enables AI agents to modify task details based on
natural language input.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from sqlmodel import Session, select
import logging

from ..models import Task

logger = logging.getLogger(__name__)


class UpdateTaskParams(BaseModel):
    """Input parameters for update_task tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        priority: New task priority level (optional)
        due_date: New task due date (optional)
        completed: Mark as completed (True) or incomplete (False) (optional)
    """

    user_id: str = Field(..., description="User ID for task ownership")
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, description="New task title")
    description: Optional[str] = Field(None, description="New task description")
    priority: Optional[str] = Field(
        None,
        description="New task priority level (high, medium, low)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="New task due date"
    )
    completed: Optional[bool] = Field(
        None,
        description="Mark task as completed (True) or incomplete (False)"
    )

    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values."""
        if v is None:
            return v
        allowed = ["high", "medium", "low"]
        if v not in allowed:
            raise ValueError(
                f"Invalid priority: {v}. Must be one of: {', '.join(allowed)}"
            )
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "task_id": 3,
                "title": "Buy milk and eggs",
                "priority": "high"
            }
        }


class UpdateTaskResult(BaseModel):
    """Result from update_task tool execution.

    Attributes:
        task_id: ID of the updated task
        title: Updated task title
        description: Updated task description
        completed: Task completion status
        priority: Task priority level
        due_date: Task due date
        updated_at: Timestamp when task was updated
    """

    task_id: int = Field(..., description="ID of the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    priority: str = Field(..., description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    updated_at: datetime = Field(..., description="Timestamp of update")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "task_id": 3,
                "title": "Buy milk and eggs",
                "description": "From grocery store",
                "completed": False,
                "priority": "high",
                "updated_at": "2025-12-30T16:30:00Z"
            }
        }


def update_task(db: Session, params: UpdateTaskParams) -> UpdateTaskResult:
    """Update task title, description, or priority.

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
        - At least one field (title, description, or priority) must be provided

    Example:
        >>> params = UpdateTaskParams(
        ...     user_id="user-123",
        ...     task_id=3,
        ...     title="Buy milk and eggs",
        ...     priority="high"
        ... )
        >>> result = update_task(db, params)
        >>> assert result.title == "Buy milk and eggs"
        >>> assert result.priority == "high"
    """
    # Validate at least one field provided (T128)
    # Check if any field was explicitly set (using __fields_set__)
    updateable_fields = {'title', 'description', 'priority', 'due_date', 'completed'}
    if not any(field in params.__fields_set__ for field in updateable_fields):
        raise ValueError("At least one field (title, description, priority, due_date, or completed) must be provided")

    logger.info(
        f"update_task: Querying task {params.task_id} for user {params.user_id}",
        extra={
            "user_id": params.user_id,
            "task_id": params.task_id,
            "fields_to_update": {
                "title": params.title,
                "description": params.description,
                "priority": params.priority,
                "due_date": params.due_date,
                "completed": params.completed
            }
        }
    )

    # Query task with user_id AND task_id (T129)
    # This enforces user isolation
    query = select(Task).where(
        Task.id == params.task_id,
        Task.user_id == params.user_id
    )

    try:
        result = db.exec(query).first()
    except Exception as e:
        logger.error(f"update_task: Query failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to query task: {str(e)}") from e

    # Handle task not found
    if not result:
        logger.warning(
            f"update_task: Task {params.task_id} not found for user {params.user_id}",
            extra={"user_id": params.user_id, "task_id": params.task_id}
        )
        raise ValueError("Task not found")

    task = result

    logger.info(
        f"update_task: Found task - id={task.id}, title={task.title}",
        extra={"user_id": params.user_id, "task_id": task.id, "old_title": task.title}
    )

    # Update provided fields (T130)
    # Use __fields_set__ to detect which fields were explicitly provided
    # This allows us to distinguish between "not provided" vs "provided as None"
    fields_set = params.__fields_set__

    if 'title' in fields_set:
        task.title = params.title
    if 'description' in fields_set:
        task.description = params.description
    if 'priority' in fields_set:
        task.priority = params.priority
    if 'due_date' in fields_set:
        # If explicitly set (even to None), update it
        # This allows removing due dates by setting them to None
        task.due_date = params.due_date
    if 'completed' in fields_set:
        task.completed = params.completed

    # Always update timestamp (T022)
    task.updated_at = datetime.utcnow()

    # Persist changes
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(
            f"update_task: Successfully committed task {task.id} to database",
            extra={
                "user_id": params.user_id,
                "task_id": task.id,
                "new_title": task.title,
                "new_priority": task.priority
            }
        )
    except Exception as e:
        logger.error(
            f"update_task: Commit failed for task {params.task_id}: {str(e)}",
            extra={"user_id": params.user_id, "task_id": params.task_id},
            exc_info=True
        )
        db.rollback()
        raise RuntimeError(f"Failed to update task: {str(e)}") from e

    # Return result (T131)
    return UpdateTaskResult(
        task_id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,
        due_date=task.due_date,
        updated_at=task.updated_at
    )
