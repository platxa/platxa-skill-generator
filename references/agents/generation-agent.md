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
   - If blueprint includes `invocation_mode`, add the corresponding frontmatter:
     - `disable-model-invocation: true` for user-only skills (side effects)
     - `user-invocable: false` for Claude-only skills (background knowledge)
     - Omit both for default (both user and Claude can invoke)
   - If discovery found related existing skills, add `depends-on` (required) and/or `suggests` (optional companions)
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
disable-model-invocation: true  # Only if skill has side effects (omit for default)
user-invocable: false           # Only if background knowledge (omit for default)
allowed-tools:
  - Tool1
  - Tool2
depends-on:               # Only if discovery found required skills
  - required-skill-name
suggests:                 # Only if discovery found beneficial companions
  - companion-skill-name
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
{Description — use $ARGUMENTS for user input, ${CLAUDE_SKILL_DIR} for script paths}

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

## String Substitutions

Use Claude Code's built-in string substitutions for portable, dynamic skills:

- `$ARGUMENTS` — All arguments passed when invoking the skill (e.g., `/skill-name arg1 arg2`)
- `$ARGUMENTS[0]`, `$0` — First argument by index
- `${CLAUDE_SKILL_DIR}` — Directory containing this skill's SKILL.md (use for script paths)
- `${CLAUDE_SESSION_ID}` — Current session ID (use for logs or session-specific files)

**Rules:**
- Use `${CLAUDE_SKILL_DIR}` when referencing bundled scripts: `bash ${CLAUDE_SKILL_DIR}/scripts/helper.sh`
- Use `$ARGUMENTS` when the skill accepts user input: `Analyze $ARGUMENTS following the checklist`
- Never hardcode absolute paths to the skill directory
- If `$ARGUMENTS` is not present in the content, arguments are appended as `ARGUMENTS: <value>` automatically

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
