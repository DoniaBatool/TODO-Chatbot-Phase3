# Backend Development Guide

This directory contains the FastAPI backend application for the Todo Chatbot Phase 3 project.

## Overview

**Technology Stack:**
- FastAPI (Python web framework)
- SQLModel (ORM with Pydantic integration)
- PostgreSQL (Database)
- Alembic (Database migrations)
- OpenAI Agents SDK (AI chatbot)
- pytest (Testing)

## Architecture

### Stateless Design
- No server-side session storage
- JWT-based authentication
- All state in PostgreSQL database
- Horizontally scalable

### Directory Structure

```
backend/
├── src/
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── models/          # SQLModel database models
│   ├── schemas/         # Pydantic DTOs
│   ├── ai/              # AI agent configuration
│   ├── mcp_tools/       # MCP tools for AI agent
│   └── db.py            # Database connection
├── tests/               # Test suites
├── alembic/             # Database migrations
└── requirements.txt     # Python dependencies
```

## 🤖 Backend Specialized Agents (9 Total - EXPANDED!)

These FTE agents are specialized for backend development tasks:

### Core Backend Agents (5)

### 1. Backend Developer (`/backend-developer`)
**Primary Agent for Backend Work**

**Skills Available (11):**
- `/sp.jwt-authentication` - JWT token creation/verification
- `/sp.password-security` - bcrypt password hashing
- `/sp.pydantic-validation` - Request/response DTOs
- `/sp.connection-pooling` - Database connection optimization
- `/sp.transaction-management` - Atomic database operations
- `/sp.database-schema-expander` - Add new database tables
- `/sp.mcp-tool-builder` - Build MCP tools for AI
- `/sp.chatbot-endpoint` - Stateless chat API endpoints
- `/sp.conversation-manager` - Conversation state management
- `/sp.api-docs-generator` - OpenAPI documentation
- `/sp.user-isolation` - Data protection at query level

**Use for:**
- API endpoint implementation
- Authentication and authorization
- MCP tool development
- Business logic services
- API documentation

---

### 2. Database Engineer (`/database-engineer`)
**Database Specialist**

**Skills Available (4):**
- `/sp.database-schema-expander` - Schema design and migrations
- `/sp.connection-pooling` - Connection pool optimization
- `/sp.transaction-management` - Transaction handling
- `/sp.user-isolation` - Row-level security

**Use for:**
- Database schema design
- SQLModel model definitions
- Alembic migrations
- Query optimization
- Index strategy

---

### 3. Security Engineer (`/security-engineer`)
**Security & Compliance Specialist**

**Skills Available (5):**
- `/sp.jwt-authentication` - Secure JWT implementation
- `/sp.password-security` - Password hashing best practices
- `/sp.user-isolation` - Prevent data leakage
- `/sp.edge-case-tester` - Security edge cases
- `/sp.pydantic-validation` - Input validation

**Use for:**
- OWASP Top 10 compliance
- Security audits
- Authentication/authorization security
- Input validation
- Penetration testing

---

### 4. QA Engineer (`/qa-engineer`)
**Backend Testing Specialist**

**Skills Available (3):**
- `/sp.edge-case-tester` - 57+ edge case scenarios
- `/sp.ab-testing` - A/B testing framework
- `/sp.production-checklist` - Production validation

**Use for:**
- Unit tests (pytest)
- Integration tests (API endpoints)
- Edge case testing
- Load testing
- Test coverage analysis

---

### 5. DevOps Engineer (`/devops-engineer`)
**Infrastructure & Deployment**

**Skills Available (5):**
- `/sp.deployment-automation` - Automated deployments
- `/sp.production-checklist` - Production readiness
- `/sp.structured-logging` - JSON logging infrastructure
- `/sp.performance-logger` - Execution time monitoring
- `/sp.render-deployer` 🔌 - Render.com deployment (MCP-enhanced, NEW!)

**Use for:**
- Docker containerization
- Alembic migrations in CI/CD
- Monitoring and logging
- Health checks
- Production deployment
- Backend deployment to Render.com with MCP automation

---

### 🆕 NEW Backend Specialists (4)

### 6. Data Engineer (`/data-engineer`)
**Data Pipeline & Analytics Specialist**

**Skills Available (7):**
- `/sp.database-engineer` - Database optimization
- `/sp.performance-logger` - Performance monitoring
- `/sp.structured-logging` - Pipeline logging
- `/sp.message-queue-integration` - Async data processing
- `/sp.observability-apm` - Pipeline monitoring
- `/sp.microservices-patterns` - Distributed processing
- `/sp.caching-strategy` - Data caching

**Use for:**
- ETL/ELT pipeline development
- Data warehouse design
- Analytics infrastructure
- Real-time data processing
- BI tool integration

---

### 7. Cloud Architect (`/cloud-architect`)
**Cloud Infrastructure Specialist**

**Skills Available (7):**
- `/sp.infrastructure-as-code` - Terraform/CloudFormation
- `/sp.container-orchestration` - Kubernetes deployment
- `/sp.deployment-automation` - CI/CD pipelines
- `/sp.observability-apm` - Cloud monitoring
- `/sp.security-engineer` - Cloud security
- `/sp.devops-engineer` - DevOps practices
- `/sp.caching-strategy` - CDN and caching

**Use for:**
- AWS/GCP/Azure architecture
- Kubernetes cluster setup
- Infrastructure as Code (Terraform)
- Cloud migration planning
- Cost optimization

---

### 8. API Architect (`/api-architect`)
**API Design & Microservices Specialist**

**Skills Available (6):**
- `/sp.api-contract-design` - OpenAPI specifications
- `/sp.graphql-api` - GraphQL implementation
- `/sp.api-docs-generator` - API documentation
- `/sp.microservices-patterns` - Microservices communication
- `/sp.backend-developer` - API implementation
- `/sp.observability-apm` - API monitoring

**Use for:**
- API contract design (OpenAPI)
- REST/GraphQL/gRPC architecture
- API versioning strategy
- Microservices communication
- API gateway configuration

---

### 9. Technical Writer (`/technical-writer`)
**Backend Documentation Specialist**

**Skills Available (4):**
- `/sp.api-docs-generator` - API reference docs
- `/sp.backend-developer` - Code examples
- `/sp.database-engineer` - Schema documentation
- Architecture documentation

**Use for:**
- API documentation
- Architecture decision records
- Database schema docs
- Developer guides
- Release notes

---

## 🧠 Backend Skills Summary (24 Total)

### Foundation Patterns (6)
- jwt-authentication, password-security, user-isolation
- pydantic-validation, connection-pooling, transaction-management

### Core Implementation (5)
- mcp-tool-builder, chatbot-endpoint, conversation-manager
- database-schema-expander, api-docs-generator

### 🆕 Modern Architecture (10 NEW!)
- caching-strategy, api-contract-design, message-queue-integration
- observability-apm, microservices-patterns, infrastructure-as-code
- feature-flags-management, websocket-realtime, graphql-api
- container-orchestration

### Quality & Deployment (3)
- edge-case-tester, deployment-automation, production-checklist

---

## 🎯 Common Backend Workflows

### Workflow 1: Add New API Endpoint

```
Pipeline:
1. /backend-developer → Design endpoint with Pydantic DTOs
2. /database-engineer → Check if schema changes needed
3. /security-engineer → Validate input validation and auth
4. /backend-developer → Implement endpoint logic
5. /qa-engineer → Write tests (unit + integration)
6. /backend-developer → Generate API documentation
```

**Skills Used:**
- `pydantic-validation` - Request/response DTOs
- `jwt-authentication` - Protected endpoint
- `user-isolation` - User-specific data access
- `edge-case-tester` - Comprehensive testing
- `api-docs-generator` - OpenAPI docs

---

### Workflow 2: Add New Database Table

```
Pipeline:
1. /database-engineer → Design schema with SQLModel
2. /database-engineer → Create Alembic migration
3. /backend-developer → Create CRUD service
4. /security-engineer → Add user isolation checks
5. /qa-engineer → Test migrations and queries
```

**Skills Used:**
- `database-schema-expander` - Schema + migration
- `transaction-management` - Atomic operations
- `user-isolation` - Row-level security
- `edge-case-tester` - Database edge cases

---

### Workflow 3: Add Authentication

```
Pipeline:
1. /security-engineer → Design auth strategy
2. /backend-developer → Implement JWT + password security
3. /database-engineer → Users table with user isolation
4. /qa-engineer → Security edge case testing
5. /devops-engineer → Environment variables setup
```

**Skills Used:**
- `jwt-authentication` - JWT creation/verification
- `password-security` - bcrypt hashing
- `user-isolation` - Data protection
- `edge-case-tester` - Auth edge cases

---

### Workflow 4: Add MCP Tool for AI Agent

```
Pipeline:
1. /backend-developer → Build MCP tool with contracts
2. /database-engineer → Optimize queries if needed
3. /security-engineer → Validate user isolation
4. /qa-engineer → Test tool with edge cases
5. /backend-developer → Register tool with agent
```

**Skills Used:**
- `mcp-tool-builder` - MCP tool implementation
- `user-isolation` - User-specific operations
- `pydantic-validation` - Input validation
- `edge-case-tester` - Tool testing

---

### Workflow 5: Prepare for Production

```
Pipeline:
1. /security-engineer → Security audit (OWASP)
2. /database-engineer → Connection pooling optimization
3. /devops-engineer → Structured logging setup
4. /devops-engineer → Performance monitoring
5. /qa-engineer → Load testing (100 concurrent users)
6. /devops-engineer → Production checklist validation
```

**Skills Used:**
- `connection-pooling` - Database optimization
- `structured-logging` - JSON logging
- `performance-logger` - Execution time tracking
- `production-checklist` - Deployment validation
- `ab-testing` - Load testing

---

## 📋 Backend Development Checklist

### For Every New API Endpoint:
- [ ] Pydantic request/response DTOs defined
- [ ] JWT authentication if protected endpoint
- [ ] User isolation enforced (user_id filtering)
- [ ] Input validation with Pydantic
- [ ] Error handling with proper status codes
- [ ] OpenAPI documentation generated
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Edge cases tested (57+ scenarios)

### For Every Database Change:
- [ ] SQLModel models defined
- [ ] Alembic migration created
- [ ] Foreign key constraints defined
- [ ] Indexes on frequently queried columns
- [ ] User isolation enforced at query level
- [ ] Transaction management for writes
- [ ] Migration tested (upgrade + downgrade)
- [ ] Backward compatible

### For Security:
- [ ] No secrets in code (use .env)
- [ ] JWT with strong secret key
- [ ] Password hashing with bcrypt (cost factor 12)
- [ ] User isolation on all user data queries
- [ ] Input validation with Pydantic
- [ ] OWASP Top 10 compliance checked
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention (output encoding)

### For Production:
- [ ] Connection pooling configured (size 5-20)
- [ ] Structured logging enabled (JSON format)
- [ ] Performance monitoring active
- [ ] Health check endpoint working
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] Rate limiting considered

---

## 🔧 Backend Skills Reference

### Phase 2 Foundation Skills (6)
Essential patterns from Phase 2:
1. `/sp.jwt-authentication` - JWT setup
2. `/sp.password-security` - Password hashing
3. `/sp.user-isolation` - Data protection
4. `/sp.pydantic-validation` - Input validation
5. `/sp.connection-pooling` - Database optimization
6. `/sp.transaction-management` - Atomicity

### Phase 3 Core Skills (5)
New Phase 3 capabilities:
1. `/sp.mcp-tool-builder` - MCP tools for AI
2. `/sp.chatbot-endpoint` - Stateless chat API
3. `/sp.conversation-manager` - Chat state management
4. `/sp.database-schema-expander` - Schema evolution
5. `/sp.api-docs-generator` - OpenAPI docs

### Testing & Quality Skills (3)
1. `/sp.edge-case-tester` - 57+ edge cases
2. `/sp.ab-testing` - A/B testing + load testing
3. `/sp.production-checklist` - Deployment validation

### Production & Monitoring Skills (4)
1. `/sp.deployment-automation` - CI/CD automation
2. `/sp.structured-logging` - JSON logging
3. `/sp.performance-logger` - Execution time tracking
4. `/sp.production-checklist` - Readiness validation

---

## 🏗️ Constitution Principles for Backend

All backend development MUST follow:

### 1. Stateless Architecture
- ✅ No server-side session storage
- ✅ JWT for authentication (expires in 1 week)
- ✅ All state in PostgreSQL database
- ✅ Horizontally scalable design

### 2. User Isolation
- ✅ Filter all queries by user_id
- ✅ Ownership checks before operations
- ✅ Prevent horizontal privilege escalation
- ✅ Row-level security enforced

### 3. MCP-First Design
- ✅ AI agent uses MCP tools only
- ✅ Tools have proper contracts
- ✅ Tools validate input with Pydantic
- ✅ Tools enforce user isolation

### 4. Database-Centric State
- ✅ Conversations stored in database
- ✅ Messages stored in database
- ✅ Agent has no memory (stateless)
- ✅ State retrieved from DB per request

### 5. Security by Default
- ✅ bcrypt for passwords (cost factor 12)
- ✅ JWT with strong secrets
- ✅ HTTPS in production
- ✅ Input validation on all endpoints
- ✅ OWASP Top 10 compliance

---

## 🚀 Quick Start

### Development Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your values

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Create New Migration
```bash
# Auto-generate migration
alembic revision --autogenerate -m "Description"

# Manual migration
alembic revision -m "Description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 📚 Additional Resources

- **Root CLAUDE.md**: Project-wide guidelines and all agents
- **Frontend CLAUDE.md**: `../frontend/CLAUDE.md` for frontend-specific guides
- **Constitution**: `.specify/memory/constitution.md` for project principles
- **API Docs**: `http://localhost:8000/docs` when server running
- **Skills Directory**: `../.claude/skills/` for all reusable skills
- **Agents Directory**: `../.claude/agents/` for all FTE agents

---

## 🎯 Remember

**Before implementing ANY backend feature:**
1. ✅ Check which agents apply
2. ✅ Check which skills apply
3. ✅ Display skill plan in terminal
4. ✅ Wait for user approval
5. ✅ Execute using identified skills

**Skills are MANDATORY - not optional!**

Manual implementation when skill exists = VIOLATION of project guidelines.

---

**Backend Development** - Powered by Reusable Intelligence 🚀
