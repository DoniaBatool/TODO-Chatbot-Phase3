"""MCP Tool: set_task_deadline

Sets or removes a task's deadline/due date for the authenticated user.

This tool enables AI agents to:
- Set a new deadline for a task
- Update an existing deadline
- Remove a deadline completely (set to None)
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlmodel import Session, select
import logging

from ..models import Task

logger = logging.getLogger(__name__)


class SetTaskDeadlineParams(BaseModel):
    """Input parameters for set_task_deadline tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        task_id: ID of the task to update
        due_date: New deadline (ISO format string) or None to remove deadline
    """

    user_id: str = Field(..., description="User ID for task ownership")
    task_id: int = Field(..., description="ID of the task to update")
    due_date: Optional[str] = Field(
        None,
        description=(
            "New task deadline in ISO 8601 format (e.g., '2026-01-15T14:30:00'). "
            "Set to null to remove the deadline completely. "
            "Examples: 'tomorrow at 5pm', 'next Friday', 'January 20 at 2pm'"
        )
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "task_id": 5,
                "due_date": "2026-01-15T17:00:00"
            }
        }


class SetTaskDeadlineResult(BaseModel):
    """Result from set_task_deadline tool execution.

    Attributes:
        task_id: ID of the updated task
        title: Task title
        due_date: New deadline (or None if removed)
        action: What action was performed (set/updated/removed)
        updated_at: Timestamp when task was updated
    """

    task_id: int = Field(..., description="ID of the task")
    title: str = Field(..., description="Task title")
    due_date: Optional[datetime] = Field(None, description="New task deadline")
    action: str = Field(
        ...,
        description="Action performed: 'set', 'updated', or 'removed'"
    )
    updated_at: datetime = Field(..., description="Timestamp of update")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "task_id": 5,
                "title": "Buy milk",
                "due_date": "2026-01-15T17:00:00",
                "action": "updated",
                "updated_at": "2026-01-12T06:30:00Z"
            }
        }


def set_task_deadline(
    db: Session,
    params: SetTaskDeadlineParams
) -> SetTaskDeadlineResult:
    """Set or remove a task's deadline.

    This is the core MCP tool function that AI agents call to manage deadlines.

    Args:
        db: Database session
        params: Deadline update parameters

    Returns:
        SetTaskDeadlineResult with updated task details

    Raises:
        ValueError: If task not found or doesn't belong to user

    Security:
        - Enforces user isolation: query filters by both user_id AND task_id
        - Returns generic "not found" error (doesn't reveal if task exists for other user)

    Actions:
        - If due_date is provided (not None): Set/update the deadline
        - If due_date is None: Remove the deadline completely

    Example:
        >>> # Set new deadline
        >>> params = SetTaskDeadlineParams(
        ...     user_id="user-123",
        ...     task_id=5,
        ...     due_date="2026-01-15T17:00:00"
        ... )
        >>> result = set_task_deadline(db, params)
        >>> assert result.action in ["set", "updated"]

        >>> # Remove deadline
        >>> params = SetTaskDeadlineParams(
        ...     user_id="user-123",
        ...     task_id=5,
        ...     due_date=None
        ... )
        >>> result = set_task_deadline(db, params)
        >>> assert result.action == "removed"
        >>> assert result.due_date is None
    """
    logger.info(
        f"set_task_deadline: Querying task {params.task_id} for user {params.user_id}",
        extra={
            "user_id": params.user_id,
            "task_id": params.task_id,
            "new_due_date": params.due_date
        }
    )

    # Query task with user_id AND task_id (user isolation)
    query = select(Task).where(
        Task.id == params.task_id,
        Task.user_id == params.user_id
    )

    try:
        result = db.exec(query).first()
    except Exception as e:
        logger.error(f"set_task_deadline: Query failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to query task: {str(e)}") from e

    # Handle task not found
    if not result:
        logger.warning(
            f"set_task_deadline: Task {params.task_id} not found for user {params.user_id}",
            extra={"user_id": params.user_id, "task_id": params.task_id}
        )
        raise ValueError("Task not found")

    task = result
    old_due_date = task.due_date

    logger.info(
        f"set_task_deadline: Found task - id={task.id}, title={task.title}, "
        f"old_due_date={old_due_date}",
        extra={
            "user_id": params.user_id,
            "task_id": task.id,
            "old_due_date": str(old_due_date) if old_due_date else None
        }
    )

    # Determine action based on old and new deadline
    if params.due_date is None:
        # Remove deadline
        action = "removed"
        task.due_date = None
        logger.info(f"set_task_deadline: Removing deadline from task {task.id}")
    else:
        # Parse due_date string to datetime
        try:
            new_due_date = datetime.fromisoformat(params.due_date)

            if old_due_date is None:
                action = "set"
                logger.info(f"set_task_deadline: Setting new deadline for task {task.id}")
            else:
                action = "updated"
                logger.info(
                    f"set_task_deadline: Updating deadline for task {task.id} "
                    f"from {old_due_date} to {new_due_date}"
                )

            task.due_date = new_due_date
        except (ValueError, TypeError) as e:
            logger.error(
                f"set_task_deadline: Invalid due_date format: {params.due_date}",
                exc_info=True
            )
            raise ValueError(f"Invalid due_date format: {params.due_date}. Use ISO 8601 format.") from e

    # Always update timestamp
    task.updated_at = datetime.utcnow()

    # Persist changes
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(
            f"set_task_deadline: Successfully committed task {task.id} to database",
            extra={
                "user_id": params.user_id,
                "task_id": task.id,
                "action": action,
                "new_due_date": str(task.due_date) if task.due_date else None
            }
        )
    except Exception as e:
        logger.error(
            f"set_task_deadline: Commit failed for task {params.task_id}: {str(e)}",
            extra={"user_id": params.user_id, "task_id": params.task_id},
            exc_info=True
        )
        db.rollback()
        raise RuntimeError(f"Failed to update task deadline: {str(e)}") from e

    # Return result
    return SetTaskDeadlineResult(
        task_id=task.id,
        title=task.title,
        due_date=task.due_date,
        action=action,
        updated_at=task.updated_at
    )
