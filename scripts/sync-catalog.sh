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
#   ./scripts/sync-catalog.sh status          # Show last sync state per skill
#   ./scripts/sync-catalog.sh list-categories # List all skill categories
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
SYNC_STATE="$CATALOG_DIR/.sync-state.json"

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
    local repo skills_path
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

# Checkout a specific SHA for a skill (when sha field is present in manifest)
checkout_skill_sha() {
    local source_name="$1"
    local sha="$2"
    local skills_path="$3"
    local skill_name="$4"
    local cache="$CACHE_DIR/$source_name"

    echo -e "  ${BLUE}[SHA pin]${NC} $skill_name → ${sha:0:8}"
    git -C "$cache" fetch --depth 1 origin "$sha" 2>/dev/null || {
        echo -e "  ${YELLOW}⚠${NC} Failed to fetch SHA $sha for $skill_name"
        return 1
    }
    git -C "$cache" checkout "$sha" -- "$skills_path/$skill_name" 2>/dev/null || {
        echo -e "  ${YELLOW}⚠${NC} Failed to checkout $skill_name at SHA $sha"
        return 1
    }
}

# Apply patch.yaml section injections to a SKILL.md
# Only injects sections that don't already exist in the file.
apply_patch_yaml() {
    local skill_md="$1"
    local patch_file="$2"

    [[ -f "$skill_md" ]] || return 1
    [[ -f "$patch_file" ]] || return 0

    python3 - "$skill_md" "$patch_file" << 'PYEOF'
import sys, yaml

skill_md_path = sys.argv[1]
patch_path = sys.argv[2]

with open(skill_md_path) as f:
    content = f.read()

with open(patch_path) as f:
    patch = yaml.safe_load(f)

sections = patch.get("sections", {})
if not sections:
    sys.exit(0)

injected = 0
for heading, body in sections.items():
    # Check if section already exists (## Heading)
    marker = f"## {heading}"
    if marker in content:
        continue
    # Append section at end of file
    content = content.rstrip() + f"\n\n{marker}\n\n{body.strip()}\n"
    injected += 1

if injected > 0:
    with open(skill_md_path, "w") as f:
        f.write(content)
    print(f"    Injected {injected} section(s)")
PYEOF
}

# Record sync state for a skill (resolved SHA + timestamp)
record_sync_state() {
    local skill_name="$1" source_name="$2" resolved_sha="$3"
    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    python3 - "$SYNC_STATE" "$skill_name" "$source_name" "$resolved_sha" "$timestamp" << 'PYEOF'
import sys, json, os

state_path, skill, source, sha, ts = sys.argv[1:6]

state = {}
if os.path.exists(state_path):
    with open(state_path) as f:
        state = json.load(f)

state.setdefault("last_synced", ts)
state["last_synced"] = ts
skills = state.setdefault("skills", {})
skills[skill] = {
    "source": source,
    "sha": sha,
    "synced_at": ts,
}

with open(state_path, "w") as f:
    json.dump(state, f, indent=2, sort_keys=True)
    f.write("\n")
PYEOF
}

# Resolve the current HEAD SHA for a source cache
resolve_cache_sha() {
    local source_name="$1"
    local cache="$CACHE_DIR/$source_name"
    git -C "$cache" rev-parse HEAD 2>/dev/null || echo "unknown"
}

# Sync a single skill from cache to catalog
sync_skill() {
    local skill_name="$1"
    local skill_info source_name ref sha skills_path source_dir

    skill_info=$(parse_manifest skill "$skill_name")
    source_name=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin)['source'])")
    ref=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ref','main'))")
    sha=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))")
    skills_path=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")

    # If SHA is pinned, fetch and checkout that specific commit
    if [[ -n "$sha" ]]; then
        checkout_skill_sha "$source_name" "$sha" "$skills_path" "$skill_name" || return 1
    fi

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

    # Apply file overrides if any (excluding patch.yaml which is handled separately)
    if [[ -d "$OVERRIDES_DIR/$skill_name" ]]; then
        local has_overrides=false
        while IFS= read -r -d '' override_file; do
            has_overrides=true
            local rel_path="${override_file#"$OVERRIDES_DIR/$skill_name/"}"
            mkdir -p "$target_dir/$(dirname "$rel_path")"
            cp "$override_file" "$target_dir/$rel_path"
        done < <(find "$OVERRIDES_DIR/$skill_name" -type f ! -name 'patch.yaml' -print0 2>/dev/null)
        if $has_overrides; then
            echo -e "  ${BLUE}[Override]${NC} Applying file overrides for $skill_name"
        fi
    fi

    # Apply patch.yaml section injections if present
    local patch_file="$OVERRIDES_DIR/$skill_name/patch.yaml"
    if [[ -f "$patch_file" ]]; then
        echo -e "  ${BLUE}[Patch]${NC} Injecting sections from patch.yaml for $skill_name"
        apply_patch_yaml "$target_dir/SKILL.md" "$patch_file"
    fi

    # Record sync state
    local resolved_sha
    if [[ -n "$sha" ]]; then
        resolved_sha="$sha"
    else
        resolved_sha=$(resolve_cache_sha "$source_name")
    fi
    record_sync_state "$skill_name" "$source_name" "$resolved_sha"

    echo -e "  ${GREEN}✓${NC} $skill_name"
    return 0
}

# ── Subcommands ──────────────────────────────────────────────────

cmd_sync() {
    local dry_run=false
    if [[ "${1:-}" == "--dry-run" ]]; then
        dry_run=true
    fi

    acquire_lock

    if $dry_run; then
        echo -e "${BOLD}Dry-run: previewing sync (no files will be modified)${NC}"
    else
        echo -e "${BOLD}Syncing external skills from manifest${NC}"
    fi
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
    if $dry_run; then
        echo -e "${BOLD}Preview of sync results:${NC}"
    else
        echo -e "${BOLD}Syncing skills...${NC}"
    fi
    local added=0 failed=0 unchanged=0 total=0
    local skill_names
    skill_names=$(parse_manifest external | python3 -c "
import sys, json
for k in sorted(json.load(sys.stdin).keys()):
    print(k)")

    while IFS= read -r name; do
        [[ -z "$name" ]] && continue
        total=$((total + 1))

        if $dry_run; then
            # Determine what would happen without modifying files
            local skill_info source_name skills_path source_dir target_dir
            skill_info=$(parse_manifest skill "$name")
            source_name=$(echo "$skill_info" | python3 -c "import sys,json; print(json.load(sys.stdin)['source'])")
            skills_path=$(parse_manifest source "$source_name" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")
            source_dir="$CACHE_DIR/$source_name/$skills_path/$name"
            target_dir="$CATALOG_DIR/$name"

            if [[ ! -d "$source_dir" ]]; then
                echo -e "  ${RED}MISSING${NC}   $name (not found in upstream)"
                failed=$((failed + 1))
            elif [[ ! -d "$target_dir" ]]; then
                echo -e "  ${GREEN}NEW${NC}       $name"
                added=$((added + 1))
            else
                local changes
                changes=$(diff -rq "$source_dir" "$target_dir" 2>/dev/null | head -1 || true)
                if [[ -z "$changes" ]]; then
                    echo -e "  ${BLUE}UNCHANGED${NC} $name"
                    unchanged=$((unchanged + 1))
                else
                    echo -e "  ${YELLOW}UPDATED${NC}   $name"
                    added=$((added + 1))
                fi
            fi
        else
            if sync_skill "$name"; then
                added=$((added + 1))
            else
                failed=$((failed + 1))
            fi
        fi
    done <<< "$skill_names"

    # Count local skills
    local local_count
    local_count=$(parse_manifest local | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if $dry_run; then
        echo -e "Would sync: ${GREEN}$added${NC} | Missing: ${RED}$failed${NC} | Unchanged: ${BLUE}$unchanged${NC} | Local (skipped): ${BLUE}$local_count${NC}"
        echo -e "${YELLOW}No files were modified (dry-run).${NC}"
    else
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

cmd_status() {
    echo -e "${BOLD}Sync State${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ ! -f "$SYNC_STATE" ]]; then
        echo "No sync state recorded. Run 'sync' first."
        return 0
    fi

    python3 - "$SYNC_STATE" << 'PYEOF'
import sys, json

with open(sys.argv[1]) as f:
    state = json.load(f)

last = state.get("last_synced", "?")
print(f"  Last synced: {last}")
print()

skills = state.get("skills", {})
if not skills:
    print("No skills recorded in sync state.")
    sys.exit(0)

for name in sorted(skills):
    s = skills[name]
    sha_short = s.get("sha", "?")[:12]
    synced_at = s.get("synced_at", "?")
    source = s.get("source", "?")
    print(f"  {name:40s} {source:12s} {sha_short}  ({synced_at})")

print(f"\nTotal: {len(skills)} synced skill(s)")
PYEOF
}

cmd_list_categories() {
    echo -e "${BOLD}Skill Categories${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 - "$MANIFEST" << 'PYEOF'
import sys, yaml
from collections import defaultdict

with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)

skills = m.get("skills", {})
by_category = defaultdict(list)
for name, info in skills.items():
    cat = info.get("category", "uncategorized")
    by_category[cat].append(name)

for cat in sorted(by_category):
    names = sorted(by_category[cat])
    print(f"\n  {cat} ({len(names)}):")
    for n in names:
        print(f"    - {n}")

print(f"\n{len(by_category)} categories, {len(skills)} total skills")
PYEOF
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
            # Fall back to sync state if cache is missing
            if [[ -f "$SYNC_STATE" ]]; then
                local state_sha
                state_sha=$(python3 -c "
import json, sys
with open('$SYNC_STATE') as f:
    s = json.load(f)
sk = s.get('skills', {}).get('$name', {})
print(sk.get('sha', ''), sk.get('synced_at', ''))
")
                if [[ -n "$state_sha" ]]; then
                    echo -e "  ${BLUE}SYNC${NC} $name (last: ${state_sha})"
                else
                    echo -e "  ${YELLOW}NEW${NC}  $name (not yet synced, no cache)"
                fi
            else
                echo -e "  ${RED}MISS${NC} $name (no cache, no sync state; run sync first)"
            fi
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
  $(basename "$0") sync --dry-run    Preview sync without modifying catalog
  $(basename "$0") update <name>     Update a single external skill
  $(basename "$0") list-external     List external skills and their status
  $(basename "$0") list-local        List local-only skills
  $(basename "$0") diff              Compare catalog vs upstream cache
  $(basename "$0") status            Show last sync state per skill
  $(basename "$0") list-categories   List all skill categories

Options:
  --help, -h    Show this help
EOF
}

# ── Main ─────────────────────────────────────────────────────────

[[ ! -f "$MANIFEST" ]] && die "Manifest not found: $MANIFEST"

case "${1:-}" in
    sync)           cmd_sync "${2:-}" ;;
    update)         [[ -z "${2:-}" ]] && die "Usage: $(basename "$0") update <skill-name>"
                    cmd_update "$2" ;;
    list-external)  cmd_list_external ;;
    list-local)     cmd_list_local ;;
    diff)           cmd_diff ;;
    status)         cmd_status ;;
    list-categories) cmd_list_categories ;;
    --help|-h)      usage ;;
    *)              usage; exit 1 ;;
esac
