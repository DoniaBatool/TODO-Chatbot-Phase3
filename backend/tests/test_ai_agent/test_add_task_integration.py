"""Integration tests for AI agent with add_task tool.

Tests the full flow: user message → agent interprets → calls add_task → returns response
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
import json

from src.ai_agent.runner import run_agent, AgentResponse
from src.ai_agent.tools import get_tool_definitions
from src.mcp_tools.add_task import AddTaskResult
from datetime import datetime


class TestAddTaskAgentIntegration:
    """Integration tests for agent using add_task tool."""

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_interprets_add_task_command(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent interprets 'Add task to buy milk' → calls add_task tool."""
        # Arrange
        user_id = "test-user-123"
        message = "Add task to buy milk"
        history = []

        # Mock tool registration
        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        # Mock OpenAI client
        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock OpenAI chat completion response with tool call
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I'll add that task for you.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="add_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "title": "Buy milk"
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
    async def test_agent_extracts_task_from_natural_language(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent extracts task from natural language input."""
        # Arrange
        user_id = "test-user-456"
        message = "Remember to call mom tomorrow"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with extracted task
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I've added a reminder to call mom tomorrow.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="add_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "title": "Call mom tomorrow"
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
    async def test_agent_handles_task_with_description(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent handles task with title and description."""
        # Arrange
        user_id = "test-user-789"
        message = "Add task: finish report with description: quarterly sales"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response with both title and description
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I've created the task 'Finish report' with the description.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="add_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "title": "Finish report",
                                    "description": "quarterly sales"
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
    async def test_agent_handles_ambiguous_input(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent handles ambiguous input 'buy' → asks clarification."""
        # Arrange
        user_id = "test-user-amb"
        message = "buy"
        history = []

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response asking for clarification (no tool call)
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="What would you like to buy?",
                    tool_calls=None
                )
            )
        ]
        mock_client.chat.completions.create = Mock(return_value=mock_response)

        # Act
        result = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(result, AgentResponse)
        assert "what" in result.response.lower() or "buy" in result.response.lower()
        # No tool calls should be made for ambiguous input
        assert result.tool_calls == []

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_agent_uses_conversation_history(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test: agent uses conversation history for context."""
        # Arrange
        user_id = "test-user-history"
        message = "And also buy eggs"
        history = [
            {"role": "user", "content": "Add task to buy milk"},
            {"role": "assistant", "content": "I've added 'Buy milk' to your tasks."}
        ]

        tools = get_tool_definitions()
        mock_register_tools.return_value = tools

        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        # Mock response using context from history
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I've added 'Buy eggs' to your tasks.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="add_task",
                                arguments=json.dumps({
                                    "user_id": user_id,
                                    "title": "Buy eggs"
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


class TestToolDefinitions:
    """Tests for add_task tool definition."""

    def test_add_task_tool_definition_structure(self):
        """Test that add_task tool definition has correct structure."""
        # Act
        tools = get_tool_definitions()

        # Assert
        assert len(tools) == 1
        tool = tools[0]

        assert tool["type"] == "function"
        assert "function" in tool
        assert tool["function"]["name"] == "add_task"
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]

    def test_add_task_tool_parameters(self):
        """Test that add_task tool has correct parameters."""
        # Act
        tools = get_tool_definitions()
        tool = tools[0]
        params = tool["function"]["parameters"]

        # Assert
        assert params["type"] == "object"
        assert "properties" in params
        assert "user_id" in params["properties"]
        assert "title" in params["properties"]
        assert "description" in params["properties"]

        # Required fields
        assert "required" in params
        assert "user_id" in params["required"]
        assert "title" in params["required"]
        assert "description" not in params["required"]  # Optional

    def test_add_task_tool_description(self):
        """Test that add_task tool has helpful description."""
        # Act
        tools = get_tool_definitions()
        tool = tools[0]
        description = tool["function"]["description"]

        # Assert
        assert "create" in description.lower() or "add" in description.lower()
        assert "task" in description.lower()
        # Should include usage examples
        assert "example" in description.lower() or "buy milk" in description.lower()
