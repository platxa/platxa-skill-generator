# Contextual Help Hints

Provide contextual tips and guidance at decision points during skill generation.

## Help Hints Purpose

| Feature | Description |
|---------|-------------|
| Decision support | Help users make informed choices |
| Best practices | Share recommended approaches |
| Error prevention | Warn about common pitfalls |
| Learning | Educate users about skill concepts |

## Hint Model

```python
from dataclasses import dataclass, field
from enum import Enum

class HintType(Enum):
    TIP = "tip"              # Helpful suggestion
    BEST_PRACTICE = "best"   # Recommended approach
    WARNING = "warning"      # Potential issue
    INFO = "info"            # Contextual information
    EXAMPLE = "example"      # Usage example

class HintTrigger(Enum):
    PHASE_START = "phase_start"
    DECISION_POINT = "decision_point"
    INPUT_FIELD = "input_field"
    VALIDATION_ERROR = "validation_error"
    COMPLETION = "completion"

class HintPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class HelpHint:
    id: str
    hint_type: HintType
    trigger: HintTrigger
    context: str              # When to show (e.g., "skill_name_input")
    title: str
    message: str
    priority: HintPriority = HintPriority.MEDIUM
    show_once: bool = False   # Only show once per session
    related_hints: list[str] = field(default_factory=list)

@dataclass
class HintContext:
    phase: str
    decision_point: str | None = None
    input_field: str | None = None
    user_input: str | None = None
    previous_choices: dict = field(default_factory=dict)
```

## Hint Registry

```python
class HintRegistry:
    """Registry of all available help hints."""

    def __init__(self):
        self.hints: dict[str, HelpHint] = {}
        self._register_default_hints()

    def _register_default_hints(self) -> None:
        """Register built-in hints."""
        # Skill naming hints
        self.register(HelpHint(
            id="skill_name_format",
            hint_type=HintType.TIP,
            trigger=HintTrigger.INPUT_FIELD,
            context="skill_name",
            title="Naming Convention",
            message=(
                "Use lowercase letters with hyphens (kebab-case). "
                "Example: 'api-doc-generator' not 'ApiDocGenerator'"
            ),
            priority=HintPriority.HIGH
        ))

        self.register(HelpHint(
            id="skill_name_length",
            hint_type=HintType.WARNING,
            trigger=HintTrigger.INPUT_FIELD,
            context="skill_name",
            title="Name Length",
            message=(
                "Keep names under 64 characters. Shorter names are "
                "easier to type when invoking the skill."
            ),
            priority=HintPriority.MEDIUM
        ))

        # Skill type hints
        self.register(HelpHint(
            id="type_builder",
            hint_type=HintType.INFO,
            trigger=HintTrigger.DECISION_POINT,
            context="skill_type:builder",
            title="Builder Skills",
            message=(
                "Builder skills generate code, files, or structures. "
                "Best for scaffolding, templates, and code generation."
            )
        ))

        self.register(HelpHint(
            id="type_guide",
            hint_type=HintType.INFO,
            trigger=HintTrigger.DECISION_POINT,
            context="skill_type:guide",
            title="Guide Skills",
            message=(
                "Guide skills provide step-by-step instructions. "
                "Best for tutorials, walkthroughs, and processes."
            )
        ))

        self.register(HelpHint(
            id="type_automation",
            hint_type=HintType.INFO,
            trigger=HintTrigger.DECISION_POINT,
            context="skill_type:automation",
            title="Automation Skills",
            message=(
                "Automation skills execute multi-step workflows. "
                "Best for repetitive tasks and batch operations."
            )
        ))

        self.register(HelpHint(
            id="type_analyzer",
            hint_type=HintType.INFO,
            trigger=HintTrigger.DECISION_POINT,
            context="skill_type:analyzer",
            title="Analyzer Skills",
            message=(
                "Analyzer skills examine code or content. "
                "Best for metrics, quality checks, and insights."
            )
        ))

        self.register(HelpHint(
            id="type_validator",
            hint_type=HintType.INFO,
            trigger=HintTrigger.DECISION_POINT,
            context="skill_type:validator",
            title="Validator Skills",
            message=(
                "Validator skills check correctness and compliance. "
                "Best for linting, schema validation, and rules."
            )
        ))

        # Reference hints
        self.register(HelpHint(
            id="ref_overview",
            hint_type=HintType.BEST_PRACTICE,
            trigger=HintTrigger.DECISION_POINT,
            context="references",
            title="Overview Reference",
            message=(
                "Include overview.md for complex skills. "
                "It provides essential context without bloating SKILL.md."
            )
        ))

        self.register(HelpHint(
            id="ref_token_budget",
            hint_type=HintType.WARNING,
            trigger=HintTrigger.DECISION_POINT,
            context="references",
            title="Token Budget",
            message=(
                "Total references should stay under 10,000 tokens. "
                "More content isn't always better - be concise."
            ),
            priority=HintPriority.HIGH
        ))

        # Phase hints
        self.register(HelpHint(
            id="phase_discovery",
            hint_type=HintType.INFO,
            trigger=HintTrigger.PHASE_START,
            context="discovery",
            title="Discovery Phase",
            message=(
                "I'll analyze your requirements to determine the "
                "best skill type and structure. Be specific about "
                "what you want the skill to accomplish."
            )
        ))

        self.register(HelpHint(
            id="phase_generation",
            hint_type=HintType.INFO,
            trigger=HintTrigger.PHASE_START,
            context="generation",
            title="Generation Phase",
            message=(
                "Generating skill files. This may take a moment. "
                "I'll create SKILL.md first, then any references."
            )
        ))

        # Validation hints
        self.register(HelpHint(
            id="validation_quality",
            hint_type=HintType.BEST_PRACTICE,
            trigger=HintTrigger.COMPLETION,
            context="validation",
            title="Quality Score",
            message=(
                "Aim for a quality score of 7.0 or higher. "
                "Lower scores may indicate missing sections or "
                "unclear instructions."
            )
        ))

    def register(self, hint: HelpHint) -> None:
        """Register a hint."""
        self.hints[hint.id] = hint

    def get(self, hint_id: str) -> HelpHint | None:
        """Get hint by ID."""
        return self.hints.get(hint_id)

    def find_by_context(self, context: str) -> list[HelpHint]:
        """Find hints matching a context."""
        matching = []
        for hint in self.hints.values():
            if hint.context == context or context.startswith(hint.context):
                matching.append(hint)
        return sorted(matching, key=lambda h: h.priority.value, reverse=True)

    def find_by_trigger(self, trigger: HintTrigger) -> list[HelpHint]:
        """Find hints by trigger type."""
        return [h for h in self.hints.values() if h.trigger == trigger]
```

## Hint Manager

```python
class HintManager:
    """Manage hint display during workflow."""

    def __init__(self, registry: HintRegistry | None = None):
        self.registry = registry or HintRegistry()
        self.shown_hints: set[str] = set()
        self.suppressed_hints: set[str] = set()

    def get_hints_for_context(
        self,
        ctx: HintContext
    ) -> list[HelpHint]:
        """Get relevant hints for current context."""
        hints = []

        # Phase start hints
        if ctx.phase:
            hints.extend(
                self.registry.find_by_context(ctx.phase)
            )

        # Decision point hints
        if ctx.decision_point:
            hints.extend(
                self.registry.find_by_context(ctx.decision_point)
            )

        # Input field hints
        if ctx.input_field:
            hints.extend(
                self.registry.find_by_context(ctx.input_field)
            )

        # Filter shown-once hints
        hints = [
            h for h in hints
            if not (h.show_once and h.id in self.shown_hints)
        ]

        # Filter suppressed hints
        hints = [
            h for h in hints
            if h.id not in self.suppressed_hints
        ]

        # Remove duplicates, keep highest priority
        seen = set()
        unique = []
        for hint in hints:
            if hint.id not in seen:
                seen.add(hint.id)
                unique.append(hint)

        return unique[:3]  # Max 3 hints at a time

    def mark_shown(self, hint_id: str) -> None:
        """Mark hint as shown."""
        self.shown_hints.add(hint_id)

    def suppress(self, hint_id: str) -> None:
        """Suppress a hint from showing."""
        self.suppressed_hints.add(hint_id)

    def get_input_hints(self, field_name: str) -> list[HelpHint]:
        """Get hints for an input field."""
        ctx = HintContext(
            phase="input",
            input_field=field_name
        )
        return self.get_hints_for_context(ctx)

    def get_decision_hints(
        self,
        decision: str,
        options: list[str] | None = None
    ) -> list[HelpHint]:
        """Get hints for a decision point."""
        hints = []

        # General decision hints
        hints.extend(self.registry.find_by_context(decision))

        # Option-specific hints
        if options:
            for opt in options:
                hints.extend(
                    self.registry.find_by_context(f"{decision}:{opt}")
                )

        return hints[:3]
```

## Hint Formatter

```python
class HintFormatter:
    """Format hints for display."""

    ICONS = {
        HintType.TIP: "💡",
        HintType.BEST_PRACTICE: "✨",
        HintType.WARNING: "⚠️",
        HintType.INFO: "ℹ️",
        HintType.EXAMPLE: "📝",
    }

    def format_hint(self, hint: HelpHint) -> str:
        """Format a single hint."""
        icon = self.ICONS.get(hint.hint_type, "•")
        return f"{icon} **{hint.title}**: {hint.message}"

    def format_hints(self, hints: list[HelpHint]) -> str:
        """Format multiple hints."""
        if not hints:
            return ""

        lines = ["", "  ───── Tips ─────"]
        for hint in hints:
            icon = self.ICONS.get(hint.hint_type, "•")
            lines.append(f"  {icon} {hint.title}")
            lines.append(f"     {hint.message}")
            lines.append("")

        return "\n".join(lines)

    def format_inline_hint(self, hint: HelpHint) -> str:
        """Format hint for inline display."""
        icon = self.ICONS.get(hint.hint_type, "•")
        return f"  {icon} {hint.message}"

    def format_hint_box(self, hints: list[HelpHint]) -> str:
        """Format hints in a box."""
        if not hints:
            return ""

        lines = []
        lines.append("  ┌─ Help ────────────────────────────────────┐")

        for hint in hints:
            icon = self.ICONS.get(hint.hint_type, "•")

            # Word wrap message
            words = hint.message.split()
            current_line = f"  │ {icon} "
            max_width = 42

            for word in words:
                if len(current_line) + len(word) + 1 > max_width:
                    lines.append(current_line.ljust(47) + "│")
                    current_line = "  │   "
                current_line += word + " "

            if current_line.strip():
                lines.append(current_line.ljust(47) + "│")
            lines.append("  │" + " " * 45 + "│")

        lines.append("  └─────────────────────────────────────────────┘")

        return "\n".join(lines)
```

## Integration

```python
def show_contextual_hints(
    phase: str,
    decision_point: str | None = None,
    input_field: str | None = None
) -> str:
    """Get formatted hints for current context."""
    manager = HintManager()
    formatter = HintFormatter()

    ctx = HintContext(
        phase=phase,
        decision_point=decision_point,
        input_field=input_field
    )

    hints = manager.get_hints_for_context(ctx)

    if not hints:
        return ""

    # Mark as shown
    for hint in hints:
        manager.mark_shown(hint.id)

    return formatter.format_hints(hints)


# Usage in workflow
def prompt_skill_name() -> str:
    """Prompt for skill name with hints."""
    hints = show_contextual_hints(
        phase="input",
        input_field="skill_name"
    )

    if hints:
        print(hints)

    # ... prompt logic ...
```

## Sample Output

```
  ───── Tips ─────
  💡 Naming Convention
     Use lowercase letters with hyphens (kebab-case).
     Example: 'api-doc-generator' not 'ApiDocGenerator'

  ⚠️ Name Length
     Keep names under 64 characters. Shorter names are
     easier to type when invoking the skill.
```

```
  ┌─ Help ────────────────────────────────────┐
  │ ✨ Builder skills generate code, files,   │
  │   or structures. Best for scaffolding,    │
  │   templates, and code generation.         │
  │                                           │
  │ ⚠️ Total references should stay under     │
  │   10,000 tokens. More content isn't       │
  │   always better - be concise.             │
  │                                           │
  └─────────────────────────────────────────────┘
```
