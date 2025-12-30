# Todo App - Phase I ✅ / Phase II ✅

A command-line todo list manager built with Python following **Spec-Driven Development** principles.

## 🎯 Project Overview

This repo now includes **Phase I (console)** and **Phase II (full-stack web)** of the Todo Hackathon project. Phase I delivers the in-memory CLI app; Phase II upgrades to a multi-user web app with FastAPI, Next.js, and Neon Postgres. Both phases follow Spec-Driven Development, TDD, and Spec-Kit Plus.

**GitHub Repository**: https://github.com/DoniaBatool/TODO-phase1

## ✨ Features

### Phase II - Full-Stack Web App (Current)
- ✅ FastAPI backend with SQLModel + Neon Postgres
- ✅ JWT authentication (signup/login/me)
- ✅ Protected task API (user isolation & ownership checks)
- ✅ Next.js (App Router) frontend with auth + task CRUD
- ✅ Tailwind UI, loading/empty/error states

### Phase I - Basic Level Features (Console)
- ✅ **Add Task**: Create new todo items with title and description
- ✅ **View Tasks**: Display all tasks with status indicators
- ✅ **Update Task**: Modify existing task details
- ✅ **Mark Complete**: Toggle task completion status
- ✅ **Delete Task**: Remove tasks from the list

## 🛠️ Technology Stack

**Phase II**
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI, SQLModel, Pydantic
- DB: Neon Serverless PostgreSQL
- Auth: JWT (PyJWT), bcrypt, Better Auth compatible secret
- Tooling: uv, npm, pytest, Alembic, Ruff

**Phase I**
- Language: Python 3.13+
- Package Manager: UV
- Development: Claude Code + Spec-Kit Plus
- Testing: pytest with coverage
- Storage: In-memory (Python data structures)

## 📁 Project Structure (Phase II)

```
.
├── backend/           # FastAPI app (JWT auth + protected tasks)
├── frontend/          # Next.js App Router UI (auth + tasks CRUD)
├── specs/             # Spec-Kit Plus docs for all phases/features
├── history/prompts/   # Prompt History Records (PHRs)
└── .specify/          # Spec-Kit templates and constitution
```

### Phase I (console) structure is described in SPEC-KIT-PLUS.md (retained for history).

```
todo/
├── .specify/                    # Spec-Kit Plus framework
│   ├── memory/
│   │   └── constitution.md      # Project principles and standards
│   ├── templates/               # Documentation templates
│   └── scripts/                 # Automation scripts
├── .claude/
│   └── commands/                # 11 custom slash commands
├── specs/                       # 42 specification files
│   ├── README.md                # Specs guide
│   ├── 1-add-task/              # Feature 1: Complete docs
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── research.md
│   │   ├── data-model.md
│   │   ├── quickstart.md
│   │   ├── contracts/
│   │   └── checklists/
│   ├── 2-view-tasks/            # Feature 2: Complete docs
│   ├── 3-update-task/           # Feature 3: Complete docs
│   ├── 4-mark-complete/         # Feature 4: Complete docs
│   └── 5-delete-task/           # Feature 5: Complete docs
├── history/
│   └── prompts/                 # 20 Prompt History Records
│       ├── add-task/            # 4 PHR files
│       ├── view-tasks/          # 4 PHR files
│       ├── update-task/         # 4 PHR files
│       ├── mark-complete/       # 4 PHR files
│       └── delete-task/         # 4 PHR files
├── src/
│   └── todo/
│       ├── __init__.py
│       ├── task.py              # Task model with validation (71 lines)
│       ├── manager.py           # Task CRUD operations (151 lines)
│       ├── cli.py               # Command-line interface (262 lines)
│       └── main.py              # Application entry point (24 lines)
├── tests/                       # 43 tests (100% passing)
│   ├── test_task.py             # 13 task model tests
│   ├── test_manager.py          # 22 manager tests
│   └── test_cli.py              # 8 CLI structure tests
├── pyproject.toml               # Project configuration
├── CLAUDE.md                    # Claude Code instructions
├── SPEC-KIT-PLUS.md             # Retrofit documentation
└── README.md                    # This file
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.13 or higher
- UV package manager (optional but recommended)
- WSL 2 (for Windows users)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/DoniaBatool/TODO-phase1.git
cd TODO-phase1
```

2. **Install UV (if not already installed)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Create virtual environment and install dependencies**
```bash
# Using UV
uv venv
source .venv/bin/activate  # On Windows WSL/Linux
# .venv\Scripts\activate   # On Windows CMD

uv pip install -e ".[dev]"
```

Or using standard Python:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 🎮 Usage

### Run the Application

```bash
# Using the installed command
todo

# Or run directly
python -m src.todo.main
```

### Main Menu
```
==================================================
           TODO LIST MANAGER
==================================================
1. Add Task
2. View All Tasks
3. Update Task
4. Mark Task Complete/Incomplete
5. Delete Task
6. Exit
==================================================
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=src/todo --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_task.py
pytest tests/test_manager.py
pytest tests/test_cli.py
```

### View Coverage Report
```bash
# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 📊 Test Coverage

**Target**: 80%+ code coverage ✅ **ACHIEVED**

**Current Status**: 43/43 tests passing (100%)

Coverage includes:
- ✅ Task model validation (13 tests)
- ✅ Task manager CRUD operations (22 tests)
- ✅ CLI structure validation (8 tests)
- ✅ Error handling scenarios
- ✅ Edge cases (empty input, max length, etc.)
- ✅ ID-never-reused guarantee
- ✅ Input validation loops

## 🎯 Data Model

### Task Entity
```python
@dataclass
class Task:
    id: int              # Auto-incremented unique identifier
    title: str           # 1-200 characters, required
    description: str     # Max 1000 characters, optional
    completed: bool      # Default: False
    created_at: datetime # Auto-generated timestamp
```

## 🔧 Development Guidelines

### Code Standards
- Follow PEP 8 style guidelines
- Type hints required for all functions
- Docstrings for all classes and public methods
- Maximum function length: 50 lines
- Single Responsibility Principle

### Test-Driven Development
1. Write tests first (Red)
2. Implement feature (Green)
3. Refactor while keeping tests green
4. Maintain 80%+ coverage

### Git Workflow
```bash
git add .
git commit -m "feat: add task creation functionality"
git push
```

## 📝 Specification-Driven Development

All features are implemented following detailed specifications in the `specs/` directory:

1. Read specification: `specs/features/[feature].md`
2. Write tests based on spec test cases
3. Implement feature according to technical spec
4. Verify all acceptance criteria met

## ❌ Out of Scope (Phase I)

- ❌ File persistence
- ❌ Database integration
- ❌ Multi-user support
- ❌ Advanced features (priorities, tags, due dates)
- ❌ Web interface
- ❌ Authentication

## 🐛 Known Issues

None! All features are working correctly. ✅

## 📈 Project Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Files** | 102 files | ✅ |
| **Total Lines of Code** | 15,763 lines | ✅ |
| **Documentation Files** | 62 files (42 specs + 20 PHRs) | ✅ |
| **Implementation Files** | 5 Python modules | ✅ |
| **Test Files** | 3 test modules | ✅ |
| **Tests Passing** | 43/43 (100%) | ✅ |
| **Features Complete** | 5/5 (100%) | ✅ |
| **Spec-Kit Plus Compliance** | 100% | ✅ |
| **Code Coverage** | >80% | ✅ |

## 🏆 Spec-Kit Plus Compliance

This project follows the **Spec-Kit Plus** workflow:

✅ **Constitution** - Project principles documented  
✅ **Specifications** - Complete spec.md for each feature  
✅ **Planning** - Detailed plan.md with architecture decisions  
✅ **Task Breakdown** - tasks.md with executable steps  
✅ **Research** - Technical decisions documented  
✅ **Contracts** - API contracts defined  
✅ **Data Models** - Entity definitions documented  
✅ **Prompt History** - 20 PHR files (4 per feature)  
✅ **Quality Checklists** - Requirements validated  

**Total Documentation**: 62 professional-grade documents

## 📚 Documentation

### Core Documents
- **Constitution**: `.specify/memory/constitution.md` - Core principles (187 lines)
- **Specifications**: `specs/` - 42 feature specification files
- **Prompt History**: `history/prompts/` - 20 PHR files documenting workflow
- **Claude Instructions**: `CLAUDE.md` - Development guidelines
- **Spec-Kit Plus**: `SPEC-KIT-PLUS.md` - Retrofit documentation (415 lines)
- **Hackathon Guide**: `Hackathon II - Todo Spec-Driven Development.md`

### Feature Documentation (Per Feature)
Each feature has complete documentation:
- `spec.md` - Requirements and acceptance criteria
- `plan.md` - Implementation plan and architecture
- `tasks.md` - Task breakdown with test cases
- `research.md` - Technical decisions and rationale
- `data-model.md` - Entity definitions
- `quickstart.md` - Quick start guide
- `contracts/` - API contracts and interfaces
- `checklists/` - Quality requirements checklist

## 🎓 Learning Objectives

This project demonstrates mastery of:
- ✅ Spec-Driven Development with Claude Code and Spec-Kit Plus
- ✅ Test-Driven Development (TDD) - Tests written before implementation
- ✅ Clean code principles (PEP 8, type hints, docstrings)
- ✅ Python project structure and packaging
- ✅ Command-line interface design with interactive menus
- ✅ Input validation and error handling with retry loops
- ✅ Professional documentation standards
- ✅ Git workflow and version control
- ✅ Comprehensive test coverage (>80%)
- ✅ Architecture decision documentation

## 🚀 Next Steps (Phase II)

- Full-stack web application with Next.js
- FastAPI backend
- PostgreSQL database (Neon)
- User authentication
- RESTful API

## 📄 License

This project is created for educational purposes as part of the Panaversity Hackathon II.

## 👤 Author

**Donia Batool**  
GitHub: [@DoniaBatool](https://github.com/DoniaBatool)

---

## 🎯 Submission Information

**Phase**: I (Complete) ✅  
**Status**: Ready for Submission 🚀  
**Version**: 1.0.0  
**Last Updated**: December 9, 2025  
**Repository**: https://github.com/DoniaBatool/TODO-phase1  

### Submission Checklist
- ✅ All 5 features implemented and working
- ✅ 43 tests passing (100%)
- ✅ Complete Spec-Kit Plus documentation (62 files)
- ✅ Code follows PEP 8 and clean code principles
- ✅ Git repository with meaningful commits
- ✅ Professional README with setup instructions
- ✅ Ready for Phase II

---

**Built with ❤️ using Spec-Driven Development**

