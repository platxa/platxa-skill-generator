# Installation Confirmation Flow

Confirm installation details with user before writing files.

## Confirmation Display

```
═══════════════════════════════════════════════════════════════
  READY TO INSTALL: api-doc-generator
═══════════════════════════════════════════════════════════════

  Installation Path:
    ~/.claude/skills/api-doc-generator/

  Files to Create:
    ✓ SKILL.md                    (1.2 KB)
    ✓ references/overview.md      (2.4 KB)
    ✓ references/workflow.md      (3.1 KB)
    ✓ references/api.md           (2.8 KB)
    ✓ scripts/generate.sh         (1.5 KB)

  Total: 5 files, 11.0 KB

───────────────────────────────────────────────────────────────
  Quality Score: 8.2/10 ████████░░ PASSED
───────────────────────────────────────────────────────────────

  Proceed with installation? [Y/n]:
```

## Confirmation Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class InstallLocation(Enum):
    USER = "user"       # ~/.claude/skills/
    PROJECT = "project" # ./.claude/skills/
    CUSTOM = "custom"   # User-specified path

class ConflictResolution(Enum):
    SKIP = "skip"
    OVERWRITE = "overwrite"
    BACKUP = "backup"
    MERGE = "merge"

@dataclass
class FileToInstall:
    relative_path: str
    size_bytes: int
    exists: bool
    will_overwrite: bool

@dataclass
class InstallationPlan:
    skill_name: str
    location: InstallLocation
    install_path: Path
    files: list[FileToInstall]
    total_size: int
    quality_score: float | None
    conflicts: list[str]
    warnings: list[str]

@dataclass
class InstallationConfirmation:
    approved: bool
    location: InstallLocation
    conflict_resolution: ConflictResolution
    create_backup: bool
```

## Confirmation Flow

```python
class InstallConfirmationFlow:
    """Guide user through installation confirmation."""

    def __init__(self, plan: InstallationPlan):
        self.plan = plan

    def run(self) -> InstallationConfirmation:
        """Run confirmation flow."""
        # Display plan
        self._display_plan()

        # Handle conflicts if any
        resolution = ConflictResolution.SKIP
        if self.plan.conflicts:
            resolution = self._handle_conflicts()
            if resolution == ConflictResolution.SKIP:
                return InstallationConfirmation(
                    approved=False,
                    location=self.plan.location,
                    conflict_resolution=resolution,
                    create_backup=False
                )

        # Ask for final confirmation
        approved = self._ask_confirmation()

        # Ask about backup
        create_backup = False
        if approved and self.plan.conflicts:
            create_backup = self._ask_backup()

        return InstallationConfirmation(
            approved=approved,
            location=self.plan.location,
            conflict_resolution=resolution,
            create_backup=create_backup
        )

    def _display_plan(self) -> None:
        """Display installation plan."""
        width = 65
        print("═" * width)
        print(f"  READY TO INSTALL: {self.plan.skill_name}")
        print("═" * width)
        print()

        # Installation path
        print("  Installation Path:")
        print(f"    {self.plan.install_path}/")
        print()

        # Files
        print("  Files to Create:")
        for f in self.plan.files:
            status = "⚠" if f.will_overwrite else "✓"
            size = self._format_size(f.size_bytes)
            print(f"    {status} {f.relative_path:30} ({size})")
        print()

        # Totals
        total_size = self._format_size(self.plan.total_size)
        print(f"  Total: {len(self.plan.files)} files, {total_size}")
        print()

        # Quality score
        if self.plan.quality_score:
            print("─" * width)
            bar = self._score_bar(self.plan.quality_score)
            status = "PASSED" if self.plan.quality_score >= 7.0 else "REVIEW"
            print(f"  Quality Score: {self.plan.quality_score:.1f}/10 {bar} {status}")
            print("─" * width)
            print()

        # Warnings
        if self.plan.warnings:
            print("  ⚠ Warnings:")
            for warn in self.plan.warnings:
                print(f"    - {warn}")
            print()

        # Conflicts
        if self.plan.conflicts:
            print("  ⚠ Existing files will be affected:")
            for conflict in self.plan.conflicts:
                print(f"    - {conflict}")
            print()

    def _format_size(self, bytes: int) -> str:
        if bytes < 1024:
            return f"{bytes} B"
        elif bytes < 1024 * 1024:
            return f"{bytes / 1024:.1f} KB"
        else:
            return f"{bytes / (1024 * 1024):.1f} MB"

    def _score_bar(self, score: float, width: int = 10) -> str:
        filled = int(score / 10 * width)
        return "█" * filled + "░" * (width - filled)

    def _handle_conflicts(self) -> ConflictResolution:
        """Handle file conflicts."""
        print("  How should existing files be handled?")
        print()
        print("    [1] Overwrite existing files")
        print("    [2] Create backup before overwriting")
        print("    [3] Skip conflicting files")
        print("    [4] Cancel installation")
        print()

        while True:
            choice = input("  Select option [1-4]: ").strip()
            if choice == "1":
                return ConflictResolution.OVERWRITE
            elif choice == "2":
                return ConflictResolution.BACKUP
            elif choice == "3":
                return ConflictResolution.SKIP
            elif choice == "4":
                return ConflictResolution.SKIP
            else:
                print("  Invalid choice. Please enter 1-4.")

    def _ask_confirmation(self) -> bool:
        """Ask for final confirmation."""
        response = input("  Proceed with installation? [Y/n]: ").strip().lower()
        return response in ("", "y", "yes")

    def _ask_backup(self) -> bool:
        """Ask about creating backup."""
        response = input("  Create backup of existing files? [Y/n]: ").strip().lower()
        return response in ("", "y", "yes")
```

## Location Selection

```python
class LocationSelector:
    """Select installation location."""

    LOCATIONS = {
        InstallLocation.USER: Path.home() / ".claude" / "skills",
        InstallLocation.PROJECT: Path.cwd() / ".claude" / "skills",
    }

    def select(self, skill_name: str) -> tuple[InstallLocation, Path]:
        """Select installation location."""
        print()
        print("  Where should the skill be installed?")
        print()
        print(f"    [1] User skills   (~/.claude/skills/{skill_name}/)")
        print(f"    [2] Project skills (./.claude/skills/{skill_name}/)")
        print("    [3] Custom path")
        print()

        while True:
            choice = input("  Select location [1-3]: ").strip()

            if choice == "1":
                path = self.LOCATIONS[InstallLocation.USER] / skill_name
                return InstallLocation.USER, path

            elif choice == "2":
                path = self.LOCATIONS[InstallLocation.PROJECT] / skill_name
                return InstallLocation.PROJECT, path

            elif choice == "3":
                custom = input("  Enter custom path: ").strip()
                path = Path(custom).expanduser().resolve()
                return InstallLocation.CUSTOM, path

            else:
                print("  Invalid choice. Please enter 1-3.")

    def validate_path(self, path: Path) -> list[str]:
        """Validate installation path."""
        warnings = []

        # Check if parent exists
        if not path.parent.exists():
            warnings.append(f"Parent directory will be created: {path.parent}")

        # Check permissions
        try:
            test_path = path.parent if path.parent.exists() else path.parent.parent
            if not test_path.exists():
                test_path = Path.home()
            (test_path / ".write_test").touch()
            (test_path / ".write_test").unlink()
        except PermissionError:
            warnings.append(f"May not have write permission to: {path.parent}")

        # Check if path already exists
        if path.exists():
            warnings.append(f"Directory already exists: {path}")

        return warnings
```

## Conflict Detection

```python
def detect_conflicts(
    install_path: Path,
    files: dict[str, str]
) -> list[FileToInstall]:
    """Detect conflicts with existing files."""
    result = []

    for relative_path, content in files.items():
        full_path = install_path / relative_path
        exists = full_path.exists()
        will_overwrite = exists

        # Check if content is different
        if exists:
            try:
                existing = full_path.read_text()
                will_overwrite = existing != content
            except:
                will_overwrite = True

        result.append(FileToInstall(
            relative_path=relative_path,
            size_bytes=len(content.encode('utf-8')),
            exists=exists,
            will_overwrite=will_overwrite
        ))

    return result
```

## Complete Flow

```python
def confirm_installation(
    skill_name: str,
    files: dict[str, str],
    quality_score: float | None = None,
    auto_approve: bool = False
) -> InstallationConfirmation | None:
    """Run complete installation confirmation flow."""

    # Select location
    if auto_approve:
        location = InstallLocation.USER
        install_path = Path.home() / ".claude" / "skills" / skill_name
    else:
        selector = LocationSelector()
        location, install_path = selector.select(skill_name)

    # Detect conflicts
    file_list = detect_conflicts(install_path, files)
    conflicts = [f.relative_path for f in file_list if f.will_overwrite]

    # Validate path
    warnings = selector.validate_path(install_path) if not auto_approve else []

    # Build plan
    plan = InstallationPlan(
        skill_name=skill_name,
        location=location,
        install_path=install_path,
        files=file_list,
        total_size=sum(f.size_bytes for f in file_list),
        quality_score=quality_score,
        conflicts=conflicts,
        warnings=warnings
    )

    # Auto-approve path
    if auto_approve and not conflicts:
        return InstallationConfirmation(
            approved=True,
            location=location,
            conflict_resolution=ConflictResolution.SKIP,
            create_backup=False
        )

    # Run interactive confirmation
    flow = InstallConfirmationFlow(plan)
    return flow.run()
```

## Post-Installation Summary

```python
def show_installation_summary(
    skill_name: str,
    install_path: Path,
    files_installed: list[str]
) -> None:
    """Show post-installation summary."""
    print()
    print("═" * 60)
    print(f"  ✓ INSTALLED: {skill_name}")
    print("═" * 60)
    print()
    print(f"  Location: {install_path}")
    print(f"  Files: {len(files_installed)}")
    print()
    print("  To use this skill:")
    print(f"    /{skill_name}")
    print()
    print("  To view skill details:")
    print(f"    cat {install_path}/SKILL.md")
    print()
    print("═" * 60)
```
