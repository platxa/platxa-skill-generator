#!/usr/bin/env bash
set -euo pipefail

# Test skill trigger accuracy — validates that a skill's description causes
# Claude to load it for relevant queries and NOT load it for irrelevant ones.
#
# Usage: test-triggers.sh <skill-directory> [--dry-run]
#
# Requires: jq
#
# Reads trigger-tests.json from the skill directory (or evals/ subdirectory):
#   {
#     "skill_name": "my-skill",
#     "should_trigger": [
#       "Help me set up a new project",
#       "I need to create a workspace"
#     ],
#     "should_not_trigger": [
#       "What's the weather?",
#       "Help me write Python code"
#     ]
#   }
#
# Reports trigger rate (goal: >=90%) and false positive rate (goal: 0%).
#
# Exit code: 0 = all targets met, 1 = usage error, 2 = missing deps, 3 = targets missed

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

error() { echo -e "${RED}ERROR:${NC} $1" >&2; }
info() { echo -e "${GREEN}OK:${NC} $1"; }
warn() { echo -e "${YELLOW}WARN:${NC} $1" >&2; }
step() { echo -e "${CYAN}>>>${NC} $1"; }

usage() {
    echo "Usage: $0 <skill-directory> [options]"
    echo ""
    echo "Test skill trigger accuracy using description analysis."
    echo ""
    echo "Options:"
    echo "  --dry-run             Show what would be tested without running"
    echo "  --trigger-rate <n>    Minimum trigger rate target (default: 90)"
    echo "  --fp-rate <n>         Maximum false positive rate target (default: 0)"
    echo "  --json                Output results as JSON"
    echo ""
    echo "Input:  <skill-dir>/trigger-tests.json or <skill-dir>/evals/trigger-tests.json"
    echo "Output: Trigger rate and false positive rate report"
    exit 1
}

# Check dependencies
check_deps() {
    if ! command -v jq &>/dev/null; then
        error "jq not found. Install: sudo apt install jq"
        exit 2
    fi
}

# Extract description from SKILL.md frontmatter
extract_description() {
    local skill_md="$1"
    local content frontmatter desc

    content=$(cat "$skill_md")
    frontmatter=$(echo "$content" | sed -n '2,/^---$/p' | sed '$d')

    # Extract multiline description
    desc=$(echo "$frontmatter" | sed -n '/^description:/,/^[a-z]/p' | head -n -1 | sed 's/^description:\s*//' | tr -d '\n' | sed 's/^[>|]-\?\s*//')

    # Fallback to single-line
    if [[ -z "$desc" ]]; then
        desc=$(echo "$frontmatter" | grep -E '^description:' | sed 's/^description:\s*//' | sed 's/^[>|]-\?\s*//')
    fi

    echo "$desc"
}

# Evaluate if a prompt would trigger a skill based on description matching
# Uses keyword overlap and semantic similarity heuristics
evaluate_trigger() {
    local prompt="$1"
    local description="$2"
    local skill_name="$3"

    # Normalize to lowercase for comparison
    local prompt_lower
    prompt_lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')
    local desc_lower
    desc_lower=$(echo "$description" | tr '[:upper:]' '[:lower:]')

    local score=0
    local max_score=0

    # 1. Check if skill name keywords appear in prompt (weight: 3)
    local name_words
    name_words=$(echo "$skill_name" | tr '-' '\n')
    while IFS= read -r word; do
        [[ -z "$word" ]] && continue
        [[ ${#word} -lt 3 ]] && continue  # Skip short words
        ((max_score += 3)) || true
        if echo "$prompt_lower" | grep -qiw "$word"; then
            ((score += 3)) || true
        fi
    done <<< "$name_words"

    # 2. Extract trigger phrases from description ("Use when..." patterns)
    local trigger_context
    trigger_context=$(echo "$desc_lower" | grep -oP '(?:use when|use for|use if|when user|when the user|asks? (?:to|for|about)|says?|mentions?)[^.]*' || echo "")
    if [[ -n "$trigger_context" ]]; then
        # Extract key action words from trigger phrases
        local trigger_words
        trigger_words=$(echo "$trigger_context" | tr ' "'"'"',' '\n' | sort -u | grep -E '^[a-z]{3,}$' | grep -vE '^(the|and|for|use|when|user|asks|says|that|this|with|from|into|about|also|each|will|your|them|then|they|what|does|have|been|were|here|more|some|such|only|like|just|very|most|many|much|well|over|even|also|back|into|than|upon|used|been|make|made|give|need|want|help)$' || echo "")
        while IFS= read -r tw; do
            [[ -z "$tw" ]] && continue
            ((max_score += 2)) || true
            if echo "$prompt_lower" | grep -qiw "$tw"; then
                ((score += 2)) || true
            fi
        done <<< "$trigger_words"
    fi

    # 3. Extract domain keywords from description (weight: 1)
    local desc_words
    desc_words=$(echo "$desc_lower" | tr ' ,.;:!?()[]{}/"'"'"'' '\n' | sort -u | grep -E '^[a-z]{4,}$' | grep -vE '^(the|and|for|use|when|user|asks|this|with|from|into|that|will|your|them|then|they|what|does|have|been|were|here|more|some|such|only|like|just|very|most|many|much|well|over|even|also|back|into|than|upon|used|been|make|made|each|code|file|tool|following|including|across|specific|based|using|create|check|should|after|before|during|between)$' || echo "")
    while IFS= read -r dw; do
        [[ -z "$dw" ]] && continue
        ((max_score += 1)) || true
        if echo "$prompt_lower" | grep -qiw "$dw"; then
            ((score += 1)) || true
        fi
    done <<< "$desc_words"

    # 4. Check for negative triggers ("Do NOT use for..." patterns)
    local negative_context
    negative_context=$(echo "$desc_lower" | grep -oP '(?:do not|don.t|not for|not use for|not when)[^.]*' || echo "")
    if [[ -n "$negative_context" ]]; then
        local neg_words
        neg_words=$(echo "$negative_context" | tr ' "'"'"',' '\n' | sort -u | grep -E '^[a-z]{3,}$' | grep -vE '^(the|and|for|use|when|not|don|this|with|from)$' || echo "")
        while IFS= read -r nw; do
            [[ -z "$nw" ]] && continue
            if echo "$prompt_lower" | grep -qiw "$nw"; then
                # Negative match — reduce score significantly
                ((score -= 3)) || true
            fi
        done <<< "$neg_words"
    fi

    # Ensure max_score is at least 1 to avoid division by zero
    [[ $max_score -lt 1 ]] && max_score=1
    # Clamp score to 0
    [[ $score -lt 0 ]] && score=0

    # Calculate percentage
    local pct=$((score * 100 / max_score))

    # Trigger threshold: 20% keyword overlap suggests relevance
    if [[ $pct -ge 20 ]]; then
        echo "trigger"
    else
        echo "no_trigger"
    fi
}

# Parse arguments
DRY_RUN=false
JSON_OUTPUT=false
TRIGGER_RATE_TARGET=90
FP_RATE_TARGET=0
SKILL_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        --dry-run) DRY_RUN=true; shift ;;
        --json) JSON_OUTPUT=true; shift ;;
        --trigger-rate) TRIGGER_RATE_TARGET="$2"; shift 2 ;;
        --fp-rate) FP_RATE_TARGET="$2"; shift 2 ;;
        -*) error "Unknown option: $1"; usage ;;
        *) SKILL_DIR="$1"; shift ;;
    esac
done

if [[ -z "$SKILL_DIR" ]]; then
    error "Skill directory required"
    usage
fi

check_deps

# Find trigger-tests.json
TRIGGER_FILE=""
if [[ -f "$SKILL_DIR/trigger-tests.json" ]]; then
    TRIGGER_FILE="$SKILL_DIR/trigger-tests.json"
elif [[ -f "$SKILL_DIR/evals/trigger-tests.json" ]]; then
    TRIGGER_FILE="$SKILL_DIR/evals/trigger-tests.json"
else
    error "trigger-tests.json not found in $SKILL_DIR or $SKILL_DIR/evals/"
    echo "Expected format:"
    echo '  {"should_trigger": ["prompt1", ...], "should_not_trigger": ["prompt2", ...]}'
    exit 1
fi

# Validate SKILL.md exists
SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
    error "SKILL.md not found in $SKILL_DIR"
    exit 1
fi

# Extract skill info
DESCRIPTION=$(extract_description "$SKILL_MD")
SKILL_NAME=$(jq -r '.skill_name // empty' "$TRIGGER_FILE" 2>/dev/null || basename "$SKILL_DIR")

if [[ -z "$DESCRIPTION" ]]; then
    error "Could not extract description from SKILL.md"
    exit 1
fi

# Read test prompts
SHOULD_TRIGGER=$(jq -r '.should_trigger[]' "$TRIGGER_FILE" 2>/dev/null || echo "")
SHOULD_NOT_TRIGGER=$(jq -r '.should_not_trigger[]' "$TRIGGER_FILE" 2>/dev/null || echo "")

TRIGGER_COUNT=$(jq '.should_trigger | length' "$TRIGGER_FILE" 2>/dev/null || echo "0")
NOT_TRIGGER_COUNT=$(jq '.should_not_trigger | length' "$TRIGGER_FILE" 2>/dev/null || echo "0")

if [[ $TRIGGER_COUNT -eq 0 && $NOT_TRIGGER_COUNT -eq 0 ]]; then
    error "trigger-tests.json has no test prompts"
    exit 1
fi

step "Testing triggers for: $SKILL_NAME"
echo "  Description: ${DESCRIPTION:0:80}..."
echo "  Should trigger: $TRIGGER_COUNT prompts"
echo "  Should NOT trigger: $NOT_TRIGGER_COUNT prompts"
echo "  Targets: trigger rate >= ${TRIGGER_RATE_TARGET}%, false positive rate <= ${FP_RATE_TARGET}%"
echo ""

if $DRY_RUN; then
    echo "=== DRY RUN ==="
    echo ""
    echo "Should trigger:"
    echo "$SHOULD_TRIGGER" | while IFS= read -r p; do
        [[ -z "$p" ]] && continue
        echo "  + $p"
    done
    echo ""
    echo "Should NOT trigger:"
    echo "$SHOULD_NOT_TRIGGER" | while IFS= read -r p; do
        [[ -z "$p" ]] && continue
        echo "  - $p"
    done
    exit 0
fi

# Run trigger tests
TRIGGER_PASS=0
TRIGGER_FAIL=0
FP_PASS=0
FP_FAIL=0

# Test should_trigger prompts
if [[ $TRIGGER_COUNT -gt 0 ]]; then
    step "Testing should-trigger prompts..."
    while IFS= read -r prompt; do
        [[ -z "$prompt" ]] && continue
        result=$(evaluate_trigger "$prompt" "$DESCRIPTION" "$SKILL_NAME")
        if [[ "$result" == "trigger" ]]; then
            info "  TRIGGER: $prompt"
            ((TRIGGER_PASS++)) || true
        else
            warn "  MISS:    $prompt"
            ((TRIGGER_FAIL++)) || true
        fi
    done <<< "$SHOULD_TRIGGER"
    echo ""
fi

# Test should_not_trigger prompts
if [[ $NOT_TRIGGER_COUNT -gt 0 ]]; then
    step "Testing should-NOT-trigger prompts..."
    while IFS= read -r prompt; do
        [[ -z "$prompt" ]] && continue
        result=$(evaluate_trigger "$prompt" "$DESCRIPTION" "$SKILL_NAME")
        if [[ "$result" == "no_trigger" ]]; then
            info "  CORRECT: $prompt"
            ((FP_PASS++)) || true
        else
            warn "  FALSE+:  $prompt"
            ((FP_FAIL++)) || true
        fi
    done <<< "$SHOULD_NOT_TRIGGER"
    echo ""
fi

# Calculate rates
TRIGGER_TOTAL=$((TRIGGER_PASS + TRIGGER_FAIL))
FP_TOTAL=$((FP_PASS + FP_FAIL))

if [[ $TRIGGER_TOTAL -gt 0 ]]; then
    TRIGGER_RATE=$((TRIGGER_PASS * 100 / TRIGGER_TOTAL))
else
    TRIGGER_RATE=100
fi

if [[ $FP_TOTAL -gt 0 ]]; then
    FP_RATE=$((FP_FAIL * 100 / FP_TOTAL))
else
    FP_RATE=0
fi

# Results
TRIGGER_MET=true
FP_MET=true
[[ $TRIGGER_RATE -lt $TRIGGER_RATE_TARGET ]] && TRIGGER_MET=false
[[ $FP_RATE -gt $FP_RATE_TARGET ]] && FP_MET=false

if $JSON_OUTPUT; then
    jq -n \
        --arg skill "$SKILL_NAME" \
        --argjson trigger_pass "$TRIGGER_PASS" \
        --argjson trigger_fail "$TRIGGER_FAIL" \
        --argjson trigger_rate "$TRIGGER_RATE" \
        --argjson trigger_target "$TRIGGER_RATE_TARGET" \
        --argjson fp_pass "$FP_PASS" \
        --argjson fp_fail "$FP_FAIL" \
        --argjson fp_rate "$FP_RATE" \
        --argjson fp_target "$FP_RATE_TARGET" \
        --argjson trigger_met "$( $TRIGGER_MET && echo true || echo false )" \
        --argjson fp_met "$( $FP_MET && echo true || echo false )" \
        '{
            skill: $skill,
            trigger: { passed: $trigger_pass, failed: $trigger_fail, rate: $trigger_rate, target: $trigger_target, met: $trigger_met },
            false_positive: { passed: $fp_pass, failed: $fp_fail, rate: $fp_rate, target: $fp_target, met: $fp_met },
            overall: ($trigger_met and $fp_met)
        }'
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Trigger Test Results: $SKILL_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if $TRIGGER_MET; then
        echo -e "  Trigger rate:       ${GREEN}${TRIGGER_RATE}%${NC} (${TRIGGER_PASS}/${TRIGGER_TOTAL}) — target: >= ${TRIGGER_RATE_TARGET}%"
    else
        echo -e "  Trigger rate:       ${RED}${TRIGGER_RATE}%${NC} (${TRIGGER_PASS}/${TRIGGER_TOTAL}) — target: >= ${TRIGGER_RATE_TARGET}%"
    fi

    if $FP_MET; then
        echo -e "  False positive rate: ${GREEN}${FP_RATE}%${NC} (${FP_FAIL}/${FP_TOTAL}) — target: <= ${FP_RATE_TARGET}%"
    else
        echo -e "  False positive rate: ${RED}${FP_RATE}%${NC} (${FP_FAIL}/${FP_TOTAL}) — target: <= ${FP_RATE_TARGET}%"
    fi

    echo ""

    if $TRIGGER_MET && $FP_MET; then
        echo -e "  ${GREEN}✓ ALL TARGETS MET${NC}"
    else
        echo -e "  ${RED}✗ TARGETS MISSED${NC}"
        if ! $TRIGGER_MET; then
            echo "    - Trigger rate below target. Add more trigger phrases to description."
        fi
        if ! $FP_MET; then
            echo "    - False positive rate above target. Add negative triggers (Do NOT use for...)."
        fi
    fi
fi

# Exit code
if $TRIGGER_MET && $FP_MET; then
    exit 0
else
    exit 3
fi
