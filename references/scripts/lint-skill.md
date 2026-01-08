# Lint Skill Script

Shell script to check markdown and YAML formatting in skills.

## Script: lint-skill.sh

```bash
#!/bin/bash
# lint-skill.sh - Lint a Claude Code skill for formatting issues
#
# Usage: lint-skill.sh <skill-path> [options]
#
# Options:
#   --fix         Auto-fix issues where possible
#   --strict      Treat warnings as errors
#   --quiet       Only show errors
#   --json        Output results as JSON

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
FIXED=0

# Options
FIX_MODE=false
STRICT_MODE=false
QUIET_MODE=false
JSON_MODE=false

# Parse arguments
SKILL_PATH=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --strict)
            STRICT_MODE=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
        --json)
            JSON_MODE=true
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

# Validate input
if [ -z "$SKILL_PATH" ]; then
    echo "Usage: lint-skill.sh <skill-path> [options]"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Directory not found: $SKILL_PATH"
    exit 1
fi

# Output functions
log_error() {
    ((ERRORS++))
    if [ "$JSON_MODE" = false ]; then
        echo -e "${RED}ERROR${NC}: $1"
        [ -n "$2" ] && echo "       File: $2"
        [ -n "$3" ] && echo "       Line: $3"
    fi
}

log_warning() {
    ((WARNINGS++))
    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo -e "${YELLOW}WARNING${NC}: $1"
        [ -n "$2" ] && echo "        File: $2"
    fi
}

log_info() {
    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo -e "${BLUE}INFO${NC}: $1"
    fi
}

log_fixed() {
    ((FIXED++))
    if [ "$JSON_MODE" = false ]; then
        echo -e "${GREEN}FIXED${NC}: $1"
    fi
}

# Header
if [ "$JSON_MODE" = false ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  LINTING SKILL: $(basename "$SKILL_PATH")"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
fi

# Check 1: SKILL.md exists
log_info "Checking SKILL.md..."
SKILL_MD="$SKILL_PATH/SKILL.md"
if [ ! -f "$SKILL_MD" ]; then
    log_error "SKILL.md not found" "$SKILL_PATH"
else
    # Check 2: YAML frontmatter
    log_info "Checking YAML frontmatter..."

    FIRST_LINE=$(head -n 1 "$SKILL_MD")
    if [ "$FIRST_LINE" != "---" ]; then
        log_error "Missing YAML frontmatter delimiter" "$SKILL_MD" "1"
    else
        # Extract frontmatter
        FRONTMATTER=$(sed -n '2,/^---$/p' "$SKILL_MD" | head -n -1)

        # Check required fields
        if ! echo "$FRONTMATTER" | grep -q "^name:"; then
            log_error "Missing required field: name" "$SKILL_MD"
        fi

        if ! echo "$FRONTMATTER" | grep -q "^description:"; then
            log_error "Missing required field: description" "$SKILL_MD"
        fi

        # Check name format
        NAME=$(echo "$FRONTMATTER" | grep "^name:" | sed 's/name:\s*//')
        if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
            log_warning "Name should be kebab-case: $NAME" "$SKILL_MD"
        fi

        # Check name length
        if [ ${#NAME} -gt 64 ]; then
            log_error "Name exceeds 64 characters: ${#NAME}" "$SKILL_MD"
        fi
    fi

    # Check 3: Markdown formatting
    log_info "Checking markdown formatting..."

    # Check for trailing whitespace
    TRAILING=$(grep -n '\s$' "$SKILL_MD" 2>/dev/null || true)
    if [ -n "$TRAILING" ]; then
        COUNT=$(echo "$TRAILING" | wc -l)
        log_warning "$COUNT lines have trailing whitespace" "$SKILL_MD"

        if [ "$FIX_MODE" = true ]; then
            sed -i 's/[[:space:]]*$//' "$SKILL_MD"
            log_fixed "Removed trailing whitespace"
        fi
    fi

    # Check for tabs (prefer spaces)
    TABS=$(grep -n $'\t' "$SKILL_MD" 2>/dev/null || true)
    if [ -n "$TABS" ]; then
        COUNT=$(echo "$TABS" | wc -l)
        log_warning "$COUNT lines contain tabs (prefer spaces)" "$SKILL_MD"

        if [ "$FIX_MODE" = true ]; then
            sed -i 's/\t/    /g' "$SKILL_MD"
            log_fixed "Converted tabs to spaces"
        fi
    fi

    # Check for unclosed code blocks
    CODE_BLOCKS=$(grep -c '```' "$SKILL_MD" || echo 0)
    if [ $((CODE_BLOCKS % 2)) -ne 0 ]; then
        log_error "Unclosed code block (odd number of \`\`\`)" "$SKILL_MD"
    fi

    # Check for very long lines
    LONG_LINES=$(awk 'length > 120 { print NR }' "$SKILL_MD" | head -5)
    if [ -n "$LONG_LINES" ]; then
        log_warning "Lines exceed 120 characters" "$SKILL_MD"
    fi
fi

# Check 4: References directory
if [ -d "$SKILL_PATH/references" ]; then
    log_info "Checking references..."

    for ref_file in "$SKILL_PATH/references"/*.md; do
        [ -f "$ref_file" ] || continue

        # Check encoding
        if ! file "$ref_file" | grep -q "UTF-8\|ASCII"; then
            log_warning "Non-UTF8 encoding detected" "$ref_file"
        fi

        # Check for empty files
        if [ ! -s "$ref_file" ]; then
            log_error "Empty reference file" "$ref_file"
        fi

        # Check trailing whitespace
        if grep -q '\s$' "$ref_file" 2>/dev/null; then
            log_warning "Trailing whitespace" "$ref_file"
            if [ "$FIX_MODE" = true ]; then
                sed -i 's/[[:space:]]*$//' "$ref_file"
                log_fixed "Cleaned $ref_file"
            fi
        fi
    done
fi

# Check 5: Scripts directory
if [ -d "$SKILL_PATH/scripts" ]; then
    log_info "Checking scripts..."

    for script_file in "$SKILL_PATH/scripts"/*.sh; do
        [ -f "$script_file" ] || continue

        # Check shebang
        FIRST_LINE=$(head -n 1 "$script_file")
        if [[ ! "$FIRST_LINE" =~ ^#! ]]; then
            log_warning "Missing shebang" "$script_file"
        fi

        # Check executable permission
        if [ ! -x "$script_file" ]; then
            log_warning "Script not executable" "$script_file"
            if [ "$FIX_MODE" = true ]; then
                chmod +x "$script_file"
                log_fixed "Made executable: $script_file"
            fi
        fi
    done
fi

# Check 6: File naming
log_info "Checking file naming..."
find "$SKILL_PATH" -name "* *" -type f | while read -r file; do
    log_warning "Filename contains spaces" "$file"
done

find "$SKILL_PATH" -name "*[A-Z]*" -type f | while read -r file; do
    # Skip SKILL.md which is uppercase by convention
    if [[ ! "$file" =~ SKILL\.md$ ]]; then
        log_warning "Filename contains uppercase" "$file"
    fi
done

# Summary
echo ""
echo "───────────────────────────────────────────────────────────"

if [ "$JSON_MODE" = true ]; then
    echo "{\"errors\": $ERRORS, \"warnings\": $WARNINGS, \"fixed\": $FIXED}"
else
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ No issues found${NC}"
    else
        echo -e "Results: ${RED}$ERRORS errors${NC}, ${YELLOW}$WARNINGS warnings${NC}"
        [ $FIXED -gt 0 ] && echo -e "         ${GREEN}$FIXED fixed${NC}"
    fi
fi

echo "═══════════════════════════════════════════════════════════"

# Exit code
if [ $ERRORS -gt 0 ]; then
    exit 1
elif [ "$STRICT_MODE" = true ] && [ $WARNINGS -gt 0 ]; then
    exit 1
else
    exit 0
fi
```

## Usage

```bash
# Basic lint
./lint-skill.sh ~/.claude/skills/my-skill/

# Auto-fix issues
./lint-skill.sh ~/.claude/skills/my-skill/ --fix

# Strict mode (warnings = errors)
./lint-skill.sh ~/.claude/skills/my-skill/ --strict

# Quiet mode (errors only)
./lint-skill.sh ~/.claude/skills/my-skill/ --quiet

# JSON output for CI
./lint-skill.sh ~/.claude/skills/my-skill/ --json
```

## Checks Performed

| Check | Severity | Auto-Fix |
|-------|----------|----------|
| SKILL.md exists | Error | No |
| YAML frontmatter present | Error | No |
| Required fields (name, description) | Error | No |
| Name format (kebab-case) | Warning | No |
| Name length (<=64) | Error | No |
| Trailing whitespace | Warning | Yes |
| Tabs vs spaces | Warning | Yes |
| Unclosed code blocks | Error | No |
| Long lines (>120) | Warning | No |
| Empty reference files | Error | No |
| Script shebang | Warning | No |
| Script executable | Warning | Yes |
| Filename spaces | Warning | No |
| Filename uppercase | Warning | No |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no errors) |
| 1 | Errors found (or warnings in strict mode) |

## Integration

```bash
# Pre-commit hook
#!/bin/bash
for skill in .claude/skills/*/; do
    if ! ./scripts/lint-skill.sh "$skill" --strict; then
        echo "Lint failed for: $skill"
        exit 1
    fi
done

# CI pipeline
- name: Lint Skills
  run: |
    for skill in .claude/skills/*/; do
      ./scripts/lint-skill.sh "$skill" --json
    done
```

## Sample Output

```
═══════════════════════════════════════════════════════════
  LINTING SKILL: api-doc-generator
═══════════════════════════════════════════════════════════

INFO: Checking SKILL.md...
INFO: Checking YAML frontmatter...
INFO: Checking markdown formatting...
WARNING: 3 lines have trailing whitespace
        File: SKILL.md
INFO: Checking references...
INFO: Checking scripts...
WARNING: Script not executable
        File: scripts/generate.sh
INFO: Checking file naming...

───────────────────────────────────────────────────────────
Results: 0 errors, 2 warnings
═══════════════════════════════════════════════════════════
```
