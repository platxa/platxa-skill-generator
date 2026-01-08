# CI Check Script

Comprehensive CI/CD validation script with proper exit codes.

## CI Check Purpose

| Feature | Description |
|---------|-------------|
| Unified validation | Run all checks in one command |
| CI/CD integration | Proper exit codes for pipelines |
| Detailed reporting | Machine and human-readable output |
| Fast feedback | Fail fast on critical errors |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Critical error (structure/syntax) |
| 2 | Quality below threshold |
| 3 | Warnings present (optional fail) |
| 4 | Script error |

## Script: ci-check.sh

```bash
#!/bin/bash
# ci-check.sh - Comprehensive CI validation for skills
#
# Usage: ci-check.sh <skill-path> [options]
#
# Options:
#   --strict           Fail on warnings
#   --quality <score>  Minimum quality score (default: 7.0)
#   --json             Output JSON report
#   --quiet            Minimal output
#   --no-color         Disable colored output
#   --junit <file>     Generate JUnit XML report

set -o pipefail

# Version
VERSION="1.0.0"

# Colors (can be disabled)
setup_colors() {
    if [ "$NO_COLOR" = true ] || [ ! -t 1 ]; then
        RED=''
        GREEN=''
        YELLOW=''
        BLUE=''
        BOLD=''
        NC=''
    else
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[0;33m'
        BLUE='\033[0;34m'
        BOLD='\033[1m'
        NC='\033[0m'
    fi
}

# Defaults
SKILL_PATH=""
STRICT=false
MIN_QUALITY=7.0
JSON_OUTPUT=false
QUIET=false
NO_COLOR=false
JUNIT_FILE=""

# Counters
CHECKS_RUN=0
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNED=0

# Results storage
declare -a RESULTS
declare -a ERRORS
declare -a WARNINGS

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --strict)
            STRICT=true
            shift
            ;;
        --quality)
            MIN_QUALITY="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --no-color)
            NO_COLOR=true
            shift
            ;;
        --junit)
            JUNIT_FILE="$2"
            shift 2
            ;;
        --version)
            echo "ci-check.sh v$VERSION"
            exit 0
            ;;
        --help|-h)
            echo "Usage: ci-check.sh <skill-path> [options]"
            echo ""
            echo "Options:"
            echo "  --strict           Fail on warnings"
            echo "  --quality <score>  Minimum quality score (default: 7.0)"
            echo "  --json             Output JSON report"
            echo "  --quiet            Minimal output"
            echo "  --no-color         Disable colored output"
            echo "  --junit <file>     Generate JUnit XML report"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            exit 4
            ;;
        *)
            SKILL_PATH="$1"
            shift
            ;;
    esac
done

setup_colors

# Logging functions
log_check() {
    ((CHECKS_RUN++))
    [ "$QUIET" = false ] && echo -e "${BLUE}▶${NC} $1"
}

log_pass() {
    ((CHECKS_PASSED++))
    RESULTS+=("PASS:$1")
    [ "$QUIET" = false ] && echo -e "  ${GREEN}✓${NC} $1"
}

log_fail() {
    ((CHECKS_FAILED++))
    RESULTS+=("FAIL:$1")
    ERRORS+=("$1: $2")
    [ "$QUIET" = false ] && echo -e "  ${RED}✗${NC} $1"
    [ "$QUIET" = false ] && [ -n "$2" ] && echo -e "    ${RED}→${NC} $2"
}

log_warn() {
    ((CHECKS_WARNED++))
    RESULTS+=("WARN:$1")
    WARNINGS+=("$1: $2")
    [ "$QUIET" = false ] && echo -e "  ${YELLOW}⚠${NC} $1"
    [ "$QUIET" = false ] && [ -n "$2" ] && echo -e "    ${YELLOW}→${NC} $2"
}

# Validate input
if [ -z "$SKILL_PATH" ]; then
    echo "Error: Skill path required"
    echo "Usage: ci-check.sh <skill-path> [options]"
    exit 4
fi

SKILL_PATH=$(cd "$SKILL_PATH" 2>/dev/null && pwd) || {
    echo "Error: Directory not found: $SKILL_PATH"
    exit 4
}

SKILL_NAME=$(basename "$SKILL_PATH")

# Header
if [ "$QUIET" = false ] && [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  CI CHECK: $SKILL_NAME"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
fi

START_TIME=$(date +%s)

#
# CHECK 1: Structure
#
log_check "Structure validation"

# SKILL.md exists
if [ -f "$SKILL_PATH/SKILL.md" ]; then
    log_pass "SKILL.md exists"
else
    log_fail "SKILL.md missing" "Required file not found"
fi

# SKILL.md readable
if [ -r "$SKILL_PATH/SKILL.md" ]; then
    log_pass "SKILL.md readable"
else
    log_fail "SKILL.md not readable" "Check file permissions"
fi

# Check for unexpected files
UNEXPECTED=$(find "$SKILL_PATH" -maxdepth 1 -type f ! -name "SKILL.md" ! -name "README.md" ! -name ".*" | head -5)
if [ -z "$UNEXPECTED" ]; then
    log_pass "No unexpected root files"
else
    log_warn "Unexpected files in root" "$(echo "$UNEXPECTED" | xargs basename -a | tr '\n' ', ')"
fi

#
# CHECK 2: Frontmatter
#
log_check "YAML frontmatter"

if [ -f "$SKILL_PATH/SKILL.md" ]; then
    # Check starts with ---
    if head -n 1 "$SKILL_PATH/SKILL.md" | grep -q "^---$"; then
        log_pass "Frontmatter delimiter present"
    else
        log_fail "Missing frontmatter" "SKILL.md must start with ---"
    fi

    # Check required fields
    if grep -q "^name:" "$SKILL_PATH/SKILL.md"; then
        log_pass "Name field present"

        # Validate name format
        NAME_VALUE=$(grep "^name:" "$SKILL_PATH/SKILL.md" | head -1 | sed 's/name:\s*//' | tr -d '"'"'")
        if [[ "$NAME_VALUE" =~ ^[a-z][a-z0-9-]*$ ]]; then
            log_pass "Name format valid"
        else
            log_fail "Invalid name format" "Must be lowercase with hyphens: $NAME_VALUE"
        fi
    else
        log_fail "Name field missing" "Add 'name:' to frontmatter"
    fi

    if grep -q "^description:" "$SKILL_PATH/SKILL.md"; then
        log_pass "Description field present"
    else
        log_warn "Description field missing" "Recommended for discoverability"
    fi
fi

#
# CHECK 3: Content
#
log_check "Content validation"

if [ -f "$SKILL_PATH/SKILL.md" ]; then
    # Token count estimate
    WORD_COUNT=$(wc -w < "$SKILL_PATH/SKILL.md")
    TOKEN_EST=$((WORD_COUNT * 4 / 3))

    if [ "$TOKEN_EST" -lt 5000 ]; then
        log_pass "SKILL.md within token budget (~$TOKEN_EST tokens)"
    else
        log_warn "SKILL.md may exceed budget" "~$TOKEN_EST tokens (limit: 5000)"
    fi

    # Check for content after frontmatter
    CONTENT_LINES=$(sed -n '/^---$/,/^---$/d; p' "$SKILL_PATH/SKILL.md" | grep -v "^$" | wc -l)
    if [ "$CONTENT_LINES" -gt 5 ]; then
        log_pass "Has substantive content ($CONTENT_LINES lines)"
    else
        log_warn "Limited content" "Only $CONTENT_LINES lines of content"
    fi

    # Check for balanced code blocks
    CODE_BLOCKS=$(grep -c '```' "$SKILL_PATH/SKILL.md" || echo 0)
    if [ $((CODE_BLOCKS % 2)) -eq 0 ]; then
        log_pass "Code blocks balanced"
    else
        log_fail "Unbalanced code blocks" "Found $CODE_BLOCKS markers (should be even)"
    fi
fi

#
# CHECK 4: References
#
log_check "References validation"

if [ -d "$SKILL_PATH/references" ]; then
    REF_COUNT=$(find "$SKILL_PATH/references" -name "*.md" | wc -l)
    log_pass "References directory ($REF_COUNT files)"

    # Check total reference size
    REF_WORDS=$(find "$SKILL_PATH/references" -name "*.md" -exec cat {} \; | wc -w)
    REF_TOKENS=$((REF_WORDS * 4 / 3))

    if [ "$REF_TOKENS" -lt 10000 ]; then
        log_pass "References within budget (~$REF_TOKENS tokens)"
    else
        log_warn "References may exceed budget" "~$REF_TOKENS tokens (limit: 10000)"
    fi

    # Check each reference
    for ref in "$SKILL_PATH/references"/*.md; do
        [ -f "$ref" ] || continue
        REF_NAME=$(basename "$ref")

        # Check for UTF-8
        if file "$ref" | grep -qE "UTF-8|ASCII"; then
            log_pass "$REF_NAME encoding valid"
        else
            log_fail "$REF_NAME encoding" "Must be UTF-8"
        fi
    done
else
    log_pass "No references directory (minimal skill)"
fi

#
# CHECK 5: Links
#
log_check "Link validation"

if [ -f "$SKILL_PATH/SKILL.md" ]; then
    # Check internal links
    BROKEN_LINKS=0

    while IFS= read -r link; do
        [ -z "$link" ] && continue
        TARGET="$SKILL_PATH/$link"
        if [ ! -e "$TARGET" ]; then
            log_warn "Broken link" "$link"
            ((BROKEN_LINKS++))
        fi
    done < <(grep -oE '\]\([^)]+\)' "$SKILL_PATH/SKILL.md" | sed 's/\](\(.*\))/\1/' | grep -v "^http" | grep -v "^#")

    if [ "$BROKEN_LINKS" -eq 0 ]; then
        log_pass "All internal links valid"
    fi
fi

#
# CHECK 6: Quality Score
#
log_check "Quality assessment"

QUALITY_SCORE=10.0

# Deductions
[ "$CHECKS_FAILED" -gt 0 ] && QUALITY_SCORE=$(echo "$QUALITY_SCORE - $CHECKS_FAILED * 2" | bc)
[ "$CHECKS_WARNED" -gt 0 ] && QUALITY_SCORE=$(echo "$QUALITY_SCORE - $CHECKS_WARNED * 0.5" | bc)

# Ensure non-negative
QUALITY_SCORE=$(echo "if ($QUALITY_SCORE < 0) 0 else $QUALITY_SCORE" | bc)

if (( $(echo "$QUALITY_SCORE >= $MIN_QUALITY" | bc -l) )); then
    log_pass "Quality score: $QUALITY_SCORE/10 (threshold: $MIN_QUALITY)"
else
    log_fail "Quality below threshold" "Score: $QUALITY_SCORE (required: $MIN_QUALITY)"
fi

#
# Summary
#
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Determine exit code
if [ "$CHECKS_FAILED" -gt 0 ]; then
    EXIT_CODE=1
elif (( $(echo "$QUALITY_SCORE < $MIN_QUALITY" | bc -l) )); then
    EXIT_CODE=2
elif [ "$STRICT" = true ] && [ "$CHECKS_WARNED" -gt 0 ]; then
    EXIT_CODE=3
else
    EXIT_CODE=0
fi

# JSON output
if [ "$JSON_OUTPUT" = true ]; then
    cat << EOF
{
  "skill": "$SKILL_NAME",
  "path": "$SKILL_PATH",
  "version": "$VERSION",
  "timestamp": "$(date -Iseconds)",
  "duration_seconds": $DURATION,
  "summary": {
    "checks_run": $CHECKS_RUN,
    "passed": $CHECKS_PASSED,
    "failed": $CHECKS_FAILED,
    "warnings": $CHECKS_WARNED
  },
  "quality_score": $QUALITY_SCORE,
  "quality_threshold": $MIN_QUALITY,
  "exit_code": $EXIT_CODE,
  "errors": $(printf '%s\n' "${ERRORS[@]}" | jq -R . | jq -s .),
  "warnings": $(printf '%s\n' "${WARNINGS[@]}" | jq -R . | jq -s .)
}
EOF
    exit $EXIT_CODE
fi

# JUnit XML output
if [ -n "$JUNIT_FILE" ]; then
    cat > "$JUNIT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="skill-validation" tests="$CHECKS_RUN" failures="$CHECKS_FAILED" errors="0" time="$DURATION">
EOF
    for result in "${RESULTS[@]}"; do
        STATUS="${result%%:*}"
        NAME="${result#*:}"
        echo "  <testcase name=\"$NAME\">" >> "$JUNIT_FILE"
        if [ "$STATUS" = "FAIL" ]; then
            echo "    <failure message=\"Check failed\"/>" >> "$JUNIT_FILE"
        fi
        echo "  </testcase>" >> "$JUNIT_FILE"
    done
    echo "</testsuite>" >> "$JUNIT_FILE"
fi

# Human-readable summary
if [ "$QUIET" = false ]; then
    echo ""
    echo "───────────────────────────────────────────────────────────────"
    echo ""
    echo "  SUMMARY"
    echo "  ───────"
    echo "  Checks:   $CHECKS_RUN total"
    echo -e "  Passed:   ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "  Failed:   ${RED}$CHECKS_FAILED${NC}"
    echo -e "  Warnings: ${YELLOW}$CHECKS_WARNED${NC}"
    echo ""
    echo "  Quality:  $QUALITY_SCORE / 10"
    echo "  Duration: ${DURATION}s"
    echo ""

    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}✓ ALL CHECKS PASSED${NC}"
    elif [ $EXIT_CODE -eq 1 ]; then
        echo -e "  ${RED}${BOLD}✗ CRITICAL ERRORS FOUND${NC}"
    elif [ $EXIT_CODE -eq 2 ]; then
        echo -e "  ${RED}${BOLD}✗ QUALITY BELOW THRESHOLD${NC}"
    elif [ $EXIT_CODE -eq 3 ]; then
        echo -e "  ${YELLOW}${BOLD}⚠ WARNINGS (strict mode)${NC}"
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
fi

exit $EXIT_CODE
```

## Usage Examples

```bash
# Basic check
./ci-check.sh ~/.claude/skills/my-skill/

# Strict mode (fail on warnings)
./ci-check.sh my-skill/ --strict

# Custom quality threshold
./ci-check.sh my-skill/ --quality 8.0

# JSON output for parsing
./ci-check.sh my-skill/ --json

# Generate JUnit report
./ci-check.sh my-skill/ --junit results.xml

# Quiet mode for scripts
./ci-check.sh my-skill/ --quiet && echo "OK" || echo "FAILED"
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Validate Skill
  run: |
    ./scripts/ci-check.sh ./my-skill --strict --junit test-results.xml

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results.xml
```

### GitLab CI

```yaml
validate-skill:
  script:
    - ./scripts/ci-check.sh ./my-skill --json > report.json
  artifacts:
    reports:
      junit: test-results.xml
```

## Sample Output

```
═══════════════════════════════════════════════════════════════
  CI CHECK: api-doc-generator
═══════════════════════════════════════════════════════════════

▶ Structure validation
  ✓ SKILL.md exists
  ✓ SKILL.md readable
  ✓ No unexpected root files

▶ YAML frontmatter
  ✓ Frontmatter delimiter present
  ✓ Name field present
  ✓ Name format valid
  ✓ Description field present

▶ Content validation
  ✓ SKILL.md within token budget (~1200 tokens)
  ✓ Has substantive content (45 lines)
  ✓ Code blocks balanced

▶ References validation
  ✓ References directory (3 files)
  ✓ References within budget (~2400 tokens)
  ✓ overview.md encoding valid
  ✓ workflow.md encoding valid
  ✓ api.md encoding valid

▶ Link validation
  ✓ All internal links valid

▶ Quality assessment
  ✓ Quality score: 10.0/10 (threshold: 7.0)

───────────────────────────────────────────────────────────────

  SUMMARY
  ───────
  Checks:   18 total
  Passed:   18
  Failed:   0
  Warnings: 0

  Quality:  10.0 / 10
  Duration: 1s

  ✓ ALL CHECKS PASSED

═══════════════════════════════════════════════════════════════
```
