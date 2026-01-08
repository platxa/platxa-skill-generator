# Feedback Collection Pattern

Structured patterns for collecting user feedback during skill generation.

## Feedback Types

| Type | When | Purpose |
|------|------|---------|
| Clarification | Discovery | Resolve ambiguity |
| Preference | Architecture | Choose between options |
| Validation | Generation | Confirm correctness |
| Approval | Validation | Accept/reject quality |
| Iteration | Quality loop | Guide improvements |

## Feedback Model

```python
from dataclasses import dataclass
from enum import Enum
from typing import Any

class FeedbackType(Enum):
    CLARIFICATION = "clarification"
    PREFERENCE = "preference"
    VALIDATION = "validation"
    APPROVAL = "approval"
    ITERATION = "iteration"
    FREE_TEXT = "free_text"

class ResponseType(Enum):
    SINGLE_CHOICE = "single"
    MULTI_CHOICE = "multi"
    YES_NO = "yes_no"
    SCALE = "scale"
    TEXT = "text"

@dataclass
class FeedbackOption:
    id: str
    label: str
    description: str | None
    is_recommended: bool = False

@dataclass
class FeedbackPrompt:
    id: str
    type: FeedbackType
    question: str
    context: str | None
    response_type: ResponseType
    options: list[FeedbackOption] | None
    default: str | None
    required: bool
    timeout_seconds: int | None

@dataclass
class FeedbackResponse:
    prompt_id: str
    value: Any
    timestamp: str
    skipped: bool
```

## Prompt Templates

```python
FEEDBACK_TEMPLATES = {
    "skill_type_clarification": FeedbackPrompt(
        id="skill_type",
        type=FeedbackType.CLARIFICATION,
        question="What type of skill is this?",
        context="Based on your description, this could be either a builder or an automation skill.",
        response_type=ResponseType.SINGLE_CHOICE,
        options=[
            FeedbackOption("builder", "Builder", "Generates files/content from templates", True),
            FeedbackOption("automation", "Automation", "Executes workflows/scripts"),
        ],
        default="builder",
        required=True,
        timeout_seconds=None
    ),

    "output_format_preference": FeedbackPrompt(
        id="output_format",
        type=FeedbackType.PREFERENCE,
        question="Which output format do you prefer?",
        context=None,
        response_type=ResponseType.SINGLE_CHOICE,
        options=[
            FeedbackOption("markdown", "Markdown", "Human-readable documentation"),
            FeedbackOption("json", "JSON", "Machine-parseable data"),
            FeedbackOption("both", "Both", "Generate both formats", True),
        ],
        default="markdown",
        required=False,
        timeout_seconds=30
    ),

    "quality_approval": FeedbackPrompt(
        id="quality_approval",
        type=FeedbackType.APPROVAL,
        question="Does the generated skill meet your requirements?",
        context="Quality score: {score}/10",
        response_type=ResponseType.YES_NO,
        options=None,
        default="yes",
        required=True,
        timeout_seconds=None
    ),

    "improvement_direction": FeedbackPrompt(
        id="improvement",
        type=FeedbackType.ITERATION,
        question="Which areas need improvement?",
        context="Select all that apply:",
        response_type=ResponseType.MULTI_CHOICE,
        options=[
            FeedbackOption("clarity", "Clarity", "Make documentation clearer"),
            FeedbackOption("examples", "Examples", "Add more/better examples"),
            FeedbackOption("completeness", "Completeness", "Add missing content"),
            FeedbackOption("accuracy", "Accuracy", "Fix incorrect information"),
            FeedbackOption("other", "Other", "Provide custom feedback"),
        ],
        default=None,
        required=True,
        timeout_seconds=None
    ),

    "custom_feedback": FeedbackPrompt(
        id="custom",
        type=FeedbackType.FREE_TEXT,
        question="Please describe what needs to change:",
        context=None,
        response_type=ResponseType.TEXT,
        options=None,
        default=None,
        required=False,
        timeout_seconds=None
    ),
}
```

## Feedback Collector

```python
class FeedbackCollector:
    """Collect structured feedback from users."""

    def __init__(self, mode: str = "interactive"):
        self.mode = mode  # interactive, batch, auto
        self.responses: list[FeedbackResponse] = []

    def ask(self, prompt: FeedbackPrompt) -> FeedbackResponse:
        """Ask for feedback based on prompt type."""
        if self.mode == "auto":
            return self._auto_respond(prompt)

        renderers = {
            ResponseType.SINGLE_CHOICE: self._ask_single_choice,
            ResponseType.MULTI_CHOICE: self._ask_multi_choice,
            ResponseType.YES_NO: self._ask_yes_no,
            ResponseType.SCALE: self._ask_scale,
            ResponseType.TEXT: self._ask_text,
        }

        renderer = renderers.get(prompt.response_type, self._ask_text)
        response = renderer(prompt)

        self.responses.append(response)
        return response

    def _auto_respond(self, prompt: FeedbackPrompt) -> FeedbackResponse:
        """Auto-respond using defaults or recommended options."""
        if prompt.default:
            value = prompt.default
        elif prompt.options:
            recommended = [o for o in prompt.options if o.is_recommended]
            value = recommended[0].id if recommended else prompt.options[0].id
        else:
            value = ""

        return FeedbackResponse(
            prompt_id=prompt.id,
            value=value,
            timestamp=self._timestamp(),
            skipped=False
        )

    def _timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

## Display Formatters

```python
class FeedbackFormatter:
    """Format feedback prompts for display."""

    def format_prompt(self, prompt: FeedbackPrompt) -> str:
        """Format prompt for display."""
        lines = []

        # Question
        lines.append("")
        lines.append(f"❓ {prompt.question}")

        # Context
        if prompt.context:
            lines.append(f"   {prompt.context}")

        lines.append("")

        # Options
        if prompt.options:
            for i, opt in enumerate(prompt.options, 1):
                rec = " (recommended)" if opt.is_recommended else ""
                desc = f" - {opt.description}" if opt.description else ""
                lines.append(f"   [{i}] {opt.label}{rec}{desc}")
            lines.append("")

        # Input hint
        if prompt.response_type == ResponseType.SINGLE_CHOICE:
            lines.append("   Enter number or name: ")
        elif prompt.response_type == ResponseType.MULTI_CHOICE:
            lines.append("   Enter numbers separated by comma: ")
        elif prompt.response_type == ResponseType.YES_NO:
            default = "[Y/n]" if prompt.default == "yes" else "[y/N]"
            lines.append(f"   {default}: ")
        elif prompt.response_type == ResponseType.TEXT:
            lines.append("   > ")

        return "\n".join(lines)

    def format_response(self, prompt: FeedbackPrompt, response: FeedbackResponse) -> str:
        """Format response confirmation."""
        if response.skipped:
            return "   ⏭ Skipped"

        value = response.value
        if prompt.options:
            option = next((o for o in prompt.options if o.id == value), None)
            if option:
                value = option.label

        return f"   ✓ Selected: {value}"
```

## Structured Prompt Patterns

### Clarification Pattern

```python
def ask_clarification(
    question: str,
    options: list[tuple[str, str]],  # (id, label)
    context: str | None = None
) -> FeedbackPrompt:
    """Create a clarification prompt."""
    return FeedbackPrompt(
        id=f"clarify_{hash(question) % 10000}",
        type=FeedbackType.CLARIFICATION,
        question=question,
        context=context,
        response_type=ResponseType.SINGLE_CHOICE,
        options=[
            FeedbackOption(id=opt[0], label=opt[1], description=None)
            for opt in options
        ],
        default=options[0][0] if options else None,
        required=True,
        timeout_seconds=None
    )
```

### Preference Pattern

```python
def ask_preference(
    question: str,
    options: list[tuple[str, str, str | None]],  # (id, label, description)
    recommended: str | None = None
) -> FeedbackPrompt:
    """Create a preference prompt."""
    return FeedbackPrompt(
        id=f"pref_{hash(question) % 10000}",
        type=FeedbackType.PREFERENCE,
        question=question,
        context=None,
        response_type=ResponseType.SINGLE_CHOICE,
        options=[
            FeedbackOption(
                id=opt[0],
                label=opt[1],
                description=opt[2],
                is_recommended=(opt[0] == recommended)
            )
            for opt in options
        ],
        default=recommended,
        required=False,
        timeout_seconds=60
    )
```

### Approval Pattern

```python
def ask_approval(
    item: str,
    context: str | None = None,
    default_approve: bool = True
) -> FeedbackPrompt:
    """Create an approval prompt."""
    return FeedbackPrompt(
        id=f"approve_{hash(item) % 10000}",
        type=FeedbackType.APPROVAL,
        question=f"Do you approve the {item}?",
        context=context,
        response_type=ResponseType.YES_NO,
        options=None,
        default="yes" if default_approve else "no",
        required=True,
        timeout_seconds=None
    )
```

### Iteration Pattern

```python
def ask_iteration_feedback(
    current_quality: float,
    dimensions: dict[str, float]
) -> FeedbackPrompt:
    """Create an iteration feedback prompt."""
    context_lines = [f"Current quality: {current_quality:.1f}/10"]
    for dim, score in dimensions.items():
        status = "✓" if score >= 7.0 else "⚠"
        context_lines.append(f"  {status} {dim}: {score:.1f}")

    low_dims = [d for d, s in dimensions.items() if s < 7.0]

    return FeedbackPrompt(
        id="iteration_feedback",
        type=FeedbackType.ITERATION,
        question="Which areas should be improved?",
        context="\n".join(context_lines),
        response_type=ResponseType.MULTI_CHOICE,
        options=[
            FeedbackOption(
                id=dim,
                label=dim.title(),
                description=None,
                is_recommended=(dim in low_dims)
            )
            for dim in dimensions
        ],
        default=None,
        required=True,
        timeout_seconds=None
    )
```

## Integration with Workflow

```python
class WorkflowFeedbackIntegration:
    """Integrate feedback collection with skill generation workflow."""

    def __init__(self, collector: FeedbackCollector):
        self.collector = collector

    def discovery_feedback(self, findings: dict) -> dict:
        """Collect feedback during discovery phase."""
        responses = {}

        # Clarify skill type if ambiguous
        if findings.get("type_ambiguous"):
            prompt = ask_clarification(
                "What type of skill is this?",
                [
                    ("builder", "Builder - generates content"),
                    ("guide", "Guide - provides information"),
                    ("automation", "Automation - runs workflows"),
                ],
                context="Based on your description, multiple types could apply."
            )
            response = self.collector.ask(prompt)
            responses["skill_type"] = response.value

        return responses

    def validation_feedback(self, quality_score: float) -> bool:
        """Collect approval after validation."""
        prompt = ask_approval(
            "generated skill",
            context=f"Quality score: {quality_score:.1f}/10",
            default_approve=(quality_score >= 7.0)
        )
        response = self.collector.ask(prompt)
        return response.value in ("yes", "y", True)

    def iteration_feedback(
        self,
        quality_score: float,
        dimensions: dict[str, float]
    ) -> list[str]:
        """Collect improvement feedback for iteration."""
        prompt = ask_iteration_feedback(quality_score, dimensions)
        response = self.collector.ask(prompt)

        if isinstance(response.value, list):
            return response.value
        return [response.value] if response.value else []
```
