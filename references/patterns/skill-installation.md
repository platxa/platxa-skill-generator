# Skill Installation

Install generated skills to Claude Code skill directories.

## Purpose

Copy validated skills to the appropriate location with correct permissions so they can be invoked via Claude Code CLI.

## Installation Targets

| Target | Path | Scope | Use Case |
|--------|------|-------|----------|
| User | `~/.claude/skills/{name}/` | All projects | Personal skills |
| Project | `.claude/skills/{name}/` | This project | Team/project skills |

## Installation Algorithm

```python
from pathlib import Path
import shutil
import os

def install_skill(
    source_dir: Path,
    skill_name: str,
    target: str = 'user',
    force: bool = False
) -> InstallResult:
    """
    Install skill to target location.

    Args:
        source_dir: Generated skill directory
        skill_name: Name of the skill
        target: 'user' for ~/.claude/skills/ or 'project' for .claude/skills/
        force: Overwrite if exists

    Returns:
        InstallResult with success status and path
    """
    # Determine target path
    if target == 'user':
        base_path = Path.home() / '.claude' / 'skills'
    else:
        base_path = Path.cwd() / '.claude' / 'skills'

    target_path = base_path / skill_name

    # Check if already exists
    if target_path.exists():
        if not force:
            return InstallResult(
                success=False,
                error=f"Skill '{skill_name}' already exists at {target_path}",
                suggestion="Use --force to overwrite"
            )
        # Backup existing
        backup_path = target_path.with_suffix('.backup')
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.move(target_path, backup_path)

    # Create parent directories
    base_path.mkdir(parents=True, exist_ok=True)

    # Copy skill directory
    try:
        shutil.copytree(source_dir, target_path)
    except Exception as e:
        return InstallResult(
            success=False,
            error=f"Copy failed: {e}"
        )

    # Set permissions
    set_permissions(target_path)

    # Verify installation
    if not verify_installation(target_path):
        return InstallResult(
            success=False,
            error="Verification failed after copy"
        )

    return InstallResult(
        success=True,
        path=target_path,
        message=f"Skill '{skill_name}' installed to {target_path}"
    )
```

## Permission Setting

```python
def set_permissions(skill_path: Path) -> None:
    """
    Set correct permissions on installed skill.

    - Directories: 755 (rwxr-xr-x)
    - Markdown files: 644 (rw-r--r--)
    - Scripts: 755 (rwxr-xr-x)
    """
    # Directory permissions
    for dirpath, dirnames, filenames in os.walk(skill_path):
        dir_path = Path(dirpath)
        dir_path.chmod(0o755)

        for filename in filenames:
            file_path = dir_path / filename

            if filename.endswith(('.sh', '.py')):
                # Executable scripts
                file_path.chmod(0o755)
            else:
                # Regular files (markdown, etc.)
                file_path.chmod(0o644)
```

## Installation Verification

```python
def verify_installation(skill_path: Path) -> bool:
    """
    Verify skill was installed correctly.

    Checks:
    - SKILL.md exists and readable
    - Frontmatter is valid
    - Scripts are executable
    - References are accessible
    """
    # Check SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False

    try:
        content = skill_md.read_text()
        if not content.startswith('---'):
            return False
    except Exception:
        return False

    # Check scripts are executable
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.sh'):
            if not os.access(script, os.X_OK):
                return False
        for script in scripts_dir.glob('*.py'):
            if not os.access(script, os.X_OK):
                return False

    return True
```

## User vs Project Installation

### User Installation (~/.claude/skills/)

```python
def install_user_skill(source_dir: Path, skill_name: str) -> InstallResult:
    """Install skill for current user (all projects)."""
    return install_skill(
        source_dir=source_dir,
        skill_name=skill_name,
        target='user'
    )

# Results in:
# ~/.claude/skills/api-doc-generator/
# ├── SKILL.md
# ├── scripts/
# └── references/
```

### Project Installation (.claude/skills/)

```python
def install_project_skill(source_dir: Path, skill_name: str) -> InstallResult:
    """Install skill for current project only."""
    return install_skill(
        source_dir=source_dir,
        skill_name=skill_name,
        target='project'
    )

# Results in:
# .claude/skills/api-doc-generator/
# ├── SKILL.md
# ├── scripts/
# └── references/
```

## Conflict Handling

```python
def check_conflicts(skill_name: str) -> list[str]:
    """Check for existing skills with same name."""
    conflicts = []

    user_path = Path.home() / '.claude' / 'skills' / skill_name
    if user_path.exists():
        conflicts.append(f"User skill exists: {user_path}")

    project_path = Path.cwd() / '.claude' / 'skills' / skill_name
    if project_path.exists():
        conflicts.append(f"Project skill exists: {project_path}")

    # Check commands directory too (legacy)
    commands_path = Path.home() / '.claude' / 'commands' / skill_name
    if commands_path.exists():
        conflicts.append(f"Legacy command exists: {commands_path}")

    return conflicts
```

## Rollback Support

```python
def rollback_installation(skill_path: Path) -> bool:
    """
    Rollback to previous version if backup exists.

    Args:
        skill_path: Path to installed skill

    Returns:
        True if rollback successful
    """
    backup_path = skill_path.with_suffix('.backup')

    if not backup_path.exists():
        return False

    try:
        # Remove current
        if skill_path.exists():
            shutil.rmtree(skill_path)

        # Restore backup
        shutil.move(backup_path, skill_path)
        return True

    except Exception:
        return False
```

## Installation Script

```bash
#!/bin/bash
# install-skill.sh - Install a generated skill

set -euo pipefail

SKILL_DIR="${1:?Usage: install-skill.sh <skill-dir> [user|project]}"
TARGET="${2:-user}"

SKILL_NAME=$(basename "$SKILL_DIR")

# Determine target path
if [[ "$TARGET" == "user" ]]; then
    TARGET_BASE="$HOME/.claude/skills"
elif [[ "$TARGET" == "project" ]]; then
    TARGET_BASE=".claude/skills"
else
    echo "Error: Target must be 'user' or 'project'"
    exit 1
fi

TARGET_PATH="$TARGET_BASE/$SKILL_NAME"

# Check for existing
if [[ -d "$TARGET_PATH" ]]; then
    echo "Warning: $TARGET_PATH already exists"
    read -p "Overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    # Backup
    mv "$TARGET_PATH" "${TARGET_PATH}.backup"
fi

# Create parent directory
mkdir -p "$TARGET_BASE"

# Copy skill
cp -r "$SKILL_DIR" "$TARGET_PATH"

# Set permissions
find "$TARGET_PATH" -type d -exec chmod 755 {} \;
find "$TARGET_PATH" -type f -name "*.md" -exec chmod 644 {} \;
find "$TARGET_PATH" -type f -name "*.sh" -exec chmod 755 {} \;
find "$TARGET_PATH" -type f -name "*.py" -exec chmod 755 {} \;

# Verify
if [[ ! -f "$TARGET_PATH/SKILL.md" ]]; then
    echo "Error: Installation verification failed"
    exit 1
fi

echo "✓ Skill '$SKILL_NAME' installed to $TARGET_PATH"
```

## Output Format

```json
{
  "installation": {
    "success": true,
    "skill_name": "api-doc-generator",
    "target": "user",
    "path": "/home/user/.claude/skills/api-doc-generator",
    "files_installed": [
      "SKILL.md",
      "scripts/generate.sh",
      "references/concepts.md",
      "references/best-practices.md"
    ],
    "permissions_set": true,
    "verification_passed": true,
    "message": "Skill 'api-doc-generator' installed successfully"
  }
}
```

## Post-Installation

After successful installation:

1. Skill is immediately available via `/skill-name`
2. No restart required
3. Appears in skill listings
4. Can be invoked with arguments
