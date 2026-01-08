# Check Links Script

Shell script to verify all file references and links in a skill.

## Script: check-links.sh

```bash
#!/bin/bash
# check-links.sh - Verify all links and references in a skill
#
# Usage: check-links.sh <skill-path> [options]
#
# Options:
#   --include-external  Also check external URLs
#   --quiet            Only show broken links
#   --json             Output as JSON

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_LINKS=0
BROKEN_LINKS=0
VALID_LINKS=0
EXTERNAL_LINKS=0
SKIPPED_LINKS=0

# Options
CHECK_EXTERNAL=false
QUIET_MODE=false
JSON_MODE=false

# Parse arguments
SKILL_PATH=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --include-external)
            CHECK_EXTERNAL=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
        --json)
            JSON_MODE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SKILL_PATH="$1"
            shift
            ;;
    esac
done

# Validate input
if [ -z "$SKILL_PATH" ]; then
    echo "Usage: check-links.sh <skill-path> [options]"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Directory not found: $SKILL_PATH"
    exit 1
fi

# Normalize path
SKILL_PATH=$(cd "$SKILL_PATH" && pwd)

# Output functions
log_valid() {
    ((VALID_LINKS++))
    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo -e "  ${GREEN}✓${NC} $1"
    fi
}

log_broken() {
    ((BROKEN_LINKS++))
    if [ "$JSON_MODE" = false ]; then
        echo -e "  ${RED}✗${NC} $1"
        echo -e "    ${YELLOW}→${NC} $2"
    fi
}

log_external() {
    ((EXTERNAL_LINKS++))
    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo -e "  ${BLUE}○${NC} $1 (external)"
    fi
}

log_skipped() {
    ((SKIPPED_LINKS++))
    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo -e "  ${YELLOW}○${NC} $1 (skipped)"
    fi
}

# Header
if [ "$JSON_MODE" = false ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  CHECKING LINKS: $(basename "$SKILL_PATH")"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
fi

# Collect all broken links for JSON output
declare -a BROKEN_ARRAY

# Check links in a file
check_file_links() {
    local file="$1"
    local rel_file="${file#$SKILL_PATH/}"
    local file_dir=$(dirname "$file")

    if [ "$JSON_MODE" = false ] && [ "$QUIET_MODE" = false ]; then
        echo ""
        echo "Checking: $rel_file"
        echo "─────────────────────────────────────────────"
    fi

    # Extract markdown links [text](url)
    while IFS= read -r line; do
        # Get link target
        local target=$(echo "$line" | sed -n 's/.*](\([^)]*\)).*/\1/p')

        [ -z "$target" ] && continue
        ((TOTAL_LINKS++))

        # Remove anchor from target for file check
        local target_file="${target%%#*}"
        local anchor="${target#*#}"
        [ "$anchor" = "$target" ] && anchor=""

        # Check link type
        if [[ "$target" =~ ^https?:// ]]; then
            # External URL
            if [ "$CHECK_EXTERNAL" = true ]; then
                if curl -s --head --fail "$target" > /dev/null 2>&1; then
                    log_valid "$target"
                else
                    log_broken "$target" "URL not reachable"
                    BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$target\",\"error\":\"URL not reachable\"}")
                fi
            else
                log_external "$target"
            fi
        elif [[ "$target" =~ ^mailto: ]]; then
            # Email link - skip
            log_skipped "$target"
        elif [[ "$target" =~ ^# ]]; then
            # Anchor-only link - check in same file
            local anchor_name="${target#\#}"
            if grep -q "^#.*$anchor_name" "$file" 2>/dev/null; then
                log_valid "$target"
            else
                log_broken "$target" "Anchor not found in file"
                BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$target\",\"error\":\"Anchor not found\"}")
            fi
        else
            # Relative file link
            local full_path

            if [[ "$target_file" =~ ^/ ]]; then
                # Absolute path from skill root
                full_path="$SKILL_PATH${target_file}"
            else
                # Relative to current file
                full_path="$file_dir/$target_file"
            fi

            # Normalize path
            full_path=$(cd "$(dirname "$full_path")" 2>/dev/null && pwd)/$(basename "$full_path") 2>/dev/null || full_path=""

            if [ -z "$full_path" ] || [ ! -e "$full_path" ]; then
                log_broken "$target" "File not found"
                BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$target\",\"error\":\"File not found\"}")
            elif [ -n "$anchor" ]; then
                # Check anchor in target file
                if grep -q "^#.*$anchor" "$full_path" 2>/dev/null; then
                    log_valid "$target"
                else
                    log_broken "$target" "Anchor not found in target"
                    BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$target\",\"error\":\"Anchor not found\"}")
                fi
            else
                log_valid "$target"
            fi
        fi
    done < <(grep -o '\[.*\](.*)'  "$file" 2>/dev/null || true)

    # Also check reference-style links [text][ref] and [ref]: url
    while IFS= read -r line; do
        local ref_name=$(echo "$line" | sed -n 's/^\[\([^]]*\)\]:.*/\1/p')
        local ref_url=$(echo "$line" | sed -n 's/^\[[^]]*\]:\s*\(.*\)/\1/p')

        [ -z "$ref_url" ] && continue
        ((TOTAL_LINKS++))

        if [[ "$ref_url" =~ ^https?:// ]]; then
            if [ "$CHECK_EXTERNAL" = true ]; then
                if curl -s --head --fail "$ref_url" > /dev/null 2>&1; then
                    log_valid "[$ref_name]: $ref_url"
                else
                    log_broken "[$ref_name]: $ref_url" "URL not reachable"
                    BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$ref_url\",\"error\":\"URL not reachable\"}")
                fi
            else
                log_external "[$ref_name]: $ref_url"
            fi
        elif [ ! -e "$file_dir/$ref_url" ]; then
            log_broken "[$ref_name]: $ref_url" "File not found"
            BROKEN_ARRAY+=("{\"file\":\"$rel_file\",\"link\":\"$ref_url\",\"error\":\"File not found\"}")
        else
            log_valid "[$ref_name]: $ref_url"
        fi
    done < <(grep '^\[.*\]:' "$file" 2>/dev/null || true)
}

# Find and check all markdown files
while IFS= read -r -d '' file; do
    check_file_links "$file"
done < <(find "$SKILL_PATH" -name "*.md" -type f -print0)

# Summary
echo ""
echo "───────────────────────────────────────────────────────────"

if [ "$JSON_MODE" = true ]; then
    echo "{"
    echo "  \"total\": $TOTAL_LINKS,"
    echo "  \"valid\": $VALID_LINKS,"
    echo "  \"broken\": $BROKEN_LINKS,"
    echo "  \"external\": $EXTERNAL_LINKS,"
    echo "  \"skipped\": $SKIPPED_LINKS,"
    echo "  \"broken_links\": ["
    local first=true
    for item in "${BROKEN_ARRAY[@]}"; do
        [ "$first" = true ] && first=false || echo ","
        echo -n "    $item"
    done
    echo ""
    echo "  ]"
    echo "}"
else
    echo ""
    echo "  Summary:"
    echo "    Total links:    $TOTAL_LINKS"
    echo -e "    Valid:          ${GREEN}$VALID_LINKS${NC}"
    echo -e "    Broken:         ${RED}$BROKEN_LINKS${NC}"
    echo -e "    External:       ${BLUE}$EXTERNAL_LINKS${NC}"
    echo -e "    Skipped:        ${YELLOW}$SKIPPED_LINKS${NC}"
    echo ""

    if [ $BROKEN_LINKS -eq 0 ]; then
        echo -e "  ${GREEN}✓ All links valid${NC}"
    else
        echo -e "  ${RED}✗ $BROKEN_LINKS broken link(s) found${NC}"
    fi
fi

echo "═══════════════════════════════════════════════════════════"

# Exit code
[ $BROKEN_LINKS -eq 0 ] && exit 0 || exit 1
```

## Usage

```bash
# Check internal links only
./check-links.sh ~/.claude/skills/my-skill/

# Include external URL checks
./check-links.sh ~/.claude/skills/my-skill/ --include-external

# Quiet mode (only broken links)
./check-links.sh ~/.claude/skills/my-skill/ --quiet

# JSON output
./check-links.sh ~/.claude/skills/my-skill/ --json
```

## Link Types Checked

| Type | Example | Checked By Default |
|------|---------|-------------------|
| Relative file | `[link](file.md)` | Yes |
| Relative with anchor | `[link](file.md#section)` | Yes |
| Anchor only | `[link](#section)` | Yes |
| External URL | `[link](https://...)` | No (use --include-external) |
| Reference style | `[link][ref]` | Yes |
| Email | `[email](mailto:...)` | Skipped |

## Sample Output

```
═══════════════════════════════════════════════════════════
  CHECKING LINKS: api-doc-generator
═══════════════════════════════════════════════════════════

Checking: SKILL.md
─────────────────────────────────────────────────────────
  ✓ references/overview.md
  ✓ references/api.md#endpoints
  ✗ references/missing.md
    → File not found
  ○ https://example.com (external)

Checking: references/overview.md
─────────────────────────────────────────────────────────
  ✓ ../SKILL.md
  ✓ #configuration
  ✗ #nonexistent-section
    → Anchor not found in file

───────────────────────────────────────────────────────────

  Summary:
    Total links:    5
    Valid:          3
    Broken:         2
    External:       1
    Skipped:        0

  ✗ 2 broken link(s) found
═══════════════════════════════════════════════════════════
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All links valid |
| 1 | Broken links found |
