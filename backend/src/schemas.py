"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class TaskCreate(BaseModel):
    """Request schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description"
    )
    priority: str = Field(
        default="medium",
        description="Task priority (high, medium, low)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date and time (optional)"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description length if provided."""
        if v and len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of allowed values."""
        allowed = ["high", "medium", "low"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}, got '{v}'")
        return v


class TaskUpdate(BaseModel):
    """Request schema for updating an existing task."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Updated task description"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Updated task priority (high, medium, low)"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Updated task due date and time (optional)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty if provided."""
        if v is not None and (not v or v.strip() == ""):
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority is one of allowed values if provided."""
        if v is not None:
            allowed = ["high", "medium", "low"]
            if v not in allowed:
                raise ValueError(f"Priority must be one of {allowed}, got '{v}'")
        return v


class TaskResponse(BaseModel):
    """Response schema for task data."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str = Field(default="medium", description="Task priority (high, medium, low)")
    due_date: Optional[datetime] = Field(default=None, description="Task due date and time")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(description="Overall system status")
    database: str = Field(description="Database connection status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(description="Health check timestamp")
    pool_status: str | None = Field(default=None, description="Database connection pool status")


# Authentication Schemas (Feature 2)

class SignupRequest(BaseModel):
    """Request schema for user registration."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User display name (optional)"
    )


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(BaseModel):
    """Response schema for user data (no password)."""
    
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiry in seconds")
    user: UserResponse = Field(description="Authenticated user data")

