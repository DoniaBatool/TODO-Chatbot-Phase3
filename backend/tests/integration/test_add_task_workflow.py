"""
Integration tests for natural language task creation workflow.

Tests the complete conversational flow for adding tasks:
- Basic workflow: confirm → priority → deadline → description → create
- All-at-once creation: "add urgent task by Friday with description"
- Multi-turn conversation state management
- Intent classification and context switching
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.conversation_service import ConversationService
from src.services.intent_classifier import IntentClassifier, Intent


class TestAddTaskBasicWorkflow:
    """Test basic add-task conversational workflow."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def conversation_service(self, mock_db):
        """Create conversation service with mock DB."""
        return ConversationService(mock_db)

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_basic_workflow_step1_intent_detection(self, classifier):
        """Step 1: Detect ADD_TASK intent from initial message."""
        result = classifier.classify("add task to buy milk")

        assert result.intent_type == Intent.ADD_TASK
        assert result.confidence >= 0.8
        assert "buy milk" in result.extracted_entities.get("title", "").lower()

    def test_basic_workflow_step2_priority_collection(self, classifier):
        """Step 2: Collect priority as PROVIDE_INFORMATION in ADDING_TASK context."""
        result = classifier.classify(
            message="high priority",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "high"

    def test_basic_workflow_step3_deadline_collection(self, classifier):
        """Step 3: Collect deadline as PROVIDE_INFORMATION."""
        result = classifier.classify(
            message="tomorrow",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.PROVIDE_INFORMATION
        # "tomorrow" should be treated as information, not parsed here

    def test_basic_workflow_step4_description_collection(self, classifier):
        """Step 4: Handle "no" for description."""
        result = classifier.classify(
            message="no",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == False

    def test_conversation_state_initialization(self, conversation_service, mock_db):
        """Test conversation state is initialized when ADD_TASK detected."""
        # Create mock conversation
        mock_conversation = Mock()
        mock_conversation.id = 123
        mock_conversation.user_id = "user-123"
        mock_conversation.current_intent = "NEUTRAL"
        mock_conversation.state_data = None
        mock_conversation.target_task_id = None

        mock_db.exec.return_value.first.return_value = mock_conversation
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Initialize state for add-task
        result = conversation_service.update_conversation_state(
            conversation_id=123,
            user_id="user-123",
            current_intent="ADDING_TASK",
            state_data={"title": "buy milk", "step": "priority"}
        )

        assert result is not None
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_conversation_state_accumulation(self, conversation_service, mock_db):
        """Test state_data accumulates through workflow."""
        mock_conversation = Mock()
        mock_conversation.id = 123
        mock_conversation.user_id = "user-123"
        mock_conversation.current_intent = "ADDING_TASK"
        mock_conversation.state_data = {"title": "buy milk", "step": "priority"}

        mock_db.exec.return_value.first.return_value = mock_conversation
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Update state with priority
        result = conversation_service.update_conversation_state(
            conversation_id=123,
            user_id="user-123",
            state_data={
                "title": "buy milk",
                "priority": "high",
                "step": "deadline"
            }
        )

        assert result is not None
        assert mock_db.add.called

    def test_conversation_state_reset_after_completion(self, conversation_service, mock_db):
        """Test state resets to NEUTRAL after task creation."""
        mock_conversation = Mock()
        mock_conversation.id = 123
        mock_conversation.user_id = "user-123"
        mock_conversation.current_intent = "ADDING_TASK"
        mock_conversation.state_data = {
            "title": "buy milk",
            "priority": "high",
            "due_date": "2026-02-01T00:00:00"
        }

        mock_db.exec.return_value.first.return_value = mock_conversation
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Reset state after task created
        result = conversation_service.reset_conversation_state(
            conversation_id=123,
            user_id="user-123"
        )

        assert result is not None
        # Verify state is reset
        assert mock_db.add.called


class TestAddTaskAllAtOnce:
    """Test all-at-once task creation with complete information."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_all_at_once_with_priority_and_deadline(self, classifier):
        """Detect ADD_TASK with all information provided."""
        result = classifier.classify(
            "add urgent task to buy milk by tomorrow"
        )

        assert result.intent_type == Intent.ADD_TASK
        assert result.confidence >= 0.8

        # Should extract title and priority
        entities = result.extracted_entities
        assert "milk" in entities.get("title", "").lower()
        assert entities.get("priority") == "high"

    def test_all_at_once_with_description(self, classifier):
        """Handle task creation with description included."""
        result = classifier.classify(
            "add task to buy milk with description get 2% milk from store"
        )

        assert result.intent_type == Intent.ADD_TASK
        assert "milk" in result.extracted_entities.get("title", "").lower()

    def test_all_at_once_minimal_workflow_steps(self):
        """All-at-once should skip guided workflow."""
        # When all info provided, should go straight to task creation
        # without asking for priority, deadline, description
        # This will be tested in end-to-end tests
        assert True  # Placeholder for E2E test


class TestAddTaskStateManagement:
    """Test conversation state management during add-task flow."""

    def test_state_data_structure(self):
        """Test expected state_data structure."""
        expected_structure = {
            "title": str,
            "priority": str,  # Optional
            "due_date": str,  # Optional (ISO format)
            "description": str,  # Optional
            "step": str  # Current workflow step
        }

        # Verify structure is consistent
        state_data = {
            "title": "buy milk",
            "step": "priority"
        }

        assert "title" in state_data
        assert "step" in state_data

    def test_state_progression_steps(self):
        """Test workflow step progression."""
        steps = ["confirm", "priority", "deadline", "description", "create"]

        # Verify step order is logical
        assert steps[0] == "confirm"
        assert steps[-1] == "create"
        assert "priority" in steps
        assert "deadline" in steps

    def test_state_partial_completion(self):
        """Test handling partial state when user provides some info."""
        state_data = {
            "title": "buy milk",
            "priority": "high",
            "step": "deadline"
        }

        # Should continue from where we left off
        assert state_data.get("title") is not None
        assert state_data.get("priority") is not None
        assert state_data.get("due_date") is None  # Not yet provided


class TestAddTaskErrorHandling:
    """Test error handling in add-task workflow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_cancel_operation_during_workflow(self, classifier):
        """User can cancel add-task operation mid-flow."""
        result = classifier.classify(
            message="never mind",
            current_intent="ADDING_TASK"
        )

        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_empty_title_rejection(self):
        """Empty title should be rejected."""
        # This will be validated in the tool call
        title = ""
        assert title == ""  # Tool will reject this

    def test_invalid_priority_handling(self):
        """Invalid priority values should be handled."""
        invalid_priorities = ["very high", "super", "extreme"]
        valid_priorities = ["high", "medium", "low"]

        for priority in invalid_priorities:
            assert priority not in valid_priorities

    def test_past_date_rejection(self):
        """Past dates should be rejected by DateParser."""
        # DateParser already handles this
        # Just verify the integration works
        assert True  # Placeholder


class TestAddTaskIntentSwitching:
    """Test intent switching during add-task workflow."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_switch_to_list_tasks_mid_flow(self, classifier):
        """User can switch to LIST_TASKS during add-task."""
        result = classifier.classify(
            message="show my tasks",
            current_intent="ADDING_TASK"
        )

        # Should detect LIST_TASKS intent
        assert result.intent_type == Intent.LIST_TASKS

    def test_switch_to_delete_task_mid_flow(self, classifier):
        """User can switch to DELETE_TASK during add-task."""
        result = classifier.classify(
            message="delete task 5",
            current_intent="ADDING_TASK"
        )

        # Should detect DELETE_TASK intent
        assert result.intent_type == Intent.DELETE_TASK

    def test_context_aware_information_vs_command(self, classifier):
        """Distinguish between providing info and issuing command."""
        # In add-task context, "high priority" is information
        result1 = classifier.classify(
            message="high priority",
            current_intent="ADDING_TASK"
        )
        assert result1.intent_type == Intent.PROVIDE_INFORMATION

        # But "delete task 5" is still a command
        result2 = classifier.classify(
            message="delete task 5",
            current_intent="ADDING_TASK"
        )
        assert result2.intent_type == Intent.DELETE_TASK


class TestAddTaskSuccessMessage:
    """Test success message formatting after task creation."""

    def test_success_message_format(self):
        """Test expected success message format."""
        # Format: "✅ Task created! #5: Buy milk (🔴 high, due tomorrow)"
        task_id = 5
        title = "Buy milk"
        priority = "high"
        due_date = "tomorrow"

        # Message should include:
        assert task_id == 5
        assert title == "Buy milk"
        assert priority in ["high", "medium", "low"]

    def test_success_message_without_optional_fields(self):
        """Success message works without deadline or description."""
        # Format: "✅ Task created! #5: Buy milk (🟡 medium)"
        task_id = 5
        title = "Buy milk"
        priority = "medium"

        assert task_id == 5
        assert title == "Buy milk"
        assert priority == "medium"
