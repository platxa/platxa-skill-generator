# Skill Uninstall Helper

Safely remove skill installations with cleanup and verification.

## Uninstall Goals

| Goal | Description |
|------|-------------|
| Clean removal | Remove all skill files completely |
| Safety checks | Verify before destructive operations |
| Backup option | Optionally preserve before removal |
| Multi-location | Handle user and project installations |

## Uninstall Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class UninstallScope(Enum):
    USER = "user"           # ~/.claude/skills/
    PROJECT = "project"     # ./.claude/skills/
    ALL = "all"             # Both locations

class UninstallAction(Enum):
    REMOVE = "remove"                 # Delete immediately
    BACKUP_REMOVE = "backup_remove"   # Backup then delete
    ARCHIVE = "archive"               # Move to archive folder

@dataclass
class SkillLocation:
    path: Path
    scope: UninstallScope
    version: str | None = None
    file_count: int = 0
    total_size: int = 0

@dataclass
class UninstallPlan:
    skill_name: str
    locations: list[SkillLocation]
    action: UninstallAction
    backup_path: Path | None = None
    requires_confirmation: bool = True

@dataclass
class UninstallResult:
    skill_name: str
    success: bool
    locations_removed: list[Path] = field(default_factory=list)
    backup_created: Path | None = None
    files_removed: int = 0
    bytes_freed: int = 0
    error: str | None = None
```

## Skill Locator

```python
import json
import re
from pathlib import Path

class SkillLocator:
    """Locate skill installations."""

    USER_SKILLS = Path.home() / ".claude" / "skills"
    PROJECT_SKILLS = Path(".claude/skills")

    def find_skill(
        self,
        skill_name: str,
        scope: UninstallScope = UninstallScope.ALL
    ) -> list[SkillLocation]:
        """Find all installations of a skill."""
        locations = []

        if scope in (UninstallScope.USER, UninstallScope.ALL):
            user_path = self.USER_SKILLS / skill_name
            if user_path.exists():
                locations.append(self._analyze_location(
                    user_path, UninstallScope.USER
                ))

        if scope in (UninstallScope.PROJECT, UninstallScope.ALL):
            project_path = self.PROJECT_SKILLS / skill_name
            if project_path.exists():
                locations.append(self._analyze_location(
                    project_path, UninstallScope.PROJECT
                ))

        return locations

    def list_all_skills(
        self,
        scope: UninstallScope = UninstallScope.ALL
    ) -> dict[str, list[SkillLocation]]:
        """List all installed skills."""
        skills = {}

        if scope in (UninstallScope.USER, UninstallScope.ALL):
            if self.USER_SKILLS.exists():
                for skill_dir in self.USER_SKILLS.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        name = skill_dir.name
                        if name not in skills:
                            skills[name] = []
                        skills[name].append(self._analyze_location(
                            skill_dir, UninstallScope.USER
                        ))

        if scope in (UninstallScope.PROJECT, UninstallScope.ALL):
            if self.PROJECT_SKILLS.exists():
                for skill_dir in self.PROJECT_SKILLS.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        name = skill_dir.name
                        if name not in skills:
                            skills[name] = []
                        skills[name].append(self._analyze_location(
                            skill_dir, UninstallScope.PROJECT
                        ))

        return skills

    def _analyze_location(
        self,
        path: Path,
        scope: UninstallScope
    ) -> SkillLocation:
        """Analyze a skill installation."""
        file_count = 0
        total_size = 0

        for file_path in path.rglob("*"):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size

        # Get version
        version = self._get_version(path)

        return SkillLocation(
            path=path,
            scope=scope,
            version=version,
            file_count=file_count,
            total_size=total_size
        )

    def _get_version(self, skill_path: Path) -> str | None:
        """Extract version from skill."""
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            match = re.search(r'^version:\s*["\']?([^"\'\n]+)', content, re.M)
            if match:
                return match.group(1).strip()

        meta_path = skill_path / ".skill-meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            return meta.get("version")

        return None
```

## Uninstaller

```python
import shutil
from datetime import datetime
from pathlib import Path

class SkillUninstaller:
    """Safely uninstall skills."""

    ARCHIVE_DIR = Path.home() / ".claude" / "skill-archive"
    BACKUP_DIR = Path.home() / ".claude" / "skill-backups"

    def __init__(self):
        self.locator = SkillLocator()

    def create_plan(
        self,
        skill_name: str,
        action: UninstallAction = UninstallAction.REMOVE,
        scope: UninstallScope = UninstallScope.ALL
    ) -> UninstallPlan | None:
        """Create uninstall plan."""
        locations = self.locator.find_skill(skill_name, scope)

        if not locations:
            return None

        backup_path = None
        if action == UninstallAction.BACKUP_REMOVE:
            backup_path = self._get_backup_path(skill_name)
        elif action == UninstallAction.ARCHIVE:
            backup_path = self._get_archive_path(skill_name)

        return UninstallPlan(
            skill_name=skill_name,
            locations=locations,
            action=action,
            backup_path=backup_path,
            requires_confirmation=True
        )

    def execute(self, plan: UninstallPlan) -> UninstallResult:
        """Execute uninstall plan."""
        locations_removed = []
        total_files = 0
        total_bytes = 0

        try:
            # Create backup/archive if needed
            if plan.action in (UninstallAction.BACKUP_REMOVE, UninstallAction.ARCHIVE):
                self._create_backup(plan)

            # Remove each location
            for location in plan.locations:
                self._remove_location(location)
                locations_removed.append(location.path)
                total_files += location.file_count
                total_bytes += location.total_size

            return UninstallResult(
                skill_name=plan.skill_name,
                success=True,
                locations_removed=locations_removed,
                backup_created=plan.backup_path,
                files_removed=total_files,
                bytes_freed=total_bytes
            )

        except Exception as e:
            return UninstallResult(
                skill_name=plan.skill_name,
                success=False,
                locations_removed=locations_removed,
                error=str(e)
            )

    def _remove_location(self, location: SkillLocation) -> None:
        """Remove a skill location."""
        if location.path.exists():
            shutil.rmtree(location.path)

    def _create_backup(self, plan: UninstallPlan) -> None:
        """Create backup before removal."""
        if not plan.backup_path:
            return

        plan.backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Backup first location (primary)
        if plan.locations:
            shutil.copytree(
                plan.locations[0].path,
                plan.backup_path
            )

    def _get_backup_path(self, skill_name: str) -> Path:
        """Generate backup path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.BACKUP_DIR / f"{skill_name}_{timestamp}"

    def _get_archive_path(self, skill_name: str) -> Path:
        """Generate archive path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.ARCHIVE_DIR / f"{skill_name}_{timestamp}"

    def verify_removal(self, plan: UninstallPlan) -> bool:
        """Verify skill was completely removed."""
        for location in plan.locations:
            if location.path.exists():
                return False
        return True
```

## Uninstall Script

```bash
#!/bin/bash
# uninstall-skill.sh - Safely remove a skill installation
#
# Usage: uninstall-skill.sh <skill-name> [options]
#
# Options:
#   --user          Remove from user skills only
#   --project       Remove from project skills only
#   --backup        Create backup before removal
#   --archive       Move to archive instead of delete
#   --force         Skip confirmation prompt
#   --dry-run       Show what would be removed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
SKILL_NAME=""
SCOPE="all"
ACTION="remove"
FORCE=false
DRY_RUN=false

USER_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS=".claude/skills"
BACKUP_DIR="$HOME/.claude/skill-backups"
ARCHIVE_DIR="$HOME/.claude/skill-archive"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            SCOPE="user"
            shift
            ;;
        --project)
            SCOPE="project"
            shift
            ;;
        --backup)
            ACTION="backup"
            shift
            ;;
        --archive)
            ACTION="archive"
            shift
            ;;
        --force|-f)
            FORCE=true
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SKILL_NAME="$1"
            shift
            ;;
    esac
done

# Validate
if [ -z "$SKILL_NAME" ]; then
    echo "Usage: uninstall-skill.sh <skill-name> [options]"
    exit 1
fi

# Find installations
LOCATIONS=()

if [ "$SCOPE" = "all" ] || [ "$SCOPE" = "user" ]; then
    if [ -d "$USER_SKILLS/$SKILL_NAME" ]; then
        LOCATIONS+=("$USER_SKILLS/$SKILL_NAME")
    fi
fi

if [ "$SCOPE" = "all" ] || [ "$SCOPE" = "project" ]; then
    if [ -d "$PROJECT_SKILLS/$SKILL_NAME" ]; then
        LOCATIONS+=("$PROJECT_SKILLS/$SKILL_NAME")
    fi
fi

if [ ${#LOCATIONS[@]} -eq 0 ]; then
    echo -e "${YELLOW}Skill '$SKILL_NAME' not found${NC}"
    exit 0
fi

# Display plan
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  UNINSTALL: $SKILL_NAME"
echo "═══════════════════════════════════════════════════════════"
echo ""

for loc in "${LOCATIONS[@]}"; do
    FILE_COUNT=$(find "$loc" -type f | wc -l)
    SIZE=$(du -sh "$loc" 2>/dev/null | cut -f1)
    echo "  Location: $loc"
    echo "  Files:    $FILE_COUNT"
    echo "  Size:     $SIZE"
    echo ""
done

echo "  Action: $ACTION"
if [ "$DRY_RUN" = true ]; then
    echo -e "  ${BLUE}(dry-run - no changes will be made)${NC}"
fi
echo ""

# Confirmation
if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    read -p "  Remove this skill? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Cancelled."
        exit 0
    fi
fi

# Execute
if [ "$DRY_RUN" = true ]; then
    echo "  Would remove:"
    for loc in "${LOCATIONS[@]}"; do
        echo "    - $loc"
    done
    exit 0
fi

# Backup/Archive if requested
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ "$ACTION" = "backup" ]; then
    mkdir -p "$BACKUP_DIR"
    BACKUP_PATH="$BACKUP_DIR/${SKILL_NAME}_$TIMESTAMP"
    cp -r "${LOCATIONS[0]}" "$BACKUP_PATH"
    echo -e "  ${GREEN}✓${NC} Backup created: $BACKUP_PATH"
fi

if [ "$ACTION" = "archive" ]; then
    mkdir -p "$ARCHIVE_DIR"
    ARCHIVE_PATH="$ARCHIVE_DIR/${SKILL_NAME}_$TIMESTAMP"
    mv "${LOCATIONS[0]}" "$ARCHIVE_PATH"
    echo -e "  ${GREEN}✓${NC} Archived to: $ARCHIVE_PATH"
    # Remove remaining locations
    for loc in "${LOCATIONS[@]:1}"; do
        rm -rf "$loc"
    done
else
    # Remove all locations
    for loc in "${LOCATIONS[@]}"; do
        rm -rf "$loc"
        echo -e "  ${GREEN}✓${NC} Removed: $loc"
    done
fi

echo ""
echo -e "  ${GREEN}✓ Skill '$SKILL_NAME' uninstalled${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
```

## Uninstall Formatter

```python
class UninstallFormatter:
    """Format uninstall information."""

    def format_plan(self, plan: UninstallPlan) -> str:
        """Format uninstall plan."""
        lines = []

        lines.append("")
        lines.append("  UNINSTALL PLAN")
        lines.append("  ──────────────")
        lines.append(f"  Skill: {plan.skill_name}")
        lines.append("")

        for loc in plan.locations:
            scope_label = "User" if loc.scope == UninstallScope.USER else "Project"
            size = self._format_size(loc.total_size)
            lines.append(f"  [{scope_label}] {loc.path}")
            lines.append(f"          {loc.file_count} files, {size}")
            if loc.version:
                lines.append(f"          Version: {loc.version}")
            lines.append("")

        lines.append(f"  Action: {plan.action.value}")
        if plan.backup_path:
            lines.append(f"  Backup: {plan.backup_path}")

        lines.append("")
        return "\n".join(lines)

    def format_result(self, result: UninstallResult) -> str:
        """Format uninstall result."""
        lines = []

        if result.success:
            lines.append(f"  ✓ Uninstalled: {result.skill_name}")
            lines.append(f"    Removed: {result.files_removed} files")
            lines.append(f"    Freed: {self._format_size(result.bytes_freed)}")
            if result.backup_created:
                lines.append(f"    Backup: {result.backup_created}")
        else:
            lines.append(f"  ✗ Uninstall failed: {result.error}")

        return "\n".join(lines)

    def format_skill_list(
        self,
        skills: dict[str, list[SkillLocation]]
    ) -> str:
        """Format list of installed skills."""
        lines = []

        lines.append("")
        lines.append("  INSTALLED SKILLS")
        lines.append("  ────────────────")

        if not skills:
            lines.append("  No skills installed")
            return "\n".join(lines)

        for name, locations in sorted(skills.items()):
            version = locations[0].version or "?"
            scopes = [l.scope.value for l in locations]
            lines.append(f"  • {name} (v{version})")
            lines.append(f"    Locations: {', '.join(scopes)}")

        lines.append("")
        lines.append(f"  Total: {len(skills)} skill(s)")
        lines.append("")

        return "\n".join(lines)

    def _format_size(self, bytes: int) -> str:
        """Format byte size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
```

## Integration

```python
def uninstall_skill(
    skill_name: str,
    backup: bool = False,
    scope: UninstallScope = UninstallScope.ALL
) -> UninstallResult:
    """Uninstall a skill."""
    uninstaller = SkillUninstaller()
    formatter = UninstallFormatter()

    action = UninstallAction.BACKUP_REMOVE if backup else UninstallAction.REMOVE
    plan = uninstaller.create_plan(skill_name, action, scope)

    if not plan:
        print(f"  Skill '{skill_name}' not found")
        return UninstallResult(
            skill_name=skill_name,
            success=False,
            error="Skill not found"
        )

    print(formatter.format_plan(plan))

    # Would prompt for confirmation here
    result = uninstaller.execute(plan)
    print(formatter.format_result(result))

    return result
```

## Sample Output

```
  UNINSTALL PLAN
  ──────────────
  Skill: api-doc-generator

  [User] /home/user/.claude/skills/api-doc-generator
          5 files, 12.3 KB
          Version: 1.2.0

  Action: backup_remove
  Backup: /home/user/.claude/skill-backups/api-doc-generator_20240115_143022

  ✓ Uninstalled: api-doc-generator
    Removed: 5 files
    Freed: 12.3 KB
    Backup: /home/user/.claude/skill-backups/api-doc-generator_20240115_143022
```
