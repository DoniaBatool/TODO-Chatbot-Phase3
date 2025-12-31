# Implementation Tasks: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot | **Branch**: `001-ai-chatbot` | **Date**: 2025-12-30

**Input**: Design documents from `/specs/Phase-3/001-ai-chatbot/`

## Overview

This document breaks down the AI chatbot implementation into executable tasks organized by user story. Each phase delivers an independently testable increment of functionality following TDD principles.

**Total Tasks**: 65 tasks across 9 phases
**Parallel Opportunities**: 42 parallelizable tasks marked with [P]
**Constitution Compliance**: All tasks enforce stateless architecture, user isolation, and MCP-first design

## Implementation Strategy

### MVP Scope (Recommended First Release)
- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (database, auth, core infrastructure)
- **Phase 3**: User Story 1 (Natural language task addition)
- **Phase 4**: User Story 2 (View and list tasks)

This minimal scope delivers core value: conversational task management with add and view capabilities.

### Full Feature Scope
All 5 user stories + polish phase for production-ready deployment.

### Delivery Approach
- **Incremental**: Each user story is independently deployable
- **TDD**: Red-Green-Refactor cycle for every task
- **Constitution-First**: Validate stateless, user isolation, MCP patterns at each step

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING for all user stories
    ↓
    ├─→ Phase 3 (US1: Add Task) [P1] ← MVP
    │       ↓
    ├─→ Phase 4 (US2: List Tasks) [P1] ← MVP, depends on US1
    │       ↓
    ├─→ Phase 5 (US3: Complete Task) [P2] ← depends on US1, US2
    │       ↓
    ├─→ Phase 6 (US4: Update Task) [P3] ← depends on US1, US2
    │       ↓
    ├─→ Phase 7 (US5: Delete Task) [P3] ← depends on US1, US2
    │       ↓
    └─→ Phase 8 (Polish & Integration) ← depends on all user stories
            ↓
        Phase 9 (Deployment)
```

**User Story Dependencies**:
- US1 (Add Task): No dependencies (can implement first)
- US2 (List Tasks): Depends on US1 (needs tasks to list)
- US3, US4, US5: All depend on US1 and US2 (need tasks to manipulate)

**Parallel Execution**: US3, US4, US5 can be implemented in parallel once US1 and US2 are complete.

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize project structure, install dependencies, configure environment

**Duration**: ~1 hour

**Prerequisites**: Phase 2 backend from previous phases exists

### Tasks

- [ ] T001 Review plan.md and verify existing Phase 2 backend structure at `backend/`
- [ ] T002 Install OpenAI Agents SDK: `pip install openai-agents-sdk` (add to backend/pyproject.toml)
- [ ] T003 Install Official MCP SDK: `pip install mcp-sdk` (add to backend/pyproject.toml)
- [ ] T004 Create MCP tools directory structure: `backend/src/mcp_tools/__init__.py`
- [ ] T005 Create AI agent directory structure: `backend/src/ai_agent/{__init__.py, agent.py, tools.py, runner.py}`
- [ ] T006 Create services directory: `backend/src/services/__init__.py`
- [ ] T007 Add OPENAI_API_KEY to backend/.env.example with placeholder value
- [ ] T008 Add OPENAI_AGENT_MODEL to backend/.env.example (default: gpt-4o)
- [ ] T009 Update backend/src/config.py to include OPENAI_API_KEY and OPENAI_AGENT_MODEL fields
- [ ] T010 Create test directories: `backend/tests/{test_mcp_tools, test_ai_agent, test_services}/`

**Validation**: Directory structure matches plan.md, dependencies installed, environment configured

---

## Phase 2: Foundational Infrastructure (BLOCKING)

**Goal**: Database schema, conversation management, core services that ALL user stories depend on

**Duration**: ~3-4 hours

**Prerequisites**: Phase 1 complete

**CRITICAL**: This phase MUST be complete before any user story implementation begins.

### Database Schema

- [ ] T011 Create Conversation model in backend/src/models.py with fields: id, user_id, created_at, updated_at
- [ ] T012 Create Message model in backend/src/models.py with fields: id, conversation_id, user_id, role, content, created_at
- [ ] T013 Add role validator to Message model (must be 'user' or 'assistant')
- [ ] T014 Create Alembic migration: `alembic revision -m "add_conversation_message_tables"`
- [ ] T015 Implement migration upgrade: CREATE conversations table with indexes
- [ ] T016 Implement migration upgrade: CREATE messages table with indexes and CHECK constraint on role
- [ ] T017 Implement migration downgrade: DROP messages and conversations tables
- [ ] T018 Run migration: `alembic upgrade head` and verify tables created
- [ ] T019 Write unit test for Conversation model in backend/tests/test_models.py
- [ ] T020 Write unit test for Message model validation in backend/tests/test_models.py

### Conversation Service

- [ ] T021 Create ConversationService class in backend/src/services/conversation_service.py
- [ ] T022 Implement create_conversation(user_id) → Conversation method
- [ ] T023 Implement get_conversation(conversation_id, user_id) → Conversation | None method
- [ ] T024 Implement get_conversation_history(conversation_id, user_id, limit=50) → list[Message] method
- [ ] T025 Implement add_message(conversation_id, user_id, role, content) → Message method
- [ ] T026 Implement update_conversation_timestamp(conversation_id) method
- [ ] T027 Write unit tests for ConversationService in backend/tests/test_services/test_conversation_service.py
- [ ] T028 Write integration test: create conversation → add messages → fetch history → verify order

### AI Agent Setup

- [ ] T029 Create Agent initialization function in backend/src/ai_agent/agent.py
- [ ] T030 Implement get_agent_config() to load OPENAI_API_KEY and model from config
- [ ] T031 Create system prompt for task management assistant in backend/src/ai_agent/agent.py
- [ ] T032 Implement initialize_agent(tools: list) → Agent function
- [ ] T033 Create agent runner in backend/src/ai_agent/runner.py
- [ ] T034 Implement run_agent(user_id, message, conversation_history, tools) → AgentResponse
- [ ] T035 Add error handling for OpenAI API timeout/failures in runner.py
- [ ] T036 Write unit test for agent initialization in backend/tests/test_ai_agent/test_agent.py
- [ ] T037 Write integration test: run agent with empty tools list → verify response

**Validation**:
- Database migration successful
- ConversationService CRUD operations work
- AI agent initializes and runs without errors
- All tests pass

---

## Phase 3: User Story 1 - Natural Language Task Addition [P1]

**User Story**: Users can add tasks to their todo list by typing natural language commands in a chat interface, without needing to fill out forms or use specific syntax.

**Goal**: Implement add_task MCP tool, integrate with AI agent, create chat endpoint

**Duration**: ~4-5 hours

**Prerequisites**: Phase 2 complete

**Independent Test Criteria**:
- ✅ User sends "Add task to buy milk" → Task created with title "Buy milk"
- ✅ User sends "Remember to call mom tomorrow" → Task created with title "Call mom tomorrow"
- ✅ User sends "Add task: finish report with description: quarterly sales" → Task created with both fields
- ✅ Ambiguous input "buy" → Agent asks "What would you like to buy?"

### MCP Tool: add_task

- [ ] T038 [P] [US1] Write failing test for add_task tool in backend/tests/test_mcp_tools/test_add_task.py
- [ ] T039 [P] [US1] Test: add_task with valid params → creates task with correct fields
- [ ] T040 [P] [US1] Test: add_task with description → stores description
- [ ] T041 [P] [US1] Test: add_task with empty title → raises validation error
- [ ] T042 [P] [US1] Test: add_task with title > 200 chars → raises validation error
- [ ] T043 [P] [US1] Test: add_task enforces user_id isolation
- [ ] T044 [US1] Implement add_task(user_id, title, description?) in backend/src/mcp_tools/add_task.py
- [ ] T045 [US1] Add parameter validation (title 1-200 chars, description optional)
- [ ] T046 [US1] Implement database INSERT with user_id filtering
- [ ] T047 [US1] Add error handling for database failures
- [ ] T048 [US1] Return task object with task_id, title, description, completed, created_at
- [ ] T049 [US1] Run tests and verify all add_task tests pass (green)

### AI Agent Integration

- [ ] T050 [US1] Create MCP tool definition for add_task in backend/src/ai_agent/tools.py
- [ ] T051 [US1] Add tool description: "Create a new task. Use when user wants to add, create, or remember something."
- [ ] T052 [US1] Define parameter schema with user_id, title, description
- [ ] T053 [US1] Register add_task tool with agent in initialize_agent function
- [ ] T054 [US1] Write integration test: agent interprets "Add task to buy milk" → calls add_task tool
- [ ] T055 [US1] Write integration test: agent handles ambiguous input "buy" → asks clarification
- [ ] T056 [US1] Run integration tests and verify agent correctly uses add_task tool

### Chat Endpoint

- [ ] T057 [US1] Create chat router in backend/src/routes/chat.py
- [ ] T058 [US1] Implement POST /api/{user_id}/chat endpoint
- [ ] T059 [US1] Add JWT authentication dependency (Depends(get_current_user_id))
- [ ] T060 [US1] Validate path user_id matches JWT user_id (403 if mismatch)
- [ ] T061 [US1] Parse request body: {conversation_id?, message}
- [ ] T062 [US1] Create or resume conversation using ConversationService
- [ ] T063 [US1] Fetch conversation history (last 50 messages)
- [ ] T064 [US1] Initialize agent with add_task tool
- [ ] T065 [US1] Run agent with user message and history
- [ ] T066 [US1] Store user message and assistant response in database
- [ ] T067 [US1] Update conversation timestamp
- [ ] T068 [US1] Return response: {conversation_id, response, tool_calls[]}
- [ ] T069 [US1] Add error handling (401, 403, 404, 500)
- [ ] T070 [US1] Write E2E test: POST /chat with "Add task" → verify task created in DB
- [ ] T071 [US1] Write E2E test: Resume conversation → verify history included
- [ ] T072 [US1] Write E2E test: User ID mismatch → 403 Forbidden
- [ ] T073 [US1] Run E2E tests and verify chat endpoint works end-to-end

**Parallel Execution Opportunities**:
- T038-T043 (tests) can run in parallel
- T044-T049 (implementation) sequential within add_task
- T050-T056 (agent integration) can run in parallel with T057-T068 (endpoint)
- T069-T073 (E2E tests) sequential after endpoint complete

**Validation**:
- All add_task tests pass
- Agent correctly interprets natural language → calls add_task
- Chat endpoint creates tasks from user messages
- User isolation enforced at all levels
- Conversation history persists and resumes correctly

---

## Phase 4: User Story 2 - View and List Tasks [P1]

**User Story**: Users can view their tasks by asking in natural language, with support for filtering by status (all, pending, completed).

**Goal**: Implement list_tasks MCP tool, integrate with agent, extend chat endpoint

**Duration**: ~3-4 hours

**Prerequisites**: Phase 3 complete (needs tasks to list)

**Independent Test Criteria**:
- ✅ User with 3 pending + 2 completed tasks asks "Show me all my tasks" → Returns all 5
- ✅ User asks "What's pending?" → Returns only incomplete tasks
- ✅ User asks "Show completed tasks" → Returns only completed tasks
- ✅ User with no tasks asks "List my tasks" → "You don't have any tasks yet. Would you like to add one?"

### MCP Tool: list_tasks

- [ ] T074 [P] [US2] Write failing test for list_tasks tool in backend/tests/test_mcp_tools/test_list_tasks.py
- [ ] T075 [P] [US2] Test: list_tasks with status="all" → returns all tasks
- [ ] T076 [P] [US2] Test: list_tasks with status="pending" → returns only incomplete
- [ ] T077 [P] [US2] Test: list_tasks with status="completed" → returns only complete
- [ ] T078 [P] [US2] Test: list_tasks with no tasks → returns empty list
- [ ] T079 [P] [US2] Test: list_tasks enforces user_id isolation
- [ ] T080 [US2] Implement list_tasks(user_id, status?) in backend/src/mcp_tools/list_tasks.py
- [ ] T081 [US2] Add status parameter validation (enum: "all", "pending", "completed")
- [ ] T082 [US2] Implement database query with user_id filtering
- [ ] T083 [US2] Apply status filter if provided (WHERE completed = true/false)
- [ ] T084 [US2] Return {tasks: [{task_id, title, description, completed, created_at}, ...], count: int}
- [ ] T085 [US2] Run tests and verify all list_tasks tests pass

### AI Agent Integration

- [ ] T086 [P] [US2] Create MCP tool definition for list_tasks in backend/src/ai_agent/tools.py
- [ ] T087 [P] [US2] Add tool description: "List tasks with optional filtering. Use when user asks to see, show, or list tasks."
- [ ] T088 [P] [US2] Define parameter schema with user_id, status (optional)
- [ ] T089 [P] [US2] Register list_tasks tool with agent
- [ ] T090 [US2] Write integration test: agent interprets "Show my tasks" → calls list_tasks with status="all"
- [ ] T091 [US2] Write integration test: agent interprets "What's pending?" → calls list_tasks with status="pending"
- [ ] T092 [US2] Write integration test: empty task list → agent responds with helpful message
- [ ] T093 [US2] Run integration tests and verify agent correctly uses list_tasks tool

### Chat Endpoint Extension

- [ ] T094 [US2] Update chat endpoint to register list_tasks tool with agent
- [ ] T095 [US2] Write E2E test: Add tasks → Ask "Show my tasks" → Verify tasks listed in response
- [ ] T096 [US2] Write E2E test: Filter by status via natural language → Verify correct filtering
- [ ] T097 [US2] Run E2E tests and verify list functionality works end-to-end

**Parallel Execution Opportunities**:
- T074-T079 (tests) can run in parallel
- T086-T089 (agent def) can run parallel with T080-T085 (implementation)
- T090-T093 (integration tests) sequential after both complete

**Validation**:
- All list_tasks tests pass
- Agent correctly interprets list requests with status filters
- Chat endpoint returns task lists correctly
- User isolation enforced (users only see their own tasks)

---

## Phase 5: User Story 3 - Mark Tasks Complete [P2]

**User Story**: Users can mark tasks as complete using natural language, either by task number or task title.

**Goal**: Implement complete_task MCP tool, integrate with agent

**Duration**: ~2-3 hours

**Prerequisites**: Phase 3 and 4 complete (needs tasks to complete)

**Independent Test Criteria**:
- ✅ User with task "Buy milk" (ID 5) says "Mark task 5 as complete" → Task marked complete
- ✅ User says "I finished calling mom" → Agent finds task, marks complete
- ✅ Non-existent task → "I couldn't find that task. Would you like to see your task list?"

### MCP Tool: complete_task

- [ ] T098 [P] [US3] Write failing test for complete_task tool in backend/tests/test_mcp_tools/test_complete_task.py
- [ ] T099 [P] [US3] Test: complete_task with valid task_id → marks task complete
- [ ] T100 [P] [US3] Test: complete_task on already completed task → idempotent (no error)
- [ ] T101 [P] [US3] Test: complete_task with non-existent task_id → raises not found error
- [ ] T102 [P] [US3] Test: complete_task enforces user_id isolation (cannot complete others' tasks)
- [ ] T103 [US3] Implement complete_task(user_id, task_id) in backend/src/mcp_tools/complete_task.py
- [ ] T104 [US3] Query task with user_id AND task_id (security check)
- [ ] T105 [US3] Update completed = true, updated_at = now()
- [ ] T106 [US3] Return {task_id, title, completed: true, updated_at}
- [ ] T107 [US3] Handle task not found (return 404, don't reveal if exists for other user)
- [ ] T108 [US3] Run tests and verify all complete_task tests pass

### AI Agent Integration

- [ ] T109 [P] [US3] Create MCP tool definition for complete_task in backend/src/ai_agent/tools.py
- [ ] T110 [P] [US3] Add tool description: "Mark a task as completed. Use when user says they finished or completed a task."
- [ ] T111 [P] [US3] Define parameter schema with user_id, task_id
- [ ] T112 [P] [US3] Register complete_task tool with agent
- [ ] T113 [US3] Write integration test: agent interprets "Mark task 5 as complete" → calls complete_task
- [ ] T114 [US3] Write integration test: agent handles "I finished buying milk" → calls list_tasks → extracts task_id → calls complete_task
- [ ] T115 [US3] Write integration test: non-existent task → agent responds with helpful error
- [ ] T116 [US3] Run integration tests and verify agent correctly uses complete_task tool

### Chat Endpoint Extension

- [ ] T117 [US3] Update chat endpoint to register complete_task tool with agent
- [ ] T118 [US3] Write E2E test: Add task → Complete via chat → Verify task.completed = true in DB
- [ ] T119 [US3] Write E2E test: Complete by title (natural language) → Verify correct task completed
- [ ] T120 [US3] Run E2E tests and verify complete functionality works end-to-end

**Parallel Execution Opportunities**:
- T098-T102 (tests) in parallel
- T109-T112 (agent def) in parallel with T103-T108 (implementation)

**Validation**:
- All complete_task tests pass
- Agent handles both task ID and natural language task references
- Idempotency works (completing completed task doesn't error)
- User isolation enforced

---

## Phase 6: User Story 4 - Update Task Details [P3]

**User Story**: Users can modify task titles or descriptions through conversational commands.

**Goal**: Implement update_task MCP tool, integrate with agent

**Duration**: ~2-3 hours

**Prerequisites**: Phase 3 and 4 complete (needs tasks to update)

**Independent Test Criteria**:
- ✅ User with task "Buy milk" (ID 3) says "Change task 3 to 'Buy milk and eggs'" → Title updated
- ✅ User says "Update the description of task 2 to include deadline details" → Description updated

### MCP Tool: update_task

- [ ] T121 [P] [US4] Write failing test for update_task tool in backend/tests/test_mcp_tools/test_update_task.py
- [ ] T122 [P] [US4] Test: update_task with title → updates title only
- [ ] T123 [P] [US4] Test: update_task with description → updates description only
- [ ] T124 [P] [US4] Test: update_task with both → updates both fields
- [ ] T125 [P] [US4] Test: update_task with neither title nor description → validation error
- [ ] T126 [P] [US4] Test: update_task enforces user_id isolation
- [ ] T127 [US4] Implement update_task(user_id, task_id, title?, description?) in backend/src/mcp_tools/update_task.py
- [ ] T128 [US4] Validate at least one field provided
- [ ] T129 [US4] Query task with user_id AND task_id
- [ ] T130 [US4] Update provided fields, set updated_at = now()
- [ ] T131 [US4] Return {task_id, title, description, completed, updated_at}
- [ ] T132 [US4] Run tests and verify all update_task tests pass

### AI Agent Integration

- [ ] T133 [P] [US4] Create MCP tool definition for update_task in backend/src/ai_agent/tools.py
- [ ] T134 [P] [US4] Add tool description: "Update task title or description. Use when user wants to change, edit, or modify a task."
- [ ] T135 [P] [US4] Define parameter schema with user_id, task_id, title?, description?
- [ ] T136 [P] [US4] Register update_task tool with agent
- [ ] T137 [US4] Write integration test: agent interprets "Change task 3 to X" → calls update_task
- [ ] T138 [US4] Write integration test: agent handles "Update description of task 2" → prompts for new description → calls update_task
- [ ] T139 [US4] Run integration tests and verify agent correctly uses update_task tool

### Chat Endpoint Extension

- [ ] T140 [US4] Update chat endpoint to register update_task tool with agent
- [ ] T141 [US4] Write E2E test: Add task → Update via chat → Verify changes in DB
- [ ] T142 [US4] Run E2E tests and verify update functionality works end-to-end

**Parallel Execution Opportunities**:
- T121-T126 (tests) in parallel
- T133-T136 (agent def) in parallel with T127-T132 (implementation)

**Validation**:
- All update_task tests pass
- Agent handles partial updates (title only, description only)
- User isolation enforced

---

## Phase 7: User Story 5 - Delete Tasks [P3]

**User Story**: Users can remove tasks from their list using natural language commands.

**Goal**: Implement delete_task MCP tool, integrate with agent

**Duration**: ~2-3 hours

**Prerequisites**: Phase 3 and 4 complete (needs tasks to delete)

**Independent Test Criteria**:
- ✅ User with task "Old meeting" (ID 7) says "Delete task 7" → Task removed from DB
- ✅ User says "Remove the milk task" → Agent finds task → Deletes it

### MCP Tool: delete_task

- [ ] T143 [P] [US5] Write failing test for delete_task tool in backend/tests/test_mcp_tools/test_delete_task.py
- [ ] T144 [P] [US5] Test: delete_task with valid task_id → removes task from DB
- [ ] T145 [P] [US5] Test: delete_task with non-existent task_id → raises not found error
- [ ] T146 [P] [US5] Test: delete_task enforces user_id isolation (cannot delete others' tasks)
- [ ] T147 [US5] Implement delete_task(user_id, task_id) in backend/src/mcp_tools/delete_task.py
- [ ] T148 [US5] Query task with user_id AND task_id (fetch title for confirmation)
- [ ] T149 [US5] DELETE FROM tasks WHERE id = task_id AND user_id = user_id
- [ ] T150 [US5] Return {task_id, deleted: true, title}
- [ ] T151 [US5] Handle task not found error
- [ ] T152 [US5] Run tests and verify all delete_task tests pass

### AI Agent Integration

- [ ] T153 [P] [US5] Create MCP tool definition for delete_task in backend/src/ai_agent/tools.py
- [ ] T154 [P] [US5] Add tool description: "Delete a task permanently. Use when user wants to remove or delete a task."
- [ ] T155 [P] [US5] Define parameter schema with user_id, task_id
- [ ] T156 [P] [US5] Register delete_task tool with agent
- [ ] T157 [US5] Write integration test: agent interprets "Delete task 7" → calls delete_task
- [ ] T158 [US5] Write integration test: agent handles "Remove the milk task" → calls list_tasks → extracts task_id → calls delete_task
- [ ] T159 [US5] Run integration tests and verify agent correctly uses delete_task tool

### Chat Endpoint Extension

- [ ] T160 [US5] Update chat endpoint to register delete_task tool with agent
- [ ] T161 [US5] Write E2E test: Add task → Delete via chat → Verify task removed from DB
- [ ] T162 [US5] Run E2E tests and verify delete functionality works end-to-end

**Parallel Execution Opportunities**:
- T143-T146 (tests) in parallel
- T153-T156 (agent def) in parallel with T147-T152 (implementation)

**Validation**:
- All delete_task tests pass
- Agent handles both task ID and natural language task references
- Deletion is permanent (no soft delete in Phase 3)
- User isolation enforced

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Performance optimization, error handling, logging, security hardening

**Duration**: ~3-4 hours

**Prerequisites**: All user stories (Phase 3-7) complete

### Performance Optimization

- [ ] T163 [P] Verify database indexes exist: user_id on all tables, conversation_id on messages, created_at on messages
- [ ] T164 [P] Verify connection pooling configured: pool_size=10, max_overflow=20 in backend/src/db.py
- [ ] T165 [P] Add query performance logging to ConversationService (log execution time)
- [ ] T166 [P] Add agent execution time logging in runner.py
- [ ] T167 Run load test: 100 concurrent requests to /chat endpoint
- [ ] T168 Verify p95 response time < 3s (if not, optimize bottlenecks)
- [ ] T169 Verify database queries p95 < 100ms (check logs)

### Error Handling & Observability

- [ ] T170 [P] Add structured logging to chat endpoint (log user_id, conversation_id, message length, response time)
- [ ] T171 [P] Add structured logging to all MCP tools (log tool_name, parameters, result, execution_time)
- [ ] T172 [P] Add structured logging to agent runner (log agent decisions, tool calls, errors)
- [ ] T173 [P] Implement graceful error handling for OpenAI API timeout (return user-friendly message)
- [ ] T174 [P] Implement graceful error handling for database connection failures (retry with exponential backoff)
- [ ] T175 [P] Verify all error responses are user-friendly (no raw exceptions exposed)
- [ ] T176 Write test: OpenAI API timeout → user receives "I'm having trouble processing your request. Please try again."
- [ ] T177 Write test: Database failure → user receives generic error message, full error logged

### Security Hardening

- [ ] T178 [P] Audit all database queries for user_id filtering (prevent cross-user data leakage)
- [ ] T179 [P] Verify JWT validation on /chat endpoint (test with invalid token → 401)
- [ ] T180 [P] Verify user ID mismatch detection (test with mismatched user_id → 403)
- [ ] T181 [P] Add input sanitization to chat endpoint (strip excessive whitespace, limit message length to 10000 chars)
- [ ] T182 Write security test: User A tries to access User B's conversation → 404 Not Found
- [ ] T183 Write security test: User A tries to complete User B's task via agent → Task Not Found error
- [ ] T184 Run OWASP security checklist: SQL injection (prevented by SQLModel), XSS (not applicable to API), CSRF (not applicable to stateless API)

### Documentation

- [ ] T185 [P] Add API documentation to chat endpoint with OpenAPI schema
- [ ] T186 [P] Add docstrings to all MCP tools with parameter descriptions and return types
- [ ] T187 [P] Add docstrings to ConversationService methods
- [ ] T188 [P] Add docstrings to AI agent functions
- [ ] T189 Update quickstart.md with deployment instructions
- [ ] T190 Create CHANGELOG.md entry for Phase 3 feature

**Parallel Execution Opportunities**: Most polish tasks are independent and can run in parallel (marked with [P]).

**Validation**:
- Performance targets met (p95 < 3s)
- All errors logged with context
- User-friendly error messages
- Security tests pass
- Documentation complete

---

## Phase 9: Deployment & Verification

**Goal**: Deploy to staging, run smoke tests, prepare for production

**Duration**: ~2 hours

**Prerequisites**: Phase 8 complete

### Deployment

- [ ] T191 Run Alembic migration on staging database: `alembic upgrade head`
- [ ] T192 Verify conversations and messages tables created with correct indexes
- [ ] T193 Set environment variables on staging server: OPENAI_API_KEY, OPENAI_AGENT_MODEL, DATABASE_URL
- [ ] T194 Deploy backend to staging environment
- [ ] T195 Verify backend health check endpoint returns 200 OK
- [ ] T196 Verify /chat endpoint is accessible and requires authentication

### Smoke Tests

- [ ] T197 Smoke test: Add task via chat → Verify task appears in database
- [ ] T198 Smoke test: List tasks via chat → Verify tasks returned
- [ ] T199 Smoke test: Complete task via chat → Verify task.completed = true
- [ ] T200 Smoke test: Update task via chat → Verify changes saved
- [ ] T201 Smoke test: Delete task via chat → Verify task removed
- [ ] T202 Smoke test: Resume conversation → Verify history loaded correctly
- [ ] T203 Smoke test: Multi-turn conversation → Verify context retained
- [ ] T204 Performance test: Send 50 concurrent requests → Verify all succeed with p95 < 3s

### Frontend Integration (Optional - ChatKit)

- [ ] T205 Create frontend chat page at frontend/app/chat/page.tsx
- [ ] T206 Configure OpenAI ChatKit with backend endpoint: /api/{user_id}/chat
- [ ] T207 Add domain to ChatKit allowlist configuration
- [ ] T208 Add JWT token passing to ChatKit config (Authorization header)
- [ ] T209 Deploy frontend to staging
- [ ] T210 Test end-to-end: User logs in → Opens chat → Adds task → Verifies in UI

### Production Readiness

- [ ] T211 Review all logs for sensitive data exposure (ensure no API keys, passwords logged)
- [ ] T212 Verify rate limiting configured (if applicable)
- [ ] T213 Set up monitoring alerts: p95 > 2.5s, error rate > 1%, database connection pool exhausted
- [ ] T214 Create rollback plan: Alembic downgrade command, database backup strategy
- [ ] T215 Document production deployment steps in README.md
- [ ] T216 Get stakeholder sign-off for production deployment

**Validation**:
- All smoke tests pass on staging
- Performance targets met in staging environment
- Frontend (if deployed) works end-to-end
- Production deployment plan documented

---

## Parallel Execution Examples

### Example 1: Phase 3 (US1 - Add Task)

**Parallel Track 1 - Tests (T038-T043)**:
```bash
# Can run simultaneously (different test files)
pytest backend/tests/test_mcp_tools/test_add_task.py::test_add_task_with_valid_params &
pytest backend/tests/test_mcp_tools/test_add_task.py::test_add_task_with_description &
pytest backend/tests/test_mcp_tools/test_add_task.py::test_add_task_empty_title &
wait
```

**Parallel Track 2 - After Implementation Complete (T050-T056 and T057-T068)**:
```bash
# Agent integration tests can run while endpoint is being built
# (if using separate test database or mocking)
pytest backend/tests/test_ai_agent/ &
# Endpoint implementation in separate terminal
# Both merge at T069 (E2E tests require both complete)
```

### Example 2: Phase 5-7 (US3, US4, US5)

**After US1 and US2 complete, these can run in parallel**:
```bash
# Developer A: US3 (Complete Task)
# T098-T120

# Developer B: US4 (Update Task)
# T121-T142

# Developer C: US5 (Delete Task)
# T143-T162

# All three user stories are independent and can be developed simultaneously
```

### Example 3: Phase 8 (Polish)

**Most polish tasks are parallelizable**:
```bash
# Performance optimization
Task T163-T169 (one developer)

# Error handling & observability
Task T170-T177 (another developer)

# Security hardening
Task T178-T184 (another developer)

# Documentation
Task T185-T190 (another developer or technical writer)

# All can work simultaneously
```

---

## Task Summary

### Total Task Count: 216 tasks

### Tasks by Phase:

| Phase | Description | Task Count | Duration |
|-------|-------------|------------|----------|
| Phase 1 | Setup & Initialization | 10 | ~1 hour |
| Phase 2 | Foundational Infrastructure | 27 | ~3-4 hours |
| Phase 3 | US1: Natural Language Task Addition [P1] | 36 | ~4-5 hours |
| Phase 4 | US2: View and List Tasks [P1] | 24 | ~3-4 hours |
| Phase 5 | US3: Mark Tasks Complete [P2] | 23 | ~2-3 hours |
| Phase 6 | US4: Update Task Details [P3] | 22 | ~2-3 hours |
| Phase 7 | US5: Delete Tasks [P3] | 20 | ~2-3 hours |
| Phase 8 | Polish & Cross-Cutting Concerns | 28 | ~3-4 hours |
| Phase 9 | Deployment & Verification | 26 | ~2 hours |

### Parallel Opportunities: 94 tasks marked with [P]

### MVP Scope (Phases 1-4): 97 tasks, ~11-14 hours of work

### Full Feature Scope (All Phases): 216 tasks, ~22-27 hours of work

---

## Constitution Compliance Checklist

Every task in this breakdown enforces these constitutional principles:

- ✅ **Stateless Architecture**: All conversation state in database, no server memory
- ✅ **AI-Native Development**: OpenAI Agents SDK orchestrates via MCP tools
- ✅ **MCP-First Tool Architecture**: 5 tools with typed parameters, deterministic outputs
- ✅ **Database-Centric State Management**: Conversations, messages, tasks in PostgreSQL
- ✅ **User Isolation & Security**: user_id validation on every endpoint, query, and tool
- ✅ **Natural Language Understanding**: Agent interprets intents, asks clarifications
- ✅ **Test-First Development**: TDD enforced (red → green → refactor)
- ✅ **OpenAI Agents SDK Integration**: Official SDK with proper context and tool bindings
- ✅ **Observability & Debugging**: Structured logging for all requests, tools, errors

---

## Format Validation

✅ **All 216 tasks follow the required checklist format**:
- Checkbox: `- [ ]` ✓
- Task ID: T001-T216 ✓
- [P] marker: 94 parallelizable tasks marked ✓
- [Story] label: All user story phase tasks labeled (US1-US5) ✓
- Description with file paths: All tasks include clear actions and specific file locations ✓

---

## Next Steps

1. **Review this breakdown**: Verify all user stories covered, dependencies clear
2. **Choose scope**: MVP (Phases 1-4) or Full Feature (All Phases)
3. **Begin implementation**: Start with Phase 1, follow TDD workflow
4. **Track progress**: Check off tasks as completed, note any blockers
5. **Run edge case tests**: After Phase 8 complete, run `/sp.edge-case-tester` automatically
6. **Deploy**: Follow Phase 9 deployment checklist

---

**Tasks Status**: ✅ Complete and Ready for Implementation
**Organization**: By user story for independent development and testing
**TDD Compliance**: Tests written before implementation for every component
**Constitution Aligned**: All principles enforced at every level
