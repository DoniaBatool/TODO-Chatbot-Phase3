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

