#!/usr/bin/env bash
# check-dependencies.sh - Check if a skill's depends-on requirements are installed
#
# Usage: check-dependencies.sh <skill-directory> [--project-dir <path>]
#
# Reads depends-on from SKILL.md frontmatter and checks if each dependency
# is installed in ~/.claude/skills/ or .claude/skills/.
#
# Exit codes:
#   0 - All dependencies satisfied (or no dependencies declared)
#   1 - One or more dependencies missing
#   2 - Usage error (missing SKILL.md, bad arguments)

set -euo pipefail

# Colors (only when outputting to terminal)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

usage() {
    echo "Usage: $(basename "$0") <skill-directory> [--project-dir <path>]"
    echo ""
    echo "Check if a skill's depends-on requirements are installed."
    echo ""
    echo "Options:"
    echo "  --project-dir <path>  Project root for .claude/skills/ lookup"
    echo "                        (default: current directory)"
    echo "  --json                Output results as JSON"
    echo "  -h, --help            Show this help message"
    exit 2
}

# Parse arguments
SKILL_DIR=""
PROJECT_DIR="."
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-dir)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo -e "${RED}Error:${NC} Unknown option: $1" >&2
            usage
            ;;
        *)
            SKILL_DIR="$1"
            shift
            ;;
    esac
done

if [[ -z "$SKILL_DIR" ]]; then
    echo -e "${RED}Error:${NC} Skill directory required" >&2
    usage
fi

SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
    echo -e "${RED}Error:${NC} SKILL.md not found: $SKILL_MD" >&2
    exit 2
fi

# Extract skill name
SKILL_NAME=$(grep -m1 "^name:" "$SKILL_MD" | sed 's/^name:\s*//' | tr -d '"' | tr -d "'" || echo "")

# Extract depends-on entries from frontmatter
# Frontmatter is between first --- and second ---
FRONTMATTER=$(sed -n '2,/^---$/p' "$SKILL_MD" | sed '$d')

DEPENDS_ON=$(echo "$FRONTMATTER" | sed -n '/^depends-on:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")

if [[ -z "$DEPENDS_ON" ]]; then
    if $JSON_OUTPUT; then
        echo '{"skill":"'"${SKILL_NAME}"'","dependencies":[],"missing":[],"satisfied":true}'
    else
        echo -e "${GREEN}No dependencies declared${NC} for ${SKILL_NAME:-unknown}"
    fi
    exit 0
fi

# Check each dependency
USER_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS="$PROJECT_DIR/.claude/skills"

MISSING=()
FOUND=()

while IFS= read -r dep; do
    [[ -z "$dep" ]] && continue

    # Check user skills directory
    if [[ -d "$USER_SKILLS/$dep" ]] && [[ -f "$USER_SKILLS/$dep/SKILL.md" ]]; then
        FOUND+=("$dep")
        continue
    fi

    # Check project skills directory
    if [[ -d "$PROJECT_SKILLS/$dep" ]] && [[ -f "$PROJECT_SKILLS/$dep/SKILL.md" ]]; then
        FOUND+=("$dep")
        continue
    fi

    MISSING+=("$dep")
done <<< "$DEPENDS_ON"

TOTAL=${#FOUND[@]}
TOTAL=$((TOTAL + ${#MISSING[@]}))

if $JSON_OUTPUT; then
    # Build JSON arrays
    deps_json="["
    first=true
    while IFS= read -r dep; do
        [[ -z "$dep" ]] && continue
        $first || deps_json+=","
        first=false
        deps_json+="\"$dep\""
    done <<< "$DEPENDS_ON"
    deps_json+="]"

    missing_json="["
    first=true
    for m in "${MISSING[@]+"${MISSING[@]}"}"; do
        $first || missing_json+=","
        first=false
        missing_json+="\"$m\""
    done
    missing_json+="]"

    satisfied="true"
    [[ ${#MISSING[@]} -gt 0 ]] && satisfied="false"

    echo "{\"skill\":\"${SKILL_NAME}\",\"dependencies\":${deps_json},\"missing\":${missing_json},\"satisfied\":${satisfied}}"
else
    echo "Checking dependencies for: ${SKILL_NAME:-unknown}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for dep in "${FOUND[@]+"${FOUND[@]}"}"; do
        echo -e "  ${GREEN}✓${NC} $dep"
    done

    for dep in "${MISSING[@]+"${MISSING[@]}"}"; do
        echo -e "  ${RED}✗${NC} $dep (not installed)"
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ ${#MISSING[@]} -eq 0 ]]; then
        echo -e "${GREEN}All $TOTAL dependencies satisfied${NC}"
    else
        echo -e "${RED}${#MISSING[@]}/$TOTAL dependencies missing${NC}"
        echo ""
        echo "Install missing dependencies:"
        for dep in "${MISSING[@]}"; do
            echo "  ./scripts/install-from-catalog.sh $dep"
        done
    fi
fi

# Exit with appropriate code
[[ ${#MISSING[@]} -eq 0 ]] && exit 0 || exit 1
