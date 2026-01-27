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

# Parse frontmatter with Python yaml.safe_load (always available, no yq dependency)
# Outputs one field per line to avoid bash IFS delimiter collapsing on empty fields
PARSED=$(python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(sys.stdin)
    if not isinstance(data, dict):
        print('__YAML_ERROR__')
        sys.exit(0)
    name = str(data.get('name', '') or '')
    desc = str(data.get('description', '') or '')
    # Accept both 'tools' and 'allowed-tools'
    tools_key = ''
    tools_list = []
    if 'allowed-tools' in data:
        tools_key = 'allowed-tools'
        tools_list = data['allowed-tools'] or []
    elif 'tools' in data:
        tools_key = 'tools'
        tools_list = data['tools'] or []
    tools_csv = ','.join(str(t) for t in tools_list) if tools_list else ''
    model = str(data.get('model', '') or '')
    fields = '|'.join(str(k) for k in data.keys())
    # One field per line — bash readarray handles empty lines correctly
    for val in [name, desc, tools_key, tools_csv, model, fields]:
        print(val)
except yaml.YAMLError:
    print('__YAML_ERROR__')
" <<< "$FRONTMATTER")

if [[ "$PARSED" == "__YAML_ERROR__" ]]; then
    error "Invalid YAML syntax"
    exit 1
fi

info "Valid YAML syntax"

# Read fields line-by-line (readarray preserves empty lines, unlike IFS read)
mapfile -t PARSED_LINES <<< "$PARSED"
NAME="${PARSED_LINES[0]}"
DESC="${PARSED_LINES[1]}"
TOOLS_KEY="${PARSED_LINES[2]}"
TOOLS_CSV="${PARSED_LINES[3]}"
MODEL="${PARSED_LINES[4]}"
FIELD_NAMES="${PARSED_LINES[5]}"

echo ""
echo "Checking required fields..."

# Check name field
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

# Check tools field (already parsed: TOOLS_KEY and TOOLS_CSV from Python)
if [[ -n "$TOOLS_KEY" ]]; then
    if [[ -n "$TOOLS_CSV" ]]; then
        IFS=',' read -ra TOOL_ARRAY <<< "$TOOLS_CSV"
        TOOL_COUNT=${#TOOL_ARRAY[@]}
        info "tools field present with $TOOL_COUNT tools"

        # Validate tool names
        VALID_TOOLS="Read Write Edit MultiEdit Glob Grep LS Bash Task WebFetch WebSearch AskUserQuestion TodoWrite KillShell BashOutput NotebookEdit"

        for TOOL in "${TOOL_ARRAY[@]}"; do
            [[ -z "$TOOL" ]] && continue
            if ! echo "$VALID_TOOLS" | grep -qw "$TOOL"; then
                error "Invalid tool: $TOOL"
            fi
        done
    else
        info "tools field present but empty"
    fi
else
    info "No tools field (optional)"
fi

# Check model field (already parsed from Python)
if [[ -n "$MODEL" ]]; then
    if [[ "$MODEL" =~ ^(opus|sonnet|haiku)$ ]]; then
        info "model field valid: $MODEL"
    else
        error "Invalid model: $MODEL (must be opus, sonnet, or haiku)"
    fi
fi

# Check for unknown fields
echo ""
echo "Checking for unknown fields..."

KNOWN_FIELDS="name description tools allowed-tools model subagent_type run_in_background license metadata"

IFS='|' read -ra FIELD_ARRAY <<< "$FIELD_NAMES"
for field in "${FIELD_ARRAY[@]}"; do
    [[ -z "$field" ]] && continue
    if ! echo "$KNOWN_FIELDS" | grep -qw "$field"; then
        warn "Unknown field will be ignored: $field"
    fi
done

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
