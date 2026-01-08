# Skill Import from ZIP

Extract and install skills from distributable ZIP archives.

## Import Goals

| Goal | Description |
|------|-------------|
| Easy installation | One-command import from archive |
| Validation | Verify archive contents before install |
| Conflict handling | Detect and handle existing skills |
| Integrity check | Verify checksum if manifest present |

## Import Model

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class ImportSource(Enum):
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    DIRECTORY = "directory"
    URL = "url"

class ConflictAction(Enum):
    SKIP = "skip"           # Keep existing
    REPLACE = "replace"     # Overwrite existing
    BACKUP = "backup"       # Backup then replace
    RENAME = "rename"       # Install with new name

@dataclass
class ImportConfig:
    source: Path | str
    target_scope: str = "user"     # "user" or "project"
    conflict_action: ConflictAction = ConflictAction.BACKUP
    verify_checksum: bool = True
    dry_run: bool = False

@dataclass
class ArchiveContents:
    skill_name: str
    version: str | None
    files: list[str]
    has_manifest: bool
    manifest_checksum: str | None = None
    total_size: int = 0

@dataclass
class ImportResult:
    success: bool
    skill_name: str
    installed_path: Path | None = None
    files_installed: int = 0
    conflict_resolved: ConflictAction | None = None
    backup_path: Path | None = None
    error: str | None = None
```

## Skill Importer

```python
import hashlib
import json
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

class SkillImporter:
    """Import skills from archives."""

    USER_SKILLS = Path.home() / ".claude" / "skills"
    PROJECT_SKILLS = Path(".claude/skills")
    BACKUP_DIR = Path.home() / ".claude" / "skill-backups"

    def __init__(self, config: ImportConfig):
        self.config = config

    def import_skill(self) -> ImportResult:
        """Import skill from archive."""
        source = Path(self.config.source)

        # Detect source type
        if not source.exists():
            return ImportResult(
                success=False,
                skill_name="unknown",
                error=f"Source not found: {source}"
            )

        # Extract to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract archive
            try:
                extracted = self._extract(source, temp_path)
            except Exception as e:
                return ImportResult(
                    success=False,
                    skill_name="unknown",
                    error=f"Extraction failed: {e}"
                )

            # Analyze contents
            contents = self._analyze_contents(extracted)

            if not contents:
                return ImportResult(
                    success=False,
                    skill_name="unknown",
                    error="No valid skill found in archive"
                )

            # Verify checksum if requested
            if self.config.verify_checksum and contents.manifest_checksum:
                if not self._verify_checksum(extracted, contents.manifest_checksum):
                    return ImportResult(
                        success=False,
                        skill_name=contents.skill_name,
                        error="Checksum verification failed"
                    )

            # Determine target path
            target_path = self._get_target_path(contents.skill_name)

            # Handle conflicts
            conflict_result = None
            backup_path = None

            if target_path.exists():
                conflict_result, backup_path = self._handle_conflict(
                    target_path, contents.skill_name
                )

                if conflict_result == ConflictAction.SKIP:
                    return ImportResult(
                        success=True,
                        skill_name=contents.skill_name,
                        conflict_resolved=ConflictAction.SKIP
                    )

            # Dry run - stop here
            if self.config.dry_run:
                return ImportResult(
                    success=True,
                    skill_name=contents.skill_name,
                    installed_path=target_path,
                    files_installed=len(contents.files)
                )

            # Install skill
            try:
                self._install(extracted, target_path)

                return ImportResult(
                    success=True,
                    skill_name=contents.skill_name,
                    installed_path=target_path,
                    files_installed=len(contents.files),
                    conflict_resolved=conflict_result,
                    backup_path=backup_path
                )

            except Exception as e:
                return ImportResult(
                    success=False,
                    skill_name=contents.skill_name,
                    error=f"Installation failed: {e}"
                )

    def _extract(self, source: Path, target: Path) -> Path:
        """Extract archive to target directory."""
        if source.suffix == ".zip":
            with zipfile.ZipFile(source, "r") as zf:
                zf.extractall(target)
        elif source.name.endswith(".tar.gz"):
            with tarfile.open(source, "r:gz") as tf:
                tf.extractall(target)
        else:
            # Assume directory
            shutil.copytree(source, target / source.name)

        # Find extracted skill directory
        for item in target.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                return item

        # Check if SKILL.md is at root
        if (target / "SKILL.md").exists():
            return target

        raise ValueError("No skill found in archive")

    def _analyze_contents(self, skill_path: Path) -> ArchiveContents | None:
        """Analyze extracted skill contents."""
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            return None

        skill_name = skill_path.name

        # Get version from SKILL.md
        version = None
        content = skill_md.read_text()
        import re
        match = re.search(r'^version:\s*["\']?([^"\'\n]+)', content, re.M)
        if match:
            version = match.group(1).strip()

        # List files
        files = []
        total_size = 0
        for f in skill_path.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(skill_path)))
                total_size += f.stat().st_size

        # Check for manifest
        manifest_path = skill_path / "MANIFEST.json"
        has_manifest = manifest_path.exists()
        manifest_checksum = None

        if has_manifest:
            manifest = json.loads(manifest_path.read_text())
            manifest_checksum = manifest.get("checksum")

        return ArchiveContents(
            skill_name=skill_name,
            version=version,
            files=files,
            has_manifest=has_manifest,
            manifest_checksum=manifest_checksum,
            total_size=total_size
        )

    def _verify_checksum(self, skill_path: Path, expected: str) -> bool:
        """Verify file checksums."""
        hasher = hashlib.sha256()

        for file_path in sorted(skill_path.rglob("*")):
            if file_path.is_file() and file_path.name != "MANIFEST.json":
                hasher.update(file_path.read_bytes())

        actual = hasher.hexdigest()[:16]
        return actual == expected

    def _get_target_path(self, skill_name: str) -> Path:
        """Get target installation path."""
        if self.config.target_scope == "project":
            return self.PROJECT_SKILLS / skill_name
        return self.USER_SKILLS / skill_name

    def _handle_conflict(
        self,
        target_path: Path,
        skill_name: str
    ) -> tuple[ConflictAction, Path | None]:
        """Handle existing skill conflict."""
        action = self.config.conflict_action

        if action == ConflictAction.SKIP:
            return ConflictAction.SKIP, None

        if action == ConflictAction.REPLACE:
            shutil.rmtree(target_path)
            return ConflictAction.REPLACE, None

        if action == ConflictAction.BACKUP:
            backup_path = self._create_backup(target_path, skill_name)
            shutil.rmtree(target_path)
            return ConflictAction.BACKUP, backup_path

        if action == ConflictAction.RENAME:
            # Find available name
            counter = 2
            while target_path.exists():
                new_name = f"{skill_name}-{counter}"
                target_path = target_path.parent / new_name
                counter += 1
            return ConflictAction.RENAME, None

        return ConflictAction.SKIP, None

    def _create_backup(self, target_path: Path, skill_name: str) -> Path:
        """Create backup of existing skill."""
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.BACKUP_DIR / f"{skill_name}_{timestamp}"

        shutil.copytree(target_path, backup_path)
        return backup_path

    def _install(self, source: Path, target: Path) -> None:
        """Install skill to target location."""
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
```

## Import Script

```bash
#!/bin/bash
# import-skill.sh - Import skill from archive
#
# Usage: import-skill.sh <archive-path> [options]
#
# Options:
#   --user           Install to user skills (default)
#   --project        Install to project skills
#   --skip           Skip if exists
#   --replace        Replace existing
#   --backup         Backup then replace (default)
#   --dry-run        Show what would happen
#   --no-verify      Skip checksum verification

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
ARCHIVE_PATH=""
SCOPE="user"
CONFLICT="backup"
DRY_RUN=false
VERIFY=true

USER_SKILLS="$HOME/.claude/skills"
PROJECT_SKILLS=".claude/skills"
BACKUP_DIR="$HOME/.claude/skill-backups"

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
        --skip)
            CONFLICT="skip"
            shift
            ;;
        --replace)
            CONFLICT="replace"
            shift
            ;;
        --backup)
            CONFLICT="backup"
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --no-verify)
            VERIFY=false
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            ARCHIVE_PATH="$1"
            shift
            ;;
    esac
done

# Validate
if [ -z "$ARCHIVE_PATH" ]; then
    echo "Usage: import-skill.sh <archive-path> [options]"
    exit 1
fi

if [ ! -f "$ARCHIVE_PATH" ]; then
    echo -e "${RED}Error: Archive not found: $ARCHIVE_PATH${NC}"
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extract archive
echo -e "${BLUE}Extracting archive...${NC}"

if [[ "$ARCHIVE_PATH" == *.zip ]]; then
    unzip -q "$ARCHIVE_PATH" -d "$TEMP_DIR"
elif [[ "$ARCHIVE_PATH" == *.tar.gz ]]; then
    tar -xzf "$ARCHIVE_PATH" -C "$TEMP_DIR"
else
    echo -e "${RED}Error: Unsupported archive format${NC}"
    exit 1
fi

# Find skill directory
SKILL_DIR=""
for dir in "$TEMP_DIR"/*/; do
    if [ -f "${dir}SKILL.md" ]; then
        SKILL_DIR="$dir"
        break
    fi
done

if [ -z "$SKILL_DIR" ]; then
    echo -e "${RED}Error: No valid skill found in archive${NC}"
    exit 1
fi

SKILL_NAME=$(basename "$SKILL_DIR")

# Get version
VERSION=$(grep -m1 "^version:" "${SKILL_DIR}SKILL.md" 2>/dev/null | sed 's/version:\s*//' | tr -d '"'"'" || echo "")

# Verify checksum if manifest exists
if [ "$VERIFY" = true ] && [ -f "${SKILL_DIR}MANIFEST.json" ]; then
    EXPECTED=$(python3 -c "import json; print(json.load(open('${SKILL_DIR}MANIFEST.json')).get('checksum', ''))")
    if [ -n "$EXPECTED" ]; then
        echo -e "${BLUE}Verifying checksum...${NC}"
        ACTUAL=$(find "$SKILL_DIR" -type f ! -name "MANIFEST.json" -exec sha256sum {} \; | sort | sha256sum | cut -c1-16)
        if [ "$EXPECTED" != "$ACTUAL" ]; then
            echo -e "${RED}Error: Checksum verification failed${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Checksum verified${NC}"
    fi
fi

# Determine target
if [ "$SCOPE" = "project" ]; then
    TARGET_DIR="$PROJECT_SKILLS/$SKILL_NAME"
else
    TARGET_DIR="$USER_SKILLS/$SKILL_NAME"
fi

# Handle conflicts
BACKUP_PATH=""
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}Existing skill found: $TARGET_DIR${NC}"

    case $CONFLICT in
        skip)
            echo -e "  Skipping installation (--skip)"
            exit 0
            ;;
        replace)
            if [ "$DRY_RUN" = false ]; then
                rm -rf "$TARGET_DIR"
            fi
            echo -e "  Replacing existing skill"
            ;;
        backup)
            TIMESTAMP=$(date +%Y%m%d_%H%M%S)
            BACKUP_PATH="$BACKUP_DIR/${SKILL_NAME}_$TIMESTAMP"
            if [ "$DRY_RUN" = false ]; then
                mkdir -p "$BACKUP_DIR"
                mv "$TARGET_DIR" "$BACKUP_PATH"
            fi
            echo -e "  Backed up to: $BACKUP_PATH"
            ;;
    esac
fi

# Install
if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${BLUE}DRY RUN - No changes made${NC}"
    echo "  Would install: $SKILL_NAME"
    echo "  Target: $TARGET_DIR"
    echo "  Files: $(find "$SKILL_DIR" -type f | wc -l)"
    exit 0
fi

mkdir -p "$(dirname "$TARGET_DIR")"
cp -r "$SKILL_DIR" "$TARGET_DIR"

# Count files
FILE_COUNT=$(find "$TARGET_DIR" -type f | wc -l)

# Report
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  SKILL IMPORTED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Skill:     $SKILL_NAME"
echo "  Version:   ${VERSION:-unknown}"
echo "  Installed: $TARGET_DIR"
echo "  Files:     $FILE_COUNT"
if [ -n "$BACKUP_PATH" ]; then
    echo "  Backup:    $BACKUP_PATH"
fi
echo ""
echo "  Invoke with: /$SKILL_NAME"
echo ""
echo "═══════════════════════════════════════════════════════════"
```

## Import Formatter

```python
class ImportFormatter:
    """Format import information."""

    def format_contents(self, contents: ArchiveContents) -> str:
        """Format archive contents preview."""
        lines = []

        lines.append("")
        lines.append("  ARCHIVE CONTENTS")
        lines.append("  ────────────────")
        lines.append(f"  Skill:    {contents.skill_name}")
        lines.append(f"  Version:  {contents.version or 'unknown'}")
        lines.append(f"  Files:    {len(contents.files)}")
        lines.append(f"  Size:     {self._format_size(contents.total_size)}")
        lines.append(f"  Manifest: {'Yes' if contents.has_manifest else 'No'}")

        if contents.manifest_checksum:
            lines.append(f"  Checksum: {contents.manifest_checksum}")

        lines.append("")
        lines.append("  Files:")
        for f in contents.files[:5]:
            lines.append(f"    • {f}")
        if len(contents.files) > 5:
            lines.append(f"    ... and {len(contents.files) - 5} more")

        return "\n".join(lines)

    def format_result(self, result: ImportResult) -> str:
        """Format import result."""
        lines = []

        if result.success:
            lines.append("")
            lines.append("  ✓ IMPORT SUCCESSFUL")
            lines.append("  ───────────────────")
            lines.append(f"  Skill:     {result.skill_name}")
            lines.append(f"  Installed: {result.installed_path}")
            lines.append(f"  Files:     {result.files_installed}")

            if result.conflict_resolved:
                lines.append(f"  Conflict:  {result.conflict_resolved.value}")
            if result.backup_path:
                lines.append(f"  Backup:    {result.backup_path}")

            lines.append("")
            lines.append(f"  Invoke with: /{result.skill_name}")
        else:
            lines.append(f"  ✗ Import failed: {result.error}")

        return "\n".join(lines)

    def _format_size(self, bytes: int) -> str:
        """Format byte size."""
        for unit in ["B", "KB", "MB"]:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} GB"
```

## Integration

```python
def import_skill(
    archive_path: Path,
    scope: str = "user",
    conflict: ConflictAction = ConflictAction.BACKUP
) -> ImportResult:
    """Import skill from archive."""
    config = ImportConfig(
        source=archive_path,
        target_scope=scope,
        conflict_action=conflict
    )

    importer = SkillImporter(config)
    formatter = ImportFormatter()

    result = importer.import_skill()
    print(formatter.format_result(result))

    return result
```

## Sample Output

```
═══════════════════════════════════════════════════════════
  SKILL IMPORTED
═══════════════════════════════════════════════════════════

  Skill:     api-doc-generator
  Version:   1.2.0
  Installed: /home/user/.claude/skills/api-doc-generator
  Files:     5
  Backup:    /home/user/.claude/skill-backups/api-doc-generator_20240115

  Invoke with: /api-doc-generator

═══════════════════════════════════════════════════════════
```
