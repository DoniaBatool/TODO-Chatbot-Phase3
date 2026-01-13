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
        - "update the task: go to saturday class"
        - "delete the task go to saturday class this week"
        - "update buy milk" (without "task" word)
        """
        # Pattern 1: "the task [title]" or "the task: [title]" - MOST COMMON
        # "update the task: go to saturday class" or "delete the task go to saturday class this week"
        # Capture everything after "the task" until end or next operation keyword
        # Use DOTALL to match across newlines, and make sure we capture the full title
        match = re.search(
            r'the\s+task:?\s+(.+?)(?=\s+(?:to\s+(?:update|set|change)|title\s+to|priority\s+to|deadline|description|update|delete|complete|mark|$))',
            message_lower,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            title = match.group(1).strip()
            # Remove trailing update keywords but keep the full title
            title = re.sub(r'\s+(to\s+(?:update|set|change)|title\s+to|priority\s+to|deadline|description|update|delete|complete|mark)\s+.*$', '', title, flags=re.IGNORECASE)
            # Remove "the" prefix if it's the only word or at the start
            if title.lower().startswith('the '):
                title = title[4:].strip()
            # Don't return if title is just "the"
            if title and len(title) > 2 and title.lower() != 'the':  # Valid title
                return title

        # Pattern 2: "the [title] task" - "update the grocery task"
        match = re.search(r'the\s+(.+?)\s+task', message_lower)
        if match:
            title = match.group(1).strip()
            if title and len(title) > 2 and title.lower() != 'the':  # Valid title, not just "the"
                return title

        # Pattern 3: "task [title]" or "task: [title]" - "update task: buy fruits"
        match = re.search(r'task:?\s+(.+?)(?:\s+to\s+|\s+title\s+to\s+|$|update|delete|priority|deadline|description)', message_lower)
        if match:
            title = match.group(1).strip()
            # Remove "the" prefix if present
            title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
            # Remove trailing words like "to", "with", etc. but keep title
            title = re.sub(r'\s+(to|with|and|title|priority|deadline|description|update|delete)\s.*', '', title, flags=re.IGNORECASE)
            if title and len(title) > 2 and not title.isdigit():  # Valid title, not a number
                return title

        # Pattern 4: After update/delete/complete, extract title directly
        # "update buy milk" or "delete grocery shopping" or "delete the task go to saturday class this week"
        for op in ['update', 'delete', 'remove', 'complete', 'mark']:
            if op in message_lower:
                # Handle "delete the task [full title]" or "update the task [full title]" pattern
                # Capture everything after "the task" until end of message or next operation keyword
                match = re.search(
                    rf'{op}\s+the\s+task\s+(.+?)(?=\s+(?:to\s+(?:update|set|change)|title\s+to|priority\s+to|deadline|description|update|delete|complete|mark|$))',
                    message_lower,
                    re.IGNORECASE | re.DOTALL
                )
                if match:
                    title = match.group(1).strip()
                    # Remove "the" if it's the only word or at the start
                    if title.lower().startswith('the '):
                        title = title[4:].strip()
                    # Don't return if title is just "the"
                    if title and len(title) > 2 and title.lower() != 'the' and not title.isdigit():
                        return title
                
                # Handle "update [title]" pattern (without "task" word) - but only if "task" not mentioned
                if 'task' not in message_lower:
                    match = re.search(
                        rf'{op}\s+(.+?)(?=\s+(?:to\s+(?:update|set|change)|title\s+to|priority\s+to|deadline|description|update|delete|complete|mark|$))',
                        message_lower,
                        re.IGNORECASE | re.DOTALL
                    )
                    if match:
                        title = match.group(1).strip()
                        # Remove common stop words
                        title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
                        # Remove trailing update keywords
                        title = re.sub(r'\s+(to|with|and|title|priority|deadline|description|update|delete|complete|mark)\s+.*$', '', title, flags=re.IGNORECASE)
                        if title and len(title) > 2 and not title.isdigit() and title.lower() != 'the':
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

    def _get_context_task_title(self, conversation_history: List[Dict[str, str]]) -> Optional[str]:
        """Get task title from recent conversation context.

        Looks at recent messages for task title mentions.
        """
        if not conversation_history:
            return None

        # Check last few messages for task title
        for msg in reversed(conversation_history[-6:]):
            content = msg.get('content', '').lower()
            # Pattern: "task 'title'" or "task \"title\""
            match = re.search(r"task\s+['\"](.+?)['\"]", content)
            if match:
                title = match.group(1).strip()
                if title and len(title) > 2:
                    return title
            # Pattern: "update the task: title" or "task: title"
            match = re.search(r'(?:update|delete|complete).*?task:?\s+(.+?)(?:\s+update|\s+delete|\s+complete|$)', content)
            if match:
                title = match.group(1).strip()
                if title and len(title) > 2 and title.lower() != 'the':
                    return title

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

        # If neither found, check conversation context for recently mentioned task
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)
            # Also try to get task title from context
            if not task_id:
                task_title = self._get_context_task_title(conversation_history)

        # If still not found but user is providing update details (like "update the title: X"),
        # this might be a follow-up to a previous update request - check conversation context
        if not task_id and not task_title:
            # Check recent conversation for task mentions in both user and assistant messages
            for msg in reversed(conversation_history[-10:]):
                content = msg.get('content', '').lower()
                role = msg.get('role', '')
                
                # Pattern 1: "update the task: [title]" or "i want to update the task: [title]"
                task_match = re.search(r'(?:update|want\s+to\s+update|updateing)\s+(?:the\s+)?task:?\s+(.+?)(?:\s+update|\s+title|\s+priority|\s+deadline|$)', content, re.IGNORECASE | re.DOTALL)
                if task_match:
                    potential_title = task_match.group(1).strip()
                    # Remove "the" prefix
                    potential_title = re.sub(r'^(the|a|an)\s+', '', potential_title, flags=re.IGNORECASE)
                    if potential_title and len(potential_title) > 2 and potential_title.lower() != 'the':
                        task_title = potential_title
                        logger.info(f"Found task title from context: '{task_title}'")
                        break
                
                # Pattern 2: "task 'title'" or "task \"title\"" in assistant message
                if role == 'assistant':
                    task_match = re.search(r"task\s+['\"](.+?)['\"]|task\s+#?(\d+)", content)
                    if task_match:
                        if task_match.group(1):  # Title found
                            task_title = task_match.group(1).strip()
                            logger.info(f"Found task title from assistant context: '{task_title}'")
                            break
                        elif task_match.group(2):  # ID found
                            try:
                                task_id = int(task_match.group(2))
                                logger.info(f"Found task ID from assistant context: {task_id}")
                                break
                            except:
                                pass
                
                # Pattern 3: Look for task mentions in assistant's confirmation messages
                # "Task 'go to saturday class' mein kya update karna hai?"
                if role == 'assistant':
                    task_match = re.search(r"task\s+['\"](.+?)['\"]", content)
                    if task_match:
                        potential_title = task_match.group(1).strip()
                        if potential_title and len(potential_title) > 2:
                            task_title = potential_title
                            logger.info(f"Found task title from assistant confirmation: '{task_title}'")
                            break

        # If still not found, this is likely first turn asking what to update
        if not task_id and not task_title:
            return None

        # Extract update parameters from message
        params = {}

        # Check if user is providing UPDATE DETAILS (not just asking what to update)
        # This is CRITICAL: Detect if user is giving all details at once
        has_update_details = any([
            'change' in message_lower and 'to' in message_lower,
            'update' in message_lower and ('to' in message_lower or ':' in message_lower),
            'set' in message_lower and ('to' in message_lower or 'as' in message_lower),
            'priority' in message_lower,
            'deadline' in message_lower or 'due date' in message_lower or 'due_date' in message_lower,
            'description' in message_lower,
            ('title' in message_lower and ('to' in message_lower or ':' in message_lower)),
            'remove' in message_lower and ('deadline' in message_lower or 'due date' in message_lower),
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
        # Patterns: "change title to X", "update title to X", "set title to X", "update the title: X"
        title_patterns = [
            r'(?:change|update|set)\s+(?:the\s+)?title\s*(?:to|:)\s*(.+?)(?:,|\s+with|\s+and|$|priority|deadline|description)',
            r'(?:change|update)\s+(?:it\s+to|to)\s+(.+?)(?:,|\s+with|\s+and|$|priority|deadline|description)',
            r'title\s*(?:to|:)\s*(.+?)(?:,|\s+with|\s+and|$|priority|deadline|description)',
            r'update\s+the\s+title:?\s*(.+?)(?:,|\s+with|\s+and|$|priority|deadline|description)',
        ]
        for pattern in title_patterns:
            title_match = re.search(pattern, message_lower)
            if title_match:
                title = title_match.group(1).strip()
                # Clean up title - remove trailing keywords
                title = re.sub(r'\s+(priority|deadline|description|and|with|update|delete|complete|mark).*$', '', title, flags=re.IGNORECASE)
                if title and len(title) > 1:
                    params['title'] = title
                    break

        # Extract priority
        for priority_level, keywords in self.PRIORITY_MAP.items():
            if any(keyword in message_lower for keyword in keywords):
                params['priority'] = priority_level
                break

        # Extract deadline/due date - check for remove first
        if re.search(r'remove\s+(?:the\s+)?(?:deadline|due\s+date|due_date)|no\s+(?:deadline|due\s+date)|cancel\s+(?:deadline|due\s+date)', message_lower):
            params['due_date'] = None  # Explicitly remove deadline
        elif any(keyword in message_lower for keyword in self.DATE_KEYWORDS) or 'due date' in message_lower or 'deadline' in message_lower:
            # Extract the deadline phrase - multiple patterns
            deadline_patterns = [
                r'(?:set|update|change)\s+(?:the\s+)?(?:due\s+date|deadline)\s+(?:for|to|as)\s+(.+?)(?:,|\s+with|\s+and|description|title|priority|$)',
                r'due\s+date\s+(?:for|to|is|as)\s+(.+?)(?:,|\s+with|\s+and|description|title|priority|$)',
                r'deadline\s+(?:is\s+)?(.+?)(?:,|\s+with|\s+and|description|title|priority|$)',
            ]
            for pattern in deadline_patterns:
                deadline_match = re.search(pattern, message_lower)
                if deadline_match:
                    params['due_date'] = deadline_match.group(1).strip()
                    break
            # Fallback to simple keywords
            if 'due_date' not in params:
                if 'tomorrow' in message_lower:
                    params['due_date'] = 'tomorrow'
                elif 'today' in message_lower:
                    params['due_date'] = 'today'
                # Try to extract any date-like string
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+\w+\s+\d{4})', message_lower)
                if date_match:
                    params['due_date'] = date_match.group(1).strip()

        # Extract description
        description_match = re.search(
            r'description:?\s+(.+?)(?:,|\s+and|title|priority|deadline|due\s+date|$)',
            message_lower
        )
        if description_match:
            params['description'] = description_match.group(1).strip()

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

        # Enhanced title extraction for complete patterns
        # Patterns: "mark buy milk as complete", "complete grocery task", "mark the grocery task as done"
        if not task_id and not task_title:
            # Pattern 1: "mark [title] as complete/done"
            title_match = re.search(
                r'mark\s+(?:the\s+)?(.+?)\s+as\s+(?:complete|done)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                # Remove "task" if present
                title = re.sub(r'\s+task\s*$', '', title, flags=re.IGNORECASE)
                # Remove common words
                title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

        # Pattern 2: "complete [title] task" or "complete [title]"
        if not task_id and not task_title:
            title_match = re.search(
                r'complete\s+(?:the\s+)?(.+?)(?:\s+task|$)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                # Remove trailing words
                title = re.sub(r'\s+(task|as|complete|done).*', '', title, flags=re.IGNORECASE)
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

        # Pattern 3: "mark task [title] as complete"
        if not task_id and not task_title:
            title_match = re.search(
                r'mark\s+task\s+(.+?)\s+as\s+(?:complete|done)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

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

        # Enhanced title extraction for incomplete patterns
        # Patterns: "mark buy milk as incomplete", "mark grocery task as pending", "mark task buy milk as incomplete"
        if not task_id and not task_title:
            # Pattern 1: "mark [title] as incomplete/pending/not done"
            title_match = re.search(
                r'mark\s+(?:the\s+)?(.+?)\s+as\s+(?:incomplete|pending|not\s+done|undone)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                # Remove "task" if present
                title = re.sub(r'\s+task\s*$', '', title, flags=re.IGNORECASE)
                # Remove common words
                title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

        # Pattern 2: "mark task [title] as incomplete"
        if not task_id and not task_title:
            title_match = re.search(
                r'mark\s+task\s+(.+?)\s+as\s+(?:incomplete|pending|not\s+done|undone)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

        # Pattern: "unmark [title] task" or "set [title] to incomplete"
        if not task_id and not task_title:
            title_match = re.search(
                r'(?:unmark|set)\s+(.+?)(?:\s+task|\s+to\s+incomplete|$)',
                message_lower
            )
            if title_match:
                title = title_match.group(1).strip()
                if title and len(title) > 2 and not title.isdigit():
                    task_title = title

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
