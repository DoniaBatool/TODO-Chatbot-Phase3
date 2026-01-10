# 🤖 Todo AI Chatbot - Phase III

**An AI-Powered Task Management System with Natural Language Interface**

[![Phase](https://img.shields.io/badge/Phase-III-blue.svg)](https://github.com)
[![Tech Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20OpenAI-green.svg)](https://github.com)
[![Architecture](https://img.shields.io/badge/Architecture-Stateless%20%7C%20MCP--First-orange.svg)](https://github.com)
[![Development](https://img.shields.io/badge/Development-Spec--Driven%20%7C%20Agent--First-purple.svg)](https://github.com)

> **Hackathon II - The Evolution of Todo**
> From simple console app to cloud-native AI-powered distributed system

---

## 📋 Table of Contents

- [Overview](#overview)
- [Phase III Objectives](#phase-iii-objectives)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Digital Agent Factory](#digital-agent-factory)
- [Reusable Intelligence Skills](#reusable-intelligence-skills)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Development Workflow](#development-workflow)
- [Documentation](#documentation)
- [MCP Tools](#mcp-tools)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Constitution & Principles](#constitution--principles)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Todo AI Chatbot - Phase III** is an AI-powered task management application that allows users to manage their todos through **natural language conversations**. Built using **Spec-Driven Development** with **Claude Code** and **SpecKit Plus**, this project demonstrates the evolution from a simple console app to a sophisticated AI-powered web application.

### Key Highlights

✅ **Natural Language Interface** - Manage tasks by chatting with an AI agent
✅ **Voice-Enabled Chat** 🎤 - Speech-to-Text (STT) and Text-to-Speech (TTS) with OpenAI Whisper
✅ **MCP-First Architecture** - Model Context Protocol for AI-app integration
✅ **Stateless Design** - Horizontally scalable, cloud-ready architecture
✅ **Database-Centric State** - All state persisted in PostgreSQL
✅ **Agent-First Development** - Built using 17 specialized FTE AI agents (3 MCP-enhanced 🔌)
✅ **43 Reusable Skills** - Intelligent automation with reusable intelligence
✅ **Spec-Driven** - Every feature starts with a specification
✅ **Constitution-Enforced** - Architectural principles religiously followed

---

## 🎯 Phase III Objectives

### From Hackathon Requirements

**Objective:** Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture.

### Requirements

1. ✅ Implement conversational interface for all **Basic Level features**
2. ✅ Use **OpenAI Agents SDK** for AI logic
3. ✅ Build **MCP server** with Official MCP SDK that exposes task operations as tools
4. ✅ **Stateless chat endpoint** that persists conversation state to database
5. ✅ AI agents use **MCP tools** to manage tasks (stateless, database-backed)

### Natural Language Commands Supported

**Text or Voice Input** 🎤 - All commands work with both typing and speaking!

| User Says | AI Agent Action |
|-----------|----------------|
| "Add a task to buy groceries" | `add_task("Buy groceries")` |
| "Show me all my tasks" | `list_tasks(status="all")` |
| "What's pending?" | `list_tasks(status="pending")` |
| "Mark task 3 as complete" | `complete_task(task_id=3)` |
| "Delete the meeting task" | `delete_task(...)` |
| "Change task 1 to 'Call mom tonight'" | `update_task(task_id=1, ...)` |

**Voice Features:**
- 🎤 **Hold** the microphone button to record (minimum 0.5 seconds)
- 🔊 **Click** the speaker button on any AI message to hear it
- 📱 **Touch-optimized** for mobile devices

---

## 🛠️ Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14+ | React framework with App Router |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.x | Styling |
| **OpenAI ChatKit** | Latest | Chatbot UI framework |
| **shadcn/ui** | Latest | Component library |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.100+ | Python web framework |
| **SQLModel** | 0.0.14+ | ORM with Pydantic integration |
| **OpenAI Agents SDK** | Latest | AI agent framework |
| **Official MCP SDK** | Latest | Model Context Protocol |
| **Alembic** | 1.13+ | Database migrations |
| **pytest** | 8.x | Testing framework |

### Database & Infrastructure

| Technology | Purpose |
|------------|---------|
| **Neon Serverless PostgreSQL** | Cloud database |
| **Better Auth** | Authentication with JWT |
| **Vercel** | Frontend deployment |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Claude Code** | AI-powered development assistant |
| **SpecKit Plus** | Specification management |
| **UV** | Python package manager |
| **WSL 2** | Windows development environment |

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │
│  (Frontend)     │     │  │  POST /api/{user_id}/chat              │  │     │  (PostgreSQL)   │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │  - tasks        │
│                 │     │                  ▼                           │     │  - conversations│
│                 │     │  ┌────────────────────────────────────────┐  │     │  - messages     │
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                     │  │     │                 │
│                 │     │  │  (5 MCP Tools for Task Operations)     │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

### Core Principles

#### 1. **Stateless Architecture**
- ✅ No server-side session storage
- ✅ JWT-based authentication (expires in 1 week)
- ✅ All state persisted in PostgreSQL
- ✅ Horizontally scalable design

#### 2. **MCP-First Design**
- ✅ AI agent uses MCP tools exclusively
- ✅ Tools have proper contracts and validation
- ✅ Tools enforce user isolation
- ✅ Standardized interface for AI-app interaction

#### 3. **Database-Centric State**
- ✅ Conversations stored in database
- ✅ Messages stored in database
- ✅ Agent has no memory (stateless)
- ✅ State retrieved from DB per request

#### 4. **User Isolation**
- ✅ All queries filtered by `user_id`
- ✅ Ownership checks before operations
- ✅ Row-level security enforced
- ✅ No horizontal privilege escalation

---

## 🏭 Digital Agent Factory

This project is built using **17 Full-Time Equivalent (FTE) AI Agents** from our Digital Agent Factory. Each agent specializes in a specific domain and has access to relevant skills.

**🔌 MCP-Enhanced Agents (3):** github-specialist, vercel-deployer, render-deployer

### Backend Specialists (5 Agents)

| Agent | Skills | Responsibilities |
|-------|--------|-----------------|
| **backend-developer** | 11 skills | Backend APIs, MCP tools, authentication, business logic |
| **database-engineer** | 4 skills | Database design, migrations, query optimization, indexes |
| **security-engineer** | 5 skills | OWASP compliance, security audits, penetration testing |
| **qa-engineer** | 3 skills | Testing (unit, integration, E2E), edge cases, quality assurance |
| **devops-engineer** | 4 skills | Infrastructure, deployment, monitoring, CI/CD |

### Frontend Specialists (3 Agents)

| Agent | Skills | Responsibilities |
|-------|--------|-----------------|
| **frontend-developer** | 3 skills | React, Next.js, TypeScript, Tailwind CSS, UI components |
| **uiux-designer** | 2 skills | UI/UX design, design systems, accessibility, user flows |
| **vercel-deployer** 🔌 | 4 skills | Vercel deployment, Next.js optimization, Edge Functions (MCP-enhanced) |

### Deployment Specialists (1 Agent) - NEW!

| Agent | Skills | Responsibilities |
|-------|--------|-----------------|
| **render-deployer** 🔌 | 4 skills | Render.com backend deployment, PostgreSQL, cron jobs (MCP-enhanced) |

### Cross-Cutting Specialists (2 Agents)

| Agent | Skills | Responsibilities |
|-------|--------|-----------------|
| **fullstack-architect** | 8 skills | System design, architecture decisions, feature planning |
| **github-specialist** 🔌 | 3 skills | Git workflows, CI/CD, code review, branch management (MCP-enhanced) |

### NEW Specialists (5 Agents)

| Agent | Skills | Responsibilities |
|-------|--------|-----------------|
| **data-engineer** | 7 skills | Data pipelines, ETL/ELT, analytics infrastructure, BI integration |
| **technical-writer** | 4 skills | Technical documentation, user guides, API docs, tutorials |
| **cloud-architect** | 7 skills | Cloud infrastructure (AWS/GCP/Azure), Kubernetes, cloud migration |
| **api-architect** | 6 skills | API design, REST/GraphQL/gRPC, microservices communication |
| **product-manager** | 4 skills | Requirements gathering, user stories, roadmap planning, prioritization |

**Documentation:** See `.claude/agents/README.md` for complete agent reference.

---

## 🧠 Reusable Intelligence Skills

This project leverages **43 Reusable Intelligence Skills** organized in 7 categories:

**🔌 MCP-Enhanced Skills (3):** vercel-deployer, render-deployer, github-specialist

### 1️⃣ Workflow & Planning (5 skills)
- `new-feature` - Complete feature scaffolding (spec→plan→tasks)
- `change-management` - Manage changes to existing features
- `skill-creator` - Create new reusable skills
- `specify` - Create feature specifications
- `plan` - Generate implementation plans

### 2️⃣ Core Implementation - Phase III (5 skills)
- `mcp-tool-builder` - Build MCP tools for AI agent
- `ai-agent-setup` - Configure OpenAI Agents SDK
- `chatbot-endpoint` - Create stateless chat API endpoints
- `conversation-manager` - Manage conversation state in database
- `database-schema-expander` - Add new database tables

### 3️⃣ Foundation Patterns - Phase II (6 skills)
- `jwt-authentication` - JWT setup and protected endpoints
- `password-security` - Secure password hashing and auth
- `user-isolation` - Enforce data protection at query level
- `pydantic-validation` - Request/response DTOs
- `connection-pooling` - Database connection optimization
- `transaction-management` - Atomic database operations

### 4️⃣ Role-Based Development (7 skills)
- FTE agent skills: backend-developer, frontend-developer, fullstack-architect, database-engineer, devops-engineer, security-engineer, uiux-designer

### 5️⃣ Quality & Testing (3 skills)
- `edge-case-tester` - 57+ edge case scenarios
- `ab-testing` - A/B testing framework
- `qa-engineer` - Comprehensive testing

### 6️⃣ Production & Deployment (6 skills) 🔌
- `deployment-automation` - Automated deployment workflows
- `production-checklist` - Production readiness validation
- `structured-logging` - JSON logging infrastructure
- `performance-logger` - Execution time monitoring
- `vercel-deployer` 🔌 - Vercel platform deployment (MCP-enhanced)
- `render-deployer` 🔌 - Render.com backend deployment (MCP-enhanced, NEW!)

**Documentation:** See `.claude/skills/` directory for all skill implementations.

---

## ✨ Features

### Basic Level (Phase III Completed)

✅ **Task Management via Natural Language**
- Add tasks through conversation
- View all tasks or filter by status (pending/completed)
- Mark tasks as complete
- Update task details
- Delete tasks

✅ **AI-Powered Chatbot**
- Natural language understanding
- Context-aware responses
- Friendly confirmations
- Error handling with helpful messages

✅ **Voice-Enabled Chat Interface** 🎤
- **Speech-to-Text (STT)** - Record voice messages and convert to text
  - Push-to-talk interface (hold button to record)
  - Minimum recording duration: 0.5 seconds
  - OpenAI Whisper API integration
  - Real-time transcription with visual feedback
  - Error handling for short/empty recordings
- **Text-to-Speech (TTS)** - Listen to AI responses
  - Speaker button on each AI message
  - Natural voice synthesis with OpenAI TTS API
  - Playback controls (play/pause)
  - Audio caching for better performance
- **Mobile-Optimized** - Touch-friendly voice controls
  - Responsive design for all screen sizes
  - Visual recording indicators
  - Loading states during processing

✅ **User Authentication**
- Secure JWT-based authentication
- User isolation (users only see their tasks)
- Session management via database

✅ **Conversation History**
- Persistent conversation state
- Resume conversations after server restart
- Message history per conversation
- Conversation sidebar with search
- Timestamped messages

### Technical Features

✅ **MCP Tools (5 Tools)**
- `add_task` - Create new tasks
- `list_tasks` - Retrieve tasks with filtering
- `complete_task` - Mark tasks complete
- `delete_task` - Remove tasks
- `update_task` - Modify task details

✅ **Stateless Architecture**
- No server-side sessions
- Horizontally scalable
- Cloud-ready deployment

✅ **Comprehensive Testing**
- Unit tests for all components
- Integration tests for API endpoints
- 57+ edge case scenarios

---

## 📂 Project Structure

```
todo-chatbot-phase3/
├── .claude/                      # Claude Code configuration
│   ├── agents/                   # 🏭 Digital Agent Factory (17 FTE agents, 3 MCP-enhanced)
│   │   ├── README.md
│   │   ├── backend-developer.md
│   │   ├── frontend-developer.md
│   │   ├── fullstack-architect.md
│   │   ├── database-engineer.md
│   │   ├── devops-engineer.md
│   │   ├── security-engineer.md
│   │   ├── qa-engineer.md
│   │   ├── uiux-designer.md
│   │   ├── github-specialist.md
│   │   └── vercel-deployer.md
│   │
│   └── skills/                   # 🧠 Reusable Intelligence (43 skills, 3 MCP-enhanced)
│       ├── AB-Testing/
│       ├── AI-Agent-Setup/
│       ├── mcp-tool-builder/
│       ├── chatbot-endpoint/
│       └── ... (27 more)
│
├── .specify/                     # SpecKit Plus framework
│   ├── memory/
│   │   └── constitution.md       # 📜 Project principles (MANDATORY)
│   ├── templates/                # Spec, plan, task templates
│   └── scripts/                  # Automation scripts
│
├── backend/                      # FastAPI backend
│   ├── CLAUDE.md                 # Backend-specific development guide
│   ├── src/
│   │   ├── routes/               # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   └── chat.py
│   │   ├── services/             # Business logic
│   │   │   ├── task_service.py
│   │   │   └── conversation_service.py
│   │   ├── models/               # SQLModel database models
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── conversation.py
│   │   │   └── message.py
│   │   ├── schemas/              # Pydantic DTOs
│   │   ├── ai/                   # AI agent configuration
│   │   │   ├── agent_config.py
│   │   │   └── agent_factory.py
│   │   ├── mcp_tools/            # MCP tools (5 tools)
│   │   │   ├── __init__.py
│   │   │   ├── add_task_tool.py
│   │   │   ├── list_tasks_tool.py
│   │   │   ├── complete_task_tool.py
│   │   │   ├── delete_task_tool.py
│   │   │   └── update_task_tool.py
│   │   ├── db.py                 # Database connection
│   │   └── main.py               # FastAPI app entry point
│   ├── tests/                    # Backend tests
│   ├── alembic/                  # Database migrations
│   │   └── versions/
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/                     # Next.js frontend
│   ├── CLAUDE.md                 # Frontend-specific development guide
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   ├── chat/
│   │   └── tasks/
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui components
│   │   └── features/             # Feature-specific components
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # API client
│   │   └── auth.ts               # Auth helpers
│   ├── hooks/                    # Custom React hooks
│   ├── package.json
│   └── next.config.js
│
├── specs/                        # Feature specifications
│   └── chatbot/
│       ├── spec.md               # Feature requirements
│       ├── plan.md               # Implementation plan
│       └── tasks.md              # Actionable tasks
│
├── history/                      # Project history
│   ├── prompts/                  # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   ├── chatbot/
│   │   └── general/
│   └── adr/                      # Architecture Decision Records
│
├── CLAUDE.md                     # Root development guide ⭐
├── README.md                     # This file ⭐
└── docker-compose.yml            # Local development setup
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.13+
- **PostgreSQL** (or Neon Serverless DB account)
- **OpenAI API Key**
- **Better Auth Secret**
- **WSL 2** (Windows users)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your values:
# - DATABASE_URL (Neon PostgreSQL connection string)
# - OPENAI_API_KEY
# - BETTER_AUTH_SECRET
# - JWT_SECRET

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
# Backend runs at http://localhost:8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your values:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_OPENAI_DOMAIN_KEY (for ChatKit)
# - BETTER_AUTH_SECRET

# Start development server
npm run dev
# Frontend runs at http://localhost:3000
```

### Environment Variables

#### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql://user:password@host/database

# OpenAI
OPENAI_API_KEY=sk-...

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# MCP Server (optional)
MCP_SERVER_URL=http://localhost:8000
```

#### Frontend `.env.local`
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here  # Same as backend
```

---

## 💻 Development Workflow

### Spec-Driven Development

This project follows **Spec-Driven Development** principles:

1. **Specification First** - Every feature starts with a spec
2. **Plan Implementation** - Design approach before coding
3. **Task Breakdown** - Break into actionable tasks
4. **Implement with Agents** - Use appropriate FTE agents
5. **Use Skills** - Leverage reusable intelligence
6. **Test Thoroughly** - 57+ edge cases

### Agent-First Approach

```bash
# Example: Add new feature

1. Select Agent: /fullstack-architect
   - Plan feature architecture

2. Backend Implementation: /backend-developer
   - Skills: mcp-tool-builder, pydantic-validation, user-isolation

3. Frontend Implementation: /frontend-developer
   - Skills: vercel-deployer, ab-testing

4. Testing: /qa-engineer
   - Skills: edge-case-tester

5. Deployment: /devops-engineer
   - Skills: deployment-automation, production-checklist
```

### Constitution Enforcement

All development MUST follow constitution principles:
- ✅ **Agents are MANDATORY** - Select appropriate agent for every task
- ✅ **Skills are MANDATORY** - Use skills, don't implement manually
- ✅ **Stateless architecture** - No server-side sessions
- ✅ **User isolation** - Filter all queries by user_id
- ✅ **MCP-first design** - AI uses MCP tools only
- ✅ **Database-centric state** - All state in PostgreSQL

See `.specify/memory/constitution.md` for complete guidelines.

---

## 📚 Documentation

### Project Documentation Hierarchy

1. **Root CLAUDE.md** - Project-wide guidelines, all agents, all skills
2. **Backend CLAUDE.md** (`backend/CLAUDE.md`) - Backend-specific guide
3. **Frontend CLAUDE.md** (`frontend/CLAUDE.md`) - Frontend-specific guide
4. **Constitution** (`.specify/memory/constitution.md`) - Project principles
5. **Agent Factory** (`.claude/agents/README.md`) - All 17 FTE agents
6. **Skills Reference** (`.claude/skills/`) - All 31 reusable skills

### Quick Reference

**Working on backend?** → See `backend/CLAUDE.md`
**Working on frontend?** → See `frontend/CLAUDE.md`
**Need project context?** → See root `CLAUDE.md`
**Architecture decisions?** → See `history/adr/`
**Feature specs?** → See `specs/`

---

## 🔧 MCP Tools

The AI agent uses **5 MCP tools** to manage tasks:

### 1. add_task

**Purpose:** Create a new task

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier |
| title | string | Yes | Task title (1-200 chars) |
| description | string | No | Task description (max 1000 chars) |

**Returns:** `{ task_id, status, title }`

### 2. list_tasks

**Purpose:** Retrieve tasks from the list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier |
| status | string | No | Filter: "all", "pending", "completed" |

**Returns:** Array of task objects

### 3. complete_task

**Purpose:** Mark a task as complete

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier |
| task_id | integer | Yes | Task ID to complete |

**Returns:** `{ task_id, status, title }`

### 4. delete_task

**Purpose:** Remove a task from the list

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier |
| task_id | integer | Yes | Task ID to delete |

**Returns:** `{ task_id, status, title }`

### 5. update_task

**Purpose:** Modify task title or description

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier |
| task_id | integer | Yes | Task ID to update |
| title | string | No | New title |
| description | string | No | New description |

**Returns:** `{ task_id, status, title }`

---

## 🌐 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create new user account |
| POST | `/api/auth/login` | Login and get JWT token |

### Tasks (RESTful)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

### Chat (AI Agent)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message & get AI response |

**Request Body:**
```json
{
  "conversation_id": 123,  // Optional, creates new if not provided
  "message": "Add a task to buy groceries"
}
```

**Response:**
```json
{
  "conversation_id": 123,
  "response": "I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy groceries"},
      "result": {"task_id": 5, "status": "created"}
    }
  ]
}
```

### Voice Interface 🎤

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/voice/transcribe` | Convert speech to text (STT) |
| POST | `/api/voice/synthesize` | Convert text to speech (TTS) |

**Transcribe Request (multipart/form-data):**
```
audio: <audio-file>  // WebM, MP3, WAV format
```

**Transcribe Response:**
```json
{
  "text": "Add a task to buy groceries",
  "language": "en",
  "duration": 2.5
}
```

**Synthesize Request:**
```json
{
  "text": "I've added 'Buy groceries' to your tasks.",
  "voice": "alloy",  // Optional: alloy, echo, fable, onyx, nova, shimmer
  "speed": 1.0       // Optional: 0.25 to 4.0
}
```

**Synthesize Response:**
```
Content-Type: audio/mpeg
<audio-data>
```

---

## 🗄️ Database Schema

### Tables

#### users
Managed by Better Auth

| Column | Type | Constraints |
|--------|------|-------------|
| id | string | PRIMARY KEY |
| email | string | UNIQUE, NOT NULL |
| name | string | |
| created_at | timestamp | DEFAULT NOW() |

#### tasks

| Column | Type | Constraints |
|--------|------|-------------|
| id | integer | PRIMARY KEY, AUTO INCREMENT |
| user_id | string | FOREIGN KEY → users.id, NOT NULL |
| title | string | NOT NULL |
| description | text | NULLABLE |
| completed | boolean | DEFAULT FALSE |
| created_at | timestamp | DEFAULT NOW() |
| updated_at | timestamp | DEFAULT NOW() |

**Indexes:**
- `tasks.user_id` (for filtering by user)
- `tasks.completed` (for status filtering)

#### conversations

| Column | Type | Constraints |
|--------|------|-------------|
| id | integer | PRIMARY KEY, AUTO INCREMENT |
| user_id | string | FOREIGN KEY → users.id, NOT NULL |
| created_at | timestamp | DEFAULT NOW() |
| updated_at | timestamp | DEFAULT NOW() |

#### messages

| Column | Type | Constraints |
|--------|------|-------------|
| id | integer | PRIMARY KEY, AUTO INCREMENT |
| conversation_id | integer | FOREIGN KEY → conversations.id, NOT NULL |
| user_id | string | FOREIGN KEY → users.id, NOT NULL |
| role | string | NOT NULL ("user" or "assistant") |
| content | text | NOT NULL |
| created_at | timestamp | DEFAULT NOW() |

**Indexes:**
- `messages.conversation_id` (for fetching history)
- `messages.user_id` (for user isolation)

---

## 📜 Constitution & Principles

This project is governed by a **Constitution** (`.specify/memory/constitution.md`) that enforces:

### Core Principles

1. **Spec-Driven Development** (NON-NEGOTIABLE)
   - Every feature starts with a spec
   - No code without approved specification

2. **Agent-First Development** (MANDATORY)
   - All work done via FTE agents
   - Manual implementation = VIOLATION

3. **Skills-First Development** (MANDATORY)
   - Use reusable intelligence skills
   - Create new skills for missing capabilities
   - Manual implementation when skill exists = VIOLATION

4. **Stateless Architecture**
   - No server-side sessions
   - JWT authentication
   - All state in PostgreSQL

5. **User Isolation**
   - Filter all queries by user_id
   - Ownership checks before operations
   - Prevent horizontal privilege escalation

6. **MCP-First Design**
   - AI agent uses MCP tools only
   - Tools have proper contracts
   - Tools enforce user isolation

7. **Database-Centric State**
   - Conversations in database
   - Messages in database
   - Agent stateless (retrieves state per request)

8. **Security by Default**
   - bcrypt for passwords (cost factor 12)
   - JWT with strong secrets
   - HTTPS in production
   - Input validation on all endpoints

### Enforcement

- ✅ **PASS** - Agent-based, skill-based implementation
- ❌ **FAIL** - Manual implementation without agents/skills
- ⚠️ **Consequence** - Work must be redone using proper approach

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# All tests
pytest tests/ -v

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Component tests
npm run test

# E2E tests
npm run test:e2e

# With coverage
npm run test:coverage
```

### Edge Case Testing

Using `/sp.edge-case-tester` skill:
- ✅ 57+ edge case scenarios
- ✅ Empty inputs, null values
- ✅ SQL injection attempts
- ✅ XSS attempts
- ✅ Unicode characters
- ✅ Concurrent operations
- ✅ Database failures
- ✅ Network timeouts

---

## 🚢 Deployment

### Development

```bash
# Start both frontend and backend
docker-compose up
```

### Production

**Frontend:** Deployed on Vercel
**Backend:** FastAPI on cloud platform
**Database:** Neon Serverless PostgreSQL

See deployment guides:
- Backend: `backend/CLAUDE.md`
- Frontend: `frontend/CLAUDE.md`
- Production: `.specify/memory/constitution.md`

---

## 🎓 Learning Resources

### Documentation

- [Root CLAUDE.md](./CLAUDE.md) - Project-wide guidelines
- [Backend CLAUDE.md](./backend/CLAUDE.md) - Backend development
- [Frontend CLAUDE.md](./frontend/CLAUDE.md) - Frontend development
- [Constitution](./specify/memory/constitution.md) - Project principles
- [Agent Factory](./claude/agents/README.md) - All 17 FTE agents

### External Resources

- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents)
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

## 📝 Phase Progression

### ✅ Phase I - Console App (Completed)
- In-memory Python console app
- Basic CRUD operations

### ✅ Phase II - Full-Stack Web App (Completed)
- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Better Auth authentication

### ✅ Phase III - AI Chatbot (Current)
- Natural language interface
- OpenAI Agents SDK
- MCP tools (5 tools)
- Stateless chat endpoint
- Conversation history

### 🔜 Phase IV - Kubernetes Deployment (Next)
- Docker containerization
- Minikube local deployment
- Helm charts
- kubectl-ai, kagent

### 🔜 Phase V - Cloud Deployment (Future)
- DigitalOcean Kubernetes
- Kafka event streaming
- Dapr runtime
- Advanced features

---

## 👥 Contributing

This is a hackathon project following strict guidelines:

1. **Spec-Driven** - Create spec before implementation
2. **Agent-First** - Use appropriate FTE agent
3. **Skills-First** - Use or create skills
4. **Constitution-Compliant** - Follow all principles
5. **Well-Documented** - Update relevant CLAUDE.md files

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines.

---

## 📄 License

This project is part of **Panaversity Hackathon II**.

---

## 🙏 Acknowledgments

- **Panaversity** - For organizing the hackathon
- **PIAIC & GIAIC** - Educational support
- **Claude Code** - AI-powered development
- **SpecKit Plus** - Specification framework
- **OpenAI** - Agents SDK and ChatKit

---

## 📞 Contact

**Hackathon Submission:**
- [Submission Form](https://forms.gle/KMKEKaFUD6ZX4UtY8)
- Zoom Presentations: Sundays at 8:00 PM

---

## 🎯 Quick Start Commands

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Frontend
cd frontend && npm run dev

# Tests
cd backend && pytest tests/ -v

# Migrations
cd backend && alembic upgrade head
```

---

**Built with ❤️ using Spec-Driven Development, Agent-First Approach, and Reusable Intelligence**

🚀 **From Console to Cloud-Native AI** 🚀
