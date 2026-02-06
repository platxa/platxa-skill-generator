# Hook Events Reference

Detailed specification for all 9 Claude Code hook events.

## PreToolUse

Execute before any tool runs. The most commonly used hook event.

**When:** Before Read, Write, Edit, Bash, Grep, Glob, or any tool executes.

**Supported hook types:** prompt, command

**Input fields:** `tool_name`, `tool_input`

**Output:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

- `allow` — approve the tool use
- `deny` — block the tool use silently
- `ask` — prompt the user for confirmation
- `updatedInput` — modify tool input before execution (optional)

**Common matchers:**
- `Write|Edit` — file modification operations
- `Bash` — shell command execution
- `mcp__.*__delete.*` — MCP delete operations
- `*` — all tool uses

**Example:**
```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "prompt",
    "prompt": "File: $TOOL_INPUT.file_path. Check: system paths, credentials, path traversal. Return 'approve' or 'deny'."
  }]
}
```

## PostToolUse

Execute after a tool completes. Use for feedback, logging, or quality checks.

**When:** After any tool finishes execution.

**Supported hook types:** command (prompt not fully supported)

**Input fields:** `tool_name`, `tool_input`, `tool_result`

**Output behavior:**
- Exit 0: stdout shown in transcript
- Exit 2: stderr fed back to Claude as error
- `systemMessage` included in context

**Example:**
```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/post-edit-check.sh"
  }]
}
```

**Use cases:** Run linters after edits, log tool usage, track metrics.

## Stop

Execute when the main agent considers stopping. Use to verify task completeness.

**When:** Claude is about to end its turn.

**Supported hook types:** prompt, command

**Input fields:** `reason`

**Output:**
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

- `approve` — allow Claude to stop
- `block` — force Claude to continue with the given reason

**Example:**
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "prompt",
    "prompt": "Verify task completion: tests run, build succeeded, questions answered. Return 'approve' to stop or 'block' with reason."
  }]
}
```

## SubagentStop

Execute when a subagent considers stopping. Same output format as Stop.

**When:** A Task-spawned subagent is about to end.

**Supported hook types:** prompt, command

**Use cases:** Ensure subagents complete their assigned tasks fully.

## UserPromptSubmit

Execute when user submits a prompt. Use to add context or validate input.

**When:** User presses Enter to submit a message.

**Supported hook types:** prompt, command

**Input fields:** `user_prompt`

**Example:**
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "prompt",
    "prompt": "If prompt discusses auth, permissions, or API security, return relevant security warnings as systemMessage."
  }]
}
```

## SessionStart

Execute when Claude Code session begins. Use to load context and set environment.

**When:** Claude Code starts up.

**Supported hook types:** command only

**Special:** Can persist environment variables via `$CLAUDE_ENV_FILE`:
```bash
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

**Example:**
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
    "timeout": 10
  }]
}
```

## SessionEnd

Execute when session ends. Use for cleanup and logging.

**When:** Claude Code session terminates.

**Supported hook types:** command only

**Use cases:** Save state, clean up temp files, send analytics.

## PreCompact

Execute before context compaction. Use to preserve critical information.

**When:** Context window is about to be compressed.

**Supported hook types:** command only

**Use cases:** Add critical context that must survive compaction via `systemMessage`.

## Notification

Execute when Claude sends notifications.

**When:** A notification is triggered.

**Supported hook types:** command only

**Use cases:** Logging, forwarding to external systems (Slack, email).

## Event Compatibility Matrix

| Event | Prompt Hooks | Command Hooks | Has Matcher |
|-------|-------------|---------------|-------------|
| PreToolUse | Yes | Yes | Yes (tool name) |
| PostToolUse | Limited | Yes | Yes (tool name) |
| Stop | Yes | Yes | Yes (usually `*`) |
| SubagentStop | Yes | Yes | Yes (usually `*`) |
| UserPromptSubmit | Yes | Yes | Yes (usually `*`) |
| SessionStart | No | Yes | Yes (usually `*`) |
| SessionEnd | No | Yes | Yes (usually `*`) |
| PreCompact | No | Yes | Yes (usually `*`) |
| Notification | No | Yes | Yes (usually `*`) |
