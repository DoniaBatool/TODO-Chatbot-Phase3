"""Tests for add_task MCP tool.

Following TDD - Red phase: These tests should fail until implementation is complete.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.mcp_tools.add_task import add_task, AddTaskParams, AddTaskResult
from src.models import Task


class TestAddTaskTool:
    """Tests for add_task MCP tool."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    def test_add_task_with_valid_params(self, mock_db):
        """Test: add_task with valid params → creates task with correct fields."""
        # Arrange
        user_id = "test-user-123"
        title = "Buy milk"
        description = None

        mock_task = Task(
            id=1,
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow()
        )
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 1))

        params = AddTaskParams(user_id=user_id, title=title, description=description)

        # Act
        result = add_task(mock_db, params)

        # Assert
        assert isinstance(result, AddTaskResult)
        assert result.task_id == 1
        assert result.title == title
        assert result.description is None
        assert result.completed is False
        assert result.created_at is not None
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_add_task_with_description(self, mock_db):
        """Test: add_task with description → stores description."""
        # Arrange
        user_id = "test-user-456"
        title = "Finish report"
        description = "Quarterly sales report for Q4"

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 2))

        params = AddTaskParams(
            user_id=user_id,
            title=title,
            description=description
        )

        # Act
        result = add_task(mock_db, params)

        # Assert
        assert result.task_id == 2
        assert result.title == title
        assert result.description == description
        assert result.completed is False

    def test_add_task_with_empty_title(self, mock_db):
        """Test: add_task with empty title → raises validation error."""
        # Arrange
        user_id = "test-user-789"
        title = ""
        description = None

        params = AddTaskParams(user_id=user_id, title=title, description=description)

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            add_task(mock_db, params)

    def test_add_task_with_whitespace_only_title(self, mock_db):
        """Test: add_task with whitespace-only title → raises validation error."""
        # Arrange
        user_id = "test-user-789"
        title = "   "
        description = None

        params = AddTaskParams(user_id=user_id, title=title, description=description)

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            add_task(mock_db, params)

    def test_add_task_with_title_exceeding_max_length(self, mock_db):
        """Test: add_task with title > 200 chars → raises validation error."""
        # Arrange
        user_id = "test-user-999"
        title = "A" * 201  # 201 characters
        description = None

        params = AddTaskParams(user_id=user_id, title=title, description=description)

        # Act & Assert
        with pytest.raises(ValueError, match="Title must be 200 characters or less"):
            add_task(mock_db, params)

    def test_add_task_enforces_user_id_isolation(self, mock_db):
        """Test: add_task enforces user_id isolation."""
        # Arrange
        user_id = "user-A"
        title = "User A's task"

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 10))

        params = AddTaskParams(user_id=user_id, title=title, description=None)

        # Act
        result = add_task(mock_db, params)

        # Assert - Verify the task is created with correct user_id
        assert result.task_id == 10
        # The created task should have been passed to mock_db.add
        # We verify that the task object added has the correct user_id
        call_args = mock_db.add.call_args
        added_task = call_args[0][0]
        assert added_task.user_id == user_id

    def test_add_task_title_at_max_length(self, mock_db):
        """Test: add_task with title exactly 200 chars → succeeds."""
        # Arrange
        user_id = "test-user-max"
        title = "A" * 200  # Exactly 200 characters
        description = None

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 20))

        params = AddTaskParams(user_id=user_id, title=title, description=description)

        # Act
        result = add_task(mock_db, params)

        # Assert
        assert result.task_id == 20
        assert len(result.title) == 200

    def test_add_task_with_long_description(self, mock_db):
        """Test: add_task with long description → stores full description."""
        # Arrange
        user_id = "test-user-desc"
        title = "Complex task"
        description = "This is a very long description. " * 50  # ~1500 chars

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 30))

        params = AddTaskParams(
            user_id=user_id,
            title=title,
            description=description
        )

        # Act
        result = add_task(mock_db, params)

        # Assert
        assert result.task_id == 30
        assert result.description == description
        assert len(result.description) > 1000

    def test_add_task_returns_created_timestamp(self, mock_db):
        """Test: add_task returns created_at timestamp."""
        # Arrange
        user_id = "test-user-time"
        title = "Time test task"

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 40))

        params = AddTaskParams(user_id=user_id, title=title, description=None)

        # Act
        result = add_task(mock_db, params)

        # Assert
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)


class TestAddTaskParams:
    """Tests for AddTaskParams schema."""

    def test_params_with_all_fields(self):
        """Test creating params with all fields."""
        # Act
        params = AddTaskParams(
            user_id="user-123",
            title="Test task",
            description="Test description"
        )

        # Assert
        assert params.user_id == "user-123"
        assert params.title == "Test task"
        assert params.description == "Test description"

    def test_params_with_optional_description(self):
        """Test creating params without description."""
        # Act
        params = AddTaskParams(
            user_id="user-456",
            title="Test task"
        )

        # Assert
        assert params.user_id == "user-456"
        assert params.title == "Test task"
        assert params.description is None


class TestAddTaskResult:
    """Tests for AddTaskResult schema."""

    def test_result_creation(self):
        """Test creating AddTaskResult."""
        # Arrange
        now = datetime.utcnow()

        # Act
        result = AddTaskResult(
            task_id=1,
            title="Test task",
            description="Test description",
            completed=False,
            created_at=now
        )

        # Assert
        assert result.task_id == 1
        assert result.title == "Test task"
        assert result.description == "Test description"
        assert result.completed is False
        assert result.created_at == now

    def test_result_with_no_description(self):
        """Test creating AddTaskResult without description."""
        # Arrange
        now = datetime.utcnow()

        # Act
        result = AddTaskResult(
            task_id=2,
            title="Simple task",
            description=None,
            completed=False,
            created_at=now
        )

        # Assert
        assert result.task_id == 2
        assert result.description is None
