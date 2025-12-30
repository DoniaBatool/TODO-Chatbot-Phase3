"""
Unit Tests for Task Model

Tests the Task class and validation logic.
"""

import pytest
from datetime import datetime
from todo.task import Task


class TestTaskCreation:
    """Test task creation and validation."""
    
    def test_create_task_with_valid_data(self):
        """Test creating a task with valid title."""
        task = Task(id=1, title="Buy groceries")
        
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
    
    def test_create_task_with_description(self):
        """Test creating a task with title and description."""
        task = Task(
            id=1,
            title="Meeting",
            description="Discuss project updates"
        )
        
        assert task.title == "Meeting"
        assert task.description == "Discuss project updates"
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="")
    
    def test_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="   ")
    
    def test_title_too_long_raises_error(self):
        """Test that title > 200 chars raises ValueError."""
        long_title = "x" * 201
        with pytest.raises(ValueError, match="Title too long"):
            Task(id=1, title=long_title)
    
    def test_description_too_long_raises_error(self):
        """Test that description > 1000 chars raises ValueError."""
        long_desc = "x" * 1001
        with pytest.raises(ValueError, match="Description too long"):
            Task(id=1, title="Valid", description=long_desc)
    
    def test_title_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed from title."""
        task = Task(id=1, title="  Buy milk  ")
        assert task.title == "Buy milk"
    
    def test_description_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed from description."""
        task = Task(id=1, title="Task", description="  Description  ")
        assert task.description == "Description"
    
    def test_max_valid_title_length(self):
        """Test that 200 char title is accepted."""
        max_title = "x" * 200
        task = Task(id=1, title=max_title)
        assert len(task.title) == 200
    
    def test_max_valid_description_length(self):
        """Test that 1000 char description is accepted."""
        max_desc = "x" * 1000
        task = Task(id=1, title="Valid", description=max_desc)
        assert len(task.description) == 1000


class TestTaskMethods:
    """Test task methods."""
    
    def test_str_representation_pending(self):
        """Test string representation of pending task."""
        task = Task(id=1, title="Buy groceries")
        assert str(task) == "[○] 1. Buy groceries"
    
    def test_str_representation_completed(self):
        """Test string representation of completed task."""
        task = Task(id=1, title="Buy groceries", completed=True)
        assert str(task) == "[✓] 1. Buy groceries"
    
    def test_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(id=1, title="Task", description="Desc")
        task_dict = task.to_dict()
        
        assert task_dict["id"] == 1
        assert task_dict["title"] == "Task"
        assert task_dict["description"] == "Desc"
        assert task_dict["completed"] is False
        assert "created_at" in task_dict

