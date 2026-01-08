# Workflow Resumption Prompt

Handle interrupted workflows with resume or fresh start options.

## Resumption Display

```
═══════════════════════════════════════════════════════════════
  PREVIOUS SESSION DETECTED
═══════════════════════════════════════════════════════════════

  Skill: api-doc-generator
  Last Activity: 2 hours ago
  Phase: Generation (3/6)
  Progress: 45%

  Files Generated:
    ✓ SKILL.md
    ✓ references/overview.md
    ○ references/workflow.md (in progress)
    ○ references/api.md
    ○ scripts/generate.sh

───────────────────────────────────────────────────────────────

  How would you like to proceed?

    [1] Resume from where you left off
    [2] Start fresh (discard previous progress)
    [3] View previous session details
    [4] Cancel

  Select option [1-4]:
```

## Session State Model

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class FileProgress:
    path: str
    status: str  # completed, in_progress, pending
    size_bytes: int | None
    completed_at: datetime | None

@dataclass
class SessionState:
    session_id: str
    skill_name: str
    status: SessionStatus
    current_phase: str
    phase_number: int
    total_phases: int
    progress_percent: float
    files: list[FileProgress]
    started_at: datetime
    last_activity: datetime
    checkpoint_data: dict
    error: str | None

@dataclass
class ResumptionChoice:
    action: str  # resume, fresh, view, cancel
    session: SessionState | None
```

## Resumption Flow

```python
class WorkflowResumptionFlow:
    """Handle workflow resumption decisions."""

    SESSION_FILE = ".claude/skill-generator-session.json"

    def __init__(self):
        self.session: SessionState | None = None

    def check_for_session(self) -> SessionState | None:
        """Check for existing session."""
        session_path = Path(self.SESSION_FILE)
        if not session_path.exists():
            return None

        try:
            import json
            data = json.loads(session_path.read_text())
            self.session = self._parse_session(data)

            # Check if session is still valid
            if self._is_session_stale():
                return None

            return self.session
        except Exception:
            return None

    def _parse_session(self, data: dict) -> SessionState:
        """Parse session data from JSON."""
        return SessionState(
            session_id=data["session_id"],
            skill_name=data["skill_name"],
            status=SessionStatus(data["status"]),
            current_phase=data["current_phase"],
            phase_number=data["phase_number"],
            total_phases=data["total_phases"],
            progress_percent=data["progress_percent"],
            files=[
                FileProgress(
                    path=f["path"],
                    status=f["status"],
                    size_bytes=f.get("size_bytes"),
                    completed_at=datetime.fromisoformat(f["completed_at"]) if f.get("completed_at") else None
                )
                for f in data.get("files", [])
            ],
            started_at=datetime.fromisoformat(data["started_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            checkpoint_data=data.get("checkpoint_data", {}),
            error=data.get("error")
        )

    def _is_session_stale(self) -> bool:
        """Check if session is too old to resume."""
        if not self.session:
            return True

        age = datetime.now() - self.session.last_activity
        max_age_hours = 24

        return age.total_seconds() > max_age_hours * 3600

    def prompt_resumption(self) -> ResumptionChoice:
        """Display resumption prompt and get choice."""
        if not self.session:
            return ResumptionChoice(action="fresh", session=None)

        self._display_session_info()
        choice = self._get_choice()

        return ResumptionChoice(
            action=choice,
            session=self.session if choice == "resume" else None
        )

    def _display_session_info(self) -> None:
        """Display previous session information."""
        s = self.session
        width = 65

        print("═" * width)
        print("  PREVIOUS SESSION DETECTED")
        print("═" * width)
        print()

        # Session details
        print(f"  Skill: {s.skill_name}")
        print(f"  Last Activity: {self._format_age(s.last_activity)}")
        print(f"  Phase: {s.current_phase} ({s.phase_number}/{s.total_phases})")
        print(f"  Progress: {s.progress_percent:.0f}%")
        print()

        # File progress
        print("  Files Generated:")
        for f in s.files:
            if f.status == "completed":
                icon = "✓"
            elif f.status == "in_progress":
                icon = "○"
            else:
                icon = "·"

            status_text = f" ({f.status})" if f.status != "completed" else ""
            print(f"    {icon} {f.path}{status_text}")

        print()

        # Error if any
        if s.error:
            print(f"  ⚠ Previous error: {s.error}")
            print()

        print("─" * width)
        print()

    def _format_age(self, dt: datetime) -> str:
        """Format datetime as relative age."""
        age = datetime.now() - dt
        hours = age.total_seconds() / 3600

        if hours < 1:
            minutes = int(age.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif hours < 24:
            hours = int(hours)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(hours / 24)
            return f"{days} day{'s' if days != 1 else ''} ago"

    def _get_choice(self) -> str:
        """Get user's choice."""
        print("  How would you like to proceed?")
        print()
        print("    [1] Resume from where you left off")
        print("    [2] Start fresh (discard previous progress)")
        print("    [3] View previous session details")
        print("    [4] Cancel")
        print()

        while True:
            choice = input("  Select option [1-4]: ").strip()

            if choice == "1":
                return "resume"
            elif choice == "2":
                confirm = input("  Discard previous progress? [y/N]: ").strip().lower()
                if confirm in ("y", "yes"):
                    self._clear_session()
                    return "fresh"
                continue
            elif choice == "3":
                self._show_details()
                continue
            elif choice == "4":
                return "cancel"
            else:
                print("  Invalid choice. Please enter 1-4.")

    def _show_details(self) -> None:
        """Show detailed session information."""
        s = self.session
        print()
        print("  ─── Session Details ───")
        print(f"  Session ID: {s.session_id}")
        print(f"  Started: {s.started_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Last Activity: {s.last_activity.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Status: {s.status.value}")
        print()

        if s.checkpoint_data:
            print("  Checkpoint Data:")
            for key, value in s.checkpoint_data.items():
                print(f"    {key}: {value}")
            print()

    def _clear_session(self) -> None:
        """Clear saved session."""
        session_path = Path(self.SESSION_FILE)
        if session_path.exists():
            session_path.unlink()
```

## Session Persistence

```python
import json
from datetime import datetime

class SessionManager:
    """Manage session state persistence."""

    SESSION_FILE = ".claude/skill-generator-session.json"

    def save_session(self, state: SessionState) -> None:
        """Save session state to file."""
        path = Path(self.SESSION_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": state.session_id,
            "skill_name": state.skill_name,
            "status": state.status.value,
            "current_phase": state.current_phase,
            "phase_number": state.phase_number,
            "total_phases": state.total_phases,
            "progress_percent": state.progress_percent,
            "files": [
                {
                    "path": f.path,
                    "status": f.status,
                    "size_bytes": f.size_bytes,
                    "completed_at": f.completed_at.isoformat() if f.completed_at else None
                }
                for f in state.files
            ],
            "started_at": state.started_at.isoformat(),
            "last_activity": state.last_activity.isoformat(),
            "checkpoint_data": state.checkpoint_data,
            "error": state.error
        }

        path.write_text(json.dumps(data, indent=2))

    def update_progress(
        self,
        phase: str,
        phase_number: int,
        progress: float,
        completed_file: str | None = None
    ) -> None:
        """Update session progress."""
        if not hasattr(self, '_current_session'):
            return

        self._current_session.current_phase = phase
        self._current_session.phase_number = phase_number
        self._current_session.progress_percent = progress
        self._current_session.last_activity = datetime.now()

        if completed_file:
            for f in self._current_session.files:
                if f.path == completed_file:
                    f.status = "completed"
                    f.completed_at = datetime.now()

        self.save_session(self._current_session)

    def clear_session(self) -> None:
        """Clear saved session on completion."""
        path = Path(self.SESSION_FILE)
        if path.exists():
            path.unlink()
```

## Integration

```python
def handle_workflow_start() -> tuple[str, SessionState | None]:
    """Handle workflow start with resumption check."""
    flow = WorkflowResumptionFlow()

    # Check for existing session
    existing = flow.check_for_session()

    if existing:
        choice = flow.prompt_resumption()

        if choice.action == "resume":
            print("\n  ▶ Resuming previous session...\n")
            return "resume", choice.session

        elif choice.action == "fresh":
            print("\n  ▶ Starting fresh...\n")
            return "fresh", None

        elif choice.action == "cancel":
            print("\n  Cancelled.\n")
            return "cancel", None

    return "fresh", None
```
