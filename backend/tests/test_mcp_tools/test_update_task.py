"""Tests for update_task MCP tool.

Following TDD - Red phase: These tests should fail until implementation is complete.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from src.mcp_tools.update_task import update_task, UpdateTaskParams, UpdateTaskResult
from src.models import Task


class TestUpdateTaskTool:
    """Tests for update_task MCP tool."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    def test_update_task_with_title_only(self, mock_db):
        """Test: update_task with title → updates title only."""
        # Arrange
        user_id = "test-user-123"
        task_id = 3

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Buy milk",
            description="Original description",
            completed=False,
            created_at=datetime.utcnow()
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Buy milk and eggs"
        )

        # Act
        result = update_task(mock_db, params)

        # Assert
        assert result.task_id == task_id
        assert result.title == "Buy milk and eggs"
        assert result.description == "Original description"  # Unchanged

    def test_update_task_with_description_only(self, mock_db):
        """Test: update_task with description → updates description only."""
        # Arrange
        user_id = "test-user-456"
        task_id = 5

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Original title",
            description="Old description",
            completed=False,
            created_at=datetime.utcnow()
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            description="New description with details"
        )

        # Act
        result = update_task(mock_db, params)

        # Assert
        assert result.task_id == task_id
        assert result.title == "Original title"  # Unchanged
        assert result.description == "New description with details"

    def test_update_task_with_both_fields(self, mock_db):
        """Test: update_task with both → updates both fields."""
        # Arrange
        user_id = "test-user-789"
        task_id = 7

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Old title",
            description="Old description",
            completed=False,
            created_at=datetime.utcnow()
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="New title",
            description="New description"
        )

        # Act
        result = update_task(mock_db, params)

        # Assert
        assert result.title == "New title"
        assert result.description == "New description"

    def test_update_task_with_neither_field(self, mock_db):
        """Test: update_task with neither title nor description → validation error."""
        # Arrange
        user_id = "test-user-invalid"
        task_id = 10

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id
        )

        # Act & Assert
        with pytest.raises(ValueError, match="At least one field"):
            update_task(mock_db, params)

    def test_update_task_enforces_user_isolation(self, mock_db):
        """Test: update_task enforces user_id isolation."""
        # Arrange
        user_a = "user-A"
        task_id = 20

        # Mock returns None (task not found for user_a)
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_a,
            task_id=task_id,
            title="Hacked title"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)

    def test_update_task_nonexistent(self, mock_db):
        """Test: update_task on non-existent task → raises error."""
        # Arrange
        user_id = "test-user-404"
        task_id = 9999

        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="New title"
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)

    def test_update_task_updates_timestamp(self, mock_db):
        """Test: update_task updates updated_at timestamp."""
        # Arrange
        user_id = "test-user-time"
        task_id = 30
        old_time = datetime(2025, 1, 1, 10, 0, 0)

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Task",
            description=None,
            completed=False,
            created_at=old_time
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Updated task"
        )

        # Act
        result = update_task(mock_db, params)

        # Assert
        assert result.updated_at > old_time


class TestUpdateTaskParams:
    """Tests for UpdateTaskParams schema."""

    def test_params_with_title_only(self):
        """Test creating params with title only."""
        # Act
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=5,
            title="New title"
        )

        # Assert
        assert params.title == "New title"
        assert params.description is None

    def test_params_with_description_only(self):
        """Test creating params with description only."""
        # Act
        params = UpdateTaskParams(
            user_id="user-456",
            task_id=7,
            description="New description"
        )

        # Assert
        assert params.title is None
        assert params.description == "New description"


class TestUpdateTaskResult:
    """Tests for UpdateTaskResult schema."""

    def test_result_creation(self):
        """Test creating UpdateTaskResult."""
        # Arrange
        now = datetime.utcnow()

        # Act
        result = UpdateTaskResult(
            task_id=1,
            title="Updated task",
            description="Updated description",
            completed=False,
            updated_at=now
        )

        # Assert
        assert result.task_id == 1
        assert result.title == "Updated task"
        assert result.updated_at == now
