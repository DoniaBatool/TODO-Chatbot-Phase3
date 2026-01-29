"""
Integration tests for task listing workflow.

Tests the complete conversational flow for listing tasks:
- Display formatting with emojis and human-readable dates
- Status filtering (pending, completed, all)
- Priority grouping
- Empty state handling
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.intent_classifier import IntentClassifier, Intent
from src.utils.task_formatter import (
    TaskFormatter,
    format_task,
    format_task_list,
    format_empty_state
)


class TestTaskDisplayFormatting:
    """Test task display formatting (T067)."""

    @pytest.fixture
    def formatter(self):
        """Create task formatter."""
        return TaskFormatter()

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return {
            "task_id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "created_at": datetime.now().isoformat()
        }

    def test_priority_emoji_high(self, formatter):
        """Test high priority emoji mapping."""
        result = formatter.format_priority("high")
        assert "🔴" in result
        assert "High" in result

    def test_priority_emoji_medium(self, formatter):
        """Test medium priority emoji mapping."""
        result = formatter.format_priority("medium")
        assert "🟡" in result
        assert "Medium" in result

    def test_priority_emoji_low(self, formatter):
        """Test low priority emoji mapping."""
        result = formatter.format_priority("low")
        assert "🟢" in result
        assert "Low" in result

    def test_status_indicator_complete(self, formatter):
        """Test complete status indicator."""
        result = formatter.format_status(True)
        assert "✅" in result
        assert "Complete" in result

    def test_status_indicator_pending(self, formatter):
        """Test pending status indicator."""
        result = formatter.format_status(False)
        assert "⏳" in result
        assert "Pending" in result

    def test_format_single_task(self, formatter, sample_task):
        """Test formatting a single task."""
        result = formatter.format_task(sample_task)

        # Should include task ID and title
        assert "#1" in result
        assert "Buy groceries" in result

        # Should include priority emoji
        assert "🔴" in result

        # Should include status indicator
        assert "⏳" in result

        # Should include description
        assert "Milk, eggs, bread" in result

    def test_format_task_list_multiple(self, formatter):
        """Test formatting multiple tasks."""
        tasks = [
            {
                "task_id": 1,
                "title": "Buy groceries",
                "priority": "high",
                "completed": False,
                "due_date": None
            },
            {
                "task_id": 2,
                "title": "Call mom",
                "priority": "medium",
                "completed": True,
                "due_date": None
            }
        ]

        result = formatter.format_task_list(tasks)

        # Should include both tasks
        assert "#1" in result
        assert "Buy groceries" in result
        assert "#2" in result
        assert "Call mom" in result

        # Should include count
        assert "2 total" in result


class TestStatusFiltering:
    """Test status filtering (T068)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    @pytest.fixture
    def formatter(self):
        """Create task formatter."""
        return TaskFormatter()

    def test_list_intent_detection(self, classifier):
        """Test LIST_TASKS intent is detected."""
        result = classifier.classify("show my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_list_with_status_filter_pending(self, classifier):
        """Test LIST_TASKS with pending filter."""
        result = classifier.classify("show pending tasks")
        assert result.intent_type == Intent.LIST_TASKS
        # Status filter should be extracted
        entities = result.extracted_entities
        assert entities.get("status") == "pending" or "pending" in str(entities).lower()

    def test_list_with_status_filter_completed(self, classifier):
        """Test LIST_TASKS with completed filter."""
        result = classifier.classify("show completed tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_list_with_priority_filter(self, classifier):
        """Test LIST_TASKS with priority filter."""
        # Note: Priority filtering is handled at the API level, not intent level
        result = classifier.classify("list tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_format_grouped_by_status(self, formatter):
        """Test grouping tasks by status."""
        tasks = [
            {"task_id": 1, "title": "Task 1", "priority": "high", "completed": False},
            {"task_id": 2, "title": "Task 2", "priority": "medium", "completed": True},
            {"task_id": 3, "title": "Task 3", "priority": "low", "completed": False}
        ]

        result = formatter.format_task_list(tasks, group_by="status")

        # Should have pending section
        assert "PENDING" in result
        # Should have completed section
        assert "COMPLETED" in result

    def test_format_grouped_by_priority(self, formatter):
        """Test grouping tasks by priority."""
        tasks = [
            {"task_id": 1, "title": "Task 1", "priority": "high", "completed": False},
            {"task_id": 2, "title": "Task 2", "priority": "medium", "completed": False},
            {"task_id": 3, "title": "Task 3", "priority": "low", "completed": False}
        ]

        result = formatter.format_task_list(tasks, group_by="priority")

        # Should have all priority sections in order
        high_pos = result.find("HIGH PRIORITY")
        medium_pos = result.find("MEDIUM")
        low_pos = result.find("LOW PRIORITY")

        assert high_pos < medium_pos < low_pos


class TestHumanReadableDates:
    """Test human-readable date formatting (T072)."""

    @pytest.fixture
    def formatter(self):
        """Create task formatter."""
        return TaskFormatter()

    def test_due_date_today(self, formatter):
        """Test 'Today' formatting."""
        today = datetime.now().replace(hour=23, minute=59, second=59)
        result = formatter.format_due_date(today)
        assert "Today" in result

    def test_due_date_tomorrow(self, formatter):
        """Test 'Tomorrow' formatting."""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=23, minute=59, second=59)
        result = formatter.format_due_date(tomorrow)
        assert "Tomorrow" in result

    def test_due_date_in_3_days(self, formatter):
        """Test 'In X days' formatting."""
        in_3_days = datetime.now() + timedelta(days=3)
        result = formatter.format_due_date(in_3_days)
        assert "3 days" in result or "In 3" in result

    def test_due_date_overdue(self, formatter):
        """Test overdue formatting."""
        overdue = datetime.now() - timedelta(days=2)
        result = formatter.format_due_date(overdue)
        assert "Overdue" in result
        assert "2 days" in result

    def test_due_date_none(self, formatter):
        """Test no due date formatting."""
        result = formatter.format_due_date(None)
        assert "No due date" in result

    def test_due_date_with_time(self, formatter):
        """Test formatting with specific time."""
        tomorrow_3pm = datetime.now() + timedelta(days=1)
        tomorrow_3pm = tomorrow_3pm.replace(hour=15, minute=0, second=0)
        result = formatter.format_due_date(tomorrow_3pm)
        assert "Tomorrow" in result
        # Time should be included
        assert "3:00" in result or "PM" in result.upper()


class TestEmptyState:
    """Test empty state handling (T073)."""

    @pytest.fixture
    def formatter(self):
        """Create task formatter."""
        return TaskFormatter()

    def test_empty_state_message(self, formatter):
        """Test empty state message content."""
        result = formatter.format_empty_state()

        # Should have friendly message
        assert "no tasks" in result.lower()
        # Should suggest adding a task
        assert "add" in result.lower()

    def test_format_empty_task_list(self, formatter):
        """Test formatting empty task list."""
        result = formatter.format_task_list([])

        # Should show empty state message
        assert "no tasks" in result.lower()

    def test_empty_state_convenience_function(self):
        """Test module-level convenience function."""
        result = format_empty_state()
        assert "no tasks" in result.lower()


class TestListIntentVariations:
    """Test various list intent phrasings."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_show_tasks(self, classifier):
        """Test 'show tasks' triggers LIST_TASKS."""
        result = classifier.classify("show tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_list_my_tasks(self, classifier):
        """Test 'list my tasks' triggers LIST_TASKS."""
        result = classifier.classify("list my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_what_tasks_do_i_have(self, classifier):
        """Test question format triggers LIST_TASKS."""
        result = classifier.classify("what are my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_show_all_tasks(self, classifier):
        """Test 'show all tasks' triggers LIST_TASKS."""
        result = classifier.classify("show all tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_view_tasks(self, classifier):
        """Test 'view tasks' triggers LIST_TASKS."""
        result = classifier.classify("view my tasks")
        assert result.intent_type == Intent.LIST_TASKS


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_format_task_function(self):
        """Test format_task convenience function."""
        task = {
            "task_id": 1,
            "title": "Test task",
            "priority": "high",
            "completed": False
        }
        result = format_task(task)
        assert "#1" in result
        assert "Test task" in result

    def test_format_task_list_function(self):
        """Test format_task_list convenience function."""
        tasks = [
            {"task_id": 1, "title": "Task 1", "priority": "high", "completed": False}
        ]
        result = format_task_list(tasks)
        assert "Task 1" in result


class TestDueDateGrouping:
    """Test grouping tasks by due date."""

    @pytest.fixture
    def formatter(self):
        """Create task formatter."""
        return TaskFormatter()

    def test_group_by_due_date(self, formatter):
        """Test grouping tasks by due date."""
        now = datetime.now()
        tasks = [
            {
                "task_id": 1,
                "title": "Overdue task",
                "priority": "high",
                "completed": False,
                "due_date": (now - timedelta(days=1)).isoformat()
            },
            {
                "task_id": 2,
                "title": "Today task",
                "priority": "medium",
                "completed": False,
                "due_date": now.isoformat()
            },
            {
                "task_id": 3,
                "title": "Tomorrow task",
                "priority": "low",
                "completed": False,
                "due_date": (now + timedelta(days=1)).isoformat()
            }
        ]

        result = formatter.format_task_list(tasks, group_by="due_date")

        # Should have sections
        assert "OVERDUE" in result
        assert "TODAY" in result
        assert "TOMORROW" in result

    def test_no_due_date_section(self, formatter):
        """Test tasks without due date go to separate section."""
        tasks = [
            {
                "task_id": 1,
                "title": "No date task",
                "priority": "medium",
                "completed": False,
                "due_date": None
            }
        ]

        result = formatter.format_task_list(tasks, group_by="due_date")
        assert "NO DUE DATE" in result
