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

        # Configure settings for this parse
        settings = self.dateparser_settings.copy()
        if prefer_day_first:
            settings['DATE_ORDER'] = 'DMY'  # Day-Month-Year

        try:
            # Parse using dateparser library
            parsed_date = dateparser.parse(date_string, settings=settings)

            if parsed_date is None:
                return DateParseResult(
                    success=False,
                    parsed_date=None,
                    confidence=0.0,
                    error_message=f"Could not parse date: '{date_string}'",
                    original_text=date_string
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
