"""MCP Tool Registration for AI Agent.

This module registers MCP tools with the AI agent, providing tool definitions
with descriptions and parameter schemas.
"""

from typing import Any, Dict, List


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get OpenAI function calling tool definitions for all MCP tools.

    Returns:
        List of tool definitions in OpenAI function calling format

    OpenAI Function Calling Format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "What the tool does",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }

    Example:
        >>> tools = get_tool_definitions()
        >>> assert isinstance(tools, list)
        >>> assert len(tools) > 0
    """
    tools = [
        # Phase 3: add_task tool
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": (
                    "Create a new task for the user. "
                    "Use this when the user wants to add, create, remember, "
                    "or note something. Examples: 'Add task to buy milk', "
                    "'Remember to call mom', 'Create task: finish report'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the authenticated user (automatically provided)"
                        },
                        "title": {
                            "type": "string",
                            "description": (
                                "Task title (1-200 characters). Extract the main "
                                "task from user's message. Examples: 'Buy milk', "
                                "'Call mom', 'Finish report'."
                            )
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Optional task description with additional details. "
                                "Use when user provides extra context. "
                                "Example: 'quarterly sales report for Q4'."
                            )
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        # Phase 4: list_tasks tool
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": (
                    "List tasks for the user with optional filtering by completion status. "
                    "Use this when the user wants to see, show, view, or list their tasks. "
                    "Examples: 'Show my tasks', 'What's pending?', 'List completed tasks', "
                    "'What do I need to do?'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the authenticated user (automatically provided)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": (
                                "Filter tasks by completion status. "
                                "'all' - show all tasks (default), "
                                "'pending' - show only incomplete tasks, "
                                "'completed' - show only finished tasks. "
                                "Examples: 'Show my tasks' → 'all', "
                                "'What's pending?' → 'pending', "
                                "'Show completed' → 'completed'."
                            )
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        # Phase 5: complete_task tool
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": (
                    "Mark a task as completed. "
                    "Use this when the user says they finished, completed, or are done with a task. "
                    "Examples: 'Mark task 5 as complete', 'I finished buying milk', "
                    "'Done with calling mom', 'Complete task 3'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the authenticated user (automatically provided)"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": (
                                "ID of the task to mark as complete. "
                                "Extract from user's message (e.g., 'Mark task 5 as complete' → 5). "
                                "If user mentions task by title instead of ID, first call list_tasks "
                                "to find the task_id, then call complete_task."
                            )
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        # Phase 6: update_task tool
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": (
                    "Update a task's title or description. "
                    "Use this when the user wants to change, edit, modify, or update a task. "
                    "Examples: 'Change task 3 to Buy milk and eggs', "
                    "'Update description of task 2 to include deadline', "
                    "'Edit task 5 title to Call mom tomorrow'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the authenticated user (automatically provided)"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional, provide if user wants to change title)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional, provide if user wants to change description)"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        # Phase 7: delete_task tool
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": (
                    "Delete a task permanently. "
                    "Use this when the user wants to remove, delete, or get rid of a task. "
                    "Examples: 'Delete task 7', 'Remove the milk task', "
                    "'Get rid of task 3', 'Delete my task about calling mom'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID of the authenticated user (automatically provided)"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": (
                                "ID of the task to delete. "
                                "If user mentions task by title, first call list_tasks "
                                "to find the task_id, then call delete_task."
                            )
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]

    return tools


def register_tools() -> List[Dict[str, Any]]:
    """Register all MCP tools with the AI agent.

    Returns:
        List of registered tool definitions

    Implemented tools:
    - Phase 3: add_task ✓
    - Phase 4: list_tasks ✓
    - Phase 5: complete_task ✓
    - Phase 6: update_task ✓
    - Phase 7: delete_task ✓

    Example:
        >>> tools = register_tools()
        >>> assert isinstance(tools, list)
        >>> assert len(tools) == 5  # All 5 task management tools
    """
    return get_tool_definitions()
