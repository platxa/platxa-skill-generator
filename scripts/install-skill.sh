#!/usr/bin/env bash
# Install a Claude Code skill to user or project location
# Usage: install-skill.sh <skill-directory> [--project|--user] [--force] [--dry-run]
#
# Copies only skill-relevant files (SKILL.md, references/, scripts/, assets/)
# and excludes session state, build artifacts, and other junk.

set -euo pipefail

SKILL_DIR="${1:-.}"
LOCATION=""
FORCE=false
DRY_RUN=false

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --user|-u)    LOCATION="user" ;;
        --project|-p) LOCATION="project" ;;
        --force|-f)   FORCE=true ;;
        --dry-run|-n) DRY_RUN=true ;;
        *)
            echo "Usage: install-skill.sh <skill-directory> [--project|--user] [--force] [--dry-run]"
            echo "  --user, -u      Install to ~/.claude/skills/ (default)"
            echo "  --project, -p   Install to .claude/skills/"
            echo "  --force, -f     Overwrite without prompting"
            echo "  --dry-run, -n   Preview what would be installed without copying"
            exit 1
            ;;
    esac
    shift
done
LOCATION="${LOCATION:-user}"

# Resolve absolute path for skill directory
if [[ ! -d "$SKILL_DIR" ]]; then
    echo "ERROR: Directory not found: $SKILL_DIR"
    echo "  Provide the path to a skill directory containing SKILL.md"
    exit 1
fi
SKILL_DIR="$(cd "$SKILL_DIR" && pwd)"

# Resolve skill name from SKILL.md
SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
    echo "ERROR: SKILL.md not found in $SKILL_DIR"
    exit 1
fi

# Extract name from YAML frontmatter (handles indentation and quoting)
SKILL_NAME=$(sed -n '/^---$/,/^---$/p' "$SKILL_MD" | grep -E '^\s*name\s*:' | head -1 | sed 's/^[[:space:]]*name[[:space:]]*:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '[:space:]')
if [[ -z "$SKILL_NAME" ]]; then
    echo "ERROR: Could not extract skill name from SKILL.md frontmatter"
    echo "  Ensure SKILL.md has YAML frontmatter with a 'name:' field between --- delimiters"
    exit 1
fi

# Determine target directory
case "$LOCATION" in
    user)
        TARGET_DIR="$HOME/.claude/skills/$SKILL_NAME"
        ;;
    project)
        TARGET_DIR=".claude/skills/$SKILL_NAME"
        ;;
esac

echo "=== Installing skill: $SKILL_NAME ==="
echo "  Source:   $SKILL_DIR"
echo "  Target:   $TARGET_DIR"
echo "  Location: $LOCATION"
if [[ "$DRY_RUN" == true ]]; then
    echo "  Mode:     DRY RUN (no changes will be made)"
fi

# Validate first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$SCRIPT_DIR/validate-skill.sh" ]]; then
    echo ""
    echo "--- Validating skill ---"
    if ! "$SCRIPT_DIR/validate-skill.sh" "$SKILL_DIR"; then
        echo ""
        echo "ERROR: Skill validation failed. Fix errors before installing."
        exit 1
    fi
fi

# Check dependencies (non-blocking warning)
if [[ -x "$SCRIPT_DIR/check-dependencies.sh" ]]; then
    echo ""
    echo "--- Checking dependencies ---"
    if ! "$SCRIPT_DIR/check-dependencies.sh" "$SKILL_DIR" 2>/dev/null; then
        echo ""
        echo "WARNING: Some dependencies are not installed."
        echo "The skill may not work correctly until dependencies are satisfied."
        echo ""
    fi
fi

# Show quality score (advisory)
if [[ -f "$SCRIPT_DIR/score-skill.py" ]] && command -v python3 &>/dev/null; then
    SCORE_JSON=$(python3 "$SCRIPT_DIR/score-skill.py" "$SKILL_DIR" --json 2>/dev/null || echo "")
    if [[ -n "$SCORE_JSON" ]]; then
        Q_SCORE=$(echo "$SCORE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['overall_score'])" 2>/dev/null || echo "")
        Q_REC=$(echo "$SCORE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['recommendation'])" 2>/dev/null || echo "")
        if [[ -n "$Q_SCORE" ]]; then
            echo ""
            echo "--- Quality score ---"
            echo "  Score: $Q_SCORE/10 ($Q_REC)"
        fi
    fi
fi

# Dry run: show what would be installed and exit
if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo "--- Files that would be installed ---"
    echo "  SKILL.md"
    [[ -f "$SKILL_DIR/.skillconfig" ]] && echo "  .skillconfig"
    for dir in references scripts assets; do
        if [[ -d "$SKILL_DIR/$dir" ]]; then
            file_count=$(find "$SKILL_DIR/$dir" -type f | wc -l)
            echo "  $dir/ ($file_count files)"
        fi
    done
    echo ""
    echo "=== Dry run complete. No files were copied. ==="
    echo "  Run without --dry-run to install."
    exit 0
fi

# Check if already installed
if [[ -d "$TARGET_DIR" ]]; then
    if [[ "$FORCE" == true ]]; then
        rm -rf "$TARGET_DIR"
    elif [[ -t 0 ]]; then
        # Interactive terminal: prompt user
        echo ""
        echo "Skill already installed at $TARGET_DIR"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
        rm -rf "$TARGET_DIR"
    else
        # Non-interactive (CI/pipe): fail with clear message
        echo ""
        echo "ERROR: Skill already installed at $TARGET_DIR"
        echo "  Use --force to overwrite in non-interactive mode."
        exit 1
    fi
fi

# Copy function: use rsync if available, fall back to cp
copy_dir() {
    local src="$1" dst="$2"

    if command -v rsync &>/dev/null; then
        rsync -a \
            --exclude=".claude/" \
            --exclude="__pycache__/" \
            --exclude="*.pyc" \
            --exclude="*.pyo" \
            --exclude=".gitkeep" \
            --exclude=".DS_Store" \
            --exclude="Thumbs.db" \
            --exclude=".git/" \
            --exclude="node_modules/" \
            "$src/" "$dst/"
    else
        # Fallback: cp -r then clean up excluded patterns
        cp -r "$src/" "$dst/"
        # Remove excluded files/dirs from the copy
        find "$dst" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$dst" \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" -o -name "Thumbs.db" -o -name ".gitkeep" \) -delete 2>/dev/null || true
        find "$dst" -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$dst" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$dst" -name ".claude" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
}

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy SKILL.md and .skillconfig
echo ""
echo "--- Copying files ---"
cp "$SKILL_MD" "$TARGET_DIR/"
echo "  SKILL.md"

if [[ -f "$SKILL_DIR/.skillconfig" ]]; then
    cp "$SKILL_DIR/.skillconfig" "$TARGET_DIR/"
    echo "  .skillconfig"
fi

# Copy directories
for dir in references scripts assets; do
    if [[ -d "$SKILL_DIR/$dir" ]]; then
        mkdir -p "$TARGET_DIR/$dir"
        copy_dir "$SKILL_DIR/$dir" "$TARGET_DIR/$dir"
        file_count=$(find "$TARGET_DIR/$dir" -type f | wc -l)
        echo "  $dir/ ($file_count files)"
    fi
done

# Make scripts executable (both .sh and .py)
if [[ -d "$TARGET_DIR/scripts" ]]; then
    chmod +x "$TARGET_DIR/scripts"/*.sh 2>/dev/null || true
    chmod +x "$TARGET_DIR/scripts"/*.py 2>/dev/null || true
fi

# Post-install summary
total_files=$(find "$TARGET_DIR" -type f | wc -l)
total_size=$(du -sh "$TARGET_DIR" | cut -f1)

echo ""
echo "--- Verification ---"

# Check for files that should not be present
junk_count=0
while IFS= read -r -d '' junk_file; do
    echo "  WARNING: Excluded file leaked: $junk_file"
    junk_count=$((junk_count + 1))
done < <(find "$TARGET_DIR" \( -name ".claude" -o -name "__pycache__" -o -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" -o -name ".gitkeep" -o -name "Thumbs.db" \) -print0 2>/dev/null)

if [[ "$junk_count" -eq 0 ]]; then
    echo "  Clean: No excluded files detected"
fi

# Verify SKILL.md is present and has frontmatter
if [[ -f "$TARGET_DIR/SKILL.md" ]]; then
    first_line=$(head -1 "$TARGET_DIR/SKILL.md")
    if [[ "$first_line" == "---" ]]; then
        echo "  SKILL.md: Valid frontmatter"
    else
        echo "  WARNING: SKILL.md missing frontmatter"
    fi
else
    echo "  ERROR: SKILL.md not found in target"
    exit 1
fi

# Show suggested companion skills
FRONTMATTER=$(sed -n '2,/^---$/p' "$SKILL_MD" | sed '$d')
SUGGESTS=$(echo "$FRONTMATTER" | sed -n '/^suggests:/,/^[a-z][a-z0-9_-]*:/p' | grep -E '^\s*-' | sed 's/^\s*-\s*//' || echo "")
if [[ -n "$SUGGESTS" ]]; then
    echo ""
    echo "--- You might also want ---"
    while IFS= read -r sug; do
        [[ -z "$sug" ]] && continue
        echo "  - $sug"
    done <<< "$SUGGESTS"
fi

echo ""
echo "=== Installed: $SKILL_NAME ==="
echo "  Files: $total_files | Size: $total_size"
echo "  Target: $TARGET_DIR"
