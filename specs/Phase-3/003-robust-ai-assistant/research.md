# Phase 0: Research - Robust AI Chat Assistant

**Feature**: 001-robust-ai-assistant
**Phase**: 0 (Research & Technical Clarification)
**Date**: 2026-01-27
**Purpose**: Resolve all technical uncertainties before detailed design

---

## Research Questions

### 1. Intent Classification Approach

**Question**: What approach should we use for intent classification (ADD_TASK, UPDATE_TASK, DELETE_TASK, etc.)?

**Options Evaluated**:
- **Option A**: Rely solely on GPT-4o natural language understanding (system prompt engineering)
- **Option B**: Implement explicit pattern matching + GPT-4o fallback
- **Option C**: Use OpenAI Agents SDK's built-in tool selection as intent classifier

**Research Findings**:

Current implementation uses **Option A** (system prompt only) in `backend/src/ai_agent/agent.py`:
```python
SYSTEM_PROMPT = """You are an intelligent, world-class task management assistant...
CONVERSATIONAL APPROACH:
When a user mentions they want to add a task, follow this interactive flow:
1. FIRST: Acknowledge their request and ask for confirmation
2. THEN: Ask about priority (high, medium, or low)
...
"""
```

**Problems with current approach**:
- Intent recognition is implicit in prompt → inconsistent results
- No explicit state tracking → "delete task" treated as task title
- GPT-4o decides intent on-the-fly → high variability

**Recommended Solution**: **Hybrid approach (Option B + C)**
1. Use OpenAI Agents SDK tool descriptions as primary intent signals
2. Add explicit pre-processing layer for command detection patterns
3. Maintain conversation state in database with explicit `intent` and `state` fields
4. GPT-4o focuses on entity extraction (title, priority, date) rather than intent classification

**Implementation Path**:
- Add `ConversationState` enum: NEUTRAL, ADDING_TASK, UPDATING_TASK, DELETING_TASK, etc.
- Add `current_intent` field to Conversation model
- Pre-process user messages for command keywords before passing to GPT-4o
- Use MCP tool calls as confirmation of intent (when GPT calls `add_task`, intent is confirmed as ADD_TASK)

---

### 2. Natural Language Date Parsing Library

**Question**: Which library should handle natural language date parsing ("tomorrow", "next Friday", "in 3 days")?

**Options Evaluated**:
- **Option A**: `dateparser` - comprehensive, supports many languages
- **Option B**: `python-dateutil` - lightweight, standard library adjacent
- **Option C**: GPT-4o via prompt engineering
- **Option D**: Custom regex patterns

**Research Findings**:

**dateparser** pros:
- Handles "tomorrow", "next Friday", "in 3 days", "Jan 20 at 2pm"
- Multi-language support (English + Urdu if needed)
- Active maintenance, 7k+ stars on GitHub

**dateparser** cons:
- Heavier dependency (~2MB)
- Slower parsing (~50-100ms per parse)

**python-dateutil** pros:
- Lightweight (~500KB)
- Fast parsing (~5-10ms)
- Part of standard Python ecosystem

**python-dateutil** cons:
- Limited natural language support (only relative deltas like "3 days")
- Doesn't handle "tomorrow", "next Friday" natively

**GPT-4o** pros:
- Already integrated, no new dependency
- Can handle ambiguous cases ("Friday" → ask user "this Friday or next Friday?")

**GPT-4o** cons:
- Adds latency (200-500ms API call)
- Non-deterministic results
- Costs per request

**Recommended Solution**: **dateparser (Option A)** for primary parsing, GPT-4o for ambiguous cases
- Use `dateparser` for 90% of common cases (fast, deterministic)
- Fall back to GPT-4o when dateparser returns low confidence or ambiguous result
- Add date validation layer (reject past dates, dates >10 years future)

**Implementation Path**:
- Add `dateparser` to `requirements.txt`
- Create `backend/src/utils/date_parser.py` with `parse_natural_date(text: str) -> datetime | None`
- Configure dateparser settings: `PREFER_DATES_FROM='future'`, `TIMEZONE='UTC'`
- Handle edge cases: "yesterday" → ask "did you mean today?", "Friday" without context → ask "this Friday or next Friday?"

---

### 3. Fuzzy Task Matching Strategy

**Question**: How should we implement fuzzy task matching for "the milk task" → task with title "buy milk from store"?

**Options Evaluated**:
- **Option A**: `fuzzywuzzy` (Levenshtein distance)
- **Option B**: `rapidfuzz` (faster, C++ implementation of fuzzywuzzy)
- **Option C**: `thefuzz` (maintained fork of fuzzywuzzy)
- **Option D**: PostgreSQL full-text search (`to_tsvector`, `ts_rank`)

**Research Findings**:

**rapidfuzz** (recommended):
- 10-20x faster than fuzzywuzzy (C++ vs pure Python)
- Same API as fuzzywuzzy (drop-in replacement)
- Active maintenance, 3k+ stars
- Handles typos, partial matches, case-insensitive

**PostgreSQL full-text search**:
- Good for keyword search, not fuzzy matching
- Requires GIN index, migrations
- Less flexible for natural language queries

**Recommended Solution**: **rapidfuzz (Option B)**
- Use `rapidfuzz.process.extractOne()` to find best match
- Set confidence threshold: 70% for single match, 60% for multiple match confirmation
- Limit search to user's own tasks (user_id filter)

**Implementation Path**:
- Add `rapidfuzz` to `requirements.txt`
- Create `backend/src/utils/fuzzy_matcher.py`:
  - `find_best_task_match(search_query: str, tasks: List[Task]) -> (Task, confidence_score)`
  - Return None if confidence < 60%
  - Return list of candidates if multiple tasks > 60%
- Integrate into MCP `find_task` tool
- Handle ambiguous matches: "I found 2 tasks: 1) Buy milk (85%), 2) Milk delivery (78%). Which one?"

---

### 4. Conversation State Management

**Question**: How should we track multi-turn conversation state (current operation, collected fields, task being edited)?

**Options Evaluated**:
- **Option A**: Store state in GPT conversation history only
- **Option B**: Add state fields to database Conversation model
- **Option C**: Use Redis for session state (separate from DB)
- **Option D**: Hybrid: critical state in DB, temporary context in message history

**Research Findings**:

Current approach uses **Option A** (conversation history only):
- State is implicit in message history
- No explicit tracking of "we're in the middle of adding a task"
- Context lost if history is truncated

**Problems**:
- When history limited to 50 messages, early context lost
- No way to query "show me all conversations currently adding a task"
- Difficult to implement cancellation ("never mind, stop adding this task")

**Recommended Solution**: **Option B** (database-centric state)
- Add to Conversation model:
  - `current_intent`: Enum (NEUTRAL, ADDING_TASK, UPDATING_TASK, etc.)
  - `state_data`: JSON field for collected information (e.g., `{"title": "buy milk", "priority": null, "due_date": null}`)
  - `target_task_id`: ID of task being updated/deleted (null for add operations)
- Update state on each turn
- Clear state on completion or cancellation

**Implementation Path**:
- Create Alembic migration to add fields to Conversation model
- Update `backend/src/services/conversation_service.py` with state management methods
- Create `backend/src/ai_agent/context_manager.py` to handle state transitions
- Modify chat endpoint to load/save state on each request

---

### 5. System Prompt Structure

**Question**: How should we restructure the system prompt to ensure proper intent recognition and conversation flow?

**Current System Prompt Issues** (from `backend/src/ai_agent/agent.py`):
- 555 lines, very detailed but lacks structure
- Intent recognition instructions buried in prose
- No clear separation between: intent classification rules, entity extraction, conversation flow, output formatting

**Recommended Solution**: **Structured prompt with explicit sections**

```markdown
# Role
You are a task management assistant.

# Core Rules (Priority Order)
1. INTENT DETECTION: Classify every message as one intent: ADD_TASK, UPDATE_TASK, DELETE_TASK, COMPLETE_TASK, LIST_TASKS, CANCEL, PROVIDE_INFO
2. NEVER treat commands ("delete task", "update task") as task titles
3. ALWAYS confirm before destructive operations (delete, update)
4. ALWAYS call MCP tools - never just say "Done!" without tool call

# Intent Detection Patterns
ADD_TASK: "add task", "create task", "new task", "want to", "need to", "remind me to"
UPDATE_TASK: "update task", "change task", "modify task", "edit task"
DELETE_TASK: "delete task", "remove task", "cancel task"
COMPLETE_TASK: "mark done", "complete", "finished"
LIST_TASKS: "show tasks", "list tasks", "my tasks"
CANCEL: "never mind", "cancel", "stop"
PROVIDE_INFO: when user answering your question (priority, deadline, etc.)

# Conversation State Awareness
You have access to conversation state in database:
- current_intent: what operation user initiated
- state_data: information collected so far
- target_task_id: task being updated/deleted

Use this to avoid asking redundant questions.

# Multi-Turn Workflows
ADD_TASK:
1. Confirm task title
2. Ask priority (detect keywords: urgent→high, someday→low)
3. Ask deadline (parse: "tomorrow", "next Friday")
4. Ask description (optional)
5. Call add_task MCP tool

UPDATE_TASK:
1. Identify task (by ID or fuzzy match by name)
2. Show current task details
3. Ask what to update (if not already specified)
4. Ask new value
5. Confirm changes
6. Call update_task MCP tool

DELETE_TASK:
1. Identify task (by ID or fuzzy match)
2. Show task details
3. Ask "Are you sure?"
4. On yes: call delete_task
5. On no: "Task is safe"

# Entity Extraction
- Title: 1-200 chars, cannot be empty
- Priority: high/medium/low (detect keywords)
- Due date: use dateparser, validate not past
- Description: max 1000 chars

# Output Format
- Use emojis for priority: 🔴 high, 🟡 medium, 🟢 low
- Use emojis for status: ✅ complete, ⏳ pending
- Format dates: "tomorrow", "in 3 days", "overdue by 2 days"
- Be conversational, friendly, mix English/Urdu for confirmations
```

**Implementation Path**:
- Rewrite `SYSTEM_PROMPT` in `backend/src/ai_agent/agent.py`
- Add examples for each intent type
- Include instructions on reading conversation state from database
- Add explicit error handling instructions

---

### 6. Testing Strategy

**Question**: How should we structure the test suite to achieve comprehensive coverage?

**Recommended Test Structure**:

```
backend/tests/
├── unit/
│   ├── test_intent_classifier.py       # Intent detection accuracy
│   ├── test_date_parser.py             # Natural language date parsing
│   ├── test_fuzzy_matcher.py           # Task matching accuracy
│   └── test_context_manager.py         # State transition logic
├── integration/
│   ├── test_add_task_workflow.py       # Multi-turn add task flow
│   ├── test_update_task_workflow.py    # Multi-turn update flow
│   ├── test_delete_task_workflow.py    # Deletion with confirmation
│   ├── test_list_tasks.py              # Task display formatting
│   └── test_mcp_tool_calls.py          # Verify tools actually called
└── edge_cases/
    └── test_50_scenarios.py            # All edge cases from spec
```

**Test-Driven Development Approach**:
1. Write tests FIRST (before implementation)
2. Tests should FAIL initially (red)
3. Implement minimum code to pass tests (green)
4. Refactor while keeping tests passing (refactor)

**Edge Case Test Examples**:
- User says "delete task" while adding a task → should switch intent
- User says "milk" as task title → should ask for confirmation
- find_task returns 3 matches with similar scores → should list all and ask user to choose
- User provides "yesterday" as deadline → should ask for clarification
- User says "low priority urgent task" → should ask which priority to use
- MCP tool fails with database error → should show user-friendly error
- Conversation has 100 messages → should only load recent 50 into context

**Success Criteria Tests** (from spec):
- SC-001: Test intent classification accuracy across 100 test messages, expect 95%+ correct
- SC-002: Test 100 conversations, verify 0 instances of commands treated as titles
- SC-004: Test 50 date expressions, expect 90%+ correctly parsed
- SC-010: Test 100 confirmed operations, verify 95%+ result in actual tool calls

**Implementation Path**:
- Create test file structure
- Write tests for all 14 success criteria
- Write tests for all 10 edge cases from spec
- Add 40+ more edge case tests for comprehensive coverage
- Use pytest fixtures for test data (users, tasks, conversations)
- Use pytest-mock for MCP tool mocking

---

## Technical Decisions Summary

| Decision Point | Selected Approach | Rationale |
|---------------|-------------------|-----------|
| Intent Classification | Hybrid: explicit state + GPT-4o tool calling | Combines reliability of state tracking with flexibility of LLM |
| Date Parsing | dateparser library with GPT-4o fallback | Fast, deterministic for common cases; LLM handles ambiguity |
| Fuzzy Matching | rapidfuzz (C++ implementation) | 10-20x faster than alternatives, same API as fuzzywuzzy |
| State Management | Database fields (current_intent, state_data) | Stateless agent design, enables horizontal scaling |
| System Prompt | Structured sections with explicit rules | Clear priority order, easier to maintain and debug |
| Testing Approach | TDD with unit/integration/edge case layers | Write tests first, comprehensive coverage (95%+) |

---

## Dependencies Confirmed

**New Dependencies to Add**:
- `dateparser==1.2.0` - Natural language date parsing
- `rapidfuzz==3.6.0` - Fast fuzzy string matching
- `pytest-mock==3.12.0` - Mocking framework for tests (if not already present)

**Existing Dependencies (Verified)**:
- `openai` - OpenAI Agents SDK already installed
- `fastapi` - Backend framework
- `sqlmodel` - Database ORM
- `pytest` - Testing framework

**No Conflicts**: All new dependencies are compatible with existing stack.

---

## Migration Requirements

**Database Schema Changes** (Alembic migration needed):

```python
# Migration: Add conversation state fields
class Conversation(SQLModel, table=True):
    # ... existing fields ...
    current_intent: Optional[str] = Field(default="NEUTRAL")  # NEW
    state_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # NEW
    target_task_id: Optional[int] = Field(default=None)  # NEW
```

**Migration Safety**:
- All new fields are nullable/have defaults → backward compatible
- No data migration needed for existing conversations
- Existing conversations default to `current_intent="NEUTRAL"`

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| GPT-4o API rate limits during peak usage | Medium | High | Implement exponential backoff, request queuing |
| dateparser fails on ambiguous dates | Medium | Low | Fallback to GPT-4o, ask user for clarification |
| Fuzzy matching false positives | Medium | Medium | Set confidence threshold to 70%, confirm before destructive ops |
| State data grows too large (JSON field) | Low | Medium | Limit state_data to 5KB, clear on operation completion |
| Migration breaks existing conversations | Low | High | Test migration on staging, add rollback script |

---

## Next Steps (Phase 1)

**Ready to proceed to Phase 1**: All technical clarifications resolved.

**Phase 1 Deliverables**:
1. `data-model.md` - Database schema changes, entity relationships
2. `contracts/` - MCP tool contracts, API endpoint contracts
3. `quickstart.md` - Developer setup instructions
4. Update agent context with research findings

**No blockers identified.** All research questions answered with concrete technical decisions.
