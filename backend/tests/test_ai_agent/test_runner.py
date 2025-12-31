"""Integration tests for AI agent runner."""

import pytest
from unittest.mock import patch, Mock, AsyncMock

from src.ai_agent.runner import run_agent, AgentResponse


class TestAgentRunner:
    """Tests for agent execution runner."""

    @pytest.mark.asyncio
    async def test_agent_response_creation(self):
        """Test AgentResponse object creation."""
        # Arrange
        response_text = "I've added 'Buy milk' to your tasks."
        tool_calls = [{"tool": "add_task", "params": {"title": "Buy milk"}}]

        # Act
        response = AgentResponse(response=response_text, tool_calls=tool_calls)

        # Assert
        assert response.response == response_text
        assert response.tool_calls == tool_calls

    @pytest.mark.asyncio
    async def test_agent_response_default_tool_calls(self):
        """Test AgentResponse with default empty tool_calls."""
        # Arrange & Act
        response = AgentResponse(response="Test response")

        # Assert
        assert response.response == "Test response"
        assert response.tool_calls == []

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_run_agent_success(self, mock_register_tools, mock_initialize_agent):
        """Test successful agent execution."""
        # Arrange
        mock_tools = []
        mock_register_tools.return_value = mock_tools
        mock_client = Mock()
        mock_initialize_agent.return_value = mock_client

        user_id = "test-user-123"
        message = "Add task to buy milk"
        history = []

        # Act
        response = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(response, AgentResponse)
        assert response.response is not None
        mock_initialize_agent.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    @patch('src.ai_agent.runner.register_tools')
    async def test_run_agent_with_conversation_history(
        self, mock_register_tools, mock_initialize_agent
    ):
        """Test agent execution with conversation history."""
        # Arrange
        mock_register_tools.return_value = []
        mock_initialize_agent.return_value = Mock()

        user_id = "test-user-123"
        message = "Show my tasks"
        history = [
            {"role": "user", "content": "Add task to buy milk"},
            {"role": "assistant", "content": "I've added 'Buy milk' to your tasks."}
        ]

        # Act
        response = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(response, AgentResponse)
        assert response.response is not None

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    async def test_run_agent_with_custom_tools(self, mock_initialize_agent):
        """Test agent execution with custom tools."""
        # Arrange
        mock_initialize_agent.return_value = Mock()

        user_id = "test-user-123"
        message = "Test message"
        history = []
        custom_tools = [{"type": "function", "function": {"name": "custom_tool"}}]

        # Act
        response = await run_agent(user_id, message, history, tools=custom_tools)

        # Assert
        assert isinstance(response, AgentResponse)
        mock_initialize_agent.assert_called_once_with(custom_tools)

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.initialize_agent')
    async def test_run_agent_error_handling(self, mock_initialize_agent):
        """Test agent error handling returns graceful message."""
        # Arrange
        mock_initialize_agent.side_effect = Exception("API Error")

        user_id = "test-user-123"
        message = "Test message"
        history = []

        # Act
        response = await run_agent(user_id, message, history)

        # Assert
        assert isinstance(response, AgentResponse)
        assert "trouble processing" in response.response.lower()
        assert response.tool_calls == []

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.logger')
    @patch('src.ai_agent.runner.initialize_agent')
    async def test_run_agent_logs_execution(self, mock_initialize_agent, mock_logger):
        """Test that agent execution is logged."""
        # Arrange
        mock_initialize_agent.return_value = Mock()

        user_id = "test-user-123"
        message = "Test message"
        history = []

        # Act
        await run_agent(user_id, message, history)

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert user_id in call_args

    @pytest.mark.asyncio
    @patch('src.ai_agent.runner.logger')
    @patch('src.ai_agent.runner.initialize_agent')
    async def test_run_agent_logs_errors(self, mock_initialize_agent, mock_logger):
        """Test that errors are logged with context."""
        # Arrange
        error_message = "Test error"
        mock_initialize_agent.side_effect = Exception(error_message)

        user_id = "test-user-123"
        message = "Test message"
        history = []

        # Act
        await run_agent(user_id, message, history)

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert user_id in call_args
