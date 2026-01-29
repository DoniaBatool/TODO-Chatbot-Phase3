"""
Intent classification for natural language task management.

Detects user intent from messages and extracts relevant entities:
- ADD_TASK, UPDATE_TASK, DELETE_TASK, COMPLETE_TASK, LIST_TASKS
- CANCEL_OPERATION, PROVIDE_INFORMATION, UNKNOWN

Context-aware classification uses current conversation state to disambiguate.
"""

import re
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class Intent(str, Enum):
    """User intent types for task management operations."""

    ADD_TASK = "ADD_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    DELETE_TASK = "DELETE_TASK"
    COMPLETE_TASK = "COMPLETE_TASK"
    LIST_TASKS = "LIST_TASKS"
    CANCEL_OPERATION = "CANCEL_OPERATION"
    PROVIDE_INFORMATION = "PROVIDE_INFORMATION"
    UNKNOWN = "UNKNOWN"


@dataclass
class IntentResult:
    """Result of intent classification."""

    intent_type: Intent
    confidence: float
    extracted_entities: Dict[str, Any]


class IntentClassifier:
    """Classify user intent from natural language messages."""

    # Pattern groups for each intent type
    ADD_PATTERNS = [
        r'\b(add|create|new|make)\s+(a\s+)?(task|urgent\s+task)\b',
        r'\b(add|create)\s+(urgent|high\s+priority|important)\s+task\b',
        r'\b(add|create|new)\s+(high|medium|low|normal)\s+(priority\s+)?task\b',
        r'\b(add|create)\s+[\w\s]+task\b',  # General pattern: "add ... task"
        r'\b(want|need|have)\s+to\b',
        r'\b(remind|remember)\s+me\s+to\b',
    ]

    DELETE_PATTERNS = [
        r'\b(delete|remove|erase)\s+(the\s+)?task\s+(\d+)\b',
        r'\b(delete|remove|erase)\s+(the\s+)?task\b',
        r'\bcancel\s+task\s+(\d+)\b',
        r'\b(delete|remove)\s+the\s+\w+\s+task\b',
    ]

    UPDATE_PATTERNS = [
        r'\b(update|change|modify|edit)\s+(the\s+)?task\b',
        r'\b(update|change)\s+task\s+(\d+)\b',
        r'\b(change|update)\s+the\s+\w+\s+task\b',
        r'\b(make|set)\s+it\s+(to\s+)?(high|medium|low)\s+priority\b',
    ]

    COMPLETE_PATTERNS = [
        r'\b(mark|set)\s+(task\s+)?(\d+)?\s*as\s+(complete|done|finished)\b',
        r'\b(complete|finish)\s+task\s+(\d+)\b',
        r'\b(done\s+with)\s+task\s+(\d+)\b',
        r'\b(i\s+)?(finished|completed|done)\s+\w+(?!\s+tasks)',
        r'\btask\s+(\d+)\s+is\s+(done|complete|finished)\b',
    ]

    LIST_PATTERNS = [
        r'\b(show|list|display|view|get)\s+(my|all|the)?\s*(pending|completed|active)?\s*tasks?\b',
        r'\b(show|list|display)\s+(all\s+)?my\s+tasks?\b',
        r'\bwhat\s+(are\s+)?my\s+tasks\b',
        r'\b(show|list|view)\s+(pending|completed|all)\s+tasks\b',
    ]

    CANCEL_PATTERNS = [
        r'\b(never\s+mind|nevermind)\b',
        r'\b(cancel|stop|abort)(?!\s+task\s+\d)\b',
        r'\b(forget\s+it|don\'t\s+bother)\b',
    ]

    CONFIRMATION_PATTERNS = [
        r'^(yes|yeah|yep|yup|sure|ok|okay|confirm)$',
        r'^(no|nope|nah|don\'t)$',
    ]

    PRIORITY_PATTERNS = [
        r'\b(high|urgent|important)\s+(priority)?\b',
        r'\b(medium|normal)\s+(priority)?\b',
        r'\b(low)\s+(priority)?\b',
    ]

    def __init__(self):
        """Initialize the intent classifier."""
        pass

    def classify(
        self,
        message: str,
        current_intent: Optional[str] = None
    ) -> IntentResult:
        """
        Classify user intent from message.

        Args:
            message: User's natural language message
            current_intent: Current conversation state (e.g., "ADDING_TASK", "NEUTRAL")

        Returns:
            IntentResult with intent_type, confidence, and extracted_entities
        """
        if not message or not message.strip():
            return IntentResult(
                intent_type=Intent.UNKNOWN,
                confidence=0.0,
                extracted_entities={}
            )

        message_lower = message.lower().strip()
        current_intent = current_intent or "NEUTRAL"

        # Context-aware classification for information provision
        if current_intent != "NEUTRAL":
            info_result = self._classify_as_information(message_lower, current_intent)
            if info_result:
                return info_result

        # Check for cancellation first (highest priority)
        if self._matches_patterns(message_lower, self.CANCEL_PATTERNS):
            return IntentResult(
                intent_type=Intent.CANCEL_OPERATION,
                confidence=0.95,
                extracted_entities={}
            )

        # Check for task operations in priority order
        # LIST_TASKS before COMPLETE_TASK to avoid "show completed tasks" confusion
        if self._matches_patterns(message_lower, self.LIST_PATTERNS):
            entities = self._extract_list_entities(message_lower)
            return IntentResult(
                intent_type=Intent.LIST_TASKS,
                confidence=0.9,
                extracted_entities=entities
            )

        # ADD_TASK before COMPLETE_TASK to avoid "have to" confusion
        if self._matches_patterns(message_lower, self.ADD_PATTERNS):
            entities = self._extract_add_entities(message, message_lower)
            return IntentResult(
                intent_type=Intent.ADD_TASK,
                confidence=0.9,
                extracted_entities=entities
            )

        if self._matches_patterns(message_lower, self.DELETE_PATTERNS):
            entities = self._extract_delete_entities(message_lower)
            return IntentResult(
                intent_type=Intent.DELETE_TASK,
                confidence=0.9,
                extracted_entities=entities
            )

        if self._matches_patterns(message_lower, self.UPDATE_PATTERNS):
            entities = self._extract_update_entities(message_lower)
            return IntentResult(
                intent_type=Intent.UPDATE_TASK,
                confidence=0.9,
                extracted_entities=entities
            )

        if self._matches_patterns(message_lower, self.COMPLETE_PATTERNS):
            entities = self._extract_complete_entities(message_lower)
            return IntentResult(
                intent_type=Intent.COMPLETE_TASK,
                confidence=0.9,
                extracted_entities=entities
            )

        # If no pattern matches, classify as UNKNOWN
        return IntentResult(
            intent_type=Intent.UNKNOWN,
            confidence=0.3,
            extracted_entities={}
        )

    def _classify_as_information(
        self,
        message_lower: str,
        current_intent: str
    ) -> Optional[IntentResult]:
        """
        Check if message is providing information in current context.

        Returns IntentResult if message is information, None otherwise.
        """
        entities = {}

        # Check for confirmation/rejection
        if re.match(r'^(yes|yeah|yep|yup|sure|ok|okay|confirm)$', message_lower):
            return IntentResult(
                intent_type=Intent.PROVIDE_INFORMATION,
                confidence=0.95,
                extracted_entities={"confirmation": True}
            )

        if re.match(r'^(no|nope|nah|don\'t)$', message_lower):
            return IntentResult(
                intent_type=Intent.PROVIDE_INFORMATION,
                confidence=0.95,
                extracted_entities={"confirmation": False}
            )

        # In ADDING_TASK context, treat many inputs as information
        if current_intent == "ADDING_TASK":
            # Check for priority information
            priority = self._extract_priority(message_lower)
            if priority:
                entities["priority"] = priority

            # Single word or short phrase likely a title
            if len(message_lower.split()) <= 5 and not self._matches_any_command_pattern(message_lower):
                entities["title"] = message_lower

            # Check for "make it" patterns
            if re.search(r'\b(make|set)\s+it\b', message_lower):
                if priority:
                    entities["priority"] = priority
                return IntentResult(
                    intent_type=Intent.PROVIDE_INFORMATION,
                    confidence=0.9,
                    extracted_entities=entities
                )

            # If we extracted any entities, it's information
            if entities:
                return IntentResult(
                    intent_type=Intent.PROVIDE_INFORMATION,
                    confidence=0.85,
                    extracted_entities=entities
                )

        # In other contexts (UPDATING_TASK, DELETING_TASK, etc.)
        if current_intent in ["UPDATING_TASK", "DELETING_TASK", "COMPLETING_TASK"]:
            # Priority information
            priority = self._extract_priority(message_lower)
            if priority:
                return IntentResult(
                    intent_type=Intent.PROVIDE_INFORMATION,
                    confidence=0.85,
                    extracted_entities={"priority": priority}
                )

        return None

    def _matches_patterns(self, message: str, patterns: list) -> bool:
        """Check if message matches any pattern in the list."""
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in patterns)

    def _matches_any_command_pattern(self, message: str) -> bool:
        """Check if message matches any command pattern (including ADD_TASK)."""
        all_patterns = (
            self.ADD_PATTERNS +  # Include ADD_PATTERNS to detect nested add commands
            self.DELETE_PATTERNS +
            self.UPDATE_PATTERNS +
            self.COMPLETE_PATTERNS +
            self.LIST_PATTERNS +
            self.CANCEL_PATTERNS
        )
        return self._matches_patterns(message, all_patterns)

    def _extract_add_entities(self, original: str, message_lower: str) -> Dict[str, Any]:
        """Extract entities for ADD_TASK intent."""
        entities = {}

        # Extract priority
        priority = self._extract_priority(message_lower)
        if priority:
            entities["priority"] = priority

        # Extract title from natural language
        # Remove add/create keywords
        title = original
        title = re.sub(r'\b(add|create|new|make)\s+(a\s+)?task\s+(to\s+)?', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(want|need|have)\s+to\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(remind|remember)\s+me\s+to\s+', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\b(urgent|high|medium|low)\s+(priority)?\s*', '', title, flags=re.IGNORECASE)
        title = title.strip()

        if title:
            entities["title"] = title

        return entities

    def _extract_delete_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities for DELETE_TASK intent."""
        entities = {}

        # Extract task ID
        task_id_match = re.search(r'\btask\s+(\d+)\b', message)
        if task_id_match:
            entities["task_id"] = int(task_id_match.group(1))
        else:
            # Try standalone number after delete/remove
            standalone_match = re.search(r'\b(delete|remove)\s+task\s+(\d+)\b', message)
            if standalone_match:
                entities["task_id"] = int(standalone_match.group(2))

        # Extract task name
        name_match = re.search(r'\b(delete|remove)\s+the\s+(\w+)\s+task\b', message)
        if name_match:
            entities["task_name"] = name_match.group(2)

        return entities

    def _extract_update_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities for UPDATE_TASK intent."""
        entities = {}

        # Extract task ID
        task_id_match = re.search(r'\btask\s+(\d+)\b', message)
        if task_id_match:
            entities["task_id"] = int(task_id_match.group(1))

        # Extract task name
        name_match = re.search(r'\b(update|change)\s+the\s+(\w+)\s+task\b', message)
        if name_match:
            entities["task_name"] = name_match.group(2)

        # Extract priority
        priority = self._extract_priority(message)
        if priority:
            entities["priority"] = priority

        return entities

    def _extract_complete_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities for COMPLETE_TASK intent."""
        entities = {}

        # Extract task ID
        task_id_match = re.search(r'\btask\s+(\d+)\b', message)
        if task_id_match:
            entities["task_id"] = int(task_id_match.group(1))

        # Extract task name from "I finished [task name]"
        finished_match = re.search(r'\b(finished|completed|done)\s+(.+)$', message)
        if finished_match:
            task_name = finished_match.group(2).strip()
            # Clean up common suffixes
            task_name = re.sub(r'\s+(task)?$', '', task_name)
            if task_name:
                entities["task_name"] = task_name

        return entities

    def _extract_list_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities for LIST_TASKS intent."""
        entities = {}

        # Extract status filter
        if re.search(r'\bpending\b', message):
            entities["status"] = "pending"
        elif re.search(r'\bcompleted\b', message):
            entities["status"] = "completed"
        elif re.search(r'\ball\b', message):
            entities["status"] = "all"

        return entities

    def _extract_priority(self, message: str) -> Optional[str]:
        """Extract priority from message."""
        if re.search(r'\b(high|urgent|important)\b', message):
            return "high"
        elif re.search(r'\b(medium|normal)\b', message):
            return "medium"
        elif re.search(r'\blow\b', message):
            return "low"
        return None
