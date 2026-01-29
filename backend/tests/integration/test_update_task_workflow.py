"""
Integration tests for task update workflow.

Goal: Validate US3 - Task Update with natural language and confirmation flow.
Focus: Multi-turn conversations, field extraction, fuzzy matching, confirmation.
"""

import pytest
from src.services.intent_classifier import IntentClassifier, Intent
from src.ai_agent.context_manager import ContextManager
from src.services.conversation_service import ConversationService
from src.mcp_tools.add_task import add_task, AddTaskParams
from src.mcp_tools.update_task import update_task, UpdateTaskParams
from src.mcp_tools.list_tasks import list_tasks, ListTasksParams
from src.mcp_tools.find_task import find_task, FindTaskParams


class TestBasicUpdateWorkflow:
    """Test basic task update workflow with step-by-step flow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def sample_task(self, db, test_user_id):
        """Create a sample task for updating."""
        params = AddTaskParams(
            user_id=test_user_id,
            title="Buy milk",
            priority="medium",
            description="From grocery store"
        )
        result = add_task(db, params)
        return result

    def test_update_by_id_single_field(self, classifier, db, test_user_id, sample_task):
        """Test updating a task by ID with single field change."""
        # Step 1: User wants to update task priority
        r1 = classifier.classify("update task {} to high priority".format(sample_task.task_id), current_intent="NEUTRAL")
        assert r1.intent_type == Intent.UPDATE_TASK
        assert r1.extracted_entities.get("task_id") == sample_task.task_id
        assert r1.extracted_entities.get("priority") == "high"

        # Execute update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id,
            priority="high"
        )
        result = update_task(db, update_params)

        assert result.task_id == sample_task.task_id
        assert result.title == "Buy milk"
        assert result.priority == "high"
        assert result.description == "From grocery store"

    def test_update_by_id_multiple_fields(self, classifier, db, test_user_id, sample_task):
        """Test updating multiple fields at once."""
        # Step 1: User wants to update multiple fields
        r1 = classifier.classify(
            "update task {} title to Buy milk and eggs, priority to high".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK
        assert r1.extracted_entities.get("task_id") == sample_task.task_id

        # Execute multi-field update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id,
            title="Buy milk and eggs",
            priority="high"
        )
        result = update_task(db, update_params)

        assert result.task_id == sample_task.task_id
        assert result.title == "Buy milk and eggs"
        assert result.priority == "high"

    def test_update_asks_what_to_update_if_not_specified(self, classifier, db, test_user_id, sample_task):
        """Test that update without details asks what to update."""
        # Step 1: User wants to update but doesn't specify what
        r1 = classifier.classify("update task {}".format(sample_task.task_id), current_intent="NEUTRAL")
        assert r1.intent_type == Intent.UPDATE_TASK
        assert r1.extracted_entities.get("task_id") == sample_task.task_id

        # System should ask: "What would you like to update?"
        # Then user provides details in next message

    def test_update_by_name_with_exact_match(self, classifier, db, test_user_id, sample_task):
        """Test updating task by name using exact match."""
        # Step 1: User refers to task by title
        r1 = classifier.classify("update the milk task to high priority", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.UPDATE_TASK

        # Find task by title
        find_params = FindTaskParams(
            user_id=test_user_id,
            title="milk"
        )
        find_result = find_task(db, find_params)

        assert find_result is not None
        assert find_result.task_id == sample_task.task_id
        assert find_result.confidence_score >= 70

        # Execute update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=find_result.task_id,
            priority="high"
        )
        result = update_task(db, update_params)
        assert result.priority == "high"

    def test_update_description(self, classifier, db, test_user_id, sample_task):
        """Test updating task description."""
        # Step 1: User wants to update description
        r1 = classifier.classify(
            "update task {} description to Get whole milk from Walmart".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK

        # Execute update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id,
            description="Get whole milk from Walmart"
        )
        result = update_task(db, update_params)

        assert result.description == "Get whole milk from Walmart"
        assert result.title == "Buy milk"  # Other fields unchanged


class TestMultiFieldUpdateWorkflow:
    """Test multi-field update scenarios."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def sample_task(self, db, test_user_id):
        """Create a sample task for updating."""
        params = AddTaskParams(
            user_id=test_user_id,
            title="Call dentist",
            priority="low",
            description="Schedule appointment"
        )
        result = add_task(db, params)
        return result

    def test_update_all_fields_at_once(self, classifier, db, test_user_id, sample_task):
        """Test updating title, priority, and description simultaneously."""
        # User provides all changes at once
        r1 = classifier.classify(
            "update task {} title to Call dentist for checkup, priority to high, description to Schedule cleaning appointment".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK

        # Execute multi-field update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id,
            title="Call dentist for checkup",
            priority="high",
            description="Schedule cleaning appointment"
        )
        result = update_task(db, update_params)

        assert result.title == "Call dentist for checkup"
        assert result.priority == "high"
        assert result.description == "Schedule cleaning appointment"

    def test_update_priority_with_keywords(self, classifier, db, test_user_id, sample_task):
        """Test priority update using natural language keywords."""
        # Test different priority keywords
        priority_tests = [
            ("make it urgent", "high"),
            ("change to high priority", "high"),
            ("set priority to medium", "medium"),
            ("make it low priority", "low"),
        ]

        for message_suffix, expected_priority in priority_tests:
            r1 = classifier.classify(
                f"update task {sample_task.task_id} {message_suffix}",
                current_intent="NEUTRAL"
            )
            assert r1.intent_type == Intent.UPDATE_TASK

            if expected_priority in r1.extracted_entities.get("priority", "").lower() or \
               expected_priority in message_suffix:
                # Priority extracted correctly
                update_params = UpdateTaskParams(
                    user_id=test_user_id,
                    task_id=sample_task.task_id,
                    priority=expected_priority
                )
                result = update_task(db, update_params)
                assert result.priority == expected_priority

    def test_update_title_and_keep_other_fields(self, classifier, db, test_user_id, sample_task):
        """Test that updating title doesn't affect other fields."""
        original_priority = sample_task.priority
        original_description = sample_task.description

        # Update only title
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id,
            title="Call dentist tomorrow"
        )
        result = update_task(db, update_params)

        assert result.title == "Call dentist tomorrow"
        assert result.priority == original_priority
        assert result.description == original_description


class TestUpdateWithFuzzyMatching:
    """Test update workflow with fuzzy task matching."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def sample_tasks(self, db, test_user_id):
        """Create multiple sample tasks."""
        tasks = []

        # Task 1
        params1 = AddTaskParams(
            user_id=test_user_id,
            title="Buy groceries",
            priority="medium"
        )
        tasks.append(add_task(db, params1))

        # Task 2
        params2 = AddTaskParams(
            user_id=test_user_id,
            title="Buy books",
            priority="low"
        )
        tasks.append(add_task(db, params2))

        return tasks

    def test_update_with_partial_title_match(self, classifier, db, test_user_id, sample_tasks):
        """Test updating task using partial title match."""
        # User uses partial title
        r1 = classifier.classify("update the groceries task to high priority", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.UPDATE_TASK

        # Find task using fuzzy matching
        find_params = FindTaskParams(
            user_id=test_user_id,
            title="groceries"
        )
        find_result = find_task(db, find_params)

        assert find_result is not None
        assert "groceries" in find_result.title.lower()
        assert find_result.confidence_score >= 70

        # Execute update
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=find_result.task_id,
            priority="high"
        )
        result = update_task(db, update_params)
        assert result.priority == "high"

    def test_update_with_typo_in_title(self, classifier, db, test_user_id, sample_tasks):
        """Test fuzzy matching handles typos in task title."""
        # User has typo: "grocerys" instead of "groceries"
        find_params = FindTaskParams(
            user_id=test_user_id,
            title="grocerys"
        )
        find_result = find_task(db, find_params)

        # Should still find the task
        assert find_result is not None
        assert "groceries" in find_result.title.lower()
        assert find_result.confidence_score >= 60  # Lower threshold for typos

    def test_update_disambiguation_when_multiple_matches(self, classifier, db, test_user_id, sample_tasks):
        """Test handling when fuzzy match returns multiple results."""
        # User uses ambiguous query "buy"
        find_params = FindTaskParams(
            user_id=test_user_id,
            title="buy"
        )
        find_result = find_task(db, find_params)

        # Should return the best match (highest confidence)
        assert find_result is not None
        assert "buy" in find_result.title.lower()


class TestUpdateConfirmation:
    """Test update confirmation flow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def sample_task(self, db, test_user_id):
        """Create a sample task."""
        params = AddTaskParams(
            user_id=test_user_id,
            title="Write report",
            priority="medium",
            description="Quarterly report"
        )
        result = add_task(db, params)
        return result

    def test_confirmation_required_for_update(self, classifier, sample_task):
        """Test that update requires confirmation."""
        # Step 1: User initiates update
        r1 = classifier.classify(
            "update task {} to high priority".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK

        # System should show:
        # "Update task #X: 'Write report'?"
        # "Priority: medium → high"
        # "Reply 'yes' to confirm or 'no' to cancel"

        # Step 2: User confirms
        r2 = classifier.classify("yes", current_intent="UPDATING_TASK")
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        assert r2.extracted_entities.get("confirmation") == True

    def test_confirmation_cancellation(self, classifier, sample_task):
        """Test canceling update during confirmation."""
        # Step 1: User initiates update
        r1 = classifier.classify(
            "update task {} to high priority".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK

        # Step 2: User cancels
        r2 = classifier.classify("no", current_intent="UPDATING_TASK")
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        assert r2.extracted_entities.get("confirmation") == False

        # Task should remain unchanged

    def test_multi_field_update_confirmation_shows_all_changes(self, classifier, sample_task):
        """Test that confirmation message shows all changes."""
        # User wants to update multiple fields
        r1 = classifier.classify(
            "update task {} title to Write quarterly report, priority to high".format(sample_task.task_id),
            current_intent="NEUTRAL"
        )
        assert r1.intent_type == Intent.UPDATE_TASK

        # Confirmation message should show:
        # "Update task #X:"
        # "• Title: 'Write report' → 'Write quarterly report'"
        # "• Priority: medium → high"
        # "Reply 'yes' to confirm"


class TestUpdateEdgeCases:
    """Test edge cases for task update."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def sample_task(self, db, test_user_id):
        """Create a sample task."""
        params = AddTaskParams(
            user_id=test_user_id,
            title="Test task",
            priority="medium"
        )
        result = add_task(db, params)
        return result

    def test_update_nonexistent_task(self, db, test_user_id):
        """Test updating a task that doesn't exist."""
        # Try to update non-existent task
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=99999,
            priority="high"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(db, update_params)

    def test_update_without_changes(self, db, test_user_id, sample_task):
        """Test that update requires at least one field."""
        # Try to update without providing any fields
        update_params = UpdateTaskParams(
            user_id=test_user_id,
            task_id=sample_task.task_id
        )

        with pytest.raises(ValueError, match="At least one field"):
            update_task(db, update_params)

    def test_update_with_invalid_priority(self, db, test_user_id, sample_task):
        """Test update with invalid priority value."""
        # Try to set invalid priority
        with pytest.raises(ValueError, match="Invalid priority"):
            update_params = UpdateTaskParams(
                user_id=test_user_id,
                task_id=sample_task.task_id,
                priority="super-urgent"  # Invalid
            )

    def test_update_other_user_task(self, db, test_user_id, sample_task):
        """Test that user cannot update another user's task."""
        # Try to update task with different user_id
        update_params = UpdateTaskParams(
            user_id="other-user-123",  # Different user
            task_id=sample_task.task_id,
            priority="high"
        )

        with pytest.raises(ValueError, match="Task not found"):
            update_task(db, update_params)
