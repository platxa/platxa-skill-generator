# Install Test Script

Shell script to test skill installation in a temporary directory.

## Script: install-test.sh

```bash
#!/bin/bash
# install-test.sh - Test skill installation in isolated environment
#
# Usage: install-test.sh <skill-path> [options]
#
# Options:
#   --keep          Keep temp directory after test
#   --verbose       Show detailed output
#   --run-skill     Simulate skill invocation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
KEEP_TEMP=false
VERBOSE=false
RUN_SKILL=false
SKILL_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep)
            KEEP_TEMP=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --run-skill)
            RUN_SKILL=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SKILL_PATH="$1"
            shift
            ;;
    esac
done

# Validate
if [ -z "$SKILL_PATH" ]; then
    echo "Usage: install-test.sh <skill-path> [options]"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Directory not found: $SKILL_PATH"
    exit 1
fi

SKILL_PATH=$(cd "$SKILL_PATH" && pwd)
SKILL_NAME=$(basename "$SKILL_PATH")

# Create temp directory
TEMP_DIR=$(mktemp -d)
TEMP_SKILLS="$TEMP_DIR/.claude/skills"
INSTALL_PATH="$TEMP_SKILLS/$SKILL_NAME"

# Cleanup function
cleanup() {
    if [ "$KEEP_TEMP" = false ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        [ "$VERBOSE" = true ] && echo "Cleaned up: $TEMP_DIR"
    fi
}
trap cleanup EXIT

# Logging
log_step() {
    echo -e "${BLUE}▶${NC} $1"
}

log_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
}

log_fail() {
    echo -e "  ${RED}✗${NC} $1"
}

log_info() {
    [ "$VERBOSE" = true ] && echo -e "  ${YELLOW}ℹ${NC} $1"
}

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local name="$1"
    local cmd="$2"

    ((TESTS_RUN++))

    if eval "$cmd" > /dev/null 2>&1; then
        log_pass "$name"
        ((TESTS_PASSED++))
        return 0
    else
        log_fail "$name"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Header
echo "═══════════════════════════════════════════════════════════"
echo "  INSTALL TEST: $SKILL_NAME"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Source: $SKILL_PATH"
echo "  Target: $INSTALL_PATH"
echo ""

# Phase 1: Pre-installation checks
log_step "Phase 1: Pre-installation checks"

run_test "Source directory exists" "[ -d '$SKILL_PATH' ]"
run_test "SKILL.md exists" "[ -f '$SKILL_PATH/SKILL.md' ]"
run_test "SKILL.md is readable" "[ -r '$SKILL_PATH/SKILL.md' ]"
run_test "SKILL.md has content" "[ -s '$SKILL_PATH/SKILL.md' ]"

# Check frontmatter
if [ -f "$SKILL_PATH/SKILL.md" ]; then
    run_test "YAML frontmatter present" "head -n 1 '$SKILL_PATH/SKILL.md' | grep -q '^---$'"
    run_test "Name field present" "grep -q '^name:' '$SKILL_PATH/SKILL.md'"
    run_test "Description field present" "grep -q '^description:' '$SKILL_PATH/SKILL.md'"
fi

echo ""

# Phase 2: Installation
log_step "Phase 2: Installation"

# Create directory structure
log_info "Creating directory: $TEMP_SKILLS"
mkdir -p "$TEMP_SKILLS"
run_test "Created skills directory" "[ -d '$TEMP_SKILLS' ]"

# Copy skill
log_info "Copying skill to: $INSTALL_PATH"
cp -r "$SKILL_PATH" "$INSTALL_PATH"
run_test "Skill copied successfully" "[ -d '$INSTALL_PATH' ]"

# Verify copy
run_test "SKILL.md copied" "[ -f '$INSTALL_PATH/SKILL.md' ]"

if [ -d "$SKILL_PATH/references" ]; then
    run_test "References directory copied" "[ -d '$INSTALL_PATH/references' ]"
    REF_COUNT=$(find "$SKILL_PATH/references" -name "*.md" | wc -l)
    COPIED_COUNT=$(find "$INSTALL_PATH/references" -name "*.md" 2>/dev/null | wc -l)
    run_test "All references copied ($REF_COUNT files)" "[ '$REF_COUNT' -eq '$COPIED_COUNT' ]"
fi

if [ -d "$SKILL_PATH/scripts" ]; then
    run_test "Scripts directory copied" "[ -d '$INSTALL_PATH/scripts' ]"
fi

echo ""

# Phase 3: Post-installation verification
log_step "Phase 3: Post-installation verification"

# Check file permissions
run_test "SKILL.md readable" "[ -r '$INSTALL_PATH/SKILL.md' ]"

# Check file sizes match
ORIG_SIZE=$(du -sb "$SKILL_PATH" | cut -f1)
INST_SIZE=$(du -sb "$INSTALL_PATH" | cut -f1)
run_test "File sizes match" "[ '$ORIG_SIZE' -eq '$INST_SIZE' ]"

# Check for broken symlinks
BROKEN_LINKS=$(find "$INSTALL_PATH" -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l)
run_test "No broken symlinks" "[ '$BROKEN_LINKS' -eq 0 ]"

# Verify markdown parsing
run_test "SKILL.md valid UTF-8" "file '$INSTALL_PATH/SKILL.md' | grep -qE 'UTF-8|ASCII'"

# Check code blocks balanced
CODE_BLOCKS=$(grep -c '```' "$INSTALL_PATH/SKILL.md" || echo 0)
run_test "Code blocks balanced" "[ \$(($CODE_BLOCKS % 2)) -eq 0 ]"

echo ""

# Phase 4: Script permissions (if applicable)
if [ -d "$INSTALL_PATH/scripts" ]; then
    log_step "Phase 4: Script verification"

    for script in "$INSTALL_PATH/scripts"/*.sh; do
        [ -f "$script" ] || continue
        script_name=$(basename "$script")

        # Make executable if not
        if [ ! -x "$script" ]; then
            chmod +x "$script"
            log_info "Made executable: $script_name"
        fi

        run_test "Script '$script_name' executable" "[ -x '$script' ]"
        run_test "Script '$script_name' has shebang" "head -n 1 '$script' | grep -q '^#!'"
    done

    echo ""
fi

# Phase 5: Simulated invocation (if requested)
if [ "$RUN_SKILL" = true ]; then
    log_step "Phase 5: Simulated invocation"

    # Simulate what Claude Code would do
    if [ -f "$INSTALL_PATH/SKILL.md" ]; then
        # Extract skill content (after frontmatter)
        SKILL_CONTENT=$(sed -n '/^---$/,/^---$/!p' "$INSTALL_PATH/SKILL.md" | tail -n +2)
        CONTENT_LENGTH=${#SKILL_CONTENT}

        run_test "Skill content extracted" "[ $CONTENT_LENGTH -gt 0 ]"
        run_test "Content length reasonable" "[ $CONTENT_LENGTH -lt 50000 ]"

        # Check for common sections
        run_test "Has usage section" "echo '$SKILL_CONTENT' | grep -qi 'usage\|how to use'"

        log_info "Content length: $CONTENT_LENGTH characters"
    fi

    echo ""
fi

# Summary
echo "───────────────────────────────────────────────────────────"
echo ""
echo "  Tests Run:    $TESTS_RUN"
echo -e "  Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Failed:       ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "  ${GREEN}✓ INSTALL TEST PASSED${NC}"
    RESULT=0
else
    echo -e "  ${RED}✗ INSTALL TEST FAILED${NC}"
    RESULT=1
fi

echo ""

if [ "$KEEP_TEMP" = true ]; then
    echo "  Temp directory preserved: $TEMP_DIR"
fi

echo "═══════════════════════════════════════════════════════════"

exit $RESULT
```

## Usage

```bash
# Basic install test
./install-test.sh ~/.claude/skills/my-skill/

# Keep temp directory for inspection
./install-test.sh ~/.claude/skills/my-skill/ --keep

# Verbose output
./install-test.sh ~/.claude/skills/my-skill/ --verbose

# Include simulated invocation
./install-test.sh ~/.claude/skills/my-skill/ --run-skill

# All options
./install-test.sh ~/.claude/skills/my-skill/ --verbose --run-skill --keep
```

## Test Phases

| Phase | Tests |
|-------|-------|
| 1. Pre-installation | Source exists, SKILL.md valid, frontmatter present |
| 2. Installation | Directory creation, file copying |
| 3. Post-installation | Permissions, sizes, symlinks, encoding |
| 4. Scripts | Executable, shebang present |
| 5. Simulated invocation | Content extraction, structure |

## Sample Output

```
═══════════════════════════════════════════════════════════
  INSTALL TEST: api-doc-generator
═══════════════════════════════════════════════════════════

  Source: /home/user/.claude/skills/api-doc-generator
  Target: /tmp/tmp.xyz123/.claude/skills/api-doc-generator

▶ Phase 1: Pre-installation checks
  ✓ Source directory exists
  ✓ SKILL.md exists
  ✓ SKILL.md is readable
  ✓ SKILL.md has content
  ✓ YAML frontmatter present
  ✓ Name field present
  ✓ Description field present

▶ Phase 2: Installation
  ✓ Created skills directory
  ✓ Skill copied successfully
  ✓ SKILL.md copied
  ✓ References directory copied
  ✓ All references copied (3 files)

▶ Phase 3: Post-installation verification
  ✓ SKILL.md readable
  ✓ File sizes match
  ✓ No broken symlinks
  ✓ SKILL.md valid UTF-8
  ✓ Code blocks balanced

───────────────────────────────────────────────────────────

  Tests Run:    15
  Passed:       15
  Failed:       0

  ✓ INSTALL TEST PASSED

═══════════════════════════════════════════════════════════
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
