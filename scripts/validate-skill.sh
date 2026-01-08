#!/usr/bin/env bash
# Validate a Claude Code skill against the Agent Skills specification
# Usage: validate-skill.sh <skill-directory>

set -euo pipefail

SKILL_DIR="${1:-.}"
SKILL_MD="$SKILL_DIR/SKILL.md"
ERRORS=0
WARNINGS=0
SCORE=10

error() { echo "❌ ERROR: $1"; ((ERRORS++)); SCORE=$((SCORE - 2)); }
warn() { echo "⚠️  WARN: $1"; ((WARNINGS++)); SCORE=$((SCORE - 1)); }
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
    if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
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

# Check for required sections
echo -e "\n--- Section Check ---"
for section in "Overview" "Workflow" "Examples"; do
    if grep -q "^## $section" "$SKILL_MD"; then
        ok "Section: $section"
    else
        warn "Missing recommended section: $section"
    fi
done

# Check for Output Checklist
if grep -q "^## Output Checklist" "$SKILL_MD" || grep -q "^## Checklist" "$SKILL_MD"; then
    ok "Section: Output Checklist"
else
    warn "Missing recommended section: Output Checklist"
fi

# Check line count (token proxy)
echo -e "\n--- Token Budget Check ---"
LINE_COUNT=$(wc -l < "$SKILL_MD")
if [[ $LINE_COUNT -gt 500 ]]; then
    error "SKILL.md too long: $LINE_COUNT lines (max 500)"
elif [[ $LINE_COUNT -gt 450 ]]; then
    warn "SKILL.md approaching limit: $LINE_COUNT/500 lines"
else
    ok "SKILL.md line count: $LINE_COUNT/500 lines"
fi

# Estimate tokens (roughly 1.3 tokens per word)
WORD_COUNT=$(wc -w < "$SKILL_MD")
EST_TOKENS=$((WORD_COUNT * 13 / 10))
if [[ $EST_TOKENS -gt 5000 ]]; then
    error "Estimated tokens too high: ~$EST_TOKENS (max 5000)"
elif [[ $EST_TOKENS -gt 4000 ]]; then
    warn "Estimated tokens approaching limit: ~$EST_TOKENS/5000"
else
    ok "Estimated tokens: ~$EST_TOKENS/5000"
fi

# Check references total if present
if [[ -d "$SKILL_DIR/references" ]]; then
    REF_WORDS=0
    for ref in "$SKILL_DIR/references"/*.md "$SKILL_DIR/references"/**/*.md; do
        [[ -f "$ref" ]] || continue
        REF_WORDS=$((REF_WORDS + $(wc -w < "$ref")))
    done
    REF_TOKENS=$((REF_WORDS * 13 / 10))
    if [[ $REF_TOKENS -gt 10000 ]]; then
        error "References too large: ~$REF_TOKENS tokens (max 10000)"
    else
        ok "References tokens: ~$REF_TOKENS/10000"
    fi
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
