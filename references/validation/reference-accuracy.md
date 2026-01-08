# Reference Accuracy Checker

Validate that cross-references between documents are accurate and functional.

## Accuracy Checks

| Check | Description | Severity |
|-------|-------------|----------|
| Link exists | Target file/anchor exists | Critical |
| Anchor valid | Section heading exists | High |
| Content matches | Link text matches target | Medium |
| Bidirectional | Reverse links exist where expected | Low |

## Accuracy Model

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class LinkStatus(Enum):
    VALID = "valid"
    BROKEN = "broken"
    ANCHOR_MISSING = "anchor_missing"
    CONTENT_MISMATCH = "content_mismatch"
    ORPHAN = "orphan"

class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class LinkCheck:
    source_file: str
    source_line: int
    link_text: str
    target_path: str
    target_anchor: str | None
    status: LinkStatus
    severity: IssueSeverity
    message: str

@dataclass
class AccuracyReport:
    total_links: int
    valid_links: int
    broken_links: list[LinkCheck]
    warnings: list[LinkCheck]
    accuracy_score: float  # 0-100%
    passed: bool
```

## Checker Implementation

```python
import re
from pathlib import Path

class ReferenceAccuracyChecker:
    """Check accuracy of cross-references in skill documents."""

    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    HEADING_PATTERN = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.files: dict[str, str] = {}
        self.headings: dict[str, set[str]] = {}

    def load_files(self) -> None:
        """Load all markdown files and extract headings."""
        for md_file in self.skill_dir.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.skill_dir))
            content = md_file.read_text()
            self.files[rel_path] = content

            # Extract headings for anchor validation
            headings = set()
            for match in self.HEADING_PATTERN.finditer(content):
                heading = match.group(1).strip()
                anchor = self._heading_to_anchor(heading)
                headings.add(anchor)
            self.headings[rel_path] = headings

    def _heading_to_anchor(self, heading: str) -> str:
        """Convert heading text to anchor ID."""
        anchor = heading.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor

    def check_all(self) -> AccuracyReport:
        """Check all cross-references for accuracy."""
        self.load_files()

        all_checks: list[LinkCheck] = []

        for source_path, content in self.files.items():
            checks = self._check_file(source_path, content)
            all_checks.extend(checks)

        # Separate valid, broken, and warnings
        valid = [c for c in all_checks if c.status == LinkStatus.VALID]
        broken = [c for c in all_checks if c.status == LinkStatus.BROKEN]
        warnings = [c for c in all_checks if c.status in [
            LinkStatus.ANCHOR_MISSING,
            LinkStatus.CONTENT_MISMATCH
        ]]

        total = len(all_checks)
        valid_count = len(valid)
        accuracy = (valid_count / total * 100) if total > 0 else 100.0

        return AccuracyReport(
            total_links=total,
            valid_links=valid_count,
            broken_links=broken,
            warnings=warnings,
            accuracy_score=accuracy,
            passed=len(broken) == 0
        )

    def _check_file(
        self,
        source_path: str,
        content: str
    ) -> list[LinkCheck]:
        """Check all links in a single file."""
        checks = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for match in self.LINK_PATTERN.finditer(line):
                link_text = match.group(1)
                target = match.group(2)

                check = self._check_link(
                    source_path, line_num, link_text, target
                )
                if check:
                    checks.append(check)

        return checks

    def _check_link(
        self,
        source_path: str,
        line_num: int,
        link_text: str,
        target: str
    ) -> LinkCheck | None:
        """Check a single link for accuracy."""

        # Skip external links
        if target.startswith(('http://', 'https://', 'mailto:')):
            return None

        # Parse target path and anchor
        if '#' in target:
            path_part, anchor = target.split('#', 1)
        else:
            path_part, anchor = target, None

        # Handle relative paths
        if path_part:
            resolved = self._resolve_path(source_path, path_part)
        else:
            resolved = source_path  # Same-file anchor

        # Check if target file exists
        if resolved not in self.files:
            return LinkCheck(
                source_file=source_path,
                source_line=line_num,
                link_text=link_text,
                target_path=resolved,
                target_anchor=anchor,
                status=LinkStatus.BROKEN,
                severity=IssueSeverity.CRITICAL,
                message=f"Target file not found: {resolved}"
            )

        # Check anchor if specified
        if anchor:
            if anchor not in self.headings.get(resolved, set()):
                return LinkCheck(
                    source_file=source_path,
                    source_line=line_num,
                    link_text=link_text,
                    target_path=resolved,
                    target_anchor=anchor,
                    status=LinkStatus.ANCHOR_MISSING,
                    severity=IssueSeverity.HIGH,
                    message=f"Anchor not found: #{anchor} in {resolved}"
                )

        # Check content match
        if not self._content_matches(link_text, resolved, anchor):
            return LinkCheck(
                source_file=source_path,
                source_line=line_num,
                link_text=link_text,
                target_path=resolved,
                target_anchor=anchor,
                status=LinkStatus.CONTENT_MISMATCH,
                severity=IssueSeverity.MEDIUM,
                message=f"Link text may not match target content"
            )

        # Valid link
        return LinkCheck(
            source_file=source_path,
            source_line=line_num,
            link_text=link_text,
            target_path=resolved,
            target_anchor=anchor,
            status=LinkStatus.VALID,
            severity=IssueSeverity.LOW,
            message="OK"
        )

    def _resolve_path(self, source: str, target: str) -> str:
        """Resolve relative path from source to target."""
        if target.startswith('/'):
            return target.lstrip('/')

        source_dir = Path(source).parent
        resolved = (source_dir / target).resolve()

        try:
            return str(resolved.relative_to(Path.cwd()))
        except ValueError:
            return str(resolved)

    def _content_matches(
        self,
        link_text: str,
        target_path: str,
        anchor: str | None
    ) -> bool:
        """Check if link text reasonably matches target content."""
        content = self.files.get(target_path, "")

        # If anchor specified, check heading
        if anchor:
            for heading in self.headings.get(target_path, set()):
                if self._heading_to_anchor(heading) == anchor:
                    # Loose match - link text should relate
                    return self._text_relates(link_text, heading)

        # Otherwise check filename
        filename = Path(target_path).stem.replace('-', ' ').replace('_', ' ')
        return self._text_relates(link_text, filename)

    def _text_relates(self, text1: str, text2: str) -> bool:
        """Check if two texts are related (loose match)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Remove common words
        stopwords = {'the', 'a', 'an', 'to', 'for', 'of', 'and', 'or'}
        words1 -= stopwords
        words2 -= stopwords

        # At least one word overlap
        return bool(words1 & words2) or len(words1) == 0 or len(words2) == 0
```

## Orphan Detection

```python
def find_orphan_documents(self) -> list[str]:
    """Find documents that are never linked to."""
    self.load_files()

    all_targets = set()

    # Collect all link targets
    for content in self.files.values():
        for match in self.LINK_PATTERN.finditer(content):
            target = match.group(2)
            if not target.startswith(('http://', 'https://')):
                path_part = target.split('#')[0] if '#' in target else target
                if path_part:
                    all_targets.add(path_part)

    # Find files never linked
    orphans = []
    for file_path in self.files:
        if file_path == "SKILL.md":
            continue  # SKILL.md is the root
        if file_path not in all_targets:
            # Check relative paths too
            is_linked = any(
                file_path.endswith(t) or t.endswith(file_path)
                for t in all_targets
            )
            if not is_linked:
                orphans.append(file_path)

    return orphans
```

## Circular Reference Detection

```python
def find_circular_references(self) -> list[list[str]]:
    """Detect circular reference chains."""
    self.load_files()

    # Build link graph
    graph: dict[str, set[str]] = {}
    for source, content in self.files.items():
        graph[source] = set()
        for match in self.LINK_PATTERN.finditer(content):
            target = match.group(2)
            if not target.startswith(('http://', 'https://')):
                path_part = target.split('#')[0] if '#' in target else target
                if path_part:
                    resolved = self._resolve_path(source, path_part)
                    if resolved in self.files:
                        graph[source].add(resolved)

    # Find cycles using DFS
    cycles = []
    visited = set()
    path = []

    def dfs(node: str) -> None:
        if node in path:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return

        if node in visited:
            return

        visited.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            dfs(neighbor)

        path.pop()

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles
```

## Report Generation

```python
def format_accuracy_report(report: AccuracyReport) -> str:
    """Format accuracy report as markdown."""
    lines = [
        "# Reference Accuracy Report",
        "",
        f"**Accuracy Score:** {report.accuracy_score:.1f}%",
        f"**Status:** {'✓ PASSED' if report.passed else '✗ FAILED'}",
        "",
        "## Summary",
        "",
        f"- Total links checked: {report.total_links}",
        f"- Valid links: {report.valid_links}",
        f"- Broken links: {len(report.broken_links)}",
        f"- Warnings: {len(report.warnings)}",
        "",
    ]

    if report.broken_links:
        lines.extend([
            "## Broken Links (Critical)",
            "",
            "| Source | Line | Target | Issue |",
            "|--------|------|--------|-------|",
        ])
        for check in report.broken_links:
            lines.append(
                f"| {check.source_file} | {check.source_line} | "
                f"{check.target_path} | {check.message} |"
            )
        lines.append("")

    if report.warnings:
        lines.extend([
            "## Warnings",
            "",
            "| Source | Line | Issue |",
            "|--------|------|-------|",
        ])
        for check in report.warnings:
            lines.append(
                f"| {check.source_file} | {check.source_line} | "
                f"{check.message} |"
            )
        lines.append("")

    return "\n".join(lines)
```

## Integration

```python
def validate_skill_references(skill_dir: Path) -> tuple[bool, str]:
    """Validate all references in a skill directory."""
    checker = ReferenceAccuracyChecker(skill_dir)
    report = checker.check_all()

    # Check for orphans
    orphans = checker.find_orphan_documents()
    if orphans:
        report.warnings.extend([
            LinkCheck(
                source_file="(none)",
                source_line=0,
                link_text="",
                target_path=orphan,
                target_anchor=None,
                status=LinkStatus.ORPHAN,
                severity=IssueSeverity.LOW,
                message=f"Orphan document: {orphan}"
            )
            for orphan in orphans
        ])

    # Check for cycles
    cycles = checker.find_circular_references()
    if cycles:
        for cycle in cycles:
            report.warnings.append(LinkCheck(
                source_file=cycle[0],
                source_line=0,
                link_text="",
                target_path=cycle[-1],
                target_anchor=None,
                status=LinkStatus.VALID,  # Not broken, just circular
                severity=IssueSeverity.LOW,
                message=f"Circular: {' → '.join(cycle)}"
            ))

    formatted = format_accuracy_report(report)
    return report.passed, formatted
```
