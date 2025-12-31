"""Unit tests for ConversationService."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.services.conversation_service import ConversationService
from src.models import Conversation, Message


class TestConversationService:
    """Tests for ConversationService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        """Create ConversationService with mock database."""
        return ConversationService(mock_db)

    def test_create_conversation(self, service, mock_db):
        """Test creating a new conversation."""
        # Arrange
        user_id = "test-user-123"
        mock_conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 1))

        # Act
        conversation = service.create_conversation(user_id)

        # Assert
        assert mock_db.add.called
        assert mock_db.commit.called
        assert conversation.user_id == user_id

    def test_get_conversation_found(self, service, mock_db):
        """Test getting an existing conversation."""
        # Arrange
        conversation_id = 1
        user_id = "test-user-123"
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_conversation
        mock_db.exec.return_value = mock_result

        # Act
        result = service.get_conversation(conversation_id, user_id)

        # Assert
        assert result is not None
        assert result.id == conversation_id
        assert result.user_id == user_id

    def test_get_conversation_not_found(self, service, mock_db):
        """Test getting a non-existent conversation."""
        # Arrange
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        # Act
        result = service.get_conversation(999, "test-user-123")

        # Assert
        assert result is None

    def test_get_conversation_wrong_user(self, service, mock_db):
        """Test that users cannot access others' conversations."""
        # Arrange
        mock_result = Mock()
        mock_result.first.return_value = None  # Query with wrong user_id returns nothing
        mock_db.exec.return_value = mock_result

        # Act
        result = service.get_conversation(1, "wrong-user-id")

        # Assert
        assert result is None

    def test_get_conversation_history_empty(self, service, mock_db):
        """Test getting history for non-existent conversation."""
        # Arrange
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_db.exec.return_value = mock_result

        # Act
        messages = service.get_conversation_history(999, "test-user-123")

        # Assert
        assert messages == []

    def test_get_conversation_history_with_messages(self, service, mock_db):
        """Test getting conversation history with messages."""
        # Arrange
        conversation_id = 1
        user_id = "test-user-123"

        # Mock conversation exists
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Mock messages (returned in DESC order, will be reversed)
        mock_messages = [
            Message(
                id=3,
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content="Done!",
                created_at=datetime.utcnow()
            ),
            Message(
                id=2,
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content="Add task",
                created_at=datetime.utcnow()
            ),
        ]

        # First call: get_conversation, second call: get messages
        mock_result_conv = Mock()
        mock_result_conv.first.return_value = mock_conversation
        mock_result_msgs = Mock()
        mock_result_msgs.all.return_value = mock_messages

        mock_db.exec.side_effect = [mock_result_conv, mock_result_msgs]

        # Act
        messages = service.get_conversation_history(conversation_id, user_id)

        # Assert
        assert len(messages) == 2
        # Should be reversed to chronological order
        assert messages[0].id == 2  # Oldest first
        assert messages[1].id == 3

    def test_add_message_user_role(self, service, mock_db):
        """Test adding a user message."""
        # Arrange
        conversation_id = 1
        user_id = "test-user-123"
        role = "user"
        content = "Add task to buy milk"

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 10))

        # Act
        message = service.add_message(conversation_id, user_id, role, content)

        # Assert
        assert mock_db.add.called
        assert mock_db.commit.called
        assert message.role == role
        assert message.content == content

    def test_add_message_assistant_role(self, service, mock_db):
        """Test adding an assistant message."""
        # Arrange
        conversation_id = 1
        user_id = "test-user-123"
        role = "assistant"
        content = "I've added 'Buy milk' to your tasks."

        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 11))

        # Act
        message = service.add_message(conversation_id, user_id, role, content)

        # Assert
        assert message.role == role
        assert message.content == content

    def test_add_message_invalid_role(self, service, mock_db):
        """Test that invalid role raises ValueError."""
        # Arrange
        conversation_id = 1
        user_id = "test-user-123"
        role = "invalid"
        content = "Test"

        # Act & Assert
        with pytest.raises(ValueError, match="Role must be 'user' or 'assistant'"):
            service.add_message(conversation_id, user_id, role, content)

    def test_update_conversation_timestamp(self, service, mock_db):
        """Test updating conversation timestamp."""
        # Arrange
        conversation_id = 1
        old_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_conversation = Conversation(
            id=conversation_id,
            user_id="test-user-123",
            created_at=old_time,
            updated_at=old_time
        )

        mock_result = Mock()
        mock_result.first.return_value = mock_conversation
        mock_db.exec.return_value = mock_result

        # Act
        service.update_conversation_timestamp(conversation_id)

        # Assert
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_conversation.updated_at > old_time


class TestConversationServiceIntegration:
    """Integration tests for ConversationService with full flow."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session for integration testing."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        """Create ConversationService with mock database."""
        return ConversationService(mock_db)

    def test_full_conversation_flow(self, service, mock_db):
        """Integration test: create conversation → add messages → fetch history → verify order.

        This test simulates a complete conversation flow:
        1. User creates a new conversation
        2. User sends a message
        3. Assistant responds
        4. User sends another message
        5. Assistant responds again
        6. Fetch history and verify chronological order
        """
        # Arrange
        user_id = "integration-test-user"

        # Mock conversation creation
        mock_conversation = Conversation(
            id=100,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 100))

        # Step 1: Create conversation
        conversation = service.create_conversation(user_id)
        assert conversation.user_id == user_id
        conversation_id = 100  # Mocked ID

        # Mock message creation with sequential IDs
        message_ids = [1, 2, 3, 4]
        mock_db.refresh = Mock(
            side_effect=lambda obj: setattr(
                obj, 'id', message_ids.pop(0) if message_ids else 999
            )
        )

        # Step 2: Add first user message
        msg1 = service.add_message(
            conversation_id,
            user_id,
            "user",
            "Add task to buy milk"
        )
        assert msg1.role == "user"
        assert msg1.content == "Add task to buy milk"

        # Step 3: Add first assistant response
        msg2 = service.add_message(
            conversation_id,
            user_id,
            "assistant",
            "I've added 'Buy milk' to your tasks."
        )
        assert msg2.role == "assistant"

        # Step 4: Add second user message
        msg3 = service.add_message(
            conversation_id,
            user_id,
            "user",
            "Show my tasks"
        )
        assert msg3.role == "user"

        # Step 5: Add second assistant response
        msg4 = service.add_message(
            conversation_id,
            user_id,
            "assistant",
            "You have 1 task: 1. Buy milk (pending)"
        )
        assert msg4.role == "assistant"

        # Step 6: Fetch conversation history
        # Mock the history retrieval
        mock_messages = [
            Message(
                id=4,
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content="You have 1 task: 1. Buy milk (pending)",
                created_at=datetime.utcnow()
            ),
            Message(
                id=3,
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content="Show my tasks",
                created_at=datetime.utcnow()
            ),
            Message(
                id=2,
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content="I've added 'Buy milk' to your tasks.",
                created_at=datetime.utcnow()
            ),
            Message(
                id=1,
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content="Add task to buy milk",
                created_at=datetime.utcnow()
            ),
        ]

        # Mock conversation and messages retrieval
        mock_result_conv = Mock()
        mock_result_conv.first.return_value = mock_conversation
        mock_result_msgs = Mock()
        mock_result_msgs.all.return_value = mock_messages

        mock_db.exec.side_effect = [mock_result_conv, mock_result_msgs]

        # Fetch history
        history = service.get_conversation_history(conversation_id, user_id, limit=50)

        # Step 7: Verify chronological order (oldest to newest)
        assert len(history) == 4
        assert history[0].id == 1
        assert history[0].role == "user"
        assert history[0].content == "Add task to buy milk"

        assert history[1].id == 2
        assert history[1].role == "assistant"
        assert history[1].content == "I've added 'Buy milk' to your tasks."

        assert history[2].id == 3
        assert history[2].role == "user"
        assert history[2].content == "Show my tasks"

        assert history[3].id == 4
        assert history[3].role == "assistant"
        assert history[3].content == "You have 1 task: 1. Buy milk (pending)"

        # Verify alternating user/assistant pattern
        for i in range(len(history)):
            expected_role = "user" if i % 2 == 0 else "assistant"
            assert history[i].role == expected_role, \
                f"Message {i} should be from {expected_role}, got {history[i].role}"
