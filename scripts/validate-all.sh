#!/bin/bash
# validate-all.sh - Run all skill validators
#
# Usage: validate-all.sh <skill-directory> [--verbose] [--json]
#
# Runs:
# - validate-structure.sh
# - validate-frontmatter.sh
# - count-tokens.py
# - validate-skill.sh (if exists)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Results tracking
declare -A RESULTS
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

usage() {
    echo "Usage: $0 <skill-directory> [--verbose] [--json]"
    echo ""
    echo "Run all validators on a skill directory."
    echo ""
    echo "Options:"
    echo "  -v, --verbose  Show detailed output from each validator"
    echo "  --json         Output results as JSON"
    echo "  -h, --help     Show this help message"
    exit 1
}

# Parse arguments
VERBOSE=false
JSON_OUTPUT=false
SKILL_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            SKILL_DIR="$1"
            shift
            ;;
    esac
done

if [[ -z "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Skill directory required" >&2
    usage
fi

# Resolve to absolute path
SKILL_DIR=$(cd "$SKILL_DIR" 2>/dev/null && pwd) || {
    echo -e "${RED}Error:${NC} Directory does not exist: $SKILL_DIR" >&2
    exit 1
}

SKILL_NAME=$(basename "$SKILL_DIR")

run_validator() {
    local name="$1"
    local cmd="$2"
    local result

    if ! $JSON_OUTPUT; then
        echo -e "\n${BLUE}[$name]${NC}"
    fi

    if $VERBOSE; then
        if eval "$cmd"; then
            RESULTS[$name]="PASS"
            return 0
        else
            RESULTS[$name]="FAIL"
            ((TOTAL_ERRORS++)) || true
            return 1
        fi
    else
        # Capture output
        local output
        if output=$(eval "$cmd" 2>&1); then
            RESULTS[$name]="PASS"
            if ! $JSON_OUTPUT; then
                echo -e "${GREEN}✓ PASSED${NC}"
            fi
            return 0
        else
            RESULTS[$name]="FAIL"
            ((TOTAL_ERRORS++)) || true
            if ! $JSON_OUTPUT; then
                echo -e "${RED}✗ FAILED${NC}"
                # Show last few lines of output
                echo "$output" | tail -5 | sed 's/^/  /'
            fi
            return 1
        fi
    fi
}

if ! $JSON_OUTPUT; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Validating Skill: $SKILL_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Track overall status
OVERALL_PASS=true

# 1. Structure validation
if [[ -x "$SCRIPT_DIR/validate-structure.sh" ]]; then
    run_validator "Structure" "$SCRIPT_DIR/validate-structure.sh '$SKILL_DIR'" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Structure]${NC} Skipped - validator not found"
    fi
    RESULTS["Structure"]="SKIP"
fi

# 2. Frontmatter validation
if [[ -x "$SCRIPT_DIR/validate-frontmatter.sh" ]]; then
    run_validator "Frontmatter" "$SCRIPT_DIR/validate-frontmatter.sh '$SKILL_DIR'" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Frontmatter]${NC} Skipped - validator not found"
    fi
    RESULTS["Frontmatter"]="SKIP"
fi

# 3. Token count validation
if [[ -x "$SCRIPT_DIR/count-tokens.py" ]]; then
    run_validator "Tokens" "python3 '$SCRIPT_DIR/count-tokens.py' '$SKILL_DIR'" || OVERALL_PASS=false
elif command -v python3 &>/dev/null && [[ -f "$SCRIPT_DIR/count-tokens.py" ]]; then
    run_validator "Tokens" "python3 '$SCRIPT_DIR/count-tokens.py' '$SKILL_DIR'" || OVERALL_PASS=false
else
    if ! $JSON_OUTPUT; then
        echo -e "\n${YELLOW}[Tokens]${NC} Skipped - Python not available"
    fi
    RESULTS["Tokens"]="SKIP"
fi

# 4. Main skill validation (if exists)
if [[ -x "$SCRIPT_DIR/validate-skill.sh" ]]; then
    run_validator "Skill" "$SCRIPT_DIR/validate-skill.sh '$SKILL_DIR'" || OVERALL_PASS=false
else
    RESULTS["Skill"]="SKIP"
fi

# 5. Script validation (if scripts exist)
SCRIPTS_DIR="$SKILL_DIR/scripts"
if [[ -d "$SCRIPTS_DIR" ]]; then
    # Check bash scripts with shellcheck
    if command -v shellcheck &>/dev/null; then
        SHELL_SCRIPTS=$(find "$SCRIPTS_DIR" -name "*.sh" 2>/dev/null || echo "")
        if [[ -n "$SHELL_SCRIPTS" ]]; then
            run_validator "Shellcheck" "shellcheck -s bash $SHELL_SCRIPTS" || OVERALL_PASS=false
        fi
    fi

    # Check Python scripts with syntax check
    PY_SCRIPTS=$(find "$SCRIPTS_DIR" -name "*.py" 2>/dev/null || echo "")
    if [[ -n "$PY_SCRIPTS" ]]; then
        run_validator "Python Syntax" "python3 -m py_compile $PY_SCRIPTS" || OVERALL_PASS=false
    fi
fi

# Output results
if $JSON_OUTPUT; then
    # JSON output
    echo "{"
    echo "  \"skill_name\": \"$SKILL_NAME\","
    echo "  \"passed\": $( $OVERALL_PASS && echo "true" || echo "false" ),"
    echo "  \"validators\": {"
    first=true
    for key in "${!RESULTS[@]}"; do
        $first || echo ","
        first=false
        echo -n "    \"$key\": \"${RESULTS[$key]}\""
    done
    echo ""
    echo "  },"
    echo "  \"total_errors\": $TOTAL_ERRORS"
    echo "}"
else
    # Human-readable summary
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Validation Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    for key in "${!RESULTS[@]}"; do
        case "${RESULTS[$key]}" in
            PASS)
                echo -e "  ${GREEN}✓${NC} $key"
                ;;
            FAIL)
                echo -e "  ${RED}✗${NC} $key"
                ;;
            SKIP)
                echo -e "  ${YELLOW}○${NC} $key (skipped)"
                ;;
        esac
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if $OVERALL_PASS; then
        echo -e "${GREEN}✓ ALL VALIDATIONS PASSED${NC}"
        echo ""
        echo "Skill '$SKILL_NAME' is ready for installation."
    else
        echo -e "${RED}✗ VALIDATION FAILED${NC}"
        echo ""
        echo "Fix the errors above before installation."
    fi
fi

# Exit with appropriate code
$OVERALL_PASS && exit 0 || exit 1
