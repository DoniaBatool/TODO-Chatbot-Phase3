"""Intent Detection Middleware for Forced Tool Execution.

This module provides DETERMINISTIC intent detection to force tool calls
when user intent is clear, bypassing unreliable AI system prompt interpretation.

Strategy: Parse user message with regex patterns to detect operations
(update, delete, complete), extract parameters, and FORCE tool execution.
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Intent:
    """Detected user intent with extracted parameters."""

    def __init__(
        self,
        operation: str,
        task_id: Optional[int] = None,
        task_title: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        needs_confirmation: bool = False
    ):
        self.operation = operation  # "update", "delete", "complete", etc.
        self.task_id = task_id
        self.task_title = task_title
        self.params = params or {}
        self.confidence = confidence
        self.needs_confirmation = needs_confirmation  # If True, ask user first

    def __repr__(self):
        return (
            f"Intent(operation={self.operation}, task_id={self.task_id}, "
            f"task_title={self.task_title}, params={self.params}, "
            f"needs_confirmation={self.needs_confirmation})"
        )


class IntentDetector:
    """Deterministic intent detector using regex patterns."""

    # Pattern for detecting task ID mentions
    TASK_ID_PATTERN = re.compile(
        r'task\s+#?(\d+)|#(\d+)|id\s+(\d+)',
        re.IGNORECASE
    )

    # Patterns for UPDATE intent
    UPDATE_PATTERNS = [
        re.compile(r'update\s+(?:the\s+)?task', re.IGNORECASE),
        re.compile(r'change\s+(?:the\s+)?task', re.IGNORECASE),
        re.compile(r'edit\s+(?:the\s+)?task', re.IGNORECASE),
        re.compile(r'modify\s+(?:the\s+)?task', re.IGNORECASE),
    ]

    # Patterns for DELETE intent
    DELETE_PATTERNS = [
        re.compile(r'delete\s+(?:the\s+)?task', re.IGNORECASE),
        re.compile(r'remove\s+(?:the\s+)?task', re.IGNORECASE),
        re.compile(r'khatam\s+(?:karo|kar|do)', re.IGNORECASE),
    ]

    # Patterns for COMPLETE intent
    COMPLETE_PATTERNS = [
        re.compile(r'mark\s+(?:task\s+)?.*?\s+as\s+(?:done|complete)', re.IGNORECASE),
        re.compile(r'complete\s+task', re.IGNORECASE),
        re.compile(r'finish(?:ed)?\s+task', re.IGNORECASE),
    ]

    # Patterns for INCOMPLETE intent (mark as not done/pending)
    INCOMPLETE_PATTERNS = [
        re.compile(r'mark\s+(?:task\s+)?.*?\s+as\s+(?:incomplete|not\s+done|pending|undone)', re.IGNORECASE),
        re.compile(r'unmark\s+task', re.IGNORECASE),
        re.compile(r'uncomplete\s+task', re.IGNORECASE),
        re.compile(r'set\s+(?:task\s+)?.*?\s+to\s+(?:incomplete|pending)', re.IGNORECASE),
    ]

    # Priority keywords
    PRIORITY_MAP = {
        'high': ['high', 'urgent', 'important', 'critical', 'asap', 'zaruri'],
        'medium': ['medium', 'normal', 'regular'],
        'low': ['low', 'minor', 'trivial', 'later', 'someday']
    }

    # Date/deadline keywords
    DATE_KEYWORDS = [
        'tomorrow', 'today', 'deadline', 'due', 'by', 'until', 'kal',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'next week', 'next month'
    ]

    # Confirmation keywords
    CONFIRM_YES = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'haan', 'han', 'theek', 'bilkul']
    CONFIRM_NO = ['no', 'nah', 'nope', 'cancel', 'nahi', 'na', 'mat']


    def detect_intent(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Detect user intent from message with conversation context.

        Args:
            message: Current user message
            conversation_history: Previous conversation turns

        Returns:
            Intent object if detected, None otherwise
        """
        message_lower = message.lower().strip()

        # STEP 1: Check if user is responding to a confirmation question
        pending_confirmation = self._check_pending_confirmation(conversation_history)
        if pending_confirmation:
            # User is responding yes/no to a previous confirmation question
            is_yes = self._is_confirmation_response(message_lower, confirm=True)
            is_no = self._is_confirmation_response(message_lower, confirm=False)

            if is_yes:
                # User confirmed - return intent with needs_confirmation=False
                return Intent(
                    operation=pending_confirmation['operation'],
                    task_id=pending_confirmation.get('task_id'),
                    task_title=pending_confirmation.get('task_title'),
                    params=pending_confirmation.get('params'),
                    needs_confirmation=False  # Confirmed! Execute now
                )
            elif is_no:
                # User cancelled - return None (don't execute)
                logger.info(f"User cancelled operation: {pending_confirmation['operation']}")
                return None

        # STEP 2: Check for UPDATE intent
        if self._matches_any_pattern(message, self.UPDATE_PATTERNS):
            return self._detect_update_intent(message, message_lower, conversation_history)

        # STEP 3: Check for DELETE intent
        if self._matches_any_pattern(message, self.DELETE_PATTERNS):
            return self._detect_delete_intent(message, message_lower, conversation_history)

        # STEP 4: Check for COMPLETE intent
        if self._matches_any_pattern(message, self.COMPLETE_PATTERNS):
            return self._detect_complete_intent(message, message_lower, conversation_history)

        # STEP 5: Check for INCOMPLETE intent
        if self._matches_any_pattern(message, self.INCOMPLETE_PATTERNS):
            return self._detect_incomplete_intent(message, message_lower, conversation_history)

        return None


    def _is_confirmation_response(self, message_lower: str, confirm: bool) -> bool:
        """Check if message is a confirmation (yes) or cancellation (no).

        Args:
            message_lower: Lowercase message
            confirm: True to check for "yes", False to check for "no"

        Returns:
            True if message matches confirmation/cancellation keywords
        """
        keywords = self.CONFIRM_YES if confirm else self.CONFIRM_NO
        # Check if message is ONLY a confirmation word (or very short with confirmation)
        words = message_lower.split()
        if len(words) <= 3:  # Short message like "yes", "yes please", "haan kar do"
            return any(keyword in message_lower for keyword in keywords)
        return False


    def _check_pending_confirmation(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Check if last assistant message was asking for confirmation.

        Looks for patterns like:
        - "Are you sure?"
        - "Kya aap sure hain?"
        - "Should I delete task X?"
        - "Delete this task?"

        Returns:
            Dict with operation details if pending confirmation, None otherwise
        """
        if not conversation_history:
            return None

        # Check last assistant message
        for msg in reversed(conversation_history[-4:]):
            if msg.get('role') == 'assistant':
                content = msg.get('content', '').lower()

                # Look for confirmation question patterns
                confirmation_patterns = [
                    r'sure|confirm|certain',
                    r'kya.*sure|pakka',
                    r'should i|shall i',
                    r'delete.*\?',
                    r'update.*\?',
                    r'complete.*\?',
                    r'mark.*\?'
                ]

                is_asking_confirmation = any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in confirmation_patterns
                )

                if is_asking_confirmation:
                    # Extract task ID if mentioned
                    task_id_match = re.search(r'task\s+#?(\d+)', content)
                    task_id = int(task_id_match.group(1)) if task_id_match else None

                    # Determine operation type
                    operation = None
                    if 'delete' in content or 'remove' in content:
                        operation = 'delete'
                    elif 'update' in content or 'change' in content or 'edit' in content:
                        operation = 'update'
                    elif 'incomplete' in content or 'not done' in content or 'pending' in content or 'undone' in content:
                        operation = 'incomplete'
                    elif 'complete' in content or 'mark' in content or 'done' in content:
                        operation = 'complete'

                    if operation:
                        return {
                            'operation': operation,
                            'task_id': task_id,
                            'task_title': None,
                            'params': {}
                        }

                break  # Only check most recent assistant message

        return None


    def _matches_any_pattern(self, message: str, patterns: List[re.Pattern]) -> bool:
        """Check if message matches any of the given patterns."""
        return any(pattern.search(message) for pattern in patterns)


    def _extract_task_id(self, message: str) -> Optional[int]:
        """Extract task ID from message."""
        match = self.TASK_ID_PATTERN.search(message)
        if match:
            # Try all groups (because regex has multiple capturing groups)
            for group in match.groups():
                if group:
                    try:
                        return int(group)
                    except ValueError:
                        pass
        return None


    def _extract_task_title(self, message: str, message_lower: str) -> Optional[str]:
        """Extract task title mention from message.

        Looks for patterns like:
        - "update the grocery task"
        - "delete buy milk task"
        - "update task: buy fruits"
        """
        # Pattern 1: "the [title] task"
        match = re.search(r'the\s+(.+?)\s+task', message_lower)
        if match:
            return match.group(1).strip()

        # Pattern 2: "task [title]" or "task: [title]"
        match = re.search(r'task:?\s+(.+?)(?:\s+|$)', message_lower)
        if match:
            title = match.group(1).strip()
            # Remove trailing words like "to", "with", etc.
            title = re.sub(r'\s+(to|with|and)\s.*', '', title)
            return title

        return None


    def _get_context_task_id(self, conversation_history: List[Dict[str, str]]) -> Optional[int]:
        """Get task ID from recent conversation context.

        Looks at last assistant message for patterns like:
        - "I found task 8"
        - "Task 5 is..."
        """
        if not conversation_history:
            return None

        # Check last 2 assistant messages
        for msg in reversed(conversation_history[-4:]):
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                # Look for "task ID" mentions
                match = re.search(r'task\s+#?(\d+)', content, re.IGNORECASE)
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        pass

        return None


    def _detect_update_intent(
        self,
        message: str,
        message_lower: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Detect UPDATE intent and extract parameters."""

        # Extract task identifier (ID or title)
        task_id = self._extract_task_id(message)
        task_title = self._extract_task_title(message, message_lower) if not task_id else None

        # If neither found, check conversation context
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)

        # If still not found, this is likely first turn asking what to update
        if not task_id and not task_title:
            return None

        # Extract update parameters from message
        params = {}

        # Check if user is providing UPDATE DETAILS (not just asking what to update)
        # This is CRITICAL: Detect if user is giving all details at once
        has_update_details = any([
            'change' in message_lower and 'to' in message_lower,
            'priority' in message_lower,
            'deadline' in message_lower,
            'description' in message_lower,
            'title' in message_lower,
        ])

        if not has_update_details:
            # User is just asking to update, not providing details yet
            # Return intent WITHOUT params to ask clarifying questions
            return Intent(
                operation="update_ask",
                task_id=task_id,
                task_title=task_title,
                params=None
            )

        # User is providing update details - extract them!

        # Extract new title
        # Pattern: "change (it to|title to|to) [new title]"
        title_match = re.search(
            r'change\s+(?:it\s+to|title\s+to|to)\s+(.+?)(?:,|\s+with|\s+and|$)',
            message_lower
        )
        if title_match:
            params['title'] = title_match.group(1).strip()

        # Extract priority
        for priority_level, keywords in self.PRIORITY_MAP.items():
            if any(keyword in message_lower for keyword in keywords):
                params['priority'] = priority_level
                break

        # Extract deadline/due date
        if any(keyword in message_lower for keyword in self.DATE_KEYWORDS):
            # Extract the deadline phrase
            deadline_match = re.search(
                r'deadline\s+(?:is\s+)?(.+?)(?:,|\s+with|\s+and|description|$)',
                message_lower
            )
            if deadline_match:
                params['due_date'] = deadline_match.group(1).strip()
            elif 'tomorrow' in message_lower:
                params['due_date'] = 'tomorrow'
            elif 'today' in message_lower:
                params['due_date'] = 'today'

        # Extract description
        description_match = re.search(
            r'description:?\s+(.+?)(?:,|\s+and|$)',
            message_lower
        )
        if description_match:
            params['description'] = description_match.group(1).strip()

        # Check if "remove deadline" mentioned
        if re.search(r'remove\s+deadline|no\s+deadline|cancel\s+deadline', message_lower):
            params['due_date'] = None  # Explicitly remove deadline

        logger.info(
            f"Detected UPDATE intent: task_id={task_id}, task_title={task_title}, "
            f"params={params}"
        )

        # If user provided update details, execute immediately (no confirmation)
        # Otherwise, ask clarifying questions first
        needs_confirmation = not bool(params)

        return Intent(
            operation="update",
            task_id=task_id,
            task_title=task_title,
            params=params if params else None,
            needs_confirmation=needs_confirmation
        )


    def _detect_delete_intent(
        self,
        message: str,
        message_lower: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Detect DELETE intent and extract task identifier."""

        task_id = self._extract_task_id(message)
        task_title = self._extract_task_title(message, message_lower) if not task_id else None

        # Check conversation context if not found
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)

        if not task_id and not task_title:
            return None

        logger.info(
            f"Detected DELETE intent: task_id={task_id}, task_title={task_title}"
        )

        return Intent(
            operation="delete",
            task_id=task_id,
            task_title=task_title,
            needs_confirmation=True  # Always ask before deleting
        )


    def _detect_complete_intent(
        self,
        message: str,
        message_lower: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Detect COMPLETE intent and extract task identifier."""

        task_id = self._extract_task_id(message)
        task_title = self._extract_task_title(message, message_lower) if not task_id else None

        # Check conversation context
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)

        if not task_id and not task_title:
            return None

        logger.info(
            f"Detected COMPLETE intent: task_id={task_id}, task_title={task_title}"
        )

        return Intent(
            operation="complete",
            task_id=task_id,
            task_title=task_title,
            needs_confirmation=True  # Always ask before marking complete
        )


    def _detect_incomplete_intent(
        self,
        message: str,
        message_lower: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Detect INCOMPLETE intent (mark task as not done/pending)."""

        task_id = self._extract_task_id(message)
        task_title = self._extract_task_title(message, message_lower) if not task_id else None

        # Check conversation context
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)

        if not task_id and not task_title:
            return None

        logger.info(
            f"Detected INCOMPLETE intent: task_id={task_id}, task_title={task_title}"
        )

        # Use update operation with completed=False
        return Intent(
            operation="incomplete",  # Will be handled as update with completed=False
            task_id=task_id,
            task_title=task_title,
            params={"completed": False},
            needs_confirmation=True  # Always ask before marking incomplete
        )


# Global detector instance
detector = IntentDetector()


def detect_user_intent(
    message: str,
    conversation_history: List[Dict[str, str]]
) -> Optional[Intent]:
    """Convenience function to detect user intent.

    Args:
        message: User's current message
        conversation_history: Previous conversation turns

    Returns:
        Intent object if detected, None otherwise

    Example:
        >>> intent = detect_user_intent(
        ...     "update task 5 to high priority",
        ...     []
        ... )
        >>> assert intent.operation == "update"
        >>> assert intent.task_id == 5
        >>> assert intent.params['priority'] == 'high'
    """
    return detector.detect_intent(message, conversation_history)
