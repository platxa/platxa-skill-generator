#!/usr/bin/env bash
# security-check.sh - Scan skill content for security issues
#
# Usage: security-check.sh <skill-directory>
#
# Two independent scan phases:
#   1. Markdown scanning (SKILL.md + references) — agent instructions are the
#      primary attack surface because they execute with AI authority.
#   2. Script scanning (scripts/*.sh, scripts/*.py) — helper scripts may
#      contain dangerous commands or hardcoded credentials.
#
# Both phases always run when applicable; neither can short-circuit the other.

set -euo pipefail

# ── Colours & counters ────────────────────────────────────────────────────────

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

usage() {
    echo "Usage: $0 <skill-directory>"
    echo ""
    echo "Scan skill content for security issues."
    exit 1
}

# ── Argument parsing ──────────────────────────────────────────────────────────

SKILL_DIR="${1:-}"

if [[ -z "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Skill directory required" >&2
    usage
fi

SKILL_NAME=$(basename "$SKILL_DIR")

echo "Security Check: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Pattern definitions ───────────────────────────────────────────────────────
# All patterns defined in one place, referenced by both scan phases as needed.

# Credential patterns (shared by both phases)
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

# Patterns dangerous when embedded as agent instructions in markdown.
# Code blocks in SKILL.md become commands the AI will run.
MARKDOWN_DANGEROUS=(
    'curl.*\| *sh'
    'curl.*\| *bash'
    'wget.*\| *sh'
    'wget.*\| *bash'
    'eval\s*"?\$\('           # eval $(command)
    'rm -rf /'
    'rm -rf /\*'
    ':(){:|:&};:'              # Fork bomb
    'mkfs\.'
    'dd if=/dev/'
    '> /dev/sd'
    'chmod -R 777 /'
    'base64\s+-d.*\|\s*bash'  # Encoded payload execution
    'base64\s+--decode.*\|\s*bash'
    'python[23]?\s+-c.*__import__'  # Inline import of arbitrary modules
    'nc\s+-[el]'              # Netcat listeners (reverse shells)
    'bash\s+-i\s+>&\s*/dev/tcp'  # Bash reverse shell
    '/dev/tcp/'               # Bash network device
    'nohup.*&'                # Background persistence
)

# Network exfiltration patterns — sending local data to external hosts
EXFIL_PATTERNS=(
    'curl.*-d\s*@'             # POST file contents: curl -d @/etc/passwd
    'curl.*--data.*@'
    'curl.*--upload-file'
    'wget.*--post-file'
    'cat.*/etc/\(passwd\|shadow\|hosts\)'
    '\$\(cat\s'               # Command substitution reading files
    'base64.*</etc/'          # Encoding system files
)

# Dangerous patterns for bash scripts
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

# Dangerous patterns for Python scripts
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

# ── Phase 1: Markdown scanning (primary security surface) ─────────────────────
# SKILL.md and reference files contain agent instructions. Dangerous patterns
# here are more severe than in helper scripts because they run with AI authority.

echo ""
echo "Phase 1: Scanning markdown files for malicious agent instructions..."
echo ""

while IFS= read -r -d '' mdfile; do
    md_rel="${mdfile#"$SKILL_DIR"/}"
    content=$(<"$mdfile")

    for pattern in "${MARKDOWN_DANGEROUS[@]}"; do
        if echo "$content" | grep -qE "$pattern"; then
            error "$md_rel: Dangerous agent instruction: $pattern"
        fi
    done

    for pattern in "${EXFIL_PATTERNS[@]}"; do
        if echo "$content" | grep -qE "$pattern"; then
            error "$md_rel: Possible data exfiltration pattern: $pattern"
        fi
    done

    # Check for credential patterns in markdown (hardcoded secrets in examples)
    for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
        if echo "$content" | grep -qiE "$pattern"; then
            match_line=$(echo "$content" | grep -iE "$pattern" | head -1)
            # Skip if it's clearly a placeholder or env reference
            if [[ ! "$match_line" =~ \<.*\> ]] && \
               [[ ! "$match_line" =~ \{.*\} ]] && \
               [[ ! "$match_line" =~ your_ ]] && \
               [[ ! "$match_line" =~ YOUR_ ]] && \
               [[ ! "$match_line" =~ os\.environ ]] && \
               [[ ! "$match_line" =~ \$\{ ]] && \
               [[ ! "$match_line" =~ getenv ]]; then
                warn "$md_rel: Possible hardcoded credential: $pattern"
            fi
        fi
    done

done < <(find "$SKILL_DIR" -name "*.md" -type f -print0 2>/dev/null)

# ── Phase 2: Script scanning (supplementary) ─────────────────────────────────
# Helper scripts in scripts/ may contain dangerous commands or credentials.
# This phase only runs when the skill has a scripts/ directory with files.

SCRIPTS_DIR="$SKILL_DIR/scripts"

if [[ -d "$SCRIPTS_DIR" ]]; then
    SCRIPT_COUNT=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f 2>/dev/null | wc -l)
    if [[ "$SCRIPT_COUNT" -gt 0 ]]; then
        echo ""
        echo "Phase 2: Scanning $SCRIPT_COUNT script(s)..."
        echo ""

        while IFS= read -r -d '' script; do
            script_name=$(basename "$script")
            echo "Checking: $script_name"

            content=$(<"$script")

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
                warn "$script_name: Contains network access - verify URLs are validated"
            fi

            # Check file permissions being set
            if echo "$content" | grep -qE 'chmod\s+[0-7]*7[0-7]*'; then
                warn "$script_name: World-writable permissions being set"
            fi

        done < <(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f -print0 2>/dev/null)
    fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────

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
