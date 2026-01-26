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
        # Also match "update X to Y" pattern (without "task" word)
        re.compile(r'^update\s+\w+.*\s+to\s+', re.IGNORECASE),
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
        # Normalize message (helps parse bullets like "•" and inconsistent separators)
        message_lower = message.lower().strip().replace('•', ',')

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
        
        # STEP 1.5: Check if assistant was asking for task specification (follow-up)
        # Example: User says "mark the task complete", assistant asks "which task?", user says "buy apples"
        follow_up_intent = self._check_follow_up_response(message, message_lower, conversation_history)
        if follow_up_intent:
            return follow_up_intent

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


    def _check_follow_up_response(
        self,
        message: str,
        message_lower: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Intent]:
        """Check if user is providing task name as follow-up to assistant's clarification question.
        
        Example:
            User: "mark the task complete"
            Assistant: "Please specify which task..."
            User: "buy apples" <- This is a follow-up
        
        Returns:
            Intent object if follow-up detected, None otherwise
        """
        if not conversation_history:
            return None
        
        # Check last assistant message for clarification patterns
        for msg in reversed(conversation_history[-3:]):
            if msg.get('role') == 'assistant':
                assistant_msg = msg.get('content', '').lower()
                
                # Case A: assistant asked WHAT FIELDS to update (follow-up details)
                # Example:
                #   Assistant: "Task #12 mein kya update karna hai?"
                #   User: "title to buy fruits, priority low, deadline tomorrow"
                update_fields_patterns = [
                    'what do you want to update',
                    "what would you like to update",
                    'tell me what you want to change',
                    'you can update',
                    'you can reply like',
                    'kya update karna hai',
                    'kya update kerna hai',
                    'mein kya update',
                    'what changes',
                    'which changes',
                ]
                is_asking_update_fields = any(p in assistant_msg for p in update_fields_patterns)

                if is_asking_update_fields:
                    # If user message contains update details, convert it into an update intent using context task_id
                    # Normalize bullets here too (user may send "•" list)
                    normalized_lower = message_lower.replace('•', ',')
                    has_details = any(
                        kw in message_lower
                        for kw in [
                            'title', 'priority', 'deadline', 'due date', 'due_date',
                            'description', 'remove', 'no deadline', 'cancel deadline',
                            'complete', 'completed', 'incomplete', 'pending', 'undone',
                            'tomorrow', 'today', 'next'
                        ]
                    ) or ('title to' in normalized_lower) or ('priority to' in normalized_lower) or ('due date' in normalized_lower)

                    if has_details:
                        task_id = self._get_context_task_id(conversation_history)
                        # Fallback: extract "#12" if present
                        if not task_id:
                            m = re.search(r'#(\d+)', assistant_msg)
                            if m:
                                try:
                                    task_id = int(m.group(1))
                                except ValueError:
                                    task_id = None

                        if task_id:
                            pseudo_message = f"update task #{task_id} {message}"
                            pseudo_lower = pseudo_message.lower()
                            intent = self._detect_update_intent(pseudo_message, pseudo_lower, conversation_history)
                            if intent:
                                # Ensure we always confirm updates
                                intent.needs_confirmation = True
                                return intent

                # Patterns indicating assistant is asking for task specification
                asking_patterns = [
                    'which task', 'specify which task', 'specify the task',
                    'task you want', 'task you would like', 'task to', 
                    'provide the name', 'mention the task', 'task number',
                    'kaunsa task', 'konsa task', 'task batao'
                ]
                
                is_asking = any(pattern in assistant_msg for pattern in asking_patterns)
                
                if is_asking:
                    # Determine operation from assistant message
                    operation = None
                    if 'update' in assistant_msg or 'change' in assistant_msg:
                        operation = 'update_ask'
                    elif 'delete' in assistant_msg or 'remove' in assistant_msg:
                        operation = 'delete'
                    elif 'complete' in assistant_msg and 'incomplete' not in assistant_msg:
                        operation = 'complete'
                    elif 'incomplete' in assistant_msg or 'not done' in assistant_msg or 'pending' in assistant_msg:
                        operation = 'incomplete'
                    
                    if operation:
                        # Extract task title from current message
                        # Current message is likely just the task title
                        task_title = message.strip()
                        
                        # Remove common prefixes
                        task_title = re.sub(r'^(the|a|an|update|delete|remove|complete|mark)\s+', '', task_title, flags=re.IGNORECASE)
                        # Remove common suffixes
                        task_title = re.sub(r'\s+(task|ko\s+update|ko\s+delete|wala).*$', '', task_title, flags=re.IGNORECASE)
                        
                        if task_title and len(task_title) >= 2 and not task_title.isdigit():
                            logger.info(f"Detected follow-up: operation={operation}, task_title='{task_title}'")
                            
                            # For update_ask, return without params to get update details
                            if operation == 'update_ask':
                                return Intent(
                                    operation='update_ask',
                                    task_id=None,
                                    task_title=task_title,
                                    params=None,
                                    needs_confirmation=True
                                )
                            elif operation == 'incomplete':
                                return Intent(
                                    operation='incomplete',
                                    task_id=None,
                                    task_title=task_title,
                                    params={"completed": False},
                                    needs_confirmation=True
                                )
                            else:
                                # delete, complete - needs confirmation
                                return Intent(
                                    operation=operation,
                                    task_id=None,
                                    task_title=task_title,
                                    needs_confirmation=True
                                )
                break  # Only check most recent assistant message
        
        return None


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
                    
                    # Extract task title from confirmation message
                    task_title_match = re.search(r"task\s+['\"](.+?)['\"]", content)
                    task_title = task_title_match.group(1).strip() if task_title_match else None

                    # Determine operation type
                    operation = None
                    params = {}
                    
                    if 'delete' in content or 'remove' in content:
                        operation = 'delete'
                    el                    if 'update' in content or 'change' in content or 'edit' in content:
                        operation = 'update'
                        
                        # FIRST: Try to extract params from confirmation template (assistant message)
                        # Pattern: "📝 **Update Task Confirmation**" with formatted fields
                        if 'update task confirmation' in content.lower() or 'changes to be made' in content.lower():
                            # Extract task ID from confirmation template
                            task_id_match = re.search(r'task\s+id:\s*#(\d+)', content, re.IGNORECASE)
                            if task_id_match:
                                task_id = int(task_id_match.group(1))
                            
                            # Extract title from template: "• Title: → \"value\""
                            title_match = re.search(r'title:\s*→\s*["\'](.+?)["\']', content, re.IGNORECASE)
                            if title_match:
                                params['title'] = title_match.group(1).strip()
                            
                            # Extract priority: "• Priority: → value"
                            priority_match = re.search(r'priority:\s*→\s*(\w+)', content, re.IGNORECASE)
                            if priority_match:
                                priority_val = priority_match.group(1).strip().lower()
                                if priority_val in ['high', 'medium', 'low']:
                                    params['priority'] = priority_val
                            
                            # Extract description: "• Description: → \"value\""
                            desc_match = re.search(r'description:\s*→\s*["\'](.+?)["\']', content, re.IGNORECASE)
                            if desc_match:
                                params['description'] = desc_match.group(1).strip()
                            
                            # Extract due date: "• Due Date: → value" or "(removed)"
                            due_date_match = re.search(r'due\s+date:\s*→\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
                            if due_date_match:
                                due_val = due_date_match.group(1).strip()
                                if '(removed)' in due_val.lower():
                                    params['due_date'] = None
                                else:
                                    # Store the date string as-is, will be parsed later
                                    params['due_date'] = due_val
                        
                        # FALLBACK: Look back at previous user messages to extract update params
                        if not params:
                            for prev_msg in reversed(conversation_history[-6:]):
                                if prev_msg.get('role') == 'user':
                                    prev_content = prev_msg.get('content', '').lower()
                                    # Pattern: "update the task X to Y" or "update X task to Y"
                                    update_match = re.search(
                                        r'update\s+(?:the\s+)?(.+?)\s+task\s+to\s+(.+?)(?:$|,|\s+with|\s+and)',
                                        prev_content,
                                        re.IGNORECASE
                                    )
                                    if update_match:
                                        # Extract new title
                                        new_title = update_match.group(2).strip()
                                        params['title'] = new_title
                                        # Also extract task title if not already found
                                        if not task_title:
                                            task_title = update_match.group(1).strip()
                                            task_title = re.sub(r'^(the|a|an)\s+', '', task_title, flags=re.IGNORECASE)
                                        break
                                    # Pattern: "update task X title to Y"
                                    title_update_match = re.search(
                                        r'update\s+(?:the\s+)?task\s+(.+?)\s+title\s+to\s+(.+?)(?:$|,|\s+with|\s+and)',
                                        prev_content,
                                        re.IGNORECASE
                                    )
                                    if title_update_match:
                                        if not task_title:
                                            task_title = title_update_match.group(1).strip()
                                        params['title'] = title_update_match.group(2).strip()
                                        break
                                    # Generic follow-up patterns (user might reply only with fields)
                                    # title / priority / due date / remove due date / description / complete/incomplete
                                    if 'title' not in params:
                                        m = re.search(r'(?:title)\s*(?:to|:)\s*(.+?)(?:,|$)', prev_content, re.IGNORECASE)
                                        if m:
                                            params['title'] = m.group(1).strip()
                                    if 'priority' not in params:
                                        for level, keywords in self.PRIORITY_MAP.items():
                                            if any(k in prev_content for k in keywords) or re.search(rf'priority\s*(?:to|:)\s*{level}', prev_content):
                                                params['priority'] = level
                                                break
                                    if 'due_date' not in params:
                                        if re.search(r'remove\s+(?:the\s+)?(?:deadline|due\s+date|due_date)|no\s+(?:deadline|due\s+date)|cancel\s+(?:deadline|due\s+date)', prev_content):
                                            params['due_date'] = None
                                        elif any(k in prev_content for k in self.DATE_KEYWORDS) or 'due date' in prev_content or 'deadline' in prev_content:
                                            # very simple extraction after "due date" / "deadline"
                                            dm = re.search(r'(?:due\s+date|deadline)\s*(?:to|is|as|:)?\s*(.+?)(?:,|$)', prev_content)
                                            if dm:
                                                params['due_date'] = dm.group(1).strip()
                                            elif 'tomorrow' in prev_content:
                                                params['due_date'] = 'tomorrow'
                                            elif 'today' in prev_content:
                                                params['due_date'] = 'today'
                                    if 'description' not in params:
                                        dm = re.search(r'description\s*(?:to|:)\s*(.+?)(?:,|$)', prev_content, re.IGNORECASE)
                                        if dm:
                                            params['description'] = dm.group(1).strip()
                                    if 'completed' not in params:
                                        if re.search(r'\b(mark\s+)?(as\s+)?complete(d)?\b|\bdone\b', prev_content) and 'incomplete' not in prev_content:
                                            params['completed'] = True
                                        elif re.search(r'\b(incomplete|pending|undone|not\s+done)\b', prev_content):
                                            params['completed'] = False
                    elif 'incomplete' in content or 'not done' in content or 'pending' in content or 'undone' in content:
                        operation = 'incomplete'
                    elif 'complete' in content or 'mark' in content or 'done' in content:
                        operation = 'complete'

                    if operation:
                        return {
                            'operation': operation,
                            'task_id': task_id,
                            'task_title': task_title,
                            'params': params
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

        # Pattern 4: After update/delete/complete, extract title directly (including partial titles)
        # "update buy milk" or "delete grocery shopping" or "delete milk" (partial)
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
                
                # Handle "update [title]" or "delete [partial title]" pattern (without "task" word)
                # This captures partial titles like "delete milk" or "update grocery"
                # Match everything after the operation until end or next keyword
                match = re.search(
                    rf'{op}\s+(?:the\s+)?(.+?)(?=\s+(?:to\s+(?:update|set|change)|title\s+to|priority\s+to|deadline|description|update|delete|complete|mark|as\s+complete|as\s+incomplete|$))',
                    message_lower,
                    re.IGNORECASE | re.DOTALL
                )
                if match:
                    title = match.group(1).strip()
                    # Remove common stop words at start
                    title = re.sub(r'^(the|a|an)\s+', '', title, flags=re.IGNORECASE)
                    # Remove trailing keywords but keep partial title
                    title = re.sub(r'\s+(to|with|and|title|priority|deadline|description|update|delete|complete|mark|task)\s+.*$', '', title, flags=re.IGNORECASE)
                    # Remove "task" if it's at the end
                    title = re.sub(r'\s+task\s*$', '', title, flags=re.IGNORECASE)
                    # Accept even single words (partial titles) - minimum 2 chars
                    if title and len(title) >= 2 and not title.isdigit() and title.lower() not in ['the', 'a', 'an']:
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

        # Normalize bullets and separators
        message_lower = message_lower.replace('•', ',')

        # Extract task identifier (ID or title)
        task_id = self._extract_task_id(message)
        
        # Special pattern FIRST: "update the task X to Y" or "update X task to Y" or "update X to Y"
        # Example: "update the task buy milk to buy vegetables" or "update buy milk task to buy fruits" or "update buy apples to buy fruits"
        # This needs to extract BOTH old title (X) and new title (Y)
        new_title_from_pattern = None
        task_title = None
        
        if not task_id:
            # Pattern 1: "update the task X to Y, ..."
            # Match everything after "update the task" until "to", then everything after "to" until comma/keyword
            update_to_pattern = re.search(
                r'update\s+the\s+task\s+(.+?)\s+to\s+(.+?)(?:,|\s+(?:with|and|priority|deadline|description|low|medium|high)|\s*$)',
                message_lower,
                re.IGNORECASE
            )
            if update_to_pattern:
                task_title = update_to_pattern.group(1).strip()
                new_title_from_pattern = update_to_pattern.group(2).strip()
                # Clean up task title
                task_title = re.sub(r'^(the|a|an)\s+', '', task_title, flags=re.IGNORECASE)
                logger.info(f"Extracted from 'update the task X to Y': task_title='{task_title}', new_title='{new_title_from_pattern}'")
            
            # Pattern 2: "update X task to Y" (without "the")
            if not task_title:
                update_to_pattern = re.search(
                    r'update\s+(.+?)\s+task\s+to\s+(.+?)(?:,|\s+(?:with|and|priority|deadline|description|low|medium|high)|\s*$)',
                    message_lower,
                    re.IGNORECASE
                )
                if update_to_pattern:
                    task_title = update_to_pattern.group(1).strip()
                    new_title_from_pattern = update_to_pattern.group(2).strip()
                    # Clean up task title
                    task_title = re.sub(r'^(the|a|an)\s+', '', task_title, flags=re.IGNORECASE)
                    logger.info(f"Extracted from 'update X task to Y': task_title='{task_title}', new_title='{new_title_from_pattern}'")
            
            # Pattern 3: "update X to Y" (without "the task" or "task")
            # BUT: Must have "update" at the start and contain operation-looking title (not just "update it to X")
            # Match words/spaces but explicitly look for " to " as delimiter
            if not task_title and message_lower.startswith('update '):
                # First, check if there's a " to " in the message after "update "
                rest_of_message = message_lower[7:]  # Remove "update "
                if ' to ' in rest_of_message:
                    # Split by first occurrence of " to "
                    parts = rest_of_message.split(' to ', 1)
                    if len(parts) == 2:
                        potential_title = parts[0].strip()
                        rest = parts[1].strip()
                        
                        # Extract new title from rest (stop at comma or keywords)
                        new_title_match = re.search(
                            r'^(.+?)(?:,|\s+(?:with|and|priority|deadline|description|low|medium|high)|\s*$)',
                            rest,
                            re.IGNORECASE
                        )
                        if new_title_match:
                            potential_new_title = new_title_match.group(1).strip()
                            
                            # Only accept if old title is not just "it" or "this"
                            if potential_title not in ['it', 'this', 'that'] and len(potential_title) >= 2 and len(potential_new_title) >= 2:
                                task_title = potential_title
                                new_title_from_pattern = potential_new_title
                                # Clean up task title
                                task_title = re.sub(r'^(the|a|an)\s+', '', task_title, flags=re.IGNORECASE)
                                logger.info(f"Extracted from 'update X to Y': task_title='{task_title}', new_title='{new_title_from_pattern}'")
        
        # If not found by special pattern, try normal title extraction
        if not task_id and not task_title:
            task_title = self._extract_task_title(message, message_lower)

        # If neither found, check conversation context for recently mentioned task
        if not task_id and not task_title:
            task_id = self._get_context_task_id(conversation_history)
            # Also try to get task title from context
            if not task_id:
                task_title = self._get_context_task_title(conversation_history)

        # If still not found but user is providing update details (like "update the title: X"),
        # this might be a follow-up to a previous update request - check conversation context
        if not task_id and not task_title:
            # Check if previous message was asking for task name and current message provides it
            last_assistant_msg = None
            for msg in reversed(conversation_history[-3:]):
                if msg.get('role') == 'assistant':
                    last_assistant_msg = msg.get('content', '').lower()
                    break
            
            # If assistant asked "which task" or similar, current message is likely the title
            if last_assistant_msg and any(keyword in last_assistant_msg for keyword in [
                'which task', 'task name', 'task you want', 'task to update', 
                'provide the name', 'mention the task', 'task number', 'kaunsa task',
                'wala task', 'task update kerna'
            ]):
                # Current message might be providing task title
                # Pattern: "zoom class wala task update kerna hai" → extract "zoom class"
                title_match = re.search(r'(.+?)\s+(?:wala|walay|ka|ki|ko|task|update|kerna|hai)', message_lower)
                if title_match:
                    potential_title = title_match.group(1).strip()
                    potential_title = re.sub(r'^(the|a|an|update)\s+', '', potential_title, flags=re.IGNORECASE)
                    if potential_title and len(potential_title) >= 2 and not potential_title.isdigit():
                        task_title = potential_title
                        logger.info(f"Extracted task title from follow-up: '{task_title}'")
                else:
                    # Just the title itself
                    potential_title = message.strip()
                    potential_title = re.sub(r'^(the|a|an|update)\s+', '', potential_title, flags=re.IGNORECASE)
                    potential_title = re.sub(r'\s+(wala|walay|task|update|kerna|hai).*$', '', potential_title, flags=re.IGNORECASE)
                    if potential_title and len(potential_title) >= 2 and not potential_title.isdigit():
                        task_title = potential_title
                        logger.info(f"Extracted task title from simple follow-up: '{task_title}'")
            
            # Check recent conversation for task mentions in both user and assistant messages
            if not task_title:
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
                                except ValueError:
                                    pass
                        
                        # Pattern 3: Look for task mentions in assistant's confirmation messages
                        # "Task 'go to saturday class' mein kya update karna hai?"
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
        
        # If new_title_from_pattern was extracted, add it to params
        if new_title_from_pattern:
            params['title'] = new_title_from_pattern
            logger.info(f"Added new title to params: '{new_title_from_pattern}'")

        # Check if user is providing UPDATE DETAILS (not just asking what to update)
        # This is CRITICAL: Detect if user is giving all details at once
        has_update_details = any([
            new_title_from_pattern is not None,  # "update X to Y" pattern detected
            # NOTE: don't treat generic word "to" (e.g., "want to update") as update details
            'priority' in message_lower,
            'deadline' in message_lower or 'due date' in message_lower or 'due_date' in message_lower,
            'description' in message_lower,
            ('title' in message_lower and ('to' in message_lower or ':' in message_lower)),
            # Stronger patterns for title change without "title" keyword
            re.search(r'\\bchange\\b.*\\btitle\\b', message_lower) is not None,
            re.search(r'\\bset\\b.*\\bpriority\\b', message_lower) is not None,
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
                params=None,
                needs_confirmation=True  # Always ask what to update
            )

        # User is providing update details - extract them!

        # Extract new title (only if not already extracted by "update X to Y" pattern)
        if 'title' not in params:
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

        return Intent(
            operation="update",
            task_id=task_id,
            task_title=task_title,
            params=params if params else None,
            # Always confirm updates before executing
            needs_confirmation=True
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

        # If still not found, check if previous message was asking for task name
        # and current message is just providing the title (follow-up)
        if not task_id and not task_title and conversation_history:
            last_assistant_msg = None
            for msg in reversed(conversation_history[-3:]):
                if msg.get('role') == 'assistant':
                    last_assistant_msg = msg.get('content', '').lower()
                    break
            
            # If assistant asked "which task" or "task name", current message is likely the title
            if last_assistant_msg and any(keyword in last_assistant_msg for keyword in [
                'which task', 'task name', 'task you want', 'task to delete', 
                'provide the name', 'mention the task', 'task number'
            ]):
                # Current message is likely just the task title
                # Extract any meaningful text (not just "the", "a", etc.)
                potential_title = message.strip()
                # Remove common words
                potential_title = re.sub(r'^(the|a|an|delete|remove)\s+', '', potential_title, flags=re.IGNORECASE)
                potential_title = re.sub(r'\s+(task|delete|remove).*$', '', potential_title, flags=re.IGNORECASE)
                if potential_title and len(potential_title) >= 2 and not potential_title.isdigit():
                    task_title = potential_title
                    logger.info(f"Extracted task title from follow-up message: '{task_title}'")

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
