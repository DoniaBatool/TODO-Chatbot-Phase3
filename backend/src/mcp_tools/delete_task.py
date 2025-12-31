"""MCP Tool: delete_task

Deletes a task for the authenticated user.

This tool enables AI agents to remove tasks based on
natural language input.
"""

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..models import Task


class DeleteTaskParams(BaseModel):
    """Input parameters for delete_task tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        task_id: ID of the task to delete
    """

    user_id: str = Field(..., description="User ID for task ownership")
    task_id: int = Field(..., description="ID of the task to delete")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "task_id": 7
            }
        }


class DeleteTaskResult(BaseModel):
    """Result from delete_task tool execution.

    Attributes:
        task_id: ID of the deleted task
        title: Title of the deleted task (for confirmation)
        success: Whether deletion was successful
    """

    task_id: int = Field(..., description="ID of the deleted task")
    title: str = Field(..., description="Title of the deleted task")
    success: bool = Field(True, description="Deletion success status")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "task_id": 7,
                "title": "Buy milk",
                "success": True
            }
        }


def delete_task(db: Session, params: DeleteTaskParams) -> DeleteTaskResult:
    """Delete a task.

    This is the core MCP tool function that AI agents call to delete tasks.

    Args:
        db: Database session
        params: Task deletion parameters

    Returns:
        DeleteTaskResult with deleted task details

    Raises:
        ValueError: If task not found or doesn't belong to user

    Security:
        - Enforces user isolation: query filters by both user_id AND task_id
        - Returns generic "not found" error (doesn't reveal if task exists for other user)

    Example:
        >>> params = DeleteTaskParams(
        ...     user_id="user-123",
        ...     task_id=7
        ... )
        >>> result = delete_task(db, params)
        >>> assert result.success is True
    """
    # Query task with user_id AND task_id
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

    # Store title for confirmation message
    task_title = task.title
    task_id = task.id

    # Delete task
    try:
        db.delete(task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to delete task: {str(e)}") from e

    # Return result
    return DeleteTaskResult(
        task_id=task_id,
        title=task_title,
        success=True
    )
