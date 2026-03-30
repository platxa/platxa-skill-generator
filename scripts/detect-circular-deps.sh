#!/usr/bin/env bash
# detect-circular-deps.sh - Detect circular dependencies in installed skills
#
# Builds a dependency graph from all installed skills and detects cycles
# using DFS-based topological sort.
#
# Usage:
#   detect-circular-deps.sh [--user|--project|--dir <path>] [--json]
#
# Exit codes:
#   0 - No circular dependencies found
#   1 - Circular dependency detected
#   2 - Usage error

set -euo pipefail

# Colors
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' NC=''
fi

usage() {
    echo "Usage: $(basename "$0") [--user|--project|--dir <path>] [--json]"
    echo ""
    echo "Detect circular dependencies among installed skills."
    echo ""
    echo "Options:"
    echo "  --user        Check ~/.claude/skills/ (default)"
    echo "  --project     Check .claude/skills/"
    echo "  --dir <path>  Check a specific skills directory"
    echo "  --json        Output results as JSON"
    echo "  -h, --help    Show this help"
    exit 2
}

# Parse arguments
SKILLS_DIR="$HOME/.claude/skills"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --user)    SKILLS_DIR="$HOME/.claude/skills"; shift ;;
        --project) SKILLS_DIR=".claude/skills"; shift ;;
        --dir)     SKILLS_DIR="$2"; shift 2 ;;
        --json)    JSON_OUTPUT=true; shift ;;
        -h|--help) usage ;;
        *)         echo "Unknown option: $1" >&2; usage ;;
    esac
done

if [[ ! -d "$SKILLS_DIR" ]]; then
    if $JSON_OUTPUT; then
        echo '{"skills":0,"edges":0,"cycles":[],"has_cycles":false}'
    else
        echo -e "${YELLOW}Skills directory not found:${NC} $SKILLS_DIR"
    fi
    exit 0
fi

# Build adjacency list from all skills' depends-on fields
# Format: SKILL_NAME:DEP1,DEP2,...
declare -A GRAPH
declare -A SKILL_EXISTS
SKILL_COUNT=0

for skill_dir in "$SKILLS_DIR"/*/; do
    [[ -f "${skill_dir}SKILL.md" ]] || continue

    skill_name=$(basename "$skill_dir")
    SKILL_EXISTS[$skill_name]=1
    SKILL_COUNT=$((SKILL_COUNT + 1))

    # Extract depends-on
    frontmatter=$(sed -n '2,/^---$/p' "${skill_dir}SKILL.md" | sed '$d')
    deps=$(echo "$frontmatter" | sed -n '/^depends-on:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

    if [[ -n "$deps" ]]; then
        dep_list=""
        while IFS= read -r dep; do
            [[ -z "$dep" ]] && continue
            [[ -n "$dep_list" ]] && dep_list+=","
            dep_list+="$dep"
        done <<< "$deps"
        GRAPH[$skill_name]="$dep_list"
    else
        GRAPH[$skill_name]=""
    fi
done

if [[ $SKILL_COUNT -eq 0 ]]; then
    if $JSON_OUTPUT; then
        echo '{"skills":0,"edges":0,"cycles":[],"has_cycles":false}'
    else
        echo "No skills found in $SKILLS_DIR"
    fi
    exit 0
fi

# Count edges
EDGE_COUNT=0
for deps in "${GRAPH[@]}"; do
    if [[ -n "$deps" ]]; then
        EDGE_COUNT=$((EDGE_COUNT + $(echo "$deps" | tr ',' '\n' | wc -l)))
    fi
done

# DFS-based cycle detection
# States: 0=unvisited, 1=in-progress, 2=done
declare -A STATE
CYCLE_COUNT=0
declare -a CYCLES=()

# Track the current DFS path for cycle reporting
declare -a DFS_PATH

detect_cycle() {
    local node="$1"
    STATE[$node]=1
    DFS_PATH+=("$node")

    local deps_str="${GRAPH[$node]:-}"
    if [[ -n "$deps_str" ]]; then
        IFS=',' read -ra deps <<< "$deps_str"
        for dep in "${deps[@]}"; do
            # Only check deps that exist as installed skills
            [[ -z "${SKILL_EXISTS[$dep]:-}" ]] && continue

            case "${STATE[$dep]:-0}" in
                1)
                    # Found cycle - extract the cycle from DFS_PATH
                    local cycle=""
                    local in_cycle=false
                    for p in "${DFS_PATH[@]}"; do
                        if [[ "$p" == "$dep" ]]; then
                            in_cycle=true
                        fi
                        if $in_cycle; then
                            [[ -n "$cycle" ]] && cycle+=" → "
                            cycle+="$p"
                        fi
                    done
                    cycle+=" → $dep"
                    CYCLES+=("$cycle")
                    CYCLE_COUNT=$((CYCLE_COUNT + 1))
                    ;;
                0)
                    detect_cycle "$dep"
                    ;;
            esac
        done
    fi

    STATE[$node]=2
    unset 'DFS_PATH[${#DFS_PATH[@]}-1]'
}

# Run DFS from every node
for skill in "${!GRAPH[@]}"; do
    if [[ "${STATE[$skill]:-0}" == "0" ]]; then
        DFS_PATH=()
        detect_cycle "$skill"
    fi
done

# Output results
if $JSON_OUTPUT; then
    cycles_json="["
    first=true
    for cycle in "${CYCLES[@]+"${CYCLES[@]}"}"; do
        $first || cycles_json+=","
        first=false
        cycles_json+="\"$cycle\""
    done
    cycles_json+="]"

    has_cycles="false"
    [[ $CYCLE_COUNT -gt 0 ]] && has_cycles="true"

    echo "{\"skills\":$SKILL_COUNT,\"edges\":$EDGE_COUNT,\"cycles\":$cycles_json,\"has_cycles\":$has_cycles}"
else
    echo "Dependency Graph Analysis"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Skills: $SKILL_COUNT"
    echo "  Edges:  $EDGE_COUNT"
    echo ""

    if [[ $CYCLE_COUNT -eq 0 ]]; then
        echo -e "${GREEN}✓ No circular dependencies detected${NC}"
    else
        echo -e "${RED}✗ Circular dependencies found:${NC}"
        echo ""
        for cycle in "${CYCLES[@]}"; do
            echo -e "  ${RED}●${NC} $cycle"
        done
        echo ""
        echo "Fix by removing one depends-on entry in each cycle."
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

[[ $CYCLE_COUNT -eq 0 ]] && exit 0 || exit 1
