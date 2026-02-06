---
name: platxa-command-builder
description: Create Claude Code slash commands with proper frontmatter, dynamic arguments, file references, bash execution, and plugin integration. Use when the user asks to "create a slash command", "add a command", "write a custom command", "build a CLI command", or needs guidance on command structure, YAML frontmatter, arguments, or command organization.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  tags:
    - builder
    - commands
    - cli
    - claude-code
---

# Platxa Command Builder

Create production-ready Claude Code slash commands with proper structure, frontmatter, and dynamic features.

## Overview

This skill builds slash commands — Markdown files containing prompts that Claude executes during interactive sessions. Commands provide reusable, shareable workflows invoked via `/command-name`.

**What it creates:**
- Project commands (`.claude/commands/`)
- Personal commands (`~/.claude/commands/`)
- Plugin commands (`plugin-name/commands/`)
- Multi-step workflow commands
- Interactive commands with AskUserQuestion

**Key features:**
- YAML frontmatter configuration
- Dynamic arguments (`$1`, `$2`, `$ARGUMENTS`)
- File references (`@path/to/file`)
- Inline bash execution (`!`command``)
- Plugin resource paths (`${CLAUDE_PLUGIN_ROOT}`)
- Namespaced organization

## Critical Principle

**Commands are instructions FOR Claude, not messages TO users.**

When a user invokes `/command-name`, the command content becomes Claude's instructions. Write commands as directives TO Claude about what to do.

**Correct:**
```markdown
Review this code for security vulnerabilities including:
- SQL injection
- XSS attacks
Provide specific line numbers and severity ratings.
```

**Incorrect:**
```markdown
This command will review your code for security issues.
You'll receive a report with vulnerability details.
```

## Workflow

### Step 1: Gather Requirements

Ask the user for:
- Command purpose (what should it do?)
- Command location (project, personal, or plugin?)
- Arguments needed (what inputs does it take?)
- Tools required (Read, Bash, etc.)
- Interactive elements needed (AskUserQuestion?)

### Step 2: Analyze Context

Use Glob/Read to understand:
- Existing commands in `.claude/commands/` or `~/.claude/commands/`
- Project conventions and naming patterns
- Related commands that may exist
- Plugin structure if building plugin commands

### Step 3: Determine Command Type

| Requirement | Type | Key Features |
|-------------|------|-------------|
| Simple analysis | Basic | No frontmatter needed |
| Tool restrictions | Standard | `allowed-tools` frontmatter |
| User inputs | Parameterized | `$1`, `$2`, `argument-hint` |
| Dynamic context | Context-aware | `!`bash command`` execution |
| Complex choices | Interactive | AskUserQuestion tool |
| Multi-phase | Workflow | State files, command chains |
| Plugin-bundled | Plugin | `${CLAUDE_PLUGIN_ROOT}` paths |

### Step 4: Generate Command

Create the `.md` file following the templates below.

### Step 5: Validate

Verify the command:
- YAML frontmatter syntax valid (if present)
- `$1`/`$2` match `argument-hint` parameters
- `allowed-tools` includes all tools used in command
- File references (`@`) point to valid paths
- Bash commands are safe and scoped

## Command Locations

| Location | Path | Scope | Label in /help |
|----------|------|-------|----------------|
| Project | `.claude/commands/` | This project only | `(project)` |
| Personal | `~/.claude/commands/` | All projects | `(user)` |
| Plugin | `plugin-name/commands/` | When plugin installed | `(plugin:name)` |

## Dynamic Features

### Arguments

| Syntax | Captures | Example |
|--------|----------|---------|
| `$ARGUMENTS` | All arguments as string | `/cmd fix the login bug` |
| `$1` | First argument | `/cmd staging` |
| `$2` | Second argument | `/cmd staging v1.2.3` |
| `$3` | Third argument | `/cmd app staging --force` |

### File References

```markdown
@path/to/file              <!-- Static file inclusion -->
@$1                        <!-- Dynamic file from argument -->
@${CLAUDE_PLUGIN_ROOT}/templates/report.md  <!-- Plugin file -->
```

### Bash Execution

```markdown
!`git status`              <!-- Execute and include output -->
!`git diff --name-only`    <!-- Dynamic context gathering -->
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`  <!-- Plugin script -->
```

## Templates

### Basic Command (No Frontmatter)

```markdown
Review this code for common issues and suggest improvements.
Focus on readability, maintainability, and potential bugs.
Provide specific line numbers and fix suggestions.
```

### Standard Command

```markdown
---
description: Review code for quality and issues
allowed-tools: Read, Bash(git:*)
---

Files changed: !`git diff --name-only`

Review each changed file for:
1. Code quality and style consistency
2. Potential bugs or logic errors
3. Test coverage gaps
4. Documentation needs

Provide specific feedback with file and line references.
```

### Parameterized Command

```markdown
---
description: Deploy to specified environment
argument-hint: [environment] [version]
allowed-tools: Bash(kubectl:*), Read
model: sonnet
---

Deploy $1 environment using version $2.

Pre-deployment checks:
- Cluster status: !`kubectl cluster-info`
- Current pods: !`kubectl get pods -n $1`

Proceed with deployment following the runbook.
```

### File Analysis Command

```markdown
---
description: Generate documentation for file
argument-hint: [source-file]
---

Generate comprehensive documentation for @$1 including:
- Function/class descriptions with parameter types
- Return value documentation
- Usage examples
- Edge cases and error handling
```

### Plugin Command

```markdown
---
description: Run plugin analysis workflow
argument-hint: [file-path]
allowed-tools: Bash(node:*), Read
---

Analyze @$1 using plugin tools:

Static analysis: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/lint.js $1`
Config: @${CLAUDE_PLUGIN_ROOT}/config/rules.json

Review results and provide:
1. Critical issues requiring immediate attention
2. Improvement suggestions
3. Overall quality score
```

### Interactive Command

```markdown
---
description: Interactive project setup wizard
allowed-tools: AskUserQuestion, Write, Read
---

Guide the user through project setup.

Use AskUserQuestion to gather configuration:

**Question 1 - Framework:**
- header: "Framework"
- question: "Which framework should we use?"
- options:
  - Next.js (React with SSR, recommended for Platxa)
  - Remix (React with nested routing)
  - Astro (Static-first with islands)

**Question 2 - Features:**
- header: "Features"
- question: "Which features do you need?"
- multiSelect: true
- options:
  - Authentication (JWT + OAuth)
  - Database (Prisma ORM)
  - API Routes (REST endpoints)
  - Testing (Vitest + Playwright)

Based on answers, generate configuration files.
```

## Command Organization

### Flat (5-15 commands)

```
.claude/commands/
├── review.md
├── test.md
├── deploy.md
└── docs.md
```

### Namespaced (15+ commands)

```
.claude/commands/
├── ci/
│   ├── build.md        # /build (project:ci)
│   ├── test.md         # /test (project:ci)
│   └── lint.md         # /lint (project:ci)
├── git/
│   ├── commit.md       # /commit (project:git)
│   └── pr.md           # /pr (project:git)
└── docs/
    └── generate.md     # /generate (project:docs)
```

## Best Practices

### Command Design

1. **Single responsibility** — one command, one task
2. **Clear descriptions** — discoverable in `/help`, start with verb
3. **Document arguments** — always provide `argument-hint`
4. **Minimal tools** — use most restrictive `allowed-tools`
5. **Safe bash** — use `Bash(git:*)` not `Bash(*)`
6. **Handle errors** — consider missing arguments and files

### Naming Conventions

- Use verb-noun pattern: `review-pr`, `fix-issue`, `deploy-app`
- Hyphens for multi-word: `security-review` not `securityReview`
- Avoid generic names: `test`, `run`, `do`
- Plugin commands: consider plugin-specific prefix

### Documentation in Commands

```markdown
---
description: Deploy application to environment
argument-hint: [environment] [version]
---

<!--
USAGE: /deploy [staging|production] [version]
REQUIRES: kubectl access, valid kubeconfig
EXAMPLE: /deploy staging v1.2.3
-->

Deploy $1 using version $2...
```

## Examples

### Example 1: PR Review Command

**User**: "Create a command to review pull requests"

**File**: `.claude/commands/review-pr.md`

```markdown
---
description: Review pull request for code quality
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read, Grep
---

PR details: !`gh pr view $1 --json title,body,author,files`
Changes: !`gh pr diff $1 --name-only`

Review PR #$1:

1. Check code quality and style
2. Identify potential bugs
3. Verify test coverage
4. Review documentation updates
5. Check for security issues

Provide structured feedback with:
- Critical issues (must fix)
- Suggestions (should fix)
- Nits (nice to have)

Recommend: approve, request changes, or comment.
```

### Example 2: Quick Fix Command

**User**: "Create a fast command for small fixes"

**File**: `.claude/commands/quick-fix.md`

```markdown
---
description: Quick fix for common issues
argument-hint: [issue-description]
model: haiku
---

Fix: $ARGUMENTS

Approach:
1. Identify the issue in the codebase
2. Apply minimal, focused fix
3. Verify fix doesn't break existing functionality

Focus on: simple solution, minimal changes, existing patterns.
```

### Example 3: Odoo Module Scaffolder (Platxa)

**User**: "Create a command to scaffold new Odoo modules"

**File**: `.claude/commands/scaffold-module.md`

```markdown
---
description: Scaffold new Odoo module with standard structure
argument-hint: [module-name] [description]
allowed-tools: Write, Bash(mkdir:*)
---

Create Odoo module '$1' with description: $2

Generate standard structure:
- __manifest__.py (name, version, depends, data)
- __init__.py (model imports)
- models/__init__.py
- models/$1.py (base model with _name, _description)
- views/$1_views.xml (tree, form, action, menu)
- security/ir.model.access.csv (CRUD permissions)

Follow Odoo conventions:
- Module name: snake_case
- Model name: module.model_name
- XML IDs: module_name.descriptive_id
- Security: group-based access
```

## Output Checklist

When creating a command, verify:

- [ ] File has `.md` extension in correct directory
- [ ] YAML frontmatter syntax valid (matching `---` delimiters)
- [ ] `description` under 60 characters, starts with verb
- [ ] `argument-hint` documents all `$1`/`$2` parameters
- [ ] `allowed-tools` includes all tools the command uses
- [ ] `model` is valid (`sonnet`, `opus`, or `haiku`) if specified
- [ ] Bash commands use scoped patterns (`Bash(git:*)` not `Bash(*)`)
- [ ] File references (`@`) use valid paths
- [ ] `${CLAUDE_PLUGIN_ROOT}` used for all plugin-internal paths
- [ ] Command written as instructions FOR Claude (imperative directives)
- [ ] No hardcoded absolute paths (use relative or variables)
- [ ] Error cases considered (missing args, missing files)

For detailed frontmatter specs, see `references/command-frontmatter.md`.
For advanced workflow patterns, see `references/command-patterns.md`.
For interactive command design, see `references/interactive-commands.md`.
