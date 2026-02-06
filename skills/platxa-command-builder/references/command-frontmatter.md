# Command Frontmatter Reference

Complete specification for YAML frontmatter fields in Claude Code slash commands.

## Frontmatter Structure

YAML frontmatter is optional metadata at the start of command files, delimited by `---`:

```markdown
---
description: Brief description
allowed-tools: Read, Write
model: sonnet
argument-hint: [arg1] [arg2]
disable-model-invocation: false
---

Command prompt content here...
```

All fields are optional. Commands work without any frontmatter.

## Field Specifications

### description

| Property | Value |
|----------|-------|
| Type | String |
| Required | No |
| Default | First line of command prompt |
| Max Length | ~60 characters recommended |

Describes what the command does, shown in `/help` output.

**Good descriptions:**
- "Review PR for code quality and security"
- "Deploy application to specified environment"
- "Generate comprehensive API documentation"

**Bad descriptions:**
- "This command reviews PRs" (unnecessary prefix)
- "Review" (too vague)
- "A command that reviews pull requests for code quality, security issues, and best practices compliance with detailed output" (too long)

**Rules:**
- Start with verb (Review, Deploy, Generate, Analyze)
- Keep under 60 characters for clean `/help` display
- Be specific about what the command does
- Omit "command" or "slash command" from text

### allowed-tools

| Property | Value |
|----------|-------|
| Type | String or Array |
| Required | No |
| Default | Inherits from conversation |

Restricts which tools the command can use.

**String format (comma-separated):**
```yaml
allowed-tools: Read, Write, Edit
```

**Array format:**
```yaml
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
```

**Bash command filters:**
```yaml
allowed-tools: Bash(git:*)       # Only git commands
allowed-tools: Bash(npm:*)       # Only npm commands
allowed-tools: Bash(kubectl:*)   # Only kubectl commands
allowed-tools: Bash(gh:*)        # Only GitHub CLI commands
```

**All tools (not recommended):**
```yaml
allowed-tools: "*"
```

**Best practices:**
- Be as restrictive as possible
- Use command filters for Bash (e.g., `Bash(git:*)` not `Bash(*)`)
- Only specify when different from conversation permissions
- Include all tools the command actually needs

**Common tool sets by command type:**

| Command Type | Typical Tools |
|-------------|---------------|
| Read-only analysis | `Read, Grep` |
| Git operations | `Bash(git:*), Read` |
| Code generation | `Read, Write, Edit` |
| Testing | `Bash(npm:*), Read` |
| Deployment | `Bash(kubectl:*), Read` |
| Interactive | `AskUserQuestion, Read, Write` |
| Full workflow | `Read, Write, Edit, Bash(git:*), Grep` |

### model

| Property | Value |
|----------|-------|
| Type | String |
| Required | No |
| Default | Inherits from conversation |
| Values | `sonnet`, `opus`, `haiku` |

Specifies which Claude model executes the command.

| Model | Use Case | Speed | Capability |
|-------|----------|-------|------------|
| `haiku` | Simple, formulaic, frequent commands | Fast | Basic |
| `sonnet` | Standard workflows (default) | Balanced | Good |
| `opus` | Complex analysis, architecture | Slow | Maximum |

**When to specify:**
- Use `haiku` for speed on simple tasks (formatting, quick fixes)
- Use `opus` for genuinely complex analysis (architecture review)
- Omit for standard commands (inherits from conversation)

### argument-hint

| Property | Value |
|----------|-------|
| Type | String |
| Required | No |
| Default | None |

Documents expected arguments for users and autocomplete.

**Format:** Use square brackets for each argument.

```yaml
argument-hint: [pr-number]
argument-hint: [environment] [version]
argument-hint: [source-file] [options]
argument-hint: [source-branch] [target-branch] [commit-message]
```

**Rules:**
- Use descriptive names (not `arg1`, `arg2`)
- Match order to positional `$1`, `$2` in command body
- Keep concise but clear

### disable-model-invocation

| Property | Value |
|----------|-------|
| Type | Boolean |
| Required | No |
| Default | `false` |

Prevents SlashCommand tool from programmatically invoking command.

**When true:** Command only invokable by user typing `/command-name`.

**Use for:**
- Destructive operations requiring human judgment
- Production deployments needing approval
- Interactive wizards requiring user input
- Commands with irreversible side effects

**Use sparingly** — limits Claude's autonomy and workflow composition.

## Validation Checklist

Before committing a command:

- [ ] YAML syntax valid (no unclosed quotes, proper indentation)
- [ ] Description under 60 characters
- [ ] `allowed-tools` uses proper format (comma-separated or array)
- [ ] Bash tools use command filters (`Bash(git:*)` not plain `Bash`)
- [ ] Model is valid value if specified (`sonnet`, `opus`, `haiku`)
- [ ] `argument-hint` matches positional arguments in command body
- [ ] Frontmatter has exactly two `---` delimiters
- [ ] No unknown fields (only description, allowed-tools, model, argument-hint, disable-model-invocation)

## Common Errors

**Invalid YAML syntax:**
```yaml
---
description: Missing quote here
allowed-tools: Read, Write  # This line is fine
---  # But first line has unbalanced quotes
```

**Bash without filter:**
```yaml
allowed-tools: Bash  # Should be Bash(git:*) or similar
```

**Invalid model:**
```yaml
model: gpt4  # Must be sonnet, opus, or haiku
```

**Wrong argument-hint format:**
```yaml
argument-hint: environment version  # Should use [brackets]
```
