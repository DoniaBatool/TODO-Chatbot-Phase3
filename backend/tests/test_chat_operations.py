"""Comprehensive tests for AI Chat Assistant operations.

Tests all major operations:
1. Create/Add Task - Should ask for details, then create
2. Delete Task - Should ask which task, then confirm, then delete  
3. Update Task - Should ask which task, then what to update, then confirm, then update
4. Show All Tasks - Should list all tasks properly
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.main import app
from src.models import Task, User, Conversation, Message
from src.db import get_session
from src.ai_agent.intent_detector import detect_user_intent, Intent
import json
from datetime import datetime, timedelta

# Test client
client = TestClient(app)

# Test user credentials
TEST_USER_ID = "test-user-chat-ops"
TEST_USER_EMAIL = "chatops@test.com"


@pytest.fixture
def db_session():
    """Get database session for tests."""
    session = next(get_session())
    yield session
    session.close()


@pytest.fixture
def cleanup(db_session: Session):
    """Clean up test data after each test."""
    yield
    # Delete test tasks
    stmt = select(Task).where(Task.user_id == TEST_USER_ID)
    tasks = db_session.exec(stmt).all()
    for task in tasks:
        db_session.delete(task)
    
    # Delete test conversations
    stmt = select(Conversation).where(Conversation.user_id == TEST_USER_ID)
    convs = db_session.exec(stmt).all()
    for conv in convs:
        # Delete messages first
        stmt = select(Message).where(Message.conversation_id == conv.id)
        messages = db_session.exec(stmt).all()
        for msg in messages:
            db_session.delete(msg)
        db_session.delete(conv)
    
    db_session.commit()


def create_test_user(db_session: Session):
    """Create test user if doesn't exist."""
    stmt = select(User).where(User.id == TEST_USER_ID)
    user = db_session.exec(stmt).first()
    if not user:
        user = User(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            name="Chat Ops Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


# ============================================================================
# INTENT DETECTOR TESTS (Unit Tests)
# ============================================================================

class TestIntentDetector:
    """Test intent detection for all operations."""
    
    def test_add_task_with_title(self):
        """Test: 'add task: Buy milk' should detect add intent with title."""
        intent = detect_user_intent("add task: Buy milk", [])
        assert intent is not None
        assert intent.operation == "add"
        assert intent.params.get("title") == "Buy milk"
        assert intent.needs_confirmation == False
    
    def test_add_task_without_title(self):
        """Test: 'add task' should detect add intent without title (ask for title)."""
        intent = detect_user_intent("add task", [])
        assert intent is not None
        assert intent.operation == "add"
        assert intent.params.get("title") is None
        # Should not force execution - need to ask for title
    
    def test_create_task_with_title(self):
        """Test: 'create task: Finish homework' should detect add intent."""
        intent = detect_user_intent("create task: Finish homework", [])
        assert intent is not None
        assert intent.operation == "add"
        assert intent.params.get("title") == "Finish homework"
    
    def test_delete_task_with_id(self):
        """Test: 'delete task 5' should detect delete intent with confirmation needed."""
        intent = detect_user_intent("delete task 5", [])
        assert intent is not None
        assert intent.operation == "delete"
        assert intent.task_id == 5
        assert intent.needs_confirmation == True  # Always ask before deleting
    
    def test_delete_task_without_id(self):
        """Test: 'delete task' should ask which task (delete_ask)."""
        intent = detect_user_intent("delete task", [])
        assert intent is not None
        assert intent.operation == "delete_ask"
        assert intent.task_id is None
    
    def test_update_task_with_id_and_details(self):
        """Test: 'update task 3 title to Buy groceries' should detect update with confirmation."""
        intent = detect_user_intent("update task 3 title to Buy groceries", [])
        assert intent is not None
        assert intent.operation == "update"
        assert intent.task_id == 3
        assert intent.params.get("title").lower() == "buy groceries"  # Case-insensitive
        assert intent.needs_confirmation == True  # Always confirm updates
    
    def test_update_task_without_id(self):
        """Test: 'update task' should ask which task (update_ask)."""
        intent = detect_user_intent("update task", [])
        assert intent is not None
        assert intent.operation == "update_ask"
        assert intent.task_id is None
    
    def test_show_all_tasks(self):
        """Test: 'show all tasks' should detect list intent."""
        intent = detect_user_intent("show all tasks", [])
        assert intent is not None
        assert intent.operation == "list"
        assert intent.params.get("status") == "all"
        assert intent.needs_confirmation == False  # Execute immediately
    
    def test_show_task_list(self):
        """Test: 'show task list' should detect list intent."""
        intent = detect_user_intent("show task list", [])
        assert intent is not None
        assert intent.operation == "list"
    
    def test_complete_task_with_id(self):
        """Test: 'mark task 7 as complete' should detect complete intent."""
        intent = detect_user_intent("mark task 7 as complete", [])
        assert intent is not None
        assert intent.operation == "complete"
        assert intent.task_id == 7
        assert intent.needs_confirmation == True
    
    def test_yes_confirmation(self):
        """Test: 'yes' after confirmation should be detected."""
        # Simulate conversation history with confirmation question
        history = [
            {"role": "user", "content": "delete task 5"},
            {"role": "assistant", "content": "🗑️ Kya aap sure hain k task #5 delete karna hai?"}
        ]
        intent = detect_user_intent("yes", history)
        assert intent is not None
        assert intent.operation == "delete"
        assert intent.task_id == 5
        assert intent.needs_confirmation == False  # Already confirmed
    
    def test_no_cancellation(self):
        """Test: 'no' after confirmation should return None (handled separately)."""
        history = [
            {"role": "user", "content": "delete task 5"},
            {"role": "assistant", "content": "🗑️ Kya aap sure hain k task #5 delete karna hai?"}
        ]
        intent = detect_user_intent("no", history)
        # Should return None, chat.py handles cancellation separately
        assert intent is None

    def test_add_task_reply_add_task_not_used_as_title(self):
        """When assistant asked for title and user replies 'add task', must NOT create task titled 'add task'."""
        history = [
            {"role": "user", "content": "add task"},
            {"role": "assistant", "content": "What's the title of the task you'd like to add?"}
        ]
        intent = detect_user_intent("add task", history)
        # Must either ask again (add with no title) or reject: must NOT be add with title "add task"
        if intent is not None and intent.operation == "add":
            assert intent.params.get("title") != "add task", "Must not use 'add task' as task title"
            assert intent.params.get("title") is None or intent.params.get("title").lower() != "add task"

    def test_update_task_bare_always_ask_which_task(self):
        """'update task' with no task in message must return update_ask and never assume from context."""
        # Even with history that mentions task 72, bare "update task" must ask which task
        history = [
            {"role": "user", "content": "delete task 72"},
            {"role": "assistant", "content": "🗑️ Kya aap sure hain k task #72 delete karna hai?"},
            {"role": "user", "content": "yes"},
            {"role": "assistant", "content": "✅ I've removed task #72."}
        ]
        intent = detect_user_intent("update task", history)
        assert intent is not None
        assert intent.operation == "update_ask"
        assert intent.task_id is None
        assert intent.task_title is None

    def test_update_task_bare_no_context_assumption(self):
        """'update task' must not pull task 72 from old context when user said only 'update task'."""
        history = [
            {"role": "assistant", "content": "Task #72 mein kya update karna hai?"}
        ]
        # User says only "update task" (new request) - must ask which task, not assume 72
        intent = detect_user_intent("update task", history)
        assert intent is not None
        assert intent.operation == "update_ask"
        assert intent.task_id is None

    def test_show_all_tasks_detected_and_list_operation(self):
        """'show all tasks' and 'show task list' must be list intent and trigger list_tasks (status all)."""
        for msg in ["show all tasks", "show task list", "list my tasks"]:
            intent = detect_user_intent(msg, [])
            assert intent is not None, f"Failed for message: {msg}"
            assert intent.operation == "list", f"Wrong operation for: {msg}"
            assert intent.params.get("status") == "all"
            assert intent.needs_confirmation == False


# ============================================================================
# API ENDPOINT TESTS (Integration Tests)
# ============================================================================

class TestChatAPI:
    """Test chat API endpoints with full flow."""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, cleanup):
        """Setup before each test."""
        self.db = db_session
        self.user = create_test_user(db_session)
        yield
    
    def _send_chat_message(self, message: str, conversation_id: int = None):
        """Helper to send chat message."""
        headers = {
            "Authorization": f"Bearer test-token-{TEST_USER_ID}"
        }
        payload = {"message": message}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json=payload,
            headers=headers
        )
        return response
    
    def test_add_task_full_flow(self):
        """Test complete add task flow: ask → provide details → create."""
        # Step 1: User says "add task" (no title)
        response = self._send_chat_message("add task")
        assert response.status_code == 200
        data = response.json()
        assert "what's the title" in data["response"].lower() or "title of the task" in data["response"].lower()
        conv_id = data["conversation_id"]
        
        # Step 2: User provides title
        response = self._send_chat_message("Buy milk and eggs", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "added" in data["response"].lower() or "created" in data["response"].lower()
        
        # Verify task was created in database
        stmt = select(Task).where(
            Task.user_id == TEST_USER_ID,
            Task.title == "Buy milk and eggs"
        )
        task = self.db.exec(stmt).first()
        assert task is not None
        assert task.title == "Buy milk and eggs"
    
    def test_add_task_with_title(self):
        """Test add task with title provided initially."""
        response = self._send_chat_message("add task: Complete homework")
        assert response.status_code == 200
        data = response.json()
        assert "added" in data["response"].lower() or "created" in data["response"].lower()
        
        # Verify task created
        stmt = select(Task).where(
            Task.user_id == TEST_USER_ID,
            Task.title == "Complete homework"
        )
        task = self.db.exec(stmt).first()
        assert task is not None
    
    def test_delete_task_full_flow(self):
        """Test complete delete flow: ask which → confirm → delete."""
        # Setup: Create a task first
        task = Task(
            user_id=TEST_USER_ID,
            title="Task to delete",
            description="This will be deleted",
            priority="low",
            completed=False
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        task_id = task.id
        
        # Step 1: User says "delete task" (no ID)
        response = self._send_chat_message("delete task")
        assert response.status_code == 200
        data = response.json()
        assert "kaunsa task" in data["response"].lower() or "which task" in data["response"].lower()
        conv_id = data["conversation_id"]
        
        # Step 2: User provides task ID
        response = self._send_chat_message(f"task #{task_id}", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "sure" in data["response"].lower() or "confirm" in data["response"].lower()
        
        # Step 3: User confirms
        response = self._send_chat_message("yes", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["response"].lower() or "removed" in data["response"].lower()
        
        # Verify task was deleted
        stmt = select(Task).where(Task.id == task_id)
        deleted_task = self.db.exec(stmt).first()
        assert deleted_task is None
    
    def test_delete_task_with_cancellation(self):
        """Test delete task flow with user saying 'no' to confirmation."""
        # Setup: Create a task
        task = Task(
            user_id=TEST_USER_ID,
            title="Task to keep",
            completed=False
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        task_id = task.id
        
        # Step 1: Delete with ID
        response = self._send_chat_message(f"delete task {task_id}")
        assert response.status_code == 200
        data = response.json()
        assert "sure" in data["response"].lower()
        conv_id = data["conversation_id"]
        
        # Step 2: User says no
        response = self._send_chat_message("no", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "deletion cancelled" in data["response"].lower()
        
        # Verify task still exists
        stmt = select(Task).where(Task.id == task_id)
        kept_task = self.db.exec(stmt).first()
        assert kept_task is not None
    
    def test_update_task_full_flow(self):
        """Test complete update flow: ask which → ask what → confirm → update."""
        # Setup: Create a task
        task = Task(
            user_id=TEST_USER_ID,
            title="Original title",
            priority="low",
            completed=False
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        task_id = task.id
        
        # Step 1: User says "update task" (no ID)
        response = self._send_chat_message("update task")
        assert response.status_code == 200
        data = response.json()
        assert "kaunsa task" in data["response"].lower() or "which task" in data["response"].lower()
        conv_id = data["conversation_id"]
        
        # Step 2: User provides task ID
        response = self._send_chat_message(f"task #{task_id}", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "what would you like to update" in data["response"].lower() or "kya update" in data["response"].lower()
        
        # Step 3: User provides update details
        response = self._send_chat_message("title to Updated title, priority to high", conv_id)
        assert response.status_code == 200
        data = response.json()
        # Should show confirmation with changes
        assert "update task" in data["response"].lower() and "confirm" in data["response"].lower() or "sure" in data["response"].lower()
        
        # Step 4: User confirms
        response = self._send_chat_message("yes", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "updated" in data["response"].lower()
        
        # Verify task was updated
        self.db.expire_all()  # Force refresh from DB
        stmt = select(Task).where(Task.id == task_id)
        updated_task = self.db.exec(stmt).first()
        assert updated_task is not None
        assert updated_task.title == "Updated title"
        assert updated_task.priority == "high"
    
    def test_show_all_tasks(self):
        """Test show all tasks functionality."""
        # Setup: Create multiple tasks
        task1 = Task(user_id=TEST_USER_ID, title="Task 1", completed=False)
        task2 = Task(user_id=TEST_USER_ID, title="Task 2", completed=True)
        task3 = Task(user_id=TEST_USER_ID, title="Task 3", completed=False)
        self.db.add_all([task1, task2, task3])
        self.db.commit()
        
        # Send "show all tasks"
        response = self._send_chat_message("show all tasks")
        assert response.status_code == 200
        data = response.json()
        
        # Should list all tasks
        response_lower = data["response"].lower()
        assert "task 1" in response_lower
        assert "task 2" in response_lower
        assert "task 3" in response_lower
        
        # Check tool_calls
        assert len(data["tool_calls"]) > 0
        assert data["tool_calls"][0]["tool"] == "list_tasks"
    
    def test_show_all_tasks_empty(self):
        """Test show all tasks when no tasks exist."""
        response = self._send_chat_message("show all tasks")
        assert response.status_code == 200
        data = response.json()
        assert "don't have any tasks" in data["response"].lower() or "no tasks" in data["response"].lower()
    
    def test_complete_task_flow(self):
        """Test marking task as complete."""
        # Setup: Create a task
        task = Task(
            user_id=TEST_USER_ID,
            title="Task to complete",
            completed=False
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        task_id = task.id
        
        # Step 1: Mark as complete
        response = self._send_chat_message(f"mark task {task_id} as complete")
        assert response.status_code == 200
        data = response.json()
        assert "mark" in data["response"].lower() and "complete" in data["response"].lower()
        conv_id = data["conversation_id"]
        
        # Step 2: Confirm
        response = self._send_chat_message("yes", conv_id)
        assert response.status_code == 200
        data = response.json()
        assert "marked" in data["response"].lower() or "completed" in data["response"].lower()
        
        # Verify task is completed
        self.db.expire_all()
        stmt = select(Task).where(Task.id == task_id)
        completed_task = self.db.exec(stmt).first()
        assert completed_task is not None
        assert completed_task.completed == True


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup(self, db_session: Session, cleanup):
        """Setup before each test."""
        self.db = db_session
        self.user = create_test_user(db_session)
        yield
    
    def _send_chat_message(self, message: str, conversation_id: int = None):
        """Helper to send chat message."""
        headers = {
            "Authorization": f"Bearer test-token-{TEST_USER_ID}"
        }
        payload = {"message": message}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json=payload,
            headers=headers
        )
        return response
    
    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist."""
        response = self._send_chat_message("delete task 99999")
        assert response.status_code == 200
        data = response.json()
        # Should ask for confirmation or say task not found
        # (Depends on implementation - find_task might return None)
    
    def test_update_nonexistent_task(self):
        """Test updating a task that doesn't exist."""
        response = self._send_chat_message("update task 99999 priority to high")
        assert response.status_code == 200
        # Should handle gracefully (task not found)
    
    def test_unauthorized_access(self):
        """Test accessing another user's task."""
        # Create task for different user
        other_task = Task(
            user_id="other-user-id",
            title="Other user's task",
            completed=False
        )
        self.db.add(other_task)
        self.db.commit()
        self.db.refresh(other_task)
        
        # Try to delete it as TEST_USER_ID
        response = self._send_chat_message(f"delete task {other_task.id}")
        # Should not find the task (user isolation)
        # OR should fail gracefully


if __name__ == "__main__":
    print("🧪 Running AI Chat Assistant Tests...")
    print("=" * 80)
    print("\nTest Categories:")
    print("1. Intent Detector Tests (Unit)")
    print("2. Chat API Tests (Integration)")
    print("3. Error Handling Tests")
    print("\n" + "=" * 80)
    pytest.main([__file__, "-v", "--tb=short"])
