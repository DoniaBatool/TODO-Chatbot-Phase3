"""
Task display formatting utility.

Provides rich formatting for task display:
- Priority emojis (🔴 high, 🟡 medium, 🟢 low)
- Status indicators (✅ complete, ⏳ pending)
- Human-readable dates ("tomorrow", "in 3 days", "overdue by 2 days")

Part of US5 implementation (Phase 7).
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class TaskFormatter:
    """Format tasks for display with emojis and human-readable text."""

    # Priority emoji mapping (T070)
    PRIORITY_EMOJIS = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    # Status indicator mapping (T071)
    STATUS_INDICATORS = {
        True: "✅",   # completed
        False: "⏳"   # pending
    }

    # Status text mapping
    STATUS_TEXT = {
        True: "Complete",
        False: "Pending"
    }

    def format_priority(self, priority: str) -> str:
        """
        Format priority with emoji.

        Args:
            priority: Priority level ('high', 'medium', 'low')

        Returns:
            Priority with emoji (e.g., "🔴 High")

        Example:
            >>> formatter = TaskFormatter()
            >>> formatter.format_priority("high")
            '🔴 High'
        """
        emoji = self.PRIORITY_EMOJIS.get(priority, "⚪")
        return f"{emoji} {priority.title()}"

    def format_status(self, completed: bool) -> str:
        """
        Format status with indicator.

        Args:
            completed: Whether task is completed

        Returns:
            Status with indicator (e.g., "✅ Complete")

        Example:
            >>> formatter = TaskFormatter()
            >>> formatter.format_status(True)
            '✅ Complete'
            >>> formatter.format_status(False)
            '⏳ Pending'
        """
        indicator = self.STATUS_INDICATORS.get(completed, "❓")
        text = self.STATUS_TEXT.get(completed, "Unknown")
        return f"{indicator} {text}"

    def format_due_date(
        self,
        due_date: Optional[datetime],
        reference_date: Optional[datetime] = None
    ) -> str:
        """
        Format due date as human-readable text (T072).

        Args:
            due_date: Task due date
            reference_date: Reference date for relative formatting (defaults to now)

        Returns:
            Human-readable date string

        Examples:
            >>> formatter = TaskFormatter()
            >>> from datetime import datetime, timedelta
            >>> tomorrow = datetime.now() + timedelta(days=1)
            >>> formatter.format_due_date(tomorrow)
            'Tomorrow'
            >>> in_3_days = datetime.now() + timedelta(days=3)
            >>> formatter.format_due_date(in_3_days)
            'In 3 days'
            >>> overdue = datetime.now() - timedelta(days=2)
            >>> formatter.format_due_date(overdue)
            '⚠️ Overdue by 2 days'
        """
        if due_date is None:
            return "No due date"

        reference = reference_date or datetime.now()

        # Normalize to date only for comparison
        due_date_only = due_date.replace(hour=23, minute=59, second=59, microsecond=0)
        ref_date_only = reference.replace(hour=0, minute=0, second=0, microsecond=0)

        delta = due_date_only - ref_date_only
        days = delta.days

        # Handle overdue
        if days < 0:
            abs_days = abs(days)
            if abs_days == 1:
                return "⚠️ Overdue by 1 day"
            return f"⚠️ Overdue by {abs_days} days"

        # Handle today
        if days == 0:
            # Check if there's a specific time
            if due_date.hour != 23 or due_date.minute != 59:
                return f"Today at {due_date.strftime('%I:%M %p').lstrip('0')}"
            return "Today"

        # Handle tomorrow
        if days == 1:
            if due_date.hour != 23 or due_date.minute != 59:
                return f"Tomorrow at {due_date.strftime('%I:%M %p').lstrip('0')}"
            return "Tomorrow"

        # Handle this week (2-6 days)
        if 2 <= days <= 6:
            return f"In {days} days ({due_date.strftime('%A')})"

        # Handle next week
        if 7 <= days <= 13:
            return f"Next {due_date.strftime('%A')}"

        # Handle within a month
        if days <= 30:
            weeks = days // 7
            if weeks == 2:
                return "In 2 weeks"
            elif weeks == 3:
                return "In 3 weeks"
            elif weeks == 4:
                return "In about a month"
            return f"In {days} days"

        # Handle longer dates
        return due_date.strftime("%B %d, %Y")

    def format_task(
        self,
        task: Dict[str, Any],
        include_description: bool = True,
        reference_date: Optional[datetime] = None
    ) -> str:
        """
        Format a single task for display.

        Args:
            task: Task dictionary with task_id, title, priority, completed, etc.
            include_description: Whether to include description in output
            reference_date: Reference date for relative due date formatting

        Returns:
            Formatted task string

        Example:
            >>> formatter = TaskFormatter()
            >>> task = {
            ...     "task_id": 1,
            ...     "title": "Buy milk",
            ...     "priority": "high",
            ...     "completed": False,
            ...     "due_date": None,
            ...     "description": "From the store"
            ... }
            >>> print(formatter.format_task(task))
            #1 Buy milk
               🔴 High | ⏳ Pending | No due date
               📝 From the store
        """
        task_id = task.get("task_id", "?")
        title = task.get("title", "Untitled")
        priority = task.get("priority", "medium")
        completed = task.get("completed", False)
        due_date = task.get("due_date")
        description = task.get("description")

        # Parse due_date if it's a string
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                due_date = None

        # Build formatted output
        lines = [f"#{task_id} {title}"]

        # Status line
        priority_str = self.format_priority(priority)
        status_str = self.format_status(completed)
        due_str = self.format_due_date(due_date, reference_date)

        lines.append(f"   {priority_str} | {status_str} | {due_str}")

        # Description (if present and requested)
        if include_description and description:
            # Truncate long descriptions
            desc_display = description[:60] + "..." if len(description) > 60 else description
            lines.append(f"   📝 {desc_display}")

        return "\n".join(lines)

    def format_task_list(
        self,
        tasks: List[Dict[str, Any]],
        group_by: Optional[str] = None,
        reference_date: Optional[datetime] = None
    ) -> str:
        """
        Format a list of tasks for display.

        Args:
            tasks: List of task dictionaries
            group_by: Optional grouping ('priority', 'status', 'due_date')
            reference_date: Reference date for relative due date formatting

        Returns:
            Formatted task list string

        Example:
            >>> formatter = TaskFormatter()
            >>> tasks = [
            ...     {"task_id": 1, "title": "Buy milk", "priority": "high", "completed": False},
            ...     {"task_id": 2, "title": "Call mom", "priority": "medium", "completed": True}
            ... ]
            >>> print(formatter.format_task_list(tasks))
        """
        if not tasks:
            return self.format_empty_state()

        # Group tasks if requested
        if group_by == "priority":
            return self._format_grouped_by_priority(tasks, reference_date)
        elif group_by == "status":
            return self._format_grouped_by_status(tasks, reference_date)
        elif group_by == "due_date":
            return self._format_grouped_by_due_date(tasks, reference_date)

        # Default: simple list
        lines = [f"📋 Your Tasks ({len(tasks)} total)", ""]

        for task in tasks:
            lines.append(self.format_task(task, reference_date=reference_date))
            lines.append("")  # Blank line between tasks

        return "\n".join(lines).rstrip()

    def format_empty_state(self) -> str:
        """
        Format empty state message (T073).

        Returns:
            Friendly message for no tasks

        Example:
            >>> formatter = TaskFormatter()
            >>> print(formatter.format_empty_state())
            📭 You have no tasks yet.

            Would you like to add one? Just say something like:
            "Add a task to buy groceries"
        """
        return """📭 You have no tasks yet.

Would you like to add one? Just say something like:
"Add a task to buy groceries\""""

    def _format_grouped_by_priority(
        self,
        tasks: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None
    ) -> str:
        """Format tasks grouped by priority."""
        priority_order = ["high", "medium", "low"]
        grouped = {p: [] for p in priority_order}

        for task in tasks:
            priority = task.get("priority", "medium")
            if priority in grouped:
                grouped[priority].append(task)
            else:
                grouped["medium"].append(task)

        lines = [f"📋 Your Tasks ({len(tasks)} total)", ""]

        for priority in priority_order:
            priority_tasks = grouped[priority]
            if priority_tasks:
                emoji = self.PRIORITY_EMOJIS.get(priority, "⚪")
                lines.append(f"─── {emoji} {priority.upper()} PRIORITY ({len(priority_tasks)}) ───")
                lines.append("")
                for task in priority_tasks:
                    lines.append(self.format_task(task, reference_date=reference_date))
                    lines.append("")

        return "\n".join(lines).rstrip()

    def _format_grouped_by_status(
        self,
        tasks: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None
    ) -> str:
        """Format tasks grouped by status."""
        pending = [t for t in tasks if not t.get("completed", False)]
        completed = [t for t in tasks if t.get("completed", False)]

        lines = [f"📋 Your Tasks ({len(tasks)} total)", ""]

        if pending:
            lines.append(f"─── ⏳ PENDING ({len(pending)}) ───")
            lines.append("")
            for task in pending:
                lines.append(self.format_task(task, reference_date=reference_date))
                lines.append("")

        if completed:
            lines.append(f"─── ✅ COMPLETED ({len(completed)}) ───")
            lines.append("")
            for task in completed:
                lines.append(self.format_task(task, reference_date=reference_date))
                lines.append("")

        return "\n".join(lines).rstrip()

    def _format_grouped_by_due_date(
        self,
        tasks: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None
    ) -> str:
        """Format tasks grouped by due date."""
        ref = reference_date or datetime.now()
        ref_date = ref.replace(hour=0, minute=0, second=0, microsecond=0)

        overdue = []
        today = []
        tomorrow = []
        this_week = []
        later = []
        no_date = []

        for task in tasks:
            due_date = task.get("due_date")
            if due_date is None:
                no_date.append(task)
                continue

            if isinstance(due_date, str):
                try:
                    due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except:
                    no_date.append(task)
                    continue

            delta = (due_date.replace(hour=0, minute=0, second=0, microsecond=0) - ref_date).days

            if delta < 0:
                overdue.append(task)
            elif delta == 0:
                today.append(task)
            elif delta == 1:
                tomorrow.append(task)
            elif delta <= 7:
                this_week.append(task)
            else:
                later.append(task)

        lines = [f"📋 Your Tasks ({len(tasks)} total)", ""]

        sections = [
            ("⚠️ OVERDUE", overdue),
            ("📅 TODAY", today),
            ("📆 TOMORROW", tomorrow),
            ("🗓️ THIS WEEK", this_week),
            ("📅 LATER", later),
            ("❓ NO DUE DATE", no_date)
        ]

        for title, section_tasks in sections:
            if section_tasks:
                lines.append(f"─── {title} ({len(section_tasks)}) ───")
                lines.append("")
                for task in section_tasks:
                    lines.append(self.format_task(task, reference_date=reference_date))
                    lines.append("")

        return "\n".join(lines).rstrip()


# Module-level instance for convenience
formatter = TaskFormatter()


def format_task(task: Dict[str, Any], **kwargs) -> str:
    """Convenience function to format a single task."""
    return formatter.format_task(task, **kwargs)


def format_task_list(tasks: List[Dict[str, Any]], **kwargs) -> str:
    """Convenience function to format a task list."""
    return formatter.format_task_list(tasks, **kwargs)


def format_empty_state() -> str:
    """Convenience function for empty state message."""
    return formatter.format_empty_state()
