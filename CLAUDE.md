# Claude Code Rules

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

---

# 📋 Project Overview: Todo Chatbot Phase 3

**Todo Chatbot Phase 3** is an AI-powered task management application with natural language interface.

### Technology Stack

**Backend:** FastAPI, SQLModel, PostgreSQL, Alembic, OpenAI Agents SDK, pytest
**Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Vercel
**Architecture:** Stateless JWT auth, MCP tools, Database-centric, Horizontally scalable

---

## 📂 Project Structure

```
todo-chatbot-phase3/
├── backend/              # FastAPI backend
│   └── CLAUDE.md         # Backend-specific guide ⭐
├── frontend/             # Next.js frontend
│   └── CLAUDE.md         # Frontend-specific guide ⭐
├── .claude/
│   ├── agents/           # 10 FTE agents
│   ├── skills/           # 31 reusable skills
│   └── docs/             # 📚 Detailed documentation
│       ├── skills-reference.md       # Complete 31 skills guide
│       ├── skills-scenarios.md       # Usage scenarios & mappings
│       └── architect-guidelines.md   # Architecture planning guide
├── .specify/             # SpecKit Plus framework
│   └── memory/constitution.md
├── specs/                # Feature specifications
└── history/              # PHRs & ADRs
```

**📌 Navigation:**
- Backend work → `backend/CLAUDE.md`
- Frontend work → `frontend/CLAUDE.md`
- Skills reference → `.claude/docs/skills-reference.md`
- Usage scenarios → `.claude/docs/skills-scenarios.md`
- Architecture → `.claude/docs/architect-guidelines.md`

---

## 🔌 MCP Server Integration (Model Context Protocol)

**Enhanced with programmatic API control for deployment and version control platforms.**

### Configured MCP Servers

The project integrates **4 MCP servers** for automated platform operations:

| Server | Platform | Purpose | Configuration |
|--------|----------|---------|---------------|
| **context7** | Documentation | Search library docs & code examples | `.claude/.mcp.json` |
| **vercel** | Deployment | Deploy & manage Next.js on Vercel | `.claude/.mcp.json` |
| **render** | Deployment | Deploy & manage FastAPI backends | `.claude/.mcp.json` |
| **github** | Version Control | Automate GitHub operations (PRs, issues, releases) | `.claude/.mcp.json` |

### MCP Configuration File

**Location:** `.claude/.mcp.json` (⚠️ Contains API keys - **gitignored**)

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_KEY"]
    },
    "vercel": {
      "url": "https://mcp.vercel.com",
      "headers": { "Authorization": "Bearer YOUR_TOKEN" }
    },
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_TOKEN" }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_PAT" }
    }
  }
}
```

### MCP-Enhanced Skills

**Skills with MCP integration:**
- ✅ `/vercel-deployer` - Programmatic Vercel deployments
- ✅ `/render-deployer` - Automated Render backend deployments
- ✅ `/github-specialist` - GitHub automation (PRs, issues, releases)

### Usage Pattern

```
User Request
    ↓
Check MCP Availability
    ↓
Use MCP Tools (programmatic) ✅
    ↓ (if MCP unavailable)
Fallback to Manual Instructions
```

**Example:**
```
User: "Deploy to Vercel"
→ Uses Vercel MCP to trigger deployment
→ Returns deployment URL and status

User: "Create a PR for my changes"
→ Uses GitHub MCP to create pull request
→ Returns PR link
```

### Security Notes

⚠️ **CRITICAL:**
- `.claude/.mcp.json` contains sensitive API keys and tokens
- ✅ Added to `.gitignore` - **NEVER commit to repository**
- ✅ Rotate tokens regularly (every 90 days)
- ✅ Use fine-grained permissions (minimum required scopes)
- ✅ Store production tokens separately from development tokens

### MCP Resources

- **MCP Specification:** https://modelcontextprotocol.io/
- **Available MCP Servers:** https://github.com/modelcontextprotocol/servers
- **Configuration:** `.claude/.mcp.json`
- **Skills Documentation:** See individual skill files

---

## 🏭 Digital Agent Factory (16 FTE Agents) - EXPANDED!

**Orchestration:** orchestrator (Auto-analyzes prompts & delegates tasks)
**Backend:** backend-developer, database-engineer, security-engineer, qa-engineer, devops-engineer
**Frontend:** frontend-developer, uiux-designer, vercel-deployer
**Cross-Cutting:** fullstack-architect, github-specialist
**NEW Specialists:** data-engineer, technical-writer, cloud-architect, api-architect, product-manager

**Total:** 42 reusable intelligence skills | **Docs:** `.claude/agents/README.md`

---

## 🧠 Reusable Intelligence Skills (42 Total) - EXPANDED!

**📚 Complete Reference:** See `.claude/docs/skills-reference.md`

### Categories Summary

0. **🤖 Automation & Orchestration (1):** prompt-analyzer
1. **Workflow & Planning (5):** new-feature, change-management, skill-creator, specify, plan
2. **Core Implementation (5):** mcp-tool-builder, ai-agent-setup, chatbot-endpoint, conversation-manager, database-schema-expander
3. **Foundation Patterns (6):** jwt-authentication, password-security, user-isolation, pydantic-validation, connection-pooling, transaction-management
4. **Role-Based (7):** backend-developer, frontend-developer, fullstack-architect, database-engineer, devops-engineer, security-engineer, uiux-designer
5. **Quality & Testing (3):** edge-case-tester, ab-testing, qa-engineer
6. **Production (5):** deployment-automation, production-checklist, structured-logging, performance-logger, vercel-deployer
7. **🆕 Modern Architecture (10 NEW!):** caching-strategy, api-contract-design, message-queue-integration, observability-apm, microservices-patterns, infrastructure-as-code, feature-flags-management, websocket-realtime, graphql-api, container-orchestration

**📚 Detailed Guides:**
- **Complete skills reference:** `.claude/docs/skills-reference.md`
- **Usage scenarios & mappings:** `.claude/docs/skills-scenarios.md`
- **When to use which skill:** `.claude/docs/skills-scenarios.md`

---

## 🎯 Quick Start

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Skills Library:**
```bash
ls .claude/skills/        # List all 31 skills
cat .claude/skills/jwt-authentication/SKILL.md
```

---

## 🔧 Development Guidelines

### ⚠️ CRITICAL: SKILL-FIRST APPROACH (MANDATORY)

**BEFORE implementing ANY feature:**
1. ✅ Check `.claude/skills/` for applicable skills
2. ✅ Display skill plan and wait for user approval
3. ✅ Execute using Skill tool
4. ❌ NEVER implement manually if skill exists

**Terminal output MANDATORY:**
```
🔧 Using Skill: /sp.skill-name
Purpose: [purpose]
Files Generated: [list]
✅ Skill Complete
```

**Enforcement:** Manual implementation when skill exists = VIOLATION

**📚 See:** `.claude/docs/skills-scenarios.md` for complete usage protocol

---

### Core Guarantees

1. **PHR Creation:** Record every user input in a Prompt History Record
   - **When:** Implementation, planning, debugging, spec/task creation
   - **Routing:** `history/prompts/constitution/`, `history/prompts/<feature>/`, `history/prompts/general/`

2. **ADR Suggestions:** Suggest (never auto-create) for architecturally significant decisions
   - **Format:** "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`"

3. **Human as Tool:** Invoke user for clarification, dependencies, architectural choices, completion checkpoints

---

### Default Policies

- Clarify and plan first; use MCP tools and CLI for verification
- Never hardcode secrets; use `.env`
- Smallest viable diff; no unrelated refactoring
- Cite code with references (path:line); propose new code in fenced blocks
- See `.specify/memory/constitution.md` for complete code standards

---

## 📚 Detailed Documentation

**All detailed guides moved to `.claude/docs/` for better organization:**

1. **Skills Reference** (`.claude/docs/skills-reference.md`)
   - Complete 31 skills with tables
   - When to use each skill
   - Quick reference mappings

2. **Skills Scenarios** (`.claude/docs/skills-scenarios.md`)
   - Usage scenarios (chatbot, auth, production, etc.)
   - Discovery protocol
   - Skill chaining examples
   - Terminal output formats

3. **Architect Guidelines** (`.claude/docs/architect-guidelines.md`)
   - Planning framework
   - ADR significance tests
   - Execution contracts
   - Acceptance criteria

4. **Constitution** (`.specify/memory/constitution.md`)
   - Project principles
   - Code quality standards
   - Architecture patterns

---

## Quick Reference: User Request → Skills

| Request | Skills |
|---------|--------|
| "Create chatbot" | ai-agent-setup, chatbot-endpoint, conversation-manager |
| "Add auth" | jwt-authentication, password-security, user-isolation |
| "Test feature" | edge-case-tester, qa-engineer |
| "Deploy" | deployment-automation, production-checklist |
| "Merge/PR" | github-specialist |
| "Optimize" | performance-logger, connection-pooling |

**📚 Complete mapping:** See `.claude/docs/skills-scenarios.md`

---

## Remember

- **Skills are MANDATORY** - not optional
- **Check `.claude/docs/` for detailed guides**
- **Backend/Frontend specifics** → See respective `CLAUDE.md` files
- **Constitution principles** → `.specify/memory/constitution.md`
- **Always create PHRs** after completing work
- **Suggest ADRs** for significant decisions

**Success = Skill-based development + PHR tracking + Constitution compliance**
