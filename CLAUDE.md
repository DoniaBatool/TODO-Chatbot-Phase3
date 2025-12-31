# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Reusable Intelligence Skills (Phase 3)

### ⚠️ CRITICAL REQUIREMENT - SKILL-FIRST APPROACH (MANDATORY)

**RELIGIOUS ENFORCEMENT OF SKILLS IS REQUIRED BY PROJECT GUIDELINES**

You have access to reusable intelligence skills that MUST be used for ALL Phase 3 development. This is a NON-NEGOTIABLE requirement from project teachers/instructors.

**SKILL USAGE RULES (MUST FOLLOW):**

1. **BEFORE implementing ANY feature:**
   - ✅ FIRST: Identify which skills apply to the task
   - ✅ SECOND: Display skill plan in terminal and wait for user approval
   - ✅ THIRD: Execute using identified skills (invoke via Skill tool)
   - ❌ NEVER implement manually if a skill exists

2. **Terminal output MANDATORY:**
   - Display: "🔧 Using Skill: /sp.skill-name"
   - Show purpose, tasks covered, files to be generated
   - Report completion status: "✅ Skill Complete"

3. **If no skill exists:**
   - Use `/sp.skill-creator` to create a new skill first
   - Document the new skill in SKILLS.md
   - THEN use the newly created skill

4. **Skill invocation tracking:**
   - Every feature MUST have a skills usage report
   - Show which skills were used and why
   - Show which skills were created for missing capabilities

**ENFORCEMENT:**
- Manual implementation when skill exists = VIOLATION of project guidelines
- Skills are NOT optional - they are MANDATORY
- Teachers require skill-based development approach
- All work must demonstrate skill usage

**WHY SKILLS ARE MANDATORY:**
- Enforce constitution principles automatically
- Ensure consistency across features
- Reusable intelligence that improves over time
- Educational requirement from instructors
- Better code quality and testing coverage

These skills MUST be used automatically when implementing Phase 3 features. Terminal output MUST show which skills are being used.

### Core Implementation Skills

**MCP Tool Builder** (`/sp.mcp-tool-builder`)
- **When to use**: When creating any MCP tool for AI agent integration
- **Auto-triggers**: When implementing task operations (add, list, complete, delete, update)
- **Output**: MCP tool implementation, tests, contracts, registration

**AI Agent Setup** (`/sp.ai-agent-setup`)
- **When to use**: When configuring OpenAI Agents SDK
- **Auto-triggers**: During chatbot initialization
- **Output**: Agent configuration, tool bindings, tests

**Chatbot Endpoint** (`/sp.chatbot-endpoint`)
- **When to use**: When creating stateless chat API endpoints
- **Auto-triggers**: When implementing chat functionality
- **Output**: Endpoint implementation, JWT validation, tests

**Conversation Manager** (`/sp.conversation-manager`)
- **When to use**: When managing conversation state in database
- **Auto-triggers**: With chatbot endpoint creation
- **Output**: Conversation/Message models, manager implementation

**Database Schema Expander** (`/sp.database-schema-expander`)
- **When to use**: When adding new tables to database
- **Auto-triggers**: When new data models needed
- **Output**: SQLModel definitions, migrations, indexes

### Phase 2 Foundation Skills

These skills implement proven patterns from Phase 2 that are essential for Phase 3 development:

**JWT Authentication** (`/sp.jwt-authentication`)
- **When to use**: Setting up user authentication, protected endpoints
- **Auto-triggers**: When implementing auth system
- **Output**: JWT creation/verification, FastAPI dependency, login endpoint

**User Isolation** (`/sp.user-isolation`)
- **When to use**: Protecting user-owned resources, preventing data leakage
- **Auto-triggers**: When implementing CRUD operations on user data
- **Output**: Query scoping patterns, ownership checks, security logging

**Password Security** (`/sp.password-security`)
- **When to use**: Implementing signup/login with credentials
- **Auto-triggers**: When user authentication with passwords needed
- **Output**: bcrypt hashing utilities, signup/login endpoints, secure schemas

**Pydantic Validation** (`/sp.pydantic-validation`)
- **When to use**: Creating API endpoints with input validation
- **Auto-triggers**: When defining FastAPI routes with request bodies
- **Output**: Request/response DTOs, custom validators, FastAPI integration

**Connection Pooling** (`/sp.connection-pooling`)
- **When to use**: Setting up database connections for production
- **Auto-triggers**: During database initialization
- **Output**: Engine config, pool settings, health monitoring, session dependency

**Transaction Management** (`/sp.transaction-management`)
- **When to use**: Implementing database write operations
- **Auto-triggers**: When creating/updating/deleting database records
- **Output**: Try/commit/rollback patterns, multi-step atomicity, error handling

### Workflow Automation Skills

**New Feature Scaffolder** (`/sp.new-feature`)
- **When to use**: Starting any new feature from scratch
- **Auto-triggers**: Never (manual invocation only)
- **Output**: Complete spec.md, plan.md, and tasks.md in one command
- **Workflow**: Sequentially runs /sp.specify → /sp.plan → /sp.tasks with validation

### Quality Assurance Skills

**A/B Testing** (`/sp.ab-testing`)
- **When to use**: When validating feature variations
- **Manual trigger**: After feature implementation
- **Output**: Test framework, variant configs, analytics

**Edge Case Tester** (`/sp.edge-case-tester`)
- **When to use**: After any feature implementation
- **Auto-triggers**: Automatically after `/sp.implementation` completes
- **Output**: Comprehensive edge case tests (57+ scenarios)

### Meta Skills

**Skill Creator** (`/sp.skill-creator`)
- **When to use**: When new reusable capability needed
- **Manual trigger**: User requests new skill
- **Output**: New skill file, tests, documentation

**Change Management** (`/sp.change-management`)
- **When to use**: When modifying existing features
- **Manual trigger**: User requests change to existing feature
- **Output**: Change spec, impact analysis, updated files, rollback plan

## Skill Usage Contract

### Automatic Skill Selection

Based on user prompts, automatically select and use relevant skills:

**Examples:**
1. **User**: "Create a new feature for user notifications"
   - **Auto-use**: `/sp.new-feature` (creates spec.md, plan.md, tasks.md automatically)

2. **User**: "Add task management chatbot"
   - **Auto-use**: `/sp.database-schema-expander`, `/sp.mcp-tool-builder`, `/sp.ai-agent-setup`, `/sp.chatbot-endpoint`, `/sp.conversation-manager`

3. **User**: "Implement add task functionality"
   - **Auto-use**: `/sp.mcp-tool-builder`

4. **User**: "Add due dates to existing tasks"
   - **Auto-use**: `/sp.change-management`

5. **After** `/sp.implementation` **completes**:
   - **Auto-use**: `/sp.edge-case-tester`

### Terminal Output Format

When using skills, display:
```text
🔧 Using Skill: /sp.mcp-tool-builder

Purpose: Build MCP tool for add_task operation
Constitution Check: ✓ Passed
Files Generated:
  - backend/src/mcp_tools/add_task_tool.py
  - tests/test_add_task_tool.py
  - specs/tasks/contracts/mcp-tools/add_task.md

✅ Skill Complete
```

### Skill Chaining

Skills can chain automatically:
```text
Feature: AI Chatbot
│
├─> /sp.database-schema-expander
│   ✅ Conversation & Message tables created
│
├─> /sp.mcp-tool-builder (5x for each tool)
│   ✅ add_task, list_tasks, complete_task, delete_task, update_task
│
├─> /sp.ai-agent-setup
│   ✅ OpenAI Agents SDK configured
│
├─> /sp.chatbot-endpoint
│   ✅ Stateless chat endpoint at /api/{user_id}/chat
│
└─> /sp.edge-case-tester (automatic after implementation)
    ✅ 57/57 edge cases passed
```

## Skill Integration Points

### When to Use Each Skill

| User Request Pattern | Skills to Use | Order |
|---------------------|---------------|-------|
| "Create chatbot" | database-schema-expander → mcp-tool-builder → ai-agent-setup → chatbot-endpoint → conversation-manager → edge-case-tester | Sequential |
| "Add [MCP tool]" | mcp-tool-builder → edge-case-tester | Sequential |
| "Change [existing feature]" | change-management | Standalone |
| "Test [feature]" | edge-case-tester, ab-testing | Parallel |
| "Create skill for [X]" | skill-creator | Standalone |

### Constitution Enforcement

All skills enforce constitution principles:
- Stateless architecture
- User isolation
- MCP-first design
- Test-driven development
- Database-centric state

Skill output includes constitution compliance verification.

## Skill Learning

**You MUST:**
1. Recognize patterns in user requests
2. Select appropriate skills automatically
3. Display skill usage in terminal
4. Chain skills when needed
5. Use edge-case-tester after implementation
6. Suggest ab-testing for new features

**Remember:**
- Skills are reusable intelligence
- They enforce best practices automatically
- They work across projects
- They self-improve via skill-creator
- They ensure constitution compliance

When in doubt about which skill to use, refer to constitution.md "Reusable Intelligence Skills" section.

## Phase 8-9 Implementation Requirements (SKILL-BASED)

When implementing Phases 8 (Polish & Cross-Cutting Concerns) and Phase 9 (Deployment & Verification), you MUST:

**STEP 1: Skill Planning (MANDATORY)**
- Analyze all tasks in the phase
- Map each task to existing skills OR identify need for new skills
- Create terminal output showing skill execution plan
- Wait for user approval before proceeding

**STEP 2: Skill Creation (If Needed)**
- Use `/sp.skill-creator` for any missing capabilities
- Common Phase 8-9 skills to create:
  - `/sp.performance-logger` - Performance monitoring setup
  - `/sp.structured-logging` - Logging infrastructure
  - `/sp.api-docs-generator` - API documentation automation
  - `/sp.deployment-automation` - Deployment workflow
  - `/sp.production-checklist` - Production readiness validation

**STEP 3: Skill Execution**
- Invoke each skill using the Skill tool
- Display terminal output for each skill invocation
- Track skill usage in implementation PHR

**STEP 4: Skills Usage Report**
- Document which skills were used
- Document which skills were created
- Report any manual tasks (with justification)

**EXAMPLE - Phase 8 Performance Optimization:**
```text
🔧 Phase 8: Performance Optimization

Skills Plan:
1. /sp.connection-pooling → Verify pool configuration (T163-T164)
2. /sp.skill-creator → Create /sp.performance-logger (T165-T166)
3. /sp.performance-logger → Add execution time logging (T165-T166)
4. /sp.ab-testing → Run load tests (T167-T169)

Waiting for approval... ✋
```

**After user approval:**
```text
✅ User approved skill plan

🔧 Using Skill: /sp.connection-pooling
Purpose: Verify database connection pooling configuration
Tasks: T163-T164
Files: backend/src/db.py
✅ Skill Complete

🔧 Using Skill: /sp.skill-creator
Purpose: Create performance logging skill
Output: .claude/skills/sp.performance-logger.md
✅ Skill Complete

🔧 Using Skill: /sp.performance-logger
Purpose: Add performance logging to all services
Tasks: T165-T166
Files: backend/src/routes/chat.py, backend/src/services/conversation_service.py
✅ Skill Complete

🔧 Using Skill: /sp.ab-testing
Purpose: Load testing (100 concurrent requests)
Tasks: T167-T169
✅ Skill Complete
```

## Complete Skills Reference (ALL 31 Skills)

**CRITICAL**: Before implementing ANYTHING, you MUST check `.claude/skills/` directory for applicable skills.

**Location**: All skills are in `.claude/skills/` directory (31 total)
**Constitution Reference**: See `.specify/memory/constitution.md` Section "Phase III+ Requirements: Reusable Intelligence Skills"

---

### 1️⃣ Workflow & Planning Skills (5 skills)

**When user says**: "Create new feature", "Plan implementation", "Break down tasks"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.specify` | `.claude/skills/skill-creator.md` | Creating feature specifications |
| `/sp.plan` | `.claude/skills/skill-creator.md` | Generating implementation plans |
| `/sp.tasks` | `.claude/skills/skill-creator.md` | Breaking down into actionable tasks |
| `/sp.implement` | `.claude/skills/skill-creator.md` | Executing implementation |
| `/sp.new-feature` | `.claude/skills/new-feature.md` | Complete spec→plan→tasks in one workflow |

**Auto-Use**: When user requests "new feature from scratch"

---

### 2️⃣ Core Implementation Skills - Phase III (5 skills)

**When user says**: "Create chatbot", "Add MCP tool", "Add chat endpoint"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.mcp-tool-builder` | `.claude/skills/mcp-tool-builder.md` | Creating MCP tools (add_task, list_tasks, etc.) |
| `/sp.ai-agent-setup` | `.claude/skills/ai-agent-setup.md` | Configuring OpenAI Agents SDK |
| `/sp.chatbot-endpoint` | `.claude/skills/chatbot-endpoint.md` | Creating stateless chat API endpoints |
| `/sp.conversation-manager` | `.claude/skills/conversation-manager.md` | Managing conversation state in database |
| `/sp.database-schema-expander` | `.claude/skills/database-schema-expander.md` | Adding new database tables |

**Auto-Use**: When user mentions "chatbot", "AI agent", "MCP tools", "conversation"

---

### 3️⃣ Foundation Skills - Phase II Patterns (6 skills)

**When user says**: "Add authentication", "Secure user data", "Add validation"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.jwt-authentication` | `.claude/skills/jwt-authentication.md` | JWT creation/verification, protected endpoints |
| `/sp.user-isolation` | `.claude/skills/user-isolation.md` | Protecting user-owned resources, preventing data leakage |
| `/sp.password-security` | `.claude/skills/password-security.md` | bcrypt hashing, signup/login endpoints |
| `/sp.pydantic-validation` | `.claude/skills/pydantic-validation.md` | Request/response DTOs, input validation |
| `/sp.connection-pooling` | `.claude/skills/connection-pooling.md` | Database pool configuration, health monitoring |
| `/sp.transaction-management` | `.claude/skills/transaction-management.md` | Try/commit/rollback patterns, atomicity |

**Auto-Use**: When user mentions "auth", "security", "database", "validation"

---

### 4️⃣ Role-Based Development Skills (7 skills)

**When user says**: "Implement backend", "Create UI", "Design system", "Deploy"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.backend-developer` | `.claude/skills/backend-developer.md` | Backend API implementation (FastAPI, SQLModel) |
| `/sp.frontend-developer` | `.claude/skills/frontend-developer.md` | Frontend UI implementation (Next.js, React) |
| `/sp.fullstack-architect` | `.claude/skills/fullstack-architect.md` | System design & end-to-end architecture |
| `/sp.database-engineer` | `.claude/skills/database-engineer.md` | Database optimization, schema design, indexes |
| `/sp.devops-engineer` | `.claude/skills/devops-engineer.md` | Infrastructure, Docker, CI/CD |
| `/sp.security-engineer` | `.claude/skills/security-engineer.md` | OWASP audit, vulnerability scanning, security tests |
| `/sp.uiux-designer` | `.claude/skills/uiux-designer.md` | Wireframes, user flows, component design |

**Auto-Use**: Based on complexity - use appropriate role-based skill for implementation

---

### 5️⃣ Quality & Testing Skills (3 skills)

**When user says**: "Test this feature", "Run A/B test", "Comprehensive testing"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.edge-case-tester` | `.claude/skills/edge-case-tester.md` | 57+ edge case scenarios (AUTO after /sp.implement) |
| `/sp.ab-testing` | `.claude/skills/ab-testing.md` | A/B test framework, variant configs, analytics |
| `/sp.qa-engineer` | `.claude/skills/qa-engineer.md` | Unit tests, integration tests, smoke tests, E2E |

**Auto-Trigger**: `/sp.edge-case-tester` MUST run automatically after ANY implementation

---

### 6️⃣ Production & Deployment Skills (5 skills)

**When user says**: "Add logging", "Optimize performance", "Deploy", "Production ready"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.performance-logger` | `.claude/skills/performance-logger.md` | Execution time logging, structured metrics |
| `/sp.structured-logging` | `.claude/skills/structured-logging.md` | JSON logging, log aggregation compatibility |
| `/sp.deployment-automation` | `.claude/skills/deployment-automation.md` | Deploy scripts, validation, health checks |
| `/sp.production-checklist` | `.claude/skills/production-checklist.md` | Production readiness validation, checklists |
| `/sp.vercel-deployer` | `.claude/skills/vercel-deployer.md` | Vercel deployment, environment config |

**Auto-Use**: When user mentions "production", "deploy", "performance", "logging"

---

### 7️⃣ Specialized Utility Skills (5 skills)

**When user says**: "Document API", "Modify feature", "Create skill", "GitHub operations"

| Skill | File | When to Use |
|-------|------|-------------|
| `/sp.api-docs-generator` | `.claude/skills/api-docs-generator.md` | OpenAPI/Swagger docs, deployment guides |
| `/sp.change-management` | `.claude/skills/change-management.md` | Modify existing features safely |
| `/sp.skill-creator` | `.claude/skills/skill-creator.md` | Create new reusable skills |
| `/sp.github-specialist` | `.claude/skills/github-specialist.md` | **GitHub operations, branch management, PRs, issues** |
| `/sp.conversation-manager` | `.claude/skills/conversation-manager.md` | Conversation/Message models, chat state |

**IMPORTANT**: Use `/sp.github-specialist` for ALL git/GitHub operations:
- Branch merging/deletion
- Push to remote
- PR creation
- Issue management
- Release creation

**Auto-Use**: When user mentions "git", "GitHub", "merge", "branch", "PR", "issue"

---

## Skills Discovery Protocol (MANDATORY)

**Before implementing ANYTHING:**

### Step 1: Check Skills Directory
```bash
ls .claude/skills/
# Returns 31 skill files
```

### Step 2: Analyze User Request
Identify keywords:
- "chatbot" → ai-agent-setup, chatbot-endpoint, conversation-manager
- "auth" → jwt-authentication, password-security, user-isolation
- "test" → edge-case-tester, qa-engineer, ab-testing
- "deploy" → deployment-automation, production-checklist, vercel-deployer
- "git/GitHub" → github-specialist
- "performance" → performance-logger, connection-pooling
- "API" → backend-developer, api-docs-generator
- "UI" → frontend-developer, uiux-designer

### Step 3: Display Skill Plan
```text
🔧 Skills Analysis for: "[user request]"

Applicable Skills Found:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. /sp.skill-name → Purpose
2. /sp.skill-name → Purpose
...

Skills Execution Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. /sp.skill-name → Task description
2. /sp.skill-name → Task description
...

Approve? (yes/no) ✋
```

### Step 4: Wait for Approval
User responds: "yes", "approved", "1" → Proceed

### Step 5: Execute Skills Sequentially
```text
🔧 Using Skill: /sp.skill-name
Purpose: [Clear purpose]
Tasks: [Task IDs if applicable]
Files Generated: [List of files]
✅ Skill Complete
```

### Step 6: Document in PHR
Add to PHR:
```yaml
skills_used:
  - name: /sp.skill-name
    purpose: [Purpose]
    files: [Files modified/created]
```

---

## Common Scenarios → Skills Mapping

### Scenario 1: "Create AI chatbot"
```
/sp.database-schema-expander → Tables
/sp.mcp-tool-builder (5x) → MCP tools
/sp.ai-agent-setup → Agent config
/sp.chatbot-endpoint → API
/sp.conversation-manager → State
/sp.edge-case-tester → Tests (auto)
```

### Scenario 2: "Add authentication"
```
/sp.database-schema-expander → Users table
/sp.jwt-authentication → JWT setup
/sp.password-security → Auth endpoints
/sp.user-isolation → Protect data
/sp.security-engineer → Audit
```

### Scenario 3: "Prepare for production"
```
/sp.security-engineer → Security audit
/sp.performance-logger → Monitoring
/sp.structured-logging → Logging
/sp.api-docs-generator → Documentation
/sp.deployment-automation → Deploy scripts
/sp.qa-engineer → Smoke tests
/sp.production-checklist → Validation
```

### Scenario 4: "Merge branches to main"
```
/sp.github-specialist → Branch operations
  - Checkout main
  - Merge feature branch
  - Push to remote
  - Delete feature branch
```

### Scenario 5: "Optimize performance"
```
/sp.connection-pooling → Pool config
/sp.performance-logger → Execution logging
/sp.database-engineer → Query optimization
/sp.ab-testing → Load testing
```

---

## Skill Usage Rules (MUST FOLLOW)

### ✅ ALWAYS Use Skills When:
- Creating new features
- Modifying existing code
- Adding authentication/security
- Database operations
- Testing and QA
- Performance optimization
- Production deployment
- **Git/GitHub operations** (merge, push, branch, PR, issue)
- Documentation generation

### ❌ NEVER Do Manually When Skill Exists:
- Manual git commands → Use `/sp.github-specialist`
- Manual file creation → Use appropriate skill
- Manual testing → Use `/sp.edge-case-tester` or `/sp.qa-engineer`
- Manual deployment → Use `/sp.deployment-automation`

### 🚨 Violations Result In:
- IMMEDIATE STOP
- Document violation
- Redo using proper skill-based approach
- Update constitution if needed

---

## Quick Reference: User Request → Skills

| User Says | Use These Skills |
|-----------|-----------------|
| "Create chatbot" | ai-agent-setup, chatbot-endpoint, conversation-manager |
| "Add authentication" | jwt-authentication, password-security, user-isolation |
| "Test feature" | edge-case-tester, qa-engineer |
| "Deploy to production" | deployment-automation, production-checklist |
| "Merge branches" | **github-specialist** |
| "Create PR" | **github-specialist** |
| "Optimize performance" | performance-logger, connection-pooling |
| "Add API endpoint" | backend-developer, pydantic-validation |
| "Create UI" | frontend-developer, uiux-designer |
| "Security audit" | security-engineer |
| "Add logging" | structured-logging, performance-logger |

---

**REMEMBER**: Check `.claude/skills/` directory FIRST, display skill plan, wait for approval, then execute using Skill tool. NO manual implementation when skills exist!
