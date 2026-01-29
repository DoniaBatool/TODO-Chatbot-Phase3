---
name: edge-case-tester
description: Comprehensive edge case testing for features to ensure robustness and prevent broken functionality (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Find and prevent failures by systematically testing edge cases beyond “happy path”.

## Test Dimensions (Checklist)

- **Input shape**: empty strings, very long strings, unicode/emoji, invalid types
- **Ambiguity**: partial matches, duplicates, missing identifiers
- **Time**: timezone, DST, “tomorrow”, invalid dates, past due dates
- **Concurrency**: double-submit, retry, simultaneous updates
- **Security**: cross-user access attempts, injection strings
- **Resilience**: tool failures, DB timeouts, partial outages

## Workflow

### Phase 1: Build an Edge-Case Matrix
- Identify inputs + constraints
- List boundary values and “weird but valid” values

### Phase 2: Execute
- Manual probes for UX flows
- Automated tests for regressions where possible

### Phase 3: Report
- Provide repro steps + expected vs actual
- Suggest a fix or mitigation (validation, clarification prompt, retry)

## Deliverables

- [ ] Edge-case matrix
- [ ] Repro steps for failures
- [ ] Regression tests added for critical bugs