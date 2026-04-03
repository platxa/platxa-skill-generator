#!/usr/bin/env bash
set -euo pipefail

# Run eval prompts against a skill and collect results.
#
# Usage: run-eval.sh <skill-directory> [--workspace <dir>] [--baseline]
#
# Requires: claude CLI, jq
#
# Reads evals/evals.json from the skill directory, spawns claude -p for each
# eval prompt, and saves outputs to the workspace directory.
#
# Exit code: 0 = all evals ran, 1 = usage error, 2 = missing dependencies

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
    echo "Run eval prompts against a skill using claude -p."
    echo ""
    echo "Options:"
    echo "  --workspace <dir>   Output directory (default: <skill-dir>/eval-workspace)"
    echo "  --baseline          Run without skill (baseline comparison)"
    echo "  --iteration <n>     Iteration number (default: 1)"
    echo ""
    echo "Requires: claude CLI, jq"
    echo ""
    echo "Input:  <skill-dir>/evals/evals.json"
    echo "Output: <workspace>/iteration-<n>/eval-<id>/with_skill/outputs/"
    exit 1
}

# Check dependencies
check_deps() {
    local missing=0
    if ! command -v claude &>/dev/null; then
        error "claude CLI not found. Install: https://docs.anthropic.com/en/docs/claude-code"
        missing=1
    fi
    if ! command -v jq &>/dev/null; then
        error "jq not found. Install: sudo apt install jq"
        missing=1
    fi
    if [[ $missing -eq 1 ]]; then
        exit 2
    fi
}

# Parse arguments
SKILL_DIR=""
WORKSPACE=""
BASELINE=false
ITERATION=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        --baseline)
            BASELINE=true
            shift
            ;;
        --iteration)
            ITERATION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            error "Unknown option: $1"
            usage
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

SKILL_DIR="$(cd "$SKILL_DIR" && pwd)"
EVALS_FILE="$SKILL_DIR/evals/evals.json"

if [[ ! -f "$EVALS_FILE" ]]; then
    error "evals.json not found: $EVALS_FILE"
    echo "Create evals/evals.json first. See: references/validation/eval-schema.md"
    exit 1
fi

check_deps

# Set workspace
if [[ -z "$WORKSPACE" ]]; then
    WORKSPACE="$SKILL_DIR/eval-workspace"
fi

ITER_DIR="$WORKSPACE/iteration-$ITERATION"
CONFIG_NAME="with_skill"
if [[ "$BASELINE" == true ]]; then
    CONFIG_NAME="without_skill"
fi

# Parse evals
SKILL_NAME=$(jq -r '.skill_name' "$EVALS_FILE")
EVAL_COUNT=$(jq '.evals | length' "$EVALS_FILE")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Eval Runner: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Skill: $SKILL_DIR"
echo "  Evals: $EVAL_COUNT"
echo "  Mode:  $CONFIG_NAME"
echo "  Iteration: $ITERATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PASSED=0
FAILED=0

for i in $(seq 0 $((EVAL_COUNT - 1))); do
    EVAL_ID=$(jq -r ".evals[$i].id" "$EVALS_FILE")
    EVAL_NAME=$(jq -r ".evals[$i].name // \"eval-$EVAL_ID\"" "$EVALS_FILE")
    EVAL_PROMPT=$(jq -r ".evals[$i].prompt" "$EVALS_FILE")
    EVAL_EXPECTED=$(jq -r ".evals[$i].expected_output" "$EVALS_FILE")

    # Create output directory
    EVAL_DIR="$ITER_DIR/$EVAL_NAME/$CONFIG_NAME"
    OUTPUT_DIR="$EVAL_DIR/outputs"
    mkdir -p "$OUTPUT_DIR"

    step "Running eval $((i+1))/$EVAL_COUNT: $EVAL_NAME"

    # Save eval metadata
    jq -n \
        --argjson id "$EVAL_ID" \
        --arg name "$EVAL_NAME" \
        --arg prompt "$EVAL_PROMPT" \
        --arg expected "$EVAL_EXPECTED" \
        --arg config "$CONFIG_NAME" \
        '{eval_id: $id, eval_name: $name, prompt: $prompt, expected_output: $expected, configuration: $config}' \
        > "$EVAL_DIR/eval_metadata.json"

    # Build claude command
    CLAUDE_ARGS=("-p" "$EVAL_PROMPT" "--output-format" "text")

    if [[ "$BASELINE" == false ]]; then
        # With skill: add skill directory to allowed paths
        CLAUDE_ARGS+=("--allowedTools" "Read,Write,Edit,Bash,Glob,Grep")
        # Prepend skill context to the prompt
        EVAL_PROMPT_WITH_SKILL="Use the skill at $SKILL_DIR to accomplish this task: $EVAL_PROMPT"
        CLAUDE_ARGS=("-p" "$EVAL_PROMPT_WITH_SKILL" "--output-format" "text")
    fi

    # Run claude and capture output + timing
    START_TIME=$(date +%s%N)

    if claude "${CLAUDE_ARGS[@]}" > "$OUTPUT_DIR/response.txt" 2>"$OUTPUT_DIR/stderr.txt"; then
        PASSED=$((PASSED + 1))
        info "Eval $EVAL_NAME completed"
    else
        FAILED=$((FAILED + 1))
        warn "Eval $EVAL_NAME failed (exit code $?)"
    fi

    END_TIME=$(date +%s%N)
    DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))

    # Save timing
    jq -n \
        --argjson duration_ms "$DURATION_MS" \
        --argjson duration_s "$(echo "scale=1; $DURATION_MS / 1000" | bc)" \
        '{duration_ms: $duration_ms, total_duration_seconds: $duration_s}' \
        > "$EVAL_DIR/timing.json"

    echo ""
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Eval Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Passed: $PASSED / $EVAL_COUNT"
echo "  Failed: $FAILED / $EVAL_COUNT"
echo "  Results: $ITER_DIR"
echo ""

if [[ $FAILED -gt 0 ]]; then
    warn "$FAILED eval(s) failed"
fi

info "Eval run complete. Next: run grader agent to evaluate expectations."
exit 0
