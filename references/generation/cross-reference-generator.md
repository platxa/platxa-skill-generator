# Cross-Reference Generator

Generate and validate cross-references between skill components.

## Reference Types

| Type | Syntax | Example |
|------|--------|---------|
| File link | `[text](path)` | `[Config Guide](references/config.md)` |
| Section link | `[text](path#section)` | `[Options](references/config.md#options)` |
| Inline reference | `See \`path\`` | See `references/workflow.md` |
| Related link | `Related: [text](path)` | Related: [Best Practices](references/best-practices.md) |

## Cross-Reference Model

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class CrossReference:
    source_file: str
    source_section: str | None
    target_file: str
    target_section: str | None
    link_text: str
    reference_type: Literal["file", "section", "inline", "related"]
    line_number: int

@dataclass
class CrossReferenceMap:
    references: list[CrossReference]
    orphaned_files: list[str]  # Files with no incoming references
    broken_links: list[CrossReference]  # References to non-existent targets
    circular_refs: list[tuple[str, str]]  # Circular reference pairs
```

## Reference Generation

### Automatic Reference Points

```python
REFERENCE_TRIGGERS = {
    # Keywords that should link to references
    "configuration": "references/config.md",
    "options": "references/config.md#options",
    "all options": "references/config.md",
    "detailed": "references/specification.md",
    "complete list": "references/specification.md",
    "troubleshooting": "references/troubleshooting.md",
    "best practices": "references/best-practices.md",
    "examples": "references/examples.md",
    "advanced": "references/advanced.md",
}

def identify_reference_points(content: str) -> list[ReferencePoint]:
    """Identify places where references should be added."""
    points = []

    for keyword, target in REFERENCE_TRIGGERS.items():
        pattern = rf"\b{re.escape(keyword)}\b"
        for match in re.finditer(pattern, content, re.IGNORECASE):
            # Check if already a link
            context = content[max(0, match.start()-10):match.end()+10]
            if not is_already_linked(context, match.group()):
                points.append(ReferencePoint(
                    keyword=match.group(),
                    position=match.start(),
                    suggested_target=target
                ))

    return points
```

### Link Generation

```python
def generate_link(
    source_file: str,
    target_file: str,
    link_text: str,
    target_section: str | None = None
) -> str:
    """Generate markdown link with correct relative path."""

    # Calculate relative path
    source_dir = os.path.dirname(source_file)
    rel_path = os.path.relpath(target_file, source_dir)

    # Add section anchor if specified
    if target_section:
        anchor = target_section.lower().replace(" ", "-")
        rel_path = f"{rel_path}#{anchor}"

    return f"[{link_text}]({rel_path})"

def generate_see_also_section(
    source_file: str,
    related_files: list[str]
) -> str:
    """Generate a 'See Also' section with related references."""
    lines = ["## See Also", ""]

    for target in related_files:
        link = generate_link(source_file, target, get_file_title(target))
        description = get_file_description(target)
        lines.append(f"- {link} - {description}")

    return "\n".join(lines)
```

## SKILL.md Reference Injection

### Required References

```python
def get_required_references(
    skill_type: str,
    reference_files: list[str]
) -> list[RequiredReference]:
    """Determine which references SKILL.md should link to."""

    required = []

    # Always link to existing reference files
    for ref_file in reference_files:
        filename = os.path.basename(ref_file)

        if filename == "concepts.md":
            required.append(RequiredReference(
                file=ref_file,
                location="after_overview",
                text="For key terminology, see [Concepts](references/concepts.md)."
            ))

        elif filename == "workflow.md":
            required.append(RequiredReference(
                file=ref_file,
                location="after_workflow",
                text="For detailed steps, see [Workflow Guide](references/workflow.md)."
            ))

        elif filename in ["config.md", "options.md"]:
            required.append(RequiredReference(
                file=ref_file,
                location="workflow_section",
                text="See [Configuration](references/config.md) for all options."
            ))

        elif filename == "examples.md":
            required.append(RequiredReference(
                file=ref_file,
                location="examples_section",
                text="More examples in [Examples](references/examples.md)."
            ))

    return required
```

### Injection Algorithm

```python
def inject_references(
    skill_md: str,
    references: list[RequiredReference]
) -> str:
    """Inject required references into SKILL.md."""

    sections = parse_markdown_sections(skill_md)

    for ref in references:
        if ref.location == "after_overview":
            sections["overview"] += f"\n\n{ref.text}"

        elif ref.location == "after_workflow":
            sections["workflow"] += f"\n\n{ref.text}"

        elif ref.location == "workflow_section":
            # Insert at end of workflow section
            if "workflow" in sections:
                sections["workflow"] += f"\n\n{ref.text}"

        elif ref.location == "examples_section":
            if "examples" in sections:
                sections["examples"] += f"\n\n{ref.text}"

        elif ref.location == "end":
            # Add to see also section
            if "see_also" not in sections:
                sections["see_also"] = "## See Also\n\n"
            sections["see_also"] += f"- {ref.text}\n"

    return reconstruct_markdown(sections)
```

## Reference Validation

### Link Checker

```python
def validate_references(
    files: dict[str, str]
) -> ReferenceValidationResult:
    """Validate all cross-references in skill files."""

    all_refs = []
    broken = []
    orphaned = []

    # Extract all references
    for filepath, content in files.items():
        refs = extract_references(content, filepath)
        all_refs.extend(refs)

    # Check each reference
    for ref in all_refs:
        if not file_exists(ref.target_file, files):
            broken.append(ref)
        elif ref.target_section:
            if not section_exists(ref.target_file, ref.target_section, files):
                broken.append(ref)

    # Find orphaned files (no incoming references)
    referenced_files = {ref.target_file for ref in all_refs}
    for filepath in files:
        if filepath.startswith("references/"):
            if filepath not in referenced_files:
                orphaned.append(filepath)

    return ReferenceValidationResult(
        total_references=len(all_refs),
        broken_references=broken,
        orphaned_files=orphaned,
        valid=len(broken) == 0
    )

def extract_references(content: str, source_file: str) -> list[CrossReference]:
    """Extract all markdown references from content."""
    refs = []

    # Match [text](path) and [text](path#section)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    for match in re.finditer(pattern, content):
        link_text = match.group(1)
        target = match.group(2)

        # Skip external URLs
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue

        # Parse target
        if '#' in target:
            target_file, target_section = target.split('#', 1)
        else:
            target_file = target
            target_section = None

        # Resolve relative path
        source_dir = os.path.dirname(source_file)
        absolute_target = os.path.normpath(os.path.join(source_dir, target_file))

        refs.append(CrossReference(
            source_file=source_file,
            source_section=get_current_section(content, match.start()),
            target_file=absolute_target,
            target_section=target_section,
            link_text=link_text,
            reference_type="section" if target_section else "file",
            line_number=content[:match.start()].count('\n') + 1
        ))

    return refs
```

### Orphan Detection

```python
def find_orphaned_references(files: dict[str, str]) -> list[str]:
    """Find reference files that are never linked from SKILL.md."""

    skill_md = files.get("SKILL.md", "")
    skill_refs = extract_references(skill_md, "SKILL.md")
    referenced = {ref.target_file for ref in skill_refs}

    orphaned = []
    for filepath in files:
        if filepath.startswith("references/"):
            if filepath not in referenced:
                orphaned.append(filepath)

    return orphaned
```

## Cross-Linking Between References

```python
def generate_reference_crosslinks(
    reference_files: dict[str, str]
) -> dict[str, str]:
    """Add cross-links between related reference files."""

    updated = {}

    for filepath, content in reference_files.items():
        # Find related files based on content
        related = find_related_files(filepath, content, reference_files)

        if related:
            # Add see also section if not present
            if "## See Also" not in content and "## Related" not in content:
                see_also = generate_see_also_section(filepath, related)
                content = content.rstrip() + "\n\n" + see_also

        updated[filepath] = content

    return updated

def find_related_files(
    current_file: str,
    content: str,
    all_files: dict[str, str]
) -> list[str]:
    """Find files related to current file."""

    related = []

    # Define relationships
    relationships = {
        "concepts.md": ["workflow.md", "best-practices.md"],
        "workflow.md": ["concepts.md", "examples.md"],
        "config.md": ["workflow.md", "advanced.md"],
        "examples.md": ["workflow.md", "troubleshooting.md"],
        "troubleshooting.md": ["config.md", "examples.md"],
    }

    filename = os.path.basename(current_file)
    if filename in relationships:
        for related_name in relationships[filename]:
            related_path = os.path.join(os.path.dirname(current_file), related_name)
            if related_path in all_files:
                related.append(related_path)

    return related
```

## Output Format

```json
{
  "cross_references": [
    {
      "source": "SKILL.md",
      "target": "references/concepts.md",
      "link_text": "Concepts",
      "type": "file",
      "line": 15
    },
    {
      "source": "SKILL.md",
      "target": "references/workflow.md#step-2",
      "link_text": "Step 2 details",
      "type": "section",
      "line": 42
    }
  ],
  "validation": {
    "total": 8,
    "valid": 8,
    "broken": 0,
    "orphaned_files": []
  }
}
```
