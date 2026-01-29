---
name: mcp-tool-builder
description: Build MCP (Model Context Protocol) tools with proper contracts, validation, and integration with AI agents (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Create MCP tools that are:
- deterministic and safe
- validated (inputs/outputs)
- easy for the agent to call correctly
- observable (logs and predictable errors)

## Tool Design Checklist

- **Name** is verb-first and specific (e.g., `update_task`)
- **Inputs**: typed schema with required vs optional clearly defined
- **Outputs**: typed schema that includes all fields the UI/agent needs
- **Errors**: predictable errors with actionable messages

## Workflow

### Phase 1: Contract
- Define Pydantic/SQLModel DTO for params and result
- Decide whether operation is idempotent

### Phase 2: Implementation
- Validate inputs; normalize whitespace/casing
- Enforce user isolation and authorization
- Return structured results (not free-form strings)

### Phase 3: Integration
- Register tool for the agent runtime
- Ensure chat endpoint logs tool_calls and persists them

### Phase 4: Testing
- Unit tests for validation
- Integration tests for DB side effects

## Deliverables

- [ ] Tool contract (params/result)
- [ ] Implementation with ownership checks
- [ ] Tests + example calls