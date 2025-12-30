"""Task CRUD API endpoints (protected by JWT and ownership checks)."""

from datetime import datetime
from typing import List, Optional

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user
from src.db import get_session
from src.models import Task
from src.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(tags=["Tasks"])
logger = logging.getLogger(__name__)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    Create a new task.
    
    Args:
        task_data: Task creation data
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Returns:
        TaskResponse: Created task with generated ID and timestamps
    
    Raises:
        HTTPException: 400 if validation fails, 500 if database error
    """
    try:
        # Always use authenticated user's ID (ignore any client-supplied user_id)
        task = Task(
            user_id=current_user_id,
            title=task_data.title,
            description=task_data.description,
        )
        
        # Add to database
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        ) from e


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    List all tasks for the authenticated user with optional filtering by completion status.
    
    Args:
        completed: Optional filter for task completion status
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Returns:
        List[TaskResponse]: List of tasks matching filter for the authenticated user
    """
    try:
        # Build query scoped to authenticated user
        statement = select(Task).where(Task.user_id == current_user_id)
        
        # Apply completion filter if provided
        if completed is not None:
            statement = statement.where(Task.completed == completed)
        
        # Execute query
        tasks = session.exec(statement).all()
        
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tasks: {str(e)}"
        ) from e


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    Get a specific task by ID (only if owned by authenticated user).
    
    Args:
        task_id: Task ID to retrieve
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Returns:
        TaskResponse: Task data
    
    Raises:
        HTTPException: 404 if task not found or not owned by user, 403 if owned by different user
    """
    task = session.get(Task, task_id)
    
    if not task:
        logger.warning("Task not found for user=%s id=%s", current_user_id, task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task.user_id != current_user_id:
        logger.warning(
            "Forbidden task access: user=%s attempted task_id=%s owned_by=%s",
            current_user_id,
            task_id,
            task.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Task does not belong to the authenticated user"
        )
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    Update an existing task (only if owned by authenticated user).
    
    Args:
        task_id: Task ID to update
        task_data: Updated task data
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Returns:
        TaskResponse: Updated task
    
    Raises:
        HTTPException: 404 if task not found, 403 if not owned by user, 400 if validation fails
    """
    task = session.get(Task, task_id)
    
    if not task:
        logger.warning("Task not found for user=%s id=%s", current_user_id, task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task.user_id != current_user_id:
        logger.warning(
            "Forbidden task update: user=%s attempted task_id=%s owned_by=%s",
            current_user_id,
            task_id,
            task.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Task does not belong to the authenticated user"
        )
    
    try:
        # Update fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        
        # Update timestamp
        task.updated_at = datetime.utcnow()
        
        # Save changes
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update task: {str(e)}"
        ) from e


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    Toggle task completion status (only if owned by authenticated user).
    
    Args:
        task_id: Task ID to toggle
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Returns:
        TaskResponse: Updated task
    
    Raises:
        HTTPException: 404 if task not found, 403 if not owned by user
    """
    task = session.get(Task, task_id)
    
    if not task:
        logger.warning("Task not found for user=%s id=%s", current_user_id, task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task.user_id != current_user_id:
        logger.warning(
            "Forbidden task toggle: user=%s attempted task_id=%s owned_by=%s",
            current_user_id,
            task_id,
            task.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Task does not belong to the authenticated user"
        )
    
    try:
        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        
        # Save changes
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to toggle task completion: {str(e)}"
        ) from e


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
):
    """
    Delete a task (only if owned by authenticated user).
    
    Args:
        task_id: Task ID to delete
        current_user_id: Authenticated user ID from JWT
        session: Database session
    
    Raises:
        HTTPException: 404 if task not found, 403 if not owned by user
    """
    task = session.get(Task, task_id)
    
    if not task:
        logger.warning("Task not found for user=%s id=%s", current_user_id, task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if task.user_id != current_user_id:
        logger.warning(
            "Forbidden task delete: user=%s attempted task_id=%s owned_by=%s",
            current_user_id,
            task_id,
            task.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Task does not belong to the authenticated user"
        )
    
    try:
        session.delete(task)
        session.commit()
        return None  # 204 No Content
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete task: {str(e)}"
        ) from e

