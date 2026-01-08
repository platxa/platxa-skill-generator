# Error Explanation Patterns

User-friendly error explanations with actionable suggested fixes.

## Error Display Format

```
┌─────────────────────────────────────────────────────────────────┐
│  ✗ ERROR: Skill validation failed                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  What happened:                                                 │
│    The skill name contains invalid characters.                  │
│                                                                 │
│  Details:                                                       │
│    Name "My Cool Skill" contains spaces and uppercase letters.  │
│    Skill names must use hyphen-case (lowercase with hyphens).   │
│                                                                 │
│  How to fix:                                                    │
│    1. Rename to: my-cool-skill                                  │
│    2. Update SKILL.md frontmatter: name: my-cool-skill          │
│                                                                 │
│  Learn more:                                                    │
│    See: references/spec/naming-conventions.md                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error Model

```python
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    FATAL = "fatal"       # Cannot continue
    ERROR = "error"       # Blocks completion
    WARNING = "warning"   # Should fix but can continue
    INFO = "info"         # Informational

class ErrorCategory(Enum):
    VALIDATION = "validation"
    STRUCTURE = "structure"
    CONTENT = "content"
    PERMISSION = "permission"
    NETWORK = "network"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"

@dataclass
class SuggestedFix:
    description: str
    command: str | None  # Optional command to run
    example: str | None  # Example of correct value

@dataclass
class ErrorExplanation:
    code: str
    severity: ErrorSeverity
    category: ErrorCategory
    title: str
    what_happened: str
    details: str
    fixes: list[SuggestedFix]
    learn_more: str | None
    context: dict | None  # Additional context data
```

## Error Catalog

```python
ERROR_CATALOG = {
    # Validation errors
    "INVALID_SKILL_NAME": ErrorExplanation(
        code="INVALID_SKILL_NAME",
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.VALIDATION,
        title="Invalid skill name",
        what_happened="The skill name contains invalid characters.",
        details="Skill names must be 1-64 characters, lowercase, using only letters, numbers, and hyphens.",
        fixes=[
            SuggestedFix(
                description="Use hyphen-case naming",
                command=None,
                example="my-skill-name"
            ),
            SuggestedFix(
                description="Remove special characters and spaces",
                command=None,
                example="api-doc-generator (not 'API Doc Generator')"
            ),
        ],
        learn_more="references/spec/naming-conventions.md",
        context=None
    ),

    "MISSING_SKILL_MD": ErrorExplanation(
        code="MISSING_SKILL_MD",
        severity=ErrorSeverity.FATAL,
        category=ErrorCategory.STRUCTURE,
        title="Missing SKILL.md",
        what_happened="The required SKILL.md file was not found.",
        details="Every skill must have a SKILL.md file in its root directory with YAML frontmatter.",
        fixes=[
            SuggestedFix(
                description="Create SKILL.md with required frontmatter",
                command=None,
                example="---\nname: my-skill\ndescription: My skill description\n---\n# My Skill"
            ),
        ],
        learn_more="references/spec/skill-structure.md",
        context=None
    ),

    "TOKEN_BUDGET_EXCEEDED": ErrorExplanation(
        code="TOKEN_BUDGET_EXCEEDED",
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.CONTENT,
        title="Token budget exceeded",
        what_happened="The skill content exceeds the maximum token limit.",
        details="SKILL.md must be <5000 tokens, references total <10000 tokens.",
        fixes=[
            SuggestedFix(
                description="Remove redundant content",
                command=None,
                example=None
            ),
            SuggestedFix(
                description="Use references instead of repeating information",
                command=None,
                example=None
            ),
            SuggestedFix(
                description="Compress examples and code blocks",
                command=None,
                example=None
            ),
        ],
        learn_more="references/generation/token-optimization.md",
        context=None
    ),

    "QUALITY_BELOW_THRESHOLD": ErrorExplanation(
        code="QUALITY_BELOW_THRESHOLD",
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.VALIDATION,
        title="Quality score too low",
        what_happened="The skill did not meet the minimum quality threshold.",
        details="Minimum required score is 7.0/10.",
        fixes=[
            SuggestedFix(
                description="Review the quality report for specific issues",
                command="/{skill_name} --quality-report",
                example=None
            ),
            SuggestedFix(
                description="Run the improvement suggester",
                command="/{skill_name} --suggest-improvements",
                example=None
            ),
        ],
        learn_more="references/validation/quality-report.md",
        context=None
    ),

    "PERMISSION_DENIED": ErrorExplanation(
        code="PERMISSION_DENIED",
        severity=ErrorSeverity.FATAL,
        category=ErrorCategory.PERMISSION,
        title="Permission denied",
        what_happened="Cannot write to the installation directory.",
        details="The target directory requires elevated permissions or is read-only.",
        fixes=[
            SuggestedFix(
                description="Check directory permissions",
                command="ls -la ~/.claude/skills/",
                example=None
            ),
            SuggestedFix(
                description="Use a different installation location",
                command=None,
                example="Install to project directory instead of user directory"
            ),
        ],
        learn_more=None,
        context=None
    ),

    "BROKEN_REFERENCE": ErrorExplanation(
        code="BROKEN_REFERENCE",
        severity=ErrorSeverity.WARNING,
        category=ErrorCategory.CONTENT,
        title="Broken cross-reference",
        what_happened="A link points to a file or section that doesn't exist.",
        details="Cross-references must point to valid files and anchors.",
        fixes=[
            SuggestedFix(
                description="Check the target file exists",
                command=None,
                example="[link](references/overview.md) - verify overview.md exists"
            ),
            SuggestedFix(
                description="Verify anchor IDs match headings",
                command=None,
                example="[link](#section-name) - heading must be '## Section Name'"
            ),
        ],
        learn_more="references/validation/reference-accuracy.md",
        context=None
    ),
}
```

## Error Formatter

```python
class ErrorFormatter:
    """Format errors for user display."""

    def __init__(self, use_colors: bool = True, width: int = 65):
        self.use_colors = use_colors
        self.width = width

    def format(self, error: ErrorExplanation, context: dict | None = None) -> str:
        """Format error for display."""
        lines = []

        # Header
        icon = self._severity_icon(error.severity)
        color = self._severity_color(error.severity)

        lines.append(self._colored("┌" + "─" * (self.width - 2) + "┐", color))
        title_line = f"│  {icon} {error.severity.value.upper()}: {error.title}"
        lines.append(self._colored(title_line.ljust(self.width - 1) + "│", color))
        lines.append(self._colored("├" + "─" * (self.width - 2) + "┤", color))
        lines.append("│" + " " * (self.width - 2) + "│")

        # What happened
        lines.append("│  What happened:".ljust(self.width - 1) + "│")
        lines.append(f"│    {error.what_happened}".ljust(self.width - 1) + "│")
        lines.append("│" + " " * (self.width - 2) + "│")

        # Details (with context substitution)
        details = error.details
        if context:
            for key, value in context.items():
                details = details.replace(f"{{{key}}}", str(value))

        lines.append("│  Details:".ljust(self.width - 1) + "│")
        for detail_line in self._wrap(details, self.width - 6):
            lines.append(f"│    {detail_line}".ljust(self.width - 1) + "│")
        lines.append("│" + " " * (self.width - 2) + "│")

        # Fixes
        if error.fixes:
            lines.append("│  How to fix:".ljust(self.width - 1) + "│")
            for i, fix in enumerate(error.fixes, 1):
                lines.append(f"│    {i}. {fix.description}".ljust(self.width - 1) + "│")
                if fix.command:
                    cmd = fix.command
                    if context:
                        for key, value in context.items():
                            cmd = cmd.replace(f"{{{key}}}", str(value))
                    lines.append(f"│       $ {cmd}".ljust(self.width - 1) + "│")
                if fix.example:
                    lines.append(f"│       Example: {fix.example}".ljust(self.width - 1) + "│")
            lines.append("│" + " " * (self.width - 2) + "│")

        # Learn more
        if error.learn_more:
            lines.append("│  Learn more:".ljust(self.width - 1) + "│")
            lines.append(f"│    See: {error.learn_more}".ljust(self.width - 1) + "│")
            lines.append("│" + " " * (self.width - 2) + "│")

        # Footer
        lines.append(self._colored("└" + "─" * (self.width - 2) + "┘", color))

        return "\n".join(lines)

    def _severity_icon(self, severity: ErrorSeverity) -> str:
        icons = {
            ErrorSeverity.FATAL: "✗",
            ErrorSeverity.ERROR: "✗",
            ErrorSeverity.WARNING: "⚠",
            ErrorSeverity.INFO: "ℹ",
        }
        return icons.get(severity, "●")

    def _severity_color(self, severity: ErrorSeverity) -> str:
        colors = {
            ErrorSeverity.FATAL: "\033[91m",   # Red
            ErrorSeverity.ERROR: "\033[91m",   # Red
            ErrorSeverity.WARNING: "\033[93m", # Yellow
            ErrorSeverity.INFO: "\033[94m",    # Blue
        }
        return colors.get(severity, "")

    def _colored(self, text: str, color: str) -> str:
        if self.use_colors and color:
            return f"{color}{text}\033[0m"
        return text

    def _wrap(self, text: str, width: int) -> list[str]:
        """Wrap text to width."""
        words = text.split()
        lines = []
        current = []
        current_len = 0

        for word in words:
            if current_len + len(word) + 1 > width:
                lines.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += len(word) + 1

        if current:
            lines.append(" ".join(current))

        return lines
```

## Error Lookup

```python
def explain_error(
    code: str,
    context: dict | None = None,
    use_colors: bool = True
) -> str:
    """Look up and format an error explanation."""
    if code not in ERROR_CATALOG:
        # Generic error
        explanation = ErrorExplanation(
            code=code,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.VALIDATION,
            title=code.replace("_", " ").title(),
            what_happened="An error occurred during skill processing.",
            details=f"Error code: {code}",
            fixes=[
                SuggestedFix(
                    description="Check the error code documentation",
                    command=None,
                    example=None
                ),
            ],
            learn_more=None,
            context=context
        )
    else:
        explanation = ERROR_CATALOG[code]

    formatter = ErrorFormatter(use_colors=use_colors)
    return formatter.format(explanation, context)
```

## Integration

```python
def handle_error(
    code: str,
    context: dict | None = None,
    raise_exception: bool = True
) -> None:
    """Handle an error with user-friendly explanation."""
    # Display explanation
    print(explain_error(code, context))

    # Exit or raise based on severity
    explanation = ERROR_CATALOG.get(code)
    if explanation and explanation.severity == ErrorSeverity.FATAL:
        if raise_exception:
            raise SystemExit(1)
```
