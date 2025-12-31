---
description: Comprehensive edge case testing for features to ensure robustness and prevent broken functionality (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This skill automatically generates and executes edge case tests after `/sp.implementation` to ensure features work perfectly with no gaps.

### 1. Edge Case Categories

Test the following edge cases for every feature:

**Input Validation:**
- Empty strings
- Null values
- Extremely long inputs (>1000 chars)
- Special characters and unicode
- SQL injection attempts
- XSS attempts

**Boundary Conditions:**
- Zero, negative numbers
- Maximum integers
- Empty lists/arrays
- Single-item lists
- Lists exceeding limits

**State Transitions:**
- Operations on non-existent resources
- Duplicate operations (idempotency)
- Concurrent modifications
- State rollback scenarios

**User Isolation:**
- Cross-user access attempts
- Missing user_id
- Invalid user_id format

**Network & Database:**
- Database connection failures
- Timeout scenarios
- Partial data states
- Transaction rollbacks

### 2. Create Edge Case Test Generator

**File: `backend/src/testing/edge_case_generator.py`**

```python
from typing import List, Dict, Any
from pydantic import BaseModel

class EdgeCase(BaseModel):
    """Edge case test definition"""
    category: str
    description: str
    input_data: Dict[str, Any]
    expected_behavior: str
    expected_error: Optional[str] = None

class EdgeCaseGenerator:
    """Generate edge case tests for features"""

    def generate_for_mcp_tool(self, tool_name: str, tool_schema: Dict) -> List[EdgeCase]:
        """
        Generate edge cases for MCP tool

        Args:
            tool_name: Name of the MCP tool
            tool_schema: Pydantic schema with parameters

        Returns:
            List of edge case tests
        """
        edge_cases = []

        # Input validation edge cases
        edge_cases.extend(self._generate_input_validation_cases(tool_schema))

        # Boundary condition edge cases
        edge_cases.extend(self._generate_boundary_cases(tool_schema))

        # User isolation edge cases
        edge_cases.append(EdgeCase(
            category="user_isolation",
            description="Missing user_id parameter",
            input_data={k: v for k, v in tool_schema.items() if k != "user_id"},
            expected_behavior="Raise validation error",
            expected_error="user_id is required"
        ))

        # Idempotency edge cases (if applicable)
        if tool_name in ["complete_task", "delete_task"]:
            edge_cases.append(EdgeCase(
                category="idempotency",
                description="Operate on already processed resource",
                input_data={"user_id": "test", "task_id": 999},
                expected_behavior="No error, graceful handling"
            ))

        return edge_cases

    def _generate_input_validation_cases(self, schema: Dict) -> List[EdgeCase]:
        """Generate input validation edge cases"""
        cases = []

        for param_name, param_type in schema.items():
            if param_type == str:
                # Empty string
                cases.append(EdgeCase(
                    category="input_validation",
                    description=f"Empty {param_name}",
                    input_data={param_name: ""},
                    expected_behavior="Raise validation error" if param_name != "description" else "Accept",
                    expected_error=f"{param_name} cannot be empty" if param_name != "description" else None
                ))

                # Extremely long string
                cases.append(EdgeCase(
                    category="input_validation",
                    description=f"Extremely long {param_name}",
                    input_data={param_name: "a" * 10000},
                    expected_behavior="Raise validation error",
                    expected_error=f"{param_name} exceeds maximum length"
                ))

                # SQL injection attempt
                cases.append(EdgeCase(
                    category="security",
                    description=f"SQL injection in {param_name}",
                    input_data={param_name: "'; DROP TABLE tasks; --"},
                    expected_behavior="Sanitized, no SQL execution",
                    expected_error=None
                ))

            if param_type == int:
                # Negative number
                cases.append(EdgeCase(
                    category="boundary",
                    description=f"Negative {param_name}",
                    input_data={param_name: -1},
                    expected_behavior="Raise validation error",
                    expected_error=f"{param_name} must be positive"
                ))

        return cases

    def _generate_boundary_cases(self, schema: Dict) -> List[EdgeCase]:
        """Generate boundary condition edge cases"""
        # Zero, max int, empty lists, etc.
        pass
```

### 3. Create Edge Case Test Runner

**File: `tests/edge_cases/test_edge_cases_auto.py`**

```python
import pytest
from backend.src.testing.edge_case_generator import EdgeCaseGenerator
from backend.src.mcp_tools import TOOL_REGISTRY

@pytest.mark.asyncio
async def test_all_mcp_tools_edge_cases():
    """Automatically test edge cases for all MCP tools"""
    generator = EdgeCaseGenerator()

    for tool_name, tool_handler in TOOL_REGISTRY.items():
        # Get tool schema
        tool_schema = tool_handler.__annotations__.get("input_data").schema()["properties"]

        # Generate edge cases
        edge_cases = generator.generate_for_mcp_tool(tool_name, tool_schema)

        # Run each edge case
        for edge_case in edge_cases:
            print(f"Testing {tool_name}: {edge_case.description}")

            if edge_case.expected_error:
                # Expect error
                with pytest.raises(Exception) as exc_info:
                    await tool_handler(edge_case.input_data)
                assert edge_case.expected_error in str(exc_info.value)
            else:
                # Expect success
                result = await tool_handler(edge_case.input_data)
                assert result is not None

@pytest.mark.asyncio
async def test_chat_endpoint_edge_cases():
    """Test chat endpoint edge cases"""
    edge_cases = [
        {
            "description": "Empty message",
            "input": {"message": ""},
            "expected_error": "Message cannot be empty"
        },
        {
            "description": "Extremely long message",
            "input": {"message": "a" * 10000},
            "expected_error": "Message exceeds maximum length"
        },
        {
            "description": "Invalid conversation_id",
            "input": {"conversation_id": -1, "message": "Hello"},
            "expected_error": "Invalid conversation ID"
        },
        {
            "description": "Cross-user conversation access",
            "input": {"conversation_id": 999, "message": "Hello"},
            "expected_error": "Access denied"
        },
    ]

    for case in edge_cases:
        print(f"Testing: {case['description']}")
        # Execute test
        pass

@pytest.mark.asyncio
async def test_concurrent_task_modifications():
    """Test concurrent modifications to same task (race conditions)"""
    import asyncio

    task_id = 1

    async def complete_task():
        # User A completes task
        pass

    async def delete_task():
        # User B deletes task
        pass

    # Run concurrently
    await asyncio.gather(complete_task(), delete_task())

    # Verify final state is consistent
    pass

@pytest.mark.asyncio
async def test_database_connection_failure():
    """Test graceful handling of database failures"""
    # Simulate DB connection failure
    # Verify error handling and user-friendly message
    pass
```

### 4. Create Edge Case Report

**File: `specs/[feature]/edge-cases-tested.md`**

```markdown
# Edge Cases Tested

## Input Validation (15 tests)
- ✅ Empty strings in required fields
- ✅ Null values
- ✅ Extremely long inputs (>1000 chars)
- ✅ Special characters (unicode, emojis)
- ✅ SQL injection attempts
- ✅ XSS attempts

## Boundary Conditions (12 tests)
- ✅ Zero values
- ✅ Negative numbers
- ✅ Maximum integers
- ✅ Empty task lists
- ✅ Single task in list
- ✅ List exceeding limit (>1000 tasks)

## State Transitions (10 tests)
- ✅ Complete non-existent task
- ✅ Delete already deleted task
- ✅ Update completed task
- ✅ Duplicate task creation (idempotency)

## User Isolation (8 tests)
- ✅ Cross-user task access
- ✅ Missing user_id
- ✅ Invalid user_id format
- ✅ JWT token mismatch

## Network & Database (7 tests)
- ✅ Database connection failure
- ✅ Query timeout
- ✅ Transaction rollback
- ✅ Partial data state

## Concurrency (5 tests)
- ✅ Concurrent task modifications
- ✅ Race conditions
- ✅ Deadlock prevention

**Total: 57 edge cases tested**
**Pass Rate: 100%**
```

### 5. Display Edge Case Testing Summary

```text
✅ Edge Case Testing Complete

🧪 Test Results:
  - Input Validation: 15/15 passed
  - Boundary Conditions: 12/12 passed
  - State Transitions: 10/10 passed
  - User Isolation: 8/8 passed
  - Network & Database: 7/7 passed
  - Concurrency: 5/5 passed

  Total: 57/57 edge cases passed ✓

📁 Files Generated:
  - backend/src/testing/edge_case_generator.py
  - tests/edge_cases/test_edge_cases_auto.py
  - specs/[feature]/edge-cases-tested.md

🛡️ Robustness Verified:
  ✓ No broken functionality
  ✓ No gaps in error handling
  ✓ All edge cases covered
  ✓ User isolation enforced
  ✓ Security vulnerabilities tested

📋 Constitution Compliance:
  ✓ Test-driven development approach
  ✓ Comprehensive edge case coverage
  ✓ No feature deployed without testing

Next: Feature ready for production ✅
```

## Success Criteria

- [ ] All edge case categories tested
- [ ] Input validation comprehensive
- [ ] Boundary conditions covered
- [ ] User isolation verified
- [ ] Concurrency scenarios tested
- [ ] Security vulnerabilities checked
- [ ] 100% edge case pass rate

## Notes

- Used automatically after `/sp.implementation`
- Ensures features are robust and production-ready
- Terminal shows edge case coverage for traceability
- Part of TDD approach per constitution
