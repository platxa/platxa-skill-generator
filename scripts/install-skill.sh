#!/usr/bin/env bash
# Install a Claude Code skill to user or project location
# Usage: install-skill.sh <skill-directory> [--project|--user]

set -euo pipefail

SKILL_DIR="${1:-.}"
LOCATION="${2:---user}"

# Resolve skill name from SKILL.md
SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ ! -f "$SKILL_MD" ]]; then
    echo "❌ ERROR: SKILL.md not found in $SKILL_DIR"
    exit 1
fi

# Extract name from frontmatter only (between first --- and second ---)
SKILL_NAME=$(sed -n '2,/^---$/p' "$SKILL_MD" | sed '$d' | grep "^name:" | head -1 | sed 's/name: *//' | tr -d '"' | tr -d "'")
if [[ -z "$SKILL_NAME" ]]; then
    echo "❌ ERROR: Could not extract skill name from SKILL.md"
    exit 1
fi

# Determine target directory
case "$LOCATION" in
    --user|-u)
        TARGET_DIR="$HOME/.claude/skills/$SKILL_NAME"
        LOCATION_NAME="user"
        ;;
    --project|-p)
        TARGET_DIR=".claude/skills/$SKILL_NAME"
        LOCATION_NAME="project"
        ;;
    *)
        echo "Usage: install-skill.sh <skill-directory> [--project|--user]"
        echo "  --user, -u    Install to ~/.claude/skills/ (default)"
        echo "  --project, -p Install to .claude/skills/"
        exit 1
        ;;
esac

echo "═══════════════════════════════════════════════════"
echo "Installing skill: $SKILL_NAME"
echo "Location: $LOCATION_NAME ($TARGET_DIR)"
echo "═══════════════════════════════════════════════════"

# Validate first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$SCRIPT_DIR/validate-skill.sh" ]]; then
    echo -e "\n--- Validating skill ---"
    if ! "$SCRIPT_DIR/validate-skill.sh" "$SKILL_DIR"; then
        echo -e "\n❌ Skill validation failed. Fix errors before installing."
        exit 1
    fi
fi

# Check if already installed
if [[ -d "$TARGET_DIR" ]]; then
    echo -e "\n⚠️  Skill already installed at $TARGET_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy files
echo -e "\n--- Copying files ---"
cp "$SKILL_MD" "$TARGET_DIR/"
echo "✓ SKILL.md"

# Copy directories if they exist
for dir in references scripts assets; do
    if [[ -d "$SKILL_DIR/$dir" ]]; then
        cp -r "$SKILL_DIR/$dir" "$TARGET_DIR/"
        echo "✓ $dir/"
    fi
done

# Make scripts executable
if [[ -d "$TARGET_DIR/scripts" ]]; then
    chmod +x "$TARGET_DIR/scripts"/*.sh 2>/dev/null || true
fi

echo -e "\n═══════════════════════════════════════════════════"
echo "✓ Skill installed successfully!"
echo "  Location: $TARGET_DIR"
echo ""
echo "To use: /$(echo "$SKILL_NAME" | tr '-' ' ' | awk '{print $1}')"
echo "═══════════════════════════════════════════════════"
