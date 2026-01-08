# Automation Skill Template

Template for skills that automate repetitive tasks.

## SKILL.md Structure

```yaml
---
name: {skill-name}
description: {Automates X. Runs Y automatically when Z.}
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - automation
    - workflow
    - {domain}
---

# {Skill Name}

{One-line description of what this skill automates.}

## Overview

This skill automates {task} for {target users}. It {what it does} whenever {trigger condition}.

**What it automates:**
- {Automated task 1}
- {Automated task 2}

**Time saved:** ~{X minutes/hours} per {occurrence}

## Triggers

### When to Run

This automation should run when:
- {Trigger condition 1}
- {Trigger condition 2}

### Manual Invocation

```
/{skill-command} [options]
```

| Option | Description |
|--------|-------------|
| --dry-run | Preview changes without applying |
| --verbose | Show detailed output |
| --force | Skip confirmation prompts |

## Process

### Step 1: {Detection/Input}

{What the automation detects or accepts as input}

### Step 2: {Processing}

{What transformations or actions are performed}

### Step 3: {Output/Application}

{What the automation produces or changes}

## Verification

### Success Indicators

- {How to know it worked 1}
- {How to know it worked 2}

### Failure Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| {Error 1} | {Why it happens} | {How to fix} |
| {Error 2} | {Why it happens} | {How to fix} |

## Examples

### Example 1: {Standard Automation}

```
User: /{skill-command}
Assistant: Running {automation name}...
✓ {Step 1 complete}
✓ {Step 2 complete}
✓ {Step 3 complete}
Done! {Summary of what was automated}
```

### Example 2: {Dry Run}

```
User: /{skill-command} --dry-run
Assistant: Preview of changes:
- Would {action 1}
- Would {action 2}
Run without --dry-run to apply.
```

## Safety

### Idempotency

This automation is {idempotent/not idempotent}:
- {Explanation of behavior when run multiple times}

### Reversibility

{Can changes be undone? How?}

### Prerequisites

Before running, ensure:
- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}

## Configuration

```json
{
  "option1": "default_value",
  "option2": true
}
```
```

## Key Sections for Automation

1. **Triggers**: When to run
2. **Process**: Clear steps
3. **Verification**: Confirm success
4. **Safety**: Idempotency and reversibility
