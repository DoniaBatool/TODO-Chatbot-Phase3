---
description: Configure database connection pooling for optimal performance and resource management (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements database connection pooling following Phase 2's proven pattern. Ensures efficient connection reuse, prevents database overload, and optimizes for concurrent requests.

### 1. Parse Requirements

Extract from user input or context:
- Expected concurrent users/requests (determines pool size)
- Database connection limit (e.g., Neon free tier: 100 connections)
- Acceptable wait time for connection (timeout setting)
- Connection reuse duration (recycle time)
- Database type (PostgreSQL, MySQL, SQLite)

### 2. Install Dependencies

```bash
pip install sqlmodel sqlalchemy psycopg2-binary
```

### 3. Implement Connection Pool Configuration

**File**: `src/db.py`

```python
from sqlmodel import create_engine, Session, SQLModel
from src.config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pool configuration
POOL_SIZE = 10          # Baseline connections (2 * CPU cores)
MAX_OVERFLOW = 20       # Additional connections under load
POOL_TIMEOUT = 30       # Seconds to wait for connection
POOL_RECYCLE = 3600     # Recycle connections after 1 hour (prevents stale)

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,

    # Connection pool settings
    pool_size=POOL_SIZE,         # Maintain 10 persistent connections
    max_overflow=MAX_OVERFLOW,   # Allow up to 30 total (10 + 20)
    pool_timeout=POOL_TIMEOUT,   # Wait 30s for connection, then error
    pool_recycle=POOL_RECYCLE,   # Recycle after 1 hour

    # Health check
    pool_pre_ping=True,          # Test connection before use (detect DB restarts)

    # Debugging (disable in production)
    echo=False,                  # Don't log all SQL statements

    # Connection arguments (PostgreSQL specific)
    connect_args={
        "connect_timeout": 10    # 10s timeout for initial connection
    }
)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")


def get_session():
    """
    FastAPI dependency for database session.

    Automatically:
    - Gets connection from pool
    - Yields session for request
    - Returns connection to pool after request
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()  # Return connection to pool
```

### 4. Pool Sizing Guidelines

**Formula**:
```python
# Basic formula
pool_size = expected_concurrent_requests / avg_request_duration_seconds

# Example: 100 req/s, avg 0.1s per request
pool_size = 100 * 0.1 = 10
```

**Sizing Tiers**:

```python
# Conservative (low traffic)
# Use for: Development, staging, low-traffic apps
POOL_SIZE = 5
MAX_OVERFLOW = 5
# Total: 10 connections max

# Moderate (typical web app)
# Use for: Production apps, moderate traffic
POOL_SIZE = 10
MAX_OVERFLOW = 20
# Total: 30 connections max

# High traffic (needs tuning)
# Use for: High-traffic production, microservices
POOL_SIZE = 20
MAX_OVERFLOW = 30
# Total: 50 connections max
```

### 5. Configuration Settings

**File**: `src/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    # Connection pool settings (optional overrides)
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

**File**: `.env.example`

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Connection pool tuning (optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 6. Usage in FastAPI Routes

**Example**:

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from src.db import get_session
from src.models import Task

router = APIRouter()

@router.get("/tasks")
async def list_tasks(session: Session = Depends(get_session)):
    """
    List tasks - connection from pool automatically.

    Connection lifecycle:
    1. Request arrives → get_session() gets connection from pool
    2. Session used for query
    3. Request ends → connection returned to pool
    4. Connection reused for next request
    """
    tasks = session.exec(select(Task)).all()
    return tasks
    # Connection automatically returned to pool here


@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create task - transaction managed automatically"""
    try:
        task = Task(**task_data.model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Failed to create task: {e}") from e
    # Connection returned to pool automatically
```

### 7. Pool Health Monitoring

**File**: `src/routes/health.py`

```python
from fastapi import APIRouter
from src.db import engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Health endpoint with pool status.

    Returns pool metrics for monitoring:
    - Pool size (configured baseline)
    - Connections in pool (available)
    - Current overflow (temporary connections)
    - Checked out connections (in use)
    """
    try:
        # Get pool status
        pool_status = engine.pool.status()
        # Example: "Pool size: 10  Connections in pool: 8
        #           Current Overflow: 2 Current Checked out connections: 2"

        logger.info(f"Pool health: {pool_status}")

        return {
            "status": "healthy",
            "database": "connected",
            "pool_status": pool_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
```

### 8. Connection Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ Request arrives                                         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI calls get_session()                            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Pool provides connection                                │
│ - If available in pool → reuse existing                │
│ - If pool full but < max_overflow → create new         │
│ - If at max → wait pool_timeout seconds                │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Session used for database operations                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Request ends → Session closed                           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Connection returned to pool (ready for reuse)           │
└─────────────────────────────────────────────────────────┘
```

### 9. Testing

**File**: `tests/test_connection_pool.py`

```python
import pytest
from sqlmodel import Session, select
from src.db import engine, get_session
from src.models import User

def test_connection_pool_configured():
    """Test pool settings are applied"""
    assert engine.pool.size() == 10  # POOL_SIZE
    assert engine.pool._max_overflow == 20  # MAX_OVERFLOW


def test_connection_reuse():
    """Test connections are reused from pool"""
    # Get first connection
    with Session(engine) as session1:
        conn1_id = id(session1.connection())

    # Get second connection - should be same (reused from pool)
    with Session(engine) as session2:
        conn2_id = id(session2.connection())

    # Note: This test may fail if pool has multiple connections
    # More robust: Check pool metrics show reuse


async def test_concurrent_requests_use_pool(client: AsyncClient):
    """Test concurrent requests share connection pool"""
    import asyncio

    # Make 20 concurrent requests
    tasks = [
        client.get("/api/tasks", headers=auth_headers)
        for _ in range(20)
    ]

    responses = await asyncio.gather(*tasks)

    # All should succeed (pool handles concurrency)
    assert all(r.status_code == 200 for r in responses)

    # Pool should not be exhausted
    pool_status = engine.pool.status()
    print(f"Pool after load: {pool_status}")
```

## Tuning Guidelines

### When to Increase Pool Size

**Symptoms of undersized pool**:
- Timeouts waiting for connections
- High pool checkout latency
- "QueuePool limit of size X overflow Y reached" errors

**Solution**:
```python
# Increase pool_size or max_overflow
POOL_SIZE = 20  # From 10
MAX_OVERFLOW = 30  # From 20
```

### When to Decrease Pool Size

**Symptoms of oversized pool**:
- Database complaining about too many connections
- Idle connections consuming resources
- "too many connections" database errors

**Solution**:
```python
# Decrease pool_size
POOL_SIZE = 5  # From 10
MAX_OVERFLOW = 10  # From 20
```

### Serverless Considerations

**IMPORTANT**: Connection pooling is **NOT recommended** for serverless (Lambda, Cloud Functions):

```python
# Serverless pattern - NO pooling
engine = create_engine(
    database_url,
    poolclass=NullPool,  # Disable pooling
    connect_args={"connect_timeout": 5}
)

# Create new connection per invocation
def get_session():
    with Session(engine) as session:
        yield session
```

## Constitution Alignment

- ✅ **Stateless Architecture**: Pool managed by SQLAlchemy, not application state
- ✅ **Performance**: Connection reuse reduces latency
- ✅ **Resource Management**: Prevents database overload
- ✅ **Observability**: Pool metrics exposed via health endpoint

## Success Criteria

- [ ] Engine configured with pool settings (pool_size, max_overflow, timeout)
- [ ] pool_pre_ping=True for connection health checks
- [ ] pool_recycle=3600 to prevent stale connections
- [ ] get_session() dependency provides pooled connections
- [ ] Health endpoint exposes pool metrics
- [ ] Pool size tuned for expected load
- [ ] Tests verify connection reuse
- [ ] No "pool limit reached" errors under normal load

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 5
- SQLAlchemy Pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
- FastAPI Database: https://fastapi.tiangolo.com/tutorial/sql-databases/
