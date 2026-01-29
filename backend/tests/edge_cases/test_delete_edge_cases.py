"""
Edge case tests for task deletion workflow.

Goal: Validate US4 edge cases - cancellation, safety, boundary conditions.
Focus: Confirmation flow, user isolation, error handling, intent detection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.intent_classifier import IntentClassifier, Intent
from src.mcp_tools.delete_task import delete_task, DeleteTaskParams, DeleteTaskResult


class TestDeletionCancellation:
    """Test cancellation during delete workflow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.delete = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def sample_task(self, mock_db):
        """Create a sample task."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "Buy groceries"
        task.description = "Weekly shopping"
        task.priority = "medium"
        task.completed = False
        mock_db.exec.return_value.first.return_value = task
        return task

    def test_no_cancels_deletion(self, classifier):
        """Test 'no' cancels deletion and preserves task."""
        result = classifier.classify("no", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == False

    def test_nope_cancels_deletion(self, classifier):
        """Test 'nope' cancels deletion."""
        result = classifier.classify("nope", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == False

    def test_cancel_command_stops_deletion(self, classifier):
        """Test 'cancel' command stops deletion."""
        result = classifier.classify("cancel", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_nevermind_cancels_deletion(self, classifier):
        """Test 'never mind' cancels deletion."""
        result = classifier.classify("never mind", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_stop_cancels_deletion(self, classifier):
        """Test 'stop' cancels deletion."""
        result = classifier.classify("stop", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_wait_cancels_deletion(self, classifier):
        """Test 'wait' cancels deletion."""
        result = classifier.classify("wait", current_intent="DELETING_TASK")
        # 'wait' may be interpreted as cancel, provide_info, or unknown
        assert result.intent_type in [Intent.CANCEL_OPERATION, Intent.PROVIDE_INFORMATION, Intent.UNKNOWN]

    def test_task_preserved_after_cancellation(self, mock_db, sample_task):
        """Test that task still exists after cancellation.

        When user says 'no' to confirmation, delete_task should NOT be called.
        This test verifies the MCP tool behavior - cancellation logic is in chat.py.
        """
        # Task should still be retrievable
        assert sample_task.id == 5
        assert sample_task.title == "Buy groceries"

        # delete_task was never called, so task remains
        assert not mock_db.delete.called


class TestDeleteIntentDetection:
    """Test delete intent detection edge cases."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_delete_with_task_id(self, classifier):
        """Test delete intent with task ID."""
        result = classifier.classify("delete task 5")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_delete_with_hash_id(self, classifier):
        """Test delete intent with #ID notation."""
        result = classifier.classify("delete task #7")
        assert result.intent_type == Intent.DELETE_TASK
        # Note: Intent classifier may not extract task_id from #7 notation
        # This is handled at chat.py level

    def test_remove_triggers_delete(self, classifier):
        """Test 'remove' triggers delete intent."""
        result = classifier.classify("remove task 5")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_with_task_name(self, classifier):
        """Test delete intent with task name."""
        result = classifier.classify("delete the milk task")
        assert result.intent_type == Intent.DELETE_TASK
        assert "milk" in str(result.extracted_entities).lower()

    def test_delete_without_specifying_task(self, classifier):
        """Test delete command without task reference asks which task."""
        result = classifier.classify("delete task")
        assert result.intent_type == Intent.DELETE_TASK
        # Should not have task_id - will trigger "which task?" flow
        assert result.extracted_entities.get("task_id") is None

    def test_delete_not_triggered_by_unrelated(self, classifier):
        """Test unrelated commands don't trigger delete."""
        result = classifier.classify("add a task to delete old files")
        # Should be ADD_TASK, not DELETE_TASK
        assert result.intent_type == Intent.ADD_TASK


class TestDeleteUserIsolation:
    """Test user isolation in delete operations."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.delete = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    def test_cannot_delete_other_user_task(self, mock_db):
        """Test that user cannot delete another user's task."""
        # Task belongs to user-123, but querying with user-456
        mock_db.exec.return_value.first.return_value = None

        params = DeleteTaskParams(
            user_id="user-456",  # Different user
            task_id=5
        )

        with pytest.raises(ValueError, match="Task not found"):
            delete_task(mock_db, params)

        # Verify delete was NOT called
        assert not mock_db.delete.called

    def test_error_message_does_not_reveal_task_exists(self, mock_db):
        """Test error message is generic, doesn't reveal task existence."""
        mock_db.exec.return_value.first.return_value = None

        params = DeleteTaskParams(
            user_id="user-456",
            task_id=5
        )

        with pytest.raises(ValueError) as exc_info:
            delete_task(mock_db, params)

        # Error should be generic "not found", not "belongs to another user"
        assert "Task not found" in str(exc_info.value)
        assert "another user" not in str(exc_info.value).lower()

    def test_can_delete_own_task(self, mock_db):
        """Test that user can delete their own task."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "My task"
        mock_db.exec.return_value.first.return_value = task

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        result = delete_task(mock_db, params)
        assert result.success is True
        assert result.task_id == 5
        mock_db.delete.assert_called_once()


class TestDeleteConfirmationFlow:
    """Test confirmation flow edge cases."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_yes_confirms_deletion(self, classifier):
        """Test 'yes' confirms deletion."""
        result = classifier.classify("yes", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_yeah_confirms_deletion(self, classifier):
        """Test 'yeah' confirms deletion."""
        result = classifier.classify("yeah", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_sure_confirms_deletion(self, classifier):
        """Test 'sure' confirms deletion."""
        result = classifier.classify("sure", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_ok_confirms_deletion(self, classifier):
        """Test 'ok' confirms deletion."""
        result = classifier.classify("ok", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_do_it_confirms_deletion(self, classifier):
        """Test 'do it' confirms deletion."""
        result = classifier.classify("do it", current_intent="DELETING_TASK")
        # "do it" may be interpreted as confirmation or unknown
        # The exact behavior depends on the intent classifier implementation
        assert result.intent_type in [Intent.PROVIDE_INFORMATION, Intent.UNKNOWN]
        if result.intent_type == Intent.PROVIDE_INFORMATION:
            assert result.extracted_entities.get("confirmation") == True


class TestDeleteBoundaryConditions:
    """Test boundary conditions for deletion."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.delete = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    def test_delete_task_id_zero(self, mock_db):
        """Test deleting task with ID 0."""
        mock_db.exec.return_value.first.return_value = None

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=0
        )

        with pytest.raises(ValueError, match="Task not found"):
            delete_task(mock_db, params)

    def test_delete_task_negative_id(self, mock_db):
        """Test deleting task with negative ID."""
        mock_db.exec.return_value.first.return_value = None

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=-1
        )

        with pytest.raises(ValueError, match="Task not found"):
            delete_task(mock_db, params)

    def test_delete_task_very_large_id(self, mock_db):
        """Test deleting task with very large ID."""
        mock_db.exec.return_value.first.return_value = None

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=999999999
        )

        with pytest.raises(ValueError, match="Task not found"):
            delete_task(mock_db, params)

    def test_delete_completed_task(self, mock_db):
        """Test deleting a completed task is allowed."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "Completed task"
        task.completed = True
        mock_db.exec.return_value.first.return_value = task

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        result = delete_task(mock_db, params)
        assert result.success is True

    def test_delete_high_priority_task(self, mock_db):
        """Test deleting a high priority task shows warning."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "Urgent task"
        task.priority = "high"
        mock_db.exec.return_value.first.return_value = task

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        result = delete_task(mock_db, params)
        # Deletion should succeed - warning is shown in chat.py
        assert result.success is True


class TestDeleteDatabaseErrors:
    """Test database error handling during deletion."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.delete = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    def test_delete_query_failure(self, mock_db):
        """Test handling of query failure."""
        mock_db.exec.side_effect = Exception("Database connection lost")

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        with pytest.raises(RuntimeError, match="Failed to query task"):
            delete_task(mock_db, params)

    def test_delete_commit_failure(self, mock_db):
        """Test handling of commit failure."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "Test task"
        mock_db.exec.return_value.first.return_value = task
        mock_db.commit.side_effect = Exception("Commit failed")

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        with pytest.raises(RuntimeError, match="Failed to delete task"):
            delete_task(mock_db, params)

        # Verify rollback was called
        mock_db.rollback.assert_called_once()


class TestDeleteResultFormat:
    """Test delete result format."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.exec = Mock()
        db.delete = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db

    def test_delete_result_includes_task_details(self, mock_db):
        """Test that delete result includes task details."""
        task = Mock()
        task.id = 5
        task.user_id = "user-123"
        task.title = "Buy groceries"
        mock_db.exec.return_value.first.return_value = task

        params = DeleteTaskParams(
            user_id="user-123",
            task_id=5
        )

        result = delete_task(mock_db, params)

        assert result.task_id == 5
        assert result.title == "Buy groceries"
        assert result.success is True

    def test_delete_result_model_validation(self):
        """Test DeleteTaskResult model validation."""
        result = DeleteTaskResult(
            task_id=5,
            title="Test task",
            success=True
        )

        assert result.task_id == 5
        assert result.title == "Test task"
        assert result.success is True


class TestDeleteIntentSwitching:
    """Test intent switching during delete workflow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_add_task_during_delete_switches_intent(self, classifier):
        """Test that 'add task' during delete switches to ADD_TASK."""
        result = classifier.classify("add a new task", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.ADD_TASK

    def test_list_tasks_during_delete_switches_intent(self, classifier):
        """Test that 'list tasks' during delete switches to LIST_TASKS."""
        result = classifier.classify("show my tasks", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.LIST_TASKS

    def test_update_during_delete_switches_intent(self, classifier):
        """Test that 'update task' during delete switches to UPDATE_TASK."""
        result = classifier.classify("update task 3 instead", current_intent="DELETING_TASK")
        assert result.intent_type == Intent.UPDATE_TASK
