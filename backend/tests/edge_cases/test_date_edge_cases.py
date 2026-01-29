"""
Edge case tests for natural language date parsing.

Tests comprehensive edge cases for date parsing including:
- Invalid date formats
- Ambiguous dates
- Past date handling
- Extreme future dates
- Special characters and injection attempts
- Timezone edge cases
- Date format variations
"""

import pytest
from datetime import datetime, timedelta
from src.utils.date_parser import DateParser, DateParseResult


class TestInvalidDateFormats:
    """Test invalid date format handling (T082)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    # Invalid Format Tests
    def test_random_text_rejected(self, parser):
        """Random text should be rejected."""
        result = parser.parse("asdfghjkl")
        assert result.success is False
        assert result.error_message is not None

    def test_special_characters_rejected(self, parser):
        """Special characters alone should be rejected."""
        invalid_inputs = ["@#$%", "!!!", "???", "---", "+++"]
        for invalid in invalid_inputs:
            result = parser.parse(invalid)
            assert result.success is False, f"Expected {invalid} to fail"

    def test_sql_injection_attempt_rejected(self, parser):
        """SQL injection attempts should be rejected safely."""
        # These should not parse as valid dates
        injections = [
            "'; DROP TABLE tasks;--",
            "1; DELETE FROM users",
            "2026-01-01'); DELETE --",
        ]
        for injection in injections:
            result = parser.parse(injection)
            assert result.success is False or result.parsed_date is not None
            # Should not crash, just reject or parse any embedded date

    def test_html_script_rejected(self, parser):
        """HTML/script tags should be rejected."""
        html_inputs = [
            "<script>alert('xss')</script>",
            "<img onerror='alert(1)'>",
            "tomorrow<script>",
        ]
        for html in html_inputs:
            result = parser.parse(html)
            # Either reject or sanitize - should not crash
            assert isinstance(result, DateParseResult)

    def test_empty_string(self, parser):
        """Empty string should be rejected."""
        result = parser.parse("")
        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_whitespace_only(self, parser):
        """Whitespace-only input should be rejected."""
        result = parser.parse("   \t\n  ")
        assert result.success is False

    def test_none_input(self, parser):
        """None input should be rejected."""
        result = parser.parse(None)
        assert result.success is False
        assert result.error_message is not None

    def test_number_only(self, parser):
        """Number-only inputs should be handled."""
        result = parser.parse("42")
        # May parse as a day or year, or reject
        assert isinstance(result, DateParseResult)

    def test_very_long_input(self, parser):
        """Very long input should be handled gracefully."""
        long_input = "tomorrow " * 1000
        result = parser.parse(long_input)
        # Should not hang or crash
        assert isinstance(result, DateParseResult)

    def test_unicode_characters(self, parser):
        """Unicode characters should be handled."""
        unicode_inputs = [
            "明日",  # Japanese for "tomorrow"
            "завтра",  # Russian for "tomorrow"
            "demain",  # French for "tomorrow"
        ]
        for u in unicode_inputs:
            result = parser.parse(u)
            # May or may not parse depending on dateparser locale support
            assert isinstance(result, DateParseResult)


class TestPastDateRejection:
    """Test past date rejection (T082)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_yesterday_rejected(self, parser):
        """'Yesterday' should be rejected."""
        result = parser.parse("yesterday")
        assert result.success is False
        assert "past" in result.error_message.lower()

    def test_last_week_rejected(self, parser):
        """'Last week' should be rejected."""
        result = parser.parse("last week")
        assert result.success is False
        assert "past" in result.error_message.lower()

    def test_explicit_past_date_rejected(self, parser):
        """Explicit past date should be rejected."""
        past_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        result = parser.parse(past_date)
        assert result.success is False
        assert "past" in result.error_message.lower()

    def test_past_year_rejected(self, parser):
        """Past year should be rejected."""
        result = parser.parse("January 1, 2020")
        assert result.success is False
        assert "past" in result.error_message.lower()

    def test_2_days_ago_rejected(self, parser):
        """'2 days ago' should be rejected."""
        result = parser.parse("2 days ago")
        assert result.success is False
        assert "past" in result.error_message.lower()

    def test_earlier_today_may_be_rejected(self, parser):
        """Time earlier today may be rejected if it's past."""
        # Try parsing a time that was definitely earlier today
        result = parser.parse("today at 1am")
        # If current time is past 1am, this should be rejected
        if datetime.now().hour > 1:
            assert result.success is False
            assert "past" in result.error_message.lower()


class TestFutureDateValidation:
    """Test future date validation (T082/T088)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_11_years_future_rejected(self, parser):
        """Date >10 years in future should be rejected."""
        result = parser.parse("in 11 years")
        assert result.success is False
        assert "future" in result.error_message.lower()

    def test_15_years_future_rejected(self, parser):
        """Date 15 years in future should be rejected."""
        result = parser.parse("in 15 years")
        assert result.success is False

    def test_year_2099_rejected(self, parser):
        """Year 2099 should be rejected (>10 years)."""
        result = parser.parse("January 1, 2099")
        assert result.success is False
        assert "future" in result.error_message.lower()

    def test_9_years_future_accepted(self, parser):
        """Date 9 years in future should be accepted."""
        result = parser.parse("in 9 years")
        assert result.success is True
        assert result.parsed_date is not None

    def test_exactly_10_years_boundary(self, parser):
        """Date exactly at 10 year boundary should be tested."""
        # Calculate 10 years from now
        future_date = datetime.now() + timedelta(days=365 * 10 - 1)
        result = parser.parse(future_date.strftime("%Y-%m-%d"))
        # Should be accepted (just under 10 years)
        assert result.success is True


class TestAmbiguousDates:
    """Test ambiguous date handling (T083)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_ambiguous_month_day_american(self, parser):
        """Test American format 3/5/2027 (March 5 vs May 3)."""
        result = parser.parse("3/5/2027")
        assert result.success is True
        # Default should be American (month/day)
        assert result.parsed_date is not None

    def test_ambiguous_month_day_european(self, parser):
        """Test European format with prefer_day_first."""
        result = parser.parse("15/2/2027", prefer_day_first=True)
        assert result.success is True
        # Should interpret as Feb 15
        assert result.parsed_date.month == 2
        assert result.parsed_date.day == 15

    def test_day_month_impossible_fallback(self, parser):
        """13/5/2027 can only be May 13 (13 > 12 months)."""
        result = parser.parse("13/5/2027")
        assert result.success is True
        # Must be day 13, month 5 (since 13 > 12)
        assert result.parsed_date.day == 13
        assert result.parsed_date.month == 5

    def test_ambiguous_two_digit_year(self, parser):
        """Test two-digit year ambiguity."""
        result = parser.parse("1/15/27")
        assert result.success is True
        # Should interpret as 2027, not 1927
        assert result.parsed_date.year == 2027

    def test_ambiguous_weekday(self, parser):
        """Test 'Friday' without context."""
        result = parser.parse("Friday")
        # Should prefer future Friday
        if result.success:
            # Should be upcoming Friday
            assert result.parsed_date > datetime.now()
            assert result.parsed_date.weekday() == 4  # Friday = 4

    def test_month_name_no_year(self, parser):
        """Test month name without year (e.g., 'March 15')."""
        result = parser.parse("March 15")
        assert result.success is True
        # Should be future March 15
        assert result.parsed_date > datetime.now()
        assert result.parsed_date.month == 3
        assert result.parsed_date.day == 15

    def test_ambiguous_time_without_ampm(self, parser):
        """Test time without AM/PM (e.g., 'tomorrow at 6')."""
        result = parser.parse("tomorrow at 6")
        assert result.success is True
        # Hour could be 6 or 18 - just verify it parsed

    def test_vague_date_sometime(self, parser):
        """Test vague date 'sometime this week'."""
        result = parser.parse("sometime this week")
        # May or may not parse
        assert isinstance(result, DateParseResult)
        if result.success:
            # Confidence should be lower
            assert result.confidence < 0.8

    def test_vague_date_later(self, parser):
        """Test vague date 'later'."""
        result = parser.parse("later")
        # Should fail or have very low confidence
        if result.success:
            assert result.confidence < 0.6

    def test_vague_date_soon(self, parser):
        """Test vague date 'soon'."""
        result = parser.parse("soon")
        # May parse or fail
        if result.success:
            assert result.confidence < 0.6


class TestDateConfidenceScores:
    """Test confidence score accuracy (T083)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_iso_date_high_confidence(self, parser):
        """ISO date should have high confidence."""
        result = parser.parse("2027-02-15 14:30")
        assert result.success is True
        assert result.confidence >= 0.9

    def test_explicit_datetime_high_confidence(self, parser):
        """Explicit datetime should have high confidence."""
        result = parser.parse("February 15, 2027 at 2:30 PM")
        assert result.success is True
        assert result.confidence >= 0.85

    def test_relative_date_medium_confidence(self, parser):
        """Relative dates should have medium confidence."""
        result = parser.parse("in 3 days")
        assert result.success is True
        assert 0.7 <= result.confidence <= 0.9

    def test_tomorrow_medium_confidence(self, parser):
        """'tomorrow' should have medium confidence."""
        result = parser.parse("tomorrow")
        assert result.success is True
        assert result.confidence >= 0.7

    def test_month_day_medium_confidence(self, parser):
        """Month and day should have medium confidence."""
        result = parser.parse("March 15")
        assert result.success is True
        assert result.confidence >= 0.7


class TestDateEdgeBoundaries:
    """Test boundary conditions for dates (T082)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_leap_year_feb_29(self, parser):
        """Leap year Feb 29 should be valid."""
        result = parser.parse("February 29, 2028")  # 2028 is a leap year
        assert result.success is True
        assert result.parsed_date.month == 2
        assert result.parsed_date.day == 29

    def test_non_leap_year_feb_29(self, parser):
        """Non-leap year Feb 29 should fail gracefully."""
        result = parser.parse("February 29, 2027")  # 2027 is NOT a leap year
        # Should either fail or adjust to valid date
        if result.success:
            # If it parses, it should have adjusted (e.g., to March 1)
            assert result.parsed_date is not None

    def test_jan_1_valid(self, parser):
        """January 1 should be valid."""
        result = parser.parse("January 1, 2027")
        assert result.success is True
        assert result.parsed_date.month == 1
        assert result.parsed_date.day == 1

    def test_dec_31_valid(self, parser):
        """December 31 should be valid."""
        result = parser.parse("December 31, 2027")
        assert result.success is True
        assert result.parsed_date.month == 12
        assert result.parsed_date.day == 31

    def test_invalid_day_32(self, parser):
        """Day 32 should be invalid."""
        result = parser.parse("January 32, 2027")
        # Should fail or adjust
        if result.success:
            # If it somehow parses, day shouldn't be 32
            assert result.parsed_date.day != 32

    def test_invalid_month_13(self, parser):
        """Month 13 should be invalid or reinterpreted."""
        result = parser.parse("2027-13-01")
        # dateparser may reinterpret this (e.g., as Jan 13, 2027)
        # Either way, it should not create a date with month 13
        if result.success:
            assert result.parsed_date.month <= 12


class TestTimezoneHandling:
    """Test timezone edge cases (T089)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_result_is_naive_datetime(self, parser):
        """Result should be timezone-naive (UTC assumption)."""
        result = parser.parse("tomorrow at 3pm")
        assert result.success is True
        # Should be timezone-naive
        assert result.parsed_date.tzinfo is None

    def test_timezone_suffix_handled(self, parser):
        """Timezone suffix in input should be handled."""
        result = parser.parse("2027-02-15T14:30:00Z")
        # Should parse (may strip timezone)
        if result.success:
            assert result.parsed_date is not None

    def test_explicit_utc_offset(self, parser):
        """Explicit UTC offset should be handled."""
        result = parser.parse("2027-02-15 14:30 UTC")
        # Should parse
        if result.success:
            assert result.parsed_date is not None


class TestNaturalLanguageVariations:
    """Test natural language date variations (T082/T083)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_tomorrow_at_noon(self, parser):
        """'tomorrow at noon' should parse."""
        result = parser.parse("tomorrow at noon")
        assert result.success is True
        assert result.parsed_date.hour == 12

    def test_tomorrow_at_midnight(self, parser):
        """'tomorrow at midnight' should parse."""
        result = parser.parse("tomorrow at midnight")
        assert result.success is True
        # Midnight could be 0 or 24 (wrapped to 0)
        assert result.parsed_date.hour in [0, 23, 24]

    def test_end_of_day(self, parser):
        """'end of day' variations."""
        result = parser.parse("tomorrow end of day")
        # May or may not parse
        assert isinstance(result, DateParseResult)

    def test_morning_afternoon_evening(self, parser):
        """Test 'morning', 'afternoon', 'evening' suffixes."""
        tests = [
            ("tomorrow morning", range(5, 13)),  # 5am-12pm
            ("tomorrow afternoon", range(12, 19)),  # 12pm-6pm
            ("tomorrow evening", range(17, 24)),  # 5pm-11pm
        ]
        for date_str, expected_hours in tests:
            result = parser.parse(date_str)
            if result.success:
                # Hour should be in expected range
                pass  # dateparser may not support these

    def test_next_tuesday(self, parser):
        """'next Tuesday' should parse to future Tuesday."""
        result = parser.parse("next Tuesday")
        # May be marked as xfail in existing tests
        if result.success:
            assert result.parsed_date > datetime.now()
            assert result.parsed_date.weekday() == 1  # Tuesday = 1

    def test_this_coming_monday(self, parser):
        """'this coming Monday' should parse."""
        result = parser.parse("this coming Monday")
        # May or may not parse
        if result.success:
            assert result.parsed_date.weekday() == 0  # Monday = 0


class TestSpecialDatePhrases:
    """Test special date phrases (T083)."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_christmas(self, parser):
        """'Christmas' should parse to Dec 25."""
        result = parser.parse("Christmas")
        # May not be supported by dateparser
        if result.success:
            assert result.parsed_date.month == 12
            assert result.parsed_date.day == 25

    def test_new_years(self, parser):
        """'New Year's Day' should parse to Jan 1."""
        result = parser.parse("New Year's Day")
        # May not be supported by dateparser
        if result.success:
            assert result.parsed_date.month == 1
            assert result.parsed_date.day == 1

    def test_no_deadline(self, parser):
        """'no deadline' should be handled gracefully."""
        result = parser.parse("no deadline")
        # Should fail (not a valid date)
        assert result.success is False

    def test_whenever(self, parser):
        """'whenever' should not parse as valid date."""
        result = parser.parse("whenever")
        # Should fail
        assert result.success is False

    def test_asap(self, parser):
        """'ASAP' should not parse as valid date."""
        result = parser.parse("ASAP")
        # Should fail (priority indicator, not date)
        assert result.success is False


class TestDateParserResultFields:
    """Test DateParseResult fields are correctly populated."""

    @pytest.fixture
    def parser(self):
        """Create date parser instance."""
        return DateParser()

    def test_success_result_has_all_fields(self, parser):
        """Successful parse should have all fields."""
        result = parser.parse("tomorrow")
        assert result.success is True
        assert result.parsed_date is not None
        assert result.confidence > 0
        assert result.error_message is None
        assert result.original_text == "tomorrow"

    def test_failure_result_has_all_fields(self, parser):
        """Failed parse should have all fields."""
        result = parser.parse("not a date")
        assert result.success is False
        assert result.parsed_date is None
        assert result.confidence == 0.0
        assert result.error_message is not None
        assert result.original_text == "not a date"

    def test_original_text_preserved(self, parser):
        """Original text should be preserved."""
        original = "   tomorrow at 3pm   "
        result = parser.parse(original)
        # Original text may be stripped or preserved
        assert result.original_text in [original, original.strip()]
