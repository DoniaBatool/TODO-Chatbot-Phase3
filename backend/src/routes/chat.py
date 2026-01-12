"""Chat API Routes.

Provides stateless chat endpoint for AI-powered task management conversations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..db import get_session
from ..services.conversation_service import ConversationService
from ..ai_agent.runner import run_agent, AgentResponse
from ..ai_agent.tools import register_tools
from ..ai_agent.intent_detector import detect_user_intent
from ..ai_agent.utils import parse_natural_date
from ..mcp_tools.add_task import add_task, AddTaskParams
from ..mcp_tools.list_tasks import list_tasks, ListTasksParams
from ..mcp_tools.complete_task import complete_task, CompleteTaskParams
from ..mcp_tools.update_task import update_task, UpdateTaskParams
from ..mcp_tools.delete_task import delete_task, DeleteTaskParams
from ..mcp_tools.find_task import find_task, FindTaskParams
from ..utils.performance import log_execution_time, track_performance
import logging
import json
import time

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.get("/conversations/latest")
async def get_latest_conversation(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get user's most recent conversation with messages.

    Args:
        current_user_id: Authenticated user ID from JWT
        db: Database session

    Returns:
        Latest conversation with its messages, or null if no conversations exist

    Example:
        >>> # GET /api/conversations/latest
        >>> {
        ...     "conversation_id": 5,
        ...     "created_at": "2026-01-01T10:00:00",
        ...     "messages": [...]
        ... }
    """
    try:
        from ..models import Conversation
        from sqlmodel import select, desc

        # Get user's most recent conversation
        statement = (
            select(Conversation)
            .where(Conversation.user_id == current_user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(1)
        )
        conversation = db.exec(statement).first()

        if not conversation:
            return {"conversation_id": None, "messages": []}

        # Fetch messages for this conversation
        conversation_service = ConversationService(db)
        messages = conversation_service.get_conversation_history(
            conversation.id,
            current_user_id,
            limit=100
        )

        return {
            "conversation_id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }

    except Exception as e:
        logger.error(
            f"Failed to fetch latest conversation: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest conversation"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get all messages for a conversation.

    Args:
        conversation_id: ID of the conversation
        current_user_id: Authenticated user ID from JWT
        db: Database session

    Returns:
        List of messages with role, content, and timestamp

    Raises:
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 404: If conversation not found
    """
    try:
        conversation_service = ConversationService(db)

        # Get conversation to verify ownership
        conversation = conversation_service.get_conversation(
            conversation_id,
            current_user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        # Fetch messages
        messages = conversation_service.get_conversation_history(
            conversation_id,
            current_user_id,
            limit=100
        )

        return {
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to fetch conversation messages: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation history"
        )


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
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_session)
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

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # INTENT DETECTION MIDDLEWARE - FORCED TOOL EXECUTION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Detect user intent BEFORE calling AI agent
        # If intent detected with params, FORCE tool execution
        # This bypasses unreliable AI system prompt interpretation

        detected_intent = detect_user_intent(request.message, conversation_history)
        forced_tool_calls = []

        if detected_intent:
            logger.info(
                f"Intent detected: {detected_intent}",
                extra={"user_id": user_id, "intent": str(detected_intent)}
            )

            # Check if confirmation is needed
            # If needs_confirmation=True, BYPASS AI and ask confirmation ourselves
            # If needs_confirmation=False, execute tool immediately
            if detected_intent.needs_confirmation:
                logger.info(
                    f"Intent needs confirmation - generating confirmation question",
                    extra={"user_id": user_id, "operation": detected_intent.operation}
                )

                # BYPASS AI AGENT - Generate confirmation question ourselves
                # First, get task details if we have task_id
                task_details = ""
                if detected_intent.task_id:
                    try:
                        # Get task details to show in confirmation
                        list_result = list_tasks(db, ListTasksParams(user_id=user_id, status="all"))
                        for task in list_result.tasks:
                            if task['task_id'] == detected_intent.task_id:
                                title = task['title']
                                priority = task.get('priority', 'medium')
                                task_details = f" '{title}' ({priority} priority)"
                                break
                    except:
                        pass

                # Generate confirmation message based on operation
                if detected_intent.operation == "delete":
                    confirmation_msg = f"🗑️ Kya aap sure hain k task{task_details} delete karna hai? (Are you sure you want to delete this task?)\n\nReply 'yes' to confirm or 'no' to cancel."
                elif detected_intent.operation == "complete":
                    confirmation_msg = f"✅ Task{task_details} ko complete mark kar doon? (Mark this task as complete?)\n\nReply 'yes' to confirm or 'no' to cancel."
                elif detected_intent.operation == "incomplete":
                    confirmation_msg = f"⏳ Task{task_details} ko incomplete mark kar doon? (Mark this task as incomplete?)\n\nReply 'yes' to confirm or 'no' to cancel."
                elif detected_intent.operation == "update":
                    confirmation_msg = f"📝 Task{task_details} update kar doon? (Update this task?)\n\nReply 'yes' to confirm or 'no' to cancel."
                elif detected_intent.operation == "update_ask":
                    # User wants to update but didn't provide details - ask what to update
                    confirmation_msg = f"📝 Task{task_details} mein kya update karna hai? (What do you want to update?)\n\nYou can update:\n• Title\n• Priority (high/medium/low)\n• Deadline/due date\n• Description\n\nTell me what you want to change!"
                else:
                    confirmation_msg = "Kya aap sure hain? (Are you sure?)\n\nReply 'yes' to confirm or 'no' to cancel."

                # Store messages in database
                conversation_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="user",
                    content=request.message
                )
                conversation_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=confirmation_msg
                )
                conversation_service.update_conversation_timestamp(conversation_id)

                # Return confirmation question immediately WITHOUT calling AI
                return ChatResponse(
                    conversation_id=conversation_id,
                    response=confirmation_msg,
                    tool_calls=[]
                )
            else:
                # User confirmed OR provided all details - FORCE execution
                logger.info(
                    f"Intent confirmed - forcing tool execution",
                    extra={"user_id": user_id, "operation": detected_intent.operation}
                )

            # Handle UPDATE intent (with full params or after confirmation)
            if detected_intent.operation == "update" and detected_intent.params and not detected_intent.needs_confirmation:
                # User provided update details - FORCE execution
                task_id = detected_intent.task_id

                # If task_title provided instead of ID, find it first
                if not task_id and detected_intent.task_title:
                    try:
                        find_params = FindTaskParams(
                            user_id=user_id,
                            title=detected_intent.task_title
                        )
                        find_result = find_task(db, find_params)
                        if find_result:
                            task_id = find_result.task_id
                    except Exception as e:
                        logger.error(f"Failed to find task: {e}")

                if task_id:
                    # Build update params - only include fields that were actually provided
                    update_params = {'task_id': task_id}

                    # Add title if provided
                    if 'title' in detected_intent.params and detected_intent.params['title'] is not None:
                        update_params['title'] = detected_intent.params['title']

                    # Add description if provided
                    if 'description' in detected_intent.params and detected_intent.params['description'] is not None:
                        update_params['description'] = detected_intent.params['description']

                    # Add priority if provided
                    if 'priority' in detected_intent.params and detected_intent.params['priority'] is not None:
                        update_params['priority'] = detected_intent.params['priority']

                    # Handle due_date - parse if provided
                    if 'due_date' in detected_intent.params:
                        due_date_str = detected_intent.params['due_date']
                        if due_date_str is None:
                            # Explicitly remove deadline
                            update_params['due_date'] = None
                        else:
                            # Parse natural language date
                            due_date = parse_natural_date(due_date_str)
                            if due_date:
                                update_params['due_date'] = due_date.isoformat()

                    # FORCE update_task execution
                    forced_tool_calls.append({
                        'tool': 'update_task',
                        'params': update_params
                    })

                    logger.info(
                        f"FORCED UPDATE: task_id={task_id}, params={detected_intent.params}",
                        extra={"user_id": user_id, "task_id": task_id}
                    )

            # Handle DELETE intent (after confirmation)
            elif detected_intent.operation == "delete" and not detected_intent.needs_confirmation:
                task_id = detected_intent.task_id

                # If task_title provided, find it first
                if not task_id and detected_intent.task_title:
                    try:
                        find_params = FindTaskParams(
                            user_id=user_id,
                            title=detected_intent.task_title
                        )
                        find_result = find_task(db, find_params)
                        if find_result:
                            task_id = find_result.task_id
                    except Exception as e:
                        logger.error(f"Failed to find task: {e}")

                if task_id:
                    # FORCE delete_task execution
                    forced_tool_calls.append({
                        'tool': 'delete_task',
                        'params': {'task_id': task_id}
                    })

                    logger.info(
                        f"FORCED DELETE: task_id={task_id}",
                        extra={"user_id": user_id, "task_id": task_id}
                    )

            # Handle COMPLETE intent (after confirmation)
            elif detected_intent.operation == "complete" and not detected_intent.needs_confirmation:
                task_id = detected_intent.task_id

                # If task_title provided, find it first
                if not task_id and detected_intent.task_title:
                    try:
                        find_params = FindTaskParams(
                            user_id=user_id,
                            title=detected_intent.task_title
                        )
                        find_result = find_task(db, find_params)
                        if find_result:
                            task_id = find_result.task_id
                    except Exception as e:
                        logger.error(f"Failed to find task: {e}")

                if task_id:
                    # FORCE complete_task execution
                    forced_tool_calls.append({
                        'tool': 'complete_task',
                        'params': {'task_id': task_id}
                    })

                    logger.info(
                        f"FORCED COMPLETE: task_id={task_id}",
                        extra={"user_id": user_id, "task_id": task_id}
                    )

            # Handle INCOMPLETE intent (mark as not done/pending)
            elif detected_intent.operation == "incomplete" and not detected_intent.needs_confirmation:
                task_id = detected_intent.task_id

                # If task_title provided, find it first
                if not task_id and detected_intent.task_title:
                    try:
                        find_params = FindTaskParams(
                            user_id=user_id,
                            title=detected_intent.task_title
                        )
                        find_result = find_task(db, find_params)
                        if find_result:
                            task_id = find_result.task_id
                    except Exception as e:
                        logger.error(f"Failed to find task: {e}")

                if task_id:
                    # FORCE update_task execution with completed=False
                    forced_tool_calls.append({
                        'tool': 'update_task',
                        'params': {
                            'task_id': task_id,
                            'completed': False
                        }
                    })

                    logger.info(
                        f"FORCED INCOMPLETE: task_id={task_id}",
                        extra={"user_id": user_id, "task_id": task_id}
                    )

        # Initialize agent tools (T064)
        tools = register_tools()

        # Run AI agent (T065)
        # If forced tool calls exist, we still call AI for conversational response
        agent_response = await run_agent(
            user_id=user_id,
            message=request.message,
            conversation_history=conversation_history,
            tools=tools
        )

        # Execute tool calls if any
        # PRIORITY: Forced tool calls execute FIRST, then AI-suggested tools
        executed_tools = []
        seen_tool_calls = set()  # Track tool call signatures for deduplication

        # STEP 1: Execute FORCED tool calls (from intent detector)
        all_tool_calls = forced_tool_calls + (agent_response.tool_calls if hasattr(agent_response, 'tool_calls') and agent_response.tool_calls else [])

        if all_tool_calls:
            for tool_call in all_tool_calls:
                tool_name = tool_call.get('tool')
                tool_params = tool_call.get('params', {})

                # Create signature for deduplication (exclude user_id)
                import json
                param_copy = {k: v for k, v in tool_params.items() if k != 'user_id'}
                tool_signature = f"{tool_name}:{json.dumps(param_copy, sort_keys=True)}"

                # Skip if we've already executed this exact tool call
                if tool_signature in seen_tool_calls:
                    logger.warning(
                        f"Skipping duplicate tool call: {tool_signature}",
                        extra={"user_id": user_id, "tool": tool_name}
                    )
                    continue

                seen_tool_calls.add(tool_signature)

                if tool_name == 'add_task':
                    # Execute add_task tool
                    try:
                        # Pass due_date as string - add_task tool will parse it
                        params = AddTaskParams(
                            user_id=user_id,
                            title=tool_params.get('title'),
                            description=tool_params.get('description'),
                            priority=tool_params.get('priority', 'medium'),
                            due_date=tool_params.get('due_date')  # Pass as string
                        )
                        result = add_task(db, params)
                        executed_tools.append({
                            'tool': 'add_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'description': result.description,
                                'priority': result.priority,
                                'due_date': result.due_date.isoformat() if result.due_date else None,
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
                                        'priority': task['priority'],
                                        'due_date': task['due_date'].isoformat() if task.get('due_date') else None,
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
                                'priority': result.priority,
                                'due_date': result.due_date.isoformat() if result.due_date else None,
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
                        logger.info(
                            f"Executing update_task for user {user_id}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id'),
                                "params": tool_params
                            }
                        )

                        # Parse due_date if provided
                        due_date = None
                        due_date_str = tool_params.get('due_date')
                        if due_date_str:
                            try:
                                due_date = datetime.fromisoformat(due_date_str)
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid due_date format: {due_date_str}")

                        params = UpdateTaskParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id'),
                            title=tool_params.get('title'),
                            description=tool_params.get('description'),
                            priority=tool_params.get('priority'),
                            due_date=due_date,
                            completed=tool_params.get('completed')
                        )
                        result = update_task(db, params)

                        logger.info(
                            f"update_task succeeded: task_id={result.task_id}, title={result.title}",
                            extra={
                                "user_id": user_id,
                                "task_id": result.task_id,
                                "updated_fields": {k: v for k, v in tool_params.items() if v is not None}
                            }
                        )

                        executed_tools.append({
                            'tool': 'update_task',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'description': result.description,
                                'priority': result.priority,
                                'due_date': result.due_date.isoformat() if result.due_date else None,
                                'completed': result.completed,
                                'updated_at': result.updated_at.isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(
                            f"update_task failed for task_id={tool_params.get('task_id')}: {str(e)}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id'),
                                "error_type": type(e).__name__,
                                "params": tool_params
                            },
                            exc_info=True
                        )
                        # Continue even if tool fails

                elif tool_name == 'delete_task':
                    # Execute delete_task tool
                    try:
                        logger.info(
                            f"Executing delete_task for user {user_id}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id')
                            }
                        )

                        params = DeleteTaskParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id')
                        )
                        result = delete_task(db, params)

                        logger.info(
                            f"delete_task succeeded: task_id={result.task_id}, title={result.title}",
                            extra={
                                "user_id": user_id,
                                "task_id": result.task_id,
                                "task_title": result.title
                            }
                        )

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
                        logger.error(
                            f"delete_task failed for task_id={tool_params.get('task_id')}: {str(e)}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id'),
                                "error_type": type(e).__name__
                            },
                            exc_info=True
                        )
                        # Continue even if tool fails

                elif tool_name == 'set_task_deadline':
                    # Execute set_task_deadline tool
                    try:
                        from ..mcp_tools.set_task_deadline import (
                            set_task_deadline,
                            SetTaskDeadlineParams
                        )

                        logger.info(
                            f"Executing set_task_deadline for user {user_id}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id'),
                                "due_date": tool_params.get('due_date')
                            }
                        )

                        # Parse due_date if it's a string (natural language)
                        due_date_value = tool_params.get('due_date')
                        if due_date_value and isinstance(due_date_value, str):
                            # Parse natural language date
                            parsed_date = parse_natural_date(due_date_value)
                            if parsed_date:
                                due_date_value = parsed_date.isoformat()
                            else:
                                logger.warning(f"Failed to parse date: {due_date_value}")

                        params = SetTaskDeadlineParams(
                            user_id=user_id,
                            task_id=tool_params.get('task_id'),
                            due_date=due_date_value
                        )
                        result = set_task_deadline(db, params)

                        logger.info(
                            f"set_task_deadline succeeded: task_id={result.task_id}, action={result.action}",
                            extra={
                                "user_id": user_id,
                                "task_id": result.task_id,
                                "action": result.action,
                                "new_due_date": result.due_date.isoformat() if result.due_date else None
                            }
                        )

                        executed_tools.append({
                            'tool': 'set_task_deadline',
                            'params': tool_params,
                            'result': {
                                'task_id': result.task_id,
                                'title': result.title,
                                'due_date': result.due_date.isoformat() if result.due_date else None,
                                'action': result.action,
                                'updated_at': result.updated_at.isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(
                            f"set_task_deadline failed for task_id={tool_params.get('task_id')}: {str(e)}",
                            extra={
                                "user_id": user_id,
                                "task_id": tool_params.get('task_id'),
                                "error_type": type(e).__name__
                            },
                            exc_info=True
                        )
                        # Continue even if tool fails

                elif tool_name == 'find_task':
                    # Execute find_task tool
                    try:
                        params = FindTaskParams(
                            user_id=user_id,
                            title=tool_params.get('title')
                        )
                        result = find_task(db, params)

                        # Return find_task result without auto-execution
                        # Agent will ask for confirmation before executing delete/update/complete
                        executed_tools.append({
                            'tool': 'find_task',
                            'params': tool_params,
                            'result': {
                                'found': result is not None,
                                'task': {
                                    'task_id': result.task_id,
                                    'title': result.title,
                                    'description': result.description,
                                    'priority': result.priority,
                                    'completed': result.completed,
                                    'created_at': result.created_at.isoformat() if result.created_at else None
                                } if result else None
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
        # Enhance response for list_tasks tool with actual task data
        final_response = agent_response.response
        if executed_tools:
            for tool_call in executed_tools:
                if tool_call.get('tool') == 'list_tasks' and tool_call.get('result'):
                    result = tool_call['result']
                    tasks = result.get('tasks', [])
                    count = result.get('count', 0)

                    if count == 0:
                        final_response = "You don't have any tasks yet. Add your first task above!"
                    else:
                        # Build task list for response
                        task_list = []
                        for task in tasks:
                            task_status = "✅" if task.get('completed') else "⏳"
                            priority = task.get('priority', 'medium')
                            task_list.append(f"{task_status} {task.get('title')} ({priority})")

                        task_display = "\n".join(task_list)
                        final_response = f"Here are your tasks:\n\n{task_display}"

        return ChatResponse(
            conversation_id=conversation_id,
            response=final_response,
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
