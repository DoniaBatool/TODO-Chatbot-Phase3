"""Conversation API routes for listing, retrieving, and deleting conversations."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..auth.dependencies import get_current_user
from ..services.conversation_service import ConversationService


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get all conversations for the current user.

    Returns:
        List of conversations with metadata and message count

    Security:
        - Requires valid JWT token
        - User isolation enforced (only returns user's conversations)
    """
    user_id = current_user
    service = ConversationService(db)
    conversations = service.get_user_conversations(user_id)

    return {"conversations": conversations}


@router.get("/latest")
async def get_latest_conversation(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get the most recent conversation with its messages.

    Returns:
        Dictionary with conversation_id and messages list

    Security:
        - Requires valid JWT token
        - User isolation enforced
    """
    user_id = current_user
    service = ConversationService(db)
    conversation = service.get_latest_conversation(user_id)

    return conversation


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get all messages for a specific conversation.

    Args:
        conversation_id: ID of the conversation

    Returns:
        Dictionary with conversation_id and messages list

    Security:
        - Requires valid JWT token
        - User isolation enforced (404 if conversation doesn't belong to user)
    """
    user_id = current_user
    service = ConversationService(db)

    # Verify user owns this conversation
    conversation = service.get_conversation(conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    messages = service.get_conversation_history(conversation_id, user_id)

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.role,  # For compatibility with frontend
                "role": msg.role,
                "message": msg.content,  # For compatibility with frontend
                "content": msg.content,
                "tool_calls": msg.tool_calls if msg.tool_calls else None,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete a single conversation for the current user."""
    user_id = current_user
    service = ConversationService(db)

    ok = service.delete_conversation(conversation_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "deleted_conversation_id": conversation_id}


@router.delete("")
async def delete_all_conversations(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete all conversations for the current user."""
    user_id = current_user
    service = ConversationService(db)

    deleted_count = service.delete_all_conversations(user_id)
    return {"success": True, "deleted_count": deleted_count}
