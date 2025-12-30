"""
Task Manager Module

Handles CRUD operations for tasks.
"""

from typing import List, Optional
from .task import Task


class TaskManager:
    """
    Manages todo tasks with in-memory storage.
    
    Provides CRUD operations: Create, Read, Update, Delete tasks.
    """
    
    def __init__(self) -> None:
        """Initialize task manager with empty task list."""
        self.tasks: List[Task] = []
        self.next_id: int = 1
    
    def add_task(self, title: str, description: str = "") -> Task:
        """
        Create and add a new task to the list.
        
        Args:
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)
            
        Returns:
            The newly created task object
            
        Raises:
            ValueError: If title or description validation fails
        """
        task = Task(
            id=self.next_id,
            title=title,
            description=description
        )
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return self.tasks.copy()
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find a task by its ID.
        
        Args:
            task_id: The task ID to search for
            
        Returns:
            The task if found, None otherwise
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(
        self, 
        task_id: int, 
        title: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update a task's title and/or description.
        
        Args:
            task_id: The task ID to update
            title: New title (optional)
            description: New description (optional)
            
        Returns:
            The updated task if found, None otherwise
            
        Raises:
            ValueError: If validation fails for title or description
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        
        # Update fields if provided
        if title is not None:
            if not title or len(title.strip()) == 0:
                raise ValueError("Title cannot be empty")
            if len(title) > 200:
                raise ValueError("Title too long (max 200 characters)")
            task.title = title.strip()
        
        if description is not None:
            if len(description) > 1000:
                raise ValueError("Description too long (max 1000 characters)")
            task.description = description.strip()
        
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: The task ID to delete
            
        Returns:
            True if task was deleted, False if not found
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False
        
        self.tasks.remove(task)
        return True
    
    def mark_complete(self, task_id: int, completed: bool = True) -> Optional[Task]:
        """
        Mark a task as complete or incomplete.
        
        Args:
            task_id: The task ID to update
            completed: Completion status (default: True)
            
        Returns:
            The updated task if found, None otherwise
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        
        task.completed = completed
        return task
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending (incomplete) tasks."""
        return [task for task in self.tasks if not task.completed]
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return [task for task in self.tasks if task.completed]

