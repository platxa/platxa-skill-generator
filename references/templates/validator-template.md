# Validator Skill Template

Template for skills that verify quality or compliance.

## SKILL.md Structure

```yaml
---
name: {skill-name}
description: {Validates X against Y rules. Ensures Z compliance.}
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - validator
    - compliance
    - {domain}
---

# {Skill Name}

{One-line description of what this skill validates.}

## Overview

This skill validates {target} against {standard/rules}. It ensures {compliance goal} for {target users}.

**What it validates:**
- {Validation target 1}
- {Validation target 2}

**Standards enforced:**
- {Standard 1}
- {Standard 2}

## Rules

### Rule 1: {Rule Name}

**Description**: {What this rule checks}

**Passes when**: {Pass condition}

**Fails when**: {Fail condition}

**Severity**: {Critical|High|Medium|Low}

### Rule 2: {Rule Name}

**Description**: {What this rule checks}

**Passes when**: {Pass condition}

**Fails when**: {Fail condition}

**Severity**: {Critical|High|Medium|Low}

### Rule 3: {Rule Name}

**Description**: {What this rule checks}

**Passes when**: {Pass condition}

**Fails when**: {Fail condition}

**Severity**: {Critical|High|Medium|Low}

## Thresholds

| Metric | Minimum | Target | Maximum |
|--------|---------|--------|---------|
| {metric1} | {value} | {value} | {value} |
| {metric2} | {value} | {value} | {value} |
| {metric3} | {value} | {value} | N/A |

## Pass/Fail Criteria

### Automatic PASS

All of the following must be true:
- [ ] {Criteria 1}
- [ ] {Criteria 2}
- [ ] {Criteria 3}

### Automatic FAIL

Any of the following triggers failure:
- {Fail condition 1}
- {Fail condition 2}
- {Fail condition 3}

### Conditional PASS

May pass with warnings if:
- {Condition for warning-level pass}

## Examples

### Example 1: {Passing Validation}

```
User: /{skill-command} {target}
Assistant: Validating {target}...

✓ Rule 1: {rule name} - PASSED
✓ Rule 2: {rule name} - PASSED
✓ Rule 3: {rule name} - PASSED

═══════════════════════
VALIDATION: ✓ PASSED
═══════════════════════
```

### Example 2: {Failing Validation}

```
User: /{skill-command} {target}
Assistant: Validating {target}...

✓ Rule 1: {rule name} - PASSED
✗ Rule 2: {rule name} - FAILED
  → {Why it failed}
  → {How to fix}
✓ Rule 3: {rule name} - PASSED

═══════════════════════
VALIDATION: ✗ FAILED
  1 critical issue found
═══════════════════════

To fix:
1. {Fix instruction}
```

### Example 3: {Warnings}

```
User: /{skill-command} {target}
Assistant: Validating {target}...

✓ Rule 1: PASSED
⚠ Rule 2: WARNING - {issue}
✓ Rule 3: PASSED

═══════════════════════
VALIDATION: ⚠ PASSED WITH WARNINGS
═══════════════════════
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation failed (critical) |
| 2 | Validation passed with warnings |

## Configuration

### Enabling/Disabling Rules

```json
{
  "rules": {
    "rule1": true,
    "rule2": true,
    "rule3": false
  },
  "severity_threshold": "medium",
  "fail_on_warning": false
}
```

### Custom Thresholds

```json
{
  "thresholds": {
    "metric1": {"min": 0, "max": 100},
    "metric2": {"min": 50}
  }
}
```
```

## Key Sections for Validators

1. **Rules**: Clear pass/fail conditions
2. **Thresholds**: Configurable limits
3. **Pass/Fail Criteria**: Decision logic
4. **Exit Codes**: Programmatic integration
