# Guide Skill Template

Template for skills that teach or explain concepts.

## SKILL.md Structure

```yaml
---
name: {skill-name}
description: {Guides users through X. Explains Y step by step.}
allowed-tools:
  - Read
  - WebSearch
  - WebFetch
  - AskUserQuestion
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - guide
    - tutorial
    - {domain}
---

# {Skill Name}

{One-line description of what this skill teaches.}

## Overview

This guide helps {target users} understand {topic}. By the end, you'll be able to {outcome}.

**What you'll learn:**
- {Learning outcome 1}
- {Learning outcome 2}
- {Learning outcome 3}

**Prerequisites:**
- {Prerequisite 1}
- {Prerequisite 2}

## Learning Path

### Level 1: {Foundation Topic}

**Concept**: {Core concept explanation}

**Key points:**
- {Point 1}
- {Point 2}

**Practice**: {How to practice this}

### Level 2: {Intermediate Topic}

**Concept**: {Building on Level 1}

**Key points:**
- {Point 1}
- {Point 2}

**Practice**: {How to practice this}

### Level 3: {Advanced Topic}

**Concept**: {Advanced application}

**Key points:**
- {Point 1}
- {Point 2}

**Practice**: {Real-world scenario}

## Best Practices

### Do
- {Best practice 1}
- {Best practice 2}
- {Best practice 3}

### Don't
- {Anti-pattern 1}
- {Anti-pattern 2}

## Common Questions

### Q: {Frequently asked question 1}
**A**: {Clear answer}

### Q: {Frequently asked question 2}
**A**: {Clear answer}

## Examples

### Example 1: {Basic Usage}

```
User: /{skill-command}
Assistant: Welcome! Let's learn about {topic}.
{Guides through first concept}
User: {Follow-up question}
Assistant: {Helpful explanation}
```

### Example 2: {Specific Question}

```
User: How do I {specific task}?
Assistant: {Step-by-step explanation}
```

## Resources

- {Resource 1}: {URL or description}
- {Resource 2}: {URL or description}

## Summary

Key takeaways:
1. {Takeaway 1}
2. {Takeaway 2}
3. {Takeaway 3}
```

## Key Sections for Guides

1. **Learning Path**: Progressive disclosure
2. **Best Practices**: Actionable advice
3. **Common Questions**: Address confusion
4. **Examples**: Show interactive learning
