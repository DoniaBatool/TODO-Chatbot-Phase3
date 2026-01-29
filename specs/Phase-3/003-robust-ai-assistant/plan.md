# Implementation Plan: Robust AI Chat Assistant for Todo Management

**Branch**: `001-robust-ai-assistant` | **Date**: 2026-01-27 | **Spec**: [specs/Phase-3/001-robust-ai-assistant/spec.md](../Phase-3/001-robust-ai-assistant/spec.md)
**Input**: Feature specification from `/specs/Phase-3/001-robust-ai-assistant/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an intelligent AI chat assistant that enables natural language task management through proper intent recognition, multi-turn conversation workflows, and context maintenance. The assistant must correctly identify user commands (add/update/delete/list tasks), guide users through conversational flows to collect task information, maintain context across turns, and integrate with existing MCP tools. This addresses critical bugs in the current implementation where commands are treated as task titles and conversation state is poorly managed.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 14 (frontend)
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK, FastAPI, SQLModel, OpenAI ChatKit, dateparser/python-dateutil (natural date parsing), rapidfuzz (fuzzy task matching)
**Storage**: PostgreSQL (Neon) for conversations, messages, tasks (database-centric state management)
**Testing**: pytest with TDD approach (write tests first), 50+ edge case scenarios, 95%+ coverage target
**Target Platform**: Web application (backend server + frontend SPA)
**Project Type**: Web (backend FastAPI + frontend Next.js)
**Performance Goals**: <5s response time for 95% of AI chat requests, handle concurrent users with connection pooling
**Constraints**: Stateless agent design (no server-side session memory), JWT authentication, user isolation at query level, max 50 recent messages per conversation context
**Scale/Scope**: Single-user conversations, 6 MCP tools (add/list/update/delete/complete/find tasks), 8 user stories with 38 acceptance scenarios, 18 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **PASS - All Gates Satisfied**

### Code Quality & Architecture Gates

1. **Stateless Architecture** (Constitution Section: Backend Principles)
   - ✅ **PASS**: Spec requires stateless agent design (FR-015), database-centric state, no server-side session storage
   - Evidence: "Each chat request loads conversation history from database, agent has no persistent memory" (Assumption 6)

2. **User Isolation** (Constitution: Security)
   - ✅ **PASS**: Spec enforces user_id filtering at all levels (FR-014)
   - Evidence: "System MUST inject user_id into all MCP tool calls" (FR-014), "Single-user context enforced by user_id filtering at database query level" (Assumption 9)

3. **MCP-First Design** (Constitution: AI Integration)
   - ✅ **PASS**: Spec mandates MCP tools only (FR-007)
   - Evidence: "System MUST call the appropriate MCP tool after user confirms actions (never just respond 'Done!' without tool call)" (FR-007)

4. **Test-Driven Development** (Constitution: Phase III Requirements)
   - ✅ **PASS**: Spec explicitly requires TDD approach with tests written first
   - Evidence: "Comprehensive test suite will be written before implementation (TDD approach)" (Assumption 14), 50+ edge case scenarios defined

5. **Database-Centric State** (Constitution: Backend Architecture)
   - ✅ **PASS**: All conversation state persists to PostgreSQL (FR-015)
   - Evidence: "System MUST persist all conversations and messages to database" (FR-015)

6. **Security by Default** (Constitution: Security)
   - ✅ **PASS**: JWT authentication, user isolation, input validation enforced
   - Evidence: "JWT authentication handled by existing middleware" (Assumption 4), "System MUST validate all extracted data before tool calls" (FR-017)

### Skill-Based Development Gates

7. **Skill Discovery Protocol** (Constitution: Phase III Enforcement)
   - ✅ **PASS**: Will create `/sp.robust-ai-assistant` skill in `.claude/skills/` as mandated
   - Evidence: User requested "create a skill that builds a robust AI Chat Assistant" and "add to constitution.md that this skill must be religiously used"

8. **Reusable Intelligence** (Constitution: Agent Factory)
   - ✅ **PASS**: Will leverage existing skills (/backend-developer, /database-engineer, /qa-engineer, /uiux-designer)
   - Evidence: Spec mentions "UI/UX designer skill exists" (Assumption 12), requires integration with existing MCP tools

### Complexity Limits

9. **No Premature Abstraction** (Constitution: Code Quality)
   - ✅ **PASS**: Spec focuses on solving current problems (intent recognition, conversation flow), not over-engineering
   - Evidence: Out of scope explicitly excludes unnecessary features (voice I/O, multi-user collaboration, recurring tasks, etc.)

10. **Smallest Viable Diff** (Constitution: Development Practice)
    - ✅ **PASS**: Spec builds on existing MCP tools, database schema, authentication - minimal new infrastructure
    - Evidence: "MCP tools already exist" (Assumption 3), "JWT authentication handled by existing middleware" (Assumption 4)

### No Violations - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/Phase-3/003-robust-ai-assistant/
├── spec.md              # Feature specification (✅ complete)
├── plan.md              # This file (/sp.plan command output - ✅ complete)
├── research.md          # Phase 0 output (✅ complete)
├── data-model.md        # Phase 1 output (✅ complete)
├── quickstart.md        # Phase 1 output (✅ complete)
├── contracts/           # Phase 1 output (✅ complete)
│   ├── mcp-tools.md     # MCP tool contracts
│   └── api-endpoints.md # HTTP API contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - ⏳ pending)
```

### Source Code (repository root)

**Web Application Structure** (backend + frontend):

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py      # Conversation model (existing)
│   │   └── message.py           # Message model (existing)
│   ├── services/
│   │   ├── conversation_service.py  # Conversation CRUD (existing)
│   │   └── intent_classifier.py     # NEW: Intent recognition logic
│   ├── ai_agent/
│   │   ├── agent.py             # Agent config + system prompt (UPDATE)
│   │   ├── runner.py            # Agent execution (UPDATE)
│   │   └── context_manager.py   # NEW: Conversation context tracking
│   ├── mcp_tools/
│   │   ├── add_task.py          # Existing MCP tool
│   │   ├── list_tasks.py        # Existing MCP tool
│   │   ├── update_task.py       # Existing MCP tool
│   │   ├── delete_task.py       # Existing MCP tool
│   │   ├── complete_task.py     # Existing MCP tool
│   │   └── find_task.py         # Existing MCP tool
│   ├── routes/
│   │   └── chat.py              # Chat endpoint (UPDATE for improved flow)
│   └── utils/
│       ├── date_parser.py       # NEW: Natural language date parsing
│       └── fuzzy_matcher.py     # NEW: Task title fuzzy matching
└── tests/
    ├── unit/
    │   ├── test_intent_classifier.py  # NEW: Intent recognition tests
    │   ├── test_date_parser.py        # NEW: Date parsing tests
    │   └── test_context_manager.py    # NEW: Context tracking tests
    ├── integration/
    │   ├── test_chat_workflows.py     # NEW: Multi-turn conversation tests
    │   └── test_mcp_integration.py    # NEW: Tool calling tests
    └── edge_cases/
        └── test_50_edge_scenarios.py  # NEW: 50+ edge case tests

frontend/
├── src/
│   ├── components/
│   │   └── chat/
│   │       └── TaskDisplay.tsx  # UPDATE: Rich task formatting UI
│   └── app/
│       └── chat/
│           └── page.tsx         # Chat interface (existing, may need updates)
└── tests/
    └── components/
        └── TaskDisplay.test.tsx # NEW: UI component tests

.claude/
└── skills/
    └── robust-ai-assistant/     # NEW: Skill to be created
        ├── SKILL.md             # Skill documentation
        ├── examples/            # Example conversations
        │   ├── add-task-flow.md
        │   ├── update-task-flow.md
        │   └── delete-task-flow.md
        └── tests/               # Skill-specific test scenarios
            └── intent-tests.yaml
```

**Structure Decision**: Web application structure (Option 2) selected because this project has both FastAPI backend (for AI agent, MCP tools, API endpoints) and Next.js frontend (for ChatKit UI). The existing codebase already follows this pattern. Changes will primarily focus on backend AI agent logic (`backend/src/ai_agent/`), new utility modules for date parsing and fuzzy matching (`backend/src/utils/`), and comprehensive test suites (`backend/tests/`). Frontend updates are minimal (improved task display component).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All constitution gates pass. Proceeding with implementation.

---

## Agent Context Summary

**Planning Status**: ✅ **COMPLETE** (Phase 0 + Phase 1 Done)

### Key Technical Decisions (from research.md)

1. **Intent Classification**: Hybrid approach - database state tracking + GPT-4o tool calling
2. **Date Parsing**: dateparser library (primary) with GPT-4o fallback for ambiguity
3. **Fuzzy Matching**: rapidfuzz (10-20x faster than fuzzywuzzy)
4. **State Management**: Database-centric (add fields to Conversation model)
5. **System Prompt**: Restructured with explicit sections and priority rules

### Database Changes (from data-model.md)

**Conversation Model - 3 New Fields**:
- `current_intent`: VARCHAR (tracks operation state: NEUTRAL, ADDING_TASK, etc.)
- `state_data`: JSON (stores collected task information across turns)
- `target_task_id`: INTEGER (task being updated/deleted)

**Migration**: Alembic migration ready, backward compatible

### MCP Tool Contracts (from contracts/mcp-tools.md)

**6 Tools with Full Contracts**:
- `add_task`, `list_tasks`, `update_task`, `delete_task`, `complete_task`, `find_task`
- Each tool: Input schema, output schema, user isolation, error handling
- Fuzzy matching: confidence thresholds (70% single, 60% multiple)

### API Contracts (from contracts/api-endpoints.md)

**4 Endpoints**:
- `POST /api/chat` - Main chat endpoint with state tracking
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation details
- `DELETE /api/chat/conversations/{id}` - Delete conversation

### Implementation Guidance (from quickstart.md)

**New Dependencies**:
- `dateparser==1.2.0`
- `rapidfuzz==3.6.0`
- `pytest-mock==3.12.0`

**Testing Strategy**: TDD approach with 95%+ coverage target

**Files to Create/Update**:
- **NEW**: `backend/src/services/intent_classifier.py`
- **NEW**: `backend/src/ai_agent/context_manager.py`
- **NEW**: `backend/src/utils/date_parser.py`
- **NEW**: `backend/src/utils/fuzzy_matcher.py`
- **UPDATE**: `backend/src/ai_agent/agent.py` (restructure system prompt)
- **UPDATE**: `backend/src/ai_agent/runner.py` (add state management)
- **UPDATE**: `backend/src/routes/chat.py` (improved flow)

**Test Files to Create**:
- `backend/tests/unit/test_intent_classifier.py`
- `backend/tests/unit/test_date_parser.py`
- `backend/tests/unit/test_fuzzy_matcher.py`
- `backend/tests/unit/test_context_manager.py`
- `backend/tests/integration/test_chat_workflows.py`
- `backend/tests/contract/test_mcp_tool_contracts.py`
- `backend/tests/contract/test_api_contracts.py`
- `backend/tests/edge_cases/test_50_scenarios.py`

### Success Criteria Targets (from spec.md)

**14 Measurable Outcomes**:
- SC-001: 95%+ intent classification accuracy
- SC-002: Zero command-as-title errors
- SC-004: 90%+ natural date parsing success
- SC-010: 95%+ tool call execution success
- SC-013: <2min full session completion

### Next Phase

**Ready for Phase 2**: Run `/sp.tasks` to generate implementation task breakdown

**Skill Creation**: After tasks complete, create `.claude/skills/robust-ai-assistant/` with:
- `SKILL.md` - Usage documentation
- `examples/` - Conversation flow examples
- `tests/` - Skill-specific test scenarios

**Constitution Update**: Add mandate to use this skill for all AI assistant work
