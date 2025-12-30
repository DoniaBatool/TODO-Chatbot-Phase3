"""
Unit Tests for Task Manager

Tests the TaskManager class and CRUD operations.
"""

import pytest
from todo.manager import TaskManager
from todo.task import Task


class TestTaskManagerAddTask:
    """Test adding tasks."""
    
    def test_add_task_with_title_only(self):
        """Test adding a task with title only."""
        manager = TaskManager()
        task = manager.add_task("Buy groceries")
        
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert len(manager.get_all_tasks()) == 1
    
    def test_add_task_with_description(self):
        """Test adding a task with title and description."""
        manager = TaskManager()
        task = manager.add_task("Meeting", "Discuss project")
        
        assert task.title == "Meeting"
        assert task.description == "Discuss project"
    
    def test_multiple_tasks_increment_id(self):
        """Test that IDs increment for multiple tasks."""
        manager = TaskManager()
        
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
    
    def test_add_task_with_empty_title_raises_error(self):
        """Test that adding task with empty title raises ValueError."""
        manager = TaskManager()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add_task("")
    
    def test_add_task_with_long_title_raises_error(self):
        """Test that adding task with >200 char title raises ValueError."""
        manager = TaskManager()
        long_title = "x" * 201
        with pytest.raises(ValueError, match="Title too long"):
            manager.add_task(long_title)


class TestTaskManagerGetTasks:
    """Test retrieving tasks."""
    
    def test_get_all_tasks_empty(self):
        """Test getting tasks from empty manager."""
        manager = TaskManager()
        assert manager.get_all_tasks() == []
    
    def test_get_all_tasks(self):
        """Test getting all tasks."""
        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        
        tasks = manager.get_all_tasks()
        assert len(tasks) == 2
    
    def test_get_task_by_id_found(self):
        """Test getting task by valid ID."""
        manager = TaskManager()
        task = manager.add_task("Task 1")
        
        found_task = manager.get_task_by_id(task.id)
        assert found_task is not None
        assert found_task.id == task.id
        assert found_task.title == "Task 1"
    
    def test_get_task_by_id_not_found(self):
        """Test getting task by invalid ID returns None."""
        manager = TaskManager()
        manager.add_task("Task 1")
        
        found_task = manager.get_task_by_id(999)
        assert found_task is None
    
    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task2.completed = True
        manager.add_task("Task 3")
        
        pending = manager.get_pending_tasks()
        assert len(pending) == 2
        assert all(not task.completed for task in pending)
    
    def test_get_completed_tasks(self):
        """Test getting completed tasks."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        task1.completed = True
        manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")
        task3.completed = True
        
        completed = manager.get_completed_tasks()
        assert len(completed) == 2
        assert all(task.completed for task in completed)


class TestTaskManagerUpdateTask:
    """Test updating tasks."""
    
    def test_update_task_title(self):
        """Test updating task title."""
        manager = TaskManager()
        task = manager.add_task("Old Title")
        
        updated = manager.update_task(task.id, title="New Title")
        
        assert updated is not None
        assert updated.title == "New Title"
    
    def test_update_task_description(self):
        """Test updating task description."""
        manager = TaskManager()
        task = manager.add_task("Task")
        
        updated = manager.update_task(task.id, description="New description")
        
        assert updated is not None
        assert updated.description == "New description"
    
    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        manager = TaskManager()
        task = manager.add_task("Old", "Old desc")
        
        updated = manager.update_task(
            task.id,
            title="New",
            description="New desc"
        )
        
        assert updated.title == "New"
        assert updated.description == "New desc"
    
    def test_update_nonexistent_task(self):
        """Test updating non-existent task returns None."""
        manager = TaskManager()
        updated = manager.update_task(999, title="New")
        assert updated is None
    
    def test_update_with_invalid_title_raises_error(self):
        """Test updating with empty title raises ValueError."""
        manager = TaskManager()
        task = manager.add_task("Task")
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.update_task(task.id, title="")


class TestTaskManagerDeleteTask:
    """Test deleting tasks."""
    
    def test_delete_existing_task(self):
        """Test deleting an existing task."""
        manager = TaskManager()
        task = manager.add_task("Task to delete")
        
        result = manager.delete_task(task.id)
        
        assert result is True
        assert len(manager.get_all_tasks()) == 0
        assert manager.get_task_by_id(task.id) is None
    
    def test_delete_nonexistent_task(self):
        """Test deleting non-existent task returns False."""
        manager = TaskManager()
        result = manager.delete_task(999)
        assert result is False
    
    def test_delete_task_ids_not_reused(self):
        """Test that IDs are not reused after deletion."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        manager.delete_task(task1.id)
        task2 = manager.add_task("Task 2")
        
        assert task2.id == 2  # ID not reused


class TestTaskManagerMarkComplete:
    """Test marking tasks complete/incomplete."""
    
    def test_mark_task_complete(self):
        """Test marking task as complete."""
        manager = TaskManager()
        task = manager.add_task("Task")
        
        updated = manager.mark_complete(task.id, True)
        
        assert updated is not None
        assert updated.completed is True
    
    def test_mark_task_incomplete(self):
        """Test marking task as incomplete."""
        manager = TaskManager()
        task = manager.add_task("Task")
        task.completed = True
        
        updated = manager.mark_complete(task.id, False)
        
        assert updated is not None
        assert updated.completed is False
    
    def test_mark_nonexistent_task_complete(self):
        """Test marking non-existent task returns None."""
        manager = TaskManager()
        result = manager.mark_complete(999)
        assert result is None

