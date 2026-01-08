#!/bin/bash
# security-check.sh - Scan scripts for dangerous patterns
#
# Usage: security-check.sh <skill-directory>
#
# Checks for:
# - Dangerous commands (rm -rf /, etc.)
# - Credential exposure
# - Unsafe eval/exec usage
# - Network access without validation

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}SECURITY:${NC} $1" >&2
    ((ERRORS++)) || true
}

warn() {
    echo -e "${YELLOW}WARN:${NC} $1" >&2
    ((WARNINGS++)) || true
}

info() {
    echo -e "${GREEN}OK:${NC} $1"
}

usage() {
    echo "Usage: $0 <skill-directory>"
    echo ""
    echo "Scan skill scripts for security issues."
    exit 1
}

SKILL_DIR="${1:-}"

if [[ -z "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Skill directory required" >&2
    usage
fi

SKILL_NAME=$(basename "$SKILL_DIR")

echo "Security Check: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Find all scripts
SCRIPTS_DIR="$SKILL_DIR/scripts"
if [[ ! -d "$SCRIPTS_DIR" ]]; then
    info "No scripts directory - nothing to check"
    exit 0
fi

SCRIPTS=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f 2>/dev/null || echo "")

if [[ -z "$SCRIPTS" ]]; then
    info "No scripts found"
    exit 0
fi

SCRIPT_COUNT=$(echo "$SCRIPTS" | wc -l)
echo "Scanning $SCRIPT_COUNT script(s)..."
echo ""

# Dangerous patterns for bash
# shellcheck disable=SC2016  # Intentionally literal strings for pattern matching
BASH_DANGEROUS=(
    'rm -rf /'
    'rm -rf /*'
    'rm -rf ~'
    'rm -rf $HOME'
    ':(){:|:&};:'          # Fork bomb
    'mkfs\.'               # Format filesystem
    'dd if=/dev/zero'
    'dd if=/dev/random'
    '> /dev/sda'
    'chmod -R 777 /'
    'chmod 777 /'
    'wget.*\| *sh'         # Pipe to shell
    'curl.*\| *sh'
    'curl.*\| *bash'
    'wget.*\| *bash'
    '\$\(.*\)\s*>\s*/etc/' # Write to /etc
    'eval "\$\('           # Dangerous eval
    'sudo\s+rm'            # sudo rm
    'sudo\s+chmod'         # sudo chmod on system
)

# Dangerous patterns for Python
PYTHON_DANGEROUS=(
    'os\.system\('
    'subprocess\.call\(.*shell=True'
    'subprocess\.Popen\(.*shell=True'
    'eval\('
    'exec\('
    '__import__\('
    'pickle\.loads?\('     # Unsafe deserialization
    'yaml\.load\([^,]*\)'  # Unsafe YAML load (no Loader)
    'os\.remove\(.*/'
    'shutil\.rmtree\(.*/'
    'open\(.*/etc/'
)

# Credential patterns
CREDENTIAL_PATTERNS=(
    'password\s*='
    'passwd\s*='
    'api_key\s*='
    'apikey\s*='
    'secret\s*='
    'token\s*='
    'AWS_ACCESS_KEY'
    'AWS_SECRET'
    'GITHUB_TOKEN'
    'ANTHROPIC_API_KEY'
    'OPENAI_API_KEY'
)

# Check each script
for script in $SCRIPTS; do
    script_name=$(basename "$script")
    echo "Checking: $script_name"

    content=$(cat "$script")

    # Check bash scripts
    if [[ "$script" == *.sh ]]; then
        for pattern in "${BASH_DANGEROUS[@]}"; do
            if echo "$content" | grep -qE "$pattern"; then
                error "$script_name: Dangerous pattern found: $pattern"
            fi
        done

        # Check for unquoted variables in rm
        if echo "$content" | grep -qE 'rm\s+(-[rf]+\s+)?\$[^"'\'']*[^"]$'; then
            warn "$script_name: Unquoted variable in rm command"
        fi

        # Check for eval with user input
        if echo "$content" | grep -qE 'eval\s+.*\$[0-9@*]'; then
            error "$script_name: eval with positional parameters is dangerous"
        fi
    fi

    # Check Python scripts
    if [[ "$script" == *.py ]]; then
        for pattern in "${PYTHON_DANGEROUS[@]}"; do
            if echo "$content" | grep -qE "$pattern"; then
                # Check if it's in a comment
                match_line=$(echo "$content" | grep -E "$pattern" | head -1)
                if [[ ! "$match_line" =~ ^[[:space:]]*# ]]; then
                    error "$script_name: Dangerous pattern found: $pattern"
                fi
            fi
        done

        # Check for subprocess without shell=False explicit
        if echo "$content" | grep -qE 'subprocess\.(call|run|Popen)\(' && \
           ! echo "$content" | grep -qE 'shell\s*=\s*False'; then
            warn "$script_name: subprocess without explicit shell=False"
        fi
    fi

    # Check for hardcoded credentials
    for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
        if echo "$content" | grep -qiE "$pattern"; then
            # Check it's not just reading from env
            match_line=$(echo "$content" | grep -iE "$pattern" | head -1)
            if [[ ! "$match_line" =~ os\.environ ]] && \
               [[ ! "$match_line" =~ \$\{ ]] && \
               [[ ! "$match_line" =~ getenv ]]; then
                warn "$script_name: Possible hardcoded credential: $pattern"
            fi
        fi
    done

    # Check for network access
    if echo "$content" | grep -qE '(curl|wget|requests\.|urllib|http\.client)'; then
        # This is a warning, not an error - network access may be intended
        warn "$script_name: Contains network access - verify URLs are validated"
    fi

    # Check file permissions being set
    if echo "$content" | grep -qE 'chmod\s+[0-7]*7[0-7]*'; then
        warn "$script_name: World-writable permissions being set"
    fi

done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Security Check Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - No security issues found"
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠ PASSED WITH WARNINGS${NC} - $WARNINGS warning(s)"
    echo "Review warnings before deployment."
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS security issue(s), $WARNINGS warning(s)"
    echo "Fix security issues before installation."
    exit 1
fi
