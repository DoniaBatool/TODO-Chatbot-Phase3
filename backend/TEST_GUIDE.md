# AI Chat Assistant - Test Guide

## Critical Bug Fixed ✅

**Issue:** All operations (add, delete, update, show tasks) were failing with "Sorry, I encountered an error"

**Root Cause:** In `backend/src/routes/chat.py` line 438, the code was trying to access `detected_intent.needs_confirmation` when `detected_intent` was `None`, causing an `AttributeError`.

**Fix:** Moved the `if detected_intent.needs_confirmation:` check inside the `if detected_intent:` block instead of the `else:` block.

---

## How to Test

### 1. Unit Tests (Intent Detector)

These tests verify that the intent detector correctly identifies user intentions:

```bash
cd backend
source venv/bin/activate
python -m pytest tests/test_chat_operations.py::TestIntentDetector -v
```

**Expected Result:** ✅ All 12 tests should pass

### 2. Start Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --log-level debug
```

### 3. Manual Testing via Chat UI

Open the frontend and test each operation:

#### Test 1: Create/Add Task

**Flow:**
1. User: "add task"
2. Bot: "What's the title of the task you'd like to add?"
3. User: "Buy groceries for weekend"
4. Bot: "✅ I've added task #X: 'Buy groceries for weekend' to your tasks."

**With full details:**
- User: "create task: Complete homework, priority high, due date tomorrow"
- Bot: Should create task immediately

#### Test 2: Show All Tasks

**Flow:**
1. User: "show all tasks"
2. Bot: Should list all tasks with details

**Variations:**
- "show task list"
- "list my tasks"
- "display all tasks"

#### Test 3: Delete Task

**Flow:**
1. User: "delete task"
2. Bot: "🗑️ Kaunsa task delete karna hai? Here are your current tasks: [list]"
3. User: "task #5" (or just "5" or "buy groceries")
4. Bot: "🗑️ Kya aap sure hain k task #5 delete karna hai?"
5. User: "yes"
6. Bot: "✅ I've removed task #5 from your tasks."

**With ID:**
- User: "delete task 5"
- Bot: Should ask for confirmation directly

**Cancellation:**
- User: "delete task 5"
- Bot: Asks for confirmation
- User: "no"
- Bot: "❌ Deletion cancelled. No task was deleted."

#### Test 4: Update Task

**Flow:**
1. User: "update task"
2. Bot: "📝 Kaunsa task update karna hai? Here are your current tasks: [list]"
3. User: "task #3"
4. Bot: "📝 Task #3 — what would you like to update?"
5. User: "title to Buy organic groceries, priority to high"
6. Bot: Shows confirmation with changes
7. User: "yes"
8. Bot: "✅ I've updated task #3: title to 'Buy organic groceries', priority to high."

**With ID and details:**
- User: "update task 3 priority to high"
- Bot: Should show confirmation directly

**Cancellation:**
- User: "update task 3 priority to high"
- Bot: Shows confirmation
- User: "no"
- Bot: "❌ Update cancelled. No changes were made."

#### Test 5: Mark as Complete

**Flow:**
1. User: "mark task 7 as complete"
2. Bot: "✅ Task #7 ko complete mark kar doon?"
3. User: "yes"
4. Bot: "✅ I've marked task #7 as complete."

---

## Debugging Tips

### Check Backend Logs

```bash
tail -f backend/logs/app.log
```

Look for:
- "Intent detected: Intent(operation=...)"
- "Executing add_task/update_task/delete_task for user..."
- "Successfully committed task X to database"

### Check Browser Console

Open browser DevTools (F12) and check:
- Network tab: Look for failed API requests to `/api/{user_id}/chat`
- Console tab: Look for JavaScript errors

### Test Intent Detector Directly

```bash
cd backend
source venv/bin/activate
python3 -c "
from src.ai_agent.intent_detector import detect_user_intent

# Test add task
intent = detect_user_intent('add task: Buy milk', [])
print(f'Add task: {intent}')

# Test delete task
intent = detect_user_intent('delete task 5', [])
print(f'Delete task: {intent}')

# Test update task
intent = detect_user_intent('update task 3 priority to high', [])
print(f'Update task: {intent}')

# Test show tasks
intent = detect_user_intent('show all tasks', [])
print(f'Show tasks: {intent}')
"
```

---

## Expected Behavior

### All Operations Should:
1. **Always ask for clarification first** (which task?) if not specified
2. **Show confirmation** before destructive operations (delete, update)
3. **Execute MCP tools** (not just AI responses)
4. **Save to database** (verify by refreshing tasks page)
5. **Return success messages** (not generic errors)

### Confirmation Flow:
- ✅ Delete: Always confirm
- ✅ Update: Always confirm
- ✅ Complete: Always confirm
- ❌ Add: No confirmation (just ask for details if missing)
- ❌ List: No confirmation (execute immediately)

---

## Common Issues

### Issue: "Sorry, I encountered an error"

**Possible Causes:**
1. Backend server not running
2. Database connection issue
3. Invalid JWT token
4. Bug in intent detector or chat.py

**Debug Steps:**
1. Check backend logs for actual error
2. Check browser console for API error response
3. Verify database is running
4. Check JWT token in localStorage

### Issue: Operation claims success but nothing changes

**Possible Causes:**
1. MCP tool not actually executing
2. Database commit failing
3. Wrong user_id

**Debug Steps:**
1. Check backend logs for "Successfully committed task X to database"
2. Query database directly: `SELECT * FROM tasks WHERE user_id='...'`
3. Check if tool_calls are present in API response

### Issue: Intent not detected

**Possible Causes:**
1. Message doesn't match regex patterns
2. Typo in keywords

**Debug Steps:**
1. Run unit tests for intent detector
2. Test with exact phrases from test cases
3. Check intent_detector.py patterns

---

## Test Results Template

```
FEATURE: Add Task
[ ] Basic "add task" → asks for title → creates task
[ ] With title "add task: X" → creates immediately
[ ] With full details → creates with all fields
[ ] Saves to database correctly

FEATURE: Delete Task
[ ] Basic "delete task" → asks which → confirms → deletes
[ ] With ID "delete task 5" → confirms → deletes
[ ] Cancellation with "no" → shows "Deletion cancelled"
[ ] Removes from database correctly

FEATURE: Update Task
[ ] Basic "update task" → asks which → asks what → confirms → updates
[ ] With ID and details → confirms → updates
[ ] Cancellation with "no" → shows "Update cancelled"
[ ] Saves changes to database correctly

FEATURE: Show Tasks
[ ] "show all tasks" → lists all tasks immediately
[ ] Shows correct task details (title, priority, due date, status)
[ ] Empty list → shows "You don't have any tasks yet"

FEATURE: Mark Complete
[ ] "mark task X as complete" → confirms → marks complete
[ ] Updates completed status in database
```

---

## Success Criteria

✅ All unit tests pass
✅ All manual tests pass
✅ No "Sorry, I encountered an error" messages
✅ Database changes persist (refresh tasks page shows updates)
✅ Confirmation questions appear for destructive operations
✅ Cancellation works properly ("no" → operation cancelled)
✅ Backend logs show detailed execution trace

---

## Next Steps

After all tests pass:
1. Commit changes with descriptive message
2. Create PHR documenting the bug fix
3. Update CHANGELOG.md
4. Deploy to production (if applicable)
