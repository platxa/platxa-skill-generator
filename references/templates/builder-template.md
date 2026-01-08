# Builder Skill Template

Template for skills that create new artifacts.

## SKILL.md Structure

```yaml
---
name: {skill-name}
description: {Creates X for Y. Generates Z based on input.}
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Task
  - AskUserQuestion
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - builder
    - generator
    - {domain}
---

# {Skill Name}

{One-line description of what this skill builds.}

## Overview

This skill creates {artifact type} by {method}. It's designed for {target users} who need to {goal}.

**What it creates:**
- {Output 1}
- {Output 2}

**Key features:**
- {Feature 1}
- {Feature 2}

## Workflow

### Step 1: Gather Requirements

Ask the user for:
- {Required input 1}
- {Required input 2}

### Step 2: Analyze Context

Use Read/Glob to understand:
- {What to analyze}
- {Patterns to detect}

### Step 3: Generate Output

Create the {artifact} using:
- {Template or pattern}
- {Customization rules}

### Step 4: Validate

Verify the output:
- {Check 1}
- {Check 2}

## Templates

### {Template Name 1}
```
{Template content}
```

### {Template Name 2}
```
{Template content}
```

## Examples

### Example 1: {Common Use Case}

```
User: /{skill-command} {input}
Assistant: I'll create a {artifact} for you.
[Creates files]
Assistant: Created {output}. Here's what was generated:
- {File 1}
- {File 2}
```

### Example 2: {Edge Case}

```
User: /{skill-command} {unusual input}
Assistant: {How it handles the edge case}
```

## Output Checklist

When complete, verify:

- [ ] All required files created
- [ ] Files follow project conventions
- [ ] No placeholder content
- [ ] Code compiles/validates
- [ ] Documentation included
- [ ] Tests generated (if applicable)

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| {option1} | {value} | {description} |
| {option2} | {value} | {description} |
```

## Key Sections for Builders

1. **Templates**: Provide starting points
2. **Output Checklist**: Verify completeness
3. **Configuration**: Allow customization
4. **Examples**: Show realistic outputs
