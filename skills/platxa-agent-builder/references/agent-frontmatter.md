# Agent Frontmatter Reference

Complete specification for YAML frontmatter fields in Claude Code plugin agents.

## Frontmatter Structure

YAML frontmatter is **required** metadata at the start of agent files, delimited by `---`:

```markdown
---
name: agent-name
description: |
  When to use this agent...

  <example>
  user: "..."
  assistant: "..."
  </example>
model: inherit
color: blue
tools:
  - Read
  - Grep
---

System prompt content here...
```

All four required fields (name, description, model, color) must be present.

## Field Specifications

### name

| Property | Value |
|----------|-------|
| Type | String |
| Required | Yes |
| Length | 3-50 characters |
| Format | Lowercase letters and hyphens only |

Unique identifier for the agent within the plugin.

**Rules:**
- Only lowercase letters (`a-z`) and hyphens (`-`)
- No consecutive hyphens (`--`)
- Cannot start or end with a hyphen
- 3-50 characters
- Must be unique within the plugin

**Good names:**
- `code-reviewer`, `test-generator`, `security-analyzer`

**Bad names:**
- `CodeReviewer` (uppercase)
- `code--reviewer` (consecutive hyphens)
- `cr` (too short)
- `-code-reviewer` (starts with hyphen)

### description

| Property | Value |
|----------|-------|
| Type | String (multiline) |
| Required | Yes |
| Must Include | Triggering conditions + 2-4 `<example>` blocks |

The most critical field. Claude reads this to decide when to launch the agent.

**Structure:**
```yaml
description: |
  [1-2 sentences: when to use this agent]
  [Optional: additional triggering conditions]

  <example>
  Context: [situation before trigger]
  user: "[what user says]"
  assistant: "[how Claude responds]"
  <commentary>[why this triggers the agent]</commentary>
  </example>

  [2-4 example blocks total]
```

**Rules:**
- Must clearly state when the agent should be triggered
- Must include 2-4 `<example>` blocks
- Each example should show a different trigger scenario
- Include both explicit requests and proactive triggers
- Commentary explains reasoning (helps Claude decide)

### model

| Property | Value |
|----------|-------|
| Type | String |
| Required | Yes |
| Values | `inherit`, `sonnet`, `opus`, `haiku` |

Which Claude model runs the agent.

| Value | Behavior |
|-------|----------|
| `inherit` | Uses the conversation's current model (recommended default) |
| `haiku` | Fast, basic tasks (formatting, simple checks) |
| `sonnet` | Balanced for standard tasks |
| `opus` | Maximum capability for complex analysis |

**Best practice:** Use `inherit` unless the agent specifically needs a different model.

### color

| Property | Value |
|----------|-------|
| Type | String |
| Required | Yes |
| Values | `blue`, `cyan`, `green`, `yellow`, `magenta`, `red` |

Displayed in the UI when the agent is running. Choose based on semantic meaning:

| Color | Meaning | Agent Types |
|-------|---------|-------------|
| `blue` | Analysis/review | Code review, architecture analysis, dependency audit |
| `cyan` | Documentation/info | Docs generation, explanations, summaries |
| `green` | Generation/creation | Code generation, scaffolding, test writing |
| `yellow` | Validation/caution | Quality checks, linting, compliance |
| `magenta` | Creative/orchestration | Refactoring, multi-phase workflows |
| `red` | Security/critical | Security audits, vulnerability scanning |

### tools

| Property | Value |
|----------|-------|
| Type | Array of strings |
| Required | No |
| Default | All tools available |

Restricts which tools the agent can use.

**Valid tool names:**
`Read`, `Write`, `Edit`, `MultiEdit`, `Glob`, `Grep`, `LS`, `Bash`, `Task`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `TodoWrite`, `KillShell`, `BashOutput`, `NotebookEdit`

**Common tool sets by pattern:**

| Pattern | Typical Tools |
|---------|---------------|
| Analysis | `Read, Grep, Glob` |
| Generation | `Read, Write, Grep, Bash` |
| Validation | `Read, Grep, Glob, Bash` |
| Orchestration | `Read, Write, Bash, Grep, Glob, Task` |

**Best practice:** Only list tools the agent actually needs. Omit the field entirely if the agent needs all tools.

## Validation Checklist

Before committing an agent:

- [ ] YAML syntax valid (matching `---` delimiters, proper indentation)
- [ ] `name`: 3-50 chars, lowercase + hyphens, no consecutive hyphens
- [ ] `description`: includes triggering conditions
- [ ] `description`: contains 2-4 `<example>` blocks
- [ ] `model`: one of `inherit`, `sonnet`, `opus`, `haiku`
- [ ] `color`: one of `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`
- [ ] `tools`: only valid tool names (if specified)
- [ ] No unknown frontmatter fields

## Common Errors

**Missing example blocks:**
```yaml
description: Reviews code for quality  # BAD: no examples
```

**Invalid name format:**
```yaml
name: Code_Reviewer  # BAD: uppercase and underscore
```

**Wrong model value:**
```yaml
model: claude-3  # BAD: must be inherit/sonnet/opus/haiku
```

**Invalid color:**
```yaml
color: orange  # BAD: not a valid color
```
