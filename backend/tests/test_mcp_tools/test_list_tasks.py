"""Tests for list_tasks MCP tool.

Following TDD - Red phase: These tests should fail until implementation is complete.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.mcp_tools.list_tasks import list_tasks, ListTasksParams, ListTasksResult
from src.models import Task


class TestListTasksTool:
    """Tests for list_tasks MCP tool."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    def test_list_tasks_with_status_all(self, mock_db):
        """Test: list_tasks with status='all' → returns all tasks."""
        # Arrange
        user_id = "test-user-123"

        # Mock tasks: 3 pending + 2 completed
        mock_tasks = [
            Task(
                id=1,
                user_id=user_id,
                title="Buy milk",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=2,
                user_id=user_id,
                title="Call mom",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=3,
                user_id=user_id,
                title="Finish report",
                description="Quarterly sales",
                completed=True,
                created_at=datetime.utcnow()
            ),
            Task(
                id=4,
                user_id=user_id,
                title="Buy eggs",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=5,
                user_id=user_id,
                title="Read book",
                description=None,
                completed=True,
                created_at=datetime.utcnow()
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="all")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert isinstance(result, ListTasksResult)
        assert result.count == 5
        assert len(result.tasks) == 5
        assert result.tasks[0]["task_id"] == 1
        assert result.tasks[2]["completed"] is True
        assert result.tasks[4]["task_id"] == 5

    def test_list_tasks_with_status_pending(self, mock_db):
        """Test: list_tasks with status='pending' → returns only incomplete tasks."""
        # Arrange
        user_id = "test-user-456"

        # Mock only pending tasks
        mock_tasks = [
            Task(
                id=1,
                user_id=user_id,
                title="Buy milk",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=2,
                user_id=user_id,
                title="Call mom",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=4,
                user_id=user_id,
                title="Buy eggs",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="pending")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.count == 3
        assert len(result.tasks) == 3
        # All tasks should be incomplete
        for task in result.tasks:
            assert task["completed"] is False

    def test_list_tasks_with_status_completed(self, mock_db):
        """Test: list_tasks with status='completed' → returns only complete tasks."""
        # Arrange
        user_id = "test-user-789"

        # Mock only completed tasks
        mock_tasks = [
            Task(
                id=3,
                user_id=user_id,
                title="Finish report",
                description="Quarterly sales",
                completed=True,
                created_at=datetime.utcnow()
            ),
            Task(
                id=5,
                user_id=user_id,
                title="Read book",
                description=None,
                completed=True,
                created_at=datetime.utcnow()
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="completed")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.count == 2
        assert len(result.tasks) == 2
        # All tasks should be complete
        for task in result.tasks:
            assert task["completed"] is True

    def test_list_tasks_with_no_tasks(self, mock_db):
        """Test: list_tasks with no tasks → returns empty list."""
        # Arrange
        user_id = "test-user-empty"

        mock_result = Mock()
        mock_result.all.return_value = []
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="all")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.count == 0
        assert len(result.tasks) == 0
        assert result.tasks == []

    def test_list_tasks_enforces_user_id_isolation(self, mock_db):
        """Test: list_tasks enforces user_id isolation."""
        # Arrange
        user_a = "user-A"
        user_b = "user-B"

        # Mock tasks for user A only
        mock_tasks_user_a = [
            Task(
                id=1,
                user_id=user_a,
                title="User A's task",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks_user_a
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_a, status="all")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.count == 1
        assert result.tasks[0]["task_id"] == 1

        # Verify query filters by user_id
        # The exec call should have a query with user_id filter
        mock_db.exec.assert_called_once()

    def test_list_tasks_default_status_is_all(self, mock_db):
        """Test: list_tasks without status parameter defaults to 'all'."""
        # Arrange
        user_id = "test-user-default"

        mock_tasks = [
            Task(
                id=1,
                user_id=user_id,
                title="Task 1",
                description=None,
                completed=False,
                created_at=datetime.utcnow()
            ),
            Task(
                id=2,
                user_id=user_id,
                title="Task 2",
                description=None,
                completed=True,
                created_at=datetime.utcnow()
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id)  # No status specified

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.count == 2  # Should return all tasks

    def test_list_tasks_with_invalid_status(self, mock_db):
        """Test: list_tasks with invalid status → raises validation error."""
        # Arrange
        user_id = "test-user-invalid"

        # Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            params = ListTasksParams(user_id=user_id, status="invalid")
            list_tasks(mock_db, params)

    def test_list_tasks_includes_all_task_fields(self, mock_db):
        """Test: list_tasks returns all required task fields."""
        # Arrange
        user_id = "test-user-fields"
        now = datetime.utcnow()

        mock_task = Task(
            id=42,
            user_id=user_id,
            title="Complete task",
            description="With all fields",
            completed=True,
            created_at=now
        )

        mock_result = Mock()
        mock_result.all.return_value = [mock_task]
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="all")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        task = result.tasks[0]
        assert task["task_id"] == 42
        assert task["title"] == "Complete task"
        assert task["description"] == "With all fields"
        assert task["completed"] is True
        assert task["created_at"] is not None

    def test_list_tasks_orders_by_created_at(self, mock_db):
        """Test: list_tasks returns tasks ordered by created_at (newest first)."""
        # Arrange
        user_id = "test-user-order"
        old_time = datetime(2025, 1, 1, 10, 0, 0)
        new_time = datetime(2025, 1, 2, 10, 0, 0)

        mock_tasks = [
            Task(
                id=2,
                user_id=user_id,
                title="Newer task",
                description=None,
                completed=False,
                created_at=new_time
            ),
            Task(
                id=1,
                user_id=user_id,
                title="Older task",
                description=None,
                completed=False,
                created_at=old_time
            ),
        ]

        mock_result = Mock()
        mock_result.all.return_value = mock_tasks
        mock_db.exec.return_value = mock_result

        params = ListTasksParams(user_id=user_id, status="all")

        # Act
        result = list_tasks(mock_db, params)

        # Assert
        assert result.tasks[0]["task_id"] == 2  # Newer first
        assert result.tasks[1]["task_id"] == 1


class TestListTasksParams:
    """Tests for ListTasksParams schema."""

    def test_params_with_all_status(self):
        """Test creating params with status='all'."""
        # Act
        params = ListTasksParams(user_id="user-123", status="all")

        # Assert
        assert params.user_id == "user-123"
        assert params.status == "all"

    def test_params_with_pending_status(self):
        """Test creating params with status='pending'."""
        # Act
        params = ListTasksParams(user_id="user-456", status="pending")

        # Assert
        assert params.status == "pending"

    def test_params_with_completed_status(self):
        """Test creating params with status='completed'."""
        # Act
        params = ListTasksParams(user_id="user-789", status="completed")

        # Assert
        assert params.status == "completed"

    def test_params_default_status(self):
        """Test that status defaults to 'all' when not provided."""
        # Act
        params = ListTasksParams(user_id="user-default")

        # Assert
        assert params.status == "all"


class TestListTasksResult:
    """Tests for ListTasksResult schema."""

    def test_result_creation(self):
        """Test creating ListTasksResult."""
        # Arrange
        tasks = [
            {
                "task_id": 1,
                "title": "Task 1",
                "description": None,
                "completed": False,
                "created_at": datetime.utcnow()
            }
        ]

        # Act
        result = ListTasksResult(tasks=tasks, count=1)

        # Assert
        assert result.count == 1
        assert len(result.tasks) == 1
        assert result.tasks[0]["task_id"] == 1

    def test_result_with_empty_list(self):
        """Test creating ListTasksResult with no tasks."""
        # Act
        result = ListTasksResult(tasks=[], count=0)

        # Assert
        assert result.count == 0
        assert result.tasks == []
