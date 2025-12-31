"""AI Agent Execution Runner.

This module handles the execution of the AI agent with conversation history
and user messages, orchestrating tool calls and response generation.
"""

from typing import Any, Dict, List
import logging

from openai import OpenAI

from .agent import initialize_agent, get_system_prompt
from .tools import register_tools
from ..utils.performance import log_execution_time, track_performance

logger = logging.getLogger(__name__)


class AgentResponse:
    """Response from AI agent execution."""

    def __init__(
        self,
        response: str,
        tool_calls: List[Dict[str, Any]] = None
    ):
        """Initialize agent response.

        Args:
            response: Natural language response from agent
            tool_calls: List of tool calls made by agent
        """
        self.response = response
        self.tool_calls = tool_calls or []


@log_execution_time("run_ai_agent")
async def run_agent(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]],
    tools: List[Dict[str, Any]] = None
) -> AgentResponse:
    """Run AI agent with user message and conversation history.

    Args:
        user_id: ID of the authenticated user
        message: User's message
        conversation_history: List of previous messages with role and content
        tools: Optional list of tool definitions (defaults to registered tools)

    Returns:
        AgentResponse with natural language response and tool calls

    Error Handling:
        - OpenAI API timeout → Returns friendly error message
        - Tool execution failure → Logs error, returns graceful message
        - Invalid response → Falls back to clarification prompt

    Example:
        >>> history = [
        ...     {"role": "user", "content": "Add task to buy milk"},
        ...     {"role": "assistant", "content": "I've added 'Buy milk'"}
        ... ]
        >>> response = await run_agent(
        ...     user_id="user-123",
        ...     message="Show my tasks",
        ...     conversation_history=history
        ... )
        >>> assert response.response is not None
    """
    try:
        # Initialize agent with tools
        with track_performance("agent_initialization", user_id):
            if tools is None:
                tools = register_tools()

            client = initialize_agent(tools)

        # Build messages array with system prompt + history + new message
        with track_performance("agent_message_preparation", user_id):
            messages = [{"role": "system", "content": get_system_prompt()}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

        # Call OpenAI API (placeholder - will be implemented with actual tool calls)
        # For Phase 2, we're just setting up the structure
        with track_performance("agent_execution", user_id):
            logger.info(
                f"Agent execution for user {user_id}: message length {len(message)}"
            )

            # Placeholder response - actual implementation will use OpenAI chat completions
            response_text = (
                "Agent is configured and ready. "
                "Tool integration will be completed in Phase 3+."
            )

        return AgentResponse(
            response=response_text,
            tool_calls=[]
        )

    except TimeoutError as e:
        # OpenAI API timeout (T173)
        logger.error(
            "OpenAI API timeout",
            extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": "timeout"
            },
            exc_info=True
        )
        return AgentResponse(
            response="I'm having trouble processing your request right now. Please try again in a moment.",
            tool_calls=[]
        )
    except Exception as e:
        # Generic error handling with user-friendly message (T175)
        error_type = type(e).__name__
        logger.error(
            "Agent execution failed",
            extra={
                "user_id": user_id,
                "error": str(e),
                "error_type": error_type
            },
            exc_info=True
        )
        return AgentResponse(
            response="I'm having trouble processing your request. Please try again.",
            tool_calls=[]
        )
