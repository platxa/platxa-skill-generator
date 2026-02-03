# Claude Code Best Practices

Core principles for effective Claude Code usage. For full documentation, see https://docs.anthropic.com/en/docs/claude-code.

## The One Rule

**Context is your most valuable resource.** Everything follows from managing the context window effectively.

## Core Principles

### 1. Give Claude Verification

The single highest-leverage practice. Provide tests, screenshots, or expected outputs so Claude can self-check.

| Strategy | Example |
|----------|---------|
| Test cases | `test cases: user@example.com -> true, invalid -> false` |
| Visual check | `[paste screenshot] implement this, take screenshot, compare, fix diffs` |
| Build verify | `fix root cause, run npm run build to verify, don't suppress errors` |

### 2. Explore -> Plan -> Code

1. **Explore** (Plan Mode): Read files, understand patterns
2. **Plan**: Create implementation plan, write to file for review
3. **Implement** (Normal Mode): Code against the plan, run tests
4. **Commit**: Descriptive message, open PR

Skip planning for trivial changes (typo fix, rename, single-line change).

### 3. Be Specific

| Do | Don't |
|----|-------|
| Reference files with `@path` | Describe file locations vaguely |
| Provide error messages verbatim | Say "getting an error" |
| Point to existing patterns | Assume Claude knows your conventions |
| State constraints explicitly | Leave requirements implicit |

### 4. Manage Sessions

- **`/clear`** between unrelated tasks
- After 2 failed corrections -> `/clear` + better prompt
- Use subagents for investigation (separate context)
- **`Esc`** to stop, **`Esc+Esc`** to rewind
- `claude --continue` / `--resume` for persistent sessions

## Environment Setup

| Tool | Purpose |
|------|---------|
| **CLAUDE.md** | Persistent project rules (commands, style, conventions) |
| **Skills** | Domain knowledge loaded on demand |
| **Subagents** | Isolated investigation in separate context |
| **Hooks** | Deterministic actions (lint on edit, block writes) |
| **`/permissions`** | Allowlist safe commands to reduce interruptions |
| **CLI tools** | `gh`, `aws`, etc. for context-efficient external access |

### CLAUDE.md Guidelines

Keep concise. For each line ask: "Would removing this cause mistakes?" If not, cut it.

**Include**: Commands Claude can't guess, style rules differing from defaults, test runners, project conventions, gotchas.
**Exclude**: Anything inferrable from code, standard conventions, long tutorials, file-by-file descriptions.

## Scaling Patterns

- **Headless**: `claude -p "prompt"` for CI/scripts
- **Parallel sessions**: Writer/Reviewer pattern, test-then-implement
- **Fan out**: Loop `claude -p` over file list with `--allowedTools` scoping
- **Sandbox**: `/sandbox` for autonomous work within boundaries

## Common Failure Patterns

| Pattern | Fix |
|---------|-----|
| Kitchen sink session | `/clear` between unrelated tasks |
| Correction spiral (2+ fails) | `/clear` + better initial prompt |
| Over-specified CLAUDE.md | Prune ruthlessly, convert to hooks |
| Trust-then-verify gap | Always provide verification criteria |
| Infinite exploration | Scope narrowly or use subagents |
