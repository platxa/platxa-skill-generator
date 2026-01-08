# Skill Preview Formatter

Format generated skill files for user preview before installation.

## Preview Modes

| Mode | Purpose | Detail Level |
|------|---------|--------------|
| Summary | Quick overview | File list + sizes |
| Tree | Structure view | Directory tree |
| Content | Full preview | All file contents |
| Diff | Changes view | Before/after comparison |

## Preview Model

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class PreviewMode(Enum):
    SUMMARY = "summary"
    TREE = "tree"
    CONTENT = "content"
    DIFF = "diff"

@dataclass
class FilePreview:
    path: str
    size_bytes: int
    tokens: int
    content: str
    language: str  # For syntax highlighting
    truncated: bool
    changes: list[str] | None  # For diff mode

@dataclass
class SkillPreview:
    skill_name: str
    total_files: int
    total_size: int
    total_tokens: int
    files: list[FilePreview]
    quality_score: float | None
    warnings: list[str]
```

## Preview Formatter

```python
class SkillPreviewFormatter:
    """Format skill files for user preview."""

    MAX_CONTENT_LINES = 50
    MAX_FILE_SIZE = 10000  # chars

    def __init__(self, mode: PreviewMode = PreviewMode.SUMMARY):
        self.mode = mode

    def format(self, skill_files: dict[str, str]) -> str:
        """Format skill files based on mode."""
        preview = self._build_preview(skill_files)

        formatters = {
            PreviewMode.SUMMARY: self._format_summary,
            PreviewMode.TREE: self._format_tree,
            PreviewMode.CONTENT: self._format_content,
            PreviewMode.DIFF: self._format_diff,
        }

        formatter = formatters.get(self.mode, self._format_summary)
        return formatter(preview)

    def _build_preview(self, files: dict[str, str]) -> SkillPreview:
        """Build preview data structure."""
        file_previews = []

        for path, content in sorted(files.items()):
            size = len(content.encode('utf-8'))
            tokens = len(content) // 4  # Approximate

            truncated = len(content) > self.MAX_FILE_SIZE
            if truncated:
                content = content[:self.MAX_FILE_SIZE] + "\n... (truncated)"

            file_previews.append(FilePreview(
                path=path,
                size_bytes=size,
                tokens=tokens,
                content=content,
                language=self._detect_language(path),
                truncated=truncated,
                changes=None
            ))

        return SkillPreview(
            skill_name=self._extract_skill_name(files),
            total_files=len(files),
            total_size=sum(fp.size_bytes for fp in file_previews),
            total_tokens=sum(fp.tokens for fp in file_previews),
            files=file_previews,
            quality_score=None,
            warnings=[]
        )

    def _extract_skill_name(self, files: dict[str, str]) -> str:
        """Extract skill name from SKILL.md frontmatter."""
        skill_md = files.get("SKILL.md", "")
        import re
        match = re.search(r'^name:\s*(.+)$', skill_md, re.MULTILINE)
        return match.group(1).strip() if match else "unnamed-skill"

    def _detect_language(self, path: str) -> str:
        """Detect language for syntax highlighting."""
        ext_map = {
            ".md": "markdown",
            ".py": "python",
            ".sh": "bash",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".txt": "text",
        }
        ext = Path(path).suffix
        return ext_map.get(ext, "text")
```

## Format: Summary

```python
def _format_summary(self, preview: SkillPreview) -> str:
    """Format as summary view."""
    lines = [
        "═" * 60,
        f"  SKILL PREVIEW: {preview.skill_name}",
        "═" * 60,
        "",
        f"  Files: {preview.total_files}",
        f"  Size:  {self._format_size(preview.total_size)}",
        f"  Tokens: {preview.total_tokens:,}",
        "",
        "─" * 60,
        "  FILES",
        "─" * 60,
        "",
        "  {:40} {:>8} {:>8}".format("Path", "Size", "Tokens"),
        "  " + "-" * 56,
    ]

    for fp in preview.files:
        size = self._format_size(fp.size_bytes)
        lines.append(f"  {fp.path:40} {size:>8} {fp.tokens:>8,}")

    lines.extend([
        "",
        "─" * 60,
        f"  Total: {preview.total_files} files, {self._format_size(preview.total_size)}, {preview.total_tokens:,} tokens",
        "═" * 60,
    ])

    if preview.warnings:
        lines.append("")
        lines.append("  ⚠ Warnings:")
        for warn in preview.warnings:
            lines.append(f"    - {warn}")

    return "\n".join(lines)

def _format_size(self, bytes: int) -> str:
    """Format byte size as human-readable."""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"
```

## Format: Tree

```python
def _format_tree(self, preview: SkillPreview) -> str:
    """Format as directory tree."""
    lines = [
        f"📁 {preview.skill_name}/",
    ]

    # Build tree structure
    tree: dict = {}
    for fp in preview.files:
        parts = Path(fp.path).parts
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = fp

    # Render tree
    self._render_tree(tree, lines, prefix="")

    lines.extend([
        "",
        f"({preview.total_files} files, {self._format_size(preview.total_size)})",
    ])

    return "\n".join(lines)

def _render_tree(
    self,
    tree: dict,
    lines: list[str],
    prefix: str
) -> None:
    """Recursively render tree structure."""
    items = sorted(tree.items())

    for i, (name, value) in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if isinstance(value, dict):
            # Directory
            lines.append(f"{prefix}{connector}📁 {name}/")
            self._render_tree(value, lines, prefix + child_prefix)
        else:
            # File
            fp = value
            icon = self._file_icon(fp.path)
            size = self._format_size(fp.size_bytes)
            lines.append(f"{prefix}{connector}{icon} {name} ({size})")

def _file_icon(self, path: str) -> str:
    """Get icon for file type."""
    icons = {
        ".md": "📄",
        ".py": "🐍",
        ".sh": "⚙️",
        ".json": "📋",
        ".yaml": "📋",
        ".yml": "📋",
        ".txt": "📝",
    }
    ext = Path(path).suffix
    return icons.get(ext, "📄")
```

## Format: Content

```python
def _format_content(self, preview: SkillPreview) -> str:
    """Format with full file contents."""
    lines = [
        "═" * 70,
        f"  SKILL PREVIEW: {preview.skill_name}",
        "═" * 70,
        "",
    ]

    for fp in preview.files:
        lines.extend([
            "─" * 70,
            f"📄 {fp.path}",
            f"   Size: {self._format_size(fp.size_bytes)} | Tokens: {fp.tokens:,} | Language: {fp.language}",
            "─" * 70,
            "",
        ])

        # Format content with line numbers
        content_lines = fp.content.split('\n')
        max_lines = self.MAX_CONTENT_LINES

        for i, line in enumerate(content_lines[:max_lines], 1):
            lines.append(f"  {i:4} │ {line}")

        if len(content_lines) > max_lines:
            remaining = len(content_lines) - max_lines
            lines.append(f"       │ ... ({remaining} more lines)")

        if fp.truncated:
            lines.append("")
            lines.append("  ⚠ File truncated for preview")

        lines.append("")

    lines.append("═" * 70)

    return "\n".join(lines)
```

## Format: Diff

```python
def _format_diff(self, preview: SkillPreview) -> str:
    """Format as diff view (for updates)."""
    lines = [
        "═" * 70,
        f"  CHANGES PREVIEW: {preview.skill_name}",
        "═" * 70,
        "",
    ]

    for fp in preview.files:
        if not fp.changes:
            lines.append(f"  + {fp.path} (new file)")
            continue

        lines.extend([
            "─" * 70,
            f"  ± {fp.path}",
            "─" * 70,
        ])

        for change in fp.changes:
            if change.startswith('+'):
                lines.append(f"  \033[32m{change}\033[0m")  # Green
            elif change.startswith('-'):
                lines.append(f"  \033[31m{change}\033[0m")  # Red
            else:
                lines.append(f"  {change}")

        lines.append("")

    lines.append("═" * 70)

    return "\n".join(lines)
```

## Interactive Preview

```python
class InteractivePreview:
    """Interactive file browser for skill preview."""

    def __init__(self, preview: SkillPreview):
        self.preview = preview
        self.current_file = 0

    def show(self) -> None:
        """Show interactive preview."""
        while True:
            self._display_current()
            action = self._get_action()

            if action == 'q':
                break
            elif action == 'n':
                self.current_file = min(
                    self.current_file + 1,
                    len(self.preview.files) - 1
                )
            elif action == 'p':
                self.current_file = max(self.current_file - 1, 0)
            elif action == 'l':
                self._show_file_list()

    def _display_current(self) -> None:
        """Display current file."""
        fp = self.preview.files[self.current_file]
        print(f"\n{'─' * 60}")
        print(f"File {self.current_file + 1}/{len(self.preview.files)}: {fp.path}")
        print(f"{'─' * 60}\n")

        lines = fp.content.split('\n')[:30]
        for i, line in enumerate(lines, 1):
            print(f"{i:4} │ {line}")

        if len(fp.content.split('\n')) > 30:
            print("     │ ...")

    def _get_action(self) -> str:
        """Get user action."""
        print("\n[n]ext [p]rev [l]ist [q]uit: ", end="")
        return input().strip().lower()

    def _show_file_list(self) -> None:
        """Show file list."""
        print("\nFiles:")
        for i, fp in enumerate(self.preview.files):
            marker = "→" if i == self.current_file else " "
            print(f"  {marker} {i + 1}. {fp.path}")
```

## Integration

```python
def preview_skill(
    skill_files: dict[str, str],
    mode: PreviewMode = PreviewMode.SUMMARY,
    interactive: bool = False
) -> str | None:
    """Preview generated skill files."""
    formatter = SkillPreviewFormatter(mode)

    if interactive:
        preview = formatter._build_preview(skill_files)
        browser = InteractivePreview(preview)
        browser.show()
        return None
    else:
        return formatter.format(skill_files)
```
