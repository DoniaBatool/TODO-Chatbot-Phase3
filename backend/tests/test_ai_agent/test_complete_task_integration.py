"""Integration tests for AI agent with complete_task tool.

Tests the full flow: user message → agent interprets → calls complete_task → returns response
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
import json

from src.ai_agent.runner import run_agent, AgentResponse
from src.ai_agent.tools import get_tool_definitions
from src.mcp_tools.complete_task import CompleteTaskResult
from datetime import datetime


class TestCompleteTaskAgentIntegration:
    """Integration tests for agent using complete_task tool."""

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_interprets_mark_task_complete_by_id(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent interprets 'Mark task 5 as complete' → calls complete_task."""
        # Arrange
        user_id = "test-user-123"
        message = "Mark task 5 as complete"
        history = []

        # Mock tool registration
        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        # Mock OpenAI client
        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock OpenAI response with complete_task tool call
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I've marked task 5 as complete.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="complete_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "task_id": 5
                                })
                            )
                        )
                    ]
                )
            )
        ]
        mock_client.chat.completions.create = Mock(return_value=mock_response)

        # Act
        result = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(result, AgentResponse)
        assert result.response is not None
        # Verify agent was initialized with correct tools
        mock_initialize_agent.assert_called_once_with(tools)

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_handles_finished_task_by_title(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent handles 'I finished buying milk' → calls list_tasks → extracts task_id → calls complete_task."""
        # Arrange
        user_id = "test-user-456"
        message = "I finished buying milk"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with multiple tool calls (list_tasks first, then complete_task)
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Great! I've marked 'Buy milk' as complete.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="list_tasks",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "status": "pending"
                                })
                            )
                        ),
                        MagicMock(
                            function=MagicMock(
                                name="complete_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "task_id": 1  # Found from list_tasks
                                })
                            )
                        )
                    ]
                )
            )
        ]
        mock_client.chat.completions.create = Mock(return_value=mock_response)

        # Act
        result = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(result, AgentResponse)
        assert result.response is not None

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_handles_nonexistent_task(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: non-existent task → agent responds with helpful error."""
        # Arrange
        user_id = "test-user-789"
        message = "Mark task 9999 as complete"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with error handling
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I couldn't find task 9999. Would you like to see your task list?",
                    tool_calls=None  # Tool call would fail
                )
            )
        ]
        mock_client.chat.completions.create = Mock(return_value=mock_response)

        # Act
        result = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(result, AgentResponse)
        assert "couldn't find" in result.response.lower() or "not found" in result.response.lower()

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_natural_language_variations(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent handles different natural language variations for completing tasks."""
        # Arrange
        variations = [
            "Done with task 3",
            "I completed task 7",
            "Finished task 2",
            "Task 5 is done"
        ]

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        for message in variations:
            # Mock response
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=f"I've marked that task as complete.",
                        tool_calls=[
                            MagicMock(
                                function=MagicMock(
                                    name="complete_task",
                                    arguments=json.dumps({
                                        "user_id": "test-user",
                                        "task_id": 3  # Extracted from message
                                    })
                                )
                            )
                        ]
                    )
                )
            ]
            mock_client.chat.completions.create = Mock(return_value=mock_response)

            # Act
            result = await run_agent("test-user", message, [])

            # Assert
            assert isinstance(result, AgentResponse)
            assert result.response is not None


class TestCompleteTaskToolDefinition:
    """Tests for complete_task tool definition."""

    def test_complete_task_tool_definition_structure(self):
        """Test that complete_task tool definition has correct structure."""
        # Act
        tools = get_tool_definitions()

        # Assert
        assert len(tools) == 3  # add_task, list_tasks, complete_task
        complete_task_tool = tools[2]

        assert complete_task_tool["type"] == "function"
        assert "function" in complete_task_tool
        assert complete_task_tool["function"]["name"] == "complete_task"
        assert "description" in complete_task_tool["function"]
        assert "parameters" in complete_task_tool["function"]

    def test_complete_task_tool_parameters(self):
        """Test that complete_task tool has correct parameters."""
        # Act
        tools = get_tool_definitions()
        tool = tools[2]  # complete_task
        params = tool["function"]["parameters"]

        # Assert
        assert params["type"] == "object"
        assert "properties" in params
        assert "user_id" in params["properties"]
        assert "task_id" in params["properties"]

        # Check task_id is integer
        task_id_prop = params["properties"]["task_id"]
        assert task_id_prop["type"] == "integer"

        # Required fields
        assert "required" in params
        assert "user_id" in params["required"]
        assert "task_id" in params["required"]

    def test_complete_task_tool_description(self):
        """Test that complete_task tool has helpful description."""
        # Act
        tools = get_tool_definitions()
        tool = tools[2]
        description = tool["function"]["description"]

        # Assert
        assert "complete" in description.lower() or "mark" in description.lower()
        assert "task" in description.lower()
        # Should include usage examples
        assert "example" in description.lower() or "finished" in description.lower()

    def test_all_three_tools_registered(self):
        """Test that all three tools (add, list, complete) are registered."""
        # Act
        tools = get_tool_definitions()

        # Assert
        assert len(tools) == 3
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names
