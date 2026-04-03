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

# Check tools field - support both "tools:" and "allowed-tools:" (Claude Code official)
HAS_TOOLS=$(echo "$FRONTMATTER" | grep -E '^(tools|allowed-tools):' || echo "")

if [[ -n "$HAS_TOOLS" ]]; then
    # Extract all lines that look like tool entries (lines starting with - after tools:/allowed-tools:)
    TOOLS=$(echo "$FRONTMATTER" | sed -n '/^\(tools\|allowed-tools\):/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

    if [[ -n "$TOOLS" ]]; then
        TOOL_COUNT=$(echo "$TOOLS" | wc -l)
        info "tools field present with $TOOL_COUNT tools"

        # Validate tool names
        VALID_TOOLS="Read Write Edit MultiEdit Glob Grep LS Bash Task Agent Skill WebFetch WebSearch AskUserQuestion TodoWrite KillShell BashOutput NotebookEdit"

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

# Check depends-on field - validate each entry is a valid skill name
DEPENDS_ON=$(echo "$FRONTMATTER" | sed -n '/^depends-on:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

if [[ -n "$DEPENDS_ON" ]]; then
    DEP_COUNT=$(echo "$DEPENDS_ON" | wc -l)
    info "depends-on field present with $DEP_COUNT dependencies"

    while IFS= read -r dep; do
        [[ -z "$dep" ]] && continue
        if [[ ! "$dep" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
            error "Invalid dependency name: $dep (must be hyphen-case)"
        elif [[ ${#dep} -gt 64 ]]; then
            error "Dependency name too long: $dep (max 64 chars)"
        elif [[ "$dep" == *"--"* ]]; then
            error "Dependency name has consecutive hyphens: $dep"
        fi
    done <<< "$DEPENDS_ON"
fi

# Check suggests field - validate each entry is a valid skill name
SUGGESTS=$(echo "$FRONTMATTER" | sed -n '/^suggests:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

if [[ -n "$SUGGESTS" ]]; then
    SUG_COUNT=$(echo "$SUGGESTS" | wc -l)
    info "suggests field present with $SUG_COUNT suggestions"

    while IFS= read -r sug; do
        [[ -z "$sug" ]] && continue
        if [[ ! "$sug" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
            error "Invalid suggestion name: $sug (must be hyphen-case)"
        fi
    done <<< "$SUGGESTS"
fi

# Check disable-model-invocation field (must be boolean if present)
DMI=$(echo "$FRONTMATTER" | grep -E '^disable-model-invocation:' | sed 's/^disable-model-invocation:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$DMI" ]]; then
    if [[ "$DMI" =~ ^(true|false|yes|no)$ ]]; then
        info "disable-model-invocation field valid: $DMI"
    else
        error "Invalid disable-model-invocation: $DMI (must be true, false, yes, or no)"
    fi
fi

# Check user-invocable field (must be boolean if present)
UI=$(echo "$FRONTMATTER" | grep -E '^user-invocable:' | sed 's/^user-invocable:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$UI" ]]; then
    if [[ "$UI" =~ ^(true|false|yes|no)$ ]]; then
        info "user-invocable field valid: $UI"
    else
        error "Invalid user-invocable: $UI (must be true, false, yes, or no)"
    fi
fi

# Warn on conflicting invocation control
if [[ "$DMI" == "true" && "$UI" == "false" ]]; then
    warn "Conflicting: disable-model-invocation=true AND user-invocable=false means nobody can invoke this skill"
fi

# Check context field (must be "fork" if present)
CONTEXT=$(echo "$FRONTMATTER" | grep -E '^context:' | sed 's/^context:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$CONTEXT" ]]; then
    if [[ "$CONTEXT" == "fork" ]]; then
        info "context field valid: fork"
    else
        error "Invalid context: $CONTEXT (must be 'fork')"
    fi
fi

# Check agent field (only valid with context: fork)
AGENT=$(echo "$FRONTMATTER" | grep -E '^agent:' | sed 's/^agent:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$AGENT" ]]; then
    if [[ -z "$CONTEXT" ]]; then
        warn "agent field set but context is not 'fork' — agent will be ignored"
    else
        info "agent field present: $AGENT"
    fi
fi

# Check effort field (must be low/medium/high/max if present)
EFFORT=$(echo "$FRONTMATTER" | grep -E '^effort:' | sed 's/^effort:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$EFFORT" ]]; then
    if [[ "$EFFORT" =~ ^(low|medium|high|max)$ ]] || [[ "$EFFORT" =~ ^[0-9]+$ ]]; then
        info "effort field valid: $EFFORT"
    else
        error "Invalid effort: $EFFORT (must be low, medium, high, max, or a positive integer)"
    fi
fi

# Check argument-hint field (just validate it's a non-empty string)
ARG_HINT=$(echo "$FRONTMATTER" | grep -E '^argument-hint:' | sed 's/^argument-hint:\s*//' || echo "")

if [[ -n "$ARG_HINT" ]]; then
    info "argument-hint field present: $ARG_HINT"
fi

# Check shell field (must be bash or powershell if present)
SHELL_VAL=$(echo "$FRONTMATTER" | grep -E '^shell:' | sed 's/^shell:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$SHELL_VAL" ]]; then
    if [[ "$SHELL_VAL" =~ ^(bash|powershell)$ ]]; then
        info "shell field valid: $SHELL_VAL"
    else
        error "Invalid shell: $SHELL_VAL (must be bash or powershell)"
    fi
fi

# Check version field (semantic versioning if present)
VERSION=$(echo "$FRONTMATTER" | grep -E '^version:' | sed 's/^version:\s*//' | tr -d '"' | tr -d "'" || echo "")

if [[ -n "$VERSION" ]]; then
    if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
        info "version field valid: $VERSION"
    else
        warn "version field not semver: $VERSION (recommended format: X.Y.Z)"
    fi
fi

# Check when_to_use / when-to-use field (non-empty string)
WHEN_TO_USE=$(echo "$FRONTMATTER" | grep -E '^when[_-]to[_-]use:' | sed 's/^when[_-]to[_-]use:\s*//' || echo "")

if [[ -n "$WHEN_TO_USE" ]]; then
    info "when_to_use field present"
fi

# Check paths field (just validate presence, glob patterns are free-form)
HAS_PATHS=$(echo "$FRONTMATTER" | grep -E '^paths:' || echo "")

if [[ -n "$HAS_PATHS" ]]; then
    info "paths field present (glob patterns for activation scope)"
fi

# Check hooks field (just validate presence — structure is complex YAML)
HAS_HOOKS=$(echo "$FRONTMATTER" | grep -E '^hooks:' || echo "")

if [[ -n "$HAS_HOOKS" ]]; then
    info "hooks field present (lifecycle hooks)"
fi

# Check for unknown fields
echo ""
echo "Checking for unknown fields..."

# All fields recognized by Claude Code skills spec + our extensions
KNOWN_FIELDS="name description allowed-tools tools model agent context disable-model-invocation user-invocable argument-hint effort hooks paths shell metadata depends-on suggests subagent_type run_in_background version when_to_use when-to-use"
FIELD_NAMES=$(echo "$FRONTMATTER" | grep -E '^[a-z][a-z0-9_-]*:' | sed 's/:.*$//' || echo "")

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
