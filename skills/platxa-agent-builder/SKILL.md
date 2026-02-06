---
name: platxa-agent-builder
description: Create Claude Code plugin agents with proper frontmatter, system prompts, triggering examples, and validation. Use when the user asks to "create an agent", "add a plugin agent", "write a subagent", "build an autonomous agent", or needs guidance on agent structure, triggering patterns, system prompt design, or agent organization.
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
    - agents
    - plugins
    - claude-code
---

# Platxa Agent Builder

Create production-ready Claude Code plugin agents with proper structure, triggering, and system prompts.

## Overview

This skill builds plugin agents — Markdown files containing system prompts that Claude launches as autonomous subprocesses. Agents handle complex, multi-step tasks independently and return results to the main conversation.

**What it creates:**
- Plugin agents (`plugin-name/agents/agent-name.md`)
- Analysis agents (code review, security audit)
- Generation agents (tests, docs, scaffolding)
- Validation agents (quality checks, compliance)
- Orchestration agents (multi-phase workflows)

**Key features:**
- YAML frontmatter configuration (name, description, model, color, tools)
- Triggering via `<example>` blocks in description
- System prompt design patterns
- Tool access control
- Color-coded categorization

## Critical Principles

### 1. Agents Are Autonomous Subprocesses

Unlike slash commands (instructions in the main conversation), agents launch as **separate processes** with their own context. They receive the system prompt as instructions and work independently.

### 2. The Description Field Controls Triggering

The `description` field is the most critical field. Claude reads agent descriptions to decide when to launch them. Include:
- Clear explanation of when to use the agent
- 2-4 `<example>` blocks showing trigger scenarios
- Specific keywords Claude will match against

### 3. System Prompts Are Second-Person Instructions

Write the body as instructions TO the agent: "You are a code review specialist. Your role is to..." — not "This agent reviews code."

## Workflow

### Step 1: Gather Requirements

Ask the user for:
- Agent purpose (what task does it handle autonomously?)
- Agent pattern (analysis, generation, validation, or orchestration?)
- Trigger scenarios (when should Claude launch this agent?)
- Tools needed (Read, Write, Bash, etc.)
- Output expectations (what should the agent return?)

### Step 2: Analyze Context

Use Glob/Read to understand:
- Existing agents in the plugin's `agents/` directory
- Plugin structure and conventions
- Related agents that may overlap
- Available tools and scripts

### Step 3: Determine Agent Pattern

| Requirement | Pattern | Color | Key Process |
|-------------|---------|-------|-------------|
| Inspect/audit code | Analysis | blue | Gather→Scan→Analyze→Synthesize→Report |
| Create artifacts | Generation | green | Understand→Context→Design→Generate→Validate |
| Check quality/rules | Validation | yellow | Load Rules→Scan→Check→Collect→Assess→Decide |
| Multi-phase workflow | Orchestration | magenta | Plan→Prepare→Execute→Monitor→Verify→Report |

### Step 4: Generate Agent File

Create the `.md` file in `agents/` following the templates below.

### Step 5: Validate

Verify the agent:
- Name: 3-50 chars, lowercase letters and hyphens only, no consecutive hyphens
- Description: includes triggering conditions and 2-4 `<example>` blocks
- Model: valid value (`inherit`, `sonnet`, `opus`, `haiku`)
- Color: valid value (`blue`, `cyan`, `green`, `yellow`, `magenta`, `red`)
- Tools: only valid Claude Code tool names if specified
- System prompt: minimum ~500 words, includes role, process, output format

## Agent File Structure

```
plugin-name/
└── agents/
    └── agent-name.md    # Frontmatter + system prompt
```

Each agent is a single Markdown file with YAML frontmatter followed by the system prompt body.

## Frontmatter Fields

### Required Fields

```yaml
---
name: agent-name           # 3-50 chars, lowercase + hyphens
description: |             # When to use + example blocks
  Use this agent when...

  <example>
  Context: ...
  user: "..."
  assistant: "..."
  </example>
model: inherit             # inherit, sonnet, opus, haiku
color: blue                # blue, cyan, green, yellow, magenta, red
---
```

### Optional Fields

```yaml
tools:                     # Restrict available tools
  - Read
  - Write
  - Grep
  - Bash
```

### Color Semantics

| Color | Meaning | Use For |
|-------|---------|---------|
| `blue` | Analysis/review | Code review, architecture analysis |
| `cyan` | Documentation/info | Docs generation, explanations |
| `green` | Generation/success | Code generation, scaffolding |
| `yellow` | Validation/caution | Quality checks, linting |
| `magenta` | Creative/orchestration | Refactoring, multi-phase workflows |
| `red` | Security/critical | Security audits, vulnerability scanning |

### Model Selection

| Model | Use For | Trade-off |
|-------|---------|-----------|
| `inherit` | Most agents (uses conversation model) | Default choice |
| `haiku` | Simple, fast tasks (formatting, basic checks) | Fast, less capable |
| `sonnet` | Standard tasks (review, generation) | Balanced |
| `opus` | Complex analysis, architecture decisions | Slow, most capable |

## Description and Triggering

The description must include **when to use** the agent and **example blocks** showing trigger scenarios.

### Example Block Format

```markdown
<example>
Context: The user has just finished implementing a new feature.
user: "Can you review my code changes?"
assistant: "I'll use the code-reviewer agent to analyze your changes."
<commentary>
Since the user wants code review, launch the code-reviewer agent.
</commentary>
</example>
```

**Components:**
- `Context:` — situation before the trigger (optional but recommended)
- `user:` — what the user says (the trigger)
- `assistant:` — how Claude responds before launching the agent
- `<commentary>` — explains WHY to trigger (helps Claude's decision-making)

### Example Types

**Explicit request** — user directly asks:
```markdown
<example>
user: "Review this pull request for security issues"
assistant: "I'll launch the security-analyzer agent to scan for vulnerabilities."
</example>
```

**Proactive trigger** — assistant decides to launch:
```markdown
<example>
Context: The assistant just finished writing authentication code.
assistant: "I've implemented the auth flow. Let me proactively run the security-analyzer to check for vulnerabilities."
<commentary>
Security-sensitive code should trigger proactive security review.
</commentary>
</example>
```

**Implicit request** — user implies the need:
```markdown
<example>
user: "I think this module is ready for production"
assistant: "Before deploying, let me run the quality-validator agent to ensure production readiness."
</example>
```

## Templates

### Analysis Agent

```markdown
---
name: code-reviewer
description: |
  Use this agent when reviewing code for bugs, quality issues, and best practices.
  Should be triggered after code changes or when the user asks for code review.

  <example>
  Context: User completed a feature implementation.
  user: "Can you review my changes?"
  assistant: "I'll use the code-reviewer agent to analyze your code."
  </example>

  <example>
  Context: Assistant just wrote significant code.
  assistant: "Let me run the code-reviewer to verify quality."
  <commentary>Proactively review after writing complex code.</commentary>
  </example>
model: inherit
color: blue
tools:
  - Read
  - Grep
  - Glob
---

You are a senior code reviewer. Your role is to provide thorough,
actionable code reviews that improve code quality.

## Responsibilities
- Identify bugs, logic errors, and edge cases
- Check adherence to project conventions
- Evaluate readability and maintainability
- Assess error handling completeness

## Process
1. **Gather context**: Read changed files and understand the purpose
2. **Scan structure**: Check file organization and naming
3. **Deep analysis**: Review logic, error handling, edge cases
4. **Cross-reference**: Check consistency with related code
5. **Synthesize**: Prioritize findings by severity
6. **Report**: Present findings with specific file:line references

## Output Format
For each finding:
- **Severity**: Critical / Warning / Suggestion
- **Location**: file_path:line_number
- **Issue**: What's wrong
- **Fix**: How to resolve it

## Quality Standards
- Only report genuine issues (no false positives)
- Include positive observations for good patterns
- Provide actionable fixes, not vague suggestions
```

### Generation Agent

```markdown
---
name: test-generator
description: |
  Use this agent when generating tests for code. Trigger after implementing
  features, fixing bugs, or when test coverage needs improvement.

  <example>
  user: "Generate tests for the authentication module"
  assistant: "I'll use the test-generator to create comprehensive tests."
  </example>

  <example>
  Context: User just fixed a bug.
  assistant: "Let me generate regression tests for this fix."
  <commentary>Bug fixes should have tests to prevent regression.</commentary>
  </example>
model: inherit
color: green
tools: [Read, Write, Grep, Bash]
---

You are a test engineering specialist. [System prompt with role,
process (Understand→Identify→Design→Generate→Validate), output format,
and quality standards. See references/system-prompt-patterns.md]
```

### Validation Agent

```markdown
---
name: quality-validator
description: |
  Use this agent to validate code quality before merging or deploying.

  <example>
  user: "Is this PR ready to merge?"
  assistant: "I'll run the quality-validator to check readiness."
  </example>

  <example>
  Context: User is about to deploy to production.
  assistant: "Let me validate quality before deployment."
  <commentary>Pre-deployment validation catches issues early.</commentary>
  </example>
model: inherit
color: yellow
tools: [Read, Grep, Glob, Bash]
---

You are a quality assurance specialist. [System prompt with role,
process (Load Rules→Scan→Check→Collect→Assess→Decide), verdicts
(PASS/CONDITIONAL/FAIL), and quality standards.]
```

### Orchestration Agent

```markdown
---
name: release-orchestrator
description: |
  Use this agent for multi-phase release workflows.

  <example>
  user: "Start the release process for v2.0"
  assistant: "I'll launch the release-orchestrator to coordinate the release."
  </example>
model: inherit
color: magenta
tools: [Read, Write, Bash, Grep, Glob]
---

You are a release coordinator. [System prompt with role,
process (Plan→Pre-flight→Execute→Monitor→Verify→Report),
error handling, and rollback instructions.]
```

## System Prompt Design

Every system prompt must include: **Role statement** ("You are a..."), **Responsibilities** (bullet list), **Process** (numbered steps), **Output format**, **Quality standards**, and **Edge cases**.

**Writing rules:**
- Second person ("You are...", "Your role is...")
- Specific process steps, not vague instructions
- Concrete output format definition
- Minimum ~500 words; standard 1000-2000; complex up to 5000

See `references/system-prompt-patterns.md` for complete templates per pattern.

## Agent Organization

All agents live in `plugin-name/agents/`. For many agents, use verb-noun naming: `review-code.md`, `review-security.md`, `generate-tests.md`, `validate-quality.md`.

## Examples

### Example 1: Security Analyzer

**User**: "Create an agent to scan code for security vulnerabilities"

**File**: `agents/security-analyzer.md`

```markdown
---
name: security-analyzer
description: |
  Use this agent to scan code for security vulnerabilities including
  injection flaws, authentication issues, and data exposure risks.
  Should be triggered proactively after writing security-sensitive code.

  <example>
  user: "Check this code for security issues"
  assistant: "I'll launch the security-analyzer to scan for vulnerabilities."
  </example>

  <example>
  Context: Assistant just implemented user authentication.
  assistant: "Let me proactively scan this auth code for security issues."
  <commentary>Auth code should always be security-reviewed.</commentary>
  </example>

  <example>
  Context: User is preparing a PR with database queries.
  user: "Is this ready to merge?"
  assistant: "Let me run a security scan on the database queries first."
  </example>
model: inherit
color: red
tools:
  - Read
  - Grep
  - Glob
---

You are a security analysis specialist. Your role is to identify
security vulnerabilities in code before they reach production.

## Scan Categories
- SQL/NoSQL injection
- Cross-site scripting (XSS)
- Authentication and authorization flaws
- Sensitive data exposure
- Insecure dependencies
- Input validation gaps

## Process
1. Read target files and understand data flow
2. Map user input paths through the application
3. Check each input handling point for sanitization
4. Verify authentication and authorization checks
5. Scan for hardcoded secrets or credentials
6. Report findings with CVSS-style severity ratings

## Output Format
For each vulnerability:
- **Severity**: Critical / High / Medium / Low
- **Category**: OWASP category
- **Location**: file_path:line_number
- **Description**: What the vulnerability is
- **Impact**: What an attacker could do
- **Remediation**: How to fix it
```

### Example 2: Documentation Generator

**User**: "Create an agent to generate API documentation"

**File**: `agents/docs-generator.md`

```markdown
---
name: docs-generator
description: |
  Use this agent to generate or update documentation for code and APIs.
  Trigger when documentation is missing or outdated.

  <example>
  user: "Generate docs for the payment API"
  assistant: "I'll use the docs-generator to create API documentation."
  </example>

  <example>
  Context: User added new API endpoints without documentation.
  assistant: "Let me generate documentation for the new endpoints."
  <commentary>New APIs should be documented immediately.</commentary>
  </example>
model: inherit
color: cyan
tools: [Read, Write, Grep, Glob]
---

You are a technical documentation specialist. Your role is to create
clear, comprehensive documentation from source code.

## Process
1. Read source code to understand functionality
2. Identify public interfaces, parameters, return types
3. Find usage examples in tests or other code
4. Generate documentation following project conventions
5. Validate completeness against the source
```

## Output Checklist

When creating an agent, verify:

- [ ] File is `.md` in plugin's `agents/` directory
- [ ] YAML frontmatter has matching `---` delimiters
- [ ] `name`: 3-50 chars, lowercase letters and hyphens, no consecutive hyphens
- [ ] `description`: explains when to trigger, includes 2-4 `<example>` blocks
- [ ] `model`: valid value (`inherit`, `sonnet`, `opus`, `haiku`)
- [ ] `color`: valid value (`blue`, `cyan`, `green`, `yellow`, `magenta`, `red`)
- [ ] `tools`: only valid Claude Code tool names (if specified)
- [ ] System prompt written in second person ("You are...")
- [ ] System prompt includes: role, responsibilities, process, output format
- [ ] System prompt minimum ~500 words
- [ ] Examples include Context, user/assistant messages, and commentary
- [ ] Agent doesn't overlap with existing agents in the plugin
- [ ] Color matches agent's semantic purpose

For detailed frontmatter specs, see `references/agent-frontmatter.md`.
For system prompt patterns, see `references/system-prompt-patterns.md`.
For triggering example design, see `references/triggering-examples.md`.
