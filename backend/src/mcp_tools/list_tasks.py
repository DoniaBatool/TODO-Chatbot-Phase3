"""MCP Tool: list_tasks

Lists tasks for the authenticated user with optional status filtering.

This tool enables AI agents to retrieve and display user tasks based on
natural language queries.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from sqlmodel import Session, select, col

from ..models import Task


class ListTasksParams(BaseModel):
    """Input parameters for list_tasks tool.

    Attributes:
        user_id: ID of the authenticated user (for isolation)
        status: Filter by completion status ('all', 'pending', 'completed')
    """

    user_id: str = Field(..., description="User ID for task ownership")
    status: str = Field(
        "all",
        description="Filter by status: 'all', 'pending', or 'completed'"
    )

    @validator('status')
    def validate_status(cls, v):
        """Validate status is one of allowed values."""
        allowed = ["all", "pending", "completed"]
        if v not in allowed:
            raise ValueError(
                f"Status must be one of {allowed}, got '{v}'"
            )
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "status": "pending"
            }
        }


class ListTasksResult(BaseModel):
    """Result from list_tasks tool execution.

    Attributes:
        tasks: List of task dictionaries with all fields
        count: Total number of tasks returned
    """

    tasks: List[Dict[str, Any]] = Field(
        ...,
        description="List of tasks matching the filter"
    )
    count: int = Field(..., description="Total number of tasks")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "task_id": 1,
                        "title": "Buy milk",
                        "description": None,
                        "completed": False,
                        "created_at": "2025-12-30T10:30:00Z"
                    },
                    {
                        "task_id": 2,
                        "title": "Call mom",
                        "description": "Wish her happy birthday",
                        "completed": False,
                        "created_at": "2025-12-30T11:00:00Z"
                    }
                ],
                "count": 2
            }
        }


def list_tasks(db: Session, params: ListTasksParams) -> ListTasksResult:
    """List tasks for the user with optional status filtering.

    This is the core MCP tool function that AI agents call to retrieve tasks.

    Args:
        db: Database session
        params: List parameters with user_id and status filter

    Returns:
        ListTasksResult with tasks array and count

    Raises:
        ValueError: If status validation fails

    Example:
        >>> params = ListTasksParams(
        ...     user_id="user-123",
        ...     status="pending"
        ... )
        >>> result = list_tasks(db, params)
        >>> assert result.count >= 0
        >>> assert all(not t["completed"] for t in result.tasks)
    """
    # Build base query with user isolation (T082)
    query = select(Task).where(Task.user_id == params.user_id)

    # Apply status filter if not "all" (T083)
    if params.status == "pending":
        query = query.where(Task.completed == False)
    elif params.status == "completed":
        query = query.where(Task.completed == True)
    # For "all", no additional filter needed

    # Order by created_at descending (newest first)
    query = query.order_by(col(Task.created_at).desc())

    # Execute query
    try:
        results = db.exec(query).all()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch tasks: {str(e)}") from e

    # Convert tasks to dict format (T084)
    tasks = [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at
        }
        for task in results
    ]

    # Return result with count (T084)
    return ListTasksResult(
        tasks=tasks,
        count=len(tasks)
    )
