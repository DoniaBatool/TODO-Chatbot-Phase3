# Todo Hackathon Phase II Constitution      
<!-- Full-Stack Web Application with Persistent Storage -->

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
**All features must be specification-first:**
- Every feature starts with a complete specification document in `/specs` folder
- Specifications organized by type: features, api, database, ui
- Specifications must include user stories and acceptance criteria
- No code implementation without approved specification
- Claude Code must reference specifications during implementation
- Specs must be updated if requirements change
- Monorepo structure with layered CLAUDE.md files

### II. Full-Stack Code Quality Standards
**Code quality is mandatory across the stack:**

**Backend (Python/FastAPI):**
- Follow PEP 8 style guidelines strictly
- Type hints required for all function signatures
- Docstrings for all classes and public methods
- Maximum function length: 50 lines
- Single Responsibility Principle for all functions and classes

**Frontend (Next.js/TypeScript):**
- Follow TypeScript strict mode
- Use ESLint and Prettier configurations
- Server Components by default, Client Components only when needed
- Reusable component patterns
- Descriptive component and variable names

### III. Persistent Multi-User Storage
**Phase II requirement - database persistence:**
- All task data stored in Neon Serverless PostgreSQL
- SQLModel ORM for database operations
- User isolation - each user sees only their tasks
- Proper database migrations and schema management
- Connection pooling and efficient queries
- No hardcoded connection strings (use environment variables)

### IV. RESTful API Architecture
**Backend API standards:**
- All routes under `/api/` prefix
- Consistent endpoint naming: `/api/{user_id}/tasks`
- Use proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Pydantic models for request/response validation
- Proper HTTP status codes (200, 201, 400, 401, 404, 500)
- JWT token authentication on all endpoints
- Comprehensive error handling with HTTPException

### V. Authentication & Security
**Multi-user security is mandatory:**
- Better Auth for user signup/signin
- JWT tokens for API authentication
- Shared secret between frontend and backend (BETTER_AUTH_SECRET)
- User ID verification on every API request
- Task ownership enforcement (users only access their data)
- Token expiry and refresh mechanism
- No exposed secrets in code (use .env files)

### VI. Core Feature Completeness
**All 5 Basic Level features are mandatory as web application:**
1. **Add Task**: Create new todo via REST API with title and description
2. **Delete Task**: Remove task by ID via REST API
3. **Update Task**: Modify existing task details via REST API
4. **View Task List**: Display all tasks via REST API with filtering
5. **Mark as Complete**: Toggle completion status via REST API

Each feature must work end-to-end: Frontend UI → API → Database

## Technology Stack Requirements

### Mandatory Technologies
**Frontend:**
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth with JWT

**Backend:**
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Package Manager**: UV

**Database:**
- **Service**: Neon Serverless PostgreSQL
- **Schema Management**: SQLModel migrations

**Development:**
- **AI Tool**: Claude Code with Spec-Kit Plus
- **Version Control**: Git with meaningful commit messages
- **Monorepo**: Single repository for frontend and backend

### Monorepo Project Structure
```
/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── history/
│   ├── prompts/
│   └── adr/
├── frontend/
│   ├── CLAUDE.md
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── tasks/
│   ├── components/
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   └── next.config.js
├── backend/
│   ├── CLAUDE.md
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   └── tasks.py
│   ├── db.py
│   ├── auth.py
│   ├── pyproject.toml
│   └── tests/
├── docker-compose.yml
├── CLAUDE.md (root)
└── README.md
```

### Code Organization
**Backend Separation:**
- `models.py` - SQLModel database models (User, Task)
- `routes/` - API endpoint handlers
- `db.py` - Database connection and session management
- `auth.py` - JWT verification middleware
- `main.py` - FastAPI application entry point

**Frontend Separation:**
- `app/` - Next.js pages and layouts
- `components/` - Reusable React components
- `lib/api.ts` - API client with JWT token handling
- Server Components for static content
- Client Components for interactivity

## Development Workflow

### Specification Phase
1. Write feature specification in organized `/specs` structure:
   - `/specs/features/` - User stories and acceptance criteria
   - `/specs/api/` - REST endpoint specifications
   - `/specs/database/` - Schema and model definitions
   - `/specs/ui/` - Component and page specifications
2. Include user stories (As a user, I want...)
3. Define acceptance criteria (Given/When/Then)
4. Specify API contracts (request/response formats)
5. Get specification approved before coding

### Implementation Phase (Full-Stack)
1. Reference spec files with Claude Code:
   - `@specs/features/[feature].md` for feature requirements
   - `@specs/api/rest-endpoints.md` for API contracts
   - `@specs/database/schema.md` for database models
2. Implement backend first:
   - Database models (SQLModel)
   - API endpoints (FastAPI)
   - Authentication middleware
   - Write and run backend tests
3. Implement frontend:
   - API client configuration
   - React components
   - Page layouts and routing
   - Authentication flow
4. Test end-to-end workflow
5. Verify all acceptance criteria met

### Quality Gates
**Before considering a feature complete:**
- [ ] Specification documents exist (feature, api, database, ui)
- [ ] Backend API implemented and tested
- [ ] Frontend UI implemented and connected to API
- [ ] Authentication working correctly
- [ ] Database models created with proper relationships
- [ ] Code follows standards (PEP 8 for Python, ESLint for TypeScript)
- [ ] Type hints/types present in both frontend and backend
- [ ] Environment variables properly configured
- [ ] Manual end-to-end testing performed
- [ ] No bugs or edge cases remaining
- [ ] User can only access their own tasks

### Git Workflow
- Meaningful commit messages: `feat: add task creation API endpoint`
- Commit after each completed feature (backend + frontend)
- Keep commits atomic and focused
- Include spec files in repository
- Separate commits for backend and frontend when appropriate

## Constraints & Non-Goals

### In Scope for Phase II
- Basic task management as web application (add, delete, update, view, complete)
- Persistent storage in PostgreSQL database
- Multi-user support with authentication
- RESTful API architecture
- Responsive web interface
- Input validation and error handling
- User isolation and data security
- JWT-based authentication

### Out of Scope for Phase II
- ❌ No advanced features yet (priorities, tags, due dates, recurring tasks)
- ❌ No AI chatbot (Phase III)
- ❌ No Kubernetes deployment (Phase IV-V)
- ❌ No event-driven architecture (Phase V)
- ❌ No real-time sync across clients
- ❌ No file attachments or media
- ❌ No email notifications

### Database Schema Constraints

**users table (managed by Better Auth):**
- `id`: String (primary key, UUID)
- `email`: String (unique, required)
- `name`: String (optional)
- `created_at`: Timestamp (auto-generated)

**tasks table:**
- `id`: Integer (primary key, auto-incremented)
- `user_id`: String (foreign key → users.id, required)
- `title`: String (1-200 characters, required)
- `description`: Text (max 1000 characters, optional)
- `completed`: Boolean (default False)
- `created_at`: Timestamp (auto-generated)
- `updated_at`: Timestamp (auto-updated)

**Indexes:**
- `tasks.user_id` (for efficient filtering by user)
- `tasks.completed` (for status filtering)

## Error Handling Standards

### Backend API Error Handling
**HTTP Status Codes:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - User doesn't own the resource
- `404 Not Found` - Task or user not found
- `500 Internal Server Error` - Unexpected server errors

**Error Response Format:**
```json
{
  "detail": "Clear error message",
  "error_code": "TASK_NOT_FOUND"
}
```

### Frontend Error Handling
- Display user-friendly error messages (not raw API errors)
- Show loading states during API calls
- Handle network failures gracefully
- Provide retry mechanisms for failed requests
- Toast notifications for success/error feedback
- Form validation before API submission

### Input Validation
**Backend (FastAPI Pydantic):**
- Title: 1-200 characters, required
- Description: max 1000 characters, optional
- User ID: valid UUID format
- Task ID: positive integer

**Frontend (Client-side):**
- Pre-validate forms before submission
- Show inline validation errors
- Disable submit button during processing
- Clear error messages for users

### Security Error Handling
- Never expose database errors to frontend
- Log detailed errors server-side only
- Use try-except blocks appropriately
- Never expose JWT secrets or connection strings
- Rate limiting on authentication endpoints

## API Endpoint Specifications

### Required REST API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks for authenticated user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get specific task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle task completion |

### API Security Requirements
- All endpoints require `Authorization: Bearer <JWT_TOKEN>` header
- JWT token must be verified using BETTER_AUTH_SECRET
- User ID in URL must match authenticated user ID from token
- Return 401 if token missing or invalid
- Return 403 if user_id doesn't match token

### Request/Response Examples

**POST /api/{user_id}/tasks**
```json
Request: {
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
Response (201): {
  "id": 1,
  "user_id": "user-uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

## Governance

### Constitution Authority
- This constitution supersedes all other development practices
- All Claude Code interactions must reference and follow these principles
- Deviations require documented justification
- Root and layered CLAUDE.md files must reference this constitution
- Monorepo structure must be maintained

### Acceptance Criteria
**Phase II is complete when:**
1. ✅ All 5 Basic Level features implemented as web application
2. ✅ Backend API with all required endpoints functional
3. ✅ Frontend Next.js application with responsive UI
4. ✅ Better Auth authentication working (signup/signin)
5. ✅ JWT token verification on all API endpoints
6. ✅ User isolation enforced (users only see their tasks)
7. ✅ Neon PostgreSQL database connected and working
8. ✅ SQLModel models created with proper relationships
9. ✅ All tests passing (backend and frontend)
10. ✅ Code meets quality standards (PEP 8, ESLint)
11. ✅ Environment variables properly configured
12. ✅ README.md includes setup instructions for both frontend and backend
13. ✅ CLAUDE.md files at root, frontend, and backend levels
14. ✅ specs folder contains organized specifications (features, api, database, ui)
15. ✅ Application deployed to Vercel (frontend) and accessible via public URL

### Success Metrics
- ✅ Frontend and backend run without errors
- ✅ All CRUD operations functional via web interface
- ✅ Users can signup, signin, and manage only their tasks
- ✅ Authentication and authorization working correctly
- ✅ Database persistence working (data survives server restart)
- ✅ Responsive UI works on desktop and mobile
- ✅ Clean, maintainable monorepo codebase
- ✅ Complete documentation for both frontend and backend
- ✅ API endpoints follow REST conventions
- ✅ Ready for demo video (under 90 seconds)
- ✅ Deployed and accessible online

### Deployment Requirements
**Frontend (Vercel):**
- Environment variables: `BETTER_AUTH_SECRET`, `NEXT_PUBLIC_API_URL`
- Build succeeds without errors
- Public URL accessible

**Backend (Python hosting or containerized):**
- Environment variables: `DATABASE_URL`, `BETTER_AUTH_SECRET`
- FastAPI app runs and serves API requests
- Accessible from frontend (CORS configured)

**Database (Neon):**
- PostgreSQL database provisioned
- Tables created via SQLModel migrations
- Connection string secured in environment variables

**Version**: 3.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09