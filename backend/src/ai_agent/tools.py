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
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": (
                                "Task priority level. CRITICAL: Extract from user's message. "
                                "Keywords mapping (YOU MUST USE THESE EXACTLY): "
                                "'urgent', 'critical', 'important', 'ASAP', 'high priority' → 'high', "
                                "'normal', 'medium priority' → 'medium', "
                                "'minor', 'trivial', 'low priority', 'someday' → 'low'. "
                                "ONLY use default 'medium' if NO priority keyword found in message. "
                                "If user says 'high priority', you MUST return 'high', NOT 'medium'!"
                            )
                        },
                        "due_date": {
                            "type": "string",
                            "description": (
                                "Task due date and time in ISO 8601 format (e.g., '2026-01-15T14:30:00'). "
                                "Extract from user's message if they mention: "
                                "'tomorrow', 'next week', 'by Friday', 'at 3pm', specific dates/times. "
                                "Optional - only include if user specifies a deadline."
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
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": (
                                "New task priority (optional, provide if user wants to change priority). "
                                "Extract from user's message using keywords: "
                                "'high priority', 'urgent', 'important' → 'high', "
                                "'medium priority', 'normal' → 'medium', "
                                "'low priority', 'minor' → 'low'. "
                                "If user says 'change to high priority', you MUST use 'high'!"
                            )
                        },
                        "due_date": {
                            "type": "string",
                            "description": (
                                "New task due date and time in ISO 8601 format (optional). "
                                "Provide if user wants to change or set deadline. "
                                "Use null to remove deadline completely."
                            )
                        },
                        "completed": {
                            "type": "boolean",
                            "description": (
                                "Mark task as complete (true) or incomplete (false). "
                                "Use this to toggle completion status. "
                                "Examples: 'mark as incomplete' → false, 'mark as done' → true"
                            )
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
        },
        # find_task tool for task lookup by title
        {
            "type": "function",
            "function": {
                "name": "find_task",
                "description": (
                    "Find a task by its title for the authenticated user. "
                    "Use this when the user refers to a task by name/title instead of ID, "
                    "especially when they want to update or delete a task. "
                    "Examples: 'Find the task about buy book', 'Look up task titled Buy milk', "
                    "'Search for task Call mom'."
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
                            "description": "Task title to search for (case-insensitive partial match)"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        # set_task_deadline tool for deadline management
        {
            "type": "function",
            "function": {
                "name": "set_task_deadline",
                "description": (
                    "Set, update, or remove a task's deadline/due date. "
                    "Use this when the user wants to: "
                    "- Set a new deadline (e.g., 'Set deadline for task 5 to tomorrow') "
                    "- Change existing deadline (e.g., 'Change task 3 deadline to next Friday') "
                    "- Remove deadline completely (e.g., 'Remove deadline from task 7'). "
                    "This is a FOCUSED tool specifically for deadline management."
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
                        "due_date": {
                            "type": "string",
                            "description": (
                                "New deadline in ISO 8601 format (e.g., '2026-01-15T14:30:00'). "
                                "Extract from natural language: 'tomorrow', 'next Friday', 'January 20 at 2pm'. "
                                "Set to null to REMOVE the deadline completely. "
                                "Examples: 'tomorrow' → parse to ISO format, 'remove deadline' → null"
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
    - Phase 8: find_task ✓
    - Phase 9: set_task_deadline ✓ (NEW - Dedicated deadline management)

    Example:
        >>> tools = register_tools()
        >>> assert isinstance(tools, list)
        >>> assert len(tools) == 7  # All 7 task management tools
    """
    return get_tool_definitions()
