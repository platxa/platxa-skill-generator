# Multi-Select Feature Options

Enable users to select multiple options simultaneously using AskUserQuestion.

## Multi-Select Purpose

| Feature | Description |
|---------|-------------|
| Batch selection | Select multiple items at once |
| Efficient input | Reduce number of prompts |
| Flexible choices | Non-mutually exclusive options |
| Feature bundling | Group related capabilities |

## Multi-Select Model

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class SelectionMode(Enum):
    SINGLE = "single"        # One option only
    MULTI = "multi"          # Multiple options
    REQUIRED_ONE = "one"     # At least one required
    OPTIONAL = "optional"    # Zero or more

@dataclass
class SelectOption:
    label: str
    description: str
    value: Any
    default_selected: bool = False
    mutually_exclusive_with: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)

@dataclass
class MultiSelectQuestion:
    question: str
    header: str
    options: list[SelectOption]
    mode: SelectionMode = SelectionMode.MULTI
    min_selections: int = 0
    max_selections: int | None = None

@dataclass
class MultiSelectResult:
    selected_values: list[Any]
    selected_labels: list[str]
    is_valid: bool
    validation_error: str | None = None
```

## Multi-Select Builder

```python
class MultiSelectBuilder:
    """Build multi-select questions for skill generation."""

    # Predefined option sets
    REFERENCE_OPTIONS = [
        SelectOption(
            label="Overview",
            description="High-level skill documentation",
            value="overview.md",
            default_selected=True
        ),
        SelectOption(
            label="Workflow",
            description="Step-by-step process guide",
            value="workflow.md",
            default_selected=True
        ),
        SelectOption(
            label="API Reference",
            description="Detailed API documentation",
            value="api.md"
        ),
        SelectOption(
            label="Examples",
            description="Usage examples and samples",
            value="examples.md"
        ),
        SelectOption(
            label="Troubleshooting",
            description="Common issues and solutions",
            value="troubleshooting.md"
        ),
        SelectOption(
            label="Glossary",
            description="Term definitions",
            value="glossary.md"
        ),
    ]

    FEATURE_OPTIONS = [
        SelectOption(
            label="Input validation",
            description="Validate user inputs before processing",
            value="input_validation"
        ),
        SelectOption(
            label="Progress tracking",
            description="Show progress during execution",
            value="progress_tracking"
        ),
        SelectOption(
            label="Error recovery",
            description="Handle errors gracefully with retry",
            value="error_recovery"
        ),
        SelectOption(
            label="Dry-run mode",
            description="Preview changes without executing",
            value="dry_run"
        ),
        SelectOption(
            label="Verbose output",
            description="Detailed logging and output",
            value="verbose_output"
        ),
        SelectOption(
            label="Configuration file",
            description="Support external config files",
            value="config_file"
        ),
    ]

    OUTPUT_FORMAT_OPTIONS = [
        SelectOption(
            label="Markdown",
            description="Standard markdown output",
            value="markdown",
            default_selected=True
        ),
        SelectOption(
            label="JSON",
            description="Machine-readable JSON",
            value="json"
        ),
        SelectOption(
            label="Plain text",
            description="Simple text output",
            value="text"
        ),
        SelectOption(
            label="HTML",
            description="Web-ready HTML",
            value="html"
        ),
    ]

    def build_reference_question(self) -> MultiSelectQuestion:
        """Build question for reference file selection."""
        return MultiSelectQuestion(
            question="Which reference files should be generated?",
            header="References",
            options=self.REFERENCE_OPTIONS,
            mode=SelectionMode.MULTI,
            min_selections=0,
            max_selections=None
        )

    def build_feature_question(self) -> MultiSelectQuestion:
        """Build question for feature selection."""
        return MultiSelectQuestion(
            question="Which features do you want to include?",
            header="Features",
            options=self.FEATURE_OPTIONS,
            mode=SelectionMode.MULTI,
            min_selections=0
        )

    def build_output_format_question(self) -> MultiSelectQuestion:
        """Build question for output format selection."""
        return MultiSelectQuestion(
            question="Which output formats should be supported?",
            header="Formats",
            options=self.OUTPUT_FORMAT_OPTIONS,
            mode=SelectionMode.REQUIRED_ONE,
            min_selections=1
        )

    def build_custom_question(
        self,
        question: str,
        header: str,
        options: list[dict]
    ) -> MultiSelectQuestion:
        """Build custom multi-select question."""
        select_options = [
            SelectOption(
                label=opt["label"],
                description=opt.get("description", ""),
                value=opt.get("value", opt["label"]),
                default_selected=opt.get("default", False)
            )
            for opt in options
        ]

        return MultiSelectQuestion(
            question=question,
            header=header,
            options=select_options,
            mode=SelectionMode.MULTI
        )
```

## Claude Code Integration

```python
class AskUserQuestionFormatter:
    """Format multi-select for AskUserQuestion tool."""

    def format_question(
        self,
        msq: MultiSelectQuestion
    ) -> dict:
        """Format for Claude Code AskUserQuestion tool."""
        options = []

        for opt in msq.options:
            option_dict = {
                "label": opt.label,
                "description": opt.description
            }
            options.append(option_dict)

        return {
            "questions": [{
                "question": msq.question,
                "header": msq.header,
                "options": options,
                "multiSelect": msq.mode in (
                    SelectionMode.MULTI,
                    SelectionMode.OPTIONAL
                )
            }]
        }

    def format_multiple_questions(
        self,
        questions: list[MultiSelectQuestion]
    ) -> dict:
        """Format multiple questions for single tool call."""
        formatted = []

        for msq in questions[:4]:  # Max 4 questions
            q_dict = {
                "question": msq.question,
                "header": msq.header,
                "options": [
                    {
                        "label": opt.label,
                        "description": opt.description
                    }
                    for opt in msq.options[:4]  # Max 4 options
                ],
                "multiSelect": msq.mode in (
                    SelectionMode.MULTI,
                    SelectionMode.OPTIONAL
                )
            }
            formatted.append(q_dict)

        return {"questions": formatted}
```

## Selection Validator

```python
class SelectionValidator:
    """Validate multi-select responses."""

    def validate(
        self,
        question: MultiSelectQuestion,
        selected: list[str]
    ) -> MultiSelectResult:
        """Validate selection against question constraints."""
        # Map labels to options
        option_map = {opt.label: opt for opt in question.options}

        # Check all selected are valid options
        invalid = [s for s in selected if s not in option_map]
        if invalid:
            return MultiSelectResult(
                selected_values=[],
                selected_labels=selected,
                is_valid=False,
                validation_error=f"Invalid options: {', '.join(invalid)}"
            )

        # Check minimum selections
        if len(selected) < question.min_selections:
            return MultiSelectResult(
                selected_values=[],
                selected_labels=selected,
                is_valid=False,
                validation_error=(
                    f"At least {question.min_selections} "
                    f"selection(s) required"
                )
            )

        # Check maximum selections
        if question.max_selections and len(selected) > question.max_selections:
            return MultiSelectResult(
                selected_values=[],
                selected_labels=selected,
                is_valid=False,
                validation_error=(
                    f"Maximum {question.max_selections} "
                    f"selection(s) allowed"
                )
            )

        # Check mutual exclusivity
        for label in selected:
            opt = option_map[label]
            conflicts = set(opt.mutually_exclusive_with) & set(selected)
            if conflicts:
                return MultiSelectResult(
                    selected_values=[],
                    selected_labels=selected,
                    is_valid=False,
                    validation_error=(
                        f"'{label}' cannot be selected with: "
                        f"{', '.join(conflicts)}"
                    )
                )

        # Check requirements
        for label in selected:
            opt = option_map[label]
            missing = set(opt.requires) - set(selected)
            if missing:
                return MultiSelectResult(
                    selected_values=[],
                    selected_labels=selected,
                    is_valid=False,
                    validation_error=(
                        f"'{label}' requires: {', '.join(missing)}"
                    )
                )

        # Extract values
        values = [option_map[label].value for label in selected]

        return MultiSelectResult(
            selected_values=values,
            selected_labels=selected,
            is_valid=True
        )

    def apply_defaults(
        self,
        question: MultiSelectQuestion
    ) -> list[str]:
        """Get default selections for a question."""
        return [
            opt.label
            for opt in question.options
            if opt.default_selected
        ]
```

## Selection Formatter

```python
class SelectionFormatter:
    """Format selection results for display."""

    def format_question_preview(
        self,
        question: MultiSelectQuestion
    ) -> str:
        """Format question for preview."""
        lines = []

        lines.append(f"  {question.question}")
        lines.append(f"  [{question.header}]")
        lines.append("")

        for i, opt in enumerate(question.options, 1):
            default = " (default)" if opt.default_selected else ""
            lines.append(f"  [ ] {opt.label}{default}")
            lines.append(f"      {opt.description}")

        mode_hint = {
            SelectionMode.SINGLE: "Select one",
            SelectionMode.MULTI: "Select multiple",
            SelectionMode.REQUIRED_ONE: "Select at least one",
            SelectionMode.OPTIONAL: "Optional selection"
        }
        lines.append("")
        lines.append(f"  Mode: {mode_hint.get(question.mode, '')}")

        return "\n".join(lines)

    def format_selection_summary(
        self,
        result: MultiSelectResult
    ) -> str:
        """Format selection result summary."""
        lines = []

        if not result.is_valid:
            lines.append(f"  ✗ Invalid selection: {result.validation_error}")
            return "\n".join(lines)

        if not result.selected_labels:
            lines.append("  ○ No options selected")
        else:
            lines.append(f"  ✓ Selected {len(result.selected_labels)} option(s):")
            for label in result.selected_labels:
                lines.append(f"    • {label}")

        return "\n".join(lines)
```

## Integration

```python
def ask_multi_select(
    question: str,
    header: str,
    options: list[dict],
    min_selections: int = 0
) -> dict:
    """Create multi-select question for Claude Code.

    Returns dict ready for AskUserQuestion tool.

    Example usage in skill:
        Use AskUserQuestion with these parameters:
        {
            "questions": [{
                "question": "Which features do you want?",
                "header": "Features",
                "options": [
                    {"label": "Feature A", "description": "Does A"},
                    {"label": "Feature B", "description": "Does B"}
                ],
                "multiSelect": true
            }]
        }
    """
    builder = MultiSelectBuilder()
    msq = builder.build_custom_question(question, header, options)
    msq.min_selections = min_selections

    formatter = AskUserQuestionFormatter()
    return formatter.format_question(msq)


def process_multi_select_response(
    question: MultiSelectQuestion,
    response: dict
) -> MultiSelectResult:
    """Process response from AskUserQuestion."""
    # Extract selected labels from response
    # Response format: {"answers": {"0": "Label1, Label2"}}
    answer = response.get("answers", {}).get("0", "")

    if not answer:
        selected = []
    else:
        selected = [s.strip() for s in answer.split(",")]

    validator = SelectionValidator()
    return validator.validate(question, selected)
```

## Sample Tool Call

```json
{
    "questions": [
        {
            "question": "Which reference files should be generated?",
            "header": "References",
            "options": [
                {
                    "label": "Overview",
                    "description": "High-level skill documentation"
                },
                {
                    "label": "Workflow",
                    "description": "Step-by-step process guide"
                },
                {
                    "label": "Examples",
                    "description": "Usage examples and samples"
                },
                {
                    "label": "Troubleshooting",
                    "description": "Common issues and solutions"
                }
            ],
            "multiSelect": true
        },
        {
            "question": "Which output formats should be supported?",
            "header": "Formats",
            "options": [
                {
                    "label": "Markdown (Recommended)",
                    "description": "Standard markdown output"
                },
                {
                    "label": "JSON",
                    "description": "Machine-readable JSON"
                },
                {
                    "label": "Plain text",
                    "description": "Simple text output"
                }
            ],
            "multiSelect": true
        }
    ]
}
```

## Usage Guidelines

| Scenario | Mode | Min | Max |
|----------|------|-----|-----|
| Reference files | MULTI | 0 | - |
| Required features | REQUIRED_ONE | 1 | - |
| Output formats | REQUIRED_ONE | 1 | 3 |
| Optional extras | OPTIONAL | 0 | - |
| Single choice | SINGLE | 1 | 1 |
