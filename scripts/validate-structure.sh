#!/usr/bin/env bash
# validate-structure.sh - Validate skill directory structure
#
# Usage: validate-structure.sh <skill-directory>
#
# Checks:
# - SKILL.md exists
# - Directory structure is correct
# - Required files present
# - Permissions correct

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
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
    echo "Validates skill directory structure."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo "  -v, --verbose Show detailed output"
    exit 1
}

# Parse arguments
VERBOSE=false
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
        *)
            SKILL_DIR="$1"
            shift
            ;;
    esac
done

if [[ -z "$SKILL_DIR" ]]; then
    error "Skill directory required"
    usage
fi

# Resolve to absolute path
SKILL_DIR=$(cd "$SKILL_DIR" 2>/dev/null && pwd) || {
    error "Directory does not exist: $SKILL_DIR"
    exit 1
}

SKILL_NAME=$(basename "$SKILL_DIR")

echo "Validating structure: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check 1: SKILL.md exists
echo ""
echo "Checking required files..."

SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ -f "$SKILL_MD" ]]; then
    info "SKILL.md exists"
else
    error "SKILL.md not found"
fi

# Check 2: SKILL.md is readable
if [[ -r "$SKILL_MD" ]]; then
    info "SKILL.md is readable"
else
    error "SKILL.md is not readable"
fi

# Check 3: SKILL.md is not empty
if [[ -s "$SKILL_MD" ]]; then
    info "SKILL.md is not empty"
else
    error "SKILL.md is empty"
fi

# Check 4: SKILL.md starts with frontmatter
if head -1 "$SKILL_MD" 2>/dev/null | grep -q '^---$'; then
    info "SKILL.md has frontmatter"
else
    error "SKILL.md missing frontmatter (must start with ---)"
fi

# Check 5: Directory structure
echo ""
echo "Checking directory structure..."

# Check for unexpected files in root
for file in "$SKILL_DIR"/*; do
    if [[ -f "$file" ]]; then
        fname=$(basename "$file")
        case "$fname" in
            SKILL.md|README.md|LICENSE)
                # Expected files
                ;;
            *)
                warn "Unexpected file in root: $fname"
                ;;
        esac
    fi
done

# Check references directory
REFS_DIR="$SKILL_DIR/references"
if [[ -d "$REFS_DIR" ]]; then
    info "references/ directory exists"

    # Check for markdown files
    MD_COUNT=$(find "$REFS_DIR" -name "*.md" | wc -l)
    if [[ $MD_COUNT -gt 0 ]]; then
        info "Found $MD_COUNT reference files"
    else
        warn "references/ directory is empty"
    fi

    # Check for non-markdown files
    OTHER_COUNT=$(find "$REFS_DIR" -type f ! -name "*.md" | wc -l)
    if [[ $OTHER_COUNT -gt 0 ]]; then
        warn "Found $OTHER_COUNT non-markdown files in references/"
    fi
else
    if $VERBOSE; then
        info "No references/ directory (optional)"
    fi
fi

# Check scripts directory
SCRIPTS_DIR="$SKILL_DIR/scripts"
if [[ -d "$SCRIPTS_DIR" ]]; then
    info "scripts/ directory exists"

    # Check for script files
    SCRIPT_COUNT=$(find "$SCRIPTS_DIR" \( -name "*.sh" -o -name "*.py" \) | wc -l)
    if [[ $SCRIPT_COUNT -gt 0 ]]; then
        info "Found $SCRIPT_COUNT scripts"
    else
        warn "scripts/ directory has no .sh or .py files"
    fi

    # Check script permissions
    echo ""
    echo "Checking script permissions..."

    for script in "$SCRIPTS_DIR"/*.sh; do
        [[ -e "$script" ]] || continue
        if [[ -x "$script" ]]; then
            info "$(basename "$script") is executable"
        else
            error "$(basename "$script") is not executable"
        fi
    done

    for script in "$SCRIPTS_DIR"/*.py; do
        [[ -e "$script" ]] || continue
        if [[ -x "$script" ]]; then
            info "$(basename "$script") is executable"
        else
            warn "$(basename "$script") is not executable (optional for Python)"
        fi
    done
else
    if $VERBOSE; then
        info "No scripts/ directory (optional)"
    fi
fi

# Check templates directory
TEMPLATES_DIR="$SKILL_DIR/templates"
if [[ -d "$TEMPLATES_DIR" ]]; then
    info "templates/ directory exists"
    TEMPLATE_COUNT=$(find "$TEMPLATES_DIR" -type f | wc -l)
    info "Found $TEMPLATE_COUNT template files"
fi

# Check 6: No hidden files (except .gitkeep)
echo ""
echo "Checking for hidden files..."

HIDDEN_FILES=$(find "$SKILL_DIR" -name ".*" ! -name ".gitkeep" ! -name ".gitignore" -type f)
if [[ -n "$HIDDEN_FILES" ]]; then
    warn "Found hidden files:"
    echo "$HIDDEN_FILES" | while read -r f; do
        echo "  - $f"
    done
else
    info "No unexpected hidden files"
fi

# Check 7: No large files
echo ""
echo "Checking file sizes..."

LARGE_FILES=$(find "$SKILL_DIR" -type f -size +100k)
if [[ -n "$LARGE_FILES" ]]; then
    warn "Found files > 100KB:"
    echo "$LARGE_FILES" | while read -r f; do
        SIZE=$(du -h "$f" | cut -f1)
        echo "  - $(basename "$f"): $SIZE"
    done
else
    info "All files under 100KB"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Structure Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 1
fi
