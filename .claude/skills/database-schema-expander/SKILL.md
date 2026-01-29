---
name: database-schema-expander
description: Add new tables to existing database schema with migrations, indexes, and backward compatibility (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Add tables/columns safely to an existing schema while keeping the app running.

## Workflow

### Phase 1: Design
- Define entities, relationships, and constraints
- Identify read/write paths that will use the new schema

### Phase 2: Migration Plan (Backwards Compatible)
- Add new tables/columns as **nullable** initially when needed
- Add indexes concurrently where supported / keep locking minimal
- Deploy code that can handle both old and new shape (dual-read)

### Phase 3: Backfill (if needed)
- Run controlled backfill job/script
- Validate counts and constraints

### Phase 4: Tighten Constraints
- Set NOT NULL / UNIQUE constraints after backfill
- Remove deprecated paths after rollout

## Pitfalls

- Long-running locks during migrations
- Missing indexes causing slow list endpoints
- Breaking changes deployed before migration

## Deliverables

- [ ] ERD or schema description
- [ ] Alembic migration(s) with upgrade/downgrade
- [ ] Rollout/backfill plan