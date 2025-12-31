---
description: Build MCP (Model Context Protocol) tools with proper contracts, validation, and integration with AI agents (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill automates the creation of MCP tools following Phase 3 constitution principles: stateless, user-isolated, type-safe, and AI-agent compatible.

### 1. Parse Tool Requirements

Extract from user input or spec.md:
- Tool name (lowercase_with_underscores format)
- Tool purpose (one-line description)
- Parameters (name, type, required/optional, description)
- Return schema (JSON structure)
- Example inputs and outputs
- User isolation requirements (user_id parameter)

### 2. Validate Against Constitution

**MUST verify:**
- [ ] Tool name follows naming convention (lowercase_with_underscores)
- [ ] user_id parameter included as required
- [ ] Parameters have typed schema
- [ ] Returns JSON object with consistent structure
- [ ] Error messages are descriptive (never raw exceptions)
- [ ] Idempotency considered (where applicable)

**Display constitution alignment:**
```text
Constitution Check: MCP-First Tool Architecture
✓ Tool name: [tool_name] (valid format)
✓ User isolation: user_id parameter required
✓ Type safety: Parameters schema defined
✓ Error handling: Descriptive messages planned
⚠ Idempotency: [explain if applicable or N/A]
```

### 3. Generate Tool Implementation Structure

Create the following files in `backend/src/mcp_tools/`:

**File: `[tool_name]_tool.py`**
```python
from typing import Optional
from pydantic import BaseModel, Field

class [ToolName]Input(BaseModel):
    """Input schema for [tool_name] tool"""
    user_id: str = Field(..., description="User ID for isolation")
    # Add other parameters from requirements

class [ToolName]Output(BaseModel):
    """Output schema for [tool_name] tool"""
    # Define return structure

async def [tool_name](input_data: [ToolName]Input) -> [ToolName]Output:
    """
    [Tool purpose description]

    Args:
        input_data: Validated input parameters

    Returns:
        [ToolName]Output: Tool execution result

    Raises:
        ValueError: [When raised]
        HTTPException: [When raised]
    """
    # Validate user_id
    # Execute business logic
    # Return structured output
    pass
```

**File: `tests/test_[tool_name]_tool.py`**
```python
import pytest
from mcp_tools.[tool_name]_tool import [tool_name], [ToolName]Input

@pytest.mark.asyncio
async def test_[tool_name]_happy_path():
    """Test successful execution"""
    pass

@pytest.mark.asyncio
async def test_[tool_name]_user_isolation():
    """Test user_id validation and isolation"""
    pass

@pytest.mark.asyncio
async def test_[tool_name]_invalid_input():
    """Test error handling for invalid inputs"""
    pass
```

### 4. Register Tool with MCP Server

Add tool registration in `backend/src/mcp_server.py`:

```python
from mcp_tools.[tool_name]_tool import [tool_name]

# In server initialization:
server.add_tool(
    name="[tool_name]",
    description="[Tool purpose]",
    input_schema=[ToolName]Input.schema(),
    handler=[tool_name]
)
```

### 5. Create Tool Contract Documentation

**File: `specs/[feature]/contracts/mcp-tools/[tool_name].md`**

```markdown
# MCP Tool: [tool_name]

## Purpose
[Tool purpose description]

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | User ID for data isolation |
| [param] | [type] | [Yes/No] | [Description] |

## Returns

\`\`\`json
{
  "field1": "type (description)",
  "field2": "type (description)"
}
\`\`\`

## Example Usage

**Input:**
\`\`\`json
{
  "user_id": "user123",
  "param": "value"
}
\`\`\`

**Output:**
\`\`\`json
{
  "result": "success"
}
\`\`\`

## Error Handling

| Error | Condition | Message |
|-------|-----------|---------|
| ValueError | Invalid param | "[descriptive message]" |
| PermissionError | User mismatch | "Access denied" |

## Idempotency

[Explain if tool is idempotent or not, and why]
```

### 6. Integration Testing

Create integration test for tool with AI agent:

**File: `tests/integration/test_agent_[tool_name].py`**

```python
import pytest
from openai_agents import Agent
from mcp_server import server

@pytest.mark.asyncio
async def test_agent_can_invoke_[tool_name]():
    """Test AI agent successfully invokes [tool_name] tool"""
    agent = Agent(tools=[server.tools])

    # Simulate user message
    response = await agent.run(
        messages=[{"role": "user", "content": "[natural language command]"}],
        user_id="test_user"
    )

    # Verify tool was called
    assert "[tool_name]" in response.tool_calls
    # Verify output structure
    assert response.output["field"] == expected_value
```

### 7. Display Creation Summary

Output to terminal:
```text
✅ MCP Tool Created: [tool_name]

📁 Files Generated:
  - backend/src/mcp_tools/[tool_name]_tool.py
  - tests/test_[tool_name]_tool.py
  - tests/integration/test_agent_[tool_name].py
  - specs/[feature]/contracts/mcp-tools/[tool_name].md

🔧 Tool Registration:
  - Added to backend/src/mcp_server.py

✅ Constitution Compliance:
  ✓ Stateless design
  ✓ User isolation (user_id required)
  ✓ Type-safe parameters
  ✓ Descriptive error handling
  ✓ Integration test included

📋 Next Steps:
  1. Run: pytest tests/test_[tool_name]_tool.py (should FAIL - Red phase)
  2. Implement tool logic to pass tests (Green phase)
  3. Run integration test with agent
  4. Update MCP server documentation
```

### 8. Test-Driven Development Workflow

**Enforce TDD:**
1. **Red**: Run unit tests - they MUST fail initially
2. **Green**: Implement minimal code to pass tests
3. **Refactor**: Optimize while keeping tests green
4. **Integration**: Test with AI agent end-to-end

**Validation Commands:**
```bash
# Red phase - tests should fail
pytest tests/test_[tool_name]_tool.py -v

# After implementation - tests should pass
pytest tests/test_[tool_name]_tool.py -v

# Integration test
pytest tests/integration/test_agent_[tool_name].py -v
```

### 9. Update Project Documentation

Add tool to:
- `README.md` - Available MCP Tools section
- `specs/[feature]/plan.md` - MCP Tools list
- `backend/docs/mcp-tools.md` - Complete tool reference

## Success Criteria

- [ ] Tool follows constitution naming conventions
- [ ] user_id parameter enforced
- [ ] Type schemas defined (Pydantic models)
- [ ] Unit tests written and initially failing (Red phase)
- [ ] Integration test with AI agent included
- [ ] Tool contract documented
- [ ] Error handling with descriptive messages
- [ ] Tool registered in MCP server
- [ ] Constitution compliance verified

## Notes

- This skill is automatically invoked when implementing Phase 3 chatbot features
- All MCP tools MUST be stateless and user-isolated
- Terminal output shows skill usage for traceability
- Supports test-driven development approach
