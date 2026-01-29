---
name: skill-creator
description: Automatically create new Claude Code skills based on requirements and project needs (project)
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

You **MUST** consider the user input before proceeding (if not empty).

## Outline

[Generated outline based on requirements]

### 1. [Step 1 Title]

[Step 1 description and implementation details]

### 2. [Step 2 Title]

[Step 2 description and implementation details]

### 3. Create Tests

[Test generation details]

### 4. Display Summary

\`\`\`text
✅ [Skill Action] Complete

📁 Files Generated:
  - [file1]
  - [file2]

✅ [Verification Points]:
  ✓ [Check 1]
  ✓ [Check 2]

📋 Next Steps:
  1. [Next action 1]
  2. [Next action 2]
\`\`\`

## Success Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Notes

- [Usage context]
- [Integration points]
```

### 4. Validate Skill Against Constitution

Check generated skill:
- [ ] Follows constitution principles
- [ ] Includes test-driven approach
- [ ] Has clear success criteria
- [ ] Specifies file outputs
- [ ] Includes terminal display summary
- [ ] Documents when to use

**Constitution alignment check:**
```text
Constitution Validation:
✓ Test-First Development: Tests included in skill
✓ Clear Success Criteria: Defined and measurable
✓ File Organization: Follows project structure
✓ Observability: Terminal output for traceability
```

### 5. Register Skill in CLAUDE.md

Add skill to `CLAUDE.md` available skills list:

```markdown
## Available Skills

### Phase 3 AI Chatbot Skills

- `/sp.mcp-tool-builder` - Build MCP tools with contracts
- `/sp.ai-agent-setup` - Setup OpenAI Agents SDK
- `/sp.chatbot-endpoint` - Create stateless chat endpoint
- `/sp.[new-skill-name]` - [Generated description]

### Utility Skills

- `/sp.ab-testing` - A/B testing framework
- `/sp.edge-case-tester` - Comprehensive edge case testing
- `/sp.skill-creator` - Auto-create skills (this skill)
```

### 6. Create Skill Documentation

**File: `docs/skills/[skill-name].md`**

```markdown
# Skill: [Skill Name]

## Purpose
[What this skill does]

## When to Use
[Context where this skill is applicable]

## Usage
\`\`\`bash
/sp.[skill-name] [arguments]
\`\`\`

## Examples

### Example 1: [Use case]
\`\`\`text
User: /sp.[skill-name] [example args]
Output: [Expected result]
\`\`\`

## Integration

### Called After
- [Prerequisite skill/command]

### Called Before
- [Subsequent skill/command]

## Constitution Alignment
- [Principle 1]: [How skill enforces it]
- [Principle 2]: [How skill enforces it]
```

### 7. Create Skill Tests

**File: `tests/skills/test_[skill-name]_skill.py`**

```python
import pytest

def test_skill_generates_expected_files():
    """Test skill creates all required files"""
    # Run skill
    # Verify files exist
    pass

def test_skill_follows_constitution():
    """Test skill output follows constitution principles"""
    # Run skill
    # Validate against constitution checklist
    pass

def test_skill_success_criteria_met():
    """Test skill meets its own success criteria"""
    # Run skill
    # Verify success criteria checkboxes
    pass
```

### 8. Display Skill Creation Summary

```text
✅ New Skill Created: sp.[skill-name]

📁 Files Generated:
  - .claude/commands/sp.[skill-name].md
  - docs/skills/[skill-name].md
  - tests/skills/test_[skill-name]_skill.py

📝 Skill Registered:
  - Added to CLAUDE.md available skills list
  - Documentation created
  - Tests included

✅ Constitution Compliance:
  ✓ Test-driven approach included
  ✓ Success criteria defined
  ✓ Terminal output format follows pattern
  ✓ Integration points documented

🧠 Skill Intelligence:
  - Purpose: [Generated purpose]
  - When to use: [Context]
  - Integrates with: [Related skills]

📋 Next Steps:
  1. Review generated skill in .claude/commands/sp.[skill-name].md
  2. Run: pytest tests/skills/test_[skill-name]_skill.py
  3. Use skill: /sp.[skill-name] [args]
  4. Iterate if needed
```

### 9. Self-Improvement Loop

After creating skill, analyze:
- Does skill follow best practices from existing skills?
- Are there missing edge cases?
- Should skill be split into smaller skills?
- Are there opportunities for reuse?

**Self-improvement prompt:**
```text
Analyzing new skill against existing patterns...

Pattern Compliance:
✓ Follows YAML frontmatter structure
✓ Includes User Input section
✓ Has numbered Outline steps
✓ Generates files with full paths
✓ Includes test generation
✓ Has success criteria checklist
✓ Terminal summary follows format

Improvement Suggestions:
- Consider adding integration test
- Could benefit from examples section
- May need error handling documentation

Overall Quality: 95/100
```

## Skill Creation Examples

### Example 1: Database Migration Skill

**Input:**
```text
/sp.skill-creator Create skill for database migrations with rollback support
```

**Output:**
- Creates `sp.database-migrator.md`
- Includes migration file generation
- Rollback procedures
- Tests for up/down migrations
- Constitution compliance (stateless, database-centric)

### Example 2: Performance Monitoring Skill

**Input:**
```text
/sp.skill-creator Create skill for monitoring API performance and alerting on SLA violations
```

**Output:**
- Creates `sp.performance-monitor.md`
- Includes metrics collection
- SLA threshold configuration
- Alert generation
- Tests for threshold violations

## Success Criteria

- [ ] Skill template generated with all sections
- [ ] Follows existing skill patterns
- [ ] Constitution compliance validated
- [ ] Registered in CLAUDE.md
- [ ] Documentation created
- [ ] Tests included
- [ ] Self-improvement analysis performed

## Notes

- This skill enables project to self-expand its capabilities
- Used when new requirements need dedicated skills
- Learns from existing skill patterns
- Maintains consistency across all skills
- Part of reusable intelligence strategy
