# Workflow Progress Reporting

Pattern for tracking and displaying generation progress to users.

## Progress Model

### State Structure

```python
@dataclass
class WorkflowProgress:
    skill_name: str
    current_phase: str
    phase_status: Literal["pending", "running", "completed", "failed"]
    completed_phases: list[str]
    remaining_phases: list[str]
    current_step: int
    total_steps: int
    iteration: int
    max_iterations: int
    started_at: datetime
    elapsed_seconds: float
    estimated_remaining: float | None
    artifacts: dict[str, ArtifactStatus]
    messages: list[ProgressMessage]
```

### Phase Tracking

```python
PHASES = [
    {"id": "init", "name": "Initialize", "weight": 5},
    {"id": "discovery", "name": "Discovery", "weight": 15},
    {"id": "architecture", "name": "Architecture", "weight": 15},
    {"id": "generation", "name": "Generation", "weight": 35},
    {"id": "validation", "name": "Validation", "weight": 20},
    {"id": "installation", "name": "Installation", "weight": 10},
]

def calculate_progress_percentage(progress: WorkflowProgress) -> float:
    """Calculate overall progress as percentage."""
    completed_weight = sum(
        p["weight"] for p in PHASES
        if p["id"] in progress.completed_phases
    )

    # Add partial progress for current phase
    current_phase = next(
        (p for p in PHASES if p["id"] == progress.current_phase),
        None
    )
    if current_phase and progress.total_steps > 0:
        phase_progress = progress.current_step / progress.total_steps
        completed_weight += current_phase["weight"] * phase_progress

    total_weight = sum(p["weight"] for p in PHASES)
    return (completed_weight / total_weight) * 100
```

## Display Formats

### Compact Progress Bar

```
Generating: api-doc-generator
[████████████░░░░░░░░] 62% | Phase: Generation (3/6) | Step 4/7
```

### Detailed Progress

```
══════════════════════════════════════════════════════════════════════
  Skill Generator Progress: api-doc-generator
══════════════════════════════════════════════════════════════════════

  Phases:
    ✓ Initialize       [██████████] 100%
    ✓ Discovery        [██████████] 100%
    ✓ Architecture     [██████████] 100%
    ▶ Generation       [██████░░░░]  60%  ← Current
    ○ Validation       [░░░░░░░░░░]   0%
    ○ Installation     [░░░░░░░░░░]   0%

  Current Phase: Generation (Step 4/7)
    ✓ Generate SKILL.md frontmatter
    ✓ Generate SKILL.md overview
    ✓ Generate SKILL.md workflow
    ▶ Generate examples section
    ○ Generate references/concepts.md
    ○ Generate references/workflow.md
    ○ Generate scripts/validate.sh

  Progress: 62% | Elapsed: 1m 23s | ETA: ~50s

══════════════════════════════════════════════════════════════════════
```

### JSON Progress (for programmatic access)

```json
{
  "skill_name": "api-doc-generator",
  "progress_percent": 62.3,
  "current_phase": {
    "id": "generation",
    "name": "Generation",
    "status": "running",
    "step": 4,
    "total_steps": 7
  },
  "phases": [
    {"id": "init", "status": "completed", "duration_ms": 1200},
    {"id": "discovery", "status": "completed", "duration_ms": 15400},
    {"id": "architecture", "status": "completed", "duration_ms": 12800},
    {"id": "generation", "status": "running", "progress": 0.57},
    {"id": "validation", "status": "pending"},
    {"id": "installation", "status": "pending"}
  ],
  "timing": {
    "started_at": "2024-01-15T10:30:00Z",
    "elapsed_ms": 83000,
    "estimated_remaining_ms": 50000
  },
  "iteration": {
    "current": 1,
    "max": 3
  }
}
```

## Progress Events

### Event Types

```python
class ProgressEventType(Enum):
    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"
    PHASE_FAILED = "phase_failed"
    STEP_START = "step_start"
    STEP_COMPLETE = "step_complete"
    ARTIFACT_CREATED = "artifact_created"
    ITERATION_START = "iteration_start"
    QUALITY_SCORE = "quality_score"
    USER_INPUT_NEEDED = "user_input_needed"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ProgressEvent:
    event_type: ProgressEventType
    timestamp: datetime
    phase: str
    message: str
    details: dict
```

### Event Emission

```python
class ProgressReporter:
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.events: list[ProgressEvent] = []
        self.listeners: list[Callable] = []

    def emit(self, event: ProgressEvent) -> None:
        """Emit progress event to all listeners."""
        self.events.append(event)
        for listener in self.listeners:
            listener(event)

    def phase_start(self, phase: str) -> None:
        self.emit(ProgressEvent(
            event_type=ProgressEventType.PHASE_START,
            timestamp=datetime.now(),
            phase=phase,
            message=f"Starting {phase} phase",
            details={}
        ))

    def step_complete(self, phase: str, step: str, artifact: str = None) -> None:
        self.emit(ProgressEvent(
            event_type=ProgressEventType.STEP_COMPLETE,
            timestamp=datetime.now(),
            phase=phase,
            message=f"Completed: {step}",
            details={"artifact": artifact} if artifact else {}
        ))
```

## Real-Time Updates

### Streaming Progress

```python
async def stream_progress(reporter: ProgressReporter):
    """Stream progress updates to user."""
    last_percent = 0

    async for event in reporter.events_stream():
        current_percent = calculate_progress_percentage(reporter.progress)

        # Update progress bar
        if current_percent != last_percent:
            print_progress_bar(current_percent)
            last_percent = current_percent

        # Show significant events
        if event.event_type == ProgressEventType.PHASE_START:
            print(f"\n▶ {event.message}")
        elif event.event_type == ProgressEventType.ARTIFACT_CREATED:
            print(f"  ✓ Created: {event.details['artifact']}")
        elif event.event_type == ProgressEventType.WARNING:
            print(f"  ⚠ {event.message}")
```

### Progress Callback Pattern

```python
def generate_skill_with_progress(
    request: SkillRequest,
    on_progress: Callable[[WorkflowProgress], None]
) -> GenerationResult:
    """Generate skill with progress callbacks."""

    reporter = ProgressReporter(request.skill_name)

    # Register progress callback
    reporter.add_listener(lambda e: on_progress(reporter.progress))

    # Execute workflow with reporting
    for phase in PHASES:
        reporter.phase_start(phase["id"])

        result = execute_phase(phase["id"], request, reporter)

        if result.success:
            reporter.phase_complete(phase["id"])
        else:
            reporter.phase_failed(phase["id"], result.error)
            break

    return result
```

## Artifact Tracking

### Artifact Status

```python
@dataclass
class ArtifactStatus:
    path: str
    status: Literal["pending", "generating", "created", "failed"]
    size_bytes: int | None
    token_count: int | None
    created_at: datetime | None

def track_artifacts(progress: WorkflowProgress) -> dict[str, ArtifactStatus]:
    """Track status of all generated artifacts."""
    return {
        "SKILL.md": ArtifactStatus(
            path="SKILL.md",
            status="created",
            size_bytes=4230,
            token_count=1847,
            created_at=datetime.now()
        ),
        "references/concepts.md": ArtifactStatus(
            path="references/concepts.md",
            status="generating",
            size_bytes=None,
            token_count=None,
            created_at=None
        ),
        # ...
    }
```

### Artifact Summary

```
Generated Artifacts:
  ✓ SKILL.md              4.2 KB  (1,847 tokens)
  ✓ references/concepts.md   2.1 KB  (892 tokens)
  ▶ references/workflow.md   generating...
  ○ scripts/validate.sh      pending

Total: 2/4 complete | 6.3 KB | 2,739 tokens
```

## Time Estimation

### ETA Calculation

```python
def estimate_remaining_time(progress: WorkflowProgress) -> float | None:
    """Estimate remaining time based on progress and elapsed time."""
    if progress.current_step == 0:
        return None

    # Calculate rate from completed work
    completed_percent = calculate_progress_percentage(progress)
    if completed_percent == 0:
        return None

    elapsed = progress.elapsed_seconds
    rate = completed_percent / elapsed  # percent per second

    remaining_percent = 100 - completed_percent
    estimated_remaining = remaining_percent / rate

    # Cap at reasonable maximum
    return min(estimated_remaining, 600)  # Max 10 minutes
```

### Display Format

```python
def format_time(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

# Usage
# Elapsed: 1m 23s | ETA: ~50s
```

## Integration with Orchestrator

```python
class SkillGeneratorOrchestrator:
    def __init__(self):
        self.reporter = None

    def generate(self, request: SkillRequest) -> GenerationResult:
        """Main generation entry point with progress reporting."""

        self.reporter = ProgressReporter(request.skill_name)

        # Print initial status
        self.show_start_banner(request)

        try:
            result = self._execute_workflow(request)
            self.show_completion_banner(result)
            return result
        except Exception as e:
            self.show_error_banner(e)
            raise

    def _execute_workflow(self, request: SkillRequest) -> GenerationResult:
        for phase in PHASES:
            self.reporter.phase_start(phase["id"])
            # ... execute phase ...
            self.reporter.phase_complete(phase["id"])

    def show_start_banner(self, request: SkillRequest) -> None:
        print(f"""
══════════════════════════════════════════════════════════════════════
  Generating Skill: {request.skill_name}
  Type: {request.skill_type}
══════════════════════════════════════════════════════════════════════
        """)

    def show_completion_banner(self, result: GenerationResult) -> None:
        print(f"""
══════════════════════════════════════════════════════════════════════
  ✓ Skill Generated Successfully!

  Location: {result.output_path}
  Quality Score: {result.quality_score}/10.0
  Total Time: {format_time(result.elapsed_seconds)}

  Next: Run 'skill-generator install {result.skill_name}' to install
══════════════════════════════════════════════════════════════════════
        """)
```
