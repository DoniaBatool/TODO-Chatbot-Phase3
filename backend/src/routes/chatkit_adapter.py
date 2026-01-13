"""ChatKit Protocol Adapter for Custom Backend.

This endpoint adapts ChatKit protocol requests to our existing chat endpoint format.
ChatKit sends requests in its own protocol, but our backend uses a simpler REST format.
This adapter converts between the two.
"""

import json
import logging
from typing import Any, Dict
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..db import get_session
from .chat import chat, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chatkit"])


@router.post("/chatkit")
async def chatkit_adapter(
    request: Request,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Adapter endpoint that converts ChatKit protocol to our chat endpoint format.
    
    ChatKit sends requests in its own protocol format. This endpoint:
    1. Receives ChatKit protocol requests
    2. Extracts user message and thread/conversation info
    3. Converts to our ChatRequest format
    4. Calls our existing chat endpoint logic
    5. Converts response back to ChatKit format
    
    Args:
        request: FastAPI request object
        current_user_id: Authenticated user ID from JWT
        db: Database session
        
    Returns:
        ChatKit-compatible response (streaming or JSON)
    """
    try:
        # Read request body
        body = await request.body()
        
        # Try to parse as JSON
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            # If not JSON, might be ChatKit protocol format
            payload = {"raw": body.decode('utf-8')}
        
        logger.info(
            f"ChatKit request received for user {current_user_id}",
            extra={"payload_keys": list(payload.keys()) if isinstance(payload, dict) else []}
        )
        
        # Extract message from ChatKit payload
        # ChatKit format varies, but typically has messages array or text field
        message_text = None
        conversation_id = None
        
        if isinstance(payload, dict):
            # Try different ChatKit payload formats
            if "messages" in payload and isinstance(payload["messages"], list):
                # ChatKit messages array format
                for msg in payload["messages"]:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        message_text = msg.get("content") or msg.get("text")
                        break
            elif "text" in payload:
                message_text = payload["text"]
            elif "message" in payload:
                message_text = payload["message"]
            elif "content" in payload:
                message_text = payload["content"]
            
            # Extract thread/conversation ID if present
            if "thread_id" in payload:
                try:
                    conversation_id = int(payload["thread_id"])
                except (ValueError, TypeError):
                    pass
            elif "conversation_id" in payload:
                try:
                    conversation_id = int(payload["conversation_id"])
                except (ValueError, TypeError):
                    pass
        
        # If no message found, return error
        if not message_text:
            logger.warning(
                f"Could not extract message from ChatKit payload",
                extra={"payload": str(payload)[:200]}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message not found in request"
            )
        
        # Create ChatRequest in our format
        chat_request = ChatRequest(
            message=message_text,
            conversation_id=conversation_id
        )
        
        # Call our existing chat endpoint logic
        # We need to call it directly since it's an async function
        chat_response = await chat(
            user_id=current_user_id,
            request=chat_request,
            current_user_id=current_user_id,
            db=db
        )
        
        # Convert our ChatResponse to ChatKit format
        # ChatKit expects streaming format (SSE) or specific JSON structure
        # For now, return JSON format that ChatKit can understand
        
        # ChatKit expects events in SSE format, but we'll return JSON for simplicity
        # Format: { "messages": [...], "thread_id": "...", ... }
        chatkit_response = {
            "messages": [
                {
                    "role": "assistant",
                    "content": chat_response.response,
                    "id": f"msg_{chat_response.conversation_id}",
                    "content_type": "output_text"
                }
            ],
            "thread_id": str(chat_response.conversation_id),
        }
        
        # Add tool calls if any
        if chat_response.tool_calls:
            chatkit_response["tool_calls"] = chat_response.tool_calls
        
        logger.info(
            f"ChatKit response prepared for user {current_user_id}",
            extra={"conversation_id": chat_response.conversation_id}
        )
        
        return JSONResponse(
            content=chatkit_response,
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"ChatKit adapter error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process ChatKit request: {str(e)}"
        )
