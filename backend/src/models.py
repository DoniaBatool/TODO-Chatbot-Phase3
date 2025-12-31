"""SQLModel database models for User and Task entities."""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """
    User account with authentication support.
    
    Supports both:
    - Backend email/password auth (password_hash field)
    - Better Auth providers (password_hash can be null for OAuth users)
    """
    
    __tablename__ = "users"
    
    id: str = Field(
        primary_key=True,
        description="UUID (generated on signup or from Better Auth)"
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (stored in lowercase)"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name"
    )
    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        description="bcrypt hashed password (null for OAuth users)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    
    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    messages: List["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Task(SQLModel, table=True):
    """
    Todo task belonging to a user.
    
    Supports full CRUD operations via REST API.
    """
    
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing task ID"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID"
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")


class Conversation(SQLModel, table=True):
    """
    Chat conversation between user and AI assistant.

    Stores conversation metadata and timestamps for stateless architecture.
    Messages are stored separately in the Message table.
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing conversation ID"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Conversation creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last message timestamp"
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """
    Individual message within a conversation.

    Can be from user (role='user') or AI assistant (role='assistant').
    Messages are ordered by created_at within a conversation.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing message ID"
    )
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation ID"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="Owner user ID (matches conversation.user_id)"
    )
    role: str = Field(
        max_length=20,
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        description="Message text content"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message timestamp"
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
    user: Optional[User] = Relationship(back_populates="messages")

    def validate_role(self) -> None:
        """Validate that role is either 'user' or 'assistant'."""
        if self.role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")

