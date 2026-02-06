# Common Hook Patterns

Proven patterns for implementing Claude Code hooks.

## Pattern 1: File Write Safety

Block writes to sensitive files and system directories:

```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "prompt",
      "prompt": "File: $TOOL_INPUT.file_path. Verify: 1) Not /etc, /sys, /usr 2) Not .env or credentials 3) No path traversal (..). Return 'approve' or 'deny'."
    }]
  }]
}
```

## Pattern 2: Bash Command Safety

Validate shell commands before execution:

```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "prompt",
      "prompt": "Command: $TOOL_INPUT.command. Check: 1) No destructive ops (rm -rf, dd, mkfs) 2) No privilege escalation (sudo) 3) No unauthorized network access. Return 'approve' or 'deny'."
    }]
  }]
}
```

## Pattern 3: Test Enforcement

Ensure tests run before stopping:

```json
{
  "Stop": [{
    "matcher": "*",
    "hooks": [{
      "type": "prompt",
      "prompt": "If code was modified (Write/Edit used), verify tests were executed. Block if no tests run after code changes."
    }]
  }]
}
```

## Pattern 4: Context Loading

Detect project type and set environment at session start:

```bash
#!/bin/bash
# load-context.sh
set -euo pipefail
cd "$CLAUDE_PROJECT_DIR" || exit 1

if [ -f "package.json" ]; then
  echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
  [ -f "tsconfig.json" ] && echo "export USES_TYPESCRIPT=true" >> "$CLAUDE_ENV_FILE"
elif [ -f "Cargo.toml" ]; then
  echo "export PROJECT_TYPE=rust" >> "$CLAUDE_ENV_FILE"
elif [ -f "go.mod" ]; then
  echo "export PROJECT_TYPE=go" >> "$CLAUDE_ENV_FILE"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  echo "export PROJECT_TYPE=python" >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

## Pattern 5: MCP Tool Monitoring

Protect against destructive MCP operations:

```json
{
  "PreToolUse": [{
    "matcher": "mcp__.*__delete.*",
    "hooks": [{
      "type": "prompt",
      "prompt": "MCP deletion detected. Verify: intentional, reversible, backed up. Return 'approve' only if safe."
    }]
  }]
}
```

## Pattern 6: Build Verification

Ensure project builds after code changes:

```json
{
  "Stop": [{
    "matcher": "*",
    "hooks": [{
      "type": "prompt",
      "prompt": "If Write/Edit tools were used, verify the project was built (npm run build, cargo build, etc). Block if not built."
    }]
  }]
}
```

## Pattern 7: Permission Confirmation

Require user confirmation for destructive operations:

```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "prompt",
      "prompt": "Command: $TOOL_INPUT.command. If contains 'rm', 'delete', 'drop', or destructive ops, return 'ask' for user confirmation. Otherwise 'approve'."
    }]
  }]
}
```

## Pattern 8: Post-Edit Quality Check

Run linters or formatters after file edits:

```bash
#!/bin/bash
# check-quality.sh (PostToolUse command hook)
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ "$file_path" == *.js ]] || [[ "$file_path" == *.ts ]]; then
  npx eslint "$file_path" 2>&1 || true
elif [[ "$file_path" == *.py ]]; then
  ruff check "$file_path" 2>&1 || true
fi
exit 0
```

## Pattern 9: Flag-File Activation

Hooks that only run when explicitly enabled:

```bash
#!/bin/bash
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"
if [ ! -f "$FLAG_FILE" ]; then
  exit 0  # Disabled, skip
fi

# Enabled — run validation
input=$(cat)
# ... validation logic ...
```

Enable: `touch .enable-strict-validation`
Disable: `rm .enable-strict-validation`

## Pattern 10: Configuration-Driven Hooks

Read project config to control behavior:

```bash
#!/bin/bash
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/hook-config.json"
if [ -f "$CONFIG_FILE" ]; then
  strict_mode=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$strict_mode" != "true" ]; then
    exit 0  # Not strict, skip
  fi
fi

input=$(cat)
# ... strict validation logic ...
```

## Pattern 11: Hybrid Validation

Fast command check + deep prompt analysis running in parallel:

```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [
      {"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/quick-check.sh", "timeout": 5},
      {"type": "prompt", "prompt": "Deep analysis of bash command: $TOOL_INPUT.command", "timeout": 15}
    ]
  }]
}
```

## Pattern 12: Cross-Event Workflow

Track state across events using temp files:

**SessionStart** — initialize tracking:
```bash
echo "0" > /tmp/test-count-$$
```

**PostToolUse** — track test execution:
```bash
input=$(cat)
if [[ "$(echo "$input" | jq -r '.tool_name')" == "Bash" ]]; then
  if [[ "$(echo "$input" | jq -r '.tool_result')" == *"test"* ]]; then
    count=$(cat /tmp/test-count-$$ 2>/dev/null || echo "0")
    echo $((count + 1)) > /tmp/test-count-$$
  fi
fi
```

**Stop** — verify based on tracking:
```bash
test_count=$(cat /tmp/test-count-$$ 2>/dev/null || echo "0")
if [ "$test_count" -eq 0 ]; then
  echo '{"decision": "block", "reason": "No tests were run"}' >&2
  exit 2
fi
```

## Choosing Between Prompt and Command

| Criteria | Use Prompt | Use Command |
|----------|-----------|-------------|
| Complex reasoning needed | Yes | No |
| Edge case handling | Yes | No |
| Deterministic check | No | Yes |
| External tool integration | No | Yes |
| Performance critical (< 50ms) | No | Yes |
| Easy to maintain | Yes | Depends |
| No scripting needed | Yes | No |
