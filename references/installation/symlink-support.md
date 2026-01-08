# Symlink Support for Development

Enable symlink-based installation for active skill development.

## Symlink Benefits

| Benefit | Description |
|---------|-------------|
| Live updates | Changes reflected immediately |
| Single source | No copy synchronization needed |
| Easy testing | Test changes without reinstall |
| Version control | Keep skill in project repo |

## Symlink Model

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class InstallMode(Enum):
    COPY = "copy"           # Traditional copy installation
    SYMLINK = "symlink"     # Symbolic link to source
    HARDLINK = "hardlink"   # Hard links (files only)

class SymlinkType(Enum):
    DIRECTORY = "directory"   # Link entire skill directory
    FILES = "files"           # Link individual files

@dataclass
class SymlinkConfig:
    source_path: Path
    target_path: Path
    link_type: SymlinkType = SymlinkType.DIRECTORY
    relative: bool = False    # Use relative paths

@dataclass
class SymlinkResult:
    success: bool
    source: Path
    target: Path
    is_relative: bool = False
    error: str | None = None

@dataclass
class SymlinkStatus:
    path: Path
    is_symlink: bool
    target: Path | None = None
    is_valid: bool = True     # Target exists
    is_development: bool = False
```

## Symlink Manager

```python
import os
from pathlib import Path

class SymlinkManager:
    """Manage symlink-based skill installations."""

    USER_SKILLS = Path.home() / ".claude" / "skills"
    DEV_MARKER = ".dev-link"

    def create_symlink(self, config: SymlinkConfig) -> SymlinkResult:
        """Create symlink for skill installation."""
        source = config.source_path.resolve()
        target = config.target_path

        # Validate source
        if not source.exists():
            return SymlinkResult(
                success=False,
                source=source,
                target=target,
                error=f"Source does not exist: {source}"
            )

        if not (source / "SKILL.md").exists():
            return SymlinkResult(
                success=False,
                source=source,
                target=target,
                error="Source is not a valid skill (missing SKILL.md)"
            )

        # Ensure target parent exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing if present
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            else:
                return SymlinkResult(
                    success=False,
                    source=source,
                    target=target,
                    error=f"Target exists and is not a symlink: {target}"
                )

        # Create symlink
        try:
            if config.relative:
                # Calculate relative path
                rel_source = os.path.relpath(source, target.parent)
                target.symlink_to(rel_source)
            else:
                target.symlink_to(source)

            # Create dev marker
            self._create_dev_marker(target, source)

            return SymlinkResult(
                success=True,
                source=source,
                target=target,
                is_relative=config.relative
            )

        except OSError as e:
            return SymlinkResult(
                success=False,
                source=source,
                target=target,
                error=str(e)
            )

    def remove_symlink(self, target: Path) -> bool:
        """Remove a symlink installation."""
        if not target.is_symlink():
            return False

        # Remove dev marker from source
        if target.exists():
            source = target.resolve()
            marker = source / self.DEV_MARKER
            if marker.exists():
                marker.unlink()

        target.unlink()
        return True

    def check_status(self, skill_path: Path) -> SymlinkStatus:
        """Check symlink status of a skill."""
        if not skill_path.exists() and not skill_path.is_symlink():
            return SymlinkStatus(
                path=skill_path,
                is_symlink=False,
                is_valid=False
            )

        if skill_path.is_symlink():
            target = skill_path.resolve()
            is_valid = target.exists()
            is_dev = (target / self.DEV_MARKER).exists() if is_valid else False

            return SymlinkStatus(
                path=skill_path,
                is_symlink=True,
                target=target,
                is_valid=is_valid,
                is_development=is_dev
            )

        return SymlinkStatus(
            path=skill_path,
            is_symlink=False,
            is_valid=True
        )

    def list_dev_links(self) -> list[SymlinkStatus]:
        """List all development symlinks."""
        dev_links = []

        if self.USER_SKILLS.exists():
            for skill_dir in self.USER_SKILLS.iterdir():
                status = self.check_status(skill_dir)
                if status.is_symlink and status.is_development:
                    dev_links.append(status)

        return dev_links

    def convert_to_copy(self, skill_path: Path) -> bool:
        """Convert symlink to regular copy."""
        if not skill_path.is_symlink():
            return False

        source = skill_path.resolve()
        if not source.exists():
            return False

        # Remove symlink
        skill_path.unlink()

        # Copy source to target
        import shutil
        shutil.copytree(source, skill_path)

        # Remove dev marker from copy
        marker = skill_path / self.DEV_MARKER
        if marker.exists():
            marker.unlink()

        return True

    def convert_to_symlink(
        self,
        skill_path: Path,
        source_path: Path
    ) -> SymlinkResult:
        """Convert regular installation to symlink."""
        if skill_path.is_symlink():
            return SymlinkResult(
                success=False,
                source=source_path,
                target=skill_path,
                error="Already a symlink"
            )

        # Backup existing
        import shutil
        backup_path = skill_path.parent / f"{skill_path.name}.backup"
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.move(skill_path, backup_path)

        # Create symlink
        config = SymlinkConfig(
            source_path=source_path,
            target_path=skill_path
        )
        result = self.create_symlink(config)

        if not result.success:
            # Restore backup
            shutil.move(backup_path, skill_path)
        else:
            # Remove backup
            shutil.rmtree(backup_path)

        return result

    def _create_dev_marker(self, target: Path, source: Path) -> None:
        """Create development marker in source."""
        marker = source / self.DEV_MARKER
        marker.write_text(f"Linked from: {target}\n")
```

## Link Script

```bash
#!/bin/bash
# link-skill.sh - Create symlink for skill development
#
# Usage: link-skill.sh <source-path> [options]
#
# Options:
#   --name <name>    Override skill name
#   --relative       Use relative symlink
#   --user           Link to user skills (default)
#   --project        Link to project skills
#   --unlink         Remove existing symlink

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
SOURCE_PATH=""
SKILL_NAME=""
RELATIVE=false
SCOPE="user"
UNLINK=false

USER_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS=".claude/skills"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            SKILL_NAME="$2"
            shift 2
            ;;
        --relative)
            RELATIVE=true
            shift
            ;;
        --user)
            SCOPE="user"
            shift
            ;;
        --project)
            SCOPE="project"
            shift
            ;;
        --unlink)
            UNLINK=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SOURCE_PATH="$1"
            shift
            ;;
    esac
done

# Validate
if [ -z "$SOURCE_PATH" ]; then
    echo "Usage: link-skill.sh <source-path> [options]"
    exit 1
fi

SOURCE_PATH=$(cd "$SOURCE_PATH" && pwd)

if [ ! -f "$SOURCE_PATH/SKILL.md" ]; then
    echo -e "${RED}Error: Not a valid skill (missing SKILL.md)${NC}"
    exit 1
fi

# Get skill name
if [ -z "$SKILL_NAME" ]; then
    SKILL_NAME=$(basename "$SOURCE_PATH")
fi

# Set target path
if [ "$SCOPE" = "user" ]; then
    TARGET_PATH="$USER_SKILLS/$SKILL_NAME"
else
    TARGET_PATH="$PROJECT_SKILLS/$SKILL_NAME"
fi

# Handle unlink
if [ "$UNLINK" = true ]; then
    if [ -L "$TARGET_PATH" ]; then
        rm "$TARGET_PATH"
        echo -e "${GREEN}✓${NC} Unlinked: $TARGET_PATH"
    else
        echo -e "${YELLOW}Not a symlink: $TARGET_PATH${NC}"
    fi
    exit 0
fi

# Check for existing
if [ -e "$TARGET_PATH" ]; then
    if [ -L "$TARGET_PATH" ]; then
        echo -e "${YELLOW}Replacing existing symlink${NC}"
        rm "$TARGET_PATH"
    else
        echo -e "${RED}Error: Target exists and is not a symlink${NC}"
        echo "  $TARGET_PATH"
        echo "Remove it first or use a different name"
        exit 1
    fi
fi

# Create parent directory
mkdir -p "$(dirname "$TARGET_PATH")"

# Create symlink
if [ "$RELATIVE" = true ]; then
    REL_SOURCE=$(python3 -c "import os; print(os.path.relpath('$SOURCE_PATH', '$(dirname "$TARGET_PATH")'))")
    ln -s "$REL_SOURCE" "$TARGET_PATH"
else
    ln -s "$SOURCE_PATH" "$TARGET_PATH"
fi

# Create dev marker
echo "Linked from: $TARGET_PATH" > "$SOURCE_PATH/.dev-link"

# Report
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  SKILL LINKED FOR DEVELOPMENT"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Source: $SOURCE_PATH"
echo "  Target: $TARGET_PATH"
echo "  Type:   $([ "$RELATIVE" = true ] && echo "relative" || echo "absolute") symlink"
echo ""
echo "  Changes to source will be reflected immediately."
echo "  Use '/skill-name' to test your skill."
echo ""
echo "  To unlink:"
echo "    link-skill.sh $SOURCE_PATH --unlink"
echo ""
echo "═══════════════════════════════════════════════════════════"
```

## Symlink Formatter

```python
class SymlinkFormatter:
    """Format symlink information."""

    def format_result(self, result: SymlinkResult) -> str:
        """Format symlink creation result."""
        lines = []

        if result.success:
            lines.append("  ✓ Symlink created")
            lines.append(f"    Source: {result.source}")
            lines.append(f"    Target: {result.target}")
            link_type = "relative" if result.is_relative else "absolute"
            lines.append(f"    Type: {link_type}")
        else:
            lines.append(f"  ✗ Symlink failed: {result.error}")

        return "\n".join(lines)

    def format_status(self, status: SymlinkStatus) -> str:
        """Format symlink status."""
        lines = []

        lines.append(f"  Path: {status.path}")

        if status.is_symlink:
            lines.append("  Type: Symlink")
            lines.append(f"  Target: {status.target}")
            valid = "✓ Valid" if status.is_valid else "✗ Broken"
            lines.append(f"  Status: {valid}")
            if status.is_development:
                lines.append("  Mode: Development")
        else:
            lines.append("  Type: Regular directory")

        return "\n".join(lines)

    def format_dev_links(self, links: list[SymlinkStatus]) -> str:
        """Format list of development links."""
        lines = []

        lines.append("")
        lines.append("  DEVELOPMENT LINKS")
        lines.append("  ─────────────────")

        if not links:
            lines.append("  No development links found")
            return "\n".join(lines)

        for link in links:
            valid = "✓" if link.is_valid else "✗"
            lines.append(f"  {valid} {link.path.name}")
            lines.append(f"      → {link.target}")

        lines.append("")
        lines.append(f"  Total: {len(links)} development link(s)")

        return "\n".join(lines)
```

## Integration

```python
def link_for_development(
    source_path: Path,
    skill_name: str | None = None,
    relative: bool = False
) -> SymlinkResult:
    """Create development symlink for a skill."""
    manager = SymlinkManager()
    formatter = SymlinkFormatter()

    # Determine skill name
    if not skill_name:
        skill_name = source_path.name

    # Create config
    config = SymlinkConfig(
        source_path=source_path,
        target_path=manager.USER_SKILLS / skill_name,
        relative=relative
    )

    # Create symlink
    result = manager.create_symlink(config)

    print(formatter.format_result(result))

    if result.success:
        print("")
        print("  Development mode active!")
        print(f"  Edit files in: {source_path}")
        print(f"  Test with: /{skill_name}")

    return result


def list_development_links() -> None:
    """List all development symlinks."""
    manager = SymlinkManager()
    formatter = SymlinkFormatter()

    links = manager.list_dev_links()
    print(formatter.format_dev_links(links))
```

## Sample Output

```
═══════════════════════════════════════════════════════════════
  SKILL LINKED FOR DEVELOPMENT
═══════════════════════════════════════════════════════════════

  Source: /home/user/projects/my-skill
  Target: /home/user/.claude/skills/my-skill
  Type:   absolute symlink

  Changes to source will be reflected immediately.
  Use '/my-skill' to test your skill.

  To unlink:
    link-skill.sh /home/user/projects/my-skill --unlink

═══════════════════════════════════════════════════════════════
```

```
  DEVELOPMENT LINKS
  ─────────────────
  ✓ api-doc-generator
      → /home/user/projects/api-doc-generator
  ✓ code-reviewer
      → /home/user/projects/code-reviewer
  ✗ old-skill
      → /home/user/projects/deleted-project

  Total: 3 development link(s)
```

## Best Practices

| Practice | Description |
|----------|-------------|
| Use for active dev | Symlink skills you're actively developing |
| Convert for release | Copy before distributing |
| Check broken links | Regularly verify symlinks are valid |
| Relative for portable | Use relative links for shared projects |
