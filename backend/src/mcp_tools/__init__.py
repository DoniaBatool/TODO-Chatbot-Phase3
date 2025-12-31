"""MCP Tools for Task Management.

This module contains MCP (Model Context Protocol) tools that expose task operations
to the AI agent. Each tool is stateless and enforces user isolation.
"""

from .add_task import add_task, AddTaskParams, AddTaskResult
from .list_tasks import list_tasks, ListTasksParams, ListTasksResult
from .complete_task import complete_task, CompleteTaskParams, CompleteTaskResult
from .update_task import update_task, UpdateTaskParams, UpdateTaskResult
from .delete_task import delete_task, DeleteTaskParams, DeleteTaskResult

__all__ = [
    "add_task",
    "AddTaskParams",
    "AddTaskResult",
    "list_tasks",
    "ListTasksParams",
    "ListTasksResult",
    "complete_task",
    "CompleteTaskParams",
    "CompleteTaskResult",
    "update_task",
    "UpdateTaskParams",
    "UpdateTaskResult",
    "delete_task",
    "DeleteTaskParams",
    "DeleteTaskResult",
]
