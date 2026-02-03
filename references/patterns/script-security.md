<!-- nosec -->
# Script Security Validation

Ensure generated scripts are safe and don't contain dangerous patterns.

## Dangerous Patterns

### Critical (Block Generation)

| Pattern | Risk | Example |
|---------|------|---------|
| `rm -rf /` | System destruction | `rm -rf /` or `rm -rf /*` |
| `rm -rf $VAR` | Unquoted variable deletion | `rm -rf $DIR` (if DIR empty) |
| `eval "$input"` | Code injection | `eval "$USER_INPUT"` |
| `bash -c "$var"` | Command injection | `bash -c "$CMD"` |
| `curl \| bash` | Remote code execution | `curl url \| bash` |
| `wget -O- \| sh` | Remote code execution | `wget url -O- \| sh` |
| `chmod 777` | Insecure permissions | `chmod 777 /path` |
| `: > /etc/` | System file overwrite | `: > /etc/passwd` |

### High Risk (Require Review)

| Pattern | Risk | Safer Alternative |
|---------|------|-------------------|
| `rm -rf` | Recursive delete | Use specific paths, `--` |
| `eval` | Dynamic execution | Use arrays, case statements |
| `sudo` | Privilege escalation | Avoid in skill scripts |
| `> /dev/sda` | Device write | Never write to devices |
| Unquoted `$*` | Word splitting | Use `"$@"` |

## Security Check Algorithm

```markdown
FUNCTION validate_script_security(script_content):
    errors = []
    warnings = []

    # Critical patterns (block)
    critical_patterns = [
        {pattern: 'rm\s+-rf\s+/', message: "Dangerous: rm -rf with root path"},
        {pattern: 'rm\s+-rf\s+/\*', message: "Dangerous: rm -rf /*"},
        {pattern: 'rm\s+-rf\s+\$[^{]', message: "Dangerous: rm -rf with unquoted variable"},
        {pattern: 'eval\s+["\']?\$', message: "Dangerous: eval with variable"},
        {pattern: 'bash\s+-c\s+["\']?\$', message: "Dangerous: bash -c with variable"},
        {pattern: 'curl.*\|\s*bash', message: "Dangerous: curl pipe to bash"},
        {pattern: 'wget.*\|\s*(ba)?sh', message: "Dangerous: wget pipe to shell"},
        {pattern: '>\s*/etc/', message: "Dangerous: writing to /etc"},
        {pattern: '>\s*/dev/[hs]d', message: "Dangerous: writing to device"},
    ]

    FOR pattern in critical_patterns:
        IF matches(script_content, pattern.pattern):
            errors.append({
                severity: "critical",
                message: pattern.message,
                action: "Remove or rewrite this pattern"
            })

    # High risk patterns (warn)
    high_risk_patterns = [
        {pattern: 'rm\s+-rf', message: "rm -rf detected - verify path is safe"},
        {pattern: '\beval\b', message: "eval detected - consider alternatives"},
        {pattern: '\bsudo\b', message: "sudo detected - skills shouldn't need root"},
        {pattern: 'chmod\s+777', message: "chmod 777 is insecure"},
        {pattern: '\$\*[^"]', message: "Unquoted $* - use \"$@\" instead"},
    ]

    FOR pattern in high_risk_patterns:
        IF matches(script_content, pattern.pattern):
            warnings.append({
                severity: "high",
                message: pattern.message
            })

    RETURN {
        safe: len(errors) == 0,
        errors: errors,
        warnings: warnings
    }
```

## Safe Patterns

### Safe Deletion

```bash
# Bad: Unquoted variable could be empty
rm -rf $TARGET

# Good: Quoted, with safety check
if [[ -n "$TARGET" && "$TARGET" != "/" ]]; then
    rm -rf "$TARGET"
fi

# Better: Use specific known path
rm -rf "${SKILL_DIR:?}/output"
```

### Safe Command Execution

```bash
# Bad: eval with user input
eval "$USER_CMD"

# Good: Use case statement
case "$ACTION" in
    build) run_build ;;
    test) run_test ;;
    *) die "Unknown action: $ACTION" ;;
esac

# Good: Use array
commands=("$CMD" "$ARG1" "$ARG2")
"${commands[@]}"
```

### Safe File Operations

```bash
# Bad: Writing to arbitrary path
cat data > "$USER_PATH"

# Good: Validate path first
validate_path() {
    local path="$1"
    # Ensure not system path
    [[ "$path" != /* ]] || [[ "$path" == "$HOME"/* ]] || return 1
    # Ensure no path traversal
    [[ "$path" != *..* ]] || return 1
    return 0
}

if validate_path "$USER_PATH"; then
    cat data > "$USER_PATH"
fi
```

## Validation Script

```bash
#!/usr/bin/env bash
# validate-script-security.sh - Check script for dangerous patterns

check_script() {
    local script="$1"
    local errors=0

    # Critical patterns
    if grep -qE 'rm\s+-rf\s+/($|[^a-zA-Z])' "$script"; then
        echo "CRITICAL: rm -rf with root path"
        ((errors++))
    fi

    if grep -qE 'eval\s+["\x27]?\$' "$script"; then
        echo "CRITICAL: eval with variable"
        ((errors++))
    fi

    if grep -qE 'curl.*\|\s*(ba)?sh' "$script"; then
        echo "CRITICAL: curl pipe to shell"
        ((errors++))
    fi

    # High risk patterns
    if grep -qE 'rm\s+-rf' "$script"; then
        echo "WARNING: rm -rf detected - verify safety"
    fi

    if grep -qE 'chmod\s+777' "$script"; then
        echo "WARNING: chmod 777 is insecure"
    fi

    return $errors
}
```

## Integration

### Generation Phase

Before writing any script:
1. Run security validation on content
2. Block if critical patterns found
3. Log warnings for review
4. Only write if validation passes

### Post-Generation Check

After all scripts generated:
1. Run shellcheck on all .sh files
2. Run security validation
3. Report any issues
4. Require manual approval for warnings

## Safe Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Safety: Prevent accidental root operations
[[ "$(id -u)" != "0" ]] || die "Do not run as root"

# Safety: Validate all paths
validate_path() {
    local path="$1"
    [[ -n "$path" ]] || return 1
    [[ "$path" != "/" ]] || return 1
    [[ "$path" != /etc/* ]] || return 1
    [[ "$path" != /usr/* ]] || return 1
    [[ "$path" != /bin/* ]] || return 1
    return 0
}

# Safety: Use parameter expansion with defaults
readonly OUTPUT_DIR="${OUTPUT_DIR:-./output}"
validate_path "$OUTPUT_DIR" || die "Invalid output path"
```
