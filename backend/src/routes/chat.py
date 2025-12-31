"""Chat API Routes.

Provides stateless chat endpoint for AI-powered task management conversations.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..auth.dependencies import get_current_user_id
from ..db import get_db
from ..services.conversation_service import ConversationService
from ..ai_agent.runner import run_agent, AgentResponse
from ..ai_agent.tools import register_tools
from ..mcp_tools.add_task import add_task, AddTaskParams
from ..mcp_tools.list_tasks import list_tasks, ListTasksParams
from ..mcp_tools.complete_task import complete_task, CompleteTaskParams
from ..mcp_tools.update_task import update_task, UpdateTaskParams
from ..mcp_tools.delete_task import delete_task, DeleteTaskParams
from ..utils.performance import log_execution_time, track_performance
import logging
import json
import time

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for chat endpoint.

    Attributes:
        conversation_id: Optional ID to resume existing conversation
        message: User's message
    """

    conversation_id: Optional[int] = Field(
        None,
        description="Conversation ID to resume (omit for new conversation)"
    )
    message: str = Field(
        ...,
        min_length=1,
        description="User's message"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Add task to buy milk"
            }
        }


class ChatResponse(BaseModel):
    """Response from chat endpoint.

    Attributes:
        conversation_id: ID of the conversation
        response: Assistant's natural language response
        tool_calls: List of tool calls made by the agent
    """

    conversation_id: int = Field(..., description="Conversation ID")
    response: str = Field(..., description="Assistant's response")
    tool_calls: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tool calls made during this turn"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "conversation_id": 42,
                "response": "I've added 'Buy milk' to your tasks.",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "params": {"title": "Buy milk"}
                    }
                ]
            }
        }


@router.post("/{user_id}/chat", response_model=ChatResponse)
@log_execution_time("chat_endpoint")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Process chat message and return AI assistant response.

    This endpoint:
    1. Validates user authentication and authorization
    2. Creates or resumes conversation
    3. Fetches conversation history
    4. Runs AI agent with user message
    5. Executes any tool calls (e.g., add_task)
    6. Stores messages in database
    7. Returns response with conversation context

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        current_user_id: Authenticated user ID from JWT
        db: Database session

    Returns:
        ChatResponse with assistant's response and metadata

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If path user_id doesn't match JWT user_id
        HTTPException 404: If conversation_id not found for user
        HTTPException 500: If internal error occurs

    Example:
        >>> # POST /api/user-123/chat
        >>> {
        ...     "message": "Add task to buy milk"
        ... }
        >>> # Response:
        >>> {
        ...     "conversation_id": 1,
        ...     "response": "I've added 'Buy milk' to your tasks.",
        ...     "tool_calls": [{"tool": "add_task", "params": {...}}]
        ... }
    """
    try:
        # Input sanitization (T181) - strip excessive whitespace, limit message length
        sanitized_message = request.message.strip()
        if len(sanitized_message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 10000 characters)"
            )
        request.message = sanitized_message

        # Structured logging with request context (T170)
        logger.info(
            "Chat request received",
            extra={
                "user_id": user_id,
                "conversation_id": request.conversation_id,
                "message_length": len(request.message),
                "has_conversation_id": request.conversation_id is not None
            }
        )

        # Validate path user_id matches JWT user_id (T060)
        if user_id != current_user_id:
            logger.warning(
                f"User isolation violation: path user_id={user_id}, "
                f"JWT user_id={current_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access chat for other users"
            )

        # Initialize conversation service
        conversation_service = ConversationService(db)

        # Create or resume conversation (T062)
        if request.conversation_id:
            # Resume existing conversation
            conversation = conversation_service.get_conversation(
                request.conversation_id,
                user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation {request.conversation_id} not found"
                )
            conversation_id = conversation.id
        else:
            # Create new conversation
            conversation = conversation_service.create_conversation(user_id)
            conversation_id = conversation.id

        logger.info(
            f"Processing chat for user {user_id}, "
            f"conversation {conversation_id}"
        )

        # Fetch conversation history (last 50 messages) (T063)
        history_messages = conversation_service.get_conversation_history(
            conversation_id,
            user_id,
            limit=50
        )

        # Convert to format expected by agent
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages
        ]

        # Initialize agent tools (T064)
        tools = register_tools()

        # Run AI agent (T065)
        agent_response = await run_agent(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history,
            tools=tools
        )

        # Execute tool calls if any
        executed_tools = []
        if hasattr(agent_response, 'tool_calls') and agent_response.tool_calls:
            for tool_call in agent_response.tool_calls:
                tool_name = tool_call.get('tool')
                tool_params = tool_call.get('params', {})

                if tool_name == 'add_task':
                    # Execute add_task tool
                    try:
                        params = AddTaskParams(
                            user_id=user_id,
                            title=tool_params.get('title'),
                            description=tool_params.get('description')
                        )
                        result = add_task(db, params)
                        executed_tools.append({
                            'tool': 'add_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'description': result.description,
                                'completed': result.completed,
                                'created_at': result.created_at.isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        # Continue even if tool fails

                elif tool_name == 'list_tasks':
                    # Execute list_tasks tool
                    try:
                        params = ListTasksParams(
                            user_id=user_id,
                            status=tool_params.get('status', 'all')
                        )
                        result = list_tasks(db, params)
                        executed_tools.append({
                            'tool': 'list_tasks',
                            'params': tool_params,
                            'result': {
                                'tasks': [
                                    {
                                        'task_id': task['task_id'],
                                        'title': task['title'],
                                        'description': task['description'],
                                        'completed': task['completed'],
                                        'created_at': task['created_at'].isoformat()
                                    }
                                    for task in result.tasks
                                ],
                                'count': result.count
                            }
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        # Continue even if tool fails

                elif tool_name == 'complete_task':
                    # Execute complete_task tool
                    try:
                        params = CompleteTaskParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id')
                        )
                        result = complete_task(db, params)
                        executed_tools.append({
                            'tool': 'complete_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'description': result.description,
                                'completed': result.completed,
                                'updated_at': result.updated_at.isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        # Continue even if tool fails

                elif tool_name == 'update_task':
                    # Execute update_task tool
                    try:
                        params = UpdateTaskParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id'),
                            title=tool_params.get('title'),
                            description=tool_params.get('description')
                        )
                        result = update_task(db, params)
                        executed_tools.append({
                            'tool': 'update_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'description': result.description,
                                'completed': result.completed,
                                'updated_at': result.updated_at.isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        # Continue even if tool fails

                elif tool_name == 'delete_task':
                    # Execute delete_task tool
                    try:
                        params = DeleteTaskParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id')
                        )
                        result = delete_task(db, params)
                        executed_tools.append({
                            'tool': 'delete_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'success': result.success
                            }
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}", exc_info=True)
                        # Continue even if tool fails

        # Store user message in database (T066)
        conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=request.message
        )

        # Store assistant response in database (T066)
        conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=agent_response.response
        )

        # Update conversation timestamp (T067)
        conversation_service.update_conversation_timestamp(conversation_id)

        # Return response (T068)
        return ChatResponse(
            conversation_id=conversation_id,
            response=agent_response.response,
            tool_calls=executed_tools
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Internal errors (T069)
        logger.error(
            f"Chat endpoint failed for user {user_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )
