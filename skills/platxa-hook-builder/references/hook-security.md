# Hook Security Best Practices

Security patterns and guidelines for Claude Code hook scripts.

## Script Safety Fundamentals

### Always Start With

```bash
#!/bin/bash
set -euo pipefail
```

- `set -e` — exit on error
- `set -u` — error on unset variables
- `set -o pipefail` — pipe failures propagate

### Read Input Safely

```bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
```

Always use `jq` for JSON parsing. Always use `// empty` for optional fields.

### Quote All Variables

```bash
# GOOD: Quoted (safe)
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"
if [ -f "$config_file" ]; then

# BAD: Unquoted (injection risk)
echo $file_path
cd $CLAUDE_PROJECT_DIR
if [ -f $config_file ]; then
```

### Validate Input Fields

```bash
# Check field exists before using
if [ -z "$file_path" ]; then
  exit 0  # Nothing to validate
fi

# Validate format
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Invalid tool name"}' >&2
  exit 2
fi
```

## Path Safety

### Check for Path Traversal

```bash
if [[ "$file_path" == *".."* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Path traversal detected"}' >&2
  exit 2
fi
```

### Block System Directories

```bash
if [[ "$file_path" == /etc/* ]] || [[ "$file_path" == /sys/* ]] || [[ "$file_path" == /usr/* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "System directory write blocked"}' >&2
  exit 2
fi
```

### Block Sensitive Files

```bash
if [[ "$file_path" == *.env ]] || [[ "$file_path" == *secret* ]] || [[ "$file_path" == *credentials* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "ask"}, "systemMessage": "Sensitive file detected"}' >&2
  exit 2
fi
```

## Command Safety

### Block Destructive Operations

```bash
command=$(echo "$input" | jq -r '.tool_input.command // empty')

if [[ "$command" == *"rm -rf"* ]] || [[ "$command" == *"rm -fr"* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Destructive command blocked"}' >&2
  exit 2
fi

if [[ "$command" == *"dd if="* ]] || [[ "$command" == *"mkfs"* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Dangerous system operation blocked"}' >&2
  exit 2
fi
```

### Check Privilege Escalation

```bash
if [[ "$command" == sudo* ]] || [[ "$command" == su* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "ask"}, "systemMessage": "Elevated privileges requested"}' >&2
  exit 2
fi
```

## Secret Detection

### Scan Content for Secrets

```bash
content=$(echo "$input" | jq -r '.tool_input.content // empty')

if echo "$content" | grep -qE "(api[_-]?key|password|secret|token).{0,20}['\"]?[A-Za-z0-9]{20,}"; then
  echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Potential secret in content"}' >&2
  exit 2
fi
```

## Rate Limiting

Prevent excessive operations:

```bash
rate_file="/tmp/hook-rate-$$"
current_minute=$(date +%Y%m%d%H%M)

if [ -f "$rate_file" ]; then
  last_minute=$(head -1 "$rate_file")
  count=$(tail -1 "$rate_file")
  if [ "$current_minute" = "$last_minute" ] && [ "$count" -gt 10 ]; then
    echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Rate limit exceeded"}' >&2
    exit 2
  fi
  [ "$current_minute" = "$last_minute" ] && count=$((count + 1)) || count=1
else
  count=1
fi

echo "$current_minute" > "$rate_file"
echo "$count" >> "$rate_file"
```

## Audit Logging

Log all operations for security review:

```bash
timestamp=$(date -Iseconds)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
echo "$timestamp | $USER | $tool_name" >> ~/.claude/audit.log
exit 0
```

## Timeout Guidelines

| Hook Type | Recommended | Maximum |
|-----------|------------|---------|
| Quick command check | 5s | 30s |
| Standard command | 10-30s | 60s |
| Prompt hook | 15-30s | 60s |
| SessionStart | 5-10s | 30s |

Default timeouts: Command hooks (60s), Prompt hooks (30s).

## Error Output

Always send error messages to stderr with JSON:

```bash
# Deny with reason (exit 2 + stderr)
echo '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "Reason"}' >&2
exit 2

# Non-blocking warning (exit 0 + stdout)
echo '{"continue": true, "systemMessage": "Warning message"}'
exit 0
```

## Security Checklist

- [ ] Scripts start with `set -euo pipefail`
- [ ] All variables are quoted
- [ ] Input fields validated before use
- [ ] Path traversal checked (`..`)
- [ ] System directories blocked
- [ ] Sensitive files protected
- [ ] Secrets not logged
- [ ] Timeouts set appropriately
- [ ] Error messages go to stderr
- [ ] JSON output is valid
- [ ] No hardcoded paths (use `${CLAUDE_PLUGIN_ROOT}`)
- [ ] Exit codes are correct (0 or 2)
