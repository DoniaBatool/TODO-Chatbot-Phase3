"""
Natural language date parsing utility.

Parses dates like:
- "tomorrow", "next Friday", "in 3 days"
- "Jan 20", "January 20 at 2pm"
- ISO formats: "2026-02-15", "2026-02-15 14:30"

Uses dateparser library with validation:
- Rejects past dates
- Rejects dates >10 years in future
- Returns confidence scores
- GPT-4o fallback for ambiguous/unparseable dates
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
import os
import json
import logging

import dateparser

logger = logging.getLogger(__name__)


@dataclass
class DateParseResult:
    """Result of date parsing operation."""

    success: bool
    parsed_date: Optional[datetime]
    confidence: float
    error_message: Optional[str] = None
    original_text: Optional[str] = None


class DateParser:
    """Parse natural language dates with validation and GPT-4o fallback."""

    # Maximum allowed future date (10 years)
    MAX_FUTURE_YEARS = 10

    # Confidence threshold below which GPT fallback is triggered
    GPT_FALLBACK_THRESHOLD = 0.6

    # Time of day mappings
    TIME_OF_DAY = {
        'morning': (9, 0),      # 9:00 AM
        'noon': (12, 0),        # 12:00 PM
        'afternoon': (14, 0),   # 2:00 PM
        'evening': (18, 0),     # 6:00 PM
        'night': (20, 0),       # 8:00 PM
        'tonight': (20, 0),     # 8:00 PM
        'midnight': (23, 59),   # 11:59 PM
    }

    def __init__(self, use_gpt_fallback: bool = True):
        """
        Initialize date parser with default settings.

        Args:
            use_gpt_fallback: If True, use GPT-4o for ambiguous/failed parses.
                             Requires OPENAI_API_KEY environment variable.
        """
        self.use_gpt_fallback = use_gpt_fallback
        self._openai_client = None
        self.dateparser_settings = {
            'PREFER_DATES_FROM': 'future',  # Prefer future dates for ambiguous cases
            'RETURN_AS_TIMEZONE_AWARE': False,  # Return naive datetime
            'RELATIVE_BASE': datetime.now(),  # Base for relative dates
            'STRICT_PARSING': False  # Allow flexible parsing
        }

    def _preprocess_date_string(self, date_string: str) -> str:
        """
        Preprocess date string to handle complex patterns.

        Handles:
        - "tomorrow morning" → "tomorrow at 9am"
        - "tonight at 8" → "today at 8pm"
        - "next friday at 2:30pm" → normalized format

        Args:
            date_string: Original date string

        Returns:
            Preprocessed date string
        """
        import re
        text = date_string.lower().strip()

        # Handle "tonight" - replace with "today" and ensure PM
        if text.startswith('tonight'):
            text = text.replace('tonight', 'today', 1)
            # If just "tonight", add default time
            if text.strip() == 'today':
                text = 'today at 8pm'
            # If "tonight at X", ensure PM
            elif 'at' in text and not ('am' in text or 'pm' in text):
                text = text + 'pm'

        # Handle time of day words (morning, afternoon, evening, night)
        for time_word, (hour, minute) in self.TIME_OF_DAY.items():
            if time_word in text and time_word != 'tonight':  # tonight handled above
                # Replace "tomorrow morning" with "tomorrow at 9am"
                am_pm = 'am' if hour < 12 else 'pm'
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12
                text = text.replace(time_word, f'at {display_hour}{am_pm}')

        # Handle "at X" without am/pm - assume PM for hours 1-7, AM for 8-11
        at_match = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*$', text)
        if at_match:
            hour = int(at_match.group(1))
            minutes = at_match.group(2) or '00'
            if hour >= 1 and hour <= 7:
                text = re.sub(r'at\s+(\d{1,2})(:\d{2})?\s*$', f'at {hour}:{minutes}pm', text)
            elif hour >= 8 and hour <= 11:
                text = re.sub(r'at\s+(\d{1,2})(:\d{2})?\s*$', f'at {hour}:{minutes}am', text)

        return text

    def _parse_day_with_time(self, date_string: str) -> Optional[datetime]:
        """
        Parse patterns like "next friday at 2:30pm" by splitting day and time.

        Args:
            date_string: Date string with day and time

        Returns:
            Parsed datetime or None
        """
        import re

        # Pattern: [next] [day] at [time]
        pattern = r'(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?'
        match = re.match(pattern, date_string.lower().strip())

        if not match:
            return None

        is_next = match.group(1) is not None
        day_name = match.group(2)
        hour = int(match.group(3))
        minute = int(match.group(4)) if match.group(4) else 0
        am_pm = match.group(5)

        # Determine AM/PM if not specified
        if not am_pm:
            am_pm = 'pm' if hour >= 1 and hour <= 7 else 'am'

        # Convert to 24-hour format
        if am_pm == 'pm' and hour != 12:
            hour += 12
        elif am_pm == 'am' and hour == 12:
            hour = 0

        # Find the next occurrence of the day
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_day = day_map[day_name]
        today = datetime.now()
        current_day = today.weekday()

        days_ahead = target_day - current_day
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        if is_next and days_ahead <= 7:
            # "next friday" means the friday of next week if today is before friday
            if days_ahead < 7:
                days_ahead += 7

        target_date = today + timedelta(days=days_ahead)
        return datetime(target_date.year, target_date.month, target_date.day, hour, minute)

    @property
    def openai_client(self):
        """Lazy initialization of OpenAI client."""
        if self._openai_client is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                try:
                    from openai import OpenAI
                    self._openai_client = OpenAI(api_key=api_key)
                except ImportError:
                    logger.warning("OpenAI package not installed, GPT fallback disabled")
                    self._openai_client = False  # Mark as unavailable
            else:
                logger.debug("OPENAI_API_KEY not set, GPT fallback disabled")
                self._openai_client = False  # Mark as unavailable
        return self._openai_client if self._openai_client else None

    def parse(
        self,
        date_string: Optional[str],
        prefer_day_first: bool = False
    ) -> DateParseResult:
        """
        Parse natural language date string.

        Args:
            date_string: Natural language date (e.g., "tomorrow", "Jan 20 at 2pm")
            prefer_day_first: If True, prefer day-first format (15/2/2026 = Feb 15)

        Returns:
            DateParseResult with success status, parsed date, and confidence

        Examples:
            >>> parser = DateParser()
            >>> result = parser.parse("tomorrow at 3pm")
            >>> assert result.success is True
            >>> assert result.parsed_date.hour == 15

            >>> result = parser.parse("yesterday")
            >>> assert result.success is False  # Past date rejected
        """
        # Handle None or empty input
        if not date_string or not str(date_string).strip():
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message="Date string cannot be empty",
                original_text=date_string
            )

        date_string = str(date_string).strip()
        original_string = date_string  # Keep original for error messages

        # Preprocess to handle complex patterns
        date_string = self._preprocess_date_string(date_string)
        if date_string != original_string.lower().strip():
            logger.debug(f"Preprocessed '{original_string}' → '{date_string}'")

        # Configure settings for this parse
        settings = self.dateparser_settings.copy()
        if prefer_day_first:
            settings['DATE_ORDER'] = 'DMY'  # Day-Month-Year

        try:
            # Parse using dateparser library
            parsed_date = dateparser.parse(date_string, settings=settings)

            # If dateparser fails, try custom day+time parser
            if parsed_date is None:
                parsed_date = self._parse_day_with_time(original_string)

            if parsed_date is None:
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message=f"Could not parse date: '{original_string}'",
                    original_text=original_string
                )

            # Validation 1: Reject past dates
            if parsed_date < datetime.now():
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message="Date cannot be in the past",
                    original_text=date_string
                )

            # Validation 2: Reject far future dates (>10 years)
            max_future_date = datetime.now() + timedelta(days=365 * self.MAX_FUTURE_YEARS)
            if parsed_date > max_future_date:
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message=f"Date cannot be more than {self.MAX_FUTURE_YEARS} years in the future",
                    original_text=date_string
                )

            # Calculate confidence score based on date format specificity
            confidence = self._calculate_confidence(date_string, parsed_date)

            return DateParseResult(
                success=True,
                parsed_date=parsed_date,
                confidence=confidence,
                error_message=None,
                original_text=date_string
            )

        except Exception as e:
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message=f"Error parsing date: {str(e)}",
                original_text=date_string
            )

    def _calculate_confidence(
        self, date_string: str, parsed_date: datetime
    ) -> float:
        """
        Calculate confidence score for parsed date.

        High confidence (0.9+): Explicit dates with year, month, day, time
        Medium confidence (0.7-0.9): Relative dates or dates without time
        Low confidence (<0.7): Ambiguous phrases

        Args:
            date_string: Original input string
            parsed_date: Successfully parsed datetime

        Returns:
            Confidence score between 0.0 and 1.0
        """
        date_lower = date_string.lower()

        # High confidence: ISO format, specific dates with times
        if any(pattern in date_lower for pattern in [
            '-', '/', ':',  # ISO format or explicit separators
            'at ', 'am', 'pm'  # Explicit time
        ]) and any(str(parsed_date.year) in date_string for _ in [1]):  # Explicit year
            return 0.95

        # High confidence: Explicit times
        if any(pattern in date_lower for pattern in ['at ', 'am', 'pm', ':']):
            return 0.9

        # Medium confidence: Common relative dates
        if any(pattern in date_lower for pattern in [
            'tomorrow', 'next week', 'next month',
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday',
            'in ', 'days', 'weeks', 'months'
        ]):
            return 0.8

        # Medium confidence: Month names with day
        if any(month in date_lower for month in [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]):
            return 0.85

        # Lower confidence: Ambiguous phrases
        if any(pattern in date_lower for pattern in [
            'sometime', 'later', 'soon', 'eventually'
        ]):
            return 0.5

        # Default medium confidence for other patterns
        return 0.7

    def _parse_with_gpt(self, date_string: str) -> DateParseResult:
        """
        Use GPT-4o to parse ambiguous date strings.

        This is a fallback when dateparser fails or has low confidence.
        Requires OPENAI_API_KEY environment variable.

        Args:
            date_string: Natural language date to parse

        Returns:
            DateParseResult with GPT-parsed date or error
        """
        if not self.use_gpt_fallback:
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message="GPT fallback disabled",
                original_text=date_string
            )

        client = self.openai_client
        if not client:
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message="OpenAI API not available for date parsing",
                original_text=date_string
            )

        try:
            current_time = datetime.now()
            prompt = f"""Parse the following natural language date/time expression and return ONLY a JSON object.

Current date/time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (use this as reference for relative dates)

Date expression to parse: "{date_string}"

Return a JSON object with these fields:
- "success": true if you can parse the date, false otherwise
- "year": the year (integer)
- "month": the month (1-12)
- "day": the day of month (1-31)
- "hour": the hour (0-23), default 23 if not specified
- "minute": the minute (0-59), default 59 if not specified
- "confidence": your confidence in the interpretation (0.0 to 1.0)
- "reasoning": brief explanation of your interpretation

Example: For "next Tuesday at 3pm" on 2026-01-29, return:
{{"success": true, "year": 2026, "month": 2, "day": 3, "hour": 15, "minute": 0, "confidence": 0.9, "reasoning": "Next Tuesday from Jan 29 is Feb 3"}}

Return ONLY valid JSON, no markdown or explanation outside the JSON."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise date parser. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )

            response_text = response.choices[0].message.content.strip()

            # Clean up response - remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            parsed_json = json.loads(response_text)

            if not parsed_json.get("success", False):
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message=f"GPT could not parse date: {parsed_json.get('reasoning', 'Unknown reason')}",
                    original_text=date_string
                )

            # Construct datetime from parsed components
            parsed_date = datetime(
                year=parsed_json["year"],
                month=parsed_json["month"],
                day=parsed_json["day"],
                hour=parsed_json.get("hour", 23),
                minute=parsed_json.get("minute", 59)
            )

            # Validate: not in past
            if parsed_date < datetime.now():
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message="Date cannot be in the past",
                    original_text=date_string
                )

            # Validate: not too far in future
            max_future_date = datetime.now() + timedelta(days=365 * self.MAX_FUTURE_YEARS)
            if parsed_date > max_future_date:
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message=f"Date cannot be more than {self.MAX_FUTURE_YEARS} years in the future",
                    original_text=date_string
                )

            logger.info(f"GPT parsed '{date_string}' as {parsed_date} (confidence: {parsed_json.get('confidence', 0.85)})")

            return DateParseResult(
                success=True,
                parsed_date=parsed_date,
                confidence=parsed_json.get("confidence", 0.85),
                error_message=None,
                original_text=date_string
            )

        except json.JSONDecodeError as e:
            logger.warning(f"GPT returned invalid JSON for date '{date_string}': {e}")
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message=f"GPT date parsing failed: Invalid response format",
                original_text=date_string
            )
        except Exception as e:
            logger.warning(f"GPT date parsing failed for '{date_string}': {e}")
            return DateParseResult(
                success=False,
                parsed_date=None,
                confidence=0.0,
                error_message=f"GPT date parsing failed: {str(e)}",
                original_text=date_string
            )

    def parse_with_fallback(
        self,
        date_string: Optional[str],
        prefer_day_first: bool = False,
        force_gpt: bool = False
    ) -> DateParseResult:
        """
        Parse date with automatic GPT-4o fallback for ambiguous cases.

        This method tries dateparser first, and falls back to GPT-4o if:
        1. dateparser completely fails to parse
        2. The confidence score is below the threshold (0.6)
        3. force_gpt is True

        Args:
            date_string: Natural language date to parse
            prefer_day_first: If True, prefer day-first format
            force_gpt: If True, skip dateparser and use GPT directly

        Returns:
            DateParseResult with parsed date or error
        """
        if force_gpt:
            return self._parse_with_gpt(date_string)

        # Try dateparser first
        result = self.parse(date_string, prefer_day_first)

        # If dateparser succeeded with good confidence, use it
        if result.success and result.confidence >= self.GPT_FALLBACK_THRESHOLD:
            return result

        # If dateparser failed or low confidence, try GPT fallback
        if self.use_gpt_fallback and self.openai_client:
            logger.debug(f"Trying GPT fallback for '{date_string}' (dateparser confidence: {result.confidence})")
            gpt_result = self._parse_with_gpt(date_string)

            # Use GPT result if successful
            if gpt_result.success:
                return gpt_result

        # Return original result if GPT also failed
        return result
