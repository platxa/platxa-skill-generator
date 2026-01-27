#!/usr/bin/env bash
#
# install-from-catalog.sh - Install skills from the catalog
#
# Usage:
#   ./scripts/install-from-catalog.sh <skill-name> [--user|--project]
#   ./scripts/install-from-catalog.sh --list
#   ./scripts/install-from-catalog.sh --all [--user|--project]
#
# Options:
#   --user      Install to ~/.claude/skills/ (default)
#   --project   Install to .claude/skills/
#   --list      List all available skills
#   --all       Install all skills from catalog
#   --force     Overwrite existing skills without prompting
#   --validate  Run validation before installing (default: on)
#   --no-validate  Skip validation
#   --tier N    Only install skills with tier <= N (from manifest.yaml)
#   --category X Only install skills matching category X (from manifest.yaml)
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Determine script and catalog directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CATALOG_DIR="$PROJECT_DIR/catalog"

# Default options
INSTALL_TARGET="user"
VALIDATE=true
FORCE=false
FILTER_TIER=""
FILTER_CATEGORY=""

# Parse arguments
SKILL_NAME=""
INSTALL_ALL=false
LIST_SKILLS=false

usage() {
    cat << EOF
${BOLD}Claude Code Skills Catalog Installer${NC}

Usage:
  $(basename "$0") <skill-name> [options]
  $(basename "$0") --list
  $(basename "$0") --all [options]

Options:
  --user        Install to ~/.claude/skills/ (default)
  --project     Install to .claude/skills/
  --list        List all available skills
  --all         Install all skills from catalog
  --force       Overwrite existing skills without prompting
  --no-validate Skip validation before install
  --tier N      Only install skills with tier <= N (requires manifest.yaml)
  --category X  Only install skills matching category X (requires manifest.yaml)

Examples:
  $(basename "$0") code-documenter              # Install to user skills
  $(basename "$0") code-documenter --project    # Install to project skills
  $(basename "$0") --list                        # List available skills
  $(basename "$0") --all                         # Install all skills
  $(basename "$0") --all --tier 1               # Install tier 0-1 skills only
  $(basename "$0") --all --category frontend    # Install frontend skills only
EOF
}

list_skills() {
    echo -e "${BOLD}Available Skills in Catalog${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    local count=0
    for skill_dir in "$CATALOG_DIR"/*/; do
        if [[ -f "${skill_dir}SKILL.md" ]]; then
            skill_name=$(basename "$skill_dir")

            # Extract description from frontmatter
            description=$(grep "^description:" "${skill_dir}SKILL.md" 2>/dev/null | sed 's/^description:[[:space:]]*//' || echo "No description")

            # Truncate description if too long
            if [[ ${#description} -gt 60 ]]; then
                description="${description:0:57}..."
            fi

            echo -e "  ${GREEN}${skill_name}${NC}"
            echo -e "    ${description}"
            echo ""
            count=$((count + 1))
        fi
    done

    if [[ $count -eq 0 ]]; then
        echo -e "  ${YELLOW}No skills found in catalog${NC}"
        echo ""
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Total: ${BOLD}$count${NC} skill(s)"
    echo ""
    echo "Install with: $(basename "$0") <skill-name>"
}

validate_skill() {
    local skill_dir="$1"
    local skill_name
    skill_name=$(basename "$skill_dir")

    echo -e "${BLUE}[Validating]${NC} $skill_name"

    # Check SKILL.md exists
    if [[ ! -f "${skill_dir}/SKILL.md" ]]; then
        echo -e "  ${RED}✗${NC} SKILL.md not found"
        return 1
    fi

    # Check frontmatter
    if ! head -1 "${skill_dir}/SKILL.md" | grep -q "^---"; then
        echo -e "  ${RED}✗${NC} Invalid frontmatter"
        return 1
    fi

    # Run full validation if available
    if [[ -x "$SCRIPT_DIR/validate-all.sh" ]]; then
        if "$SCRIPT_DIR/validate-all.sh" "$skill_dir" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} All validations passed"
            return 0
        else
            echo -e "  ${YELLOW}⚠${NC} Some validations failed (see validate-all.sh for details)"
            return 0  # Continue anyway, just warn
        fi
    else
        echo -e "  ${GREEN}✓${NC} Basic checks passed"
        return 0
    fi
}

install_skill() {
    local skill_name="$1"
    local skill_dir="$CATALOG_DIR/$skill_name"

    # Check skill exists
    if [[ ! -d "$skill_dir" ]]; then
        echo -e "${RED}Error:${NC} Skill '$skill_name' not found in catalog"
        echo ""
        echo "Available skills:"
        for s in "$CATALOG_DIR"/*/; do
            [[ -f "${s}SKILL.md" ]] && echo "  - $(basename "$s")"
        done
        return 1
    fi

    # Determine target directory
    local target_dir
    if [[ "$INSTALL_TARGET" == "project" ]]; then
        target_dir=".claude/skills/$skill_name"
    else
        target_dir="$HOME/.claude/skills/$skill_name"
    fi

    # Check if already exists
    if [[ -d "$target_dir" ]] && [[ "$FORCE" != true ]]; then
        echo -e "${YELLOW}Warning:${NC} Skill '$skill_name' already exists at $target_dir"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipped."
            return 0
        fi
    fi

    # Validate if enabled
    if [[ "$VALIDATE" == true ]]; then
        if ! validate_skill "$skill_dir"; then
            echo -e "${RED}Error:${NC} Validation failed. Use --no-validate to skip."
            return 1
        fi
    fi

    # Create target directory
    mkdir -p "$(dirname "$target_dir")"

    # Install (copy)
    echo -e "${BLUE}[Installing]${NC} $skill_name → $target_dir"

    if [[ -d "$target_dir" ]]; then
        rm -rf "$target_dir"
    fi

    cp -r "$skill_dir" "$target_dir"

    # Make scripts executable
    if [[ -d "$target_dir/scripts" ]]; then
        chmod +x "$target_dir/scripts/"*.sh 2>/dev/null || true
    fi

    echo -e "${GREEN}✓${NC} Installed '$skill_name' successfully"
    echo ""
}

# Check if a skill passes tier/category filters using manifest.yaml
skill_passes_filter() {
    local skill_name="$1"
    local manifest="$CATALOG_DIR/manifest.yaml"

    # No filters set → always pass
    if [[ -z "$FILTER_TIER" ]] && [[ -z "$FILTER_CATEGORY" ]]; then
        return 0
    fi

    # No manifest → can't filter, pass by default
    if [[ ! -f "$manifest" ]]; then
        echo -e "  ${YELLOW}⚠${NC} No manifest.yaml found; ignoring --tier/--category filters"
        return 0
    fi

    python3 - "$manifest" "$skill_name" "$FILTER_TIER" "$FILTER_CATEGORY" << 'PYEOF'
import sys, yaml
manifest_path, skill_name, tier_filter, cat_filter = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(manifest_path) as f:
    m = yaml.safe_load(f)
skill = m.get("skills", {}).get(skill_name)
if skill is None:
    sys.exit(0)  # Not in manifest, allow install
if tier_filter and skill.get("tier", 99) > int(tier_filter):
    sys.exit(1)
if cat_filter and skill.get("category", "") != cat_filter:
    sys.exit(1)
sys.exit(0)
PYEOF
}

install_all() {
    local count=0
    local failed=0

    echo -e "${BOLD}Installing all skills from catalog${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    for skill_dir in "$CATALOG_DIR"/*/; do
        if [[ -f "${skill_dir}SKILL.md" ]]; then
            skill_name=$(basename "$skill_dir")
            if ! skill_passes_filter "$skill_name"; then
                continue
            fi
            if install_skill "$skill_name"; then
                count=$((count + 1))
            else
                failed=$((failed + 1))
            fi
        fi
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "Installed: ${GREEN}$count${NC} | Failed: ${RED}$failed${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)
            LIST_SKILLS=true
            shift
            ;;
        --all)
            INSTALL_ALL=true
            shift
            ;;
        --user)
            INSTALL_TARGET="user"
            shift
            ;;
        --project)
            INSTALL_TARGET="project"
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        --no-validate)
            VALIDATE=false
            shift
            ;;
        --tier)
            FILTER_TIER="$2"
            shift 2
            ;;
        --category)
            FILTER_CATEGORY="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Error:${NC} Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            SKILL_NAME="$1"
            shift
            ;;
    esac
done

# Execute requested action
if [[ "$LIST_SKILLS" == true ]]; then
    list_skills
elif [[ "$INSTALL_ALL" == true ]]; then
    install_all
elif [[ -n "$SKILL_NAME" ]]; then
    install_skill "$SKILL_NAME"
else
    usage
fi
