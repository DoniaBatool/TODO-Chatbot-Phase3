---
description: Implement atomic database operations with proper transaction management and rollback handling (Phase 2 pattern)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill implements transaction management following Phase 2's proven pattern. Ensures data consistency through atomic operations, proper error handling, and automatic rollback on failures.

### 1. Parse Requirements

Extract from user input or context:
- What operations must be atomic? (all-or-nothing)
- Scope of transaction (single request, multi-step operation)
- Error handling strategy (rollback, retry, propagate)
- Need for nested transactions (savepoints)
- Isolation level required (read committed, serializable)

### 2. Core Transaction Principles

**Atomicity**: Group related operations in single transaction - all succeed or all fail
**Explicit Rollback**: Always rollback on error to prevent partial updates
**Short Transactions**: Minimize lock time to prevent blocking
**Exception Handling**: Try/except with rollback in except block
**Explicit Commit**: Don't rely on auto-commit in production
**Refresh After Commit**: Get updated object from database (timestamps, auto-generated IDs)

### 3. Basic Transaction Pattern

**File**: `src/routes/tasks.py`

```python
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from src.db import get_session
from src.models import Task
from src.schemas import TaskCreate, TaskResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create task with transaction management.

    Transaction lifecycle:
    1. Implicit transaction start (first session operation)
    2. Add object to session
    3. Explicit commit (persist to database)
    4. Refresh to get DB-generated values
    5. Rollback if any error occurs
    """
    try:
        # Transaction starts implicitly
        task = Task(
            user_id=current_user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False
        )

        # Add to session (not yet in database)
        session.add(task)

        # Commit transaction (write to database)
        session.commit()

        # Refresh to get database-generated values (id, created_at, updated_at)
        session.refresh(task)

        logger.info(f"Task created: id={task.id} user={current_user_id}")
        return task

    except Exception as e:
        # Rollback on any error (revert transaction)
        session.rollback()

        # Log error for debugging
        logger.error(f"Failed to create task: {e}", exc_info=True)

        # Return error to client
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        ) from e
```

### 4. Multi-Step Atomic Transaction

**Pattern**: Multiple database operations that must all succeed or all fail

```python
@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create order with inventory update - atomic transaction.

    Both operations must succeed:
    1. Create order record
    2. Update product inventory

    If either fails, both rollback.
    """
    try:
        # Step 1: Verify inventory (read with lock)
        product = session.get(Product, order_data.product_id)

        if not product:
            raise HTTPException(404, f"Product {order_data.product_id} not found")

        if product.stock < order_data.quantity:
            raise HTTPException(400, "Insufficient stock")

        # Step 2: Create order
        order = Order(
            user_id=current_user_id,
            product_id=order_data.product_id,
            quantity=order_data.quantity,
            total_price=product.price * order_data.quantity
        )
        session.add(order)

        # Step 3: Update inventory (atomic with order creation)
        product.stock -= order_data.quantity
        product.updated_at = datetime.utcnow()
        session.add(product)

        # Commit all changes atomically
        # Both order creation and inventory update succeed or both fail
        session.commit()

        # Refresh both objects
        session.refresh(order)
        session.refresh(product)

        logger.info(
            f"Order created: id={order.id} product={product.id} "
            f"new_stock={product.stock}"
        )
        return order

    except HTTPException:
        # Re-raise business logic errors (400, 404)
        # Still rollback to clean up any session changes
        session.rollback()
        raise

    except Exception as e:
        # Rollback and wrap database errors as 500
        session.rollback()
        logger.error(f"Order creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Order creation failed: {str(e)}"
        ) from e
```

### 5. Update Transaction Pattern

**Pattern**: Fetch, modify, commit with ownership check

```python
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Update task with transaction management"""
    try:
        # Fetch existing task
        task = session.get(Task, task_id)

        # Existence check
        if not task:
            raise HTTPException(404, f"Task {task_id} not found")

        # Ownership check
        if task.user_id != current_user_id:
            logger.warning(
                f"SECURITY: Forbidden update - user={current_user_id} "
                f"task={task_id} owned_by={task.user_id}"
            )
            raise HTTPException(403, "Forbidden: Task does not belong to you")

        # Update fields (partial update)
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed

        task.updated_at = datetime.utcnow()

        # Add to session and commit
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task updated: id={task.id} user={current_user_id}")
        return task

    except HTTPException:
        session.rollback()
        raise

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update task {task_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to update task: {e}") from e
```

### 6. Delete Transaction Pattern

```python
@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """Delete task with transaction management"""
    try:
        task = session.get(Task, task_id)

        if not task:
            raise HTTPException(404, f"Task {task_id} not found")

        if task.user_id != current_user_id:
            logger.warning(
                f"SECURITY: Forbidden delete - user={current_user_id} "
                f"task={task_id} owned_by={task.user_id}"
            )
            raise HTTPException(403, "Forbidden: Task does not belong to you")

        # Delete and commit
        session.delete(task)
        session.commit()

        logger.info(f"Task deleted: id={task_id} user={current_user_id}")
        return None  # 204 No Content

    except HTTPException:
        session.rollback()
        raise

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete task {task_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to delete task: {e}") from e
```

### 7. Nested Transaction with Savepoint

**For advanced use cases requiring partial rollback**:

```python
from sqlalchemy import exc

@router.post("/batch-tasks", response_model=List[TaskResponse])
async def create_batch_tasks(
    tasks_data: List[TaskCreate],
    session: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create multiple tasks with partial rollback support.

    Uses savepoints to rollback individual task failures
    without affecting other tasks.
    """
    created_tasks = []
    errors = []

    try:
        for i, task_data in enumerate(tasks_data):
            # Create savepoint for this task
            savepoint = session.begin_nested()

            try:
                task = Task(
                    user_id=current_user_id,
                    title=task_data.title,
                    description=task_data.description
                )
                session.add(task)
                session.flush()  # Execute SQL but don't commit

                created_tasks.append(task)
                savepoint.commit()  # Commit savepoint

            except Exception as e:
                # Rollback this task only
                savepoint.rollback()
                errors.append(f"Task {i}: {str(e)}")
                logger.warning(f"Failed to create task {i}: {e}")

        # Commit all successful tasks
        if created_tasks:
            session.commit()
            for task in created_tasks:
                session.refresh(task)

        return {
            "created": created_tasks,
            "errors": errors,
            "success_count": len(created_tasks),
            "error_count": len(errors)
        }

    except Exception as e:
        # Rollback everything on outer transaction error
        session.rollback()
        raise HTTPException(500, f"Batch creation failed: {e}") from e
```

### 8. Transaction Isolation Levels

**When to use different isolation levels**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Default: READ COMMITTED (sufficient for most cases)
engine = create_engine(database_url)

# SERIALIZABLE (strictest, prevents all anomalies)
# Use for: Financial transactions, inventory with race conditions
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_serializable(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE")
    cursor.close()

# Usage in critical operations
@router.post("/transfer")
async def transfer_funds(
    transfer_data: TransferCreate,
    session: Session = Depends(get_session)
):
    """
    Financial transfer with SERIALIZABLE isolation.

    Prevents race conditions:
    - Read balance
    - Deduct from source
    - Add to destination
    All atomic and isolated from other transactions.
    """
    try:
        # ... transfer logic ...
        session.commit()
    except exc.OperationalError as e:
        # Handle serialization failure (retry transaction)
        session.rollback()
        raise HTTPException(409, "Transaction conflict, please retry")
```

### 9. Testing Transaction Behavior

**File**: `tests/test_transactions.py`

```python
import pytest
from sqlmodel import Session, select
from src.models import Task, Product
from src.db import engine

def test_transaction_rollback_on_error(session: Session):
    """Test transaction rolls back on error"""
    initial_count = len(session.exec(select(Task)).all())

    try:
        # Create task
        task = Task(user_id="user-1", title="Test")
        session.add(task)

        # Simulate error before commit
        raise Exception("Simulated error")

    except Exception:
        session.rollback()

    # Verify no task was created (rollback worked)
    final_count = len(session.exec(select(Task)).all())
    assert final_count == initial_count


def test_multi_step_atomic_transaction(session: Session):
    """Test multi-step transaction is atomic"""
    # Create product
    product = Product(id=1, name="Widget", stock=10, price=100)
    session.add(product)
    session.commit()

    try:
        # Start transaction
        product.stock -= 5  # Update 1

        # Simulate error before second update
        raise Exception("Simulated failure")

        order = Order(product_id=1, quantity=5)  # Never reached
        session.add(order)
        session.commit()

    except Exception:
        session.rollback()

    # Verify product stock unchanged (rollback worked)
    session.refresh(product)
    assert product.stock == 10  # Original value


async def test_concurrent_transactions_isolated(client: AsyncClient):
    """Test transactions are isolated from each other"""
    # Two users update same resource concurrently
    # Depending on isolation level, may see serialization errors
    # or last-write-wins behavior
    pass
```

## Transaction Best Practices

### ✅ DO:

- Always use try/except with session.rollback() in except block
- Commit explicitly (don't rely on auto-commit)
- Refresh objects after commit to get DB-generated values
- Keep transactions short (minimize lock time)
- Log all transaction errors with context
- Use savepoints for partial rollback scenarios
- Handle HTTPException separately from database exceptions

### ❌ DON'T:

- Don't leave transactions open (causes locks)
- Don't commit inside loops (inefficient)
- Don't catch exceptions without rollback
- Don't perform long-running operations inside transactions
- Don't use auto-commit in production
- Don't ignore transaction errors silently

## Constitution Alignment

- ✅ **Data Consistency**: ACID guarantees via proper transactions
- ✅ **Error Handling**: Explicit rollback prevents partial updates
- ✅ **Observability**: All transaction errors logged
- ✅ **Database-Centric**: State changes atomic and durable

## Success Criteria

- [ ] All write operations wrapped in try/except/rollback
- [ ] session.commit() called explicitly (not auto-commit)
- [ ] session.rollback() in all exception handlers
- [ ] session.refresh() after commit for DB-generated values
- [ ] Multi-step operations atomic (all succeed or all fail)
- [ ] HTTPException handled separately from database exceptions
- [ ] Transaction errors logged with context
- [ ] Tests verify rollback behavior
- [ ] No partial updates visible to users

## References

- Phase 2 Pattern: `docs/reverse-engineered/intelligence-object.md` - Skill 6
- SQLAlchemy Transactions: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
- FastAPI Error Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
