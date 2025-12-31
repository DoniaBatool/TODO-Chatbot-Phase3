"""Unit tests for database models."""

import pytest
from datetime import datetime
from src.models import Conversation, Message


class TestConversationModel:
    """Tests for Conversation model."""

    def test_conversation_creation(self):
        """Test creating a conversation with required fields."""
        conversation = Conversation(
            user_id="test-user-123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert conversation.user_id == "test-user-123"
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    def test_conversation_default_timestamps(self):
        """Test that timestamps are auto-generated."""
        conversation = Conversation(user_id="test-user-123")
        # Timestamps should be set by default_factory
        assert conversation.created_at is not None
        assert conversation.updated_at is not None


class TestMessageModel:
    """Tests for Message model."""

    def test_message_creation_user_role(self):
        """Test creating a message with user role."""
        message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="user",
            content="Add task to buy milk",
            created_at=datetime.utcnow()
        )
        assert message.conversation_id == 1
        assert message.user_id == "test-user-123"
        assert message.role == "user"
        assert message.content == "Add task to buy milk"

    def test_message_creation_assistant_role(self):
        """Test creating a message with assistant role."""
        message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="assistant",
            content="I've added 'Buy milk' to your tasks.",
            created_at=datetime.utcnow()
        )
        assert message.role == "assistant"
        assert "Buy milk" in message.content

    def test_message_role_validation(self):
        """Test that invalid roles raise ValueError."""
        message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="invalid",
            content="Test content"
        )
        with pytest.raises(ValueError, match="Role must be 'user' or 'assistant'"):
            message.validate_role()

    def test_message_valid_role_no_error(self):
        """Test that valid roles pass validation."""
        user_message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="user",
            content="Test"
        )
        assistant_message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="assistant",
            content="Test"
        )
        # Should not raise
        user_message.validate_role()
        assistant_message.validate_role()

    def test_message_default_timestamp(self):
        """Test that created_at is auto-generated."""
        message = Message(
            conversation_id=1,
            user_id="test-user-123",
            role="user",
            content="Test"
        )
        assert message.created_at is not None
