# Reference Update Strategy

Manage versioning, dating, and update tracking for reference files.

## Update Strategy Goals

| Goal | Description |
|------|-------------|
| Version tracking | Track reference file versions |
| Date stamping | Record creation and update dates |
| Change detection | Identify when updates needed |
| Migration support | Handle breaking changes gracefully |

## Update Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

class UpdateFrequency(Enum):
    STATIC = "static"          # Rarely changes
    PERIODIC = "periodic"      # Regular updates
    DYNAMIC = "dynamic"        # Frequently updated
    ON_DEMAND = "on_demand"    # Updated when requested

class ChangeType(Enum):
    PATCH = "patch"            # Bug fixes, typos
    MINOR = "minor"            # New content, clarifications
    MAJOR = "major"            # Breaking changes, restructure

class UpdateStatus(Enum):
    CURRENT = "current"        # Up to date
    STALE = "stale"            # Needs review
    OUTDATED = "outdated"      # Needs update
    DEPRECATED = "deprecated"  # Scheduled for removal

@dataclass
class VersionInfo:
    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, change_type: ChangeType) -> "VersionInfo":
        if change_type == ChangeType.MAJOR:
            return VersionInfo(self.major + 1, 0, 0)
        elif change_type == ChangeType.MINOR:
            return VersionInfo(self.major, self.minor + 1, 0)
        else:
            return VersionInfo(self.major, self.minor, self.patch + 1)

@dataclass
class ReferenceMetadata:
    file_path: Path
    version: VersionInfo
    created_at: datetime
    updated_at: datetime
    update_frequency: UpdateFrequency
    status: UpdateStatus
    checksum: str
    changelog: list[str] = field(default_factory=list)

@dataclass
class UpdatePlan:
    reference: ReferenceMetadata
    change_type: ChangeType
    reason: str
    new_version: VersionInfo
    breaking_changes: list[str] = field(default_factory=list)
    migration_notes: str | None = None
```

## Version Manager

```python
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class VersionManager:
    """Manage reference file versions."""

    METADATA_FILE = ".reference-versions.json"

    # Staleness thresholds by frequency
    STALE_THRESHOLDS = {
        UpdateFrequency.STATIC: timedelta(days=365),
        UpdateFrequency.PERIODIC: timedelta(days=30),
        UpdateFrequency.DYNAMIC: timedelta(days=7),
        UpdateFrequency.ON_DEMAND: timedelta(days=90),
    }

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.metadata_path = skill_path / self.METADATA_FILE
        self.references: dict[str, ReferenceMetadata] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load existing metadata."""
        if self.metadata_path.exists():
            data = json.loads(self.metadata_path.read_text())
            for path, meta in data.items():
                self.references[path] = ReferenceMetadata(
                    file_path=Path(path),
                    version=VersionInfo(**meta["version"]),
                    created_at=datetime.fromisoformat(meta["created_at"]),
                    updated_at=datetime.fromisoformat(meta["updated_at"]),
                    update_frequency=UpdateFrequency(meta["update_frequency"]),
                    status=UpdateStatus(meta["status"]),
                    checksum=meta["checksum"],
                    changelog=meta.get("changelog", [])
                )

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        data = {}
        for path, meta in self.references.items():
            data[path] = {
                "version": {
                    "major": meta.version.major,
                    "minor": meta.version.minor,
                    "patch": meta.version.patch
                },
                "created_at": meta.created_at.isoformat(),
                "updated_at": meta.updated_at.isoformat(),
                "update_frequency": meta.update_frequency.value,
                "status": meta.status.value,
                "checksum": meta.checksum,
                "changelog": meta.changelog
            }
        self.metadata_path.write_text(json.dumps(data, indent=2))

    def register_reference(
        self,
        file_path: Path,
        frequency: UpdateFrequency = UpdateFrequency.STATIC
    ) -> ReferenceMetadata:
        """Register a new reference file."""
        content = file_path.read_text()
        checksum = self._compute_checksum(content)
        now = datetime.now()

        metadata = ReferenceMetadata(
            file_path=file_path,
            version=VersionInfo(1, 0, 0),
            created_at=now,
            updated_at=now,
            update_frequency=frequency,
            status=UpdateStatus.CURRENT,
            checksum=checksum,
            changelog=["Initial version"]
        )

        rel_path = str(file_path.relative_to(self.skill_path))
        self.references[rel_path] = metadata
        self._save_metadata()

        return metadata

    def check_status(self, file_path: Path) -> UpdateStatus:
        """Check current status of a reference."""
        rel_path = str(file_path.relative_to(self.skill_path))

        if rel_path not in self.references:
            return UpdateStatus.CURRENT  # Not tracked

        meta = self.references[rel_path]

        # Check if content changed
        if file_path.exists():
            current_checksum = self._compute_checksum(file_path.read_text())
            if current_checksum != meta.checksum:
                return UpdateStatus.OUTDATED

        # Check staleness
        threshold = self.STALE_THRESHOLDS.get(
            meta.update_frequency,
            timedelta(days=90)
        )
        age = datetime.now() - meta.updated_at

        if age > threshold * 2:
            return UpdateStatus.OUTDATED
        elif age > threshold:
            return UpdateStatus.STALE

        return UpdateStatus.CURRENT

    def record_update(
        self,
        file_path: Path,
        change_type: ChangeType,
        change_description: str
    ) -> ReferenceMetadata:
        """Record an update to a reference."""
        rel_path = str(file_path.relative_to(self.skill_path))

        if rel_path not in self.references:
            return self.register_reference(file_path)

        meta = self.references[rel_path]

        # Update version
        meta.version = meta.version.bump(change_type)
        meta.updated_at = datetime.now()
        meta.status = UpdateStatus.CURRENT

        # Update checksum
        if file_path.exists():
            meta.checksum = self._compute_checksum(file_path.read_text())

        # Add to changelog
        entry = f"v{meta.version}: {change_description}"
        meta.changelog.append(entry)

        # Keep last 10 entries
        meta.changelog = meta.changelog[-10:]

        self._save_metadata()
        return meta

    def get_all_status(self) -> dict[str, UpdateStatus]:
        """Get status of all tracked references."""
        status = {}
        for rel_path in self.references:
            full_path = self.skill_path / rel_path
            status[rel_path] = self.check_status(full_path)
        return status

    def _compute_checksum(self, content: str) -> str:
        """Compute SHA-256 checksum of content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
```

## Update Detector

```python
class UpdateDetector:
    """Detect when references need updating."""

    def __init__(self, version_manager: VersionManager):
        self.manager = version_manager

    def detect_needed_updates(self) -> list[UpdatePlan]:
        """Detect all references needing updates."""
        plans = []

        for rel_path, meta in self.manager.references.items():
            full_path = self.manager.skill_path / rel_path
            status = self.manager.check_status(full_path)

            if status in (UpdateStatus.STALE, UpdateStatus.OUTDATED):
                plan = self._create_update_plan(meta, status)
                if plan:
                    plans.append(plan)

        return plans

    def _create_update_plan(
        self,
        meta: ReferenceMetadata,
        status: UpdateStatus
    ) -> UpdatePlan | None:
        """Create update plan for a reference."""
        if status == UpdateStatus.STALE:
            return UpdatePlan(
                reference=meta,
                change_type=ChangeType.PATCH,
                reason="Reference is stale and needs review",
                new_version=meta.version.bump(ChangeType.PATCH)
            )
        elif status == UpdateStatus.OUTDATED:
            return UpdatePlan(
                reference=meta,
                change_type=ChangeType.MINOR,
                reason="Reference content has changed",
                new_version=meta.version.bump(ChangeType.MINOR)
            )
        return None

    def check_breaking_changes(
        self,
        old_content: str,
        new_content: str
    ) -> list[str]:
        """Check for breaking changes between versions."""
        breaking = []

        # Check for removed sections
        old_sections = self._extract_sections(old_content)
        new_sections = self._extract_sections(new_content)

        removed = old_sections - new_sections
        for section in removed:
            breaking.append(f"Section removed: {section}")

        # Check for renamed sections
        # (simplified - would need more sophisticated matching)

        return breaking

    def _extract_sections(self, content: str) -> set[str]:
        """Extract markdown section headings."""
        import re
        sections = set()
        for match in re.finditer(r'^#{1,3}\s+(.+)$', content, re.MULTILINE):
            sections.add(match.group(1).strip())
        return sections
```

## Version Header Generator

```python
class VersionHeaderGenerator:
    """Generate version/date headers for references."""

    HEADER_TEMPLATE = """---
version: {version}
created: {created}
updated: {updated}
status: {status}
---

"""

    FOOTER_TEMPLATE = """
---

*Version {version} | Updated {updated}*
"""

    def generate_header(self, meta: ReferenceMetadata) -> str:
        """Generate YAML frontmatter with version info."""
        return self.HEADER_TEMPLATE.format(
            version=str(meta.version),
            created=meta.created_at.strftime("%Y-%m-%d"),
            updated=meta.updated_at.strftime("%Y-%m-%d"),
            status=meta.status.value
        )

    def generate_footer(self, meta: ReferenceMetadata) -> str:
        """Generate version footer."""
        return self.FOOTER_TEMPLATE.format(
            version=str(meta.version),
            updated=meta.updated_at.strftime("%Y-%m-%d")
        )

    def inject_version_info(
        self,
        content: str,
        meta: ReferenceMetadata,
        include_header: bool = True,
        include_footer: bool = True
    ) -> str:
        """Inject version information into content."""
        result = content

        # Check if already has frontmatter
        if content.startswith("---"):
            # Update existing frontmatter
            parts = content.split("---", 2)
            if len(parts) >= 3:
                # Parse and update YAML
                result = self._update_frontmatter(content, meta)
        elif include_header:
            result = self.generate_header(meta) + content

        if include_footer:
            result = result.rstrip() + self.generate_footer(meta)

        return result

    def _update_frontmatter(
        self,
        content: str,
        meta: ReferenceMetadata
    ) -> str:
        """Update existing frontmatter."""
        import re

        def replace_field(match):
            return f"version: {meta.version}"

        content = re.sub(
            r'^version:\s*.*$',
            f'version: {meta.version}',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^updated:\s*.*$',
            f'updated: {meta.updated_at.strftime("%Y-%m-%d")}',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^status:\s*.*$',
            f'status: {meta.status.value}',
            content,
            flags=re.MULTILINE
        )

        return content
```

## Update Formatter

```python
class UpdateFormatter:
    """Format update information for display."""

    def format_status_report(
        self,
        manager: VersionManager
    ) -> str:
        """Format status report for all references."""
        lines = []
        lines.append("")
        lines.append("  REFERENCE STATUS")
        lines.append("  ────────────────")
        lines.append("")

        status_map = manager.get_all_status()

        for rel_path, status in sorted(status_map.items()):
            meta = manager.references.get(rel_path)
            icon = self._status_icon(status)
            version = f"v{meta.version}" if meta else "?"

            lines.append(f"  {icon} {rel_path}")
            lines.append(f"      Version: {version} | Status: {status.value}")

        lines.append("")
        return "\n".join(lines)

    def format_update_plan(self, plan: UpdatePlan) -> str:
        """Format a single update plan."""
        lines = []

        lines.append(f"  📝 {plan.reference.file_path.name}")
        lines.append(f"     Current: v{plan.reference.version}")
        lines.append(f"     Planned: v{plan.new_version}")
        lines.append(f"     Type: {plan.change_type.value}")
        lines.append(f"     Reason: {plan.reason}")

        if plan.breaking_changes:
            lines.append("     ⚠ Breaking changes:")
            for bc in plan.breaking_changes:
                lines.append(f"       • {bc}")

        if plan.migration_notes:
            lines.append(f"     Migration: {plan.migration_notes}")

        return "\n".join(lines)

    def format_changelog(self, meta: ReferenceMetadata) -> str:
        """Format changelog for a reference."""
        lines = []
        lines.append(f"  CHANGELOG: {meta.file_path.name}")
        lines.append("  " + "─" * 40)

        for entry in reversed(meta.changelog):
            lines.append(f"  • {entry}")

        return "\n".join(lines)

    def _status_icon(self, status: UpdateStatus) -> str:
        """Get icon for status."""
        icons = {
            UpdateStatus.CURRENT: "✓",
            UpdateStatus.STALE: "○",
            UpdateStatus.OUTDATED: "⚠",
            UpdateStatus.DEPRECATED: "✗",
        }
        return icons.get(status, "?")
```

## Integration

```python
def manage_reference_versions(skill_path: Path) -> None:
    """Manage versions for all references in a skill."""
    manager = VersionManager(skill_path)
    detector = UpdateDetector(manager)
    formatter = UpdateFormatter()

    # Show current status
    print(formatter.format_status_report(manager))

    # Detect needed updates
    plans = detector.detect_needed_updates()

    if plans:
        print("  UPDATES NEEDED")
        print("  ──────────────")
        for plan in plans:
            print(formatter.format_update_plan(plan))
            print()
    else:
        print("  ✓ All references up to date")
```

## Sample Output

```
  REFERENCE STATUS
  ────────────────

  ✓ references/overview.md
      Version: v1.2.0 | Status: current
  ○ references/workflow.md
      Version: v1.0.0 | Status: stale
  ⚠ references/api.md
      Version: v1.1.0 | Status: outdated

  UPDATES NEEDED
  ──────────────
  📝 workflow.md
     Current: v1.0.0
     Planned: v1.0.1
     Type: patch
     Reason: Reference is stale and needs review

  📝 api.md
     Current: v1.1.0
     Planned: v1.2.0
     Type: minor
     Reason: Reference content has changed
```
