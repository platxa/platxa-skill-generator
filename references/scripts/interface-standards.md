# Script Interface Standards

Standard interface patterns for all skill scripts.

## Required Flags

| Flag | Short | Description | Required |
|------|-------|-------------|----------|
| `--help` | `-h` | Show usage information | Yes |
| `--verbose` | `-v` | Enable verbose output | Yes |
| `--version` | `-V` | Show script version | Recommended |
| `--dry-run` | `-n` | Preview without changes | For write operations |
| `--quiet` | `-q` | Suppress non-error output | Recommended |

## Bash Script Template

```bash
#!/bin/bash
# script-name.sh - Brief description
#
# Usage: script-name.sh [OPTIONS] <required-arg>
#
# Options:
#   -h, --help      Show this help message
#   -v, --verbose   Enable verbose output
#   -V, --version   Show version
#   -n, --dry-run   Preview without making changes
#   -q, --quiet     Suppress non-error output

set -euo pipefail

# Script metadata
SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="1.0.0"

# Default options
VERBOSE=false
DRY_RUN=false
QUIET=false

# Colors (disabled if not terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Logging functions
log_info() {
    if [[ "$QUIET" != true ]]; then
        echo -e "${BLUE}INFO:${NC} $1"
    fi
}

log_success() {
    if [[ "$QUIET" != true ]]; then
        echo -e "${GREEN}OK:${NC} $1"
    fi
}

log_warn() {
    echo -e "${YELLOW}WARN:${NC} $1" >&2
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

log_verbose() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${BLUE}DEBUG:${NC} $1"
    fi
}

# Usage function
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <required-arg>

Brief description of what this script does.

Arguments:
  required-arg    Description of required argument

Options:
  -h, --help      Show this help message and exit
  -v, --verbose   Enable verbose output
  -V, --version   Show version information
  -n, --dry-run   Preview changes without executing
  -q, --quiet     Suppress informational output

Examples:
  $SCRIPT_NAME input.txt
  $SCRIPT_NAME --verbose --dry-run input.txt

EOF
    exit 0
}

# Version function
version() {
    echo "$SCRIPT_NAME version $SCRIPT_VERSION"
    exit 0
}

# Parse arguments
parse_args() {
    local positional=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -V|--version)
                version
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -q|--quiet)
                QUIET=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                echo "Use --help for usage information" >&2
                exit 1
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
    if [[ ${#positional[@]} -lt 1 ]]; then
        log_error "Missing required argument"
        echo "Use --help for usage information" >&2
        exit 1
    fi

    # Export positional args
    REQUIRED_ARG="${positional[0]}"
}

# Main function
main() {
    parse_args "$@"

    log_verbose "Starting $SCRIPT_NAME"
    log_verbose "Arguments: REQUIRED_ARG=$REQUIRED_ARG"
    log_verbose "Options: VERBOSE=$VERBOSE, DRY_RUN=$DRY_RUN, QUIET=$QUIET"

    # Main script logic here
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would process: $REQUIRED_ARG"
    else
        log_info "Processing: $REQUIRED_ARG"
        # Actual processing...
    fi

    log_success "Completed successfully"
}

# Run main
main "$@"
```

## Python Script Template

```python
#!/usr/bin/env python3
"""Script description.

Usage:
    script_name.py [OPTIONS] <required_arg>

Examples:
    script_name.py input.txt
    script_name.py --verbose --dry-run input.txt
"""

import argparse
import logging
import sys
from pathlib import Path

__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Configure logging based on verbosity flags."""
    if quiet:
        logging.root.setLevel(logging.ERROR)
    elif verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Brief description of what this script does.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt
  %(prog)s --verbose --dry-run input.txt
        """
    )

    # Positional arguments
    parser.add_argument(
        "required_arg",
        type=str,
        help="Description of required argument"
    )

    # Standard flags
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress informational output"
    )

    # Script-specific arguments
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout)"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose, args.quiet)

    logger.debug(f"Arguments: {args}")

    try:
        if args.dry_run:
            logger.info(f"[DRY RUN] Would process: {args.required_arg}")
        else:
            logger.info(f"Processing: {args.required_arg}")
            # Actual processing...

        logger.info("Completed successfully")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Exit Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | General error | Unspecified error |
| 2 | Usage error | Invalid arguments or options |
| 3 | Input error | Missing or invalid input file |
| 4 | Output error | Cannot write output |
| 5 | Validation error | Content validation failed |

```bash
# Exit code constants
EXIT_SUCCESS=0
EXIT_ERROR=1
EXIT_USAGE=2
EXIT_INPUT=3
EXIT_OUTPUT=4
EXIT_VALIDATION=5
```

## Output Format Standards

### Standard Output

```bash
# Success messages to stdout
echo "Processing file.txt"
echo "Generated 5 files"

# Structured output for parsing
echo "FILE: output.md"
echo "TOKENS: 1234"
echo "STATUS: success"
```

### Standard Error

```bash
# Errors always to stderr
echo "Error: File not found" >&2
echo "Warning: Deprecated option" >&2
```

### Verbose Output

```bash
# Only when --verbose
log_verbose "Reading configuration from config.yaml"
log_verbose "Found 10 entries to process"
log_verbose "Skipping entry: invalid format"
```

## Validation Function

```python
def validate_script_interface(script_path: str) -> list[str]:
    """Validate script follows interface standards."""
    errors = []

    content = Path(script_path).read_text()

    # Check for --help
    if "--help" not in content and "-h" not in content:
        errors.append("Missing --help/-h flag support")

    # Check for --verbose
    if "--verbose" not in content and "-v" not in content:
        errors.append("Missing --verbose/-v flag support")

    # Check for usage function/docstring
    if script_path.endswith(".sh"):
        if "usage()" not in content and "Usage:" not in content:
            errors.append("Missing usage function")
    elif script_path.endswith(".py"):
        if "argparse" not in content:
            errors.append("Missing argparse for argument handling")

    # Check for proper exit codes
    if script_path.endswith(".sh"):
        if "exit 0" not in content and "exit $?" not in content:
            errors.append("Missing explicit exit code")

    # Check for error handling
    if script_path.endswith(".sh"):
        if "set -e" not in content and "set -euo pipefail" not in content:
            errors.append("Missing 'set -e' for error handling")

    return errors
```

## Interface Compliance Checklist

```markdown
## Script Interface Checklist

- [ ] Accepts --help/-h flag
- [ ] Accepts --verbose/-v flag
- [ ] Shows version with --version/-V
- [ ] Uses standard exit codes
- [ ] Errors go to stderr
- [ ] Supports --dry-run for write operations
- [ ] Has usage documentation
- [ ] Validates required arguments
- [ ] Handles missing files gracefully
- [ ] Works with stdin/stdout when appropriate
```
