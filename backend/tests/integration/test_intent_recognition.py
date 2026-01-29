"""
Integration tests for intent recognition in conversation flows.

Goal: Validate 95%+ intent classification accuracy in realistic conversation scenarios.
Focus: Multi-turn conversations, context switches, real-world user messages.
"""

import pytest
from src.services.intent_classifier import IntentClassifier, Intent


class TestRealWorldConversations:
    """Test intent recognition in realistic conversation flows."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_add_task_conversation_flow(self, classifier):
        """Test complete add-task conversation flow."""
        # User starts adding task
        r1 = classifier.classify("add task to buy milk", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.ADD_TASK
        assert "milk" in r1.extracted_entities.get("title", "").lower()

        # Bot asks for priority, user provides
        r2 = classifier.classify("high priority", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        assert r2.extracted_entities.get("priority") == "high"

        # Bot asks for deadline, user provides
        r3 = classifier.classify("tomorrow", current_intent="ADDING_TASK")
        assert r3.intent_type == Intent.PROVIDE_INFORMATION

        # Bot asks for description, user declines
        r4 = classifier.classify("no", current_intent="ADDING_TASK")
        assert r4.intent_type == Intent.PROVIDE_INFORMATION
        assert r4.extracted_entities.get("confirmation") == False

    def test_list_then_update_conversation(self, classifier):
        """Test list tasks then update one."""
        # User lists tasks
        r1 = classifier.classify("show my tasks", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.LIST_TASKS

        # User decides to update task 3
        r2 = classifier.classify("update task 3", current_intent="NEUTRAL")
        assert r2.intent_type == Intent.UPDATE_TASK
        assert r2.extracted_entities.get("task_id") == 3

        # Bot asks what to update, user provides priority
        r3 = classifier.classify("make it high priority", current_intent="UPDATING_TASK")
        assert r3.intent_type == Intent.PROVIDE_INFORMATION
        assert r3.extracted_entities.get("priority") == "high"

    def test_intent_switch_mid_add(self, classifier):
        """Test switching intent during add-task flow."""
        # User starts adding task
        r1 = classifier.classify("add task to call mom", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.ADD_TASK

        # Mid-flow, user asks to see tasks instead
        r2 = classifier.classify("show my tasks", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.LIST_TASKS

    def test_cancel_during_add(self, classifier):
        """Test canceling add-task flow."""
        # User starts adding task
        r1 = classifier.classify("add task to buy groceries", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.ADD_TASK

        # User cancels mid-flow
        r2 = classifier.classify("never mind", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.CANCEL_OPERATION

    def test_delete_then_list(self, classifier):
        """Test delete task then list remaining."""
        # User deletes task
        r1 = classifier.classify("delete task 5", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.DELETE_TASK
        assert r1.extracted_entities.get("task_id") == 5

        # User lists remaining tasks
        r2 = classifier.classify("show my tasks", current_intent="NEUTRAL")
        assert r2.intent_type == Intent.LIST_TASKS

    def test_complete_multiple_tasks(self, classifier):
        """Test completing multiple tasks in sequence."""
        # Complete first task
        r1 = classifier.classify("mark task 3 as complete", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.COMPLETE_TASK
        assert r1.extracted_entities.get("task_id") == 3

        # Complete second task
        r2 = classifier.classify("finish task 7", current_intent="NEUTRAL")
        assert r2.intent_type == Intent.COMPLETE_TASK
        assert r2.extracted_entities.get("task_id") == 7

        # Check remaining tasks
        r3 = classifier.classify("show pending tasks", current_intent="NEUTRAL")
        assert r3.intent_type == Intent.LIST_TASKS
        assert r3.extracted_entities.get("status") == "pending"


class TestContextAwareClassification:
    """Test context-aware intent classification."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_single_word_context_neutral_vs_adding(self, classifier):
        """Single word has different meaning in different contexts."""
        # In NEUTRAL context, "milk" is ambiguous
        r1 = classifier.classify("milk", current_intent="NEUTRAL")
        # Could be UNKNOWN or low-confidence ADD_TASK

        # In ADDING_TASK context, "milk" is providing title
        r2 = classifier.classify("milk", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        assert r2.extracted_entities.get("title") == "milk"

    def test_priority_keyword_context_aware(self, classifier):
        """'high priority' means different things in different contexts."""
        # In NEUTRAL context, part of ADD_TASK command
        r1 = classifier.classify("add high priority task", current_intent="NEUTRAL")
        assert r1.intent_type == Intent.ADD_TASK
        assert r1.extracted_entities.get("priority") == "high"

        # In ADDING_TASK context, providing priority info
        r2 = classifier.classify("high priority", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.PROVIDE_INFORMATION
        assert r2.extracted_entities.get("priority") == "high"

    def test_command_override_in_workflow(self, classifier):
        """Commands override workflow context."""
        # Even in ADDING_TASK, explicit commands switch intent
        r1 = classifier.classify("delete task 5", current_intent="ADDING_TASK")
        assert r1.intent_type == Intent.DELETE_TASK
        assert r1.extracted_entities.get("task_id") == 5

        r2 = classifier.classify("list my tasks", current_intent="ADDING_TASK")
        assert r2.intent_type == Intent.LIST_TASKS

        r3 = classifier.classify("update task 3", current_intent="ADDING_TASK")
        assert r3.intent_type == Intent.UPDATE_TASK


class TestAccuracyBenchmark:
    """Benchmark intent classification accuracy."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_add_task_accuracy(self, classifier):
        """Test ADD_TASK intent accuracy (20 samples)."""
        test_cases = [
            "add task to buy milk",
            "create a task for meeting prep",
            "new task to call dentist",
            "I want to add groceries",
            "I need to finish report",
            "remind me to pay bills",
            "add urgent task to submit PR",
            "add high priority task",
            "create low priority task for cleanup",
            "make a task to review code",
            "add task to schedule meeting",
            "create task for documentation",
            "new task: buy gift",
            "add important task to deploy",
            "I want to schedule dentist",
            "I need to call mom",
            "remind me to water plants",
            "remember to backup files",
            "add medium priority task to test",
            "create normal task for email"
        ]

        correct = 0
        for message in test_cases:
            result = classifier.classify(message, current_intent="NEUTRAL")
            if result.intent_type == Intent.ADD_TASK:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.95, f"ADD_TASK accuracy {accuracy:.1%} below 95% target"

    def test_delete_task_accuracy(self, classifier):
        """Test DELETE_TASK intent accuracy (15 samples)."""
        test_cases = [
            "delete task 5",
            "remove task 10",
            "delete the task 3",
            "remove the milk task",
            "delete task",
            "erase task 7",
            "cancel task 9",
            "delete the report task",
            "remove task 2",
            "delete task 100",
            "remove the task 15",
            "erase task 8",
            "delete task 1",
            "remove the shopping task",
            "cancel task 20"
        ]

        correct = 0
        for message in test_cases:
            result = classifier.classify(message, current_intent="NEUTRAL")
            if result.intent_type == Intent.DELETE_TASK:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.95, f"DELETE_TASK accuracy {accuracy:.1%} below 95% target"

    def test_list_tasks_accuracy(self, classifier):
        """Test LIST_TASKS intent accuracy (15 samples)."""
        test_cases = [
            "show my tasks",
            "list all tasks",
            "display tasks",
            "view my tasks",
            "get all tasks",
            "show pending tasks",
            "list completed tasks",
            "what are my tasks",
            "show all my tasks",
            "display all tasks",
            "view pending tasks",
            "list my tasks",
            "get my tasks",
            "show the tasks",
            "display completed tasks"
        ]

        correct = 0
        for message in test_cases:
            result = classifier.classify(message, current_intent="NEUTRAL")
            if result.intent_type == Intent.LIST_TASKS:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.95, f"LIST_TASKS accuracy {accuracy:.1%} below 95% target"

    def test_overall_accuracy(self, classifier):
        """Test overall intent classification accuracy (50 samples)."""
        test_cases = [
            # ADD_TASK (10)
            ("add task to buy milk", Intent.ADD_TASK),
            ("create task for meeting", Intent.ADD_TASK),
            ("I need to call mom", Intent.ADD_TASK),
            ("remind me to pay bills", Intent.ADD_TASK),
            ("add urgent task to deploy", Intent.ADD_TASK),
            ("new task to review code", Intent.ADD_TASK),
            ("add high priority task", Intent.ADD_TASK),
            ("I want to schedule dentist", Intent.ADD_TASK),
            ("make a task to test", Intent.ADD_TASK),
            ("create low priority task", Intent.ADD_TASK),
            # DELETE_TASK (10)
            ("delete task 5", Intent.DELETE_TASK),
            ("remove task 3", Intent.DELETE_TASK),
            ("delete the milk task", Intent.DELETE_TASK),
            ("erase task 7", Intent.DELETE_TASK),
            ("cancel task 9", Intent.DELETE_TASK),
            ("remove the task 15", Intent.DELETE_TASK),
            ("delete task", Intent.DELETE_TASK),
            ("remove the report task", Intent.DELETE_TASK),
            ("delete task 100", Intent.DELETE_TASK),
            ("erase task 2", Intent.DELETE_TASK),
            # UPDATE_TASK (10)
            ("update task 5", Intent.UPDATE_TASK),
            ("change task 3", Intent.UPDATE_TASK),
            ("modify task 7", Intent.UPDATE_TASK),
            ("edit task 2", Intent.UPDATE_TASK),
            ("update the milk task", Intent.UPDATE_TASK),
            ("change the report task", Intent.UPDATE_TASK),
            ("make it high priority", Intent.UPDATE_TASK),
            ("set it to low priority", Intent.UPDATE_TASK),
            ("update task", Intent.UPDATE_TASK),
            ("change task 10", Intent.UPDATE_TASK),
            # COMPLETE_TASK (10)
            ("mark task 5 as complete", Intent.COMPLETE_TASK),
            ("finish task 3", Intent.COMPLETE_TASK),
            ("complete task 7", Intent.COMPLETE_TASK),
            ("I finished buying milk", Intent.COMPLETE_TASK),
            ("task 9 is done", Intent.COMPLETE_TASK),
            ("mark as complete", Intent.COMPLETE_TASK),
            ("done with task 15", Intent.COMPLETE_TASK),
            ("task 2 is finished", Intent.COMPLETE_TASK),
            ("I completed the report", Intent.COMPLETE_TASK),
            ("finish task 20", Intent.COMPLETE_TASK),
            # LIST_TASKS (10)
            ("show my tasks", Intent.LIST_TASKS),
            ("list all tasks", Intent.LIST_TASKS),
            ("display tasks", Intent.LIST_TASKS),
            ("view my tasks", Intent.LIST_TASKS),
            ("what are my tasks", Intent.LIST_TASKS),
            ("show pending tasks", Intent.LIST_TASKS),
            ("list completed tasks", Intent.LIST_TASKS),
            ("get all tasks", Intent.LIST_TASKS),
            ("display all tasks", Intent.LIST_TASKS),
            ("show the tasks", Intent.LIST_TASKS),
        ]

        correct = 0
        for message, expected_intent in test_cases:
            result = classifier.classify(message, current_intent="NEUTRAL")
            if result.intent_type == expected_intent:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.95, f"Overall accuracy {accuracy:.1%} below 95% target"

        print(f"\n✅ Overall intent classification accuracy: {accuracy:.1%}")
