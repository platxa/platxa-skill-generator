#!/bin/bash
# validate-frontmatter.sh - Validate SKILL.md frontmatter
#
# Usage: validate-frontmatter.sh <skill-directory>
#
# Checks:
# - Frontmatter exists and is valid YAML
# - Required fields: name, description
# - Field constraints (length, format)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
    echo "Validates SKILL.md frontmatter against spec."
    exit 1
}

# Parse arguments
SKILL_DIR="${1:-}"

if [[ -z "$SKILL_DIR" ]]; then
    error "Skill directory required"
    usage
fi

SKILL_MD="$SKILL_DIR/SKILL.md"

if [[ ! -f "$SKILL_MD" ]]; then
    error "SKILL.md not found: $SKILL_MD"
    exit 1
fi

echo "Validating frontmatter: $(basename "$SKILL_DIR")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Extract frontmatter
CONTENT=$(cat "$SKILL_MD")

# Check starts with ---
if ! echo "$CONTENT" | head -1 | grep -q '^---$'; then
    error "File must start with --- (frontmatter delimiter)"
    exit 1
fi

# Extract frontmatter content (between first and second ---)
FRONTMATTER=$(echo "$CONTENT" | sed -n '2,/^---$/p' | sed '$d')

if [[ -z "$FRONTMATTER" ]]; then
    error "Empty frontmatter"
    exit 1
fi

info "Frontmatter found"

# Validate YAML syntax (if yq is available)
if command -v yq &>/dev/null; then
    if echo "$FRONTMATTER" | yq eval '.' - &>/dev/null; then
        info "Valid YAML syntax"
    else
        error "Invalid YAML syntax"
    fi
else
    warn "yq not installed, skipping YAML syntax validation"
fi

echo ""
echo "Checking required fields..."

# Check name field
NAME=$(echo "$FRONTMATTER" | grep -E '^name:' | sed 's/^name:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -z "$NAME" ]]; then
    error "Missing required field: name"
else
    info "name field present: $NAME"

    # Check name format (hyphen-case)
    if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
        error "name must be hyphen-case (lowercase letters, numbers, hyphens)"
    else
        info "name format valid (hyphen-case)"
    fi

    # Check name length
    NAME_LEN=${#NAME}
    if [[ $NAME_LEN -gt 64 ]]; then
        error "name too long: $NAME_LEN chars (max 64)"
    elif [[ $NAME_LEN -lt 2 ]]; then
        error "name too short: $NAME_LEN chars (min 2)"
    else
        info "name length valid: $NAME_LEN chars"
    fi

    # Check for double hyphens
    if [[ "$NAME" == *"--"* ]]; then
        error "name cannot contain consecutive hyphens"
    fi
fi

# Check description field
DESC=$(echo "$FRONTMATTER" | sed -n '/^description:/,/^[a-z]/p' | head -n -1 | sed 's/^description:\s*//' | tr -d '\n' | sed 's/^|//' || echo "")

# Try simpler extraction if multiline didn't work
if [[ -z "$DESC" ]]; then
    DESC=$(echo "$FRONTMATTER" | grep -E '^description:' | sed 's/^description:\s*//' || echo "")
fi

if [[ -z "$DESC" ]]; then
    error "Missing required field: description"
else
    info "description field present"

    # Check description length
    DESC_LEN=${#DESC}
    if [[ $DESC_LEN -gt 1024 ]]; then
        error "description too long: $DESC_LEN chars (max 1024)"
    elif [[ $DESC_LEN -lt 10 ]]; then
        warn "description very short: $DESC_LEN chars"
    else
        info "description length valid: $DESC_LEN chars"
    fi

    # Check for placeholders
    if echo "$DESC" | grep -qiE '(TODO|TBD|FIXME|placeholder)'; then
        error "description contains placeholder text"
    fi
fi

echo ""
echo "Checking optional fields..."

# Check tools field - extract all tool entries under tools: section
HAS_TOOLS=$(echo "$FRONTMATTER" | grep -E '^tools:' || echo "")

if [[ -n "$HAS_TOOLS" ]]; then
    # Extract all lines that look like tool entries (lines starting with - after tools:)
    TOOLS=$(echo "$FRONTMATTER" | sed -n '/^tools:/,/^[a-z_]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

    if [[ -n "$TOOLS" ]]; then
        TOOL_COUNT=$(echo "$TOOLS" | wc -l)
        info "tools field present with $TOOL_COUNT tools"

        # Validate tool names
        VALID_TOOLS="Read Write Edit MultiEdit Glob Grep LS Bash Task WebFetch WebSearch AskUserQuestion TodoWrite KillShell BashOutput NotebookEdit"

        while IFS= read -r TOOL; do
            [[ -z "$TOOL" ]] && continue
            if ! echo "$VALID_TOOLS" | grep -qw "$TOOL"; then
                error "Invalid tool: $TOOL"
            fi
        done <<< "$TOOLS"
    else
        info "tools field present but empty"
    fi
else
    info "No tools field (optional)"
fi

# Check model field
MODEL=$(echo "$FRONTMATTER" | grep -E '^model:' | sed 's/^model:\s*//' || echo "")

if [[ -n "$MODEL" ]]; then
    if [[ "$MODEL" =~ ^(opus|sonnet|haiku)$ ]]; then
        info "model field valid: $MODEL"
    else
        error "Invalid model: $MODEL (must be opus, sonnet, or haiku)"
    fi
fi

# Check subagent_type field
SUBAGENT=$(echo "$FRONTMATTER" | grep -E '^subagent_type:' | sed 's/^subagent_type:\s*//' || echo "")

if [[ -n "$SUBAGENT" ]]; then
    info "subagent_type field present: $SUBAGENT"
fi

# Check for unknown fields
echo ""
echo "Checking for unknown fields..."

KNOWN_FIELDS="name description tools model subagent_type run_in_background"
FIELD_NAMES=$(echo "$FRONTMATTER" | grep -E '^[a-z_]+:' | sed 's/:.*$//' || echo "")

while IFS= read -r field; do
    [[ -z "$field" ]] && continue
    if ! echo "$KNOWN_FIELDS" | grep -qw "$field"; then
        warn "Unknown field will be ignored: $field"
    fi
done <<< "$FIELD_NAMES"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontmatter Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ PASSED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 0
else
    echo -e "${RED}✗ FAILED${NC} - $ERRORS errors, $WARNINGS warnings"
    exit 1
fi
