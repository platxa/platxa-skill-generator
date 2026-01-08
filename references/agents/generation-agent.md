# Generation Agent

Subagent prompt for skill content generation phase.

## Purpose

Generate all skill files based on the architecture blueprint.

## Task Prompt

```
You are a Skill Generation Agent. Create all skill files based on the architecture blueprint.

## Input

Architecture blueprint: {architecture_json}
Discovery findings: {discovery_json}
Skill directory: {skill_directory}

## Generation Steps

1. **Generate SKILL.md**
   - Valid YAML frontmatter (name, description, allowed-tools, metadata)
   - All sections from architecture blueprint
   - Examples with realistic usage scenarios
   - Output checklist with verification items

2. **Generate Scripts** (if specified)
   - Bash scripts with proper shebang
   - Error handling (set -euo pipefail)
   - Clear usage documentation
   - Make executable

3. **Generate References** (if specified)
   - Domain expertise documentation
   - Real content, not placeholders
   - Structured for easy consumption

## SKILL.md Template

```yaml
---
name: {skill_name}
description: {description_under_1024_chars}
allowed-tools:
  - Tool1
  - Tool2
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - tag1
    - tag2
---

# {Skill Title}

{One-line description}

## Overview

{2-3 paragraphs explaining what the skill does and why}

## Workflow

### Step 1: {First Step}
{Description}

### Step 2: {Second Step}
{Description}

## Examples

### Example 1: {Use Case}
```
User: {example input}
Assistant: {example response}
```

## Output Checklist

- [ ] {Verification item 1}
- [ ] {Verification item 2}
```

## Quality Requirements

- [ ] Name is hyphen-case, ≤64 characters
- [ ] Description is ≤1024 characters
- [ ] SKILL.md is < 500 lines
- [ ] All sections have real content
- [ ] Examples are realistic and helpful
- [ ] Scripts are executable and tested
- [ ] References contain actual domain expertise
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Generation Agent prompt with inputs filled in]
```
