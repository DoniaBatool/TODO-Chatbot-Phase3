"""
Comprehensive unit tests for IntentClassifier with 100+ test messages.

Goal: Validate 95%+ intent classification accuracy across all intent types.
Focus: Zero command-as-title errors, context-aware classification.
"""

import pytest
from src.services.intent_classifier import IntentClassifier, Intent


class TestAddTaskIntent:
    """Test ADD_TASK intent detection (20 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_add_task_simple(self, classifier):
        """Simple add task command."""
        result = classifier.classify("add task to buy milk")
        assert result.intent_type == Intent.ADD_TASK
        assert result.confidence >= 0.8
        assert "milk" in result.extracted_entities.get("title", "").lower()

    def test_add_task_with_priority(self, classifier):
        """Add task with priority."""
        result = classifier.classify("add high priority task to call mom")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "high"

    def test_add_urgent_task(self, classifier):
        """Add urgent task."""
        result = classifier.classify("add urgent task to finish report")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "high"

    def test_create_task(self, classifier):
        """Create task variant."""
        result = classifier.classify("create task to review PR")
        assert result.intent_type == Intent.ADD_TASK

    def test_new_task(self, classifier):
        """New task variant."""
        result = classifier.classify("new task for meeting prep")
        assert result.intent_type == Intent.ADD_TASK

    def test_make_task(self, classifier):
        """Make task variant."""
        result = classifier.classify("make a task to update docs")
        assert result.intent_type == Intent.ADD_TASK

    def test_want_to(self, classifier):
        """Want to variant."""
        result = classifier.classify("I want to add buy groceries")
        assert result.intent_type == Intent.ADD_TASK

    def test_need_to(self, classifier):
        """Need to variant."""
        result = classifier.classify("I need to call the dentist")
        assert result.intent_type == Intent.ADD_TASK

    def test_have_to(self, classifier):
        """Have to variant."""
        result = classifier.classify("I have to finish homework")
        assert result.intent_type == Intent.ADD_TASK

    def test_remind_me_to(self, classifier):
        """Remind me to variant."""
        result = classifier.classify("remind me to pay bills")
        assert result.intent_type == Intent.ADD_TASK

    def test_remember_to(self, classifier):
        """Remember to variant."""
        result = classifier.classify("remember me to schedule dentist")
        assert result.intent_type == Intent.ADD_TASK

    def test_add_with_article(self, classifier):
        """Add task with article."""
        result = classifier.classify("add a task to water plants")
        assert result.intent_type == Intent.ADD_TASK

    def test_add_low_priority(self, classifier):
        """Add low priority task."""
        result = classifier.classify("add low priority task to organize desk")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "low"

    def test_add_medium_priority(self, classifier):
        """Add medium priority task."""
        result = classifier.classify("add medium priority task to review code")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "medium"

    def test_add_normal_priority(self, classifier):
        """Add normal priority (maps to medium)."""
        result = classifier.classify("add normal task to check email")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "medium"

    def test_add_important_task(self, classifier):
        """Add important task (maps to high)."""
        result = classifier.classify("add important task to submit report")
        assert result.intent_type == Intent.ADD_TASK
        assert result.extracted_entities.get("priority") == "high"

    def test_add_multiple_words_title(self, classifier):
        """Add task with multi-word title."""
        result = classifier.classify("add task to buy organic milk from whole foods")
        assert result.intent_type == Intent.ADD_TASK
        assert "milk" in result.extracted_entities.get("title", "").lower()

    def test_add_with_special_chars(self, classifier):
        """Add task with special characters."""
        result = classifier.classify("add task: buy @groceries #2 (organic)")
        assert result.intent_type == Intent.ADD_TASK

    def test_add_with_numbers(self, classifier):
        """Add task with numbers."""
        result = classifier.classify("add task to call 555-1234")
        assert result.intent_type == Intent.ADD_TASK

    def test_add_mixed_case(self, classifier):
        """Add task with mixed case."""
        result = classifier.classify("Add Task To Buy Milk")
        assert result.intent_type == Intent.ADD_TASK


class TestDeleteTaskIntent:
    """Test DELETE_TASK intent detection (15 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_delete_task_by_id(self, classifier):
        """Delete task by ID."""
        result = classifier.classify("delete task 5")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_delete_task_with_the(self, classifier):
        """Delete the task variant."""
        result = classifier.classify("delete the task 10")
        assert result.intent_type == Intent.DELETE_TASK

    def test_remove_task(self, classifier):
        """Remove task variant."""
        result = classifier.classify("remove task 3")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 3

    def test_cancel_task(self, classifier):
        """Cancel task variant."""
        result = classifier.classify("cancel task 7")
        assert result.intent_type == Intent.DELETE_TASK

    def test_erase_task(self, classifier):
        """Erase task variant."""
        result = classifier.classify("erase task 2")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_by_name(self, classifier):
        """Delete task by name reference."""
        result = classifier.classify("delete the milk task")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_name") == "milk"

    def test_remove_by_name(self, classifier):
        """Remove task by name."""
        result = classifier.classify("remove the report task")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_large_id(self, classifier):
        """Delete task with large ID."""
        result = classifier.classify("delete task 9999")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.extracted_entities.get("task_id") == 9999

    def test_delete_no_id(self, classifier):
        """Delete task without ID."""
        result = classifier.classify("delete task")
        assert result.intent_type == Intent.DELETE_TASK
        # Should still classify as DELETE even without ID

    def test_delete_lowercase(self, classifier):
        """Delete with lowercase."""
        result = classifier.classify("delete task 5")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_uppercase(self, classifier):
        """Delete with uppercase."""
        result = classifier.classify("DELETE TASK 5")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_mixed_case(self, classifier):
        """Delete with mixed case."""
        result = classifier.classify("Delete Task 5")
        assert result.intent_type == Intent.DELETE_TASK

    def test_remove_the_task(self, classifier):
        """Remove the task variant."""
        result = classifier.classify("remove the task 8")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_task_sentence(self, classifier):
        """Delete in sentence context."""
        result = classifier.classify("please delete task 4")
        assert result.intent_type == Intent.DELETE_TASK

    def test_delete_task_question(self, classifier):
        """Delete as question."""
        result = classifier.classify("can you delete task 6?")
        assert result.intent_type == Intent.DELETE_TASK


class TestUpdateTaskIntent:
    """Test UPDATE_TASK intent detection (15 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_update_task_by_id(self, classifier):
        """Update task by ID."""
        result = classifier.classify("update task 5")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_update_with_priority(self, classifier):
        """Update with priority."""
        result = classifier.classify("update task 3 to high priority")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("priority") == "high"

    def test_change_task(self, classifier):
        """Change task variant."""
        result = classifier.classify("change task 7")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_modify_task(self, classifier):
        """Modify task variant."""
        result = classifier.classify("modify task 2")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_edit_task(self, classifier):
        """Edit task variant."""
        result = classifier.classify("edit task 9")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_update_by_name(self, classifier):
        """Update task by name."""
        result = classifier.classify("update the milk task")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("task_name") == "milk"

    def test_change_by_name(self, classifier):
        """Change task by name."""
        result = classifier.classify("change the report task")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_make_it_priority(self, classifier):
        """Make it priority pattern."""
        result = classifier.classify("make it high priority")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.extracted_entities.get("priority") == "high"

    def test_set_it_priority(self, classifier):
        """Set it priority pattern."""
        result = classifier.classify("set it to low priority")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_update_no_id(self, classifier):
        """Update without ID."""
        result = classifier.classify("update task")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_update_the_task(self, classifier):
        """Update the task variant."""
        result = classifier.classify("update the task 4")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_change_priority_only(self, classifier):
        """Change priority without task reference."""
        result = classifier.classify("change priority to medium")
        # Could be UPDATE_TASK or PROVIDE_INFO depending on context

    def test_update_sentence(self, classifier):
        """Update in sentence."""
        result = classifier.classify("please update task 6")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_update_question(self, classifier):
        """Update as question."""
        result = classifier.classify("can you update task 8?")
        assert result.intent_type == Intent.UPDATE_TASK

    def test_modify_the_task(self, classifier):
        """Modify the task variant."""
        result = classifier.classify("modify the task 3")
        assert result.intent_type == Intent.UPDATE_TASK


class TestCompleteTaskIntent:
    """Test COMPLETE_TASK intent detection (15 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_mark_complete(self, classifier):
        """Mark as complete."""
        result = classifier.classify("mark task 5 as complete")
        assert result.intent_type == Intent.COMPLETE_TASK
        assert result.extracted_entities.get("task_id") == 5

    def test_mark_done(self, classifier):
        """Mark as done."""
        result = classifier.classify("mark task 3 as done")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_mark_finished(self, classifier):
        """Mark as finished."""
        result = classifier.classify("mark task 7 as finished")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_set_complete(self, classifier):
        """Set as complete."""
        result = classifier.classify("set task 2 as complete")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_complete_task(self, classifier):
        """Complete task variant."""
        result = classifier.classify("complete task 4")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_finish_task(self, classifier):
        """Finish task variant."""
        result = classifier.classify("finish task 6")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_done_with_task(self, classifier):
        """Done with task variant."""
        result = classifier.classify("done with task 8")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_i_finished(self, classifier):
        """I finished variant."""
        result = classifier.classify("I finished buying milk")
        assert result.intent_type == Intent.COMPLETE_TASK
        assert "milk" in result.extracted_entities.get("task_name", "").lower()

    def test_i_completed(self, classifier):
        """I completed variant."""
        result = classifier.classify("I completed the report")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_i_done(self, classifier):
        """I'm done variant."""
        result = classifier.classify("I'm done with groceries")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_task_is_done(self, classifier):
        """Task is done variant."""
        result = classifier.classify("task 9 is done")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_task_is_complete(self, classifier):
        """Task is complete variant."""
        result = classifier.classify("task 10 is complete")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_task_is_finished(self, classifier):
        """Task is finished variant."""
        result = classifier.classify("task 5 is finished")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_complete_without_id(self, classifier):
        """Complete without ID."""
        result = classifier.classify("mark as complete")
        assert result.intent_type == Intent.COMPLETE_TASK

    def test_finished_task_name(self, classifier):
        """Finished with task name."""
        result = classifier.classify("I finished the homework task")
        assert result.intent_type == Intent.COMPLETE_TASK


class TestListTasksIntent:
    """Test LIST_TASKS intent detection (15 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_show_tasks(self, classifier):
        """Show tasks."""
        result = classifier.classify("show my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_list_tasks(self, classifier):
        """List tasks."""
        result = classifier.classify("list my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_display_tasks(self, classifier):
        """Display tasks."""
        result = classifier.classify("display my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_view_tasks(self, classifier):
        """View tasks."""
        result = classifier.classify("view my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_get_tasks(self, classifier):
        """Get tasks."""
        result = classifier.classify("get my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_show_all_tasks(self, classifier):
        """Show all tasks."""
        result = classifier.classify("show all tasks")
        assert result.intent_type == Intent.LIST_TASKS
        assert result.extracted_entities.get("status") == "all"

    def test_show_pending_tasks(self, classifier):
        """Show pending tasks."""
        result = classifier.classify("show pending tasks")
        assert result.intent_type == Intent.LIST_TASKS
        assert result.extracted_entities.get("status") == "pending"

    def test_show_completed_tasks(self, classifier):
        """Show completed tasks."""
        result = classifier.classify("show completed tasks")
        assert result.intent_type == Intent.LIST_TASKS
        assert result.extracted_entities.get("status") == "completed"

    def test_list_all_tasks(self, classifier):
        """List all tasks."""
        result = classifier.classify("list all my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_what_are_my_tasks(self, classifier):
        """What are my tasks."""
        result = classifier.classify("what are my tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_show_the_tasks(self, classifier):
        """Show the tasks."""
        result = classifier.classify("show the tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_display_all_tasks(self, classifier):
        """Display all tasks."""
        result = classifier.classify("display all tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_list_pending(self, classifier):
        """List pending."""
        result = classifier.classify("list pending tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_view_completed(self, classifier):
        """View completed."""
        result = classifier.classify("view completed tasks")
        assert result.intent_type == Intent.LIST_TASKS

    def test_get_all_tasks(self, classifier):
        """Get all tasks."""
        result = classifier.classify("get all tasks")
        assert result.intent_type == Intent.LIST_TASKS


class TestCancelIntent:
    """Test CANCEL_OPERATION intent detection (10 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_cancel(self, classifier):
        """Cancel."""
        result = classifier.classify("cancel", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_never_mind(self, classifier):
        """Never mind."""
        result = classifier.classify("never mind", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_nevermind(self, classifier):
        """Nevermind (no space)."""
        result = classifier.classify("nevermind", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_stop(self, classifier):
        """Stop."""
        result = classifier.classify("stop", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_abort(self, classifier):
        """Abort."""
        result = classifier.classify("abort", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_forget_it(self, classifier):
        """Forget it."""
        result = classifier.classify("forget it", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_dont_bother(self, classifier):
        """Don't bother."""
        result = classifier.classify("don't bother", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_cancel_uppercase(self, classifier):
        """Cancel uppercase."""
        result = classifier.classify("CANCEL", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_never_mind_with_punctuation(self, classifier):
        """Never mind with punctuation."""
        result = classifier.classify("never mind.", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION

    def test_cancel_in_sentence(self, classifier):
        """Cancel in sentence."""
        result = classifier.classify("please cancel this", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.CANCEL_OPERATION


class TestProvideInformationIntent:
    """Test PROVIDE_INFORMATION intent detection (10 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_yes_confirmation(self, classifier):
        """Yes confirmation."""
        result = classifier.classify("yes", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == True

    def test_no_confirmation(self, classifier):
        """No confirmation."""
        result = classifier.classify("no", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("confirmation") == False

    def test_yeah(self, classifier):
        """Yeah variant."""
        result = classifier.classify("yeah", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION

    def test_nope(self, classifier):
        """Nope variant."""
        result = classifier.classify("nope", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION

    def test_sure(self, classifier):
        """Sure variant."""
        result = classifier.classify("sure", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION

    def test_okay(self, classifier):
        """Okay variant."""
        result = classifier.classify("okay", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION

    def test_priority_high(self, classifier):
        """High priority information."""
        result = classifier.classify("high priority", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "high"

    def test_priority_low(self, classifier):
        """Low priority information."""
        result = classifier.classify("low priority", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "low"

    def test_single_word_title(self, classifier):
        """Single word as title."""
        result = classifier.classify("milk", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("title") == "milk"

    def test_make_it_high(self, classifier):
        """Make it high pattern."""
        result = classifier.classify("make it high priority", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.PROVIDE_INFORMATION
        assert result.extracted_entities.get("priority") == "high"


class TestCriticalEdgeCases:
    """Critical edge cases - zero command-as-title errors (10 test cases)."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_delete_not_title_in_neutral(self, classifier):
        """'delete task 5' should never be a task title."""
        result = classifier.classify("delete task 5", current_intent="NEUTRAL")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.intent_type != Intent.ADD_TASK

    def test_update_not_title_in_neutral(self, classifier):
        """'update task 3' should never be a task title."""
        result = classifier.classify("update task 3", current_intent="NEUTRAL")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.intent_type != Intent.ADD_TASK

    def test_delete_not_title_in_adding(self, classifier):
        """'delete task 5' during ADD should switch intent."""
        result = classifier.classify("delete task 5", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.DELETE_TASK
        assert result.intent_type != Intent.PROVIDE_INFORMATION

    def test_update_not_title_in_adding(self, classifier):
        """'update task 3' during ADD should switch intent."""
        result = classifier.classify("update task 3", current_intent="ADDING_TASK")
        assert result.intent_type == Intent.UPDATE_TASK
        assert result.intent_type != Intent.PROVIDE_INFORMATION

    def test_list_not_title(self, classifier):
        """'show my tasks' should never be a title."""
        result = classifier.classify("show my tasks", current_intent="NEUTRAL")
        assert result.intent_type == Intent.LIST_TASKS
        assert result.intent_type != Intent.ADD_TASK

    def test_complete_not_title(self, classifier):
        """'mark as complete' should never be a title."""
        result = classifier.classify("mark task 5 as complete", current_intent="NEUTRAL")
        assert result.intent_type == Intent.COMPLETE_TASK
        assert result.intent_type != Intent.ADD_TASK

    def test_remove_not_title(self, classifier):
        """'remove task' should be delete, not add."""
        result = classifier.classify("remove task 7", current_intent="NEUTRAL")
        assert result.intent_type == Intent.DELETE_TASK

    def test_cancel_not_title(self, classifier):
        """'cancel task' should be delete, not add."""
        result = classifier.classify("cancel task 4", current_intent="NEUTRAL")
        assert result.intent_type == Intent.DELETE_TASK

    def test_display_not_title(self, classifier):
        """'display tasks' should be list, not add."""
        result = classifier.classify("display all tasks", current_intent="NEUTRAL")
        assert result.intent_type == Intent.LIST_TASKS

    def test_finish_not_title(self, classifier):
        """'finish task' should be complete, not add."""
        result = classifier.classify("finish task 9", current_intent="NEUTRAL")
        assert result.intent_type == Intent.COMPLETE_TASK
