# Reference Cross-Linking

Strategy for linking references to each other appropriately.

## Linking Principles

### 1. Bidirectional Links
When A references B, B should reference A (where appropriate).

### 2. Hierarchical Links
- Parent documents link down to children
- Child documents link up to parent
- Siblings link horizontally

### 3. Contextual Links
Link when the reference adds value, not just because it exists.

## Link Topology

```
SKILL.md (hub)
    │
    ├── references/
    │   ├── overview.md ←→ workflow.md
    │   │       │               │
    │   │       ↓               ↓
    │   ├── api.md ←────── examples.md
    │   │       │               ↑
    │   │       ↓               │
    │   └── troubleshooting.md ─┘
    │
    └── scripts/ ──→ references/api.md
```

## Link Types

```python
from dataclasses import dataclass
from enum import Enum

class LinkType(Enum):
    PARENT = "parent"       # Link to containing document
    CHILD = "child"         # Link to sub-section
    SIBLING = "sibling"     # Link to related peer
    PREREQUISITE = "prereq" # Must read before this
    SEE_ALSO = "see_also"   # Related reading
    EXAMPLE = "example"     # Link to example
    DEFINITION = "def"      # Link to term definition

@dataclass
class CrossLink:
    source_file: str
    target_file: str
    link_type: LinkType
    anchor: str | None  # Optional section anchor
    context: str        # Why this link exists
    bidirectional: bool # Should reverse link exist

@dataclass
class LinkGraph:
    nodes: set[str]        # All files
    edges: list[CrossLink] # All links
```

## Link Rules by Document

```python
DOCUMENT_LINK_RULES = {
    "SKILL.md": {
        "links_to": ["references/*", "scripts/*", "examples/*"],
        "link_types": [LinkType.CHILD],
        "bidirectional": False,  # Children link back
    },
    "references/overview.md": {
        "links_to": ["references/*.md"],
        "link_types": [LinkType.SEE_ALSO],
        "bidirectional": True,
    },
    "references/workflow.md": {
        "links_to": ["references/api.md", "examples/*"],
        "link_types": [LinkType.SEE_ALSO, LinkType.EXAMPLE],
        "bidirectional": True,
    },
    "references/api.md": {
        "links_to": ["references/examples.md", "scripts/*"],
        "link_types": [LinkType.EXAMPLE, LinkType.SEE_ALSO],
        "bidirectional": True,
    },
    "references/troubleshooting.md": {
        "links_to": ["references/*.md"],
        "link_types": [LinkType.SEE_ALSO],
        "bidirectional": False,  # One-way reference
    },
    "references/patterns.md": {
        "links_to": ["references/examples.md", "references/api.md"],
        "link_types": [LinkType.EXAMPLE, LinkType.SEE_ALSO],
        "bidirectional": True,
    },
    "examples/*": {
        "links_to": ["references/api.md", "SKILL.md"],
        "link_types": [LinkType.PARENT, LinkType.SEE_ALSO],
        "bidirectional": False,
    },
}
```

## Cross-Linker Implementation

```python
from pathlib import Path
import re

class CrossLinker:
    """Manages cross-links between reference documents."""

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.links: list[CrossLink] = []
        self.files: dict[str, str] = {}  # path -> content

    def load_files(self) -> None:
        """Load all markdown files."""
        for md_file in self.skill_dir.rglob("*.md"):
            rel_path = md_file.relative_to(self.skill_dir)
            self.files[str(rel_path)] = md_file.read_text()

    def analyze_links(self) -> list[CrossLink]:
        """Analyze existing links in all files."""
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for source, content in self.files.items():
            for match in re.finditer(link_pattern, content):
                text, target = match.groups()

                # Skip external links
                if target.startswith(('http://', 'https://')):
                    continue

                # Parse target path and anchor
                if '#' in target:
                    path, anchor = target.split('#', 1)
                else:
                    path, anchor = target, None

                # Resolve relative path
                resolved = self._resolve_path(source, path)
                if resolved:
                    self.links.append(CrossLink(
                        source_file=source,
                        target_file=resolved,
                        link_type=self._infer_link_type(source, resolved),
                        anchor=anchor,
                        context=text,
                        bidirectional=self._should_be_bidirectional(source, resolved)
                    ))

        return self.links

    def _resolve_path(self, source: str, target: str) -> str | None:
        """Resolve relative path from source to target."""
        if not target or target.startswith('#'):
            return None

        source_dir = Path(source).parent
        resolved = (source_dir / target).resolve()

        # Make relative to skill dir
        try:
            return str(resolved.relative_to(self.skill_dir.resolve()))
        except ValueError:
            return None

    def _infer_link_type(self, source: str, target: str) -> LinkType:
        """Infer link type from source and target paths."""
        source_parts = Path(source).parts
        target_parts = Path(target).parts

        # SKILL.md to anything = CHILD
        if source == "SKILL.md":
            return LinkType.CHILD

        # Anything to SKILL.md = PARENT
        if target == "SKILL.md":
            return LinkType.PARENT

        # Same directory = SIBLING
        if source_parts[:-1] == target_parts[:-1]:
            return LinkType.SIBLING

        # To examples = EXAMPLE
        if "examples" in target_parts:
            return LinkType.EXAMPLE

        return LinkType.SEE_ALSO

    def _should_be_bidirectional(self, source: str, target: str) -> bool:
        """Determine if link should have reverse."""
        # SKILL.md links are one-way (hub pattern)
        if source == "SKILL.md" or target == "SKILL.md":
            return False

        # Troubleshooting links are one-way
        if "troubleshooting" in source:
            return False

        # Siblings should link both ways
        if self._infer_link_type(source, target) == LinkType.SIBLING:
            return True

        # See also links are bidirectional
        return True

    def find_missing_links(self) -> list[CrossLink]:
        """Find links that should exist but don't."""
        missing = []

        # Check for missing reverse links
        for link in self.links:
            if link.bidirectional:
                reverse_exists = any(
                    l.source_file == link.target_file and
                    l.target_file == link.source_file
                    for l in self.links
                )
                if not reverse_exists:
                    missing.append(CrossLink(
                        source_file=link.target_file,
                        target_file=link.source_file,
                        link_type=self._reverse_link_type(link.link_type),
                        anchor=None,
                        context=f"Reverse link to {link.context}",
                        bidirectional=True
                    ))

        # Check for recommended links based on rules
        for source, rules in DOCUMENT_LINK_RULES.items():
            if source not in self.files:
                continue

            for target_pattern in rules["links_to"]:
                matching_files = self._match_pattern(target_pattern)
                for target in matching_files:
                    link_exists = any(
                        l.source_file == source and l.target_file == target
                        for l in self.links
                    )
                    if not link_exists:
                        missing.append(CrossLink(
                            source_file=source,
                            target_file=target,
                            link_type=rules["link_types"][0],
                            anchor=None,
                            context=f"Recommended: {source} → {target}",
                            bidirectional=rules.get("bidirectional", True)
                        ))

        return missing

    def _reverse_link_type(self, link_type: LinkType) -> LinkType:
        """Get reverse of a link type."""
        reversals = {
            LinkType.PARENT: LinkType.CHILD,
            LinkType.CHILD: LinkType.PARENT,
            LinkType.SIBLING: LinkType.SIBLING,
            LinkType.SEE_ALSO: LinkType.SEE_ALSO,
            LinkType.EXAMPLE: LinkType.SEE_ALSO,
        }
        return reversals.get(link_type, LinkType.SEE_ALSO)

    def _match_pattern(self, pattern: str) -> list[str]:
        """Match file pattern against loaded files."""
        import fnmatch
        return [f for f in self.files if fnmatch.fnmatch(f, pattern)]
```

## Link Insertion

```python
def insert_links(
    content: str,
    links: list[CrossLink],
    position: str = "end"  # "end", "section", "inline"
) -> str:
    """Insert cross-links into document content."""

    if not links:
        return content

    if position == "end":
        # Add "See Also" section at end
        link_section = format_see_also_section(links)
        return content.rstrip() + "\n\n" + link_section

    elif position == "section":
        # Add links after relevant section headers
        for link in links:
            if link.anchor:
                content = insert_after_section(
                    content, link.anchor, format_inline_link(link)
                )
        return content

    return content


def format_see_also_section(links: list[CrossLink]) -> str:
    """Format links as a See Also section."""
    lines = ["## See Also", ""]

    # Group by type
    by_type: dict[LinkType, list[CrossLink]] = {}
    for link in links:
        if link.link_type not in by_type:
            by_type[link.link_type] = []
        by_type[link.link_type].append(link)

    for link_type, type_links in by_type.items():
        if link_type == LinkType.EXAMPLE:
            lines.append("### Examples")
        elif link_type == LinkType.PREREQUISITE:
            lines.append("### Prerequisites")
        else:
            lines.append("### Related")

        lines.append("")
        for link in type_links:
            anchor = f"#{link.anchor}" if link.anchor else ""
            lines.append(f"- [{link.context}]({link.target_file}{anchor})")
        lines.append("")

    return "\n".join(lines)


def format_inline_link(link: CrossLink) -> str:
    """Format a single inline link."""
    anchor = f"#{link.anchor}" if link.anchor else ""
    return f"[{link.context}]({link.target_file}{anchor})"
```

## Validation

```python
def validate_link_graph(linker: CrossLinker) -> list[str]:
    """Validate the link graph for issues."""
    issues = []

    # Check for orphan documents (no incoming links)
    all_targets = {l.target_file for l in linker.links}
    for file in linker.files:
        if file != "SKILL.md" and file not in all_targets:
            issues.append(f"Orphan document: {file} has no incoming links")

    # Check for broken links
    for link in linker.links:
        if link.target_file not in linker.files:
            issues.append(f"Broken link: {link.source_file} → {link.target_file}")

    # Check for circular dependencies in prerequisites
    prereq_links = [l for l in linker.links if l.link_type == LinkType.PREREQUISITE]
    cycles = find_cycles(prereq_links)
    for cycle in cycles:
        issues.append(f"Circular prerequisite: {' → '.join(cycle)}")

    # Check for missing bidirectional links
    missing = linker.find_missing_links()
    for link in missing:
        if link.bidirectional:
            issues.append(
                f"Missing reverse link: {link.target_file} should link to {link.source_file}"
            )

    return issues


def find_cycles(links: list[CrossLink]) -> list[list[str]]:
    """Find cycles in directed graph."""
    graph: dict[str, list[str]] = {}
    for link in links:
        if link.source_file not in graph:
            graph[link.source_file] = []
        graph[link.source_file].append(link.target_file)

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

        for neighbor in graph.get(node, []):
            dfs(neighbor)

        path.pop()

    for node in graph:
        dfs(node)

    return cycles
```

## Integration with Generation

```python
def apply_cross_linking(skill_dir: Path) -> dict[str, str]:
    """Apply cross-linking to all generated files."""

    linker = CrossLinker(skill_dir)
    linker.load_files()
    linker.analyze_links()

    # Find and add missing links
    missing = linker.find_missing_links()

    updated_files = {}
    for link in missing:
        if link.source_file in linker.files:
            content = linker.files[link.source_file]
            updated = insert_links(content, [link], position="end")
            updated_files[link.source_file] = updated
            linker.files[link.source_file] = updated

    # Validate final graph
    issues = validate_link_graph(linker)
    if issues:
        print("Link validation issues:")
        for issue in issues:
            print(f"  - {issue}")

    return updated_files
```
