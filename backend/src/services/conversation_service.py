"""Conversation Service for managing chat conversations and messages.

This service handles CRUD operations for conversations and messages,
enforcing user isolation and stateless architecture principles.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select
from sqlalchemy import delete

from ..models import Conversation, Message
from ..utils.performance import log_execution_time


class ConversationService:
    """Service for managing conversations and messages."""

    def __init__(self, db: Session):
        """Initialize service with database session.

        Args:
            db: SQLModel database session
        """
        self.db = db

    @log_execution_time("create_conversation")
    def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for a user.

        Args:
            user_id: ID of the user creating the conversation

        Returns:
            Created Conversation object with ID

        Example:
            >>> service = ConversationService(db)
            >>> conversation = service.create_conversation("user-123")
            >>> assert conversation.id is not None
        """
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(
        self, conversation_id: int, user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation by ID with user isolation.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the authenticated user

        Returns:
            Conversation object if found and owned by user, None otherwise

        Security:
            Only returns conversation if user_id matches owner.
            Returns None (not 403) to prevent conversation enumeration.

        Example:
            >>> conversation = service.get_conversation(123, "user-123")
            >>> if conversation:
            ...     print(f"Found conversation {conversation.id}")
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.db.exec(statement).first()
        return conversation

    @log_execution_time("get_conversation_history")
    def get_conversation_history(
        self, conversation_id: int, user_id: str, limit: int = 50
    ) -> List[Message]:
        """Get conversation message history with user isolation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            limit: Maximum number of messages to return (default: 50)

        Returns:
            List of Message objects ordered by created_at ASC (chronological)
            Returns empty list if conversation doesn't exist or user doesn't own it

        Performance:
            - Limited to last N messages for performance
            - Uses index on (conversation_id, created_at)
            - Returns in chronological order (oldest first)

        Example:
            >>> messages = service.get_conversation_history(123, "user-123", limit=50)
            >>> for msg in messages:
            ...     print(f"{msg.role}: {msg.content}")
        """
        # First verify user owns this conversation (security check)
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        # Fetch last N messages in reverse chronological order
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = self.db.exec(statement).all()

        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))

    @log_execution_time("add_message")
    def add_message(
        self, conversation_id: int, user_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (owner of conversation)
            role: Message role ('user' or 'assistant')
            content: Message text content

        Returns:
            Created Message object with ID

        Raises:
            ValueError: If role is not 'user' or 'assistant'

        Security:
            Assumes conversation ownership has been verified before calling.
            For production, consider adding ownership check here too.

        Example:
            >>> message = service.add_message(
            ...     conversation_id=123,
            ...     user_id="user-123",
            ...     role="user",
            ...     content="Add task to buy milk"
            ... )
            >>> assert message.id is not None
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            created_at=datetime.utcnow()
        )

        # Validate role
        message.validate_role()

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def update_conversation_timestamp(self, conversation_id: int) -> None:
        """Update conversation's updated_at timestamp.

        Args:
            conversation_id: ID of the conversation to update

        Note:
            This is called after adding messages to track last activity.
            Uses direct UPDATE query for efficiency.

        Example:
            >>> service.update_conversation_timestamp(123)
        """
        statement = select(Conversation).where(Conversation.id == conversation_id)
        conversation = self.db.exec(statement).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.db.add(conversation)
            self.db.commit()

    @log_execution_time("get_user_conversations")
    def get_user_conversations(self, user_id: str) -> List[dict]:
        """Get all conversations for a user with message count.

        Args:
            user_id: ID of the authenticated user

        Returns:
            List of conversation dictionaries with metadata and message count

        Example:
            >>> conversations = service.get_user_conversations("user-123")
            >>> for conv in conversations:
            ...     print(f"{conv['title']} - {conv['message_count']} messages")
        """
        from sqlalchemy import func

        # Get conversations with message count
        statement = (
            select(
                Conversation.id,
                Conversation.user_id,
                Conversation.created_at,
                Conversation.updated_at,
                func.count(Message.id).label('message_count')
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
        )

        results = self.db.exec(statement).all()

        conversations = []
        for row in results:
            # Get first user message as title
            first_message_statement = (
                select(Message.content)
                .where(
                    Message.conversation_id == row.id,
                    Message.role == 'user'
                )
                .order_by(Message.created_at.asc())
                .limit(1)
            )
            first_message = self.db.exec(first_message_statement).first()
            title = first_message[:50] if first_message else "New Chat"

            conversations.append({
                'id': row.id,
                'title': title,
                'created_at': row.created_at.isoformat(),
                'updated_at': row.updated_at.isoformat(),
                'message_count': row.message_count or 0
            })

        return conversations

    @log_execution_time("get_latest_conversation")
    def get_latest_conversation(self, user_id: str) -> dict:
        """Get user's most recent conversation with messages.

        Args:
            user_id: ID of the authenticated user

        Returns:
            Dictionary with conversation_id and messages list

        Example:
            >>> latest = service.get_latest_conversation("user-123")
            >>> print(f"Conversation {latest['conversation_id']}")
        """
        # Get latest conversation
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conversation = self.db.exec(statement).first()

        if not conversation:
            return {'conversation_id': None, 'messages': []}

        # Get messages for this conversation
        messages = self.get_conversation_history(conversation.id, user_id)

        return {
            'conversation_id': conversation.id,
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }

    @log_execution_time("delete_conversation")
    def delete_conversation(self, conversation_id: int, user_id: str) -> bool:
        """Delete a single conversation (and its messages) for a user."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        # Delete messages first (defensive), then conversation
        try:
            self.db.exec(
                delete(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.user_id == user_id
                )
            )
            self.db.exec(
                delete(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    @log_execution_time("delete_all_conversations")
    def delete_all_conversations(self, user_id: str) -> int:
        """Delete all conversations (and messages) for a user. Returns count deleted."""
        # Fetch IDs first to return count
        statement = select(Conversation.id).where(Conversation.user_id == user_id)
        ids = [row for row in self.db.exec(statement).all()]
        if not ids:
            return 0

        try:
            self.db.exec(delete(Message).where(Message.user_id == user_id))
            self.db.exec(delete(Conversation).where(Conversation.user_id == user_id))
            self.db.commit()
            return len(ids)
        except Exception:
            self.db.rollback()
            raise
