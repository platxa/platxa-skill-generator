# Progressive Complexity Ordering

Organize content from basic to advanced across skill components.

## Complexity Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                        SKILL.md                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 1: BASICS                                         ││
│  │ • What is this skill?                                   ││
│  │ • When to use it?                                       ││
│  │ • Quick start example                                   ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 2: CORE WORKFLOW                                  ││
│  │ • Main steps (high-level)                               ││
│  │ • Key concepts (summary)                                ││
│  │ • Common use cases                                      ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 3: PRACTICAL                                      ││
│  │ • Examples (2-3 typical)                                ││
│  │ • Output format                                         ││
│  │ • Links to references for depth                         ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      references/                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 4: DETAILED                                       ││
│  │ • Complete specifications                               ││
│  │ • All configuration options                             ││
│  │ • Edge cases and exceptions                             ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 5: ADVANCED                                       ││
│  │ • Complex scenarios                                     ││
│  │ • Performance optimization                              ││
│  │ • Integration patterns                                  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Level 6: EXPERT                                         ││
│  │ • Internals and architecture                            ││
│  │ • Extension points                                      ││
│  │ • Troubleshooting guide                                 ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Complexity Levels

```python
from enum import IntEnum
from dataclasses import dataclass

class ComplexityLevel(IntEnum):
    BASIC = 1       # Essential, everyone needs
    CORE = 2        # Main functionality
    PRACTICAL = 3   # Common usage patterns
    DETAILED = 4    # Full specifications
    ADVANCED = 5    # Complex scenarios
    EXPERT = 6      # Deep internals

@dataclass
class ContentBlock:
    id: str
    title: str
    content: str
    complexity: ComplexityLevel
    prerequisites: list[str]
```

## SKILL.md Structure (Levels 1-3)

```python
SKILL_MD_SECTIONS = {
    # Level 1: Basics (first 20% of content)
    "overview": {
        "complexity": ComplexityLevel.BASIC,
        "purpose": "What and why",
        "content": [
            "One-sentence description",
            "Primary use case",
            "Key benefit"
        ]
    },
    "quick_start": {
        "complexity": ComplexityLevel.BASIC,
        "purpose": "Immediate value",
        "content": [
            "Simplest possible example",
            "Expected output",
            "Success indicator"
        ]
    },

    # Level 2: Core (middle 50% of content)
    "workflow": {
        "complexity": ComplexityLevel.CORE,
        "purpose": "How it works",
        "content": [
            "High-level steps",
            "Key decision points",
            "Main inputs/outputs"
        ]
    },
    "concepts": {
        "complexity": ComplexityLevel.CORE,
        "purpose": "Essential understanding",
        "content": [
            "3-5 key terms",
            "Core principles",
            "Mental model"
        ]
    },

    # Level 3: Practical (last 30% of content)
    "examples": {
        "complexity": ComplexityLevel.PRACTICAL,
        "purpose": "Real-world usage",
        "content": [
            "2-3 typical examples",
            "Input variations",
            "Output variations"
        ]
    },
    "next_steps": {
        "complexity": ComplexityLevel.PRACTICAL,
        "purpose": "Growth path",
        "content": [
            "Links to references",
            "Advanced capabilities",
            "Related skills"
        ]
    }
}
```

## Reference Structure (Levels 4-6)

```python
REFERENCE_SECTIONS = {
    # Level 4: Detailed
    "complete_specification": {
        "complexity": ComplexityLevel.DETAILED,
        "content": [
            "All parameters/options",
            "Type definitions",
            "Default values",
            "Valid ranges"
        ]
    },
    "all_examples": {
        "complexity": ComplexityLevel.DETAILED,
        "content": [
            "Comprehensive examples",
            "Edge case examples",
            "Error examples"
        ]
    },

    # Level 5: Advanced
    "complex_scenarios": {
        "complexity": ComplexityLevel.ADVANCED,
        "content": [
            "Multi-step workflows",
            "Integration patterns",
            "Performance tuning"
        ]
    },
    "customization": {
        "complexity": ComplexityLevel.ADVANCED,
        "content": [
            "Configuration options",
            "Extension points",
            "Override patterns"
        ]
    },

    # Level 6: Expert
    "internals": {
        "complexity": ComplexityLevel.EXPERT,
        "content": [
            "Architecture overview",
            "Algorithm details",
            "Implementation notes"
        ]
    },
    "troubleshooting": {
        "complexity": ComplexityLevel.EXPERT,
        "content": [
            "Common issues",
            "Debug strategies",
            "Error codes"
        ]
    }
}
```

## Ordering Algorithm

```python
def order_content_by_complexity(
    blocks: list[ContentBlock]
) -> list[ContentBlock]:
    """Order content blocks by progressive complexity."""

    # Sort by complexity level, then by prerequisites
    def sort_key(block: ContentBlock) -> tuple:
        # Calculate prerequisite depth
        prereq_depth = calculate_prereq_depth(block, blocks)
        return (block.complexity, prereq_depth, block.id)

    return sorted(blocks, key=sort_key)

def calculate_prereq_depth(
    block: ContentBlock,
    all_blocks: list[ContentBlock],
    visited: set | None = None
) -> int:
    """Calculate depth of prerequisite chain."""
    if visited is None:
        visited = set()

    if block.id in visited:
        return 0  # Avoid cycles

    visited.add(block.id)

    if not block.prerequisites:
        return 0

    max_depth = 0
    for prereq_id in block.prerequisites:
        prereq = next((b for b in all_blocks if b.id == prereq_id), None)
        if prereq:
            depth = 1 + calculate_prereq_depth(prereq, all_blocks, visited)
            max_depth = max(max_depth, depth)

    return max_depth
```

## Content Placement Rules

```python
def assign_content_location(
    block: ContentBlock
) -> str:
    """Determine where content should be placed."""

    if block.complexity <= ComplexityLevel.PRACTICAL:
        return "SKILL.md"
    elif block.complexity == ComplexityLevel.DETAILED:
        return "references/specification.md"
    elif block.complexity == ComplexityLevel.ADVANCED:
        return "references/advanced.md"
    else:
        return "references/internals.md"

def validate_placement(
    files: dict[str, str]
) -> list[str]:
    """Validate content is placed at appropriate complexity level."""
    issues = []

    skill_md = files.get("SKILL.md", "")

    # Check SKILL.md doesn't have expert content
    expert_indicators = [
        "implementation detail",
        "internal architecture",
        "algorithm complexity",
        "performance characteristics",
        "memory layout"
    ]

    for indicator in expert_indicators:
        if indicator.lower() in skill_md.lower():
            issues.append(
                f"SKILL.md contains expert-level content: '{indicator}'. "
                "Move to references/"
            )

    # Check references don't duplicate basics
    for filepath, content in files.items():
        if filepath.startswith("references/"):
            basic_indicators = [
                "## Overview",
                "## What is",
                "## Quick Start"
            ]
            for indicator in basic_indicators:
                if indicator in content:
                    issues.append(
                        f"{filepath} contains basic content: '{indicator}'. "
                        "This belongs in SKILL.md"
                    )

    return issues
```

## Progressive Disclosure Pattern

```python
def apply_progressive_disclosure(
    content: str,
    max_level: ComplexityLevel
) -> str:
    """Apply progressive disclosure to content."""

    sections = parse_sections(content)
    result = []

    for section in sections:
        if section.complexity <= max_level:
            result.append(section.content)
        elif section.complexity == max_level + 1:
            # Add summary with link
            summary = extract_first_sentence(section.content)
            link = f"See [{section.title}](references/{section.id}.md)"
            result.append(f"**{section.title}**: {summary} {link}")
        # Skip higher levels entirely

    return "\n\n".join(result)
```

## Validation

```python
def validate_complexity_ordering(
    skill_md: str,
    references: dict[str, str]
) -> ValidationResult:
    """Validate progressive complexity ordering."""
    errors = []
    warnings = []

    # Check SKILL.md section order
    sections = extract_section_headers(skill_md)
    expected_order = [
        "Overview", "Quick Start", "Workflow",
        "Examples", "Next Steps"
    ]

    for i, expected in enumerate(expected_order):
        if i < len(sections):
            if expected.lower() not in sections[i].lower():
                warnings.append(
                    f"Section {i+1} should be '{expected}', found '{sections[i]}'"
                )

    # Check first section is basic
    first_section = get_first_section_content(skill_md)
    word_count = len(first_section.split())
    if word_count > 200:
        warnings.append(
            f"First section too long ({word_count} words). "
            "Keep basics brief."
        )

    # Check references have depth
    for filepath, content in references.items():
        depth_score = calculate_depth_score(content)
        if depth_score < 3:
            warnings.append(
                f"{filepath} lacks depth (score: {depth_score}/10). "
                "Add detailed specifications."
            )

    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

## Example Application

### Before (flat structure)
```markdown
# API Doc Generator

## All Configuration Options
--output: Output directory (default: ./docs)
--format: Output format (md, html, pdf)
--template: Custom template path
--include-private: Include private endpoints
--group-by: Grouping strategy (tag, path, method)
... (50 more options)

## Complete Workflow
Step 1: Parse OpenAPI spec
  1.1: Validate YAML/JSON syntax
  1.2: Resolve $ref references
  1.3: Validate against OpenAPI 3.0 schema
... (detailed substeps)
```

### After (progressive complexity)
```markdown
# API Doc Generator

## Overview
Generate beautiful API documentation from OpenAPI specs.

## Quick Start
```
/api-doc-generator --input openapi.yaml
```

## Workflow
1. Parse your OpenAPI spec
2. Generate documentation
3. Review output in ./docs/

## Examples
[2-3 simple examples]

## Next Steps
See [Configuration Reference](references/config.md) for all options.
See [Advanced Usage](references/advanced.md) for complex scenarios.
```
