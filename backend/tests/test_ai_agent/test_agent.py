"""Unit tests for AI agent initialization."""

import pytest
from unittest.mock import patch, Mock

from src.ai_agent.agent import (
    get_agent_config,
    initialize_agent,
    get_system_prompt,
    SYSTEM_PROMPT
)


class TestAgentConfiguration:
    """Tests for agent configuration."""

    @patch('src.ai_agent.agent.settings')
    def test_get_agent_config_success(self, mock_settings):
        """Test successful agent config retrieval."""
        # Arrange
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.openai_agent_model = "gpt-4o"

        # Act
        config = get_agent_config()

        # Assert
        assert config["api_key"] == "sk-test-key"
        assert config["model"] == "gpt-4o"

    @patch('src.ai_agent.agent.settings')
    def test_get_agent_config_missing_key(self, mock_settings):
        """Test that missing API key raises ValueError."""
        # Arrange
        mock_settings.openai_api_key = ""

        # Act & Assert
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
            get_agent_config()

    @patch('src.ai_agent.agent.OpenAI')
    @patch('src.ai_agent.agent.get_agent_config')
    def test_initialize_agent(self, mock_get_config, mock_openai):
        """Test agent initialization with tools."""
        # Arrange
        mock_get_config.return_value = {
            "api_key": "sk-test-key",
            "model": "gpt-4o"
        }
        mock_client = Mock()
        mock_openai.return_value = mock_client

        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        # Act
        client = initialize_agent(tools)

        # Assert
        assert client is not None
        mock_openai.assert_called_once_with(api_key="sk-test-key")

    def test_get_system_prompt(self):
        """Test system prompt retrieval."""
        # Act
        prompt = get_system_prompt()

        # Assert
        assert prompt == SYSTEM_PROMPT
        assert "task management" in prompt.lower()
        assert "add tasks" in prompt.lower()
        assert "view tasks" in prompt.lower()


class TestSystemPrompt:
    """Tests for system prompt content."""

    def test_system_prompt_contains_operations(self):
        """Test that system prompt mentions all task operations."""
        assert "add" in SYSTEM_PROMPT.lower()
        assert "view" in SYSTEM_PROMPT.lower() or "show" in SYSTEM_PROMPT.lower()
        assert "complete" in SYSTEM_PROMPT.lower()
        assert "update" in SYSTEM_PROMPT.lower() or "change" in SYSTEM_PROMPT.lower()
        assert "delete" in SYSTEM_PROMPT.lower() or "remove" in SYSTEM_PROMPT.lower()

    def test_system_prompt_mentions_clarification(self):
        """Test that system prompt includes clarification guidance."""
        assert "clarify" in SYSTEM_PROMPT.lower() or "unclear" in SYSTEM_PROMPT.lower()

    def test_system_prompt_mentions_tools(self):
        """Test that system prompt mentions using tools."""
        assert "tool" in SYSTEM_PROMPT.lower()
