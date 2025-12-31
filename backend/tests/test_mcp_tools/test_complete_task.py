"""Tests for complete_task MCP tool.

Following TDD - Red phase: These tests should fail until implementation is complete.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.mcp_tools.complete_task import complete_task, CompleteTaskParams, CompleteTaskResult
from src.models import Task


class TestCompleteTaskTool:
    """Tests for complete_task MCP tool."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    def test_complete_task_with_valid_task_id(self, mock_db):
        """Test: complete_task with valid task_id → marks task complete."""
        # Arrange
        user_id = "test-user-123"
        task_id = 5

        # Mock existing incomplete task
        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Buy milk",
            description=None,
            completed=False,
            created_at=datetime(2025, 1, 1, 10, 0, 0)
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_id, task_id=task_id)

        # Act
        result = complete_task(mock_db, params)

        # Assert
        assert isinstance(result, CompleteTaskResult)
        assert result.task_id == task_id
        assert result.title == "Buy milk"
        assert result.completed is True
        assert result.updated_at is not None
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_complete_task_on_already_completed_task(self, mock_db):
        """Test: complete_task on already completed task → idempotent (no error)."""
        # Arrange
        user_id = "test-user-456"
        task_id = 10

        # Mock already completed task
        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Call mom",
            description=None,
            completed=True,
            created_at=datetime(2025, 1, 1, 10, 0, 0)
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_id, task_id=task_id)

        # Act
        result = complete_task(mock_db, params)

        # Assert - Should succeed without error
        assert result.task_id == task_id
        assert result.completed is True
        # Idempotent - no exception raised

    def test_complete_task_with_nonexistent_task_id(self, mock_db):
        """Test: complete_task with non-existent task_id → raises not found error."""
        # Arrange
        user_id = "test-user-789"
        task_id = 9999  # Non-existent

        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_id, task_id=task_id)

        # Act & Assert
        with pytest.raises(ValueError, match="Task not found"):
            complete_task(mock_db, params)

    def test_complete_task_enforces_user_id_isolation(self, mock_db):
        """Test: complete_task enforces user_id isolation (cannot complete others' tasks)."""
        # Arrange
        user_a = "user-A"
        user_b = "user-B"
        task_id = 20

        # Mock returns None when querying with wrong user_id
        # (because query includes both user_id AND task_id filters)
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_a, task_id=task_id)

        # Act & Assert
        # User A tries to complete User B's task → should fail
        with pytest.raises(ValueError, match="Task not found"):
            complete_task(mock_db, params)

    def test_complete_task_updates_timestamp(self, mock_db):
        """Test: complete_task updates updated_at timestamp."""
        # Arrange
        user_id = "test-user-time"
        task_id = 30
        old_time = datetime(2025, 1, 1, 10, 0, 0)

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Task with old timestamp",
            description=None,
            completed=False,
            created_at=old_time
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_id, task_id=task_id)

        # Act
        result = complete_task(mock_db, params)

        # Assert
        assert result.updated_at is not None
        # Updated_at should be recent (not the old time)
        assert result.updated_at > old_time

    def test_complete_task_returns_all_fields(self, mock_db):
        """Test: complete_task returns all required fields."""
        # Arrange
        user_id = "test-user-fields"
        task_id = 40

        mock_task = Task(
            id=task_id,
            user_id=user_id,
            title="Complete task",
            description="With description",
            completed=False,
            created_at=datetime.utcnow()
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_task
        mock_db.exec.return_value = mock_result

        params = CompleteTaskParams(user_id=user_id, task_id=task_id)

        # Act
        result = complete_task(mock_db, params)

        # Assert
        assert result.task_id == task_id
        assert result.title == "Complete task"
        assert result.description == "With description"
        assert result.completed is True
        assert result.updated_at is not None


class TestCompleteTaskParams:
    """Tests for CompleteTaskParams schema."""

    def test_params_creation(self):
        """Test creating CompleteTaskParams."""
        # Act
        params = CompleteTaskParams(user_id="user-123", task_id=5)

        # Assert
        assert params.user_id == "user-123"
        assert params.task_id == 5

    def test_params_requires_task_id(self):
        """Test that task_id is required."""
        # Act & Assert
        with pytest.raises(Exception):  # Pydantic validation error
            CompleteTaskParams(user_id="user-123")


class TestCompleteTaskResult:
    """Tests for CompleteTaskResult schema."""

    def test_result_creation(self):
        """Test creating CompleteTaskResult."""
        # Arrange
        now = datetime.utcnow()

        # Act
        result = CompleteTaskResult(
            task_id=1,
            title="Test task",
            description="Test description",
            completed=True,
            updated_at=now
        )

        # Assert
        assert result.task_id == 1
        assert result.title == "Test task"
        assert result.description == "Test description"
        assert result.completed is True
        assert result.updated_at == now

    def test_result_with_no_description(self):
        """Test creating CompleteTaskResult without description."""
        # Arrange
        now = datetime.utcnow()

        # Act
        result = CompleteTaskResult(
            task_id=2,
            title="Simple task",
            description=None,
            completed=True,
            updated_at=now
        )

        # Assert
        assert result.task_id == 2
        assert result.description is None
