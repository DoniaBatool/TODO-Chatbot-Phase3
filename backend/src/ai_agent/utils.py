"""Utility functions for AI chatbot enhancements.

Provides:
- Natural language date parsing
- Fuzzy string matching for task lookup
- Response formatting
- Smart suggestions
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import parsedatetime
from dateutil import parser as dateutil_parser
from dateutil.parser import ParserError
from thefuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)

# Initialize calendar parser for natural language dates
cal = parsedatetime.Calendar()


def parse_natural_date(date_str: str) -> Optional[datetime]:
    """Parse natural language date/time strings.

    Supports:
    - "tomorrow", "today", "yesterday"
    - "next Friday", "this Monday"
    - "in 3 days", "in 2 weeks"
    - "at 3pm", "at 14:30"
    - "January 15", "Jan 15 2026"
    - ISO format: "2026-01-15T14:30:00"

    Args:
        date_str: Natural language date string

    Returns:
        datetime object or None if parsing fails

    Examples:
        >>> parse_natural_date("tomorrow")
        datetime(2026, 1, 9, 23, 59, 59)
        >>> parse_natural_date("next Friday at 3pm")
        datetime(2026, 1, 12, 15, 0, 0)
    """
    if not date_str or not isinstance(date_str, str):
        return None

    date_str = date_str.strip()
    current_time = datetime.now()

    # CRITICAL: Check for natural language keywords FIRST (before dateutil parser)
    # This prevents "tomorrow" from being incorrectly parsed as "Nov 29, 2023"
    natural_language_keywords = ['tomorrow', 'today', 'yesterday', 'next', 'this', 'in']
    if any(keyword in date_str.lower() for keyword in natural_language_keywords):
        # Try parsedatetime for natural language FIRST
        try:
            time_struct, parse_status = cal.parse(date_str, sourceTime=current_time)
            if parse_status in [1, 2, 3]:  # Successfully parsed
                parsed = datetime(*time_struct[:6])
                logger.info(f"Parsed natural date '{date_str}' as {parsed} (relative to {current_time})")
                return parsed
        except Exception as e:
            logger.warning(f"Failed to parse natural language date '{date_str}': {e}")

    # Try ISO format
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        pass

    # Try parsedatetime for other natural language (if not already tried)
    if not any(keyword in date_str.lower() for keyword in natural_language_keywords):
        try:
            time_struct, parse_status = cal.parse(date_str, sourceTime=current_time)
            if parse_status in [1, 2, 3]:  # Successfully parsed
                parsed = datetime(*time_struct[:6])
                logger.info(f"Parsed date '{date_str}' as {parsed} (relative to {current_time})")
                return parsed
        except Exception as e:
            logger.warning(f"Failed to parse date with parsedatetime '{date_str}': {e}")

    # Try dateutil parser LAST (handles many formats but can misparse natural language)
    try:
        # CRITICAL FIX: Set default year to current year to avoid parsing "Nov 29" as 2023
        parsed = dateutil_parser.parse(
            date_str,
            fuzzy=True,
            default=current_time  # Use current date as default for missing components
        )

        # VALIDATION: If parsed date is more than 1 year in the past, assume user meant future year
        if parsed < current_time - timedelta(days=365):
            # Date is way in the past - likely a parsing error
            # Try adding current year + 1
            logger.warning(f"Parsed date '{date_str}' as {parsed}, which is >1 year in past. Trying with current/next year...")
            # Re-parse with explicit year correction
            try:
                # If month has passed this year, use next year
                if parsed.month < current_time.month or (parsed.month == current_time.month and parsed.day < current_time.day):
                    parsed = parsed.replace(year=current_time.year + 1)
                else:
                    parsed = parsed.replace(year=current_time.year)
            except:
                pass  # Keep original parsed date if replacement fails

        logger.info(f"Parsed date '{date_str}' as {parsed} using dateutil")
        return parsed
    except (ValueError, TypeError, ParserError):
        pass

    return None


def fuzzy_match_task_title(
    query: str,
    task_titles: List[str],
    threshold: int = 60
) -> List[Tuple[str, int]]:
    """Find task titles that fuzzy match the query.

    Args:
        query: Search query (e.g., "milk task")
        task_titles: List of task titles to search
        threshold: Minimum similarity score (0-100)

    Returns:
        List of (title, score) tuples, sorted by score descending

    Examples:
        >>> fuzzy_match_task_title("buy milk", ["Buy milk", "Get groceries", "Call mom"])
        [("Buy milk", 100), ("Get groceries", 50)]
    """
    if not query or not task_titles:
        return []

    # Use fuzz.token_set_ratio for better matching with word order variations
    matches = process.extract(
        query,
        task_titles,
        scorer=fuzz.token_set_ratio,
        limit=None
    )

    # Filter by threshold and return
    return [(title, score) for title, score in matches if score >= threshold]


def format_task_list_response(tasks: List[Dict[str, Any]]) -> str:
    """Format task list into a rich, readable response.

    Args:
        tasks: List of task dictionaries

    Returns:
        Formatted string with task details

    Example:
        "📋 You have 3 tasks:

        ⏳ #1: Buy milk (high priority) - Due: Tomorrow at 5pm
        ⏳ #2: Call mom (medium priority)
        ✅ #3: Finish report (low priority) - Done!"
    """
    if not tasks:
        return "📋 You don't have any tasks yet!"

    lines = [f"📋 You have {len(tasks)} task{'s' if len(tasks) != 1 else ''}:\n"]

    for task in tasks:
        # Status emoji
        status = "✅" if task.get('completed') else "⏳"

        # Priority indicator
        priority = task.get('priority', 'medium')
        if priority == 'high':
            priority_str = "🔴 high priority"
        elif priority == 'low':
            priority_str = "🟢 low priority"
        else:
            priority_str = "🟡 medium priority"

        # Due date - format with proper date and time
        due_str = ""
        if task.get('due_date'):
            try:
                # Parse ISO format date
                if isinstance(task['due_date'], str):
                    due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                else:
                    due_date = task['due_date']
                
                # Format with proper date and time: "Jan 20, 2026 at 3:00 PM"
                date_str = due_date.strftime("%b %d, %Y at %I:%M %p").lstrip('0')
                due_str = f" - 📅 Due: {date_str}"
            except Exception as e:
                logger.warning(f"Failed to format due date: {e}")
                pass

        # Build line
        line = f"{status} #{task['task_id']}: {task['title']} ({priority_str}){due_str}"
        lines.append(line)

    return "\n".join(lines)


def format_relative_date(dt: datetime) -> str:
    """Format datetime as relative string (e.g., 'Tomorrow at 3pm').

    Args:
        dt: datetime object

    Returns:
        Human-readable relative date string
    """
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    target_day = datetime(dt.year, dt.month, dt.day)

    # Calculate days difference
    days_diff = (target_day - today).days

    # Format time
    time_str = dt.strftime("%I:%M %p").lstrip('0')

    # Relative day
    if days_diff == 0:
        return f"Today at {time_str}"
    elif days_diff == 1:
        return f"Tomorrow at {time_str}"
    elif days_diff == -1:
        return f"Yesterday at {time_str}"
    elif 0 < days_diff < 7:
        day_name = dt.strftime("%A")
        return f"{day_name} at {time_str}"
    else:
        date_str = dt.strftime("%b %d")
        return f"{date_str} at {time_str}"


def detect_batch_operation(message: str) -> Optional[Dict[str, Any]]:
    """Detect if message requests a batch operation.

    Args:
        message: User message

    Returns:
        Dict with operation details or None

    Examples:
        "delete all completed tasks" → {"operation": "delete", "filter": "completed"}
        "mark all high priority as complete" → {"operation": "complete", "filter": "high"}
    """
    message_lower = message.lower()

    # Delete operations
    if "delete all" in message_lower or "remove all" in message_lower:
        if "completed" in message_lower or "done" in message_lower:
            return {"operation": "delete", "filter": "completed"}
        elif "pending" in message_lower or "incomplete" in message_lower:
            return {"operation": "delete", "filter": "pending"}

    # Complete operations
    if "mark all" in message_lower or "complete all" in message_lower:
        if "high" in message_lower or "urgent" in message_lower:
            return {"operation": "complete", "filter": "high"}
        elif "low" in message_lower:
            return {"operation": "complete", "filter": "low"}

    return None


def suggest_priority_from_keywords(title: str, description: str = "") -> str:
    """Suggest task priority based on keywords.

    Args:
        title: Task title
        description: Task description (optional)

    Returns:
        Suggested priority: "high", "medium", or "low"
    """
    text = f"{title} {description}".lower()

    # High priority keywords
    high_keywords = [
        "urgent", "asap", "important", "critical", "emergency",
        "deadline", "today", "now", "immediately", "soon"
    ]

    # Low priority keywords
    low_keywords = [
        "someday", "maybe", "later", "eventually", "minor",
        "trivial", "optional", "nice to have"
    ]

    for keyword in high_keywords:
        if keyword in text:
            return "high"

    for keyword in low_keywords:
        if keyword in text:
            return "low"

    return "medium"


def generate_task_suggestions(title: str, existing_tasks: List[Dict[str, Any]]) -> List[str]:
    """Generate smart suggestions for task creation.

    Args:
        title: New task title
        existing_tasks: List of existing tasks

    Returns:
        List of suggestion strings
    """
    suggestions = []

    # Check for duplicates
    existing_titles = [task['title'] for task in existing_tasks]
    matches = fuzzy_match_task_title(title, existing_titles, threshold=80)

    if matches:
        similar_titles = [m[0] for m in matches[:3]]
        suggestions.append(
            f"⚠️ Similar tasks exist: {', '.join(similar_titles)}"
        )

    # Suggest deadline if none provided
    time_keywords = ["call", "meeting", "appointment", "deadline", "due"]
    if any(keyword in title.lower() for keyword in time_keywords):
        suggestions.append("💡 Consider adding a due date for this task")

    return suggestions


def extract_task_id_from_message(message: str) -> Optional[int]:
    """Extract task ID from natural language message.

    Args:
        message: User message

    Returns:
        Task ID as integer or None

    Examples:
        "update task 5" → 5
        "delete #42" → 42
        "complete task number 7" → 7
    """
    import re

    # Try patterns
    patterns = [
        r'task\s+#?(\d+)',
        r'#(\d+)',
        r'task\s+number\s+(\d+)',
        r'id\s+(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            try:
                return int(match.group(1))
            except:
                pass

    return None


def validate_task_data(
    title: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Tuple[bool, Optional[str]]:
    """Validate task data before creation/update.

    Args:
        title: Task title
        due_date: Task due date

    Returns:
        (is_valid, error_message) tuple
    """
    # Validate title
    if title is not None:
        if not title or len(title.strip()) == 0:
            return False, "Task title cannot be empty"
        if len(title) > 200:
            return False, "Task title too long (max 200 characters)"

    # Validate due date
    if due_date is not None:
        now = datetime.now()
        # Allow past dates (for retroactive tasks)
        # But warn if way in the past
        if due_date < now - timedelta(days=365):
            return False, "Due date is more than a year in the past"
        # Check for unrealistic future dates
        if due_date > now + timedelta(days=365 * 10):
            return False, "Due date is too far in the future"

    return True, None
