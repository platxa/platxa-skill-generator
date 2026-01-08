# Error Handling Patterns

Graceful error handling with proper return codes for scripts.

## Exit Code Convention

| Code | Meaning | When to Use |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Error | Operation failed |
| 2 | Warning | Partial success or non-critical issue |
| 126 | Not executable | Permission denied |
| 127 | Not found | Command not found |
| 130 | Interrupted | Ctrl+C (SIGINT) |

## Bash Error Handling

### Safety Options

```bash
#!/usr/bin/env bash
set -euo pipefail

# -e: Exit on error
# -u: Error on undefined variable
# -o pipefail: Fail if any pipe command fails
```

### Error Functions

```bash
# Print error and exit
die() {
    echo "ERROR: $*" >&2
    exit 1
}

# Print warning (don't exit)
warn() {
    echo "WARNING: $*" >&2
}

# Print error without exiting
error() {
    echo "ERROR: $*" >&2
}
```

### Try-Catch Pattern

```bash
# Trap errors
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_number=$2
    echo "ERROR: Command failed at line $line_number with exit code $exit_code" >&2
    cleanup
    exit "$exit_code"
}

cleanup() {
    # Remove temp files, restore state
    rm -f "$TEMP_FILE" 2>/dev/null || true
}
```

### Graceful Degradation

```bash
# Check command exists before using
if command -v jq >/dev/null 2>&1; then
    result=$(echo "$json" | jq -r '.key')
else
    warn "jq not found, using fallback parser"
    result=$(grep -o '"key":"[^"]*"' <<< "$json" | cut -d'"' -f4)
fi
```

### Validate Before Action

```bash
validate_inputs() {
    local target="$1"

    # Check target exists
    [[ -e "$target" ]] || die "Target not found: $target"

    # Check readable
    [[ -r "$target" ]] || die "Cannot read: $target"

    # Check is expected type
    [[ -d "$target" ]] || die "Not a directory: $target"
}
```

## Python Error Handling

### Exception Hierarchy

```python
class SkillError(Exception):
    """Base exception for skill operations."""
    pass

class ValidationError(SkillError):
    """Validation failed."""
    pass

class InstallationError(SkillError):
    """Installation failed."""
    pass

class ConfigurationError(SkillError):
    """Invalid configuration."""
    pass
```

### Main Function Pattern

```python
def main(argv: list[str] | None = None) -> int:
    """Main entry point with proper error handling."""
    try:
        args = parse_args(argv)
        return run(args)
    except ValidationError as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        return 126
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
```

### Context Managers

```python
from contextlib import contextmanager
from pathlib import Path
import tempfile

@contextmanager
def temp_directory():
    """Create temp directory, cleanup on exit."""
    tmpdir = Path(tempfile.mkdtemp())
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# Usage
with temp_directory() as tmp:
    process_files(tmp)
# Automatically cleaned up
```

### Result Types

```python
from typing import NamedTuple

class Result(NamedTuple):
    """Operation result with status and message."""
    success: bool
    message: str
    data: dict | None = None

def validate_skill(path: Path) -> Result:
    """Validate skill, return result object."""
    if not path.exists():
        return Result(False, f"Path not found: {path}")

    errors = run_checks(path)
    if errors:
        return Result(False, f"Validation failed: {len(errors)} errors", {"errors": errors})

    return Result(True, "Validation passed")
```

## Error Messages

### Good Error Messages

```
ERROR: SKILL.md not found in /path/to/skill
  Expected: /path/to/skill/SKILL.md
  Action: Create SKILL.md with valid frontmatter

ERROR: Name exceeds 64 characters (found: 78)
  Name: "my-extremely-long-skill-name-that-exceeds-the-limit"
  Action: Shorten to 64 characters or less

WARNING: Description approaching limit (980/1024 chars)
  Consider shortening for future additions
```

### Bad Error Messages

```
ERROR: Invalid input
ERROR: Operation failed
ERROR: Something went wrong
```

### Message Template

```python
def format_error(
    error_type: str,
    message: str,
    details: dict | None = None,
    action: str | None = None,
) -> str:
    """Format error message with context."""
    lines = [f"ERROR: {message}"]

    if details:
        for key, value in details.items():
            lines.append(f"  {key}: {value}")

    if action:
        lines.append(f"  Action: {action}")

    return "\n".join(lines)
```

## Recovery Strategies

### Retry Pattern

```python
import time
from typing import TypeVar, Callable

T = TypeVar("T")

def retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 1.0,
) -> T:
    """Retry function with exponential backoff."""
    last_error = None

    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))

    raise last_error
```

### Fallback Pattern

```python
def get_config(key: str) -> str:
    """Get config with fallback chain."""
    # Try environment variable
    value = os.environ.get(f"SKILL_{key.upper()}")
    if value:
        return value

    # Try config file
    config_file = Path.home() / ".claude" / "config.json"
    if config_file.exists():
        config = json.loads(config_file.read_text())
        if key in config:
            return config[key]

    # Use default
    defaults = {"output_dir": "./output", "format": "markdown"}
    return defaults.get(key, "")
```

## Validation with Errors

```python
def validate_with_errors(path: Path) -> tuple[bool, list[str], list[str]]:
    """Validate and collect all errors/warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check SKILL.md
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md")
    else:
        content = skill_md.read_text()
        if len(content.splitlines()) > 500:
            errors.append(f"SKILL.md exceeds 500 lines")
        elif len(content.splitlines()) > 450:
            warnings.append("SKILL.md approaching 500 line limit")

    # Continue checks...

    passed = len(errors) == 0
    return passed, errors, warnings
```

## Integration

Scripts should:
1. Use proper exit codes (0/1/2)
2. Print errors to stderr
3. Provide actionable error messages
4. Clean up on failure
5. Support --quiet and --verbose flags
