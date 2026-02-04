#!/usr/bin/env bash
# regenerate-skill.sh - Regenerate an upstream skill through the Platxa pipeline.
#
# Uses Claude Code CLI natively to orchestrate the regeneration pipeline:
# Intent Agent → Discovery Agent → Architecture → Generation → Validation
#
# Usage:
#   ./scripts/regenerate-skill.sh skills/figma                              # Full pipeline
#   ./scripts/regenerate-skill.sh skills/figma --dry-run                    # Show plan only
#   ./scripts/regenerate-skill.sh --intent-file intents/figma.json          # From pre-extracted intent
#   ./scripts/regenerate-skill.sh skills/figma --output-dir out/figma       # Custom output
#   ./scripts/regenerate-skill.sh --batch --dry-run                         # All upstream skills

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOW_DOC="$PROJECT_ROOT/references/workflows/regeneration-pipeline.md"

# --- Argument parsing ---

SKILL_DIR=""
INTENT_FILE=""
OUTPUT_DIR=""
DRY_RUN=false
BATCH_MODE=false

usage() {
  cat <<'EOF'
Usage: regenerate-skill.sh <skill-dir> [options]
       regenerate-skill.sh --intent-file <json> [options]
       regenerate-skill.sh --batch [options]

Input modes (mutually exclusive):
  <skill-dir>       Upstream skill directory (full pipeline: Intent → Discovery → ...)
  --intent-file     Pre-extracted intent JSON (skip Intent Agent: Discovery → ...)

Options:
  --dry-run         Show regeneration plan without executing
  --output-dir      Write regenerated skill to this directory
  --batch           Regenerate all upstream skills from manifest
  -h, --help        Show this help message

Examples:
  ./scripts/regenerate-skill.sh skills/figma                          # Full pipeline
  ./scripts/regenerate-skill.sh skills/figma --dry-run                # Dry-run
  ./scripts/regenerate-skill.sh --intent-file intents/figma.json      # From intent
  ./scripts/regenerate-skill.sh --batch --dry-run                     # Batch dry-run
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)      DRY_RUN=true; shift ;;
    --intent-file)  INTENT_FILE="$2"; shift 2 ;;
    --output-dir)   OUTPUT_DIR="$2"; shift 2 ;;
    --batch)        BATCH_MODE=true; shift ;;
    -h|--help)      usage ;;
    -*)             echo "Error: Unknown option: $1" >&2; exit 1 ;;
    *)              SKILL_DIR="$1"; shift ;;
  esac
done

# --- Validation ---

if [[ "$BATCH_MODE" = false && -z "$SKILL_DIR" && -z "$INTENT_FILE" ]]; then
  echo "Error: Provide a skill directory, --intent-file, or --batch" >&2
  usage
fi

if [[ -n "$SKILL_DIR" && -n "$INTENT_FILE" ]]; then
  echo "Error: Cannot use both <skill-dir> and --intent-file" >&2
  exit 1
fi

if [[ -n "$SKILL_DIR" && ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "Error: SKILL.md not found in $SKILL_DIR" >&2
  exit 1
fi

if [[ -n "$INTENT_FILE" && ! -f "$INTENT_FILE" ]]; then
  echo "Error: Intent file not found: $INTENT_FILE" >&2
  exit 1
fi

if [[ ! -f "$WORKFLOW_DOC" ]]; then
  echo "Error: Workflow document not found: $WORKFLOW_DOC" >&2
  exit 1
fi

if ! command -v claude &>/dev/null; then
  echo "Error: claude CLI not found. Install Claude Code first." >&2
  exit 1
fi

# --- Single skill regeneration ---

regenerate_from_upstream() {
  local skill_dir="$1"
  local output_dir="${2:-$skill_dir}"
  local skill_name
  skill_name="$(basename "$skill_dir")"

  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "SKIP: $skill_name (no SKILL.md)" >&2
    return 1
  fi

  local mode_instruction=""
  if [[ "$DRY_RUN" = true ]]; then
    mode_instruction="Mode: DRY-RUN. Follow the Dry-Run Mode section of the workflow document. Show the regeneration plan only. Do NOT invoke any agents, generate files, or make any changes."
  else
    mode_instruction="Mode: EXECUTE. Run the full regeneration pipeline. Write the regenerated skill to: $output_dir"
  fi

  local prompt
  prompt="$(cat <<PROMPT
Follow the regeneration pipeline defined in references/workflows/regeneration-pipeline.md.

Input mode: UPSTREAM DIRECTORY
Upstream skill directory: $skill_dir
Output directory: $output_dir

$mode_instruction

Start from Phase 1 (Intent Extraction) — read the upstream skill and extract its intent, then continue through all phases.
Read the workflow document first, then execute the appropriate mode.
PROMPT
)"

  echo "═══════════════════════════════════════════════════"
  echo "Regenerating: $skill_name (from upstream)"
  echo "═══════════════════════════════════════════════════"

  claude -p "$prompt" --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch,Task"
  local exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    echo "FAIL: $skill_name (claude exited with $exit_code)" >&2
    return 1
  fi

  echo ""
  return 0
}

regenerate_from_intent() {
  local intent_file="$1"
  local output_dir="$2"
  local skill_name
  skill_name="$(python3 -c "import json,sys; print(json.load(open('$intent_file'))['skill_name'])" 2>/dev/null || basename "${intent_file%.json}")"

  if [[ -z "$output_dir" ]]; then
    output_dir="$PROJECT_ROOT/skills/$skill_name"
  fi

  local mode_instruction=""
  if [[ "$DRY_RUN" = true ]]; then
    mode_instruction="Mode: DRY-RUN. Follow the Dry-Run Mode section of the workflow document. Show the regeneration plan only — include the intent summary from the provided JSON. Do NOT invoke any agents, generate files, or make any changes."
  else
    mode_instruction="Mode: EXECUTE. Run the regeneration pipeline starting from Phase 2 (Discovery Enrichment). Write the regenerated skill to: $output_dir"
  fi

  local prompt
  prompt="$(cat <<PROMPT
Follow the regeneration pipeline defined in references/workflows/regeneration-pipeline.md.

Input mode: PRE-EXTRACTED INTENT
Intent file: $intent_file
Output directory: $output_dir

$mode_instruction

Phase 1 (Intent Extraction) is ALREADY DONE — the intent JSON file contains the extracted intent. Read it, then continue from Phase 2 (Discovery Enrichment) through all remaining phases.
Read the workflow document first, then execute the appropriate mode.
PROMPT
)"

  echo "═══════════════════════════════════════════════════"
  echo "Regenerating: $skill_name (from intent file)"
  echo "═══════════════════════════════════════════════════"

  claude -p "$prompt" --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch,Task"
  local exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    echo "FAIL: $skill_name (claude exited with $exit_code)" >&2
    return 1
  fi

  echo ""
  return 0
}

# --- Batch mode ---

regenerate_batch() {
  local skills_dir="$PROJECT_ROOT/skills"
  local total=0
  local success=0
  local failed=0
  local skipped=0

  echo "═══════════════════════════════════════════════════"
  echo "Batch Regeneration$([ "$DRY_RUN" = true ] && echo " (DRY-RUN)")"
  echo "═══════════════════════════════════════════════════"
  echo ""

  for skill_dir in "$skills_dir"/*/; do
    [[ -d "$skill_dir" ]] || continue
    total=$((total + 1))

    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
      skipped=$((skipped + 1))
      continue
    fi

    local out_dir="${OUTPUT_DIR:+$OUTPUT_DIR/$(basename "$skill_dir")}"
    if regenerate_from_upstream "$skill_dir" "${out_dir:-$skill_dir}"; then
      success=$((success + 1))
    else
      failed=$((failed + 1))
    fi
  done

  echo ""
  echo "═══════════════════════════════════════════════════"
  echo "Batch Complete: $success success, $failed failed, $skipped skipped (of $total)"
  echo "═══════════════════════════════════════════════════"
}

# --- Main ---

if [[ "$BATCH_MODE" = true ]]; then
  regenerate_batch
elif [[ -n "$INTENT_FILE" ]]; then
  regenerate_from_intent "$INTENT_FILE" "$OUTPUT_DIR"
else
  output="${OUTPUT_DIR:-$SKILL_DIR}"
  regenerate_from_upstream "$SKILL_DIR" "$output"
fi
