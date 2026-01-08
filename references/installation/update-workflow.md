# Skill Update Workflow

Detect existing skills and provide update options during installation.

## Update Workflow Goals

| Goal | Description |
|------|-------------|
| Detect existing | Find installed versions of skill |
| Compare versions | Determine if update is needed |
| Offer options | Let user choose update strategy |
| Safe update | Preserve user customizations |

## Update Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class UpdateAction(Enum):
    INSTALL_NEW = "install_new"      # Fresh installation
    UPDATE_IN_PLACE = "update"       # Replace existing
    UPDATE_BACKUP = "backup_update"  # Backup then update
    MERGE = "merge"                  # Merge changes
    SKIP = "skip"                    # Keep existing
    SIDE_BY_SIDE = "side_by_side"    # Install as new version

class ChangeCategory(Enum):
    ADDED = "added"           # New files
    MODIFIED = "modified"     # Changed files
    REMOVED = "removed"       # Deleted files
    UNCHANGED = "unchanged"   # Same content

@dataclass
class VersionComparison:
    existing_version: str
    new_version: str
    is_newer: bool
    is_major_update: bool

@dataclass
class FileChange:
    path: Path
    category: ChangeCategory
    existing_hash: str | None = None
    new_hash: str | None = None
    is_user_modified: bool = False

@dataclass
class UpdateAnalysis:
    skill_name: str
    existing_path: Path
    comparison: VersionComparison
    file_changes: list[FileChange]
    has_user_modifications: bool
    recommended_action: UpdateAction
    warnings: list[str] = field(default_factory=list)

@dataclass
class UpdateResult:
    action_taken: UpdateAction
    success: bool
    backup_path: Path | None = None
    files_updated: list[Path] = field(default_factory=list)
    files_preserved: list[Path] = field(default_factory=list)
    error: str | None = None
```

## Existing Skill Detector

```python
import hashlib
import json
import re
from pathlib import Path

class ExistingSkillDetector:
    """Detect and analyze existing skill installations."""

    USER_SKILLS_PATH = Path.home() / ".claude" / "skills"
    PROJECT_SKILLS_PATH = Path(".claude/skills")
    METADATA_FILE = ".skill-meta.json"

    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    def find_existing(self) -> list[Path]:
        """Find all existing installations of the skill."""
        locations = []

        # Check user skills
        user_path = self.USER_SKILLS_PATH / self.skill_name
        if user_path.exists():
            locations.append(user_path)

        # Check project skills
        project_path = self.PROJECT_SKILLS_PATH / self.skill_name
        if project_path.exists():
            locations.append(project_path)

        return locations

    def get_installed_version(self, skill_path: Path) -> str | None:
        """Get version of installed skill."""
        # Check metadata file
        meta_path = skill_path / self.METADATA_FILE
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            return meta.get("version")

        # Parse from SKILL.md frontmatter
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            match = re.search(r'^version:\s*["\']?([^"\'\n]+)', content, re.M)
            if match:
                return match.group(1).strip()

        return None

    def get_file_hashes(self, skill_path: Path) -> dict[str, str]:
        """Get hashes of all files in skill."""
        hashes = {}

        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(skill_path)
                content = file_path.read_bytes()
                hashes[str(rel_path)] = hashlib.sha256(content).hexdigest()[:16]

        return hashes

    def check_user_modifications(
        self,
        skill_path: Path,
        original_hashes: dict[str, str]
    ) -> list[str]:
        """Check which files have been modified by user."""
        modified = []
        current_hashes = self.get_file_hashes(skill_path)

        for rel_path, original_hash in original_hashes.items():
            current_hash = current_hashes.get(rel_path)
            if current_hash and current_hash != original_hash:
                modified.append(rel_path)

        return modified
```

## Update Analyzer

```python
class UpdateAnalyzer:
    """Analyze differences between existing and new skill."""

    def __init__(self, detector: ExistingSkillDetector):
        self.detector = detector

    def analyze(
        self,
        existing_path: Path,
        new_content: dict[str, str],
        new_version: str
    ) -> UpdateAnalysis:
        """Analyze update requirements."""
        # Get version comparison
        existing_version = self.detector.get_installed_version(existing_path)
        comparison = self._compare_versions(existing_version, new_version)

        # Get file changes
        existing_hashes = self.detector.get_file_hashes(existing_path)
        new_hashes = {
            path: hashlib.sha256(content.encode()).hexdigest()[:16]
            for path, content in new_content.items()
        }

        file_changes = self._compute_changes(existing_hashes, new_hashes)

        # Check for user modifications
        # (would need original hashes from installation)
        meta_path = existing_path / ".skill-meta.json"
        original_hashes = {}
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            original_hashes = meta.get("original_hashes", {})

        user_modified = self.detector.check_user_modifications(
            existing_path, original_hashes
        )
        has_user_mods = len(user_modified) > 0

        # Mark user-modified files
        for change in file_changes:
            if str(change.path) in user_modified:
                change.is_user_modified = True

        # Determine recommended action
        recommended = self._recommend_action(
            comparison, file_changes, has_user_mods
        )

        # Collect warnings
        warnings = []
        if has_user_mods:
            warnings.append(
                f"{len(user_modified)} file(s) have local modifications"
            )
        if comparison.is_major_update:
            warnings.append("Major version update - may have breaking changes")

        return UpdateAnalysis(
            skill_name=self.detector.skill_name,
            existing_path=existing_path,
            comparison=comparison,
            file_changes=file_changes,
            has_user_modifications=has_user_mods,
            recommended_action=recommended,
            warnings=warnings
        )

    def _compare_versions(
        self,
        existing: str | None,
        new: str
    ) -> VersionComparison:
        """Compare version strings."""
        if not existing:
            existing = "0.0.0"

        def parse_version(v: str) -> tuple[int, int, int]:
            parts = v.split(".")
            return (
                int(parts[0]) if len(parts) > 0 else 0,
                int(parts[1]) if len(parts) > 1 else 0,
                int(parts[2]) if len(parts) > 2 else 0
            )

        ex_parts = parse_version(existing)
        new_parts = parse_version(new)

        is_newer = new_parts > ex_parts
        is_major = new_parts[0] > ex_parts[0]

        return VersionComparison(
            existing_version=existing,
            new_version=new,
            is_newer=is_newer,
            is_major_update=is_major
        )

    def _compute_changes(
        self,
        existing: dict[str, str],
        new: dict[str, str]
    ) -> list[FileChange]:
        """Compute file changes."""
        changes = []
        all_files = set(existing.keys()) | set(new.keys())

        for file_path in all_files:
            ex_hash = existing.get(file_path)
            new_hash = new.get(file_path)

            if ex_hash and not new_hash:
                category = ChangeCategory.REMOVED
            elif not ex_hash and new_hash:
                category = ChangeCategory.ADDED
            elif ex_hash != new_hash:
                category = ChangeCategory.MODIFIED
            else:
                category = ChangeCategory.UNCHANGED

            changes.append(FileChange(
                path=Path(file_path),
                category=category,
                existing_hash=ex_hash,
                new_hash=new_hash
            ))

        return changes

    def _recommend_action(
        self,
        comparison: VersionComparison,
        changes: list[FileChange],
        has_user_mods: bool
    ) -> UpdateAction:
        """Recommend update action."""
        if not comparison.is_newer:
            return UpdateAction.SKIP

        if has_user_mods:
            return UpdateAction.UPDATE_BACKUP

        modified_count = sum(
            1 for c in changes
            if c.category == ChangeCategory.MODIFIED
        )

        if modified_count == 0:
            return UpdateAction.UPDATE_IN_PLACE

        return UpdateAction.UPDATE_IN_PLACE
```

## Update Executor

```python
import shutil
from datetime import datetime

class UpdateExecutor:
    """Execute skill updates."""

    BACKUP_DIR = Path.home() / ".claude" / "skill-backups"

    def execute(
        self,
        analysis: UpdateAnalysis,
        action: UpdateAction,
        new_content: dict[str, str]
    ) -> UpdateResult:
        """Execute the update action."""
        if action == UpdateAction.SKIP:
            return UpdateResult(
                action_taken=action,
                success=True,
                files_preserved=list(analysis.existing_path.rglob("*"))
            )

        if action == UpdateAction.UPDATE_BACKUP:
            return self._update_with_backup(analysis, new_content)

        if action == UpdateAction.UPDATE_IN_PLACE:
            return self._update_in_place(analysis, new_content)

        if action == UpdateAction.MERGE:
            return self._merge_update(analysis, new_content)

        if action == UpdateAction.SIDE_BY_SIDE:
            return self._side_by_side(analysis, new_content)

        return UpdateResult(
            action_taken=action,
            success=False,
            error=f"Unknown action: {action}"
        )

    def _update_with_backup(
        self,
        analysis: UpdateAnalysis,
        new_content: dict[str, str]
    ) -> UpdateResult:
        """Update with backup of existing."""
        # Create backup
        backup_path = self._create_backup(analysis.existing_path)

        # Perform update
        result = self._update_in_place(analysis, new_content)
        result.backup_path = backup_path

        return result

    def _update_in_place(
        self,
        analysis: UpdateAnalysis,
        new_content: dict[str, str]
    ) -> UpdateResult:
        """Replace existing files."""
        updated = []
        preserved = []

        try:
            for rel_path, content in new_content.items():
                file_path = analysis.existing_path / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                updated.append(file_path)

            # Update metadata
            self._update_metadata(
                analysis.existing_path,
                analysis.comparison.new_version,
                new_content
            )

            return UpdateResult(
                action_taken=UpdateAction.UPDATE_IN_PLACE,
                success=True,
                files_updated=updated,
                files_preserved=preserved
            )

        except Exception as e:
            return UpdateResult(
                action_taken=UpdateAction.UPDATE_IN_PLACE,
                success=False,
                error=str(e)
            )

    def _merge_update(
        self,
        analysis: UpdateAnalysis,
        new_content: dict[str, str]
    ) -> UpdateResult:
        """Merge new content with existing, preserving modifications."""
        updated = []
        preserved = []

        for change in analysis.file_changes:
            rel_path = str(change.path)
            file_path = analysis.existing_path / change.path

            if change.is_user_modified:
                # Preserve user modifications
                preserved.append(file_path)
                continue

            if rel_path in new_content:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(new_content[rel_path])
                updated.append(file_path)

        return UpdateResult(
            action_taken=UpdateAction.MERGE,
            success=True,
            files_updated=updated,
            files_preserved=preserved
        )

    def _side_by_side(
        self,
        analysis: UpdateAnalysis,
        new_content: dict[str, str]
    ) -> UpdateResult:
        """Install as new version alongside existing."""
        # Create versioned path
        new_path = analysis.existing_path.parent / (
            f"{analysis.skill_name}-{analysis.comparison.new_version}"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        updated = []
        for rel_path, content in new_content.items():
            file_path = new_path / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            updated.append(file_path)

        return UpdateResult(
            action_taken=UpdateAction.SIDE_BY_SIDE,
            success=True,
            files_updated=updated
        )

    def _create_backup(self, skill_path: Path) -> Path:
        """Create backup of existing skill."""
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{skill_path.name}_{timestamp}"
        backup_path = self.BACKUP_DIR / backup_name

        shutil.copytree(skill_path, backup_path)
        return backup_path

    def _update_metadata(
        self,
        skill_path: Path,
        version: str,
        content: dict[str, str]
    ) -> None:
        """Update skill metadata file."""
        meta = {
            "version": version,
            "updated_at": datetime.now().isoformat(),
            "original_hashes": {
                path: hashlib.sha256(c.encode()).hexdigest()[:16]
                for path, c in content.items()
            }
        }
        meta_path = skill_path / ".skill-meta.json"
        meta_path.write_text(json.dumps(meta, indent=2))
```

## Update Formatter

```python
class UpdateFormatter:
    """Format update information for display."""

    def format_analysis(self, analysis: UpdateAnalysis) -> str:
        """Format update analysis."""
        lines = []

        lines.append("")
        lines.append("  EXISTING SKILL DETECTED")
        lines.append("  ───────────────────────")
        lines.append(f"  Skill: {analysis.skill_name}")
        lines.append(f"  Location: {analysis.existing_path}")
        lines.append("")
        lines.append("  Version Comparison:")
        lines.append(f"    Installed: v{analysis.comparison.existing_version}")
        lines.append(f"    Available: v{analysis.comparison.new_version}")

        if analysis.comparison.is_newer:
            lines.append("    Status: ⬆ Update available")
        else:
            lines.append("    Status: ✓ Up to date")

        # File changes summary
        added = sum(1 for c in analysis.file_changes
                   if c.category == ChangeCategory.ADDED)
        modified = sum(1 for c in analysis.file_changes
                      if c.category == ChangeCategory.MODIFIED)
        removed = sum(1 for c in analysis.file_changes
                     if c.category == ChangeCategory.REMOVED)

        if added or modified or removed:
            lines.append("")
            lines.append("  Changes:")
            if added:
                lines.append(f"    + {added} file(s) to add")
            if modified:
                lines.append(f"    ~ {modified} file(s) to update")
            if removed:
                lines.append(f"    - {removed} file(s) to remove")

        # Warnings
        if analysis.warnings:
            lines.append("")
            lines.append("  ⚠ Warnings:")
            for warn in analysis.warnings:
                lines.append(f"    • {warn}")

        lines.append("")
        return "\n".join(lines)

    def format_options(self, analysis: UpdateAnalysis) -> str:
        """Format update options."""
        lines = []

        lines.append("  UPDATE OPTIONS")
        lines.append("  ──────────────")

        rec = analysis.recommended_action

        options = [
            (UpdateAction.UPDATE_IN_PLACE, "Update in place",
             "Replace existing files with new version"),
            (UpdateAction.UPDATE_BACKUP, "Update with backup",
             "Backup existing, then update"),
            (UpdateAction.MERGE, "Merge changes",
             "Update only unmodified files"),
            (UpdateAction.SKIP, "Skip update",
             "Keep existing installation"),
        ]

        for action, label, desc in options:
            marker = " (recommended)" if action == rec else ""
            lines.append(f"  • {label}{marker}")
            lines.append(f"    {desc}")

        lines.append("")
        return "\n".join(lines)

    def format_result(self, result: UpdateResult) -> str:
        """Format update result."""
        lines = []

        if result.success:
            lines.append(f"  ✓ {result.action_taken.value} completed")

            if result.files_updated:
                lines.append(f"    Updated: {len(result.files_updated)} file(s)")
            if result.files_preserved:
                lines.append(f"    Preserved: {len(result.files_preserved)} file(s)")
            if result.backup_path:
                lines.append(f"    Backup: {result.backup_path}")
        else:
            lines.append(f"  ✗ Update failed: {result.error}")

        return "\n".join(lines)
```

## Integration

```python
def check_and_update(
    skill_name: str,
    new_content: dict[str, str],
    new_version: str
) -> UpdateResult | None:
    """Check for existing skill and offer update."""
    detector = ExistingSkillDetector(skill_name)
    analyzer = UpdateAnalyzer(detector)
    executor = UpdateExecutor()
    formatter = UpdateFormatter()

    # Find existing installations
    existing = detector.find_existing()

    if not existing:
        return None  # Fresh install

    # Analyze first installation
    analysis = analyzer.analyze(existing[0], new_content, new_version)

    # Display analysis
    print(formatter.format_analysis(analysis))
    print(formatter.format_options(analysis))

    # Would prompt user here - using recommended action
    action = analysis.recommended_action

    # Execute update
    result = executor.execute(analysis, action, new_content)

    print(formatter.format_result(result))
    return result
```

## Sample Output

```
  EXISTING SKILL DETECTED
  ───────────────────────
  Skill: api-doc-generator
  Location: /home/user/.claude/skills/api-doc-generator

  Version Comparison:
    Installed: v1.2.0
    Available: v1.3.0
    Status: ⬆ Update available

  Changes:
    + 1 file(s) to add
    ~ 2 file(s) to update

  ⚠ Warnings:
    • 1 file(s) have local modifications

  UPDATE OPTIONS
  ──────────────
  • Update in place
    Replace existing files with new version
  • Update with backup (recommended)
    Backup existing, then update
  • Merge changes
    Update only unmodified files
  • Skip update
    Keep existing installation

  ✓ backup_update completed
    Updated: 3 file(s)
    Preserved: 1 file(s)
    Backup: /home/user/.claude/skill-backups/api-doc-generator_20240115_143022
```
