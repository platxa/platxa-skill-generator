#!/usr/bin/env bash
# list-installed.sh - List all installed skills with dependency info
#
# Usage: list-installed.sh [--user|--project|--all] [--json]
#
# Exit codes:
#   0 - Success

set -euo pipefail

if [[ -t 1 ]]; then
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
else
    GREEN='' BLUE='' BOLD='' DIM='' NC=''
fi

SCOPE="all"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --user)    SCOPE="user"; shift ;;
        --project) SCOPE="project"; shift ;;
        --all)     SCOPE="all"; shift ;;
        --json)    JSON_OUTPUT=true; shift ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--user|--project|--all] [--json]"
            exit 0
            ;;
        *) echo "Unknown: $1" >&2; exit 2 ;;
    esac
done

USER_DIR="$HOME/.claude/skills"
PROJECT_DIR=".claude/skills"

list_skills_in_dir() {
    local dir="$1"
    local scope="$2"

    [[ -d "$dir" ]] || return

    for skill_dir in "$dir"/*/; do
        [[ -f "${skill_dir}SKILL.md" ]] || continue

        local name
        name=$(basename "$skill_dir")

        local frontmatter
        frontmatter=$(sed -n '2,/^---$/p' "${skill_dir}SKILL.md" | sed '$d')

        local deps
        deps=$(echo "$frontmatter" | sed -n '/^depends-on:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' | tr '\n' ',' | sed 's/,$//' || echo "")

        local suggests
        suggests=$(echo "$frontmatter" | sed -n '/^suggests:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' | tr '\n' ',' | sed 's/,$//' || echo "")

        if $JSON_OUTPUT; then
            local deps_json="[]"
            if [[ -n "$deps" ]]; then
                deps_json="[$(echo "$deps" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/' )]"
            fi
            local sug_json="[]"
            if [[ -n "$suggests" ]]; then
                sug_json="[$(echo "$suggests" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/' )]"
            fi
            echo "{\"name\":\"$name\",\"scope\":\"$scope\",\"depends_on\":$deps_json,\"suggests\":$sug_json}"
        else
            echo -e "  ${GREEN}$name${NC} ${DIM}($scope)${NC}"
            [[ -n "$deps" ]] && echo -e "    depends-on: $deps"
            [[ -n "$suggests" ]] && echo -e "    suggests:   $suggests"
        fi
    done
}

if $JSON_OUTPUT; then
    echo "["
    first=true
    if [[ "$SCOPE" == "all" || "$SCOPE" == "user" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            $first || echo ","
            first=false
            echo -n "  $line"
        done < <(list_skills_in_dir "$USER_DIR" "user")
    fi
    if [[ "$SCOPE" == "all" || "$SCOPE" == "project" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            $first || echo ","
            first=false
            echo -n "  $line"
        done < <(list_skills_in_dir "$PROJECT_DIR" "project")
    fi
    echo ""
    echo "]"
else
    echo -e "${BOLD}Installed Skills${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    count=0
    if [[ "$SCOPE" == "all" || "$SCOPE" == "user" ]]; then
        if [[ -d "$USER_DIR" ]]; then
            echo -e "\n${BLUE}User skills${NC} ($USER_DIR):"
            while IFS= read -r line; do
                [[ -n "$line" ]] && echo "$line" && count=$((count + 1))
            done < <(list_skills_in_dir "$USER_DIR" "user")
        fi
    fi
    if [[ "$SCOPE" == "all" || "$SCOPE" == "project" ]]; then
        if [[ -d "$PROJECT_DIR" ]]; then
            echo -e "\n${BLUE}Project skills${NC} ($PROJECT_DIR):"
            while IFS= read -r line; do
                [[ -n "$line" ]] && echo "$line" && count=$((count + 1))
            done < <(list_skills_in_dir "$PROJECT_DIR" "project")
        fi
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
