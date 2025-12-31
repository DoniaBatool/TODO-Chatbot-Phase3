---
description: Add new tables to existing database schema with migrations, indexes, and backward compatibility (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Safely expands database schema for new features following constitution.

### 1. Analyze Schema Addition

Parse requirements:
- New table name
- Fields and types
- Foreign keys
- Indexes
- Constraints

### 2. Generate SQLModel

```python
class [NewTable](SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Always include for user isolation
    # Other fields...
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Create Migration Script

```python
# migrations/[timestamp]_add_[table].py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        '[table_name]',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        # Other columns...
    )
    op.create_index('idx_[table]_user_id', '[table_name]', ['user_id'])

def downgrade():
    op.drop_table('[table_name]')
```

### 4. Test Migration

```python
def test_migration_adds_table():
    # Test upgrade
    # Test downgrade
    pass
```

### 5. Success Criteria

- [ ] SQLModel created with proper types
- [ ] Migration script with upgrade/downgrade
- [ ] Indexes on user_id for isolation
- [ ] Backward compatible
- [ ] Tests included

## Notes
- Used when expanding database for new features
- Always includes user_id for isolation
- Migration tested before deployment
