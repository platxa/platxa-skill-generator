# Discovery Timeout Handler

Handle discovery phase timeouts gracefully while preserving partial results.

## Timeout Purpose

| Feature | Description |
|---------|-------------|
| Bounded research | Prevent infinite discovery loops |
| Partial preservation | Save progress before timeout |
| Graceful degradation | Continue with available data |
| User notification | Inform about timeout and next steps |

## Timeout Model

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

class TimeoutAction(Enum):
    PROCEED_PARTIAL = "proceed_partial"    # Continue with partial data
    EXTEND_ONCE = "extend_once"            # Allow one extension
    PROMPT_USER = "prompt_user"            # Ask user what to do
    ABORT = "abort"                        # Stop discovery

class DiscoveryStage(Enum):
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    SKILL_TYPE_DETECTION = "skill_type_detection"
    CONTEXT_GATHERING = "context_gathering"
    PATTERN_IDENTIFICATION = "pattern_identification"
    SCOPE_ESTIMATION = "scope_estimation"

@dataclass
class TimeoutConfig:
    total_timeout_seconds: int = 120
    stage_timeout_seconds: int = 30
    extension_seconds: int = 30
    max_extensions: int = 1
    action_on_timeout: TimeoutAction = TimeoutAction.PROCEED_PARTIAL
    warn_at_percent: int = 80

@dataclass
class StageProgress:
    stage: DiscoveryStage
    started_at: datetime
    completed_at: datetime | None = None
    progress_percent: int = 0
    partial_results: dict = field(default_factory=dict)
    timed_out: bool = False

@dataclass
class DiscoveryProgress:
    total_started_at: datetime
    stages: dict[DiscoveryStage, StageProgress] = field(default_factory=dict)
    extensions_used: int = 0
    current_stage: DiscoveryStage | None = None
    warnings: list[str] = field(default_factory=list)
```

## Timeout Handler

```python
import time
from datetime import datetime, timedelta
from threading import Timer
from typing import Any

class TimeoutHandler:
    """Handle discovery phase timeouts."""

    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.progress = DiscoveryProgress(
            total_started_at=datetime.now()
        )
        self._callbacks: list[Callable[[str], None]] = []
        self._timer: Timer | None = None
        self._warning_timer: Timer | None = None

    def start_stage(self, stage: DiscoveryStage) -> StageProgress:
        """Start tracking a discovery stage."""
        stage_progress = StageProgress(
            stage=stage,
            started_at=datetime.now()
        )
        self.progress.stages[stage] = stage_progress
        self.progress.current_stage = stage

        # Start stage timer
        self._start_stage_timer(stage)

        return stage_progress

    def update_progress(
        self,
        stage: DiscoveryStage,
        percent: int,
        partial_results: dict | None = None
    ) -> None:
        """Update progress for a stage."""
        if stage in self.progress.stages:
            sp = self.progress.stages[stage]
            sp.progress_percent = percent
            if partial_results:
                sp.partial_results.update(partial_results)

    def complete_stage(
        self,
        stage: DiscoveryStage,
        results: dict
    ) -> None:
        """Mark a stage as complete."""
        if stage in self.progress.stages:
            sp = self.progress.stages[stage]
            sp.completed_at = datetime.now()
            sp.progress_percent = 100
            sp.partial_results = results

        self._cancel_stage_timer()

    def check_timeout(self) -> tuple[bool, TimeoutAction | None]:
        """Check if timeout has occurred."""
        elapsed = datetime.now() - self.progress.total_started_at
        total_seconds = elapsed.total_seconds()

        # Check total timeout
        if total_seconds >= self.config.total_timeout_seconds:
            return True, self.config.action_on_timeout

        # Check warning threshold
        warn_threshold = (
            self.config.total_timeout_seconds *
            self.config.warn_at_percent / 100
        )
        if total_seconds >= warn_threshold:
            remaining = self.config.total_timeout_seconds - total_seconds
            self._emit_warning(
                f"Discovery timeout in {int(remaining)} seconds"
            )

        return False, None

    def request_extension(self) -> bool:
        """Request timeout extension."""
        if self.progress.extensions_used >= self.config.max_extensions:
            return False

        self.progress.extensions_used += 1
        self.config.total_timeout_seconds += self.config.extension_seconds

        self._emit_warning(
            f"Timeout extended by {self.config.extension_seconds}s "
            f"({self.config.max_extensions - self.progress.extensions_used} "
            f"extensions remaining)"
        )

        return True

    def get_partial_results(self) -> dict[str, Any]:
        """Get all partial results collected so far."""
        results = {}
        for stage, sp in self.progress.stages.items():
            if sp.partial_results:
                results[stage.value] = {
                    "progress": sp.progress_percent,
                    "data": sp.partial_results,
                    "timed_out": sp.timed_out
                }
        return results

    def get_elapsed_time(self) -> timedelta:
        """Get elapsed discovery time."""
        return datetime.now() - self.progress.total_started_at

    def get_remaining_time(self) -> timedelta:
        """Get remaining time before timeout."""
        elapsed = self.get_elapsed_time()
        total = timedelta(seconds=self.config.total_timeout_seconds)
        remaining = total - elapsed
        return max(remaining, timedelta(0))

    def add_callback(self, callback: Callable[[str], None]) -> None:
        """Add warning callback."""
        self._callbacks.append(callback)

    def _start_stage_timer(self, stage: DiscoveryStage) -> None:
        """Start timer for stage timeout."""
        self._cancel_stage_timer()

        def on_stage_timeout():
            if stage in self.progress.stages:
                self.progress.stages[stage].timed_out = True
                self._emit_warning(f"Stage {stage.value} timed out")

        self._timer = Timer(
            self.config.stage_timeout_seconds,
            on_stage_timeout
        )
        self._timer.daemon = True
        self._timer.start()

    def _cancel_stage_timer(self) -> None:
        """Cancel stage timer."""
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _emit_warning(self, message: str) -> None:
        """Emit warning to callbacks."""
        self.progress.warnings.append(message)
        for callback in self._callbacks:
            try:
                callback(message)
            except Exception:
                pass

    def cleanup(self) -> None:
        """Clean up timers."""
        self._cancel_stage_timer()
        if self._warning_timer:
            self._warning_timer.cancel()
```

## Timeout Context Manager

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def discovery_timeout(
    config: TimeoutConfig | None = None
) -> Generator[TimeoutHandler, None, None]:
    """Context manager for discovery timeout handling."""
    handler = TimeoutHandler(config or TimeoutConfig())

    try:
        yield handler
    finally:
        handler.cleanup()


@contextmanager
def stage_timeout(
    handler: TimeoutHandler,
    stage: DiscoveryStage
) -> Generator[StageProgress, None, None]:
    """Context manager for stage-level timeout."""
    progress = handler.start_stage(stage)

    try:
        yield progress
    except Exception as e:
        progress.timed_out = True
        raise
    finally:
        if not progress.completed_at:
            handler.complete_stage(stage, progress.partial_results)
```

## Timeout Formatter

```python
class TimeoutFormatter:
    """Format timeout information for display."""

    def format_progress(self, handler: TimeoutHandler) -> str:
        """Format current progress."""
        lines = []
        elapsed = handler.get_elapsed_time()
        remaining = handler.get_remaining_time()

        lines.append("")
        lines.append("  DISCOVERY PROGRESS")
        lines.append("  ──────────────────")
        lines.append(f"  Elapsed:   {self._format_duration(elapsed)}")
        lines.append(f"  Remaining: {self._format_duration(remaining)}")
        lines.append("")

        # Stage progress
        lines.append("  Stages:")
        for stage in DiscoveryStage:
            if stage in handler.progress.stages:
                sp = handler.progress.stages[stage]
                status = self._stage_status(sp)
                lines.append(f"    {status} {stage.value}: {sp.progress_percent}%")
            else:
                lines.append(f"    ○ {stage.value}: pending")

        # Warnings
        if handler.progress.warnings:
            lines.append("")
            lines.append("  Warnings:")
            for warn in handler.progress.warnings[-3:]:  # Last 3
                lines.append(f"    ⚠ {warn}")

        lines.append("")
        return "\n".join(lines)

    def format_timeout_notice(
        self,
        handler: TimeoutHandler,
        action: TimeoutAction
    ) -> str:
        """Format timeout notice."""
        lines = []

        lines.append("")
        lines.append("  ⏱ DISCOVERY TIMEOUT")
        lines.append("  ───────────────────")
        lines.append(f"  Elapsed: {self._format_duration(handler.get_elapsed_time())}")
        lines.append("")

        # Partial results summary
        partial = handler.get_partial_results()
        if partial:
            lines.append("  Partial results collected:")
            for stage_name, data in partial.items():
                lines.append(f"    • {stage_name}: {data['progress']}% complete")
        else:
            lines.append("  No partial results available")

        lines.append("")
        lines.append(f"  Action: {self._action_description(action)}")
        lines.append("")

        return "\n".join(lines)

    def _format_duration(self, td: timedelta) -> str:
        """Format timedelta for display."""
        total_seconds = int(td.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _stage_status(self, sp: StageProgress) -> str:
        """Get status icon for stage."""
        if sp.timed_out:
            return "⏱"
        if sp.completed_at:
            return "✓"
        if sp.progress_percent > 0:
            return "▶"
        return "○"

    def _action_description(self, action: TimeoutAction) -> str:
        """Get human description of action."""
        descriptions = {
            TimeoutAction.PROCEED_PARTIAL: "Proceeding with partial data",
            TimeoutAction.EXTEND_ONCE: "Extending timeout",
            TimeoutAction.PROMPT_USER: "Waiting for user decision",
            TimeoutAction.ABORT: "Aborting discovery"
        }
        return descriptions.get(action, str(action.value))
```

## Integration

```python
def run_discovery_with_timeout(
    skill_request: dict,
    config: TimeoutConfig | None = None
) -> dict:
    """Run discovery phase with timeout handling."""
    formatter = TimeoutFormatter()

    with discovery_timeout(config) as handler:
        # Add progress callback
        handler.add_callback(lambda msg: print(f"  ⚠ {msg}"))

        results = {}

        # Run each stage with timeout tracking
        stages = [
            (DiscoveryStage.REQUIREMENT_ANALYSIS, analyze_requirements),
            (DiscoveryStage.SKILL_TYPE_DETECTION, detect_skill_type),
            (DiscoveryStage.CONTEXT_GATHERING, gather_context),
            (DiscoveryStage.PATTERN_IDENTIFICATION, identify_patterns),
            (DiscoveryStage.SCOPE_ESTIMATION, estimate_scope),
        ]

        for stage, stage_func in stages:
            # Check for timeout before each stage
            timed_out, action = handler.check_timeout()
            if timed_out:
                print(formatter.format_timeout_notice(handler, action))

                if action == TimeoutAction.EXTEND_ONCE:
                    if not handler.request_extension():
                        action = TimeoutAction.PROCEED_PARTIAL

                if action == TimeoutAction.PROCEED_PARTIAL:
                    return {
                        "partial": True,
                        "results": handler.get_partial_results(),
                        "warnings": handler.progress.warnings
                    }
                elif action == TimeoutAction.ABORT:
                    raise TimeoutError("Discovery aborted due to timeout")

            # Run stage with tracking
            with stage_timeout(handler, stage) as progress:
                try:
                    stage_result = stage_func(
                        skill_request,
                        lambda p, r: handler.update_progress(stage, p, r)
                    )
                    results[stage.value] = stage_result
                except TimeoutError:
                    # Stage timed out, continue with partial
                    results[stage.value] = progress.partial_results

        return {
            "partial": False,
            "results": results,
            "duration": handler.get_elapsed_time().total_seconds()
        }


# Stage function signatures
def analyze_requirements(
    request: dict,
    progress_callback: Callable[[int, dict], None]
) -> dict:
    """Analyze skill requirements."""
    progress_callback(50, {"requirements": []})
    # ... analysis logic ...
    progress_callback(100, {"requirements": ["req1", "req2"]})
    return {"requirements": ["req1", "req2"]}


def detect_skill_type(
    request: dict,
    progress_callback: Callable[[int, dict], None]
) -> dict:
    """Detect skill type."""
    # ... detection logic ...
    return {"type": "builder"}


def gather_context(
    request: dict,
    progress_callback: Callable[[int, dict], None]
) -> dict:
    """Gather additional context."""
    # ... context gathering ...
    return {"context": {}}


def identify_patterns(
    request: dict,
    progress_callback: Callable[[int, dict], None]
) -> dict:
    """Identify relevant patterns."""
    # ... pattern identification ...
    return {"patterns": []}


def estimate_scope(
    request: dict,
    progress_callback: Callable[[int, dict], None]
) -> dict:
    """Estimate skill scope."""
    # ... scope estimation ...
    return {"estimated_tokens": 3000}
```

## Sample Output

```
  DISCOVERY PROGRESS
  ──────────────────
  Elapsed:   45s
  Remaining: 75s

  Stages:
    ✓ requirement_analysis: 100%
    ✓ skill_type_detection: 100%
    ▶ context_gathering: 65%
    ○ pattern_identification: pending
    ○ scope_estimation: pending

  Warnings:
    ⚠ Discovery timeout in 75 seconds
```

```
  ⏱ DISCOVERY TIMEOUT
  ───────────────────
  Elapsed: 2m 0s

  Partial results collected:
    • requirement_analysis: 100% complete
    • skill_type_detection: 100% complete
    • context_gathering: 65% complete

  Action: Proceeding with partial data
```
