# Skill Export to ZIP

Create distributable ZIP archives of skills for sharing and distribution.

## Export Goals

| Goal | Description |
|------|-------------|
| Distribution | Package skills for sharing |
| Portability | Single file for easy transfer |
| Metadata | Include version and manifest |
| Validation | Verify completeness before export |

## Export Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class ExportFormat(Enum):
    ZIP = "zip"
    TAR_GZ = "tar.gz"

class ExportScope(Enum):
    FULL = "full"           # All files
    MINIMAL = "minimal"     # SKILL.md only
    STANDARD = "standard"   # SKILL.md + references

@dataclass
class ExportConfig:
    skill_path: Path
    output_path: Path | None = None
    format: ExportFormat = ExportFormat.ZIP
    scope: ExportScope = ExportScope.FULL
    include_metadata: bool = True
    include_readme: bool = True
    exclude_patterns: list[str] = field(default_factory=list)

@dataclass
class ExportManifest:
    skill_name: str
    version: str
    created_at: str
    files: list[str]
    total_size: int
    checksum: str

@dataclass
class ExportResult:
    success: bool
    output_path: Path | None = None
    manifest: ExportManifest | None = None
    file_count: int = 0
    archive_size: int = 0
    error: str | None = None
```

## Skill Exporter

```python
import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

class SkillExporter:
    """Export skills to distributable archives."""

    # Files to exclude by default
    DEFAULT_EXCLUDES = [
        ".git",
        ".git/**",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".dev-link",
        ".skill-meta.json",
        "*.backup",
    ]

    def __init__(self, config: ExportConfig):
        self.config = config
        self.excludes = self.DEFAULT_EXCLUDES + config.exclude_patterns

    def export(self) -> ExportResult:
        """Export skill to archive."""
        skill_path = self.config.skill_path

        # Validate skill
        if not (skill_path / "SKILL.md").exists():
            return ExportResult(
                success=False,
                error="Not a valid skill (missing SKILL.md)"
            )

        # Determine output path
        output_path = self._get_output_path()

        # Collect files
        files = self._collect_files()

        if not files:
            return ExportResult(
                success=False,
                error="No files to export"
            )

        # Create archive
        try:
            if self.config.format == ExportFormat.ZIP:
                self._create_zip(output_path, files)
            else:
                self._create_tar(output_path, files)

            # Create manifest
            manifest = self._create_manifest(files, output_path)

            return ExportResult(
                success=True,
                output_path=output_path,
                manifest=manifest,
                file_count=len(files),
                archive_size=output_path.stat().st_size
            )

        except Exception as e:
            return ExportResult(
                success=False,
                error=str(e)
            )

    def _get_output_path(self) -> Path:
        """Determine output archive path."""
        if self.config.output_path:
            return self.config.output_path

        skill_name = self.config.skill_path.name
        version = self._get_version()
        timestamp = datetime.now().strftime("%Y%m%d")

        if version:
            filename = f"{skill_name}-{version}.zip"
        else:
            filename = f"{skill_name}-{timestamp}.zip"

        return self.config.skill_path.parent / filename

    def _get_version(self) -> str | None:
        """Get skill version."""
        skill_md = self.config.skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            match = re.search(r'^version:\s*["\']?([^"\'\n]+)', content, re.M)
            if match:
                return match.group(1).strip()
        return None

    def _collect_files(self) -> list[Path]:
        """Collect files to include in archive."""
        files = []
        skill_path = self.config.skill_path

        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(skill_path)

                # Check exclusions
                if self._should_exclude(rel_path):
                    continue

                # Check scope
                if not self._in_scope(rel_path):
                    continue

                files.append(file_path)

        return files

    def _should_exclude(self, rel_path: Path) -> bool:
        """Check if file should be excluded."""
        import fnmatch

        path_str = str(rel_path)

        for pattern in self.excludes:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if fnmatch.fnmatch(rel_path.name, pattern):
                return True

        return False

    def _in_scope(self, rel_path: Path) -> bool:
        """Check if file is in export scope."""
        scope = self.config.scope

        if scope == ExportScope.FULL:
            return True

        if scope == ExportScope.MINIMAL:
            return rel_path.name == "SKILL.md"

        if scope == ExportScope.STANDARD:
            # SKILL.md, README.md, references/
            if rel_path.name in ("SKILL.md", "README.md"):
                return True
            if str(rel_path).startswith("references"):
                return True
            return False

        return True

    def _create_zip(self, output_path: Path, files: list[Path]) -> None:
        """Create ZIP archive."""
        skill_path = self.config.skill_path
        skill_name = skill_path.name

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add files
            for file_path in files:
                rel_path = file_path.relative_to(skill_path)
                arc_name = f"{skill_name}/{rel_path}"
                zf.write(file_path, arc_name)

            # Add manifest
            if self.config.include_metadata:
                manifest = self._create_manifest(files, output_path)
                manifest_content = json.dumps({
                    "skill_name": manifest.skill_name,
                    "version": manifest.version,
                    "created_at": manifest.created_at,
                    "files": manifest.files,
                    "total_size": manifest.total_size,
                    "checksum": manifest.checksum
                }, indent=2)
                zf.writestr(f"{skill_name}/MANIFEST.json", manifest_content)

    def _create_tar(self, output_path: Path, files: list[Path]) -> None:
        """Create TAR.GZ archive."""
        import tarfile

        skill_path = self.config.skill_path
        skill_name = skill_path.name

        with tarfile.open(output_path, "w:gz") as tf:
            for file_path in files:
                rel_path = file_path.relative_to(skill_path)
                arc_name = f"{skill_name}/{rel_path}"
                tf.add(file_path, arc_name)

    def _create_manifest(
        self,
        files: list[Path],
        output_path: Path
    ) -> ExportManifest:
        """Create export manifest."""
        skill_path = self.config.skill_path
        skill_name = skill_path.name

        # Calculate total size
        total_size = sum(f.stat().st_size for f in files)

        # Calculate checksum
        checksum = self._calculate_checksum(files)

        # File list
        file_list = [
            str(f.relative_to(skill_path))
            for f in files
        ]

        return ExportManifest(
            skill_name=skill_name,
            version=self._get_version() or "0.0.0",
            created_at=datetime.now().isoformat(),
            files=file_list,
            total_size=total_size,
            checksum=checksum
        )

    def _calculate_checksum(self, files: list[Path]) -> str:
        """Calculate combined checksum of files."""
        hasher = hashlib.sha256()

        for file_path in sorted(files):
            hasher.update(file_path.read_bytes())

        return hasher.hexdigest()[:16]
```

## Export Script

```bash
#!/bin/bash
# export-skill.sh - Export skill to distributable archive
#
# Usage: export-skill.sh <skill-path> [options]
#
# Options:
#   --output <path>  Output archive path
#   --format <fmt>   Format: zip (default) or tar.gz
#   --minimal        Export SKILL.md only
#   --standard       Export SKILL.md + references
#   --full           Export all files (default)
#   --no-manifest    Skip manifest generation

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
SKILL_PATH=""
OUTPUT_PATH=""
FORMAT="zip"
SCOPE="full"
INCLUDE_MANIFEST=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output|-o)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --format|-f)
            FORMAT="$2"
            shift 2
            ;;
        --minimal)
            SCOPE="minimal"
            shift
            ;;
        --standard)
            SCOPE="standard"
            shift
            ;;
        --full)
            SCOPE="full"
            shift
            ;;
        --no-manifest)
            INCLUDE_MANIFEST=false
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

# Validate
if [ -z "$SKILL_PATH" ]; then
    echo "Usage: export-skill.sh <skill-path> [options]"
    exit 1
fi

SKILL_PATH=$(cd "$SKILL_PATH" && pwd)
SKILL_NAME=$(basename "$SKILL_PATH")

if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
    echo "Error: Not a valid skill (missing SKILL.md)"
    exit 1
fi

# Get version
VERSION=$(grep -m1 "^version:" "$SKILL_PATH/SKILL.md" | sed 's/version:\s*//' | tr -d '"'"'" || echo "")

# Determine output path
if [ -z "$OUTPUT_PATH" ]; then
    if [ -n "$VERSION" ]; then
        OUTPUT_PATH="${SKILL_NAME}-${VERSION}.${FORMAT}"
    else
        OUTPUT_PATH="${SKILL_NAME}-$(date +%Y%m%d).${FORMAT}"
    fi
fi

# Create temp directory for staging
TEMP_DIR=$(mktemp -d)
STAGE_DIR="$TEMP_DIR/$SKILL_NAME"
mkdir -p "$STAGE_DIR"

# Copy files based on scope
echo -e "${BLUE}Collecting files...${NC}"

if [ "$SCOPE" = "minimal" ]; then
    cp "$SKILL_PATH/SKILL.md" "$STAGE_DIR/"
elif [ "$SCOPE" = "standard" ]; then
    cp "$SKILL_PATH/SKILL.md" "$STAGE_DIR/"
    [ -f "$SKILL_PATH/README.md" ] && cp "$SKILL_PATH/README.md" "$STAGE_DIR/"
    [ -d "$SKILL_PATH/references" ] && cp -r "$SKILL_PATH/references" "$STAGE_DIR/"
else
    # Full - copy all except excluded
    rsync -a --exclude='.git' --exclude='__pycache__' \
          --exclude='.DS_Store' --exclude='.dev-link' \
          --exclude='*.pyc' --exclude='*.backup' \
          "$SKILL_PATH/" "$STAGE_DIR/"
fi

# Generate manifest
if [ "$INCLUDE_MANIFEST" = true ]; then
    FILE_COUNT=$(find "$STAGE_DIR" -type f | wc -l)
    TOTAL_SIZE=$(du -sb "$STAGE_DIR" | cut -f1)
    CHECKSUM=$(find "$STAGE_DIR" -type f -exec sha256sum {} \; | sha256sum | cut -c1-16)

    cat > "$STAGE_DIR/MANIFEST.json" << EOF
{
  "skill_name": "$SKILL_NAME",
  "version": "${VERSION:-0.0.0}",
  "created_at": "$(date -Iseconds)",
  "file_count": $FILE_COUNT,
  "total_size": $TOTAL_SIZE,
  "checksum": "$CHECKSUM"
}
EOF
fi

# Create archive
echo -e "${BLUE}Creating archive...${NC}"

cd "$TEMP_DIR"
if [ "$FORMAT" = "zip" ]; then
    zip -r "$OUTPUT_PATH" "$SKILL_NAME" > /dev/null
else
    tar -czf "$OUTPUT_PATH" "$SKILL_NAME"
fi

mv "$OUTPUT_PATH" "$(pwd -P)/../$OUTPUT_PATH"
OUTPUT_PATH="../$OUTPUT_PATH"

# Cleanup
rm -rf "$TEMP_DIR"

# Report
ARCHIVE_SIZE=$(ls -lh "$OUTPUT_PATH" | awk '{print $5}')

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  SKILL EXPORTED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Skill:   $SKILL_NAME"
echo "  Version: ${VERSION:-unversioned}"
echo "  Scope:   $SCOPE"
echo "  Format:  $FORMAT"
echo ""
echo "  Output:  $OUTPUT_PATH"
echo "  Size:    $ARCHIVE_SIZE"
echo ""
echo "  To install:"
echo "    unzip $OUTPUT_PATH -d ~/.claude/skills/"
echo ""
echo "═══════════════════════════════════════════════════════════"
```

## Export Formatter

```python
class ExportFormatter:
    """Format export information."""

    def format_result(self, result: ExportResult) -> str:
        """Format export result."""
        lines = []

        if result.success:
            lines.append("")
            lines.append("  ✓ EXPORT SUCCESSFUL")
            lines.append("  ──────────────────")
            lines.append(f"  Output: {result.output_path}")
            lines.append(f"  Files:  {result.file_count}")
            lines.append(f"  Size:   {self._format_size(result.archive_size)}")

            if result.manifest:
                lines.append("")
                lines.append("  Manifest:")
                lines.append(f"    Name:     {result.manifest.skill_name}")
                lines.append(f"    Version:  {result.manifest.version}")
                lines.append(f"    Checksum: {result.manifest.checksum}")

            lines.append("")
            lines.append("  To install:")
            lines.append(f"    unzip {result.output_path} -d ~/.claude/skills/")
        else:
            lines.append(f"  ✗ Export failed: {result.error}")

        return "\n".join(lines)

    def format_manifest(self, manifest: ExportManifest) -> str:
        """Format manifest for display."""
        lines = []

        lines.append("  MANIFEST")
        lines.append("  ────────")
        lines.append(f"  Skill:    {manifest.skill_name}")
        lines.append(f"  Version:  {manifest.version}")
        lines.append(f"  Created:  {manifest.created_at}")
        lines.append(f"  Size:     {self._format_size(manifest.total_size)}")
        lines.append(f"  Checksum: {manifest.checksum}")
        lines.append("")
        lines.append(f"  Files ({len(manifest.files)}):")

        for f in manifest.files[:10]:
            lines.append(f"    • {f}")

        if len(manifest.files) > 10:
            lines.append(f"    ... and {len(manifest.files) - 10} more")

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
def export_skill(
    skill_path: Path,
    output_path: Path | None = None,
    scope: ExportScope = ExportScope.FULL
) -> ExportResult:
    """Export skill to distributable archive."""
    config = ExportConfig(
        skill_path=skill_path,
        output_path=output_path,
        scope=scope
    )

    exporter = SkillExporter(config)
    formatter = ExportFormatter()

    result = exporter.export()
    print(formatter.format_result(result))

    return result
```

## Sample Output

```
═══════════════════════════════════════════════════════════
  SKILL EXPORTED
═══════════════════════════════════════════════════════════

  Skill:   api-doc-generator
  Version: 1.2.0
  Scope:   full
  Format:  zip

  Output:  api-doc-generator-1.2.0.zip
  Size:    15.2 KB

  To install:
    unzip api-doc-generator-1.2.0.zip -d ~/.claude/skills/

═══════════════════════════════════════════════════════════
```
