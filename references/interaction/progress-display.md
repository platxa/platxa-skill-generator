# Progress Display Pattern

User-facing progress reporting for skill generation workflow.

## Display Principles

1. **Informative** - Show what's happening and why
2. **Non-blocking** - Don't interrupt workflow
3. **Contextual** - Relevant to current phase
4. **Recoverable** - Allow pause/resume understanding

## Progress Display Formats

### Compact (Default)

```
[Discovery] Analyzing requirements... ████████░░ 80%
```

### Detailed

```
═══════════════════════════════════════════════════════
  Phase 2/6: Discovery
═══════════════════════════════════════════════════════

  ▶ Analyzing skill requirements...

  Completed:
    ✓ Extracted skill type: builder
    ✓ Identified 12 requirements
    ✓ Detected 3 constraints

  Progress: ████████░░ 80%

  Next: Architecture planning
═══════════════════════════════════════════════════════
```

### Minimal (CI/Quiet Mode)

```
Phase 2/6: Discovery (80%)
```

## Display Model

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable

class DisplayMode(Enum):
    COMPACT = "compact"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    JSON = "json"

@dataclass
class PhaseProgress:
    phase_name: str
    phase_number: int
    total_phases: int
    current_step: str
    completed_steps: list[str]
    percent_complete: float
    next_phase: str | None
    warnings: list[str]
    errors: list[str]

@dataclass
class DisplayConfig:
    mode: DisplayMode
    show_timestamps: bool
    show_step_details: bool
    use_colors: bool
    width: int
```

## Display Implementation

```python
class ProgressDisplay:
    """Display progress to users during skill generation."""

    PHASE_ICONS = {
        "init": "🚀",
        "discovery": "🔍",
        "architecture": "📐",
        "generation": "⚙️",
        "validation": "✓",
        "installation": "📦",
    }

    def __init__(self, config: DisplayConfig | None = None):
        self.config = config or DisplayConfig(
            mode=DisplayMode.COMPACT,
            show_timestamps=False,
            show_step_details=True,
            use_colors=True,
            width=60
        )

    def show(self, progress: PhaseProgress) -> str:
        """Render progress based on display mode."""
        renderers = {
            DisplayMode.COMPACT: self._render_compact,
            DisplayMode.DETAILED: self._render_detailed,
            DisplayMode.MINIMAL: self._render_minimal,
            DisplayMode.JSON: self._render_json,
        }

        renderer = renderers.get(self.config.mode, self._render_compact)
        return renderer(progress)

    def _render_compact(self, p: PhaseProgress) -> str:
        """Render compact single-line progress."""
        icon = self.PHASE_ICONS.get(p.phase_name.lower(), "▶")
        bar = self._progress_bar(p.percent_complete)

        line = f"[{p.phase_name}] {p.current_step}... {bar} {p.percent_complete:.0f}%"

        if self.config.use_colors:
            if p.errors:
                line = f"\033[91m{line}\033[0m"  # Red
            elif p.warnings:
                line = f"\033[93m{line}\033[0m"  # Yellow

        return line

    def _render_detailed(self, p: PhaseProgress) -> str:
        """Render detailed multi-line progress."""
        width = self.config.width
        lines = []

        # Header
        lines.append("═" * width)
        header = f"  Phase {p.phase_number}/{p.total_phases}: {p.phase_name}"
        lines.append(header)
        lines.append("═" * width)
        lines.append("")

        # Current step
        icon = self.PHASE_ICONS.get(p.phase_name.lower(), "▶")
        lines.append(f"  {icon} {p.current_step}...")
        lines.append("")

        # Completed steps
        if p.completed_steps and self.config.show_step_details:
            lines.append("  Completed:")
            for step in p.completed_steps[-5:]:  # Last 5
                lines.append(f"    ✓ {step}")
            lines.append("")

        # Progress bar
        bar = self._progress_bar(p.percent_complete, width=30)
        lines.append(f"  Progress: {bar} {p.percent_complete:.0f}%")
        lines.append("")

        # Next phase
        if p.next_phase:
            lines.append(f"  Next: {p.next_phase}")

        # Warnings
        if p.warnings:
            lines.append("")
            lines.append("  ⚠ Warnings:")
            for warn in p.warnings[:3]:
                lines.append(f"    - {warn}")

        # Errors
        if p.errors:
            lines.append("")
            lines.append("  ✗ Errors:")
            for err in p.errors[:3]:
                lines.append(f"    - {err}")

        lines.append("═" * width)

        return "\n".join(lines)

    def _render_minimal(self, p: PhaseProgress) -> str:
        """Render minimal progress for CI/scripts."""
        return f"Phase {p.phase_number}/{p.total_phases}: {p.phase_name} ({p.percent_complete:.0f}%)"

    def _render_json(self, p: PhaseProgress) -> str:
        """Render progress as JSON."""
        import json
        return json.dumps({
            "phase": p.phase_name,
            "phase_number": p.phase_number,
            "total_phases": p.total_phases,
            "current_step": p.current_step,
            "percent_complete": p.percent_complete,
            "completed_steps": p.completed_steps,
            "next_phase": p.next_phase,
            "warnings": p.warnings,
            "errors": p.errors,
        })

    def _progress_bar(self, percent: float, width: int = 10) -> str:
        """Generate ASCII progress bar."""
        filled = int(percent / 100 * width)
        empty = width - filled
        return "█" * filled + "░" * empty
```

## Live Updates

```python
import sys
import time

class LiveProgressDisplay:
    """Display live-updating progress."""

    def __init__(self, display: ProgressDisplay):
        self.display = display
        self.last_output_lines = 0

    def update(self, progress: PhaseProgress) -> None:
        """Update display in-place."""
        # Clear previous output
        if self.last_output_lines > 0:
            sys.stdout.write(f"\033[{self.last_output_lines}A")
            sys.stdout.write("\033[J")

        # Render new output
        output = self.display.show(progress)
        print(output)

        # Track lines for next clear
        self.last_output_lines = output.count('\n') + 1
        sys.stdout.flush()

    def complete(self, message: str) -> None:
        """Show completion message."""
        self.last_output_lines = 0
        print(f"\n✓ {message}\n")
```

## Phase Transitions

```python
class PhaseTransitionDisplay:
    """Display phase transition animations."""

    TRANSITIONS = {
        ("discovery", "architecture"): "Requirements analyzed, planning architecture...",
        ("architecture", "generation"): "Architecture defined, generating content...",
        ("generation", "validation"): "Content generated, validating quality...",
        ("validation", "installation"): "Quality verified, preparing installation...",
    }

    def show_transition(
        self,
        from_phase: str,
        to_phase: str,
        mode: DisplayMode = DisplayMode.COMPACT
    ) -> str:
        """Display transition between phases."""
        key = (from_phase.lower(), to_phase.lower())
        message = self.TRANSITIONS.get(key, f"Moving to {to_phase}...")

        if mode == DisplayMode.COMPACT:
            return f"→ {message}"

        elif mode == DisplayMode.DETAILED:
            lines = [
                "",
                "─" * 40,
                f"  ✓ {from_phase.title()} complete",
                f"  → {message}",
                "─" * 40,
                "",
            ]
            return "\n".join(lines)

        else:
            return message
```

## Callback Integration

```python
from typing import Protocol

class ProgressCallback(Protocol):
    """Protocol for progress callbacks."""

    def on_phase_start(self, phase: str, total_steps: int) -> None: ...
    def on_step_complete(self, step: str) -> None: ...
    def on_phase_complete(self, phase: str) -> None: ...
    def on_warning(self, message: str) -> None: ...
    def on_error(self, message: str) -> None: ...


class DisplayProgressCallback:
    """Progress callback that updates display."""

    def __init__(self, display: ProgressDisplay):
        self.display = display
        self.live = LiveProgressDisplay(display)
        self.current_phase = ""
        self.total_steps = 0
        self.completed_steps: list[str] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def on_phase_start(self, phase: str, total_steps: int) -> None:
        self.current_phase = phase
        self.total_steps = total_steps
        self.completed_steps = []
        self._update()

    def on_step_complete(self, step: str) -> None:
        self.completed_steps.append(step)
        self._update()

    def on_phase_complete(self, phase: str) -> None:
        self.live.complete(f"{phase} phase complete")

    def on_warning(self, message: str) -> None:
        self.warnings.append(message)
        self._update()

    def on_error(self, message: str) -> None:
        self.errors.append(message)
        self._update()

    def _update(self) -> None:
        percent = (len(self.completed_steps) / self.total_steps * 100
                   if self.total_steps > 0 else 0)

        progress = PhaseProgress(
            phase_name=self.current_phase,
            phase_number=self._phase_number(),
            total_phases=6,
            current_step=self.completed_steps[-1] if self.completed_steps else "Starting...",
            completed_steps=self.completed_steps,
            percent_complete=percent,
            next_phase=self._next_phase(),
            warnings=self.warnings,
            errors=self.errors,
        )

        self.live.update(progress)

    def _phase_number(self) -> int:
        phases = ["init", "discovery", "architecture", "generation", "validation", "installation"]
        try:
            return phases.index(self.current_phase.lower()) + 1
        except ValueError:
            return 0

    def _next_phase(self) -> str | None:
        phases = ["Discovery", "Architecture", "Generation", "Validation", "Installation", None]
        idx = self._phase_number()
        return phases[idx] if idx < len(phases) else None
```

## Usage Example

```python
# Create display
config = DisplayConfig(
    mode=DisplayMode.DETAILED,
    show_timestamps=True,
    show_step_details=True,
    use_colors=True,
    width=60
)
display = ProgressDisplay(config)

# Create callback for workflow
callback = DisplayProgressCallback(display)

# Workflow integration
workflow = SkillGeneratorWorkflow(progress_callback=callback)
workflow.run()
```
