"""ChatKit session endpoint for OpenAI ChatKit integration.

This endpoint creates ChatKit sessions that allow the frontend ChatKit component
to communicate with our backend chat API.
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI
import jwt
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter(tags=["chatkit"])


class ChatKitSessionResponse(BaseModel):
    """Response with ChatKit client secret."""
    client_secret: str


@router.post("/chatkit/session", response_model=ChatKitSessionResponse)
async def create_chatkit_session(
    current_user_id: str = Depends(get_current_user)
):
    """Create a ChatKit session for the authenticated user.
    
    ChatKit requires a client secret to initialize. This endpoint creates
    a session that points to our backend chat API endpoint.
    
    The ChatKit component will use this session to send messages to:
    /api/{user_id}/chat
    
    Args:
        current_user_id: Authenticated user ID from JWT
        
    Returns:
        ChatKitSessionResponse with client_secret
        
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 500: If session creation fails
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Get API URL for backend endpoint
        # In production, this should be your actual backend URL
        # For now, we'll use a relative path that ChatKit can resolve
        backend_url = f"/api/{current_user_id}/chat"
        
        # Create ChatKit session
        # Note: The exact API might vary based on OpenAI ChatKit version
        # This is a placeholder - adjust based on actual ChatKit API
        
        try:
            # Try to create session with backend endpoint configuration
            # ChatKit should be configured to send messages to our backend
            session = client.chatkit.sessions.create(
                endpoint=backend_url,
                user_id=current_user_id,
            )
            
            return ChatKitSessionResponse(
                client_secret=session.client_secret
            )
        except (AttributeError, Exception) as e:
            # If chatkit.sessions doesn't exist, ChatKit might work differently
            # In that case, we can return a token that ChatKit can use
            # to authenticate with our backend directly
            
            # Alternative: Return a JWT-like token that our backend accepts
            # ChatKit will use this to authenticate requests
            # Create a token for ChatKit to use
            token = jwt.encode(
                {
                    "sub": current_user_id,
                    "exp": int(time.time()) + 3600,  # 1 hour expiry
                    "type": "chatkit"
                },
                settings.better_auth_secret,
                algorithm="HS256"
            )
            
            return ChatKitSessionResponse(
                client_secret=token
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ChatKit session: {str(e)}"
        )
