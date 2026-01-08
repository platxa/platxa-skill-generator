# Bash Script Generator

Generate shellcheck-compliant, executable bash scripts.

## Shellcheck Compliance

### Required Practices

```bash
#!/usr/bin/env bash
set -euo pipefail

# SC2086: Quote variables to prevent word splitting
echo "$variable"  # Good
echo $variable    # Bad - SC2086

# SC2046: Quote command substitution
files="$(find . -name "*.md")"  # Good
files=$(find . -name "*.md")    # Risky - SC2046

# SC2155: Declare and assign separately
local exit_code
exit_code="$?"  # Good
local exit_code="$?"  # Bad - SC2155

# SC2164: Use || exit after cd
cd "$dir" || exit 1  # Good
cd "$dir"            # Bad - SC2164
```

### Common Shellcheck Warnings to Avoid

| Code | Issue | Fix |
|------|-------|-----|
| SC2086 | Unquoted variable | Quote: `"$var"` |
| SC2046 | Unquoted command sub | Quote: `"$(cmd)"` |
| SC2155 | Declare/assign together | Separate lines |
| SC2164 | cd without || exit | Add `|| exit 1` |
| SC2181 | Check exit code directly | Use `if cmd; then` |
| SC2034 | Unused variable | Remove or use |
| SC2162 | read without -r | Add `-r` flag |

## Script Template

```bash
#!/usr/bin/env bash
#
# {script_name} - {brief_description}
#
# Usage: {script_name} [OPTIONS] <arguments>
#
# Options:
#   -h, --help     Show this help message
#   -v, --verbose  Enable verbose output
#   -q, --quiet    Suppress non-error output
#
# Exit codes:
#   0  Success
#   1  Error
#   2  Warning (partial success)
#

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults
VERBOSE=0
QUIET=0

#######################################
# Print usage information
#######################################
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <arguments>

Options:
  -h, --help     Show this help message
  -v, --verbose  Enable verbose output
  -q, --quiet    Suppress non-error output

EOF
}

#######################################
# Print error message and exit
# Arguments:
#   Error message
#######################################
die() {
    echo "ERROR: $*" >&2
    exit 1
}

#######################################
# Print warning message
# Arguments:
#   Warning message
#######################################
warn() {
    echo "WARNING: $*" >&2
}

#######################################
# Print info message (if not quiet)
# Arguments:
#   Info message
#######################################
info() {
    [[ $QUIET -eq 0 ]] && echo "INFO: $*"
}

#######################################
# Print debug message (if verbose)
# Arguments:
#   Debug message
#######################################
debug() {
    [[ $VERBOSE -eq 1 ]] && echo "DEBUG: $*" >&2
}

#######################################
# Parse command line arguments
# Globals:
#   VERBOSE, QUIET
# Arguments:
#   Command line args
#######################################
parse_args() {
    local positional=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            -q|--quiet)
                QUIET=1
                shift
                ;;
            --)
                shift
                positional+=("$@")
                break
                ;;
            -*)
                die "Unknown option: $1"
                ;;
            *)
                positional+=("$1")
                shift
                ;;
        esac
    done

    # Restore positional parameters
    set -- "${positional[@]}"

    # Validate required arguments
    # [[ $# -ge 1 ]] || die "Missing required argument"
}

#######################################
# Main function
# Arguments:
#   Command line args
#######################################
main() {
    parse_args "$@"

    # Script logic here
    info "Starting $SCRIPT_NAME"

    # Return success
    return 0
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Generation Algorithm

```markdown
FUNCTION generate_script(script_spec):
    content = []

    # Header
    content.append(generate_header(script_spec))

    # Safety options
    content.append("set -euo pipefail")
    content.append("")

    # Constants
    content.append(generate_constants(script_spec))

    # Helper functions
    content.append(generate_helpers())

    # Custom functions
    FOR func in script_spec.functions:
        content.append(generate_function(func))

    # Argument parsing
    IF script_spec.has_args:
        content.append(generate_arg_parser(script_spec.args))

    # Main function
    content.append(generate_main(script_spec))

    # Entry point
    content.append(generate_entry_point())

    RETURN "\n".join(content)
```

## Script Types

### Validation Scripts

```bash
validate() {
    local target="$1"
    local errors=0
    local warnings=0

    # Check existence
    [[ -e "$target" ]] || { warn "Target not found: $target"; return 1; }

    # Run checks
    check_structure "$target" || ((errors++))
    check_content "$target" || ((warnings++))

    # Report
    if [[ $errors -gt 0 ]]; then
        die "Validation failed with $errors errors"
    elif [[ $warnings -gt 0 ]]; then
        warn "Validation passed with $warnings warnings"
        return 2
    else
        info "Validation passed"
        return 0
    fi
}
```

### Installation Scripts

```bash
install() {
    local source="$1"
    local dest="$2"

    # Validate source
    [[ -d "$source" ]] || die "Source not found: $source"

    # Create destination
    mkdir -p "$dest" || die "Cannot create: $dest"

    # Copy files
    cp -r "$source"/* "$dest/" || die "Copy failed"

    # Set permissions
    chmod +x "$dest/scripts/"*.sh 2>/dev/null || true

    info "Installed to: $dest"
}
```

### Generation Scripts

```bash
generate() {
    local input="$1"
    local output="$2"

    # Validate input
    [[ -f "$input" ]] || die "Input not found: $input"

    # Create output directory
    mkdir -p "$(dirname "$output")" || die "Cannot create output dir"

    # Generate
    process_input "$input" > "$output" || die "Generation failed"

    info "Generated: $output"
}
```

## Portability Guidelines

### Use POSIX-Compatible Features

```bash
# Good: POSIX compatible
if [ -f "$file" ]; then
    echo "exists"
fi

# Bash-specific (document if used)
if [[ -f "$file" ]]; then  # Bash only
    echo "exists"
fi
```

### Handle Missing Commands

```bash
# Check for required commands
require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

require_cmd jq
require_cmd curl
```

## Testing Scripts

```bash
# Test basic execution
./scripts/validate.sh --help
echo $?  # Should be 0

# Test with valid input
./scripts/validate.sh /path/to/skill
echo $?  # Should be 0 or 2

# Test with invalid input
./scripts/validate.sh /nonexistent
echo $?  # Should be 1
```

## Integration

### Generation Phase

1. Read script plan from architecture
2. Generate each script using template
3. Customize based on script type
4. Write to scripts/ directory
5. Make executable (chmod +x)
6. Verify shellcheck passes
