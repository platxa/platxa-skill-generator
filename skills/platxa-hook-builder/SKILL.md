---
name: platxa-hook-builder
description: Create Claude Code plugin hooks with proper configuration, event handling, matchers, and security patterns. Use when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "block dangerous commands", "enforce test execution", or needs guidance on hook events, prompt-based hooks, command hooks, matchers, or hooks.json configuration.
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
    - hooks
    - plugins
    - claude-code
---

# Platxa Hook Builder

Create production-ready Claude Code hooks for event-driven automation, validation, and policy enforcement.

## Overview

This skill builds hooks — event-driven scripts that execute in response to Claude Code events. Hooks validate operations, enforce policies, load context, and integrate external tools.

**What it creates:**
- Plugin hooks (`hooks/hooks.json` + scripts)
- Settings hooks (`.claude/settings.json`)
- Prompt-based hooks (LLM-driven validation)
- Command hooks (bash script validation)
- Multi-event hook configurations

**Key features:**
- 9 hook events (PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification)
- Two hook types: prompt-based (recommended) and command
- Regex matchers for tool targeting
- JSON input/output protocol
- Parallel execution model

## Critical Principles

### 1. Prompt Hooks for Complex Logic, Command Hooks for Speed

**Prompt-based hooks** use LLM reasoning — better for nuanced decisions, edge cases, and maintainability. **Command hooks** use bash scripts — better for deterministic checks, external tool integration, and performance-critical paths.

### 2. Hooks Run in Parallel

All matching hooks for an event run simultaneously. Don't rely on execution order. Design hooks to be independent.

### 3. Hooks Load at Session Start

Changes to hook configuration require restarting Claude Code. Use `claude --debug` for testing.

## Workflow

### Step 1: Gather Requirements

Ask the user for:
- What to validate/automate (file writes, bash commands, completion checks?)
- Which events to hook into (PreToolUse, Stop, SessionStart, etc.?)
- Hook type preference (prompt-based or command?)
- Plugin or settings context?

### Step 2: Analyze Context

Use Glob/Read to understand:
- Existing hooks in `hooks/hooks.json` or `.claude/settings.json`
- Plugin structure if building plugin hooks
- Scripts directory if command hooks needed

### Step 3: Determine Hook Configuration

| Goal | Event | Hook Type | Matcher |
|------|-------|-----------|---------|
| Block dangerous writes | PreToolUse | prompt | `Write\|Edit` |
| Block dangerous commands | PreToolUse | prompt | `Bash` |
| Enforce tests before stop | Stop | prompt | `*` |
| Load project context | SessionStart | command | `*` |
| Post-edit quality check | PostToolUse | command | `Write\|Edit` |
| Monitor MCP deletions | PreToolUse | prompt | `mcp__.*__delete.*` |
| Validate user prompts | UserPromptSubmit | prompt | `*` |
| Preserve context on compact | PreCompact | command | `*` |

### Step 4: Generate Hook Configuration

Create the hooks.json and any supporting scripts.

### Step 5: Validate

Verify:
- Valid JSON syntax in hooks.json
- Valid event names (PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification)
- Valid hook types (`prompt` or `command`)
- Matchers are properly formatted
- Command scripts exist and are executable
- Prompt hooks used only on supported events (Stop, SubagentStop, UserPromptSubmit, PreToolUse)
- Timeouts are reasonable (5-600 seconds)
- Scripts use `${CLAUDE_PLUGIN_ROOT}` for portability

## Hook Types

### Prompt-Based Hooks (Recommended)

LLM evaluates the hook with context awareness:

```json
{
  "type": "prompt",
  "prompt": "Validate this bash command for safety: $TOOL_INPUT. Check for destructive ops, privilege escalation, network access. Return 'approve' or 'deny'.",
  "timeout": 15
}
```

**Supported events:** PreToolUse, Stop, SubagentStop, UserPromptSubmit

**Advantages:** Context-aware, handles edge cases, no scripting needed, easy to extend.

### Command Hooks

Execute bash scripts for deterministic checks:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 10
}
```

**Use for:** Fast deterministic checks, external tool integration, file system operations, performance-critical validations.

## Configuration Formats

### Plugin Format (hooks/hooks.json)

```json
{
  "description": "Plugin validation hooks",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Validate file write safety"
          }
        ]
      }
    ]
  }
}
```

Note: `description` is optional, `hooks` wrapper is required for plugins.

### Settings Format (.claude/settings.json)

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety"
        }
      ]
    }
  ]
}
```

No wrapper — events directly at top level.

## Hook Events

| Event | When | Common Use | Output |
|-------|------|------------|--------|
| PreToolUse | Before tool runs | Approve/deny/modify | `permissionDecision: allow\|deny\|ask` |
| PostToolUse | After tool completes | Feedback, logging | `systemMessage` |
| Stop | Agent considers stopping | Completeness check | `decision: approve\|block` |
| SubagentStop | Subagent considers stopping | Task validation | `decision: approve\|block` |
| UserPromptSubmit | User submits prompt | Context, validation | `systemMessage` |
| SessionStart | Session begins | Load context, set env | `$CLAUDE_ENV_FILE` |
| SessionEnd | Session ends | Cleanup, logging | — |
| PreCompact | Before compaction | Preserve critical info | `systemMessage` |
| Notification | Notification sent | Logging, reactions | — |

See `references/hook-events.md` for detailed event specifications.

## Matchers

```json
"matcher": "Write"              // Exact tool match
"matcher": "Read|Write|Edit"    // Multiple tools (pipe-separated)
"matcher": "*"                  // All tools (wildcard)
"matcher": "mcp__.*__delete.*"  // Regex pattern
"matcher": "mcp__plugin_asana_.*"  // Specific MCP plugin
"matcher": "Bash"               // Bash commands only
```

Matchers are case-sensitive.

## Hook Input/Output

### Input (JSON via stdin)

All hooks receive:
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

Event-specific fields: `tool_name`, `tool_input` (PreToolUse/PostToolUse), `tool_result` (PostToolUse), `user_prompt` (UserPromptSubmit), `reason` (Stop/SubagentStop).

In prompt hooks, access fields via `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`.

### Output

**Standard:** `{"continue": true, "suppressOutput": false, "systemMessage": "..."}`

**PreToolUse:** `{"hookSpecificOutput": {"permissionDecision": "allow|deny|ask", "updatedInput": {...}}}`

**Stop/SubagentStop:** `{"decision": "approve|block", "reason": "..."}`

**Exit codes:** 0 = success, 2 = blocking error, other = non-blocking.

## Environment Variables

- `$CLAUDE_PROJECT_DIR` — Project root path
- `$CLAUDE_PLUGIN_ROOT` — Plugin directory (use for portable paths)
- `$CLAUDE_ENV_FILE` — SessionStart only: persist env vars here
- `$CLAUDE_CODE_REMOTE` — Set if running in remote context

**Always use `${CLAUDE_PLUGIN_ROOT}` in hook commands for portability.**

## Templates

### Security Validation (PreToolUse + Prompt)

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "File: $TOOL_INPUT.file_path. Verify: 1) Not system directories (/etc, /sys) 2) Not credentials (.env, secrets, tokens) 3) No path traversal (..). Return 'approve' or 'deny'."
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. Check: 1) No destructive ops (rm -rf, dd, mkfs) 2) No privilege escalation (sudo) 3) No unauthorized network access. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

### Test Enforcement (Stop + Prompt)

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Review transcript. If code was modified (Write/Edit used), verify tests were executed. If no tests run, block with reason 'Tests must be run after code changes'."
        }
      ]
    }
  ]
}
```

### Context Loading (SessionStart + Command)

```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

### Multi-Event Configuration

```json
{
  "PreToolUse": [
    {"matcher": "Write|Edit", "hooks": [{"type": "prompt", "prompt": "Validate file write safety"}]},
    {"matcher": "Bash", "hooks": [{"type": "prompt", "prompt": "Validate bash command safety"}]}
  ],
  "Stop": [
    {"matcher": "*", "hooks": [{"type": "prompt", "prompt": "Verify tests run and build succeeded"}]}
  ],
  "SessionStart": [
    {"matcher": "*", "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh", "timeout": 10}]}
  ]
}
```

## Command Hook Script Template

```bash
#!/bin/bash
set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract fields with jq
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Validate input
if [ -z "$file_path" ]; then
  exit 0  # Nothing to validate
fi

# Check conditions
if [[ "$file_path" == *".."* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Path traversal detected"}' >&2
  exit 2
fi

# Approve
exit 0
```

**Script rules:** Use `set -euo pipefail`, read from stdin, parse with `jq`, quote all variables, use `${CLAUDE_PLUGIN_ROOT}` for paths, exit 0 (approve) or 2 (deny).

## Examples

### Example 1: File Safety Plugin

**User**: "Create hooks to prevent writing to sensitive files"

**File**: `hooks/hooks.json`

```json
{
  "description": "File safety validation",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "File: $TOOL_INPUT.file_path. Verify: 1) Not /etc, /sys, /usr 2) Not .env, secrets, credentials, tokens 3) No path traversal (..) 4) Content doesn't contain hardcoded secrets. Return 'approve' or 'deny' with reason."
          }
        ]
      }
    ]
  }
}
```

### Example 2: Quality Enforcement Plugin

**User**: "Create hooks that enforce tests and builds before stopping"

**File**: `hooks/hooks.json`

```json
{
  "description": "Code quality enforcement",
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review transcript. Check: 1) If code was modified, were tests run? 2) Did tests pass? 3) Was the project built? 4) Were all user questions answered? Return 'approve' to stop or 'block' with specific reason to continue."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-quality.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Example 3: Hybrid Validation

**User**: "Create hooks with fast bash checks plus deep LLM analysis"

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/quick-check.sh",
          "timeout": 5
        },
        {
          "type": "prompt",
          "prompt": "Deep analysis of bash command: $TOOL_INPUT.command. Check for destructive ops, privilege escalation, data exfiltration.",
          "timeout": 15
        }
      ]
    }
  ]
}
```

Both hooks run in parallel — the command hook quickly validates obvious cases while the prompt hook handles nuanced analysis.

## Best Practices

**DO:**
- Use prompt hooks for complex/nuanced validation
- Use `${CLAUDE_PLUGIN_ROOT}` for all file paths
- Quote all bash variables (`"$variable"`)
- Set appropriate timeouts (command: 5-60s, prompt: 15-30s)
- Return structured JSON output
- Use `set -euo pipefail` in all scripts
- Test with `claude --debug`

**DON'T:**
- Use hardcoded absolute paths
- Rely on hook execution order (they run in parallel)
- Create long-running hooks (will timeout)
- Trust user input without validation
- Use prompt hooks on unsupported events (only PreToolUse, Stop, SubagentStop, UserPromptSubmit)

## Output Checklist

When creating hooks, verify:

- [ ] hooks.json has valid JSON syntax
- [ ] Plugin hooks use `{"hooks": {...}}` wrapper format
- [ ] Event names are valid (PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification)
- [ ] Hook types are valid (`prompt` or `command`)
- [ ] Prompt hooks only on supported events (PreToolUse, Stop, SubagentStop, UserPromptSubmit)
- [ ] Matchers use correct format (exact, pipe-separated, wildcard, or regex)
- [ ] Command hooks reference scripts with `${CLAUDE_PLUGIN_ROOT}`
- [ ] Scripts use `set -euo pipefail` and read from stdin
- [ ] Scripts quote all variables and validate inputs
- [ ] Timeouts are reasonable (5-600 seconds)
- [ ] Exit codes are correct (0 = approve, 2 = block)
- [ ] Hooks are independent (don't rely on execution order)

For detailed event specs, see `references/hook-events.md`.
For common patterns, see `references/hook-patterns.md`.
For security best practices, see `references/hook-security.md`.
