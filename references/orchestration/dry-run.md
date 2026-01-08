# Workflow Dry-Run Mode

Preview planned workflow steps without creating files.

## Dry-Run Purpose

| Feature | Description |
|---------|-------------|
| Preview steps | See what will happen before execution |
| Validate inputs | Check configuration without side effects |
| Estimate scope | Understand files and tokens to be generated |
| Debug workflow | Troubleshoot issues safely |

## Dry-Run Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class StepType(Enum):
    CREATE_DIR = "create_dir"
    CREATE_FILE = "create_file"
    WRITE_CONTENT = "write_content"
    RUN_VALIDATION = "run_validation"
    CALL_AGENT = "call_agent"
    USER_PROMPT = "user_prompt"

@dataclass
class PlannedStep:
    step_number: int
    phase: str
    step_type: StepType
    description: str
    target: str | None
    estimated_tokens: int | None
    will_prompt_user: bool

@dataclass
class PlannedFile:
    path: Path
    estimated_size: int
    estimated_tokens: int
    template: str | None
    description: str

@dataclass
class DryRunResult:
    skill_name: str
    total_steps: int
    steps: list[PlannedStep]
    files: list[PlannedFile]
    total_estimated_tokens: int
    estimated_duration_seconds: int
    warnings: list[str]
    would_overwrite: list[Path]
```

## Dry-Run Executor

```python
class DryRunExecutor:
    """Execute workflow in dry-run mode."""

    # Estimates based on skill type
    TOKEN_ESTIMATES = {
        "SKILL.md": (800, 1500),      # (min, max)
        "overview.md": (400, 800),
        "workflow.md": (600, 1200),
        "api.md": (500, 1000),
        "examples.md": (400, 900),
        "troubleshooting.md": (300, 600),
    }

    PHASE_DURATIONS = {
        "init": 2,
        "discovery": 30,
        "architecture": 20,
        "generation": 60,
        "validation": 15,
        "installation": 5,
    }

    def __init__(self, config: dict):
        self.config = config
        self.steps: list[PlannedStep] = []
        self.files: list[PlannedFile] = []
        self.step_counter = 0

    def execute(self) -> DryRunResult:
        """Execute dry-run and return plan."""
        skill_name = self.config.get("name", "unnamed-skill")
        install_path = Path(self.config.get("install_path", f"~/.claude/skills/{skill_name}"))

        # Plan each phase
        self._plan_init_phase()
        self._plan_discovery_phase()
        self._plan_architecture_phase()
        self._plan_generation_phase(skill_name)
        self._plan_validation_phase()
        self._plan_installation_phase(install_path)

        # Calculate totals
        total_tokens = sum(f.estimated_tokens for f in self.files)
        total_duration = sum(self.PHASE_DURATIONS.values())

        # Check for overwrites
        would_overwrite = []
        for pf in self.files:
            full_path = install_path / pf.path
            if full_path.exists():
                would_overwrite.append(full_path)

        # Collect warnings
        warnings = []
        if total_tokens > 15000:
            warnings.append(f"Estimated tokens ({total_tokens}) exceed budget (15000)")
        if would_overwrite:
            warnings.append(f"{len(would_overwrite)} existing file(s) would be overwritten")

        return DryRunResult(
            skill_name=skill_name,
            total_steps=len(self.steps),
            steps=self.steps,
            files=self.files,
            total_estimated_tokens=total_tokens,
            estimated_duration_seconds=total_duration,
            warnings=warnings,
            would_overwrite=would_overwrite
        )

    def _add_step(
        self,
        phase: str,
        step_type: StepType,
        description: str,
        target: str | None = None,
        tokens: int | None = None,
        prompts_user: bool = False
    ) -> None:
        """Add a planned step."""
        self.step_counter += 1
        self.steps.append(PlannedStep(
            step_number=self.step_counter,
            phase=phase,
            step_type=step_type,
            description=description,
            target=target,
            estimated_tokens=tokens,
            will_prompt_user=prompts_user
        ))

    def _add_file(
        self,
        path: str,
        template: str | None = None,
        description: str = ""
    ) -> None:
        """Add a planned file."""
        # Estimate tokens
        filename = Path(path).name
        min_t, max_t = self.TOKEN_ESTIMATES.get(filename, (300, 600))
        estimated = (min_t + max_t) // 2

        self.files.append(PlannedFile(
            path=Path(path),
            estimated_size=estimated * 4,  # ~4 chars per token
            estimated_tokens=estimated,
            template=template,
            description=description
        ))

    def _plan_init_phase(self) -> None:
        """Plan initialization phase."""
        self._add_step("init", StepType.USER_PROMPT,
                      "Collect skill requirements", prompts_user=True)
        self._add_step("init", StepType.RUN_VALIDATION,
                      "Validate skill name format")

    def _plan_discovery_phase(self) -> None:
        """Plan discovery phase."""
        self._add_step("discovery", StepType.CALL_AGENT,
                      "Analyze skill requirements", tokens=500)
        self._add_step("discovery", StepType.CALL_AGENT,
                      "Identify skill type", tokens=200)
        self._add_step("discovery", StepType.USER_PROMPT,
                      "Confirm skill type and scope", prompts_user=True)

    def _plan_architecture_phase(self) -> None:
        """Plan architecture phase."""
        self._add_step("architecture", StepType.CALL_AGENT,
                      "Design skill structure", tokens=400)
        self._add_step("architecture", StepType.CALL_AGENT,
                      "Plan reference files", tokens=300)

    def _plan_generation_phase(self, skill_name: str) -> None:
        """Plan generation phase."""
        # SKILL.md
        self._add_step("generation", StepType.CREATE_FILE,
                      "Generate SKILL.md", target="SKILL.md", tokens=1200)
        self._add_file("SKILL.md", description="Main skill file")

        # References
        refs = self.config.get("references", ["overview.md", "workflow.md"])
        for ref in refs:
            self._add_step("generation", StepType.CREATE_FILE,
                          f"Generate {ref}", target=f"references/{ref}", tokens=600)
            self._add_file(f"references/{ref}", description=f"Reference: {ref}")

    def _plan_validation_phase(self) -> None:
        """Plan validation phase."""
        self._add_step("validation", StepType.RUN_VALIDATION,
                      "Check YAML frontmatter")
        self._add_step("validation", StepType.RUN_VALIDATION,
                      "Validate cross-references")
        self._add_step("validation", StepType.RUN_VALIDATION,
                      "Calculate quality score", tokens=100)
        self._add_step("validation", StepType.USER_PROMPT,
                      "Review quality report", prompts_user=True)

    def _plan_installation_phase(self, install_path: Path) -> None:
        """Plan installation phase."""
        self._add_step("installation", StepType.CREATE_DIR,
                      "Create skill directory", target=str(install_path))
        self._add_step("installation", StepType.WRITE_CONTENT,
                      "Write all files")
        self._add_step("installation", StepType.RUN_VALIDATION,
                      "Verify installation")
```

## Dry-Run Formatter

```python
class DryRunFormatter:
    """Format dry-run results for display."""

    def format(self, result: DryRunResult) -> str:
        """Format complete dry-run output."""
        lines = []

        # Header
        lines.append("")
        lines.append("═" * 65)
        lines.append("  DRY RUN: " + result.skill_name)
        lines.append("  (No files will be created)")
        lines.append("═" * 65)
        lines.append("")

        # Summary
        lines.append("  SUMMARY")
        lines.append("  ───────")
        lines.append(f"  Steps:    {result.total_steps}")
        lines.append(f"  Files:    {len(result.files)}")
        lines.append(f"  Tokens:   ~{result.total_estimated_tokens:,}")
        lines.append(f"  Duration: ~{result.estimated_duration_seconds}s")
        lines.append("")

        # Warnings
        if result.warnings:
            lines.append("  ⚠ WARNINGS")
            lines.append("  ──────────")
            for warn in result.warnings:
                lines.append(f"    • {warn}")
            lines.append("")

        # Files to create
        lines.append("  FILES TO CREATE")
        lines.append("  ───────────────")
        for pf in result.files:
            tokens = f"~{pf.estimated_tokens} tokens"
            lines.append(f"    📄 {pf.path} ({tokens})")
        lines.append("")

        # Would overwrite
        if result.would_overwrite:
            lines.append("  ⚠ WOULD OVERWRITE")
            lines.append("  ─────────────────")
            for path in result.would_overwrite:
                lines.append(f"    ⚠ {path}")
            lines.append("")

        # Steps
        lines.append("  PLANNED STEPS")
        lines.append("  ─────────────")

        current_phase = None
        for step in result.steps:
            if step.phase != current_phase:
                current_phase = step.phase
                lines.append(f"\n  Phase: {current_phase.upper()}")

            icon = self._step_icon(step.step_type)
            prompt = " [user input]" if step.will_prompt_user else ""
            lines.append(f"    {step.step_number}. {icon} {step.description}{prompt}")

        lines.append("")
        lines.append("═" * 65)
        lines.append("  Run without --dry-run to execute")
        lines.append("═" * 65)
        lines.append("")

        return "\n".join(lines)

    def _step_icon(self, step_type: StepType) -> str:
        """Get icon for step type."""
        icons = {
            StepType.CREATE_DIR: "📁",
            StepType.CREATE_FILE: "📄",
            StepType.WRITE_CONTENT: "✏️",
            StepType.RUN_VALIDATION: "✓",
            StepType.CALL_AGENT: "🤖",
            StepType.USER_PROMPT: "❓",
        }
        return icons.get(step_type, "•")
```

## Integration

```python
def run_dry_run(config: dict) -> None:
    """Execute and display dry-run."""
    executor = DryRunExecutor(config)
    result = executor.execute()

    formatter = DryRunFormatter()
    print(formatter.format(result))
```

## Sample Output

```
═════════════════════════════════════════════════════════════════
  DRY RUN: api-doc-generator
  (No files will be created)
═════════════════════════════════════════════════════════════════

  SUMMARY
  ───────
  Steps:    14
  Files:    4
  Tokens:   ~3,600
  Duration: ~132s

  FILES TO CREATE
  ───────────────
    📄 SKILL.md (~1,200 tokens)
    📄 references/overview.md (~600 tokens)
    📄 references/workflow.md (~900 tokens)
    📄 references/api.md (~750 tokens)

  PLANNED STEPS
  ─────────────

  Phase: INIT
    1. ❓ Collect skill requirements [user input]
    2. ✓ Validate skill name format

  Phase: DISCOVERY
    3. 🤖 Analyze skill requirements
    4. 🤖 Identify skill type
    5. ❓ Confirm skill type and scope [user input]

  Phase: ARCHITECTURE
    6. 🤖 Design skill structure
    7. 🤖 Plan reference files

  Phase: GENERATION
    8. 📄 Generate SKILL.md
    9. 📄 Generate overview.md
    10. 📄 Generate workflow.md
    11. 📄 Generate api.md

  Phase: VALIDATION
    12. ✓ Check YAML frontmatter
    13. ✓ Validate cross-references
    14. ✓ Calculate quality score

═════════════════════════════════════════════════════════════════
  Run without --dry-run to execute
═════════════════════════════════════════════════════════════════
```
