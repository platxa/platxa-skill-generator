# Completion Summary Display

Display comprehensive summary after skill generation completes.

## Summary Display

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ✓ SKILL GENERATED SUCCESSFULLY                                  ║
║                                                                   ║
║   api-doc-generator                                               ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   FILES CREATED                                                   ║
║   ─────────────                                                   ║
║   📄 SKILL.md                           1.2 KB    312 tokens     ║
║   📁 references/                                                  ║
║      📄 overview.md                     2.4 KB    598 tokens     ║
║      📄 workflow.md                     3.1 KB    782 tokens     ║
║      📄 api.md                          2.8 KB    701 tokens     ║
║      📄 troubleshooting.md              1.8 KB    456 tokens     ║
║   📁 scripts/                                                     ║
║      ⚙️ generate.sh                     1.5 KB                    ║
║                                                                   ║
║   Total: 6 files, 12.8 KB, 2,849 tokens                          ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   QUALITY SCORE                                                   ║
║   ─────────────                                                   ║
║   Overall: 8.2/10 ████████░░                                     ║
║                                                                   ║
║   Clarity       8.5  ████████░░                                  ║
║   Completeness  7.8  ████████░░                                  ║
║   Examples      8.0  ████████░░                                  ║
║   Structure     8.5  ████████░░                                  ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   NEXT STEPS                                                      ║
║   ──────────                                                      ║
║   1. Try the skill: /api-doc-generator                           ║
║   2. View full docs: cat ~/.claude/skills/api-doc-generator/     ║
║   3. Customize: Edit SKILL.md to adjust behavior                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## Completion Model

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class GeneratedFile:
    path: str
    size_bytes: int
    tokens: int | None
    is_directory: bool

@dataclass
class QualityBreakdown:
    dimension: str
    score: float
    max_score: float

@dataclass
class NextStep:
    number: int
    description: str
    command: str | None

@dataclass
class CompletionSummary:
    skill_name: str
    status: str  # success, partial, failed
    install_path: Path
    files: list[GeneratedFile]
    total_size: int
    total_tokens: int
    quality_score: float | None
    quality_breakdown: list[QualityBreakdown]
    next_steps: list[NextStep]
    duration_seconds: float
    warnings: list[str]
    timestamp: datetime
```

## Summary Formatter

```python
class CompletionSummaryFormatter:
    """Format completion summary for display."""

    def __init__(self, width: int = 70, use_colors: bool = True):
        self.width = width
        self.use_colors = use_colors

    def format(self, summary: CompletionSummary) -> str:
        """Format complete summary."""
        lines = []

        # Header
        lines.extend(self._format_header(summary))

        # Files section
        lines.extend(self._format_files(summary))

        # Quality section
        if summary.quality_score is not None:
            lines.extend(self._format_quality(summary))

        # Next steps
        lines.extend(self._format_next_steps(summary))

        # Warnings
        if summary.warnings:
            lines.extend(self._format_warnings(summary))

        # Footer
        lines.extend(self._format_footer(summary))

        return "\n".join(lines)

    def _format_header(self, s: CompletionSummary) -> list[str]:
        """Format header section."""
        w = self.width

        # Status icon and color
        if s.status == "success":
            icon = "✓"
            title = "SKILL GENERATED SUCCESSFULLY"
            color = "\033[92m"  # Green
        elif s.status == "partial":
            icon = "⚠"
            title = "SKILL GENERATED WITH WARNINGS"
            color = "\033[93m"  # Yellow
        else:
            icon = "✗"
            title = "SKILL GENERATION FAILED"
            color = "\033[91m"  # Red

        lines = [
            self._colored("╔" + "═" * (w - 2) + "╗", color),
            self._colored("║" + " " * (w - 2) + "║", color),
            self._colored(f"║   {icon} {title}".ljust(w - 1) + "║", color),
            self._colored("║" + " " * (w - 2) + "║", color),
            self._colored(f"║   {s.skill_name}".ljust(w - 1) + "║", color),
            self._colored("║" + " " * (w - 2) + "║", color),
            self._colored("╠" + "═" * (w - 2) + "╣", color),
        ]

        return lines

    def _format_files(self, s: CompletionSummary) -> list[str]:
        """Format files section."""
        w = self.width
        lines = [
            "║" + " " * (w - 2) + "║",
            "║   FILES CREATED".ljust(w - 1) + "║",
            "║   " + "─" * 13 + " " * (w - 17) + "║",
        ]

        # Build tree structure
        tree = self._build_tree(s.files)
        tree_lines = self._render_tree(tree, s.files)

        for line in tree_lines:
            lines.append(f"║   {line}".ljust(w - 1) + "║")

        # Totals
        total_files = len([f for f in s.files if not f.is_directory])
        total_size = self._format_size(s.total_size)
        lines.append("║" + " " * (w - 2) + "║")
        lines.append(
            f"║   Total: {total_files} files, {total_size}, {s.total_tokens:,} tokens".ljust(w - 1) + "║"
        )
        lines.append("║" + " " * (w - 2) + "║")
        lines.append("╠" + "═" * (w - 2) + "╣")

        return lines

    def _build_tree(self, files: list[GeneratedFile]) -> dict:
        """Build tree structure from file list."""
        tree: dict = {}
        for f in files:
            parts = Path(f.path).parts
            current = tree
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {"_files": [], "_dirs": {}}
                if i == len(parts) - 1 and not f.is_directory:
                    current[part]["_files"].append(f)
                else:
                    current = current[part]["_dirs"]
        return tree

    def _render_tree(
        self,
        tree: dict,
        all_files: list[GeneratedFile],
        indent: str = ""
    ) -> list[str]:
        """Render tree as lines."""
        lines = []

        for name, node in sorted(tree.items()):
            # Check if directory
            is_dir = bool(node.get("_dirs")) or name.endswith("/")

            if is_dir:
                lines.append(f"{indent}📁 {name}/")
                # Render children
                child_lines = self._render_tree(
                    node.get("_dirs", {}),
                    all_files,
                    indent + "   "
                )
                lines.extend(child_lines)
            else:
                # Find file info
                file_info = next(
                    (f for f in all_files if f.path.endswith(name)),
                    None
                )
                if file_info:
                    icon = self._file_icon(name)
                    size = self._format_size(file_info.size_bytes)
                    tokens = f"{file_info.tokens:,} tokens" if file_info.tokens else ""
                    lines.append(f"{indent}{icon} {name:25} {size:>8}  {tokens}")

        return lines

    def _format_quality(self, s: CompletionSummary) -> list[str]:
        """Format quality section."""
        w = self.width
        lines = [
            "║" + " " * (w - 2) + "║",
            "║   QUALITY SCORE".ljust(w - 1) + "║",
            "║   " + "─" * 13 + " " * (w - 17) + "║",
        ]

        # Overall score
        bar = self._score_bar(s.quality_score or 0, 10)
        lines.append(f"║   Overall: {s.quality_score:.1f}/10 {bar}".ljust(w - 1) + "║")
        lines.append("║" + " " * (w - 2) + "║")

        # Breakdown
        for q in s.quality_breakdown:
            bar = self._score_bar(q.score, q.max_score)
            lines.append(f"║   {q.dimension:14} {q.score:.1f}  {bar}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")
        lines.append("╠" + "═" * (w - 2) + "╣")

        return lines

    def _format_next_steps(self, s: CompletionSummary) -> list[str]:
        """Format next steps section."""
        w = self.width
        lines = [
            "║" + " " * (w - 2) + "║",
            "║   NEXT STEPS".ljust(w - 1) + "║",
            "║   " + "─" * 10 + " " * (w - 14) + "║",
        ]

        for step in s.next_steps:
            lines.append(f"║   {step.number}. {step.description}".ljust(w - 1) + "║")
            if step.command:
                lines.append(f"║      $ {step.command}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")

        return lines

    def _format_warnings(self, s: CompletionSummary) -> list[str]:
        """Format warnings section."""
        w = self.width
        lines = [
            "╠" + "═" * (w - 2) + "╣",
            "║" + " " * (w - 2) + "║",
            "║   ⚠ WARNINGS".ljust(w - 1) + "║",
            "║   " + "─" * 10 + " " * (w - 14) + "║",
        ]

        for warn in s.warnings:
            lines.append(f"║   • {warn}".ljust(w - 1) + "║")

        lines.append("║" + " " * (w - 2) + "║")

        return lines

    def _format_footer(self, s: CompletionSummary) -> list[str]:
        """Format footer."""
        w = self.width
        return [
            "╚" + "═" * (w - 2) + "╝",
            "",
            f"Generated in {s.duration_seconds:.1f}s at {s.timestamp.strftime('%H:%M:%S')}",
        ]

    def _colored(self, text: str, color: str) -> str:
        if self.use_colors and color:
            return f"{color}{text}\033[0m"
        return text

    def _score_bar(self, score: float, max_score: float, width: int = 10) -> str:
        filled = int(score / max_score * width)
        return "█" * filled + "░" * (width - filled)

    def _format_size(self, bytes: int) -> str:
        if bytes < 1024:
            return f"{bytes} B"
        elif bytes < 1024 * 1024:
            return f"{bytes / 1024:.1f} KB"
        else:
            return f"{bytes / (1024 * 1024):.1f} MB"

    def _file_icon(self, path: str) -> str:
        icons = {".md": "📄", ".py": "🐍", ".sh": "⚙️", ".json": "📋"}
        ext = Path(path).suffix
        return icons.get(ext, "📄")
```

## Default Next Steps

```python
def default_next_steps(skill_name: str, install_path: Path) -> list[NextStep]:
    """Generate default next steps."""
    return [
        NextStep(
            number=1,
            description="Try the skill",
            command=f"/{skill_name}"
        ),
        NextStep(
            number=2,
            description="View documentation",
            command=f"cat {install_path}/SKILL.md"
        ),
        NextStep(
            number=3,
            description="Customize behavior",
            command=None
        ),
    ]
```

## Integration

```python
def show_completion_summary(
    skill_name: str,
    install_path: Path,
    files: dict[str, str],
    quality_score: float,
    quality_breakdown: dict[str, float],
    duration: float,
    warnings: list[str] | None = None
) -> None:
    """Show completion summary after generation."""

    # Build file list
    file_list = []
    total_tokens = 0
    for path, content in files.items():
        size = len(content.encode('utf-8'))
        tokens = len(content) // 4
        total_tokens += tokens
        file_list.append(GeneratedFile(
            path=path,
            size_bytes=size,
            tokens=tokens,
            is_directory=False
        ))

    # Build quality breakdown
    breakdown = [
        QualityBreakdown(dim, score, 10.0)
        for dim, score in quality_breakdown.items()
    ]

    # Create summary
    summary = CompletionSummary(
        skill_name=skill_name,
        status="success" if quality_score >= 7.0 else "partial",
        install_path=install_path,
        files=file_list,
        total_size=sum(f.size_bytes for f in file_list),
        total_tokens=total_tokens,
        quality_score=quality_score,
        quality_breakdown=breakdown,
        next_steps=default_next_steps(skill_name, install_path),
        duration_seconds=duration,
        warnings=warnings or [],
        timestamp=datetime.now()
    )

    # Format and display
    formatter = CompletionSummaryFormatter()
    print(formatter.format(summary))
```
