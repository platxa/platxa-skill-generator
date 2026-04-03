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
   - **Description is the primary trigger mechanism.** Front-load the first 250 chars with:
     - What the skill does (one sentence)
     - When to use it: `Use when the user asks to "create X", "review Y", or "check Z".`
     - Include quoted trigger phrases that users would actually say
     - Descriptions over 250 chars are truncated in skill listings — the trigger context must come first
   - Write descriptions in **third person** ("Analyzes code...") not first ("I can help...")
   - Do NOT use `when_to_use` field — it is not in the Agent Skills open standard
   - If blueprint includes `invocation_mode`, add the corresponding frontmatter:
     - `disable-model-invocation: true` for user-only skills (side effects)
     - `user-invocable: false` for Claude-only skills (background knowledge)
     - Omit both for default (both user and Claude can invoke)
   - All sections from architecture blueprint, respecting freedom levels:
     - **low freedom**: Use exact scripts, specific commands, strict templates
     - **medium freedom**: Use pseudocode or parameterized scripts
     - **high freedom**: Use text instructions, let Claude adapt to context
   - Examples with realistic usage scenarios
   - Output checklist with verification items
   - **Conditional workflows**: When the skill has branching logic, use explicit decision trees:
     ```
     1. Determine the task type:
        Creating new content? → Follow "Creation workflow" below
        Editing existing content? → Follow "Editing workflow" below
     2. Creation workflow: [steps...]
     3. Editing workflow: [steps...]
     ```

   - **Writing style**: Explain the WHY behind instructions, not just the WHAT. Modern LLMs
     have strong theory of mind — when given reasoning, they go beyond rote instructions and
     adapt intelligently. If you find yourself writing ALWAYS, NEVER, or MUST in all caps,
     reframe as reasoning: explain the constraint and why it matters. This produces skills
     that generalize across diverse prompts rather than overfitting to narrow examples.

2. **Generate Scripts** (if specified)
   - Bash scripts with proper shebang
   - Error handling (set -euo pipefail)
   - Clear usage documentation
   - Make executable

3. **Generate References** (if specified)
   - Domain expertise documentation
   - Real content, not placeholders
   - Structured for easy consumption
   - **Multi-domain skills**: Create per-domain reference files instead of one monolithic file
     - Example: `references/aws.md`, `references/gcp.md`, `references/azure.md`
     - Each file loads independently — Claude only reads the relevant domain
     - Include a quick-search tip in SKILL.md: `grep -i "metric" references/sales.md`
   - **Single-domain skills**: One reference file is fine

## SKILL.md Template

```yaml
---
name: {skill_name}
description: >-
  {What it does}. Use when the user asks to "{trigger1}", "{trigger2}",
  or "{trigger3}". {Additional detail about capabilities and output}.
argument-hint: "[filename] [format]"  # Only if skill accepts arguments (omit otherwise)
disable-model-invocation: true  # Only if skill has side effects (omit for default)
user-invocable: false           # Only if background knowledge (omit for default)
allowed-tools:
  - Tool1
  - Tool2
metadata:
  version: "1.0.0"
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

Include at least 2 concrete input/output pairs. Examples help Claude understand
the desired style and detail level more clearly than descriptions alone.

### Example 1: {Common Use Case}

**Input:** {Realistic user prompt or command}
**Output:**
```
{Exact expected output format}
```

### Example 2: {Edge Case or Variation}

**Input:** {Different input showing another use case}
**Output:**
```
{Expected output for this variation}
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

## Dynamic Context Injection

When a skill needs live data at invocation time, use the `` !`command` `` syntax.
These shell commands run **before** the skill content reaches Claude — the output
replaces the placeholder inline.

**When to use:**
- Skill needs current git state: `` !`git status --short` ``
- Skill needs environment info: `` !`node --version` ``
- Skill needs file listings: `` !`ls src/` ``
- Skill needs PR context: `` !`gh pr diff` ``

**Example in a PR review skill:**
```markdown
## Current PR context
- Changed files: !`gh pr diff --name-only`
- PR description: !`gh pr view --json body -q .body`

## Your task
Review the changes above...
```

**Rules:**
- Commands run as preprocessing — Claude only sees the output
- Keep commands fast and deterministic (no interactive commands)
- Only use when the skill genuinely needs live runtime data
- For static data, use regular markdown instead

## Skill-to-Skill Invocation

When a skill invokes other skills (e.g., a workflow skill that calls `/lint` then `/test`):
- Include `Skill` in the `allowed-tools` list
- Reference other skills by name: "Invoke the `/lint` skill to check code quality"
- If the skill requires specific other skills, add them to `depends-on`

## Quality Requirements

- [ ] Name is hyphen-case, ≤64 characters
- [ ] Description is ≤1024 characters with trigger context in first 250 chars
- [ ] Description in third person, no when_to_use field
- [ ] Description includes quoted trigger phrases users would actually say
- [ ] SKILL.md is < 500 lines
- [ ] All sections have real content (explain WHY, not rigid MUSTs)
- [ ] Examples are realistic and helpful
- [ ] Scripts are executable and tested
- [ ] Skills that invoke other skills include `Skill` in allowed-tools
- [ ] References contain actual domain expertise
- [ ] Version under metadata.version (not top-level)
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Generation Agent prompt with inputs filled in]
```
