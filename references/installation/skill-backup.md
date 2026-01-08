# Existing Skill Backup

Create backups before overwriting existing skills.

## Backup Strategy

| Scenario | Action | Backup Location |
|----------|--------|-----------------|
| New install | No backup needed | N/A |
| Overwrite existing | Create timestamped .bak | Same directory |
| Update in place | Incremental backup | Same directory |
| Rollback needed | Restore from .bak | Original location |

## Backup Model

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

class BackupType(Enum):
    FULL = "full"           # Complete directory backup
    INCREMENTAL = "incr"    # Only changed files
    SNAPSHOT = "snap"       # Quick state capture

class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORED = "restored"

@dataclass
class BackupMetadata:
    backup_id: str
    skill_name: str
    backup_type: BackupType
    status: BackupStatus
    source_path: Path
    backup_path: Path
    created_at: datetime
    file_count: int
    total_size: int
    checksum: str | None

@dataclass
class BackupResult:
    success: bool
    metadata: BackupMetadata | None
    error: str | None
    duration_ms: int
```

## Backup Manager

```python
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

class SkillBackupManager:
    """Manage skill backups before overwriting."""

    BACKUP_DIR = ".skill-backups"
    METADATA_FILE = "backup-metadata.json"
    MAX_BACKUPS = 5

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or Path.home() / ".claude"
        self.backup_root = self.base_path / self.BACKUP_DIR

    def backup_exists(self, skill_name: str) -> bool:
        """Check if skill has existing backups."""
        skill_backup_dir = self.backup_root / skill_name
        return skill_backup_dir.exists() and any(skill_backup_dir.iterdir())

    def create_backup(
        self,
        skill_path: Path,
        backup_type: BackupType = BackupType.FULL
    ) -> BackupResult:
        """Create backup of existing skill."""
        start_time = datetime.now()
        skill_name = skill_path.name

        # Validate source exists
        if not skill_path.exists():
            return BackupResult(
                success=False,
                metadata=None,
                error=f"Source path does not exist: {skill_path}",
                duration_ms=0
            )

        try:
            # Generate backup ID
            backup_id = self._generate_backup_id(skill_name)

            # Create backup directory
            backup_path = self.backup_root / skill_name / backup_id
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Perform backup based on type
            if backup_type == BackupType.FULL:
                file_count, total_size = self._full_backup(skill_path, backup_path)
            elif backup_type == BackupType.INCREMENTAL:
                file_count, total_size = self._incremental_backup(skill_path, backup_path)
            else:
                file_count, total_size = self._snapshot_backup(skill_path, backup_path)

            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)

            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                skill_name=skill_name,
                backup_type=backup_type,
                status=BackupStatus.COMPLETED,
                source_path=skill_path,
                backup_path=backup_path,
                created_at=datetime.now(),
                file_count=file_count,
                total_size=total_size,
                checksum=checksum
            )

            # Save metadata
            self._save_metadata(metadata)

            # Cleanup old backups
            self._cleanup_old_backups(skill_name)

            duration = int((datetime.now() - start_time).total_seconds() * 1000)

            return BackupResult(
                success=True,
                metadata=metadata,
                error=None,
                duration_ms=duration
            )

        except Exception as e:
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return BackupResult(
                success=False,
                metadata=None,
                error=str(e),
                duration_ms=duration
            )

    def _generate_backup_id(self, skill_name: str) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{skill_name}.bak.{timestamp}"

    def _full_backup(self, source: Path, dest: Path) -> tuple[int, int]:
        """Perform full directory backup."""
        shutil.copytree(source, dest)

        file_count = sum(1 for _ in dest.rglob("*") if _.is_file())
        total_size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())

        return file_count, total_size

    def _incremental_backup(self, source: Path, dest: Path) -> tuple[int, int]:
        """Backup only changed files since last backup."""
        dest.mkdir(parents=True, exist_ok=True)

        # Get last backup for comparison
        last_backup = self._get_last_backup(source.name)

        file_count = 0
        total_size = 0

        for src_file in source.rglob("*"):
            if not src_file.is_file():
                continue

            rel_path = src_file.relative_to(source)
            dest_file = dest / rel_path

            # Check if file changed
            if last_backup:
                last_file = last_backup.backup_path / rel_path
                if last_file.exists():
                    if self._files_identical(src_file, last_file):
                        continue

            # Copy changed file
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)
            file_count += 1
            total_size += src_file.stat().st_size

        return file_count, total_size

    def _snapshot_backup(self, source: Path, dest: Path) -> tuple[int, int]:
        """Quick snapshot with file list and checksums."""
        dest.mkdir(parents=True, exist_ok=True)

        manifest = []
        total_size = 0

        for src_file in source.rglob("*"):
            if not src_file.is_file():
                continue

            rel_path = str(src_file.relative_to(source))
            size = src_file.stat().st_size
            checksum = self._file_checksum(src_file)

            manifest.append({
                "path": rel_path,
                "size": size,
                "checksum": checksum,
                "mtime": src_file.stat().st_mtime
            })
            total_size += size

        # Save manifest
        manifest_file = dest / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2))

        return len(manifest), total_size

    def _files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are identical."""
        if file1.stat().st_size != file2.stat().st_size:
            return False
        return self._file_checksum(file1) == self._file_checksum(file2)

    def _file_checksum(self, path: Path) -> str:
        """Calculate file checksum."""
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate checksum of entire backup."""
        hasher = hashlib.md5()
        for file in sorted(path.rglob("*")):
            if file.is_file():
                hasher.update(self._file_checksum(file).encode())
        return hasher.hexdigest()

    def _save_metadata(self, metadata: BackupMetadata) -> None:
        """Save backup metadata."""
        meta_file = metadata.backup_path / self.METADATA_FILE
        data = {
            "backup_id": metadata.backup_id,
            "skill_name": metadata.skill_name,
            "backup_type": metadata.backup_type.value,
            "status": metadata.status.value,
            "source_path": str(metadata.source_path),
            "backup_path": str(metadata.backup_path),
            "created_at": metadata.created_at.isoformat(),
            "file_count": metadata.file_count,
            "total_size": metadata.total_size,
            "checksum": metadata.checksum
        }
        meta_file.write_text(json.dumps(data, indent=2))

    def _get_last_backup(self, skill_name: str) -> BackupMetadata | None:
        """Get most recent backup for skill."""
        backups = self.list_backups(skill_name)
        return backups[0] if backups else None

    def _cleanup_old_backups(self, skill_name: str) -> int:
        """Remove old backups beyond MAX_BACKUPS."""
        backups = self.list_backups(skill_name)
        removed = 0

        for backup in backups[self.MAX_BACKUPS:]:
            shutil.rmtree(backup.backup_path)
            removed += 1

        return removed

    def list_backups(self, skill_name: str) -> list[BackupMetadata]:
        """List all backups for a skill."""
        skill_backup_dir = self.backup_root / skill_name
        if not skill_backup_dir.exists():
            return []

        backups = []
        for backup_dir in skill_backup_dir.iterdir():
            if not backup_dir.is_dir():
                continue

            meta_file = backup_dir / self.METADATA_FILE
            if meta_file.exists():
                try:
                    data = json.loads(meta_file.read_text())
                    backups.append(BackupMetadata(
                        backup_id=data["backup_id"],
                        skill_name=data["skill_name"],
                        backup_type=BackupType(data["backup_type"]),
                        status=BackupStatus(data["status"]),
                        source_path=Path(data["source_path"]),
                        backup_path=Path(data["backup_path"]),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        file_count=data["file_count"],
                        total_size=data["total_size"],
                        checksum=data.get("checksum")
                    ))
                except (json.JSONDecodeError, KeyError):
                    continue

        return sorted(backups, key=lambda b: b.created_at, reverse=True)
```

## Restore Operations

```python
class BackupRestorer:
    """Restore skills from backups."""

    def restore(
        self,
        backup: BackupMetadata,
        target_path: Path | None = None
    ) -> bool:
        """Restore skill from backup."""
        target = target_path or backup.source_path

        # Verify backup integrity
        if not self._verify_backup(backup):
            print(f"  ✗ Backup integrity check failed")
            return False

        # Remove existing if present
        if target.exists():
            shutil.rmtree(target)

        # Restore from backup
        if backup.backup_type == BackupType.SNAPSHOT:
            return self._restore_from_snapshot(backup, target)
        else:
            shutil.copytree(backup.backup_path, target)
            return True

    def _verify_backup(self, backup: BackupMetadata) -> bool:
        """Verify backup integrity."""
        if not backup.backup_path.exists():
            return False

        if backup.checksum:
            current = self._calculate_checksum(backup.backup_path)
            return current == backup.checksum

        return True

    def _restore_from_snapshot(
        self,
        backup: BackupMetadata,
        target: Path
    ) -> bool:
        """Restore from snapshot manifest."""
        manifest_file = backup.backup_path / "manifest.json"
        if not manifest_file.exists():
            return False

        # Snapshot only contains manifest, not files
        # This would require original source or full backup
        print("  ⚠ Snapshot restore requires original files")
        return False

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate checksum of directory."""
        hasher = hashlib.md5()
        for file in sorted(path.rglob("*")):
            if file.is_file() and file.name != "backup-metadata.json":
                with open(file, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        hasher.update(chunk)
        return hasher.hexdigest()
```

## Backup Display

```python
def display_backup_info(backup: BackupMetadata) -> None:
    """Display backup information."""
    print()
    print("─" * 50)
    print(f"  Backup: {backup.backup_id}")
    print("─" * 50)
    print(f"  Skill:    {backup.skill_name}")
    print(f"  Type:     {backup.backup_type.value}")
    print(f"  Status:   {backup.status.value}")
    print(f"  Created:  {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Files:    {backup.file_count}")
    print(f"  Size:     {_format_size(backup.total_size)}")
    print(f"  Path:     {backup.backup_path}")
    print()

def _format_size(bytes: int) -> str:
    """Format byte size."""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"
```

## Integration

```python
def backup_before_install(skill_path: Path) -> BackupResult | None:
    """Create backup before installing over existing skill."""
    if not skill_path.exists():
        return None

    print()
    print(f"  ⚠ Existing skill found: {skill_path.name}")
    print()

    # Ask user
    response = input("  Create backup before overwriting? [Y/n]: ").strip().lower()

    if response not in ("", "y", "yes"):
        confirm = input("  Proceed WITHOUT backup? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            raise SystemExit(1)
        return None

    # Create backup
    print()
    print("  Creating backup...")

    manager = SkillBackupManager()
    result = manager.create_backup(skill_path)

    if result.success:
        print(f"  ✓ Backup created: {result.metadata.backup_id}")
        print(f"    Files: {result.metadata.file_count}")
        print(f"    Size:  {_format_size(result.metadata.total_size)}")
    else:
        print(f"  ✗ Backup failed: {result.error}")
        proceed = input("  Continue without backup? [y/N]: ").strip().lower()
        if proceed not in ("y", "yes"):
            raise SystemExit(1)

    return result
```

## Backup Display Format

```
  ⚠ Existing skill found: api-doc-generator

  Create backup before overwriting? [Y/n]: y

  Creating backup...
  ✓ Backup created: api-doc-generator.bak.20240115_143022
    Files: 6
    Size:  12.4 KB

  Proceeding with installation...
```
