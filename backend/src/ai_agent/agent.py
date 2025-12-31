"""AI Agent Initialization and Configuration.

This module handles the initialization of the OpenAI agent with the appropriate
system prompt and tool configurations.
"""

from typing import Any, Dict, List
from openai import OpenAI

from ..config import settings


# System prompt for task management assistant
SYSTEM_PROMPT = """You are a helpful task management assistant. Users can ask you to:
- Add tasks (e.g., "Add task to buy milk")
- View tasks (e.g., "Show my tasks", "What's pending?")
- Complete tasks (e.g., "Mark task 5 as done", "I finished buying milk")
- Update tasks (e.g., "Change task 3 to 'Buy groceries'")
- Delete tasks (e.g., "Delete task 7", "Remove the milk task")

When user intent is unclear, ask clarifying questions.
Always confirm actions with friendly, natural language.
Use the provided tools to perform task operations.
"""


def get_agent_config() -> Dict[str, Any]:
    """Load agent configuration from settings.

    Returns:
        Dict with api_key and model configuration

    Raises:
        ValueError: If OPENAI_API_KEY is not set

    Example:
        >>> config = get_agent_config()
        >>> assert 'api_key' in config
        >>> assert 'model' in config
    """
    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please configure it in .env file."
        )

    return {
        "api_key": settings.openai_api_key,
        "model": settings.openai_agent_model,
    }


def initialize_agent(tools: List[Dict[str, Any]]) -> OpenAI:
    """Initialize OpenAI client with tools.

    Args:
        tools: List of MCP tool definitions

    Returns:
        Configured OpenAI client instance

    Example:
        >>> tools = [{"type": "function", "function": {...}}]
        >>> client = initialize_agent(tools)
        >>> assert client is not None
    """
    config = get_agent_config()
    client = OpenAI(api_key=config["api_key"])
    return client


def get_system_prompt() -> str:
    """Get the system prompt for the task management assistant.

    Returns:
        System prompt string

    Example:
        >>> prompt = get_system_prompt()
        >>> assert "task management" in prompt.lower()
    """
    return SYSTEM_PROMPT
