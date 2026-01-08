# Slash Command Setup Guidance

Guide users on how to invoke their newly installed skill.

## Command Invocation

| Skill Location | Invocation | Example |
|---------------|------------|---------|
| User skills | `/<skill-name>` | `/api-doc-generator` |
| Project skills | `/<skill-name>` | `/my-project-skill` |
| With arguments | `/<skill-name> <args>` | `/commit -m "message"` |

## Setup Guidance Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class InvocationType(Enum):
    SIMPLE = "simple"           # No arguments
    WITH_ARGS = "with_args"     # Takes arguments
    INTERACTIVE = "interactive" # Multi-step workflow

@dataclass
class CommandExample:
    command: str
    description: str
    output_preview: str | None

@dataclass
class SetupGuidance:
    skill_name: str
    install_path: Path
    invocation_type: InvocationType
    primary_command: str
    examples: list[CommandExample]
    tips: list[str]
    troubleshooting: list[str]
```

## Guidance Generator

```python
class SetupGuidanceGenerator:
    """Generate setup guidance for installed skills."""

    def __init__(self, skill_name: str, install_path: Path):
        self.skill_name = skill_name
        self.install_path = install_path

    def generate(self) -> SetupGuidance:
        """Generate complete setup guidance."""
        invocation_type = self._detect_invocation_type()

        return SetupGuidance(
            skill_name=self.skill_name,
            install_path=self.install_path,
            invocation_type=invocation_type,
            primary_command=f"/{self.skill_name}",
            examples=self._generate_examples(invocation_type),
            tips=self._generate_tips(),
            troubleshooting=self._generate_troubleshooting()
        )

    def _detect_invocation_type(self) -> InvocationType:
        """Detect how skill should be invoked."""
        skill_md = self.install_path / "SKILL.md"

        if not skill_md.exists():
            return InvocationType.SIMPLE

        content = skill_md.read_text()

        # Check for argument patterns
        if "{{" in content or "${" in content or "<arg>" in content.lower():
            return InvocationType.WITH_ARGS

        # Check for workflow indicators
        workflow_keywords = ["step 1", "phase 1", "first,", "then,", "next,"]
        if any(kw in content.lower() for kw in workflow_keywords):
            return InvocationType.INTERACTIVE

        return InvocationType.SIMPLE

    def _generate_examples(self, inv_type: InvocationType) -> list[CommandExample]:
        """Generate usage examples."""
        examples = [
            CommandExample(
                command=f"/{self.skill_name}",
                description="Basic invocation",
                output_preview=None
            )
        ]

        if inv_type == InvocationType.WITH_ARGS:
            examples.extend([
                CommandExample(
                    command=f"/{self.skill_name} --help",
                    description="Show available options",
                    output_preview=None
                ),
                CommandExample(
                    command=f"/{self.skill_name} <target>",
                    description="Run with specific target",
                    output_preview=None
                )
            ])

        if inv_type == InvocationType.INTERACTIVE:
            examples.append(CommandExample(
                command=f"/{self.skill_name}",
                description="Start interactive workflow",
                output_preview="The skill will guide you through each step..."
            ))

        return examples

    def _generate_tips(self) -> list[str]:
        """Generate usage tips."""
        return [
            f"Type /{self.skill_name} to invoke the skill",
            "Skills have access to your full conversation context",
            "You can customize behavior by editing SKILL.md",
            "Reference files in references/ provide additional context"
        ]

    def _generate_troubleshooting(self) -> list[str]:
        """Generate troubleshooting guidance."""
        return [
            f"If command not found: Verify skill exists at {self.install_path}",
            "If skill not loading: Check SKILL.md has valid YAML frontmatter",
            "If behavior unexpected: Review the skill description in SKILL.md",
            "For issues: Check references/ folder for detailed documentation"
        ]
```

## Display Formatter

```python
class SetupGuidanceFormatter:
    """Format setup guidance for display."""

    def __init__(self, width: int = 65):
        self.width = width

    def format(self, guidance: SetupGuidance) -> str:
        """Format complete guidance."""
        lines = []

        # Header
        lines.extend(self._format_header(guidance))

        # How to use
        lines.extend(self._format_usage(guidance))

        # Examples
        lines.extend(self._format_examples(guidance))

        # Tips
        lines.extend(self._format_tips(guidance))

        # Troubleshooting
        lines.extend(self._format_troubleshooting(guidance))

        # Footer
        lines.extend(self._format_footer(guidance))

        return "\n".join(lines)

    def _format_header(self, g: SetupGuidance) -> list[str]:
        """Format header section."""
        w = self.width
        return [
            "",
            "╔" + "═" * (w - 2) + "╗",
            f"║  ✓ SKILL READY: {g.skill_name}".ljust(w - 1) + "║",
            "╠" + "═" * (w - 2) + "╣",
        ]

    def _format_usage(self, g: SetupGuidance) -> list[str]:
        """Format usage section."""
        w = self.width
        lines = [
            "║" + " " * (w - 2) + "║",
            "║  HOW TO USE".ljust(w - 1) + "║",
            "║  " + "─" * 10 + " " * (w - 14) + "║",
            "║" + " " * (w - 2) + "║",
        ]

        # Primary command
        cmd_line = f"║    {g.primary_command}"
        lines.append(cmd_line.ljust(w - 1) + "║")
        lines.append("║" + " " * (w - 2) + "║")

        # Invocation type hint
        if g.invocation_type == InvocationType.WITH_ARGS:
            lines.append("║    This skill accepts arguments.".ljust(w - 1) + "║")
        elif g.invocation_type == InvocationType.INTERACTIVE:
            lines.append("║    This skill runs an interactive workflow.".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")
        return lines

    def _format_examples(self, g: SetupGuidance) -> list[str]:
        """Format examples section."""
        w = self.width
        lines = [
            "╠" + "─" * (w - 2) + "╣",
            "║" + " " * (w - 2) + "║",
            "║  EXAMPLES".ljust(w - 1) + "║",
            "║  " + "─" * 8 + " " * (w - 12) + "║",
        ]

        for ex in g.examples:
            lines.append("║" + " " * (w - 2) + "║")
            lines.append(f"║    $ {ex.command}".ljust(w - 1) + "║")
            lines.append(f"║      {ex.description}".ljust(w - 1) + "║")
            if ex.output_preview:
                lines.append(f"║      → {ex.output_preview}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")
        return lines

    def _format_tips(self, g: SetupGuidance) -> list[str]:
        """Format tips section."""
        w = self.width
        lines = [
            "╠" + "─" * (w - 2) + "╣",
            "║" + " " * (w - 2) + "║",
            "║  TIPS".ljust(w - 1) + "║",
            "║  " + "─" * 4 + " " * (w - 8) + "║",
        ]

        for tip in g.tips:
            lines.append(f"║    • {tip}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")
        return lines

    def _format_troubleshooting(self, g: SetupGuidance) -> list[str]:
        """Format troubleshooting section."""
        w = self.width
        lines = [
            "╠" + "─" * (w - 2) + "╣",
            "║" + " " * (w - 2) + "║",
            "║  TROUBLESHOOTING".ljust(w - 1) + "║",
            "║  " + "─" * 15 + " " * (w - 19) + "║",
        ]

        for item in g.troubleshooting:
            # Wrap long lines
            wrapped = self._wrap_text(item, w - 8)
            for i, line in enumerate(wrapped):
                prefix = "• " if i == 0 else "  "
                lines.append(f"║    {prefix}{line}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")
        return lines

    def _format_footer(self, g: SetupGuidance) -> list[str]:
        """Format footer."""
        w = self.width
        return [
            "╠" + "─" * (w - 2) + "╣",
            f"║  Installed at: {g.install_path}".ljust(w - 1) + "║",
            "╚" + "═" * (w - 2) + "╝",
            "",
        ]

    def _wrap_text(self, text: str, width: int) -> list[str]:
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

## Quick Start Card

```python
def generate_quick_start(skill_name: str) -> str:
    """Generate quick start card."""
    return f"""
┌─────────────────────────────────────────┐
│  Quick Start: {skill_name:24} │
├─────────────────────────────────────────┤
│                                         │
│  To use this skill, type:               │
│                                         │
│    /{skill_name:32} │
│                                         │
│  in any Claude Code conversation.       │
│                                         │
└─────────────────────────────────────────┘
"""
```

## Integration

```python
def show_setup_guidance(skill_name: str, install_path: Path) -> None:
    """Display setup guidance after installation."""
    generator = SetupGuidanceGenerator(skill_name, install_path)
    guidance = generator.generate()

    formatter = SetupGuidanceFormatter()
    print(formatter.format(guidance))

    # Also show quick start
    print(generate_quick_start(skill_name))
```

## Display Format

```
╔═══════════════════════════════════════════════════════════════╗
║  ✓ SKILL READY: api-doc-generator                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  HOW TO USE                                                   ║
║  ──────────                                                   ║
║                                                               ║
║    /api-doc-generator                                         ║
║                                                               ║
║    This skill accepts arguments.                              ║
║                                                               ║
╠───────────────────────────────────────────────────────────────╣
║                                                               ║
║  EXAMPLES                                                     ║
║  ────────                                                     ║
║                                                               ║
║    $ /api-doc-generator                                       ║
║      Basic invocation                                         ║
║                                                               ║
║    $ /api-doc-generator --help                                ║
║      Show available options                                   ║
║                                                               ║
╠───────────────────────────────────────────────────────────────╣
║                                                               ║
║  TIPS                                                         ║
║  ────                                                         ║
║    • Type /api-doc-generator to invoke the skill              ║
║    • Skills have access to your full conversation context     ║
║    • You can customize behavior by editing SKILL.md           ║
║                                                               ║
╠───────────────────────────────────────────────────────────────╣
║  Installed at: ~/.claude/skills/api-doc-generator             ║
╚═══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────┐
│  Quick Start: api-doc-generator         │
├─────────────────────────────────────────┤
│                                         │
│  To use this skill, type:               │
│                                         │
│    /api-doc-generator                   │
│                                         │
│  in any Claude Code conversation.       │
│                                         │
└─────────────────────────────────────────┘
```
