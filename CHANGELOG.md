# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 3: AI-Powered Todo Chatbot

#### Added
- **AI Chat Endpoint** (`POST /api/{user_id}/chat`)
  - Stateless conversational interface for task management
  - Natural language processing via OpenAI Agents SDK
  - Conversation history persistence with user isolation
  - Support for multi-turn conversations

- **MCP Tools** (Model Context Protocol)
  - `add_task` - Create tasks via natural language
  - `list_tasks` - View tasks with status filtering
  - `complete_task` - Mark tasks as complete
  - `update_task` - Modify task details
  - `delete_task` - Remove tasks

- **Conversation Management**
  - Database models for Conversations and Messages
  - ConversationService for CRUD operations
  - Message history with chronological ordering
  - Automatic timestamp tracking

- **AI Agent Infrastructure**
  - OpenAI Agents SDK integration
  - Tool registration and orchestration
  - System prompt for task management assistant
  - Agent runner with error handling

- **Performance & Observability**
  - Production-ready connection pooling (pool_size=10, max_overflow=20)
  - Performance logging utilities with execution time tracking
  - Structured JSON logging for all services
  - Health endpoint with connection pool status
  - Load testing framework (target: p95 < 3s)

- **Error Handling & Resilience**
  - OpenAI API timeout handling with user-friendly messages
  - Database retry logic with exponential backoff
  - Input sanitization (message length limit: 10,000 chars)
  - Comprehensive error logging with context

#### Changed
- Database connection pool settings optimized for production load
- Health endpoint enhanced with pool metrics
- All service methods instrumented with performance logging
- Logging format changed to structured JSON for aggregation tools

#### Security
- User isolation enforced across all chat operations
- Path user_id validation against JWT claims
- Input sanitization for chat messages
- Cross-user data leakage prevention

#### Performance
- Connection pooling: 30 total connections (10 baseline + 20 overflow)
- Performance targets: p95 < 3s for chat endpoint, p95 < 100ms for DB queries
- Structured logging with minimal performance impact
- Efficient conversation history pagination (limit: 50 messages)

## [0.1.0] - 2024-12-30

### Phase 2: Backend API Foundation

#### Added
- FastAPI application with CORS configuration
- PostgreSQL database with SQLModel ORM
- Alembic database migrations
- User and Task models with relationships
- JWT authentication system
- Protected task API endpoints (CRUD operations)
- Health check endpoint
- Global error handling middleware
- Environment-based configuration

#### Security
- Password hashing with bcrypt
- JWT token-based authentication
- User isolation for all task operations
- Input validation with Pydantic

---

## Deployment Notes

### Phase 3 Requirements
- Python 3.13+
- PostgreSQL 14+
- OpenAI API key
- Environment variables (see `.env.example`)

### New Dependencies
- `openai>=1.12.0` - OpenAI Agents SDK
- `mcp>=0.1.0` - Model Context Protocol
- `python-json-logger>=2.0.7` - Structured logging

### Migration
```bash
# Run Phase 3 migrations
alembic upgrade head

# Verify conversations and messages tables created
psql -d your_database -c "\dt"
```

### Configuration
```bash
# Required environment variables
OPENAI_API_KEY=sk-...
OPENAI_AGENT_MODEL=gpt-4o

# Optional performance tuning
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

---

**Contributors**: AI Chatbot Team (Phase 3 Hackathon)
**License**: MIT
