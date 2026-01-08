# Workflow Abort and Cleanup

Handle workflow interruptions and clean up partial artifacts.

## Abort Scenarios

| Scenario | Trigger | Cleanup Action |
|----------|---------|----------------|
| User cancellation | Ctrl+C, "cancel" | Remove partial files |
| Error during phase | Exception thrown | Rollback to checkpoint |
| Quality gate failure | Score < threshold | Preserve for review |
| Timeout | Duration exceeded | Save state for resume |

## Abort Model

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

class AbortReason(Enum):
    USER_CANCEL = "user_cancel"
    ERROR = "error"
    QUALITY_FAILURE = "quality_failure"
    TIMEOUT = "timeout"
    DEPENDENCY_MISSING = "dependency_missing"

class CleanupAction(Enum):
    REMOVE_ALL = "remove_all"
    KEEP_CHECKPOINT = "keep_checkpoint"
    KEEP_FOR_REVIEW = "keep_for_review"
    ROLLBACK = "rollback"

@dataclass
class AbortContext:
    reason: AbortReason
    phase: str
    message: str
    timestamp: datetime
    partial_files: list[Path]
    checkpoint_data: dict | None

@dataclass
class CleanupResult:
    action: CleanupAction
    files_removed: list[Path]
    files_preserved: list[Path]
    rollback_path: Path | None
    success: bool
    error: str | None
```

## Cleanup Manager

```python
import shutil
from pathlib import Path
from datetime import datetime

class CleanupManager:
    """Manage cleanup of partial artifacts."""

    ROLLBACK_DIR = ".skill-rollback"
    CHECKPOINT_FILE = ".checkpoint.json"

    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.rollback_dir = work_dir / self.ROLLBACK_DIR
        self.created_files: list[Path] = []
        self.created_dirs: list[Path] = []

    def track_file(self, path: Path) -> None:
        """Track a created file for potential cleanup."""
        self.created_files.append(path)

    def track_dir(self, path: Path) -> None:
        """Track a created directory for potential cleanup."""
        self.created_dirs.append(path)

    def create_checkpoint(self, phase: str, data: dict) -> Path:
        """Create checkpoint for rollback."""
        self.rollback_dir.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "files": [str(f) for f in self.created_files],
            "dirs": [str(d) for d in self.created_dirs]
        }

        checkpoint_path = self.rollback_dir / self.CHECKPOINT_FILE
        import json
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2))

        return checkpoint_path

    def abort(self, context: AbortContext) -> CleanupResult:
        """Handle workflow abort with cleanup."""
        action = self._determine_action(context)

        if action == CleanupAction.REMOVE_ALL:
            return self._remove_all()
        elif action == CleanupAction.ROLLBACK:
            return self._rollback()
        elif action == CleanupAction.KEEP_CHECKPOINT:
            return self._keep_checkpoint(context)
        else:
            return self._keep_for_review(context)

    def _determine_action(self, context: AbortContext) -> CleanupAction:
        """Determine appropriate cleanup action."""
        if context.reason == AbortReason.USER_CANCEL:
            return CleanupAction.REMOVE_ALL
        elif context.reason == AbortReason.ERROR:
            return CleanupAction.ROLLBACK
        elif context.reason == AbortReason.QUALITY_FAILURE:
            return CleanupAction.KEEP_FOR_REVIEW
        elif context.reason == AbortReason.TIMEOUT:
            return CleanupAction.KEEP_CHECKPOINT
        else:
            return CleanupAction.REMOVE_ALL

    def _remove_all(self) -> CleanupResult:
        """Remove all created artifacts."""
        removed = []
        errors = []

        # Remove files first
        for file in reversed(self.created_files):
            try:
                if file.exists():
                    file.unlink()
                    removed.append(file)
            except Exception as e:
                errors.append(str(e))

        # Remove directories (empty ones only)
        for dir in reversed(self.created_dirs):
            try:
                if dir.exists() and not any(dir.iterdir()):
                    dir.rmdir()
                    removed.append(dir)
            except Exception as e:
                errors.append(str(e))

        # Remove rollback dir
        if self.rollback_dir.exists():
            shutil.rmtree(self.rollback_dir)

        return CleanupResult(
            action=CleanupAction.REMOVE_ALL,
            files_removed=removed,
            files_preserved=[],
            rollback_path=None,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else None
        )

    def _rollback(self) -> CleanupResult:
        """Rollback to last checkpoint."""
        checkpoint_path = self.rollback_dir / self.CHECKPOINT_FILE

        if not checkpoint_path.exists():
            return self._remove_all()

        import json
        checkpoint = json.loads(checkpoint_path.read_text())

        # Remove files created after checkpoint
        checkpoint_files = set(checkpoint.get("files", []))
        removed = []

        for file in self.created_files:
            if str(file) not in checkpoint_files:
                try:
                    if file.exists():
                        file.unlink()
                        removed.append(file)
                except Exception:
                    pass

        return CleanupResult(
            action=CleanupAction.ROLLBACK,
            files_removed=removed,
            files_preserved=[Path(f) for f in checkpoint_files if Path(f).exists()],
            rollback_path=checkpoint_path,
            success=True,
            error=None
        )

    def _keep_checkpoint(self, context: AbortContext) -> CleanupResult:
        """Keep checkpoint for later resume."""
        self.create_checkpoint(context.phase, context.checkpoint_data or {})

        return CleanupResult(
            action=CleanupAction.KEEP_CHECKPOINT,
            files_removed=[],
            files_preserved=self.created_files.copy(),
            rollback_path=self.rollback_dir / self.CHECKPOINT_FILE,
            success=True,
            error=None
        )

    def _keep_for_review(self, context: AbortContext) -> CleanupResult:
        """Keep files for user review."""
        # Create review marker
        review_file = self.work_dir / ".needs-review"
        review_file.write_text(f"""
Skill generation needs review.

Reason: {context.reason.value}
Phase: {context.phase}
Message: {context.message}
Time: {context.timestamp.isoformat()}

Files created:
{chr(10).join('  - ' + str(f) for f in self.created_files)}
""")

        return CleanupResult(
            action=CleanupAction.KEEP_FOR_REVIEW,
            files_removed=[],
            files_preserved=self.created_files.copy(),
            rollback_path=None,
            success=True,
            error=None
        )
```

## Signal Handler

```python
import signal
import sys

class AbortHandler:
    """Handle abort signals gracefully."""

    def __init__(self, cleanup_manager: CleanupManager):
        self.cleanup = cleanup_manager
        self.current_phase = "init"
        self._original_handlers = {}

    def install(self) -> None:
        """Install signal handlers."""
        self._original_handlers[signal.SIGINT] = signal.signal(
            signal.SIGINT, self._handle_interrupt
        )
        self._original_handlers[signal.SIGTERM] = signal.signal(
            signal.SIGTERM, self._handle_terminate
        )

    def uninstall(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)

    def set_phase(self, phase: str) -> None:
        """Update current phase for context."""
        self.current_phase = phase

    def _handle_interrupt(self, signum, frame) -> None:
        """Handle Ctrl+C."""
        print("\n\n  ⚠ Abort requested. Cleaning up...")

        context = AbortContext(
            reason=AbortReason.USER_CANCEL,
            phase=self.current_phase,
            message="User pressed Ctrl+C",
            timestamp=datetime.now(),
            partial_files=self.cleanup.created_files.copy(),
            checkpoint_data=None
        )

        result = self.cleanup.abort(context)
        self._report_cleanup(result)

        sys.exit(130)  # 128 + SIGINT

    def _handle_terminate(self, signum, frame) -> None:
        """Handle SIGTERM."""
        context = AbortContext(
            reason=AbortReason.USER_CANCEL,
            phase=self.current_phase,
            message="Process terminated",
            timestamp=datetime.now(),
            partial_files=self.cleanup.created_files.copy(),
            checkpoint_data=None
        )

        self.cleanup.abort(context)
        sys.exit(143)  # 128 + SIGTERM

    def _report_cleanup(self, result: CleanupResult) -> None:
        """Report cleanup results."""
        if result.action == CleanupAction.REMOVE_ALL:
            print(f"  ✓ Removed {len(result.files_removed)} partial files")
        elif result.action == CleanupAction.ROLLBACK:
            print(f"  ✓ Rolled back to checkpoint")
        elif result.action == CleanupAction.KEEP_FOR_REVIEW:
            print(f"  ℹ Files preserved for review")

        if result.error:
            print(f"  ⚠ Some cleanup errors: {result.error}")
```

## Integration

```python
def run_with_cleanup(work_dir: Path, generator_func):
    """Run generator with cleanup on abort."""
    cleanup = CleanupManager(work_dir)
    handler = AbortHandler(cleanup)

    try:
        handler.install()

        # Track files as they're created
        def track_write(path: Path, content: str) -> None:
            cleanup.track_file(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

        # Run the generator
        result = generator_func(track_write, handler.set_phase)

        # Success - no cleanup needed
        return result

    except Exception as e:
        # Error - perform cleanup
        context = AbortContext(
            reason=AbortReason.ERROR,
            phase=handler.current_phase,
            message=str(e),
            timestamp=datetime.now(),
            partial_files=cleanup.created_files.copy(),
            checkpoint_data=None
        )

        cleanup.abort(context)
        raise

    finally:
        handler.uninstall()
```

## Cleanup Display

```
  ⚠ Abort requested. Cleaning up...

  Phase: generation (3/6)
  Files created: 4

  Cleanup action: remove_all

    ✗ Removing: SKILL.md
    ✗ Removing: references/overview.md
    ✗ Removing: references/workflow.md
    ✗ Removing: references/

  ✓ Removed 4 partial files

  Workflow aborted.
```
