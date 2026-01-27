#!/usr/bin/env bash
#
# sync-catalog.sh - Sync external skills from upstream repos via manifest.yaml
#
# Usage:
#   ./scripts/sync-catalog.sh sync            # Fetch/update all external skills
#   ./scripts/sync-catalog.sh update <name>   # Update a single external skill
#   ./scripts/sync-catalog.sh list-external   # List external skills
#   ./scripts/sync-catalog.sh list-local      # List local-only skills
#   ./scripts/sync-catalog.sh diff            # Show changes vs upstream
#
# Requires: git, python3 (for YAML parsing)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CATALOG_DIR="$PROJECT_DIR/catalog"
MANIFEST="$CATALOG_DIR/manifest.yaml"
OVERRIDES_DIR="$CATALOG_DIR/overrides"
CACHE_DIR="/tmp/skill-sync-cache"
LOCK_FILE="/tmp/skill-sync.lock"

# ── Helpers ──────────────────────────────────────────────────────

die() { echo -e "${RED}Error:${NC} $*" >&2; exit 1; }

cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local pid
        pid=$(cat "$LOCK_FILE" 2>/dev/null || true)
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            die "Another sync is running (PID $pid). Remove $LOCK_FILE if stale."
        fi
        rm -f "$LOCK_FILE"
    fi
    echo $$ > "$LOCK_FILE"
}

# Parse manifest with Python (portable, no yq dependency)
parse_manifest() {
    python3 - "$MANIFEST" "$@" << 'PYEOF'
import sys, yaml, json

manifest_path = sys.argv[1]
query = sys.argv[2] if len(sys.argv) > 2 else "all"

with open(manifest_path) as f:
    m = yaml.safe_load(f)

sources = m.get("sources", {})
skills = m.get("skills", {})

if query == "sources":
    print(json.dumps(sources))
elif query == "external":
    ext = {k: v for k, v in skills.items() if not v.get("local", False)}
    print(json.dumps(ext))
elif query == "local":
    loc = {k: v for k, v in skills.items() if v.get("local", False)}
    print(json.dumps(loc))
elif query == "skill":
    name = sys.argv[3]
    if name in skills:
        print(json.dumps(skills[name]))
    else:
        sys.exit(1)
elif query == "source":
    name = sys.argv[3]
    if name in sources:
        print(json.dumps(sources[name]))
    else:
        sys.exit(1)
elif query == "all":
    print(json.dumps(m))
PYEOF
}

# Clone or update a source repo (sparse checkout of skills/ dir only)
ensure_source_cache() {
    local source_name="$1"
    local repo ref skills_path
    repo=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['repo'])")
    skills_path=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")

    local cache="$CACHE_DIR/$source_name"

    if [[ -d "$cache/.git" ]]; then
        echo -e "  ${BLUE}[Updating]${NC} $source_name cache"
        git -C "$cache" fetch --depth 1 origin 2>/dev/null
        git -C "$cache" checkout FETCH_HEAD -- "$skills_path" 2>/dev/null || true
    else
        echo -e "  ${BLUE}[Cloning]${NC} $source_name → $cache"
        mkdir -p "$cache"
        git clone --depth 1 --filter=blob:none --sparse "$repo" "$cache" 2>/dev/null
        git -C "$cache" sparse-checkout set "$skills_path" 2>/dev/null
    fi
}

# Sync a single skill from cache to catalog
sync_skill() {
    local skill_name="$1"
    local skill_info source_name ref skills_path source_dir

    skill_info=$(parse_manifest skill "$skill_name")
    source_name=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin)['source'])")
    ref=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ref','main'))")
    skills_path=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")

    source_dir="$CACHE_DIR/$source_name/$skills_path/$skill_name"
    local target_dir="$CATALOG_DIR/$skill_name"

    if [[ ! -d "$source_dir" ]]; then
        echo -e "  ${YELLOW}⚠${NC} $skill_name: not found in $source_name/$skills_path/"
        return 1
    fi

    # Copy from cache
    if [[ -d "$target_dir" ]]; then
        rm -rf "$target_dir"
    fi
    cp -r "$source_dir" "$target_dir"

    # Apply overrides if any
    if [[ -d "$OVERRIDES_DIR/$skill_name" ]]; then
        echo -e "  ${BLUE}[Override]${NC} Applying overrides for $skill_name"
        cp -r "$OVERRIDES_DIR/$skill_name/"* "$target_dir/" 2>/dev/null || true
    fi

    echo -e "  ${GREEN}✓${NC} $skill_name"
    return 0
}

# ── Subcommands ──────────────────────────────────────────────────

cmd_sync() {
    acquire_lock
    echo -e "${BOLD}Syncing external skills from manifest${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Collect unique sources needed
    local sources_needed
    sources_needed=$(parse_manifest external | python3 -c "
import sys, json
ext = json.load(sys.stdin)
print('\n'.join(sorted(set(v['source'] for v in ext.values()))))")

    echo ""
    echo -e "${BOLD}Fetching sources...${NC}"
    mkdir -p "$CACHE_DIR"
    while IFS= read -r src; do
        [[ -z "$src" ]] && continue
        ensure_source_cache "$src"
    done <<< "$sources_needed"

    echo ""
    echo -e "${BOLD}Syncing skills...${NC}"
    local added=0 failed=0 total=0
    local skill_names
    skill_names=$(parse_manifest external | python3 -c "
import sys, json
for k in sorted(json.load(sys.stdin).keys()):
    print(k)")

    while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        total=$((total + 1))
        if sync_skill "$name"; then
            added=$((added + 1))
        else
            failed=$((failed + 1))
        fi
    done <<< "$skill_names"

    # Count local skills
    local local_count
    local_count=$(parse_manifest local | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Synced: ${GREEN}$added${NC} | Failed: ${RED}$failed${NC} | Local (skipped): ${BLUE}$local_count${NC}"

    # Optionally validate
    if [[ -x "$SCRIPT_DIR/validate-all.sh" ]] && [[ $added -gt 0 ]]; then
        echo ""
        echo -e "${BOLD}Running validation on synced skills (profile: spec)...${NC}"
        local valid=0 invalid=0
        while IFS= read -r name; do
            [[ -z "$name" ]] && continue
            [[ ! -d "$CATALOG_DIR/$name" ]] && continue
            if "$SCRIPT_DIR/validate-all.sh" "$CATALOG_DIR/$name" --profile=spec > /dev/null 2>&1; then
                valid=$((valid + 1))
            else
                echo -e "  ${YELLOW}⚠${NC} $name failed validation"
                invalid=$((invalid + 1))
            fi
        done <<< "$skill_names"
        echo -e "Valid: ${GREEN}$valid${NC} | Invalid: ${YELLOW}$invalid${NC}"
    fi
}

cmd_update() {
    local skill_name="$1"
    acquire_lock

    # Check it's external
    local skill_info
    skill_info=$(parse_manifest skill "$skill_name") || die "Skill '$skill_name' not in manifest"
    local is_local
    is_local=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin).get('local', False))")
    [[ "$is_local" == "True" ]] && die "'$skill_name' is a local skill, cannot sync from upstream"

    local source_name
    source_name=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin)['source'])")

    mkdir -p "$CACHE_DIR"
    ensure_source_cache "$source_name"
    sync_skill "$skill_name"
}

cmd_list_external() {
    echo -e "${BOLD}External Skills (synced from upstream)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    parse_manifest external | python3 -c "
import sys, json
ext = json.load(sys.stdin)
for name in sorted(ext):
    s = ext[name]
    status = '✓' if __import__('os').path.isdir('$CATALOG_DIR/' + name) else '✗'
    print(f'  {status} {name:40s} source={s[\"source\"]:12s} tier={s.get(\"tier\",\"?\")} category={s.get(\"category\",\"?\")}')
print(f'\nTotal: {len(ext)} external skill(s)')
"
}

cmd_list_local() {
    echo -e "${BOLD}Local Skills (not synced)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    parse_manifest local | python3 -c "
import sys, json
loc = json.load(sys.stdin)
for name in sorted(loc):
    s = loc[name]
    status = '✓' if __import__('os').path.isdir('$CATALOG_DIR/' + name) else '✗'
    print(f'  {status} {name:40s} tier={s.get(\"tier\",\"?\")} category={s.get(\"category\",\"?\")}')
print(f'\nTotal: {len(loc)} local skill(s)')
"
}

cmd_diff() {
    echo -e "${BOLD}Diff: catalog vs upstream${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local skill_names
    skill_names=$(parse_manifest external | python3 -c "
import sys, json
for k in sorted(json.load(sys.stdin).keys()):
    print(k)")

    while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        local skill_info source_name skills_path
        skill_info=$(parse_manifest skill "$name")
        source_name=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin)['source'])")
        skills_path=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")
        local upstream="$CACHE_DIR/$source_name/$skills_path/$name"
        local local_dir="$CATALOG_DIR/$name"

        if [[ ! -d "$local_dir" ]]; then
            echo -e "  ${YELLOW}NEW${NC}  $name (not yet synced)"
        elif [[ ! -d "$upstream" ]]; then
            echo -e "  ${RED}MISS${NC} $name (upstream not cached; run sync first)"
        else
            local changes
            changes=$(diff -rq "$upstream" "$local_dir" 2>/dev/null | head -5 || true)
            if [[ -z "$changes" ]]; then
                echo -e "  ${GREEN}OK${NC}   $name"
            else
                echo -e "  ${YELLOW}DIFF${NC} $name"
                echo "$changes" | sed 's/^/       /'
            fi
        fi
    done <<< "$skill_names"
}

usage() {
    cat << EOF
${BOLD}Skill Catalog Sync${NC}

Usage:
  $(basename "$0") sync              Fetch/update all external skills
  $(basename "$0") update <name>     Update a single external skill
  $(basename "$0") list-external     List external skills and their status
  $(basename "$0") list-local        List local-only skills
  $(basename "$0") diff              Compare catalog vs upstream cache

Options:
  --help, -h    Show this help
EOF
}

# ── Main ─────────────────────────────────────────────────────────

[[ ! -f "$MANIFEST" ]] && die "Manifest not found: $MANIFEST"

case "${1:-}" in
    sync)           cmd_sync ;;
    update)         [[ -z "${2:-}" ]] && die "Usage: $(basename "$0") update <skill-name>"
                    cmd_update "$2" ;;
    list-external)  cmd_list_external ;;
    list-local)     cmd_list_local ;;
    diff)           cmd_diff ;;
    --help|-h)      usage ;;
    *)              usage; exit 1 ;;
esac
