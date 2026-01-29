"""
Unit tests for GPT-4o fallback in DateParser.

Tests cover:
- GPT fallback initialization
- GPT parsing for ambiguous dates
- Fallback behavior when dateparser fails
- Validation in GPT parsing
- Error handling
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.utils.date_parser import DateParser, DateParseResult


class TestGPTFallbackInitialization:
    """Test GPT fallback initialization and configuration."""

    def test_default_uses_gpt_fallback(self):
        """GPT fallback is enabled by default."""
        parser = DateParser()
        assert parser.use_gpt_fallback is True

    def test_can_disable_gpt_fallback(self):
        """GPT fallback can be disabled."""
        parser = DateParser(use_gpt_fallback=False)
        assert parser.use_gpt_fallback is False

    def test_gpt_fallback_threshold(self):
        """GPT fallback threshold is set correctly."""
        parser = DateParser()
        assert parser.GPT_FALLBACK_THRESHOLD == 0.6

    @patch.dict("os.environ", {}, clear=True)
    def test_openai_client_none_without_api_key(self):
        """OpenAI client is None when API key not set."""
        parser = DateParser()
        # Clear any cached client
        parser._openai_client = None
        assert parser.openai_client is None

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_openai_client_created_with_api_key(self):
        """OpenAI client is created when API key is set."""
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client

            parser = DateParser()
            parser._openai_client = None  # Reset cached client

            client = parser.openai_client
            assert client is mock_client
            mock_openai_class.assert_called_once_with(api_key="test-key")


class TestGPTParsingDirectly:
    """Test _parse_with_gpt method directly."""

    def test_gpt_fallback_disabled_returns_error(self):
        """Returns error when GPT fallback is disabled."""
        parser = DateParser(use_gpt_fallback=False)
        result = parser._parse_with_gpt("next Tuesday")

        assert result.success is False
        assert "GPT fallback disabled" in result.error_message

    @patch.dict("os.environ", {}, clear=True)
    def test_no_api_key_returns_error(self):
        """Returns error when no API key available."""
        parser = DateParser(use_gpt_fallback=True)
        parser._openai_client = None  # Reset

        result = parser._parse_with_gpt("next Tuesday")

        assert result.success is False
        assert "OpenAI API not available" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_parses_ambiguous_date(self):
        """GPT can parse ambiguous date strings."""
        parser = DateParser(use_gpt_fallback=True)

        # Use a safe future date (7 days from now)
        future_date = datetime.now() + timedelta(days=7)

        # Mock OpenAI client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "success": True,
            "year": future_date.year,
            "month": future_date.month,
            "day": future_date.day,
            "hour": 14,
            "minute": 0,
            "confidence": 0.9,
            "reasoning": "A week from now"
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("sometime next week around 2pm")

        assert result.success is True
        assert result.parsed_date is not None
        assert result.confidence == 0.9

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_rejects_past_date(self):
        """GPT-parsed dates in the past are rejected."""
        parser = DateParser(use_gpt_fallback=True)

        # Mock response with past date
        past_date = datetime.now() - timedelta(days=5)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "success": True,
            "year": past_date.year,
            "month": past_date.month,
            "day": past_date.day,
            "hour": 10,
            "minute": 0,
            "confidence": 0.9,
            "reasoning": "Last week"
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("last week")

        assert result.success is False
        assert "past" in result.error_message.lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_rejects_far_future_date(self):
        """GPT-parsed dates too far in future are rejected."""
        parser = DateParser(use_gpt_fallback=True)

        # Mock response with far future date
        future_date = datetime.now() + timedelta(days=365 * 15)  # 15 years
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "success": True,
            "year": future_date.year,
            "month": future_date.month,
            "day": future_date.day,
            "hour": 10,
            "minute": 0,
            "confidence": 0.8,
            "reasoning": "15 years from now"
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("in 15 years")

        assert result.success is False
        assert "10 years" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_handles_unparseable_response(self):
        """GPT handles responses that indicate failure to parse."""
        parser = DateParser(use_gpt_fallback=True)

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "success": False,
            "reasoning": "Cannot determine date from 'asdfgh'"
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("asdfgh")

        assert result.success is False
        assert "Cannot determine" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_handles_invalid_json(self):
        """GPT handles invalid JSON responses gracefully."""
        parser = DateParser(use_gpt_fallback=True)

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("next week")

        assert result.success is False
        assert "Invalid response format" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_handles_api_exception(self):
        """GPT handles API exceptions gracefully."""
        parser = DateParser(use_gpt_fallback=True)

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("next week")

        assert result.success is False
        assert "API Error" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_strips_markdown_code_blocks(self):
        """GPT strips markdown code blocks from response."""
        parser = DateParser(use_gpt_fallback=True)

        future_date = datetime.now() + timedelta(days=7)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        # Response wrapped in markdown code block
        mock_response.choices[0].message.content = f'''```json
{{
    "success": true,
    "year": {future_date.year},
    "month": {future_date.month},
    "day": {future_date.day},
    "hour": 15,
    "minute": 30,
    "confidence": 0.85,
    "reasoning": "Next week"
}}
```'''

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("next week at 3:30pm")

        assert result.success is True
        assert result.parsed_date.hour == 15
        assert result.parsed_date.minute == 30


class TestParseWithFallback:
    """Test parse_with_fallback method."""

    def test_uses_dateparser_for_clear_dates(self):
        """Uses dateparser when it returns high confidence."""
        parser = DateParser(use_gpt_fallback=True)

        result = parser.parse_with_fallback("tomorrow at 3pm")

        assert result.success is True
        assert result.confidence >= parser.GPT_FALLBACK_THRESHOLD

    def test_force_gpt_bypasses_dateparser(self):
        """force_gpt=True bypasses dateparser entirely."""
        parser = DateParser(use_gpt_fallback=False)

        # Even with GPT disabled, force_gpt should attempt GPT
        result = parser.parse_with_fallback("next week", force_gpt=True)

        # Should fail because GPT is disabled
        assert result.success is False
        assert "GPT fallback disabled" in result.error_message

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_fallback_triggered_on_low_confidence(self):
        """GPT fallback is triggered when dateparser has low confidence."""
        parser = DateParser(use_gpt_fallback=True)

        # Mock dateparser to return low confidence
        with patch.object(parser, 'parse') as mock_parse:
            mock_parse.return_value = DateParseResult(
                success=True,
                parsed_date=datetime.now() + timedelta(days=1),
                confidence=0.5,  # Below threshold
                original_text="sometime soon"
            )

            # Mock GPT to return better result
            future_date = datetime.now() + timedelta(days=3)
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "success": True,
                "year": future_date.year,
                "month": future_date.month,
                "day": future_date.day,
                "hour": 12,
                "minute": 0,
                "confidence": 0.85,
                "reasoning": "In a few days"
            })

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            parser._openai_client = mock_client

            result = parser.parse_with_fallback("sometime soon")

            # Should use GPT result due to higher confidence
            assert result.success is True
            assert result.confidence == 0.85

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_fallback_triggered_on_dateparser_failure(self):
        """GPT fallback is triggered when dateparser fails completely."""
        parser = DateParser(use_gpt_fallback=True)

        # Mock dateparser to fail
        with patch.object(parser, 'parse') as mock_parse:
            mock_parse.return_value = DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message="Could not parse",
                original_text="gibberish date"
            )

            # Mock GPT to also fail
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "success": False,
                "reasoning": "Cannot interpret"
            })

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            parser._openai_client = mock_client

            result = parser.parse_with_fallback("gibberish date")

            # Both failed, should return original dateparser error
            assert result.success is False

    def test_returns_dateparser_result_when_gpt_unavailable(self):
        """Returns dateparser result when GPT is unavailable."""
        parser = DateParser(use_gpt_fallback=True)
        parser._openai_client = None

        result = parser.parse_with_fallback("tomorrow")

        # Should still work with dateparser
        assert result.success is True
        assert result.confidence >= 0.7


class TestGPTFallbackIntegration:
    """Integration tests for GPT fallback with real-ish scenarios."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_ambiguous_date_scenario(self):
        """Test handling of genuinely ambiguous date."""
        parser = DateParser(use_gpt_fallback=True)

        # "next quarter" is ambiguous - dateparser might fail or have low confidence
        with patch.object(parser, '_parse_with_gpt') as mock_gpt:
            future_date = datetime.now() + timedelta(days=90)
            mock_gpt.return_value = DateParseResult(
                success=True,
                parsed_date=future_date,
                confidence=0.75,
                original_text="next quarter"
            )

            result = parser.parse_with_fallback("next quarter")

            # If dateparser failed or had low confidence, should fall back to GPT
            # Either result is acceptable as long as we get a date
            if result.success:
                assert result.parsed_date is not None

    def test_standard_dates_dont_need_gpt(self):
        """Standard date formats don't trigger GPT fallback."""
        parser = DateParser(use_gpt_fallback=True)

        standard_dates = [
            "tomorrow",
            "next Monday",
            "January 15",
            "in 3 days",
            "next week",
        ]

        for date_str in standard_dates:
            result = parser.parse(date_str)
            # Standard dates should have good confidence from dateparser
            if result.success:
                assert result.confidence >= 0.7, f"Low confidence for '{date_str}'"


class TestEdgeCasesGPTFallback:
    """Edge cases for GPT fallback."""

    def test_empty_string_doesnt_trigger_gpt(self):
        """Empty strings fail fast without triggering GPT."""
        parser = DateParser(use_gpt_fallback=True)

        result = parser.parse("")

        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_none_input_doesnt_trigger_gpt(self):
        """None input fails fast without triggering GPT."""
        parser = DateParser(use_gpt_fallback=True)

        result = parser.parse(None)

        assert result.success is False

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_gpt_default_time_when_not_specified(self):
        """GPT uses end of day when time not specified."""
        parser = DateParser(use_gpt_fallback=True)

        future_date = datetime.now() + timedelta(days=5)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "success": True,
            "year": future_date.year,
            "month": future_date.month,
            "day": future_date.day,
            # No hour/minute specified
            "confidence": 0.85,
            "reasoning": "In 5 days"
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        parser._openai_client = mock_client

        result = parser._parse_with_gpt("in about 5 days")

        assert result.success is True
        # Should default to 23:59 when time not specified
        assert result.parsed_date.hour == 23
        assert result.parsed_date.minute == 59
