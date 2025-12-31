"""Integration tests for AI agent with list_tasks tool.

Tests the full flow: user message → agent interprets → calls list_tasks → returns response
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
import json

from src.ai_agent.runner import run_agent, AgentResponse
from src.ai_agent.tools import get_tool_definitions
from src.mcp_tools.list_tasks import ListTasksResult
from datetime import datetime


class TestListTasksAgentIntegration:
    """Integration tests for agent using list_tasks tool."""

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_interprets_show_my_tasks(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent interprets 'Show my tasks' → calls list_tasks with status='all'."""
        # Arrange
        user_id = "test-user-123"
        message = "Show my tasks"
        history = []

        # Mock tool registration
        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        # Mock OpenAI client
        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock OpenAI response with list_tasks tool call
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Here are all your tasks.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="list_tasks",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "status": "all"
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
    async def test_agent_interprets_whats_pending(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent interprets 'What's pending?' → calls list_tasks with status='pending'."""
        # Arrange
        user_id = "test-user-456"
        message = "What's pending?"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with status='pending'
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Here are your pending tasks.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="list_tasks",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "status": "pending"
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
    async def test_agent_interprets_show_completed(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent interprets 'Show completed tasks' → calls list_tasks with status='completed'."""
        # Arrange
        user_id = "test-user-789"
        message = "Show completed tasks"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with status='completed'
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Here are your completed tasks.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="list_tasks",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "status": "completed"
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
    async def test_agent_handles_empty_task_list(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: empty task list → agent responds with helpful message."""
        # Arrange
        user_id = "test-user-empty"
        message = "Show my tasks"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with helpful message for empty list
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="You don't have any tasks yet. Would you like to add one?",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="list_tasks",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "status": "all"
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
        assert "don't have" in result.response.lower() or "no tasks" in result.response.lower()

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_natural_language_variations(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent handles different natural language variations for listing tasks."""
        # Arrange
        variations = [
            "What do I need to do?",
            "List my tasks",
            "Show me what I have to do",
            "What's on my todo list?"
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
                        content="Here are your tasks.",
                        tool_calls=[
                            MagicMock(
                                function=MagicMock(
                                    name="list_tasks",
                                    arguments=json.dumps({
                                        "user_id": "test-user",
                                        "status": "all"
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


class TestListTasksToolDefinition:
    """Tests for list_tasks tool definition."""

    def test_list_tasks_tool_definition_structure(self):
        """Test that list_tasks tool definition has correct structure."""
        # Act
        tools = get_tool_definitions()

        # Assert
        assert len(tools) == 2  # add_task and list_tasks
        list_tasks_tool = tools[1]

        assert list_tasks_tool["type"] == "function"
        assert "function" in list_tasks_tool
        assert list_tasks_tool["function"]["name"] == "list_tasks"
        assert "description" in list_tasks_tool["function"]
        assert "parameters" in list_tasks_tool["function"]

    def test_list_tasks_tool_parameters(self):
        """Test that list_tasks tool has correct parameters."""
        # Act
        tools = get_tool_definitions()
        tool = tools[1]  # list_tasks
        params = tool["function"]["parameters"]

        # Assert
        assert params["type"] == "object"
        assert "properties" in params
        assert "user_id" in params["properties"]
        assert "status" in params["properties"]

        # Check status enum
        status_prop = params["properties"]["status"]
        assert "enum" in status_prop
        assert status_prop["enum"] == ["all", "pending", "completed"]

        # Required fields
        assert "required" in params
        assert "user_id" in params["required"]
        assert "status" not in params["required"]  # Optional

    def test_list_tasks_tool_description(self):
        """Test that list_tasks tool has helpful description."""
        # Act
        tools = get_tool_definitions()
        tool = tools[1]
        description = tool["function"]["description"]

        # Assert
        assert "list" in description.lower() or "show" in description.lower()
        assert "task" in description.lower()
        # Should include usage examples
        assert "example" in description.lower() or "show my tasks" in description.lower()

    def test_both_tools_registered(self):
        """Test that both add_task and list_tasks are registered."""
        # Act
        tools = get_tool_definitions()

        # Assert
        assert len(tools) == 2
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
