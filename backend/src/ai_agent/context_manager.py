"""
Conversation Context Manager for multi-turn workflows.

Manages conversation state for:
- ADD_TASK workflow: confirm → priority → deadline → description → create
- UPDATE_TASK workflow: identify → confirm → update
- DELETE_TASK workflow: identify → confirm → delete
- COMPLETE_TASK workflow: identify → confirm → complete

State management:
- current_intent: Tracks workflow state (NEUTRAL, ADDING_TASK, etc.)
- state_data: Collects information during workflow
- target_task_id: References task being operated on
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from ..services.conversation_service import ConversationService
from ..services.intent_classifier import IntentClassifier, Intent
from ..utils.date_parser import DateParser, DateParseResult

logger = logging.getLogger(__name__)


class ContextManager:
    """Manage conversation context and workflow state."""

    # Workflow steps for ADD_TASK
    ADD_TASK_STEPS = ["confirm", "priority", "deadline", "description", "create"]

    # Workflow steps for UPDATE_TASK
    UPDATE_TASK_STEPS = ["identify", "show_details", "collect_changes", "confirm", "execute"]

    # Workflow steps for DELETE_TASK
    DELETE_TASK_STEPS = ["identify", "show_details", "confirm", "execute"]

    # Workflow steps for COMPLETE_TASK
    COMPLETE_TASK_STEPS = ["identify", "confirm", "execute"]

    def __init__(self, conversation_service: ConversationService):
        """
        Initialize context manager.

        Args:
            conversation_service: Service for conversation state persistence
        """
        self.conversation_service = conversation_service
        self.intent_classifier = IntentClassifier()

    def initialize_add_task_state(
        self,
        conversation_id: int,
        user_id: str,
        initial_title: str,
        initial_priority: Optional[str] = None,
        initial_due_date: Optional[str] = None,
        initial_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize state for ADD_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            initial_title: Extracted task title from user message
            initial_priority: Optional priority if provided upfront
            initial_due_date: Optional due date if provided upfront
            initial_description: Optional description if provided upfront

        Returns:
            Initialized state_data dictionary

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> state = manager.initialize_add_task_state(
            ...     conversation_id=123,
            ...     user_id="user-123",
            ...     initial_title="buy milk"
            ... )
            >>> assert state["title"] == "buy milk"
            >>> assert state["step"] == "confirm"
        """
        logger.info(
            f"Initializing ADD_TASK state for conversation {conversation_id}, "
            f"title='{initial_title}'"
        )

        # Determine starting step based on provided information
        if all([initial_priority, initial_due_date, initial_description]):
            step = "create"  # All info provided, ready to create
        elif initial_priority and initial_due_date:
            step = "description"  # Have priority and deadline, ask for description
        elif initial_priority:
            step = "deadline"  # Have priority, ask for deadline
        else:
            step = "confirm"  # Need confirmation and priority

        state_data = {
            "title": initial_title,
            "step": step
        }

        # Add optional fields if provided
        if initial_priority:
            state_data["priority"] = initial_priority
        if initial_due_date:
            state_data["due_date"] = initial_due_date
        if initial_description:
            state_data["description"] = initial_description

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            current_intent="ADDING_TASK",
            state_data=state_data
        )

        logger.info(f"ADD_TASK state initialized at step '{step}'")
        return state_data

    def collect_add_task_information(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        current_state: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Collect information during ADD_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            user_message: User's message
            current_state: Current state_data from conversation

        Returns:
            Tuple of (updated_state_data, next_step)

        Workflow progression:
            confirm → priority → deadline → description → create
        """
        logger.info(
            f"Collecting ADD_TASK info: step='{current_state.get('step')}', "
            f"message='{user_message}'"
        )

        current_step = current_state.get("step", "confirm")
        updated_state = current_state.copy()

        # Classify user's response as PROVIDE_INFORMATION
        intent_result = self.intent_classifier.classify(
            message=user_message,
            current_intent="ADDING_TASK"
        )

        # Handle cancellation
        if intent_result.intent_type == Intent.CANCEL_OPERATION:
            logger.info("User cancelled ADD_TASK workflow")
            return updated_state, "cancel"

        # Handle intent switching (user wants to do something else)
        if intent_result.intent_type not in [Intent.PROVIDE_INFORMATION, Intent.ADD_TASK]:
            logger.info(f"User switched intent to {intent_result.intent_type}")
            return updated_state, "switch_intent"

        # Extract entities from user message
        entities = intent_result.extracted_entities

        # Process based on current step
        if current_step == "confirm":
            # Waiting for confirmation and priority
            if entities.get("confirmation") or "priority" in entities:
                # User confirmed, extract priority if provided
                if "priority" in entities:
                    updated_state["priority"] = entities["priority"]
                    updated_state["step"] = "deadline"
                    next_step = "deadline"
                else:
                    # Need to ask for priority still
                    updated_state["step"] = "priority"
                    next_step = "priority"
            else:
                # Still waiting for confirmation
                next_step = "confirm"

        elif current_step == "priority":
            # Waiting for priority
            if "priority" in entities:
                updated_state["priority"] = entities["priority"]
                updated_state["step"] = "deadline"
                next_step = "deadline"
            else:
                # Try to extract from message text
                priority = self.extract_priority_from_text(user_message)
                if priority:
                    updated_state["priority"] = priority
                    updated_state["step"] = "deadline"
                    next_step = "deadline"
                else:
                    # Still need priority
                    next_step = "priority"

        elif current_step == "deadline":
            # Waiting for deadline
            confirmation = entities.get("confirmation")
            message_lower = user_message.lower().strip()

            # Check for explicit "no deadline" responses
            no_deadline_phrases = [
                "no deadline", "no due date", "skip", "none", "nope",
                "don't need one", "no thanks", "skip deadline"
            ]
            if confirmation == False or any(phrase in message_lower for phrase in no_deadline_phrases):
                # User doesn't want a deadline
                updated_state["due_date_raw"] = None
                updated_state["step"] = "description"
                next_step = "description"
            else:
                # User provided a date - validate it with DateParser
                parsed_date, error_msg, needs_clarification = self.validate_and_parse_date(user_message)

                if parsed_date:
                    # Successfully parsed - store both raw and parsed
                    updated_state["due_date_raw"] = user_message
                    updated_state["due_date_parsed"] = parsed_date.isoformat()
                    updated_state["step"] = "description"
                    next_step = "description"
                    logger.info(f"Date validated: '{user_message}' -> {parsed_date}")
                elif needs_clarification:
                    # Date couldn't be parsed - stay on deadline step for clarification
                    updated_state["date_error"] = error_msg
                    next_step = "deadline"  # Stay on deadline step
                    logger.warning(f"Date clarification needed for: '{user_message}'")
                else:
                    # Parsing failed but no clarification needed - proceed without date
                    updated_state["due_date_raw"] = user_message
                    updated_state["step"] = "description"
                    next_step = "description"

        elif current_step == "description":
            # Waiting for description
            confirmation = entities.get("confirmation")
            if confirmation == False:
                # User said no to description
                updated_state["step"] = "create"
                next_step = "create"
            else:
                # User provided description
                updated_state["description"] = user_message
                updated_state["step"] = "create"
                next_step = "create"

        else:
            # Unknown step
            logger.warning(f"Unknown step: {current_step}")
            next_step = current_step

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            state_data=updated_state
        )

        logger.info(f"ADD_TASK state updated: next_step='{next_step}'")
        return updated_state, next_step

    def extract_priority_from_text(self, text: str) -> Optional[str]:
        """
        Extract priority from natural language text.

        Args:
            text: User's message text

        Returns:
            Priority level ("high", "medium", "low") or None

        Examples:
            >>> manager = ContextManager(conversation_service)
            >>> manager.extract_priority_from_text("make it urgent")
            'high'
            >>> manager.extract_priority_from_text("low priority")
            'low'
        """
        text_lower = text.lower()

        # High priority keywords
        high_keywords = [
            "high", "urgent", "critical", "important", "asap",
            "high priority", "very important"
        ]
        if any(keyword in text_lower for keyword in high_keywords):
            return "high"

        # Low priority keywords
        low_keywords = [
            "low", "minor", "trivial", "someday", "later",
            "low priority", "not urgent"
        ]
        if any(keyword in text_lower for keyword in low_keywords):
            return "low"

        # Medium priority keywords
        medium_keywords = [
            "medium", "normal", "regular", "medium priority"
        ]
        if any(keyword in text_lower for keyword in medium_keywords):
            return "medium"

        return None

    def validate_priority(self, priority: str) -> Tuple[bool, Optional[str]]:
        """
        Validate priority value.

        Args:
            priority: Priority level to validate

        Returns:
            Tuple of (is_valid, error_message)

        Examples:
            >>> manager = ContextManager(conversation_service)
            >>> is_valid, error = manager.validate_priority("high")
            >>> assert is_valid is True
            >>> is_valid, error = manager.validate_priority("extreme")
            >>> assert is_valid is False
        """
        valid_priorities = ["high", "medium", "low"]

        if priority not in valid_priorities:
            return False, f"Invalid priority '{priority}'. Must be 'high', 'medium', or 'low'."

        return True, None

    def validate_and_parse_date(
        self,
        date_string: str
    ) -> Tuple[Optional[datetime], Optional[str], bool]:
        """
        Validate and parse a natural language date string.

        Uses DateParser to validate dates with proper error messages for:
        - Past dates (needs clarification)
        - Far future dates (>10 years, rejected)
        - Invalid formats (rejected)

        Args:
            date_string: Natural language date string (e.g., "tomorrow", "Jan 20")

        Returns:
            Tuple of (parsed_datetime, error_message, needs_clarification)
            - parsed_datetime: Parsed datetime if successful, None otherwise
            - error_message: Human-readable error message if failed
            - needs_clarification: True if user should clarify (e.g., past date)

        Examples:
            >>> manager = ContextManager(conversation_service)
            >>> dt, err, needs_clarify = manager.validate_and_parse_date("tomorrow")
            >>> assert dt is not None
            >>> assert err is None
            >>> dt, err, needs_clarify = manager.validate_and_parse_date("yesterday")
            >>> assert dt is None
            >>> assert "past" in err.lower()
            >>> assert needs_clarify is True
        """
        parser = DateParser()
        result = parser.parse(date_string)

        if result.success:
            logger.info(f"Successfully parsed date '{date_string}' to {result.parsed_date}")
            return result.parsed_date, None, False

        # Handle specific error cases
        error_msg = result.error_message or "Could not parse the date"

        # Check if it's a past date (needs clarification)
        if "past" in error_msg.lower():
            clarification_msg = (
                f"That date appears to be in the past. "
                "Could you provide a future date? "
                "(e.g., 'tomorrow', 'next week', 'January 20')"
            )
            return None, clarification_msg, True

        # Far future date
        if "future" in error_msg.lower():
            clarification_msg = (
                "That date is too far in the future (more than 10 years). "
                "Please provide a more reasonable deadline."
            )
            return None, clarification_msg, True

        # Generic parse failure
        clarification_msg = (
            f"I couldn't understand '{date_string}' as a date. "
            "Try something like 'tomorrow', 'next Friday', 'January 20', or 'in 3 days'."
        )
        return None, clarification_msg, True

    def format_date_clarification_prompt(
        self,
        original_input: str,
        error_reason: str
    ) -> str:
        """
        Format a user-friendly clarification prompt for date issues.

        Args:
            original_input: The user's original date input
            error_reason: Brief reason why the date failed

        Returns:
            User-friendly clarification prompt

        Examples:
            >>> manager = ContextManager(conversation_service)
            >>> prompt = manager.format_date_clarification_prompt("yesterday", "past date")
            >>> assert "past" in prompt or "future" in prompt
        """
        if "past" in error_reason.lower():
            return (
                f"'{original_input}' appears to be in the past. "
                "When would you like this task to be due? "
                "(e.g., 'tomorrow at 5pm', 'next week', 'no deadline')"
            )
        elif "future" in error_reason.lower() and "10 year" in error_reason.lower():
            return (
                f"'{original_input}' is more than 10 years away. "
                "Please provide a closer deadline, or say 'no deadline'."
            )
        else:
            return (
                f"I couldn't understand '{original_input}' as a date. "
                "You can say things like:\n"
                "• 'tomorrow at 3pm'\n"
                "• 'next Friday'\n"
                "• 'January 20'\n"
                "• 'in 3 days'\n"
                "• 'no deadline' (to skip)"
            )

    def reset_state_after_completion(
        self,
        conversation_id: int,
        user_id: str
    ) -> None:
        """
        Reset conversation state to NEUTRAL after task creation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> manager.reset_state_after_completion(123, "user-123")
        """
        logger.info(f"Resetting state for conversation {conversation_id}")

        self.conversation_service.reset_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id
        )

        logger.info("State reset to NEUTRAL")

    def get_current_state(
        self,
        conversation_id: int,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current conversation state.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user

        Returns:
            Dictionary with current_intent, state_data, target_task_id

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> state = manager.get_current_state(123, "user-123")
            >>> if state and state['current_intent'] == 'ADDING_TASK':
            ...     print("User is adding a task")
        """
        return self.conversation_service.get_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # UPDATE_TASK WORKFLOW METHODS (T052-T054)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def initialize_update_task_state(
        self,
        conversation_id: int,
        user_id: str,
        target_task_id: Optional[int] = None,
        task_name: Optional[str] = None,
        initial_changes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize state for UPDATE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            target_task_id: ID of the task to update (if known)
            task_name: Name/title of task for fuzzy matching (if ID not known)
            initial_changes: Changes extracted from initial message

        Returns:
            Initialized state_data dictionary

        Workflow:
            identify → show_details → collect_changes → confirm → execute

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> state = manager.initialize_update_task_state(
            ...     conversation_id=123,
            ...     user_id="user-123",
            ...     target_task_id=5,
            ...     initial_changes={"priority": "high"}
            ... )
            >>> assert state["step"] == "show_details"
        """
        logger.info(
            f"Initializing UPDATE_TASK state for conversation {conversation_id}, "
            f"task_id={target_task_id}, task_name={task_name}"
        )

        # Determine starting step based on what we know
        if target_task_id:
            # We know which task - show details
            step = "show_details"
        elif task_name:
            # Need to find task by name first
            step = "identify"
        else:
            # Need user to specify which task
            step = "identify"

        state_data = {
            "step": step,
            "changes": initial_changes or {}
        }

        # Add task reference if provided
        if target_task_id:
            state_data["target_task_id"] = target_task_id
        if task_name:
            state_data["task_name"] = task_name

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            current_intent="UPDATING_TASK",
            state_data=state_data,
            target_task_id=target_task_id
        )

        logger.info(f"UPDATE_TASK state initialized at step '{step}'")
        return state_data

    def collect_update_task_information(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        current_state: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Collect information during UPDATE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            user_message: User's message
            current_state: Current state_data from conversation

        Returns:
            Tuple of (updated_state_data, next_step)

        Workflow progression:
            identify → show_details → collect_changes → confirm → execute
        """
        logger.info(
            f"Collecting UPDATE_TASK info: step='{current_state.get('step')}', "
            f"message='{user_message}'"
        )

        current_step = current_state.get("step", "identify")
        updated_state = current_state.copy()

        # Classify user's response
        intent_result = self.intent_classifier.classify(
            message=user_message,
            current_intent="UPDATING_TASK"
        )

        # Handle cancellation
        if intent_result.intent_type == Intent.CANCEL_OPERATION:
            logger.info("User cancelled UPDATE_TASK workflow")
            return updated_state, "cancel"

        # Handle intent switching (user wants to do something else)
        if intent_result.intent_type not in [Intent.PROVIDE_INFORMATION, Intent.UPDATE_TASK]:
            logger.info(f"User switched intent to {intent_result.intent_type}")
            return updated_state, "switch_intent"

        # Extract entities from user message
        entities = intent_result.extracted_entities

        # Process based on current step
        if current_step == "identify":
            # Need to identify which task to update
            if "task_id" in entities:
                updated_state["target_task_id"] = entities["task_id"]
                updated_state["step"] = "show_details"
                next_step = "show_details"
            elif "task_name" in entities:
                updated_state["task_name"] = entities["task_name"]
                updated_state["step"] = "show_details"
                next_step = "show_details"
            else:
                # Try to extract task reference from message
                task_ref = self.extract_task_reference(user_message)
                if task_ref:
                    if isinstance(task_ref, int):
                        updated_state["target_task_id"] = task_ref
                    else:
                        updated_state["task_name"] = task_ref
                    updated_state["step"] = "show_details"
                    next_step = "show_details"
                else:
                    # Still need task identification
                    next_step = "identify"

        elif current_step == "show_details":
            # After showing details, ask what to change
            # Extract any changes mentioned
            changes = self.extract_field_changes(user_message, entities)
            if changes:
                updated_state["changes"] = {**updated_state.get("changes", {}), **changes}
                updated_state["step"] = "confirm"
                next_step = "confirm"
            else:
                # Need to collect what to change
                updated_state["step"] = "collect_changes"
                next_step = "collect_changes"

        elif current_step == "collect_changes":
            # Collect field changes from user
            changes = self.extract_field_changes(user_message, entities)
            if changes:
                updated_state["changes"] = {**updated_state.get("changes", {}), **changes}
                updated_state["step"] = "confirm"
                next_step = "confirm"
            else:
                # Still need changes
                next_step = "collect_changes"

        elif current_step == "confirm":
            # Waiting for confirmation
            confirmation = entities.get("confirmation")
            if confirmation == True:
                updated_state["step"] = "execute"
                next_step = "execute"
            elif confirmation == False:
                # User cancelled
                next_step = "cancel"
            else:
                # Still waiting for yes/no
                next_step = "confirm"

        else:
            # Unknown step
            logger.warning(f"Unknown UPDATE_TASK step: {current_step}")
            next_step = current_step

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            state_data=updated_state
        )

        logger.info(f"UPDATE_TASK state updated: next_step='{next_step}'")
        return updated_state, next_step

    def extract_task_reference(self, message: str) -> Optional[Any]:
        """
        Extract task reference (ID or name) from message.

        Args:
            message: User's message text

        Returns:
            Task ID (int), task name (str), or None

        Examples:
            >>> manager.extract_task_reference("task 5")
            5
            >>> manager.extract_task_reference("the milk task")
            "milk"
        """
        import re

        message_lower = message.lower().strip()

        # Try to extract task ID
        task_id_match = re.search(r'\btask\s*#?(\d+)\b', message_lower)
        if task_id_match:
            return int(task_id_match.group(1))

        # Try standalone number after "task"
        standalone_match = re.search(r'^(\d+)$', message_lower)
        if standalone_match:
            return int(standalone_match.group(1))

        # Try to extract task name from "the [name] task" pattern
        name_match = re.search(r'\bthe\s+(\w+)\s+task\b', message_lower)
        if name_match:
            return name_match.group(1)

        # Try to extract from "[name] task" pattern
        name_match2 = re.search(r'\b(\w+)\s+task\b', message_lower)
        if name_match2 and name_match2.group(1) not in ['my', 'the', 'a', 'this', 'that']:
            return name_match2.group(1)

        return None

    def extract_field_changes(
        self,
        message: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract field changes from user message.

        Args:
            message: User's message text
            entities: Entities extracted by intent classifier

        Returns:
            Dictionary of field changes {field_name: new_value}

        Examples:
            >>> changes = manager.extract_field_changes(
            ...     "make it high priority",
            ...     {"priority": "high"}
            ... )
            >>> assert changes == {"priority": "high"}
        """
        import re

        changes = {}
        message_lower = message.lower()

        # Extract priority from entities or text
        if "priority" in entities:
            changes["priority"] = entities["priority"]
        else:
            priority = self.extract_priority_from_text(message)
            if priority:
                changes["priority"] = priority

        # Extract title change
        title_match = re.search(
            r'(?:title|name)\s+(?:to|as|=)\s*["\']?(.+?)["\']?(?:\s*,|$)',
            message_lower
        )
        if title_match:
            changes["title"] = title_match.group(1).strip()

        # Extract description change
        desc_match = re.search(
            r'description\s+(?:to|as|=)\s*["\']?(.+?)["\']?(?:\s*,|$)',
            message_lower
        )
        if desc_match:
            changes["description"] = desc_match.group(1).strip()

        # Extract due date change
        # Look for patterns like "due [date]", "deadline [date]", "by [date]"
        due_patterns = [
            r'(?:due|deadline|by)\s+(.+?)(?:\s*,|$)',
            r'due_date\s+(?:to|as|=)\s*(.+?)(?:\s*,|$)'
        ]
        for pattern in due_patterns:
            due_match = re.search(pattern, message_lower)
            if due_match:
                raw_date = due_match.group(1).strip()
                # Validate the extracted date
                parsed_date, error_msg, needs_clarification = self.validate_and_parse_date(raw_date)
                if parsed_date:
                    changes["due_date_raw"] = raw_date
                    changes["due_date_parsed"] = parsed_date.isoformat()
                else:
                    # Store raw for error handling
                    changes["due_date_raw"] = raw_date
                    changes["due_date_error"] = error_msg
                break

        # Extract completed status
        if re.search(r'\b(complete|done|finished)\b', message_lower):
            changes["completed"] = True
        elif re.search(r'\b(incomplete|not\s+done|pending)\b', message_lower):
            changes["completed"] = False

        return changes

    def format_update_confirmation(
        self,
        task_details: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> str:
        """
        Format confirmation message showing what will be changed.

        Args:
            task_details: Current task details
            changes: Proposed changes

        Returns:
            Formatted confirmation message

        Example:
            >>> msg = manager.format_update_confirmation(
            ...     {"title": "Buy milk", "priority": "medium"},
            ...     {"priority": "high"}
            ... )
            >>> assert "medium → high" in msg
        """
        lines = [
            f"📝 Update task #{task_details.get('id', '?')}: '{task_details.get('title', '?')}'?",
            ""
        ]

        # Show each change
        for field, new_value in changes.items():
            if field in ["due_date_raw"]:
                continue  # Skip raw fields

            old_value = task_details.get(field, "not set")
            if old_value is None:
                old_value = "not set"

            # Format field name for display
            display_field = field.replace("_", " ").title()

            lines.append(f"• {display_field}: {old_value} → {new_value}")

        lines.append("")
        lines.append("Reply 'yes' to confirm or 'no' to cancel.")

        return "\n".join(lines)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DELETE_TASK WORKFLOW METHODS (T062)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def initialize_delete_task_state(
        self,
        conversation_id: int,
        user_id: str,
        target_task_id: Optional[int] = None,
        task_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize state for DELETE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            target_task_id: ID of the task to delete (if known)
            task_name: Name/title of task for fuzzy matching (if ID not known)

        Returns:
            Initialized state_data dictionary

        Workflow:
            identify → show_details → confirm → execute

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> state = manager.initialize_delete_task_state(
            ...     conversation_id=123,
            ...     user_id="user-123",
            ...     target_task_id=5
            ... )
            >>> assert state["step"] == "show_details"
        """
        logger.info(
            f"Initializing DELETE_TASK state for conversation {conversation_id}, "
            f"task_id={target_task_id}, task_name={task_name}"
        )

        # Determine starting step based on what we know
        if target_task_id:
            # We know which task - show details for confirmation
            step = "show_details"
        elif task_name:
            # Need to find task by name first
            step = "identify"
        else:
            # Need user to specify which task
            step = "identify"

        state_data = {
            "step": step
        }

        # Add task reference if provided
        if target_task_id:
            state_data["target_task_id"] = target_task_id
        if task_name:
            state_data["task_name"] = task_name

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            current_intent="DELETING_TASK",
            state_data=state_data,
            target_task_id=target_task_id
        )

        logger.info(f"DELETE_TASK state initialized at step '{step}'")
        return state_data

    def collect_delete_task_information(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        current_state: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Collect information during DELETE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            user_message: User's message
            current_state: Current state_data from conversation

        Returns:
            Tuple of (updated_state_data, next_step)

        Workflow progression:
            identify → show_details → confirm → execute
        """
        logger.info(
            f"Collecting DELETE_TASK info: step='{current_state.get('step')}', "
            f"message='{user_message}'"
        )

        current_step = current_state.get("step", "identify")
        updated_state = current_state.copy()

        # Classify user's response
        intent_result = self.intent_classifier.classify(
            message=user_message,
            current_intent="DELETING_TASK"
        )

        # Handle cancellation
        if intent_result.intent_type == Intent.CANCEL_OPERATION:
            logger.info("User cancelled DELETE_TASK workflow")
            return updated_state, "cancel"

        # Handle intent switching (user wants to do something else)
        if intent_result.intent_type not in [Intent.PROVIDE_INFORMATION, Intent.DELETE_TASK]:
            logger.info(f"User switched intent to {intent_result.intent_type}")
            return updated_state, "switch_intent"

        # Extract entities from user message
        entities = intent_result.extracted_entities

        # Process based on current step
        if current_step == "identify":
            # Need to identify which task to delete
            if "task_id" in entities:
                updated_state["target_task_id"] = entities["task_id"]
                updated_state["step"] = "show_details"
                next_step = "show_details"
            elif "task_name" in entities:
                updated_state["task_name"] = entities["task_name"]
                updated_state["step"] = "show_details"
                next_step = "show_details"
            else:
                # Try to extract task reference from message
                task_ref = self.extract_task_reference(user_message)
                if task_ref:
                    if isinstance(task_ref, int):
                        updated_state["target_task_id"] = task_ref
                    else:
                        updated_state["task_name"] = task_ref
                    updated_state["step"] = "show_details"
                    next_step = "show_details"
                else:
                    # Still need task identification
                    next_step = "identify"

        elif current_step == "show_details":
            # After showing details, wait for confirmation
            confirmation = entities.get("confirmation")
            if confirmation == True:
                updated_state["step"] = "execute"
                next_step = "execute"
            elif confirmation == False:
                # User cancelled
                next_step = "cancel"
            else:
                # Still waiting for confirmation - may be in confirmation step now
                updated_state["step"] = "confirm"
                next_step = "confirm"

        elif current_step == "confirm":
            # Waiting for confirmation
            confirmation = entities.get("confirmation")
            if confirmation == True:
                updated_state["step"] = "execute"
                next_step = "execute"
            elif confirmation == False:
                # User cancelled
                next_step = "cancel"
            else:
                # Still waiting for yes/no
                next_step = "confirm"

        else:
            # Unknown step
            logger.warning(f"Unknown DELETE_TASK step: {current_step}")
            next_step = current_step

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            state_data=updated_state
        )

        logger.info(f"DELETE_TASK state updated: next_step='{next_step}'")
        return updated_state, next_step

    def format_delete_confirmation(
        self,
        task_details: Dict[str, Any],
        confidence_score: Optional[int] = None
    ) -> str:
        """
        Format confirmation message for task deletion.

        Args:
            task_details: Task details to display
            confidence_score: Fuzzy match confidence (0-100) if matched by name

        Returns:
            Formatted confirmation message

        Example:
            >>> msg = manager.format_delete_confirmation(
            ...     {"id": 5, "title": "Buy milk", "priority": "medium"},
            ...     confidence_score=85
            ... )
            >>> assert "Delete task #5" in msg
        """
        task_id = task_details.get('id', '?')
        title = task_details.get('title', 'Unknown')
        priority = task_details.get('priority', 'medium')
        completed = task_details.get('completed', False)

        # Status emoji
        status_emoji = "✅" if completed else "⏳"
        status_text = "Complete" if completed else "Pending"

        # Priority emoji
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")

        lines = [
            f"🗑️ Delete task #{task_id}: '{title}'?"
        ]

        # Show confidence score if from fuzzy match
        if confidence_score is not None and confidence_score < 100:
            lines.append(f"   ({confidence_score}% match)")

        lines.append("")
        lines.append(f"• Priority: {priority_emoji} {priority}")
        lines.append(f"• Status: {status_emoji} {status_text}")

        # Add due date if present
        due_date = task_details.get('due_date')
        if due_date:
            if isinstance(due_date, str):
                lines.append(f"• Due: {due_date}")
            else:
                lines.append(f"• Due: {due_date.strftime('%B %d, %Y')}")

        # Add description if present
        description = task_details.get('description')
        if description:
            # Truncate long descriptions
            desc_display = description[:50] + "..." if len(description) > 50 else description
            lines.append(f"• Description: {desc_display}")

        lines.append("")
        lines.append("⚠️ This action cannot be undone.")
        lines.append("Reply 'yes' to confirm or 'no' to cancel.")

        return "\n".join(lines)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMPLETE_TASK WORKFLOW METHODS (T078-T079)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def initialize_complete_task_state(
        self,
        conversation_id: int,
        user_id: str,
        target_task_id: Optional[int] = None,
        task_name: Optional[str] = None,
        toggle_to: bool = True  # True = complete, False = incomplete
    ) -> Dict[str, Any]:
        """
        Initialize state for COMPLETE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            target_task_id: ID of the task to complete (if known)
            task_name: Name/title of task for fuzzy matching (if ID not known)
            toggle_to: Target completion state (True=complete, False=incomplete)

        Returns:
            Initialized state_data dictionary

        Workflow:
            identify → confirm → execute

        Example:
            >>> manager = ContextManager(conversation_service)
            >>> state = manager.initialize_complete_task_state(
            ...     conversation_id=123,
            ...     user_id="user-123",
            ...     target_task_id=5
            ... )
            >>> assert state["step"] == "confirm"
        """
        logger.info(
            f"Initializing COMPLETE_TASK state for conversation {conversation_id}, "
            f"task_id={target_task_id}, task_name={task_name}, toggle_to={toggle_to}"
        )

        # Determine starting step based on what we know
        if target_task_id:
            # We know which task - go to confirmation
            step = "confirm"
        elif task_name:
            # Need to find task by name first
            step = "identify"
        else:
            # Need user to specify which task
            step = "identify"

        state_data = {
            "step": step,
            "toggle_to": toggle_to  # True = mark complete, False = mark incomplete
        }

        # Add task reference if provided
        if target_task_id:
            state_data["target_task_id"] = target_task_id
        if task_name:
            state_data["task_name"] = task_name

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            current_intent="COMPLETING_TASK",
            state_data=state_data,
            target_task_id=target_task_id
        )

        logger.info(f"COMPLETE_TASK state initialized at step '{step}'")
        return state_data

    def collect_complete_task_information(
        self,
        conversation_id: int,
        user_id: str,
        user_message: str,
        current_state: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Collect information during COMPLETE_TASK workflow.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            user_message: User's message
            current_state: Current state_data from conversation

        Returns:
            Tuple of (updated_state_data, next_step)

        Workflow progression:
            identify → confirm → execute
        """
        logger.info(
            f"Collecting COMPLETE_TASK info: step='{current_state.get('step')}', "
            f"message='{user_message}'"
        )

        current_step = current_state.get("step", "identify")
        updated_state = current_state.copy()

        # Classify user's response
        intent_result = self.intent_classifier.classify(
            message=user_message,
            current_intent="COMPLETING_TASK"
        )

        # Handle cancellation
        if intent_result.intent_type == Intent.CANCEL_OPERATION:
            logger.info("User cancelled COMPLETE_TASK workflow")
            return updated_state, "cancel"

        # Handle intent switching (user wants to do something else)
        if intent_result.intent_type not in [Intent.PROVIDE_INFORMATION, Intent.COMPLETE_TASK]:
            logger.info(f"User switched intent to {intent_result.intent_type}")
            return updated_state, "switch_intent"

        # Extract entities from user message
        entities = intent_result.extracted_entities

        # Process based on current step
        if current_step == "identify":
            # Need to identify which task to complete
            if "task_id" in entities:
                updated_state["target_task_id"] = entities["task_id"]
                updated_state["step"] = "confirm"
                next_step = "confirm"
            elif "task_name" in entities:
                updated_state["task_name"] = entities["task_name"]
                updated_state["step"] = "confirm"
                next_step = "confirm"
            else:
                # Try to extract task reference from message
                task_ref = self.extract_task_reference(user_message)
                if task_ref:
                    if isinstance(task_ref, int):
                        updated_state["target_task_id"] = task_ref
                    else:
                        updated_state["task_name"] = task_ref
                    updated_state["step"] = "confirm"
                    next_step = "confirm"
                else:
                    # Still need task identification
                    next_step = "identify"

        elif current_step == "confirm":
            # Waiting for confirmation
            confirmation = entities.get("confirmation")
            if confirmation == True:
                updated_state["step"] = "execute"
                next_step = "execute"
            elif confirmation == False:
                # User cancelled
                next_step = "cancel"
            else:
                # Still waiting for yes/no
                next_step = "confirm"

        else:
            # Unknown step
            logger.warning(f"Unknown COMPLETE_TASK step: {current_step}")
            next_step = current_step

        # Update conversation state
        self.conversation_service.update_conversation_state(
            conversation_id=conversation_id,
            user_id=user_id,
            state_data=updated_state
        )

        logger.info(f"COMPLETE_TASK state updated: next_step='{next_step}'")
        return updated_state, next_step

    def format_complete_confirmation(
        self,
        task_details: Dict[str, Any],
        toggle_to: bool = True,
        confidence_score: Optional[int] = None
    ) -> str:
        """
        Format confirmation message for task completion.

        Args:
            task_details: Task details to display
            toggle_to: Target completion state (True=complete, False=incomplete)
            confidence_score: Fuzzy match confidence (0-100) if matched by name

        Returns:
            Formatted confirmation message

        Example:
            >>> msg = manager.format_complete_confirmation(
            ...     {"id": 5, "title": "Buy milk", "completed": False},
            ...     toggle_to=True
            ... )
            >>> assert "Mark task #5" in msg
        """
        task_id = task_details.get('id', '?')
        title = task_details.get('title', 'Unknown')
        current_status = task_details.get('completed', False)

        # Determine action text
        if toggle_to:
            action = "complete"
            emoji = "✅"
        else:
            action = "incomplete"
            emoji = "⏳"

        lines = [
            f"{emoji} Mark task #{task_id}: '{title}' as {action}?"
        ]

        # Show confidence score if from fuzzy match
        if confidence_score is not None and confidence_score < 100:
            lines.append(f"   ({confidence_score}% match)")

        lines.append("")

        # Show current status
        current_emoji = "✅" if current_status else "⏳"
        current_text = "Complete" if current_status else "Pending"
        lines.append(f"Current status: {current_emoji} {current_text}")

        lines.append("")
        lines.append("Reply 'yes' to confirm or 'no' to cancel.")

        return "\n".join(lines)

    def format_completion_success(
        self,
        task_details: Dict[str, Any],
        completed: bool
    ) -> str:
        """
        Format success message after completing/uncompleting task.

        Args:
            task_details: Updated task details
            completed: New completion status

        Returns:
            Formatted success message
        """
        task_id = task_details.get('id', '?')
        title = task_details.get('title', 'Unknown')

        if completed:
            return f"✅ Task #{task_id}: '{title}' marked as complete!"
        else:
            return f"⏳ Task #{task_id}: '{title}' marked as incomplete."
