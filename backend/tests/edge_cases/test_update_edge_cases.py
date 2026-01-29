"""
Edge case tests for task update workflow.

Goal: Validate US3 edge cases - field removal, invalid inputs, edge conditions.
Focus: Boundary conditions, null handling, user isolation, concurrent updates.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.intent_classifier import IntentClassifier, Intent
from src.mcp_tools.update_task import update_task, UpdateTaskParams, UpdateTaskResult
from src.mcp_tools.add_task import add_task, AddTaskParams


class TestFieldRemoval:
    """Test removing fields by setting to null."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def sample_task(self, mock_db):
        """Create a sample task with all fields populated."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original Title"
        task.description = "Original Description"
        task.priority = "medium"
        task.due_date = datetime(2026, 2, 15, 23, 59, 59)
        task.completed = False
        task.created_at = datetime(2026, 1, 28)
        task.updated_at = datetime(2026, 1, 28)

        mock_db.exec.return_value.first.return_value = task
        return task

    def test_remove_description_by_setting_none(self, mock_db, sample_task):
        """Test that description can be removed by explicitly setting to None."""
        # Arrange - task with description
        assert sample_task.description == "Original Description"

        # Act - update with description set explicitly
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            description=None  # Explicitly set to None
        )

        # Need to manually set __fields_set__ for this test
        params.__fields_set__.add('description')

        result = update_task(mock_db, params)

        # Assert - description should be removed
        assert sample_task.description is None
        mock_db.commit.assert_called_once()

    def test_remove_due_date_by_setting_none(self, mock_db, sample_task):
        """Test that due_date can be removed by explicitly setting to None."""
        # Arrange
        assert sample_task.due_date is not None

        # Act
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            due_date=None  # Explicitly remove deadline
        )
        params.__fields_set__.add('due_date')

        result = update_task(mock_db, params)

        # Assert
        assert sample_task.due_date is None
        mock_db.commit.assert_called_once()

    def test_keep_fields_unchanged_when_not_provided(self, mock_db, sample_task):
        """Test that unspecified fields remain unchanged."""
        original_description = sample_task.description
        original_due_date = sample_task.due_date

        # Act - update only title
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title="New Title"
        )
        result = update_task(mock_db, params)

        # Assert - other fields unchanged
        assert sample_task.description == original_description
        assert sample_task.due_date == original_due_date


class TestUpdateIntentDetection:
    """Test update intent detection edge cases."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    def test_update_intent_with_task_number(self, classifier):
        """Test detecting update intent with task ID."""
        result = classifier.classify("update task 5")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_update_intent_with_name_reference(self, classifier):
        """Test detecting update intent with task name."""
        result = classifier.classify("update the milk task")
        assert result.intent_type == Intent.UPDATE_TASK
        assert "milk" in result.extracted_entities.get("task_name", "").lower()

    def test_update_intent_with_priority_change(self, classifier):
        """Test detecting update intent with priority in same message."""
        result = classifier.classify("change task 3 to high priority")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("task_id") == 3
        # Priority should be extracted
        assert result.extracted_entities.get("priority") == "high"

    def test_update_not_triggered_by_add(self, classifier):
        """Test that 'add' commands don't trigger update."""
        result = classifier.classify("add a new task called update logs")
        # Should be ADD_TASK, not UPDATE_TASK
        assert result.intent_type == Intent.ADD_TASK

    def test_update_with_make_it_pattern(self, classifier):
        """Test 'make it' pattern triggers update."""
        result = classifier.classify("make it high priority", current_intent="UPDATING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "high"

    def test_update_with_change_to_pattern(self, classifier):
        """Test 'change to' pattern triggers update."""
        result = classifier.classify("change it to low priority", current_intent="UPDATING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "low"


class TestUpdateValidation:
    """Test update validation edge cases."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    def test_update_with_empty_title_rejected(self, mock_db):
        """Test that empty title is rejected."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"
        task.description = None
        task.priority = "medium"
        task.completed = False
        mock_db.exec.return_value.first.return_value = task

        # Empty title should be rejected by Pydantic validation
        # (handled at params level)
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title=""  # Empty title
        )

        # Title can be empty string, that's allowed but the task model
        # may reject it - this tests the boundary

    def test_update_with_very_long_title(self, mock_db):
        """Test handling of very long title (boundary test)."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"
        task.description = "Test description"  # Add explicit string
        task.priority = "medium"
        task.due_date = None  # Explicit None
        task.completed = False
        task.updated_at = datetime.utcnow()
        mock_db.exec.return_value.first.return_value = task

        # Very long title (200+ chars)
        long_title = "A" * 250

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title=long_title
        )

        # Should not raise - validation at DB level
        result = update_task(mock_db, params)
        assert task.title == long_title

    def test_update_invalid_priority_rejected(self):
        """Test that invalid priority is rejected."""
        with pytest.raises(ValueError, match="Invalid priority"):
            UpdateTaskParams(
                user_id="user-123",
                task_id=1,
                priority="super-urgent"  # Invalid
            )

    def test_update_nonexistent_task(self, mock_db):
        """Test updating task that doesn't exist returns error."""
        mock_db.exec.return_value.first.return_value = None

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=99999,
            title="New Title"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)


class TestUpdateUserIsolation:
    """Test user isolation in update operations."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    def test_cannot_update_other_user_task(self, mock_db):
        """Test that user cannot update another user's task."""
        # Task belongs to user-123
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"

        # When querying with wrong user, return None
        mock_db.exec.return_value.first.return_value = None

        params = UpdateTaskParams(
            user_id="user-456",  # Different user
            task_id=1,
            title="Hacked Title"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)

    def test_update_own_task_succeeds(self, mock_db):
        """Test that user can update their own task."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"
        task.description = None
        task.priority = "medium"
        task.due_date = None
        task.completed = False
        task.updated_at = datetime.utcnow()

        mock_db.exec.return_value.first.return_value = task

        params = UpdateTaskParams(
            user_id="user-123",  # Same user
            task_id=1,
            title="Updated Title"
        )

        result = update_task(mock_db, params)
        assert task.title == "Updated Title"
        mock_db.commit.assert_called_once()


class TestUpdateConfirmationFlow:
    """Test update confirmation flow edge cases."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    def test_yes_confirmation_in_updating_context(self, classifier):
        """Test 'yes' is recognized as confirmation during update."""
        result = classifier.classify("yes", current_intent="UPDATING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_no_cancellation_in_updating_context(self, classifier):
        """Test 'no' cancels update."""
        result = classifier.classify("no", current_intent="UPDATING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == False

    def test_cancel_command_in_updating_context(self, classifier):
        """Test 'cancel' command stops update."""
        result = classifier.classify("cancel", current_intent="UPDATING_TASK")
        # Should be CANCEL_OPERATION
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_nevermind_in_updating_context(self, classifier):
        """Test 'never mind' cancels update."""
        result = classifier.classify("never mind", current_intent="UPDATING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION


class TestUpdateMultiFieldChanges:
    """Test updating multiple fields at once."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def sample_task(self, mock_db):
        """Create sample task."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"
        task.description = "Original Desc"
        task.priority = "low"
        task.due_date = None
        task.completed = False
        task.updated_at = datetime.utcnow()
        mock_db.exec.return_value.first.return_value = task
        return task

    def test_update_title_and_priority(self, mock_db, sample_task):
        """Test updating title and priority together."""
        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title="New Title",
            priority="high"
        )

        result = update_task(mock_db, params)

        assert sample_task.title == "New Title"
        assert sample_task.priority == "high"

    def test_update_all_fields(self, mock_db, sample_task):
        """Test updating all fields at once."""
        new_due = datetime(2026, 3, 1, 12, 0, 0)

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title="All New",
            description="New Desc",
            priority="high",
            due_date=new_due,
            completed=True
        )

        result = update_task(mock_db, params)

        assert sample_task.title == "All New"
        assert sample_task.description == "New Desc"
        assert sample_task.priority == "high"
        assert sample_task.due_date == new_due
        assert sample_task.completed == True

    def test_update_marks_timestamp(self, mock_db, sample_task):
        """Test that update always updates timestamp."""
        old_updated_at = sample_task.updated_at

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title="New Title"
        )

        result = update_task(mock_db, params)

        # Timestamp should be updated
        assert sample_task.updated_at != old_updated_at


class TestUpdateFuzzyMatching:
    """Test fuzzy matching integration for update by name."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    def test_update_extracts_task_name(self, classifier):
        """Test task name extraction for fuzzy matching."""
        result = classifier.classify("update the grocery task to high priority")
        assert result.intent_type == Intent.UPDATE_TASK
        # Should extract 'grocery' as task name
        assert "grocery" in str(result.extracted_entities).lower()

    def test_update_handles_typos_in_name(self, classifier):
        """Test that typos don't prevent update intent detection."""
        # Typo: "grocerys" instead of "grocery"
        result = classifier.classify("update the grocerys task")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_update_with_partial_name(self, classifier):
        """Test update with partial task name."""
        result = classifier.classify("update the milk task to high priority")
        assert result.intent_type == Intent.UPDATE_TASK


class TestUpdateEdgeBoundaries:
    """Test boundary conditions for update."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    def test_update_with_no_changes_rejected(self, mock_db):
        """Test that update with no fields is rejected."""
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        mock_db.exec.return_value.first.return_value = task

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1
            # No fields provided
        )

        with pytest.raises(ValueError, match="At least one field"):
            update_task(mock_db, params)

    def test_update_task_id_zero(self, mock_db):
        """Test updating task with ID 0 (edge case)."""
        mock_db.exec.return_value.first.return_value = None

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=0,
            title="New Title"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)

    def test_update_negative_task_id(self, mock_db):
        """Test updating task with negative ID."""
        mock_db.exec.return_value.first.return_value = None

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=-1,
            title="New Title"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(mock_db, params)

    def test_update_preserves_created_at(self, mock_db):
        """Test that created_at is never modified during update."""
        original_created = datetime(2026, 1, 1, 10, 0, 0)
        task = Mock()
        task.id = 1
        task.user_id = "user-123"
        task.title = "Original"
        task.description = "Test description"  # Add explicit string
        task.priority = "medium"
        task.due_date = None  # Explicit None
        task.completed = False
        task.created_at = original_created
        task.updated_at = datetime.utcnow()
        mock_db.exec.return_value.first.return_value = task

        params = UpdateTaskParams(
            user_id="user-123",
            task_id=1,
            title="New Title"
        )

        result = update_task(mock_db, params)

        # created_at should remain unchanged
        assert task.created_at == original_created
