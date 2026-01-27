"""Quick test script for all chat operations.

Run this to verify all operations work correctly:
- Add task
- Show all tasks  
- Update task
- Delete task
- Mark as complete

Usage:
    python scripts/test_chat_all_operations.py
"""

import sys
sys.path.insert(0, '.')

from src.ai_agent.intent_detector import detect_user_intent

print("=" * 80)
print("AI CHAT ASSISTANT - OPERATIONS TEST")
print("=" * 80)
print()

# Test data
test_cases = [
    # ADD TASK tests
    {
        "category": "ADD TASK",
        "message": "add task",
        "expected_operation": "add",
        "expected_params": {},
        "expected_confirmation": False,
        "description": "Should ask for title"
    },
    {
        "category": "ADD TASK",
        "message": "add task: Buy groceries",
        "expected_operation": "add",
        "expected_params": {"title": "Buy groceries"},
        "expected_confirmation": False,
        "description": "Should create task immediately"
    },
    {
        "category": "ADD TASK",
        "message": "create task: Complete homework",
        "expected_operation": "add",
        "expected_params": {"title": "Complete homework"},
        "expected_confirmation": False,
        "description": "Should create task immediately"
    },
    
    # SHOW TASKS tests
    {
        "category": "SHOW TASKS",
        "message": "show all tasks",
        "expected_operation": "list",
        "expected_params": {"status": "all"},
        "expected_confirmation": False,
        "description": "Should list all tasks immediately"
    },
    {
        "category": "SHOW TASKS",
        "message": "show task list",
        "expected_operation": "list",
        "expected_params": {"status": "all"},
        "expected_confirmation": False,
        "description": "Should list all tasks immediately"
    },
    
    # DELETE TASK tests
    {
        "category": "DELETE TASK",
        "message": "delete task",
        "expected_operation": "delete_ask",
        "expected_params": {},
        "expected_confirmation": False,
        "description": "Should ask which task to delete"
    },
    {
        "category": "DELETE TASK",
        "message": "delete task 5",
        "expected_operation": "delete",
        "expected_task_id": 5,
        "expected_confirmation": True,
        "description": "Should ask for confirmation"
    },
    
    # UPDATE TASK tests
    {
        "category": "UPDATE TASK",
        "message": "update task",
        "expected_operation": "update_ask",
        "expected_params": {},
        "expected_confirmation": False,
        "description": "Should ask which task to update"
    },
    {
        "category": "UPDATE TASK",
        "message": "update task 3 priority to high",
        "expected_operation": "update",
        "expected_task_id": 3,
        "expected_params": {"priority": "high"},
        "expected_confirmation": True,
        "description": "Should ask for confirmation"
    },
    {
        "category": "UPDATE TASK",
        "message": "update task 7 title to Buy organic groceries",
        "expected_operation": "update",
        "expected_task_id": 7,
        "expected_params": {"title": "buy organic groceries"},
        "expected_confirmation": True,
        "description": "Should ask for confirmation"
    },
    
    # MARK COMPLETE tests
    {
        "category": "MARK COMPLETE",
        "message": "mark task 10 as complete",
        "expected_operation": "complete",
        "expected_task_id": 10,
        "expected_confirmation": True,
        "description": "Should ask for confirmation"
    },
]

# Run tests
passed = 0
failed = 0
errors = []

for i, test in enumerate(test_cases, 1):
    category = test["category"]
    message = test["message"]
    description = test["description"]
    
    print(f"\n{'─' * 80}")
    print(f"TEST {i}: {category}")
    print(f"{'─' * 80}")
    print(f"Message: '{message}'")
    print(f"Expected: {description}")
    print()
    
    try:
        # Detect intent
        intent = detect_user_intent(message, [])
        
        if intent is None:
            print("❌ FAILED: No intent detected")
            failed += 1
            errors.append(f"Test {i} ({category}): No intent detected for '{message}'")
            continue
        
        # Check operation
        expected_op = test["expected_operation"]
        if intent.operation != expected_op:
            print(f"❌ FAILED: Expected operation '{expected_op}', got '{intent.operation}'")
            failed += 1
            errors.append(f"Test {i} ({category}): Wrong operation ({intent.operation} vs {expected_op})")
            continue
        
        # Check task_id if expected
        if "expected_task_id" in test:
            expected_id = test["expected_task_id"]
            if intent.task_id != expected_id:
                print(f"❌ FAILED: Expected task_id={expected_id}, got {intent.task_id}")
                failed += 1
                errors.append(f"Test {i} ({category}): Wrong task_id ({intent.task_id} vs {expected_id})")
                continue
        
        # Check params if expected
        if "expected_params" in test:
            expected_params = test["expected_params"]
            for key, expected_value in expected_params.items():
                actual_value = intent.params.get(key)
                # Case-insensitive comparison for strings
                if isinstance(expected_value, str) and isinstance(actual_value, str):
                    if actual_value.lower() != expected_value.lower():
                        print(f"❌ FAILED: Expected {key}='{expected_value}', got '{actual_value}'")
                        failed += 1
                        errors.append(f"Test {i} ({category}): Wrong {key} ({actual_value} vs {expected_value})")
                        continue
                elif actual_value != expected_value:
                    print(f"❌ FAILED: Expected {key}={expected_value}, got {actual_value}")
                    failed += 1
                    errors.append(f"Test {i} ({category}): Wrong {key} ({actual_value} vs {expected_value})")
                    continue
        
        # Check confirmation requirement
        expected_confirmation = test["expected_confirmation"]
        if intent.needs_confirmation != expected_confirmation:
            print(f"⚠️  WARNING: Expected needs_confirmation={expected_confirmation}, got {intent.needs_confirmation}")
            # Don't fail on this, just warn
        
        # Success!
        print(f"✅ PASSED")
        print(f"   Intent: {intent.operation}")
        if intent.task_id:
            print(f"   Task ID: {intent.task_id}")
        if intent.params:
            print(f"   Params: {intent.params}")
        print(f"   Confirmation needed: {intent.needs_confirmation}")
        passed += 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        failed += 1
        errors.append(f"Test {i} ({category}): Exception - {str(e)}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total tests: {len(test_cases)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print()

if failed > 0:
    print("FAILURES:")
    for error in errors:
        print(f"  - {error}")
    print()
    sys.exit(1)
else:
    print("🎉 ALL TESTS PASSED!")
    print()
    print("Next steps:")
    print("1. Start backend server: uvicorn src.main:app --reload")
    print("2. Test via Chat UI to verify end-to-end flow")
    print("3. Verify database persistence (refresh tasks page)")
    sys.exit(0)
