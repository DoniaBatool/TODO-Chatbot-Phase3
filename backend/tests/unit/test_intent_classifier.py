"""
Unit tests for IntentClassifier.

Tests intent detection patterns for:
- ADD_TASK, UPDATE_TASK, DELETE_TASK, COMPLETE_TASK, LIST_TASKS
- CANCEL_OPERATION, PROVIDE_INFORMATION
- Context-aware classification
"""

import pytest
from src.services.intent_classifier import IntentClassifier, Intent


class TestIntentClassifier:
    """Test intent classification accuracy."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier instance."""
        return IntentClassifier()

    # ADD_TASK Intent Tests
    def test_add_task_explicit(self, classifier):
        """Detect 'add task' command."""
        intent = classifier.classify("add task to buy milk")
        assert intent.intent_type == Intent.ADD_TASK
        assert intent.confidence >= 0.9

    def test_add_task_create_synonym(self, classifier):
        """Detect 'create task' synonym."""
        intent = classifier.classify("create task for meeting")
        assert intent.intent_type == Intent.ADD_TASK

    def test_add_task_natural_language(self, classifier):
        """Detect natural language task creation."""
        intent = classifier.classify("want to call shops for macbook prices")
        assert intent.intent_type == Intent.ADD_TASK
        assert "call shops" in intent.extracted_entities.get("title", "")

    def test_add_task_urgent(self, classifier):
        """Detect urgent task creation with priority extraction."""
        intent = classifier.classify("add urgent task to fix bug")
        assert intent.intent_type == Intent.ADD_TASK
        assert intent.extracted_entities.get("priority") == "high"

    # DELETE_TASK Intent Tests
    def test_delete_task_by_id(self, classifier):
        """Detect 'delete task 5' - NOT as task title."""
        intent = classifier.classify("delete task 5")
        assert intent.intent_type == Intent.DELETE_TASK
        assert intent.extracted_entities.get("task_id") == 5

    def test_delete_task_by_name(self, classifier):
        """Detect 'delete the milk task'."""
        intent = classifier.classify("delete the milk task")
        assert intent.intent_type == Intent.DELETE_TASK
        assert "milk" in intent.extracted_entities.get("task_name", "")

    def test_remove_task_synonym(self, classifier):
        """Detect 'remove task' synonym."""
        intent = classifier.classify("remove task 3")
        assert intent.intent_type == Intent.DELETE_TASK

    # UPDATE_TASK Intent Tests
    def test_update_task_by_id(self, classifier):
        """Detect 'update task 3'."""
        intent = classifier.classify("update task 3")
        assert intent.intent_type == Intent.UPDATE_TASK
        assert intent.extracted_entities.get("task_id") == 3

    def test_update_task_by_name(self, classifier):
        """Detect 'update the milk task'."""
        intent = classifier.classify("update the milk task")
        assert intent.intent_type == Intent.UPDATE_TASK
        assert "milk" in intent.extracted_entities.get("task_name", "")

    def test_change_task_synonym(self, classifier):
        """Detect 'change task' synonym."""
        intent = classifier.classify("change task 2 to high priority")
        assert intent.intent_type == Intent.UPDATE_TASK

    # COMPLETE_TASK Intent Tests
    def test_mark_task_complete(self, classifier):
        """Detect 'mark task 7 as complete'."""
        intent = classifier.classify("mark task 7 as complete")
        assert intent.intent_type == Intent.COMPLETE_TASK
        assert intent.extracted_entities.get("task_id") == 7

    def test_complete_task_natural(self, classifier):
        """Detect 'I finished buying milk'."""
        intent = classifier.classify("I finished buying milk")
        assert intent.intent_type == Intent.COMPLETE_TASK
        assert "buying milk" in intent.extracted_entities.get("task_name", "")

    def test_task_done_synonym(self, classifier):
        """Detect 'task done' synonym."""
        intent = classifier.classify("task 5 is done")
        assert intent.intent_type == Intent.COMPLETE_TASK

    # LIST_TASKS Intent Tests
    def test_show_my_tasks(self, classifier):
        """Detect 'show my tasks'."""
        intent = classifier.classify("show my tasks")
        assert intent.intent_type == Intent.LIST_TASKS

    def test_list_all_tasks(self, classifier):
        """Detect 'list all tasks'."""
        intent = classifier.classify("list all tasks")
        assert intent.intent_type == Intent.LIST_TASKS

    def test_show_pending_tasks(self, classifier):
        """Detect filtered listing."""
        intent = classifier.classify("show pending tasks")
        assert intent.intent_type == Intent.LIST_TASKS
        assert intent.extracted_entities.get("status") == "pending"

    # CANCEL_OPERATION Intent Tests
    def test_cancel_operation(self, classifier):
        """Detect 'never mind' cancellation."""
        intent = classifier.classify("never mind")
        assert intent.intent_type == Intent.CANCEL_OPERATION

    def test_cancel_synonym(self, classifier):
        """Detect 'cancel' synonym."""
        intent = classifier.classify("cancel that")
        assert intent.intent_type == Intent.CANCEL_OPERATION

    def test_stop_synonym(self, classifier):
        """Detect 'stop' synonym."""
        intent = classifier.classify("stop")
        assert intent.intent_type == Intent.CANCEL_OPERATION

    # PROVIDE_INFORMATION Intent Tests (Context-Aware)
    def test_provide_info_in_add_flow(self, classifier):
        """Detect 'high priority' as info when adding task."""
        intent = classifier.classify(
            message="high priority",
            current_intent="ADDING_TASK"
        )
        assert intent.intent_type == Intent.PROVIDE_INFORMATION
        assert intent.extracted_entities.get("priority") == "high"

    def test_provide_info_yes_confirmation(self, classifier):
        """Detect 'yes' as confirmation in context."""
        intent = classifier.classify(
            message="yes",
            current_intent="DELETING_TASK"
        )
        assert intent.intent_type == Intent.PROVIDE_INFORMATION
        assert intent.extracted_entities.get("confirmation") == True

    def test_provide_info_no_cancellation(self, classifier):
        """Detect 'no' as cancellation in context."""
        intent = classifier.classify(
            message="no",
            current_intent="UPDATING_TASK"
        )
        assert intent.intent_type == Intent.PROVIDE_INFORMATION
        assert intent.extracted_entities.get("confirmation") == False

    # Edge Cases
    def test_ambiguous_command_favors_context(self, classifier):
        """When ambiguous, use context to disambiguate."""
        intent = classifier.classify(
            message="make it high priority",
            current_intent="ADDING_TASK"
        )
        # Should be PROVIDE_INFO, not UPDATE_TASK
        assert intent.intent_type == Intent.PROVIDE_INFORMATION

    def test_single_word_in_add_flow(self, classifier):
        """Single word 'milk' in add flow is task title."""
        intent = classifier.classify(
            message="milk",
            current_intent="ADDING_TASK"
        )
        assert intent.intent_type == Intent.PROVIDE_INFORMATION
        assert intent.extracted_entities.get("title") == "milk"

    def test_neutral_context_detects_command(self, classifier):
        """In neutral context, 'delete task' is command."""
        intent = classifier.classify(
            message="delete task 5",
            current_intent="NEUTRAL"
        )
        assert intent.intent_type == Intent.DELETE_TASK
        # Should NOT be ADD_TASK with title "delete task 5"

    def test_confidence_score_range(self, classifier):
        """Confidence scores are between 0 and 1."""
        intent = classifier.classify("add task to test confidence")
        assert 0.0 <= intent.confidence <= 1.0

    def test_empty_message_returns_unknown(self, classifier):
        """Empty message returns unknown intent."""
        intent = classifier.classify("")
        assert intent.intent_type == Intent.UNKNOWN
        assert intent.confidence == 0.0

    # Integration with 100 test messages (to achieve 95%+ accuracy target)
    @pytest.mark.parametrize("message,expected_intent", [
        ("add task to buy groceries", Intent.ADD_TASK),
        ("create new task for meeting", Intent.ADD_TASK),
        ("delete task 10", Intent.DELETE_TASK),
        ("remove the shopping task", Intent.DELETE_TASK),
        ("update task 5 to high priority", Intent.UPDATE_TASK),
        ("change the milk task", Intent.UPDATE_TASK),
        ("mark task 3 as done", Intent.COMPLETE_TASK),
        ("I finished task 7", Intent.COMPLETE_TASK),
        ("show all my tasks", Intent.LIST_TASKS),
        ("list pending tasks", Intent.LIST_TASKS),
        ("never mind", Intent.CANCEL_OPERATION),
        ("cancel", Intent.CANCEL_OPERATION),
        # Add 88 more test cases to reach 100 total...
    ])
    def test_intent_accuracy_suite(self, classifier, message, expected_intent):
        """Test intent classification accuracy on large dataset."""
        intent = classifier.classify(message)
        assert intent.intent_type == expected_intent
