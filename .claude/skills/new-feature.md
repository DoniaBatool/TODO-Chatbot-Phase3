---
description: Automatically scaffold a complete new feature with spec.md, plan.md, and tasks.md from a feature description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill automates the complete feature scaffolding workflow by sequentially creating spec.md, plan.md, and tasks.md from a single feature description. Ensures consistent structure and complete planning artifacts before implementation begins.

### 1. Parse Feature Description

Extract from user input:
- **Feature name**: Short identifier (e.g., "ai-chatbot", "task-management", "user-profiles")
- **Feature description**: What the feature should do and why
- **Key requirements**: Main functionality points
- **User context**: Who will use this feature and how

**If feature description is incomplete**, use the AskUserQuestion tool to clarify:
- What is the primary goal of this feature?
- Who are the users and what problem does it solve?
- What are the must-have capabilities?
- Any specific constraints or dependencies?

### 2. Determine Feature Location

**Feature directory structure**:
```
specs/
├── <feature-name>/
│   ├── spec.md          # Created by /sp.specify
│   ├── plan.md          # Created by /sp.plan
│   └── tasks.md         # Created by /sp.tasks
```

**Feature name rules**:
- Lowercase with hyphens (e.g., `ai-chatbot`, not `AI_Chatbot`)
- Descriptive but concise (2-4 words max)
- Matches the main capability (e.g., `user-authentication`, `task-management`)

### 3. Workflow Execution

Execute the three-phase workflow **sequentially** (each phase depends on previous):

#### Phase 1: Create Specification (`/sp.specify`)

**Purpose**: Define WHAT the feature does and WHY it's needed

**Action**: Invoke `/sp.specify` skill with feature description

**Input to /sp.specify**:
```
Feature: <feature-name>

Description: <user's feature description>

Requirements:
- <key requirement 1>
- <key requirement 2>
- <key requirement 3>
```

**Expected Output**: `specs/<feature-name>/spec.md` created with:
- Feature overview
- Functional requirements (numbered)
- Success criteria
- Acceptance tests
- Out of scope items
- Dependencies

**Validation**: Verify `specs/<feature-name>/spec.md` exists and contains:
- At least 3 functional requirements
- At least 3 success criteria
- Clear feature boundaries (in/out of scope)

#### Phase 2: Create Implementation Plan (`/sp.plan`)

**Purpose**: Define HOW the feature will be built (architecture and design)

**Action**: Invoke `/sp.plan` skill (reads from spec.md automatically)

**Expected Output**: `specs/<feature-name>/plan.md` created with:
- Architecture overview
- Design decisions with rationale
- Technology stack
- Data models
- API contracts
- File structure
- ADR suggestions (if significant decisions made)

**Validation**: Verify `specs/<feature-name>/plan.md` exists and contains:
- Clear architecture section
- Design patterns identified
- Technology choices justified
- File structure defined

#### Phase 3: Create Task Breakdown (`/sp.tasks`)

**Purpose**: Define step-by-step implementation tasks with dependencies

**Action**: Invoke `/sp.tasks` skill (reads from spec.md and plan.md automatically)

**Expected Output**: `specs/<feature-name>/tasks.md` created with:
- Ordered task list with IDs
- Dependencies between tasks
- Acceptance criteria per task
- Estimated complexity
- Test requirements

**Validation**: Verify `specs/<feature-name>/tasks.md` exists and contains:
- At least 5 tasks
- Dependencies clearly marked
- Each task has acceptance criteria
- Tasks follow plan architecture

### 4. Cross-Artifact Consistency Check

After all three files created, verify consistency:

**Check 1: Requirements Coverage**
- Every requirement in spec.md has corresponding tasks in tasks.md
- No tasks exist that don't trace back to a requirement

**Check 2: Architecture Alignment**
- Tasks implement the architecture defined in plan.md
- File structure in plan.md matches file creation tasks

**Check 3: Constitution Compliance**
- Spec, plan, and tasks all reference constitution principles
- Architecture follows Phase 3 constitution (stateless, user isolation, MCP-first, etc.)

**Check 4: Completeness**
- All three files created successfully
- No placeholder sections left unfilled
- All cross-references valid

### 5. ADR Suggestion

If plan.md identified architecturally significant decisions, suggest creating ADRs:

**Detection**: Look for decisions in plan.md that involve:
- Framework/library choices
- Database schema design
- Authentication/authorization approach
- API design patterns
- State management strategy

**Suggestion Format**:
```
📋 Architectural decisions detected in plan.md:
   1. [Decision title 1]
   2. [Decision title 2]

Document these decisions? Run:
   /sp.adr <decision-title-1>
   /sp.adr <decision-title-2>
```

### 6. Summary and Next Steps

Provide clear summary of what was created:

```text
✅ Feature Scaffolding Complete: <feature-name>

📁 Files Created:
   - specs/<feature-name>/spec.md (X requirements, Y success criteria)
   - specs/<feature-name>/plan.md (architecture, Z design patterns)
   - specs/<feature-name>/tasks.md (N tasks, M dependencies)

📋 Feature Overview:
   <1-2 sentence summary from spec.md>

🎯 Next Steps:
   1. Review spec.md - verify requirements are complete
   2. Review plan.md - validate architecture decisions
   3. Review tasks.md - ensure task breakdown is clear
   4. [If ADRs suggested] Document architectural decisions
   5. Run /sp.implement to begin implementation

📊 Constitution Compliance:
   ✓ Stateless Architecture
   ✓ User Isolation & Security
   ✓ MCP-First Tool Architecture
   ✓ Database-Centric State Management
   [... other relevant principles ...]

Ready to implement? Run: /sp.implement
```

## Workflow Diagram

```
User Prompt: "Create AI chatbot feature"
           |
           ▼
    ┌──────────────────────────────────┐
    │ sp.new-feature skill activated   │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Parse feature description        │
    │ - Feature name: ai-chatbot       │
    │ - Requirements extracted         │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Phase 1: /sp.specify             │
    │ Creates: specs/ai-chatbot/spec.md│
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Phase 2: /sp.plan                │
    │ Creates: specs/ai-chatbot/plan.md│
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Phase 3: /sp.tasks               │
    │ Creates: specs/ai-chatbot/tasks.md│
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Validate all 3 files             │
    │ - Consistency check              │
    │ - Constitution compliance        │
    │ - Completeness verification      │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Suggest ADRs (if applicable)     │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Summary + Next Steps             │
    │ Ready for /sp.implement          │
    └──────────────────────────────────┘
```

## Error Handling

### If /sp.specify fails:
- **Error**: Stop workflow immediately
- **Action**: Show error message from /sp.specify
- **Recovery**: Fix spec.md issues before proceeding

### If /sp.plan fails:
- **Error**: spec.md exists but plan.md creation failed
- **Action**: Show error message from /sp.plan
- **Recovery**: Verify spec.md is complete and valid

### If /sp.tasks fails:
- **Error**: spec.md and plan.md exist but tasks.md creation failed
- **Action**: Show error message from /sp.tasks
- **Recovery**: Verify plan.md has sufficient detail for task breakdown

### If consistency check fails:
- **Error**: Files created but have inconsistencies
- **Action**: List specific inconsistencies found
- **Recovery**: Manually edit files to resolve conflicts

## Usage Examples

### Example 1: AI Chatbot Feature

**User prompt**:
```
Create an AI chatbot feature that lets users manage tasks through natural language
```

**Skill execution**:
```bash
/sp.new-feature Create an AI chatbot feature that lets users manage tasks through natural language
```

**Result**:
- `specs/ai-chatbot/spec.md` - Requirements for chat interface, NLP, task operations
- `specs/ai-chatbot/plan.md` - OpenAI Agents SDK, MCP tools, conversation state
- `specs/ai-chatbot/tasks.md` - 15 tasks from DB schema to endpoint implementation

### Example 2: User Profile Feature

**User prompt**:
```
Add user profiles with avatar upload, bio, and settings
```

**Skill execution**:
```bash
/sp.new-feature Add user profiles with avatar upload, bio, and settings
```

**Result**:
- `specs/user-profiles/spec.md` - Profile CRUD, file upload, settings management
- `specs/user-profiles/plan.md` - S3 storage, image processing, schema design
- `specs/user-profiles/tasks.md` - 12 tasks from migration to API endpoints

### Example 3: Minimal Feature Description

**User prompt**:
```
Add notifications
```

**Skill execution**:
```bash
/sp.new-feature Add notifications
```

**Skill action**: Detect incomplete description, ask clarifying questions:
```
❓ Clarification Needed:

1. What type of notifications?
   • Email notifications
   • In-app notifications
   • Push notifications
   • All of the above

2. What triggers notifications?
   • Task deadlines
   • Team mentions
   • System alerts
   • Custom events

3. Do users need notification preferences?
   • Yes, full control
   • No, all notifications enabled
   • Some preferences only

Please provide more details or select from options above.
```

## Constitution Alignment

- ✅ **Spec-Driven Development**: Creates complete planning artifacts before code
- ✅ **Constitution Compliance**: All artifacts enforce constitution principles
- ✅ **Systematic Planning**: Structured workflow prevents incomplete specs
- ✅ **Traceability**: Requirements → Plan → Tasks linkage maintained
- ✅ **Quality Assurance**: Cross-artifact consistency checks

## Success Criteria

- [ ] Feature name extracted from user prompt (or clarified via questions)
- [ ] /sp.specify executed successfully, spec.md created
- [ ] /sp.plan executed successfully, plan.md created
- [ ] /sp.tasks executed successfully, tasks.md created
- [ ] All three files exist in `specs/<feature-name>/` directory
- [ ] Consistency check passes (requirements → plan → tasks alignment)
- [ ] Constitution compliance verified in all artifacts
- [ ] ADR suggestions provided if significant decisions detected
- [ ] Summary printed with file locations and next steps
- [ ] User can proceed directly to /sp.implement

## Integration with Existing Workflow

### Before this skill:
```
User: "Create AI chatbot"
Developer: Manually run /sp.specify, then /sp.plan, then /sp.tasks
```

### With this skill:
```
User: "Create AI chatbot"
/sp.new-feature: Automatically runs all three in sequence
Developer: Review artifacts and run /sp.implement
```

### Skill chaining:
```
/sp.new-feature → spec.md + plan.md + tasks.md created
         ↓
/sp.implement → reads tasks.md and executes implementation
         ↓
/sp.edge-case-tester → automatically runs after implementation
         ↓
/sp.git.commit_pr → commits and creates PR
```

## Advantages

1. **Speed**: One command instead of three
2. **Consistency**: Ensures complete planning before implementation
3. **Quality**: Cross-artifact validation catches gaps early
4. **Compliance**: Constitution principles enforced from start
5. **Traceability**: Complete audit trail from requirement to task
6. **Beginner-Friendly**: Automates complex workflow for new users

## References

- Existing Skills: `/sp.specify`, `/sp.plan`, `/sp.tasks`
- Constitution: `.specify/memory/constitution.md`
- Spec Template: `.specify/templates/spec-template.md`
- Plan Template: `.specify/templates/plan-template.md`
- Tasks Template: `.specify/templates/tasks-template.md`
