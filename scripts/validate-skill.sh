#!/usr/bin/env bash
# Validate a Claude Code skill against the Agent Skills specification
# Usage: validate-skill.sh <skill-directory>
#
# Supports .skillconfig for custom limits (useful for meta-skills)

set -euo pipefail

SKILL_DIR=""
PROFILE="strict"  # strict (default) or spec

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --profile=*) PROFILE="${arg#--profile=}" ;;
        *) SKILL_DIR="$arg" ;;
    esac
done

SKILL_DIR="${SKILL_DIR:-.}"
SKILL_MD="$SKILL_DIR/SKILL.md"
SKILL_CONFIG="$SKILL_DIR/.skillconfig"
ERRORS=0
WARNINGS=0
SCORE=10

if [[ "$PROFILE" != "strict" && "$PROFILE" != "spec" ]]; then
    echo "Error: Invalid profile '$PROFILE'. Use 'strict' or 'spec'." >&2
    exit 1
fi

# Default limits
LIMIT_REF_TOKENS=10000
SKIP_TOKEN_VALIDATION=false

# Load custom config if present
if [[ -f "$SKILL_CONFIG" ]]; then
    # Check for skip_token_validation
    if grep -q '"skip_token_validation".*:.*true' "$SKILL_CONFIG" 2>/dev/null; then
        SKIP_TOKEN_VALIDATION=true
    fi
    # Check for custom total_ref_tokens limit
    CUSTOM_LIMIT=$(grep -o '"total_ref_tokens"[[:space:]]*:[[:space:]]*[0-9]*' "$SKILL_CONFIG" 2>/dev/null | grep -o '[0-9]*' || echo "")
    if [[ -n "$CUSTOM_LIMIT" ]]; then
        LIMIT_REF_TOKENS=$CUSTOM_LIMIT
    fi
fi

error() { echo "❌ ERROR: $1"; ((ERRORS++)) || true; SCORE=$((SCORE - 2)); }
warn() { echo "⚠️  WARN: $1"; ((WARNINGS++)) || true; SCORE=$((SCORE - 1)); }
ok() { echo "✓ $1"; }

echo "═══════════════════════════════════════════════════"
echo "Validating skill: $SKILL_DIR"
echo "═══════════════════════════════════════════════════"

# Check SKILL.md exists
if [[ ! -f "$SKILL_MD" ]]; then
    error "SKILL.md not found"
    echo -e "\nScore: 0/10 (FAIL)"
    exit 1
fi
ok "SKILL.md exists"

# Check YAML frontmatter
if ! head -1 "$SKILL_MD" | grep -q "^---$"; then
    error "Missing YAML frontmatter (must start with ---)"
else
    ok "YAML frontmatter present"
fi

# Extract and validate name
NAME=$(grep "^name:" "$SKILL_MD" | head -1 | sed 's/name: *//' | tr -d '"' | tr -d "'")
if [[ -z "$NAME" ]]; then
    error "Missing 'name' in frontmatter"
else
    # Check length
    if [[ ${#NAME} -gt 64 ]]; then
        error "Name too long: ${#NAME} chars (max 64)"
    else
        ok "Name length: ${#NAME}/64 chars"
    fi

    # Check hyphen-case
    if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
        error "Name must be hyphen-case (lowercase, hyphens, start with letter)"
    else
        ok "Name is hyphen-case: $NAME"
    fi
fi

# Extract and validate description
DESC=$(grep "^description:" "$SKILL_MD" | head -1 | sed 's/description: *//')
if [[ -z "$DESC" ]]; then
    error "Missing 'description' in frontmatter"
else
    DESC_LEN=${#DESC}
    if [[ $DESC_LEN -gt 1024 ]]; then
        error "Description too long: $DESC_LEN chars (max 1024)"
    else
        ok "Description length: $DESC_LEN/1024 chars"
    fi
fi

# Check for recommended sections
echo -e "\n--- Section Check (profile: $PROFILE) ---"
for section in "Overview" "Workflow" "Examples"; do
    if grep -q "^## $section" "$SKILL_MD"; then
        ok "Section: $section"
    elif [[ "$PROFILE" == "strict" ]]; then
        warn "Missing recommended section: $section"
    else
        echo "ℹ️  INFO: Optional section not present: $section"
    fi
done

# Check for Output Checklist
if grep -q "^## Output Checklist" "$SKILL_MD" || grep -q "^## Checklist" "$SKILL_MD"; then
    ok "Section: Output Checklist"
elif [[ "$PROFILE" == "strict" ]]; then
    warn "Missing recommended section: Output Checklist"
else
    echo "ℹ️  INFO: Optional section not present: Output Checklist"
fi

# Token budget check — delegate to count-tokens.py (single source of truth)
echo -e "\n--- Token Budget Check ---"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN_SCRIPT="$SCRIPT_DIR/count-tokens.py"

if [[ -f "$TOKEN_SCRIPT" ]] && command -v python3 &>/dev/null; then
    # Parse JSON output from count-tokens.py
    TOKEN_JSON=$(python3 "$TOKEN_SCRIPT" "$SKILL_DIR" --json 2>/dev/null || echo "")
    if [[ -n "$TOKEN_JSON" ]]; then
        # Extract values via Python (reliable JSON parsing)
        mapfile -t TOKEN_VALS < <(python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
print(d.get('skill_md_tokens', 0))
print(d.get('skill_md_lines', 0))
print(d.get('ref_total_tokens', 0))
print(d.get('exit_code', 0))
" <<< "$TOKEN_JSON")
        MD_TOKENS="${TOKEN_VALS[0]}"
        LINE_COUNT="${TOKEN_VALS[1]}"
        REF_TOKENS="${TOKEN_VALS[2]}"
        TOKEN_EXIT="${TOKEN_VALS[3]}"

        # SKILL.md lines
        if [[ $LINE_COUNT -gt 1000 ]]; then
            error "SKILL.md too long: $LINE_COUNT lines (hard limit 1000)"
        elif [[ $LINE_COUNT -gt 500 ]]; then
            warn "SKILL.md exceeds recommended limit: $LINE_COUNT lines (recommended < 500)"
        else
            ok "SKILL.md line count: $LINE_COUNT/500 lines"
        fi

        # SKILL.md tokens
        if [[ $MD_TOKENS -gt 10000 ]]; then
            error "SKILL.md tokens too high: $MD_TOKENS (hard limit 10000)"
        elif [[ $MD_TOKENS -gt 5000 ]]; then
            warn "SKILL.md tokens exceeds recommended: $MD_TOKENS (recommended < 5000)"
        else
            ok "SKILL.md tokens: $MD_TOKENS/5000"
        fi

        # References tokens
        if [[ -d "$SKILL_DIR/references" ]]; then
            if [[ "$SKIP_TOKEN_VALIDATION" == "true" ]]; then
                ok "References tokens: $REF_TOKENS (validation skipped via .skillconfig)"
            elif [[ $REF_TOKENS -gt $LIMIT_REF_TOKENS ]]; then
                error "References too large: $REF_TOKENS tokens (max $LIMIT_REF_TOKENS)"
            else
                ok "References tokens: $REF_TOKENS/$LIMIT_REF_TOKENS"
            fi
        fi
    else
        warn "count-tokens.py produced no output, skipping token check"
    fi
else
    warn "count-tokens.py or python3 not available, skipping token check"
fi

# Check scripts are executable
echo -e "\n--- Scripts Check ---"
if [[ -d "$SKILL_DIR/scripts" ]]; then
    for script in "$SKILL_DIR/scripts"/*.sh; do
        [[ -f "$script" ]] || continue
        if [[ -x "$script" ]]; then
            ok "Executable: $(basename "$script")"
        else
            warn "Not executable: $(basename "$script")"
        fi
    done
else
    ok "No scripts/ directory (optional)"
fi

# Final score
echo -e "\n═══════════════════════════════════════════════════"
[[ $SCORE -lt 0 ]] && SCORE=0
echo "Score: $SCORE/10"
echo "Errors: $ERRORS | Warnings: $WARNINGS"

if [[ $SCORE -ge 7 ]]; then
    echo "Status: PASS ✓"
    exit 0
else
    echo "Status: FAIL (minimum 7.0 required)"
    exit 1
fi
