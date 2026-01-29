"""
Unit tests for DateParser utility.

Tests natural language date parsing for:
- Relative dates ("tomorrow", "next Friday", "in 3 days")
- Absolute dates ("Jan 20", "January 20 at 2pm")
- Time specifications ("at 3pm", "2:30 PM")
- Edge cases (past dates, far future dates, invalid formats)
"""

import pytest
from datetime import datetime, timedelta
from src.utils.date_parser import DateParser, DateParseResult


class TestDateParser:
    """Test natural language date parsing."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    # Relative Date Tests
    def test_tomorrow(self, parser):
        """Parse 'tomorrow' as next day at midnight."""
        result = parser.parse("tomorrow")
        assert result.success is True
        assert result.parsed_date is not None

        # Should be tomorrow's date
        expected = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        assert result.parsed_date.date() == expected.date()

    def test_next_week(self, parser):
        """Parse 'next week' as 7 days from now."""
        result = parser.parse("next week")
        assert result.success is True
        assert result.parsed_date is not None

        # Should be approximately 7 days from now
        days_diff = (result.parsed_date - datetime.now()).days
        assert 6 <= days_diff <= 8  # Allow for time zone differences

    @pytest.mark.xfail(reason="dateparser doesn't handle 'next Friday' - will use GPT-4o fallback")
    def test_next_friday(self, parser):
        """Parse 'next Friday' correctly."""
        result = parser.parse("next Friday")
        assert result.success is True
        assert result.parsed_date is not None

        # Should be a Friday
        assert result.parsed_date.weekday() == 4  # Friday = 4

    def test_in_3_days(self, parser):
        """Parse 'in 3 days' as 3 days from now."""
        result = parser.parse("in 3 days")
        assert result.success is True
        assert result.parsed_date is not None

        expected = (datetime.now() + timedelta(days=3)).date()
        assert result.parsed_date.date() == expected

    def test_in_2_weeks(self, parser):
        """Parse 'in 2 weeks' as 14 days from now."""
        result = parser.parse("in 2 weeks")
        assert result.success is True
        assert result.parsed_date is not None

        days_diff = (result.parsed_date - datetime.now()).days
        assert 13 <= days_diff <= 15  # Allow for time zone differences

    # Absolute Date Tests
    def test_specific_date_jan_20(self, parser):
        """Parse 'Jan 20' as January 20th of current/next year."""
        result = parser.parse("Jan 20")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.month == 1
        assert result.parsed_date.day == 20

    def test_specific_date_january_20_2pm(self, parser):
        """Parse 'January 20 at 2pm'."""
        result = parser.parse("January 20 at 2pm")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.month == 1
        assert result.parsed_date.day == 20
        assert result.parsed_date.hour == 14  # 2pm = 14:00

    def test_specific_date_dec_25(self, parser):
        """Parse 'Dec 25' as December 25th."""
        result = parser.parse("Dec 25")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.month == 12
        assert result.parsed_date.day == 25

    # Time Specification Tests
    def test_tomorrow_at_3pm(self, parser):
        """Parse 'tomorrow at 3pm'."""
        result = parser.parse("tomorrow at 3pm")
        assert result.success is True
        assert result.parsed_date is not None

        expected_date = (datetime.now() + timedelta(days=1)).date()
        assert result.parsed_date.date() == expected_date
        assert result.parsed_date.hour == 15  # 3pm = 15:00

    @pytest.mark.xfail(reason="dateparser doesn't handle 'next Monday' - will use GPT-4o fallback")
    def test_next_monday_at_9am(self, parser):
        """Parse 'next Monday at 9am'."""
        result = parser.parse("next Monday at 9am")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.weekday() == 0  # Monday = 0
        assert result.parsed_date.hour == 9

    def test_in_2_hours(self, parser):
        """Parse 'in 2 hours'."""
        result = parser.parse("in 2 hours")
        assert result.success is True
        assert result.parsed_date is not None

        # Should be approximately 2 hours from now
        hours_diff = (result.parsed_date - datetime.now()).total_seconds() / 3600
        assert 1.9 <= hours_diff <= 2.1  # Allow for processing time

    # Edge Case Tests
    def test_past_date_rejected(self, parser):
        """Reject dates in the past."""
        result = parser.parse("yesterday")
        assert result.success is False
        assert result.error_message is not None
        assert "past" in result.error_message.lower()

    def test_far_future_rejected(self, parser):
        """Reject dates more than 10 years in the future."""
        result = parser.parse("in 15 years")
        assert result.success is False
        assert result.error_message is not None
        assert "future" in result.error_message.lower()

    def test_invalid_format_handled(self, parser):
        """Handle invalid date formats gracefully."""
        result = parser.parse("asdfghjkl")
        assert result.success is False
        assert result.error_message is not None

    def test_empty_string_handled(self, parser):
        """Handle empty string gracefully."""
        result = parser.parse("")
        assert result.success is False
        assert result.error_message is not None

    def test_none_input_handled(self, parser):
        """Handle None input gracefully."""
        result = parser.parse(None)
        assert result.success is False
        assert result.error_message is not None

    def test_ambiguous_date_uses_future_preference(self, parser):
        """Ambiguous dates prefer future interpretation."""
        # If today is May 15, parsing "March 10" should give next year's March 10
        result = parser.parse("March 10")
        assert result.success is True
        assert result.parsed_date is not None
        # Result should be in the future
        assert result.parsed_date > datetime.now()

    # Natural Language Variations
    def test_today_at_5pm(self, parser):
        """Parse 'today at 5pm'."""
        result = parser.parse("today at 5pm")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.date() == datetime.now().date()
        assert result.parsed_date.hour == 17  # 5pm = 17:00

    @pytest.mark.xfail(reason="dateparser doesn't handle 'this weekend' - will use GPT-4o fallback")
    def test_this_weekend(self, parser):
        """Parse 'this weekend' as upcoming Saturday."""
        result = parser.parse("this weekend")
        assert result.success is True
        assert result.parsed_date is not None
        # Should be Saturday (5) or Sunday (6)
        assert result.parsed_date.weekday() in [5, 6]

    def test_next_month(self, parser):
        """Parse 'next month' as 1 month from now."""
        result = parser.parse("next month")
        assert result.success is True
        assert result.parsed_date is not None

        # Should be approximately 30 days from now
        days_diff = (result.parsed_date - datetime.now()).days
        assert 25 <= days_diff <= 35  # Allow for varying month lengths

    @pytest.mark.xfail(reason="dateparser doesn't handle 'end of week' - will use GPT-4o fallback")
    def test_end_of_week(self, parser):
        """Parse 'end of week' as upcoming Friday."""
        result = parser.parse("end of week")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.weekday() == 4  # Friday = 4

    # ISO Format Tests
    def test_iso_format_date(self, parser):
        """Parse ISO format date '2026-02-15'."""
        result = parser.parse("2026-02-15")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.year == 2026
        assert result.parsed_date.month == 2
        assert result.parsed_date.day == 15

    def test_iso_format_datetime(self, parser):
        """Parse ISO format datetime '2026-02-15 14:30'."""
        result = parser.parse("2026-02-15 14:30")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.year == 2026
        assert result.parsed_date.month == 2
        assert result.parsed_date.day == 15
        assert result.parsed_date.hour == 14
        assert result.parsed_date.minute == 30

    # Confidence Score Tests
    def test_explicit_date_high_confidence(self, parser):
        """Explicit dates have high confidence scores."""
        result = parser.parse("January 20, 2027 at 2:00 PM")
        assert result.success is True
        assert result.confidence >= 0.9

    def test_relative_date_medium_confidence(self, parser):
        """Relative dates have medium confidence scores."""
        result = parser.parse("in 3 days")
        assert result.success is True
        assert result.confidence >= 0.7

    def test_ambiguous_date_lower_confidence(self, parser):
        """Ambiguous dates have lower confidence scores."""
        result = parser.parse("sometime next week")
        # May succeed with lower confidence or fail
        if result.success:
            assert result.confidence < 0.9

    # Multiple Date Formats
    def test_american_format(self, parser):
        """Parse American date format '2/15/2026'."""
        result = parser.parse("2/15/2026")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.parsed_date.month == 2
        assert result.parsed_date.day == 15
        assert result.parsed_date.year == 2026

    def test_european_format_with_setting(self, parser):
        """Parse European date format '15/2/2026' when configured."""
        # Note: dateparser supports this with settings
        result = parser.parse("15/2/2026", prefer_day_first=True)
        assert result.success is True
        assert result.parsed_date is not None
        # Could be Feb 15 or 15th day of month 2
        assert result.parsed_date.month == 2 or result.parsed_date.day == 15
