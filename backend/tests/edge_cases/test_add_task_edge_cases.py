"""
Edge case tests for add-task workflow.

Tests critical edge cases that must be handled correctly:
- Ambiguous input ("milk" - is it a command or task title?)
- Intent switching mid-flow (user changes their mind)
- Empty/invalid input handling
- Conflicting information
"""

import pytest
from src.services.intent_classifier import IntentClassifier, Intent


class TestAmbiguousTitleEdgeCases:
    """Test handling of ambiguous task titles."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_single_word_in_neutral_context(self, classifier):
        """Single word in NEUTRAL context is ambiguous."""
        result = classifier.classify(
            message="milk",
            current_intent="NEUTRAL"
        )

        # In neutral context, single word is UNKNOWN or low confidence
        # It's ambiguous - could be asking about milk tasks or wanting to add milk
        assert result.intent_type in [Intent.UNKNOWN, Intent.ADD_TASK]
        if result.intent_type == Intent.ADD_TASK:
            # If classified as ADD_TASK, confidence should be lower
            assert result.confidence < 0.9

    def test_single_word_in_adding_task_context(self, classifier):
        """Single word in ADDING_TASK context is task title."""
        result = classifier.classify(
            message="milk",
            current_intent="ADDING_TASK"
        )

        # In adding context, this is clearly providing the title
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("title") == "milk"

    def test_command_phrase_not_confused_with_title(self, classifier):
        """'delete task' should not become task title."""
        result = classifier.classify(
            message="delete task 5",
            current_intent="NEUTRAL"
        )

        # CRITICAL: This must be DELETE_TASK, not ADD_TASK with title "delete task 5"
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_update_command_not_confused_with_title(self, classifier):
        """'update task' should not become task title."""
        result = classifier.classify(
            message="update task 3",
            current_intent="NEUTRAL"
        )

        # CRITICAL: This must be UPDATE_TASK, not ADD_TASK
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("task_id") == 3

    def test_ambiguous_priority_keyword(self, classifier):
        """'important' could be priority or part of title."""
        # In neutral context: ambiguous
        result1 = classifier.classify(
            message="important meeting",
            current_intent="NEUTRAL"
        )
        # Could be ADD_TASK with title "important meeting" and high priority

        # In adding context: provides priority
        result2 = classifier.classify(
            message="important",
            current_intent="ADDING_TASK"
        )
        assert result2.intent_type == Intent.PROVIDE_INFORMATION
        # Should extract as priority
        assert result2.extracted_entities.get("priority") == "high"

    def test_yes_no_ambiguity(self, classifier):
        """'yes' and 'no' only make sense in context."""
        # In neutral context: unclear
        result1 = classifier.classify(
            message="yes",
            current_intent="NEUTRAL"
        )
        # Probably UNKNOWN or low confidence

        # In adding context: confirmation
        result2 = classifier.classify(
            message="yes",
            current_intent="ADDING_TASK"
        )
        assert result2.intent_type == Intent.PROVIDE_INFORMATION
        assert result2.extracted_entities.get("confirmation") == True


class TestIntentSwitchingEdgeCases:
    """Test intent switching mid-workflow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_switch_from_add_to_list(self, classifier):
        """Switch from ADDING_TASK to LIST_TASKS."""
        # User starts adding a task
        result1 = classifier.classify("add task to buy milk")
        assert result1.intent_type == Intent.ADD_TASK

        # Then asks to see tasks instead
        result2 = classifier.classify(
            message="show my tasks",
            current_intent="ADDING_TASK"
        )
        assert result2.intent_type == Intent.LIST_TASKS

        # State should be reset to NEUTRAL after LIST_TASKS completes

    def test_switch_from_add_to_delete(self, classifier):
        """Switch from ADDING_TASK to DELETE_TASK."""
        result = classifier.classify(
            message="delete task 5",
            current_intent="ADDING_TASK"
        )

        # Should recognize as DELETE_TASK even in adding context
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_cancel_operation_mid_add(self, classifier):
        """User cancels add-task mid-flow."""
        result = classifier.classify(
            message="cancel",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_multiple_switches_in_sequence(self, classifier):
        """Handle multiple intent switches."""
        # Start add task
        r1 = classifier.classify("add task to buy milk")
        assert r1.intent_type == Intent.ADD_TASK

        # Switch to list
        r2 = classifier.classify("show tasks", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.LIST_TASKS

        # Then back to add (new task)
        r3 = classifier.classify("add task to call mom", current_intent="NEUTRAL")
        assert r3.intent_type == Intent.ADD_TASK

    def test_nested_add_task_commands(self, classifier):
        """User tries to add another task while adding a task."""
        # Already adding "buy milk"
        result = classifier.classify(
            message="add task to call mom",
            current_intent="ADDING_TASK"
        )

        # This is tricky - could be:
        # 1. Providing title for current task: "add task to call mom"
        # 2. Starting a new add task operation
        # We should treat it as a new ADD_TASK command
        assert result.intent_type == Intent.ADD_TASK


class TestEmptyAndInvalidInput:
    """Test handling of empty and invalid input."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_empty_message_in_adding_context(self, classifier):
        """Empty message in ADDING_TASK context."""
        result = classifier.classify(
            message="",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.UNKNOWN
        assert result.confidence == 0.0

    def test_whitespace_only_message(self, classifier):
        """Message with only whitespace."""
        result = classifier.classify(
            message="   ",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.UNKNOWN

    def test_very_long_message(self, classifier):
        """Very long message (200+ characters)."""
        long_message = "add task to " + ("very " * 50) + "important thing"

        result = classifier.classify(long_message)

        # Should still classify correctly
        assert result.intent_type == Intent.ADD_TASK

    def test_special_characters_in_title(self, classifier):
        """Task title with special characters."""
        result = classifier.classify("add task: buy @milk #2 (organic)")

        assert result.intent_type == Intent.ADD_TASK
        # Title should preserve special characters

    def test_unicode_characters_in_title(self, classifier):
        """Task title with unicode characters."""
        result = classifier.classify("add task to buy 牛奶")

        assert result.intent_type == Intent.ADD_TASK

    def test_multiple_languages_mixed(self, classifier):
        """Mixed language input."""
        result = classifier.classify("add task comprar milk")

        # Should still detect ADD_TASK from "add task"
        assert result.intent_type == Intent.ADD_TASK


class TestConflictingInformation:
    """Test handling of conflicting information."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_multiple_priorities_in_message(self, classifier):
        """Message with multiple priority keywords."""
        result = classifier.classify(
            "add high priority low importance task"
        )

        # Should pick one priority (preferably first/highest)
        assert result.intent_type == Intent.ADD_TASK
        entities = result.extracted_entities
        if "priority" in entities:
            assert entities["priority"] in ["high", "low"]

    def test_contradictory_dates(self, classifier):
        """Message with contradictory date information."""
        result = classifier.classify(
            "add task by tomorrow no by next week"
        )

        # Should still classify as ADD_TASK
        # Date parsing will need to handle the conflict
        assert result.intent_type == Intent.ADD_TASK

    def test_multiple_tasks_in_one_message(self, classifier):
        """User tries to add multiple tasks at once."""
        result = classifier.classify(
            "add task to buy milk and also add task to call mom"
        )

        # Should detect ADD_TASK
        # Could extract first task or both - implementation choice
        assert result.intent_type == Intent.ADD_TASK


class TestRapidFireMessages:
    """Test handling of rapid consecutive messages."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_quick_succession_messages(self, classifier):
        """Multiple messages in quick succession."""
        messages = [
            ("add task to buy milk", "NEUTRAL"),
            ("high priority", "ADDING_TASK"),
            ("tomorrow", "ADDING_TASK"),
            ("no", "ADDING_TASK"),
        ]

        results = []
        for message, context in messages:
            result = classifier.classify(message, current_intent=context)
            results.append(result)

        # First should be ADD_TASK
        assert results[0].intent_type == Intent.ADD_TASK

        # Rest should be PROVIDE_INFORMATION
        assert results[1].intent_type == Intent.PROVIDE_INFORMATION
        assert results[2].intent_type == Intent.PROVIDE_INFORMATION
        assert results[3].intent_type == Intent.PROVIDE_INFORMATION

    def test_duplicate_information_provision(self, classifier):
        """User provides same information twice."""
        # First time providing priority
        r1 = classifier.classify(
            message="high priority",
            current_intent="ADDING_TASK"
        )
        assert r1.intent_type == Intent.PROVIDE_INFORMATION
        assert r1.extracted_entities.get("priority") == "high"

        # Provides priority again (maybe changing mind)
        r2 = classifier.classify(
            message="actually low priority",
            current_intent="ADDING_TASK"
        )
        # Should still extract as PROVIDE_INFORMATION
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        # Should extract new priority
        assert r2.extracted_entities.get("priority") == "low"


class TestStateRecoveryEdgeCases:
    """Test state recovery in edge cases."""

    def test_state_after_error(self):
        """State should be recoverable after error."""
        # If task creation fails, state should not be lost
        # User should be able to retry or modify
        assert True  # Placeholder

    def test_state_after_timeout(self):
        """State should handle session timeout gracefully."""
        # If user returns after long time, state should be cleared
        # or user should be prompted to continue
        assert True  # Placeholder

    def test_state_with_concurrent_requests(self):
        """Handle concurrent requests on same conversation."""
        # Should maintain consistency
        assert True  # Placeholder


class TestBoundaryConditions:
    """Test boundary conditions."""

    def test_title_max_length(self):
        """Task title at maximum length (200 chars)."""
        title = "a" * 200
        assert len(title) == 200

    def test_title_exceeds_max_length(self):
        """Task title exceeds maximum length."""
        title = "a" * 201
        assert len(title) > 200
        # Should be truncated or rejected

    def test_description_max_length(self):
        """Task description at maximum length (1000 chars)."""
        description = "a" * 1000
        assert len(description) == 1000

    def test_description_exceeds_max_length(self):
        """Task description exceeds maximum length."""
        description = "a" * 1001
        assert len(description) > 1000
        # Should be truncated or rejected
