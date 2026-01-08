# Installation Path Selection

Allow users to choose installation location with validation.

## Path Options

| Option | Path | Scope |
|--------|------|-------|
| User | `~/.claude/skills/<name>/` | All projects |
| Project | `./.claude/skills/<name>/` | Current project only |
| Custom | User-specified path | Custom scope |

## Path Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class PathScope(Enum):
    USER = "user"       # Global user skills
    PROJECT = "project" # Project-specific skills
    CUSTOM = "custom"   # User-defined location

@dataclass
class InstallPath:
    scope: PathScope
    base_path: Path
    skill_path: Path
    exists: bool
    writable: bool
    conflicts: list[str]

@dataclass
class PathChoice:
    selected_scope: PathScope
    install_path: Path
    create_parents: bool
    backup_existing: bool
```

## Path Selection Flow

```python
class PathSelector:
    """Guide user through path selection."""

    DEFAULT_PATHS = {
        PathScope.USER: Path.home() / ".claude" / "skills",
        PathScope.PROJECT: Path.cwd() / ".claude" / "skills",
    }

    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    def select(self) -> PathChoice:
        """Run path selection flow."""
        # Analyze available options
        options = self._analyze_options()

        # Display options
        self._display_options(options)

        # Get user choice
        choice = self._get_choice(options)

        return choice

    def _analyze_options(self) -> list[InstallPath]:
        """Analyze available installation paths."""
        options = []

        for scope, base in self.DEFAULT_PATHS.items():
            skill_path = base / self.skill_name
            options.append(InstallPath(
                scope=scope,
                base_path=base,
                skill_path=skill_path,
                exists=skill_path.exists(),
                writable=self._check_writable(base),
                conflicts=self._find_conflicts(skill_path)
            ))

        return options

    def _check_writable(self, path: Path) -> bool:
        """Check if path is writable."""
        try:
            test_path = path
            while not test_path.exists():
                test_path = test_path.parent

            # Try creating test file
            test_file = test_path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False

    def _find_conflicts(self, path: Path) -> list[str]:
        """Find existing files that would be overwritten."""
        if not path.exists():
            return []

        conflicts = []
        for item in path.rglob("*"):
            if item.is_file():
                conflicts.append(str(item.relative_to(path)))

        return conflicts

    def _display_options(self, options: list[InstallPath]) -> None:
        """Display path options to user."""
        print()
        print("═" * 60)
        print("  WHERE SHOULD THE SKILL BE INSTALLED?")
        print("═" * 60)
        print()

        for i, opt in enumerate(options, 1):
            scope_name = opt.scope.value.title()
            status = self._get_status(opt)

            print(f"  [{i}] {scope_name} Skills")
            print(f"      Path: {opt.skill_path}")
            print(f"      {status}")
            print()

        print("  [3] Custom Path")
        print("      Specify a custom installation directory")
        print()

    def _get_status(self, opt: InstallPath) -> str:
        """Get status string for option."""
        if not opt.writable:
            return "⚠ Not writable"
        if opt.conflicts:
            return f"⚠ {len(opt.conflicts)} existing files"
        if opt.exists:
            return "○ Directory exists (empty)"
        return "✓ Ready to install"

    def _get_choice(self, options: list[InstallPath]) -> PathChoice:
        """Get user's path choice."""
        while True:
            choice = input("  Select option [1-3]: ").strip()

            if choice == "1":
                return self._finalize_choice(options[0])
            elif choice == "2":
                return self._finalize_choice(options[1])
            elif choice == "3":
                return self._handle_custom()
            else:
                print("  Invalid choice. Please enter 1-3.")

    def _handle_custom(self) -> PathChoice:
        """Handle custom path input."""
        print()
        path_str = input("  Enter custom path: ").strip()
        path = Path(path_str).expanduser().resolve()

        if not path_str:
            print("  Path cannot be empty.")
            return self._handle_custom()

        skill_path = path / self.skill_name

        # Validate
        opt = InstallPath(
            scope=PathScope.CUSTOM,
            base_path=path,
            skill_path=skill_path,
            exists=skill_path.exists(),
            writable=self._check_writable(path),
            conflicts=self._find_conflicts(skill_path)
        )

        if not opt.writable:
            print(f"  ⚠ Cannot write to: {path}")
            retry = input("  Try another path? [Y/n]: ").strip().lower()
            if retry in ("", "y", "yes"):
                return self._handle_custom()
            raise SystemExit(1)

        return self._finalize_choice(opt)

    def _finalize_choice(self, opt: InstallPath) -> PathChoice:
        """Finalize path choice with options."""
        create_parents = False
        backup_existing = False

        # Check if we need to create parent directories
        if not opt.base_path.exists():
            print()
            print(f"  Directory will be created: {opt.base_path}")
            confirm = input("  Proceed? [Y/n]: ").strip().lower()
            if confirm not in ("", "y", "yes"):
                raise SystemExit(1)
            create_parents = True

        # Check for conflicts
        if opt.conflicts:
            print()
            print(f"  ⚠ {len(opt.conflicts)} existing files will be affected:")
            for f in opt.conflicts[:5]:
                print(f"      - {f}")
            if len(opt.conflicts) > 5:
                print(f"      ... and {len(opt.conflicts) - 5} more")

            print()
            print("    [1] Overwrite existing files")
            print("    [2] Create backup first")
            print("    [3] Cancel")
            print()

            choice = input("  Select option [1-3]: ").strip()
            if choice == "1":
                backup_existing = False
            elif choice == "2":
                backup_existing = True
            else:
                raise SystemExit(1)

        return PathChoice(
            selected_scope=opt.scope,
            install_path=opt.skill_path,
            create_parents=create_parents,
            backup_existing=backup_existing
        )
```

## Path Validation

```python
from dataclasses import dataclass

@dataclass
class PathValidation:
    valid: bool
    errors: list[str]
    warnings: list[str]

class PathValidator:
    """Validate installation paths."""

    RESERVED_NAMES = {"system", "core", "internal", "claude"}
    MAX_PATH_LENGTH = 255

    def validate(self, path: Path, skill_name: str) -> PathValidation:
        """Validate installation path."""
        errors = []
        warnings = []

        # Check path length
        if len(str(path)) > self.MAX_PATH_LENGTH:
            errors.append(f"Path exceeds {self.MAX_PATH_LENGTH} characters")

        # Check reserved names
        if skill_name.lower() in self.RESERVED_NAMES:
            errors.append(f"Skill name '{skill_name}' is reserved")

        # Check path characters
        invalid_chars = set('<>:"|?*')
        path_str = str(path)
        for char in invalid_chars:
            if char in path_str:
                errors.append(f"Path contains invalid character: {char}")

        # Check if inside restricted directories
        restricted = [Path("/usr"), Path("/bin"), Path("/etc")]
        for r in restricted:
            try:
                path.relative_to(r)
                errors.append(f"Cannot install to system directory: {r}")
            except ValueError:
                pass

        # Warnings
        if not str(path).startswith(str(Path.home())):
            warnings.append("Installing outside home directory")

        if ".claude" not in path.parts:
            warnings.append("Installing outside .claude directory")

        return PathValidation(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

## Backup Management

```python
from datetime import datetime
import shutil

class BackupManager:
    """Manage backups of existing installations."""

    BACKUP_SUFFIX = ".backup"

    def create_backup(self, path: Path) -> Path | None:
        """Create backup of existing installation."""
        if not path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.parent / f"{path.name}{self.BACKUP_SUFFIX}.{timestamp}"

        shutil.copytree(path, backup_path)
        return backup_path

    def list_backups(self, skill_name: str, base_path: Path) -> list[Path]:
        """List available backups for a skill."""
        pattern = f"{skill_name}{self.BACKUP_SUFFIX}.*"
        return sorted(base_path.glob(pattern), reverse=True)

    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore from backup."""
        if not backup_path.exists():
            return False

        if target_path.exists():
            shutil.rmtree(target_path)

        shutil.copytree(backup_path, target_path)
        return True

    def cleanup_old_backups(self, skill_name: str, base_path: Path, keep: int = 3) -> int:
        """Remove old backups, keeping the most recent."""
        backups = self.list_backups(skill_name, base_path)

        removed = 0
        for backup in backups[keep:]:
            shutil.rmtree(backup)
            removed += 1

        return removed
```

## Integration with AskUserQuestion

```python
def select_installation_path(skill_name: str) -> PathChoice:
    """Select installation path using interactive flow."""
    selector = PathSelector(skill_name)

    # Display current state
    print()
    print(f"  Installing skill: {skill_name}")

    # Run selection
    choice = selector.select()

    # Validate
    validator = PathValidator()
    validation = validator.validate(choice.install_path, skill_name)

    if not validation.valid:
        print()
        print("  ✗ Path validation failed:")
        for err in validation.errors:
            print(f"    - {err}")
        raise SystemExit(1)

    if validation.warnings:
        print()
        print("  ⚠ Warnings:")
        for warn in validation.warnings:
            print(f"    - {warn}")
        print()
        proceed = input("  Continue anyway? [y/N]: ").strip().lower()
        if proceed not in ("y", "yes"):
            raise SystemExit(1)

    return choice
```

## Path Display Format

```
═══════════════════════════════════════════════════════════
  WHERE SHOULD THE SKILL BE INSTALLED?
═══════════════════════════════════════════════════════════

  [1] User Skills
      Path: ~/.claude/skills/api-doc-generator
      ✓ Ready to install

  [2] Project Skills
      Path: ./.claude/skills/api-doc-generator
      ○ Directory exists (empty)

  [3] Custom Path
      Specify a custom installation directory

  Select option [1-3]:
```
