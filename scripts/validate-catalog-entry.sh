#!/bin/bash
# validate-catalog-entry.sh - Enhanced validation for catalog skill submissions
#
# Runs all standard checks plus catalog-specific quality gates:
# - All validate-all.sh checks
# - Description trigger analysis (must have what + when)
# - Reference link integrity (no broken links)
# - Quality score minimum 8.0 (higher than standard 7.0)
#
# Usage: validate-catalog-entry.sh <skill-directory>

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: $0 <skill-directory>"
    echo ""
    echo "Enhanced validation for catalog skill submissions."
    echo "Requires quality score >= 8.0 (vs standard 7.0)."
    exit 1
}

SKILL_DIR="${1:-}"

if [[ -z "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Skill directory required" >&2
    usage
fi

if [[ ! -d "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Not a directory: $SKILL_DIR" >&2
    exit 1
fi

SKILL_NAME=$(basename "$SKILL_DIR")
ERRORS=0

echo "Catalog Entry Validation: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Run all standard checks
echo "Step 1: Standard validation..."
if "$SCRIPT_DIR/validate-all.sh" "$SKILL_DIR"; then
    echo -e "${GREEN}✓${NC} Standard validation passed"
else
    echo -e "${RED}✗${NC} Standard validation failed"
    ((ERRORS++)) || true
fi

echo ""

# Step 2: Enhanced quality score (catalog requires >= 8.0)
echo "Step 2: Catalog quality gate (score >= 8.0)..."

SCORE_OUTPUT=$(python3 "$SCRIPT_DIR/score-skill.py" "$SKILL_DIR" --json 2>/dev/null || echo '{"overall_score": 0}')
SCORE=$(echo "$SCORE_OUTPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('overall_score', 0))" 2>/dev/null || echo "0")

if python3 -c "exit(0 if float('$SCORE') >= 8.0 else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Quality score: $SCORE/10 (catalog minimum: 8.0)"
else
    echo -e "${RED}✗${NC} Quality score: $SCORE/10 (catalog minimum: 8.0)"
    ((ERRORS++)) || true
fi

echo ""

# Step 3: Description trigger analysis
echo "Step 3: Description trigger analysis..."

SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ -f "$SKILL_MD" ]]; then
    DESC=$(sed -n '2,/^---$/p' "$SKILL_MD" | sed '$d' | grep -E '^description:' | sed 's/^description:\s*//' || echo "")

    if [[ -n "$DESC" ]]; then
        # Check for trigger context
        if echo "$DESC" | grep -qiE '\buse\s+when\b|\bwhen\s+(the\s+)?user\b|\bwhen\s+working\b|\buse\s+this\b'; then
            echo -e "${GREEN}✓${NC} Description includes trigger context (when to use)"
        else
            echo -e "${YELLOW}⚠${NC} Description lacks explicit trigger context (add 'Use when...')"
            # Warning, not error — but catalog should strive for this
        fi

        # Check first 250 chars have the key info
        FIRST_250="${DESC:0:250}"
        if [[ ${#DESC} -gt 250 ]]; then
            echo -e "${YELLOW}⚠${NC} Description is ${#DESC} chars — only first 250 shown in skill listing"
        fi
    fi
fi

echo ""

# Step 4: Reference link integrity
echo "Step 4: Reference link integrity..."
if "$SCRIPT_DIR/validate-structure.sh" "$SKILL_DIR" 2>/dev/null | grep -q "Broken reference"; then
    echo -e "${RED}✗${NC} Broken reference links found"
    ((ERRORS++)) || true
else
    echo -e "${GREEN}✓${NC} All reference links valid"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Catalog Entry Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}✓ APPROVED${NC} for catalog submission"
    exit 0
else
    echo -e "${RED}✗ NOT APPROVED${NC} — $ERRORS issue(s) must be fixed"
    exit 1
fi
