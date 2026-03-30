#!/usr/bin/env bash
# skill-graph.sh - Output dependency graph of installed skills in DOT format
#
# Usage:
#   skill-graph.sh [--user|--project|--dir <path>]
#   skill-graph.sh --user | dot -Tpng -o skills.png   # Render with graphviz
#
# Exit codes:
#   0 - Graph generated
#   2 - Usage error

set -euo pipefail

usage() {
    echo "Usage: $(basename "$0") [--user|--project|--dir <path>]"
    echo ""
    echo "Output skill dependency graph in DOT format."
    echo ""
    echo "Options:"
    echo "  --user        Check ~/.claude/skills/ (default)"
    echo "  --project     Check .claude/skills/"
    echo "  --dir <path>  Check a specific skills directory"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") --user                          # Print DOT to stdout"
    echo "  $(basename "$0") --user | dot -Tpng -o graph.png # Render PNG"
    exit 2
}

SKILLS_DIR="$HOME/.claude/skills"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --user)    SKILLS_DIR="$HOME/.claude/skills"; shift ;;
        --project) SKILLS_DIR=".claude/skills"; shift ;;
        --dir)     SKILLS_DIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *)         echo "Unknown option: $1" >&2; usage ;;
    esac
done

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "digraph skills { }"
    exit 0
fi

echo "digraph skills {"
echo '  rankdir=LR;'
echo '  node [shape=box, style=rounded, fontname="Helvetica"];'
echo '  edge [fontname="Helvetica", fontsize=10];'
echo ""

for skill_dir in "$SKILLS_DIR"/*/; do
    [[ -f "${skill_dir}SKILL.md" ]] || continue

    skill_name=$(basename "$skill_dir")
    echo "  \"$skill_name\";"

    frontmatter=$(sed -n '2,/^---$/p' "${skill_dir}SKILL.md" | sed '$d')

    # depends-on edges (solid, red)
    deps=$(echo "$frontmatter" | sed -n '/^depends-on:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")
    if [[ -n "$deps" ]]; then
        while IFS= read -r dep; do
            [[ -z "$dep" ]] && continue
            echo "  \"$skill_name\" -> \"$dep\" [color=red, label=\"depends\"];"
        done <<< "$deps"
    fi

    # suggests edges (dashed, blue)
    suggests=$(echo "$frontmatter" | sed -n '/^suggests:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")
    if [[ -n "$suggests" ]]; then
        while IFS= read -r sug; do
            [[ -z "$sug" ]] && continue
            echo "  \"$skill_name\" -> \"$sug\" [style=dashed, color=blue, label=\"suggests\"];"
        done <<< "$suggests"
    fi
done

echo "}"
