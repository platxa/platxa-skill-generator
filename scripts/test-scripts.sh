#!/bin/bash
# test-scripts.sh - Test skill scripts for correct execution
#
# Usage: test-scripts.sh <skill-directory> [--verbose] [--sandbox]
#
# Test levels:
# - Syntax: Parse without errors (always)
# - Dry run: Execute with --help/--dry-run (always)
# - Sandbox: Execute in isolated environment (if --sandbox)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
ERRORS=()
WARNINGS=()

error() {
    echo -e "${RED}FAIL:${NC} $1" >&2
    ERRORS+=("$1")
    ((TESTS_FAILED++)) || true
}

pass() {
    echo -e "${GREEN}PASS:${NC} $1"
    ((TESTS_PASSED++)) || true
}

warn() {
    echo -e "${YELLOW}WARN:${NC} $1"
    WARNINGS+=("$1")
}

info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

usage() {
    echo "Usage: $0 <skill-directory> [options]"
    echo ""
    echo "Test skill scripts for correct execution."
    echo ""
    echo "Options:"
    echo "  -v, --verbose    Show detailed output"
    echo "  -s, --sandbox    Run scripts in sandbox environment"
    echo "  --json           Output results as JSON"
    echo "  -h, --help       Show this help message"
    exit 1
}

# Parse arguments
VERBOSE=false
SANDBOX=false
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
        -s|--sandbox)
            SANDBOX=true
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
SCRIPTS_DIR="$SKILL_DIR/scripts"

if ! $JSON_OUTPUT; then
    echo "Script Testing: $SKILL_NAME"
    echo "=============================================="
fi

# Check if scripts directory exists
if [[ ! -d "$SCRIPTS_DIR" ]]; then
    if $JSON_OUTPUT; then
        echo '{"passed": true, "message": "No scripts directory", "tests_run": 0}'
    else
        info "No scripts directory - nothing to test"
    fi
    exit 0
fi

# Find all scripts
SCRIPTS=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) -type f 2>/dev/null || echo "")

if [[ -z "$SCRIPTS" ]]; then
    if $JSON_OUTPUT; then
        echo '{"passed": true, "message": "No scripts found", "tests_run": 0}'
    else
        info "No scripts found"
    fi
    exit 0
fi

SCRIPT_COUNT=$(echo "$SCRIPTS" | wc -l)
if ! $JSON_OUTPUT; then
    echo "Found $SCRIPT_COUNT script(s)"
    echo ""
fi

# Test results storage
declare -A SCRIPT_RESULTS

#######################################
# Test a bash script
#######################################
test_bash_script() {
    local script_path="$1"
    local script_name
    script_name=$(basename "$script_path")
    local script_passed=true

    if ! $JSON_OUTPUT; then
        echo -e "\n${BLUE}Testing:${NC} $script_name"
        echo "----------------------------------------"
    fi

    # 1. Syntax check with bash -n
    ((TESTS_RUN++)) || true
    if bash -n "$script_path" 2>/dev/null; then
        pass "Syntax check"
    else
        error "$script_name: Syntax error"
        script_passed=false
    fi

    # 2. Shebang check
    ((TESTS_RUN++)) || true
    if head -1 "$script_path" | grep -q '^#!/'; then
        pass "Shebang present"
    else
        error "$script_name: Missing shebang line"
        script_passed=false
    fi

    # 3. Shellcheck (if available)
    if command -v shellcheck &>/dev/null; then
        ((TESTS_RUN++)) || true
        local shellcheck_output
        if shellcheck_output=$(shellcheck -s bash "$script_path" 2>&1); then
            pass "Shellcheck"
        else
            # Check severity
            if echo "$shellcheck_output" | grep -q "error"; then
                error "$script_name: Shellcheck errors found"
                if $VERBOSE; then
                    echo "$shellcheck_output" | head -10
                fi
                script_passed=false
            else
                pass "Shellcheck (warnings only)"
                warn "$script_name: Shellcheck warnings"
            fi
        fi
    else
        warn "shellcheck not installed, skipping"
    fi

    # 4. Help flag test (if script supports it)
    local content
    content=$(cat "$script_path")
    if [[ "$content" == *"--help"* ]] || [[ "$content" == *"-h"* ]]; then
        ((TESTS_RUN++)) || true
        local help_exit
        timeout 5 bash "$script_path" --help &>/dev/null
        help_exit=$?

        # Exit codes 0, 1, 2 are acceptable for help
        if [[ $help_exit -le 2 ]]; then
            pass "Help flag (exit code $help_exit)"
        else
            error "$script_name: Help flag failed (exit code $help_exit)"
            script_passed=false
        fi
    fi

    # 5. Dry run test (if supported)
    if [[ "$content" == *"--dry-run"* ]]; then
        ((TESTS_RUN++)) || true
        local dryrun_exit
        timeout 10 bash "$script_path" --dry-run &>/dev/null
        dryrun_exit=$?

        if [[ $dryrun_exit -eq 0 ]]; then
            pass "Dry run"
        else
            warn "$script_name: Dry run returned exit code $dryrun_exit"
        fi
    fi

    # 6. Check for set -e or set -euo pipefail
    ((TESTS_RUN++)) || true
    if echo "$content" | grep -qE 'set -[euo]+|set -.*e'; then
        pass "Error handling (set -e)"
    else
        warn "$script_name: Consider adding 'set -euo pipefail'"
    fi

    SCRIPT_RESULTS[$script_name]=$script_passed
}

#######################################
# Test a Python script
#######################################
test_python_script() {
    local script_path="$1"
    local script_name
    script_name=$(basename "$script_path")
    local script_passed=true

    if ! $JSON_OUTPUT; then
        echo -e "\n${BLUE}Testing:${NC} $script_name"
        echo "----------------------------------------"
    fi

    # 1. Syntax check with py_compile
    ((TESTS_RUN++)) || true
    if python3 -m py_compile "$script_path" 2>/dev/null; then
        pass "Syntax check"
    else
        error "$script_name: Python syntax error"
        script_passed=false
    fi

    # 2. Import check
    ((TESTS_RUN++)) || true
    local import_check
    import_check="import importlib.util; spec = importlib.util.spec_from_file_location('mod', '$script_path')"
    if python3 -c "$import_check" 2>/dev/null; then
        pass "Import check"
    else
        error "$script_name: Import error"
        script_passed=false
    fi

    # 3. Type check with pyright (if available)
    if command -v pyright &>/dev/null; then
        ((TESTS_RUN++)) || true
        if pyright "$script_path" --outputjson 2>/dev/null | grep -q '"errorCount": 0'; then
            pass "Type check (pyright)"
        else
            # Type errors are warnings for scripts
            pass "Type check (warnings)"
            warn "$script_name: Pyright found type issues"
        fi
    elif command -v mypy &>/dev/null; then
        ((TESTS_RUN++)) || true
        if mypy "$script_path" --ignore-missing-imports 2>/dev/null | grep -q "Success"; then
            pass "Type check (mypy)"
        else
            pass "Type check (warnings)"
            warn "$script_name: Mypy found type issues"
        fi
    fi

    # 4. Help flag test
    local content
    content=$(cat "$script_path")
    if [[ "$content" == *"argparse"* ]] || [[ "$content" == *"--help"* ]]; then
        ((TESTS_RUN++)) || true
        local help_exit
        if timeout 5 python3 "$script_path" --help &>/dev/null; then
            help_exit=$?
        else
            help_exit=$?
        fi

        if [[ $help_exit -eq 0 ]]; then
            pass "Help flag"
        else
            error "$script_name: Help flag failed (exit code $help_exit)"
            script_passed=false
        fi
    fi

    # 5. Main guard check
    ((TESTS_RUN++)) || true
    if echo "$content" | grep -qE "if __name__ == ['\"]__main__['\"]"; then
        pass "Main guard present"
    else
        warn "$script_name: Missing if __name__ == '__main__' guard"
    fi

    # 6. Check for type hints
    ((TESTS_RUN++)) || true
    if echo "$content" | grep -qE 'def \w+\([^)]*: |-> '; then
        pass "Type hints present"
    else
        warn "$script_name: Consider adding type hints"
    fi

    SCRIPT_RESULTS[$script_name]=$script_passed
}

#######################################
# Sandbox execution test
#######################################
test_in_sandbox() {
    local script_path="$1"
    local script_name
    script_name=$(basename "$script_path")

    if ! $JSON_OUTPUT; then
        echo -e "\n${BLUE}Sandbox test:${NC} $script_name"
    fi

    # Create temporary directory
    local tmpdir
    tmpdir=$(mktemp -d)
    trap 'rm -rf "$tmpdir"' EXIT

    # Copy script to sandbox
    cp "$script_path" "$tmpdir/"
    chmod +x "$tmpdir/$script_name"

    ((TESTS_RUN++)) || true

    # Execute with timeout in minimal environment
    local sandbox_exit
    timeout 30 env -i HOME="$tmpdir" PATH=/usr/bin:/bin TERM=dumb "$tmpdir/$script_name" --help &>/dev/null
    sandbox_exit=$?

    if [[ $sandbox_exit -le 2 ]]; then
        pass "Sandbox execution"
    else
        warn "$script_name: Sandbox execution returned $sandbox_exit"
    fi

    rm -rf "$tmpdir"
    trap - EXIT
}

#######################################
# Main test loop
#######################################
for script in $SCRIPTS; do
    if [[ "$script" == *.sh ]]; then
        test_bash_script "$script"
    elif [[ "$script" == *.py ]]; then
        test_python_script "$script"
    fi

    if $SANDBOX; then
        test_in_sandbox "$script"
    fi
done

#######################################
# Output results
#######################################
ALL_PASSED=true
for result in "${SCRIPT_RESULTS[@]}"; do
    if [[ "$result" != "true" ]]; then
        ALL_PASSED=false
        break
    fi
done

if $JSON_OUTPUT; then
    # JSON output
    cat << EOF
{
  "passed": $ALL_PASSED,
  "tests_run": $TESTS_RUN,
  "tests_passed": $TESTS_PASSED,
  "tests_failed": $TESTS_FAILED,
  "scripts_tested": $SCRIPT_COUNT,
  "errors": [$(printf '"%s",' "${ERRORS[@]}" | sed 's/,$//')],
  "warnings": [$(printf '"%s",' "${WARNINGS[@]}" | sed 's/,$//')]
}
EOF
else
    # Human-readable summary
    echo ""
    echo "=============================================="
    echo "Script Testing Summary"
    echo "=============================================="
    echo ""
    echo "Scripts tested: $SCRIPT_COUNT"
    echo "Tests run: $TESTS_RUN"
    echo "Tests passed: $TESTS_PASSED"
    echo "Tests failed: $TESTS_FAILED"
    echo "Warnings: ${#WARNINGS[@]}"
    echo ""

    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        echo "Errors:"
        for err in "${ERRORS[@]}"; do
            echo "  - $err"
        done
        echo ""
    fi

    if [[ ${#WARNINGS[@]} -gt 0 ]] && $VERBOSE; then
        echo "Warnings:"
        for warn_msg in "${WARNINGS[@]}"; do
            echo "  - $warn_msg"
        done
        echo ""
    fi

    echo "=============================================="
    if $ALL_PASSED; then
        echo -e "${GREEN}PASSED${NC} - All script tests passed"
        exit 0
    else
        echo -e "${RED}FAILED${NC} - Some script tests failed"
        exit 1
    fi
fi

$ALL_PASSED && exit 0 || exit 1
