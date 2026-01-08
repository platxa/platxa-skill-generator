# Reference Priority Ordering

Order references by usefulness for optimal skill consumption.

## Priority Principles

1. **Most-Used First** - Frequently accessed content appears early
2. **Prerequisite Before Dependent** - Required knowledge precedes advanced
3. **Action Before Theory** - Practical guidance before deep explanations
4. **Common Before Edge** - Typical cases before special cases

## Priority Model

```python
from dataclasses import dataclass
from enum import IntEnum

class ReferencePriority(IntEnum):
    CRITICAL = 1      # Must read first
    HIGH = 2          # Important for basic usage
    MEDIUM = 3        # Enhances understanding
    LOW = 4           # Advanced/optional
    SUPPLEMENTARY = 5 # Nice to have

@dataclass
class PrioritizedReference:
    path: str
    priority: ReferencePriority
    access_frequency: float  # Estimated 0.0-1.0
    prerequisite_of: list[str]  # Files that depend on this
    depends_on: list[str]  # Prerequisites
    usefulness_score: float  # Computed score
```

## Priority Assignment

### By Reference Type

```python
REFERENCE_PRIORITIES = {
    # Core usage (Priority 1-2)
    "overview.md": ReferencePriority.CRITICAL,
    "quickstart.md": ReferencePriority.CRITICAL,
    "workflow.md": ReferencePriority.HIGH,
    "api.md": ReferencePriority.HIGH,

    # Practical (Priority 2-3)
    "examples.md": ReferencePriority.HIGH,
    "patterns.md": ReferencePriority.MEDIUM,
    "configuration.md": ReferencePriority.MEDIUM,

    # Support (Priority 3-4)
    "troubleshooting.md": ReferencePriority.MEDIUM,
    "faq.md": ReferencePriority.LOW,
    "glossary.md": ReferencePriority.LOW,

    # Deep dive (Priority 4-5)
    "internals.md": ReferencePriority.LOW,
    "architecture.md": ReferencePriority.LOW,
    "contributing.md": ReferencePriority.SUPPLEMENTARY,
    "changelog.md": ReferencePriority.SUPPLEMENTARY,
}
```

### By Skill Type

```python
SKILL_TYPE_PRIORITIES = {
    "builder": {
        "workflow.md": ReferencePriority.CRITICAL,
        "templates.md": ReferencePriority.CRITICAL,
        "api.md": ReferencePriority.HIGH,
        "examples.md": ReferencePriority.HIGH,
    },
    "guide": {
        "overview.md": ReferencePriority.CRITICAL,
        "topics.md": ReferencePriority.CRITICAL,
        "examples.md": ReferencePriority.HIGH,
        "glossary.md": ReferencePriority.MEDIUM,
    },
    "automation": {
        "workflow.md": ReferencePriority.CRITICAL,
        "configuration.md": ReferencePriority.CRITICAL,
        "troubleshooting.md": ReferencePriority.HIGH,
        "examples.md": ReferencePriority.HIGH,
    },
    "analyzer": {
        "api.md": ReferencePriority.CRITICAL,
        "output-formats.md": ReferencePriority.CRITICAL,
        "examples.md": ReferencePriority.HIGH,
        "patterns.md": ReferencePriority.MEDIUM,
    },
    "validator": {
        "rules.md": ReferencePriority.CRITICAL,
        "configuration.md": ReferencePriority.HIGH,
        "examples.md": ReferencePriority.HIGH,
        "troubleshooting.md": ReferencePriority.MEDIUM,
    },
}
```

## Usefulness Scoring

```python
def calculate_usefulness(ref: PrioritizedReference) -> float:
    """Calculate usefulness score for ordering."""

    # Base score from priority (1-5 -> 1.0-0.2)
    base_score = 1.0 - (ref.priority - 1) * 0.2

    # Boost for high access frequency
    frequency_boost = ref.access_frequency * 0.3

    # Boost for being a prerequisite
    prerequisite_boost = min(len(ref.prerequisite_of) * 0.1, 0.3)

    # Penalty for having many dependencies
    dependency_penalty = min(len(ref.depends_on) * 0.05, 0.2)

    return base_score + frequency_boost + prerequisite_boost - dependency_penalty


def order_references(refs: list[PrioritizedReference]) -> list[PrioritizedReference]:
    """Order references by usefulness with dependency constraints."""

    # Calculate usefulness scores
    for ref in refs:
        ref.usefulness_score = calculate_usefulness(ref)

    # Topological sort respecting dependencies
    ordered = topological_sort_by_score(refs)

    return ordered


def topological_sort_by_score(refs: list[PrioritizedReference]) -> list[PrioritizedReference]:
    """Sort by usefulness while respecting dependencies."""
    result = []
    remaining = {r.path: r for r in refs}
    satisfied = set()

    while remaining:
        # Find refs with satisfied dependencies
        ready = [
            r for r in remaining.values()
            if all(d in satisfied for d in r.depends_on)
        ]

        if not ready:
            # Circular dependency - just take highest score
            ready = list(remaining.values())

        # Sort ready items by usefulness
        ready.sort(key=lambda r: -r.usefulness_score)

        # Take the best one
        best = ready[0]
        result.append(best)
        satisfied.add(best.path)
        del remaining[best.path]

    return result
```

## SKILL.md Reference Ordering

```python
def order_skill_md_references(
    skill_type: str,
    references: list[str]
) -> list[str]:
    """Order references for SKILL.md listing."""

    # Get type-specific priorities
    type_priorities = SKILL_TYPE_PRIORITIES.get(skill_type, {})

    def get_priority(ref: str) -> int:
        # Check type-specific first
        if ref in type_priorities:
            return type_priorities[ref].value

        # Fall back to general
        if ref in REFERENCE_PRIORITIES:
            return REFERENCE_PRIORITIES[ref].value

        # Default to medium
        return ReferencePriority.MEDIUM.value

    return sorted(references, key=get_priority)
```

## Content Section Ordering

```python
SECTION_ORDER = {
    # Overview documents
    "overview.md": [
        "purpose",
        "key_features",
        "quick_example",
        "when_to_use",
        "limitations",
    ],

    # Workflow documents
    "workflow.md": [
        "quick_start",
        "basic_workflow",
        "common_tasks",
        "advanced_usage",
        "integration",
    ],

    # API documents
    "api.md": [
        "quick_reference",
        "commands",
        "options",
        "output_formats",
        "examples",
    ],

    # Troubleshooting
    "troubleshooting.md": [
        "quick_fixes",
        "common_errors",
        "configuration_issues",
        "advanced_debugging",
    ],
}

def order_sections(doc_type: str, sections: list[str]) -> list[str]:
    """Order sections within a document by priority."""
    order = SECTION_ORDER.get(doc_type, [])

    def get_order(section: str) -> int:
        try:
            return order.index(section)
        except ValueError:
            return len(order)  # Unknown sections go last

    return sorted(sections, key=get_order)
```

## Access Frequency Estimation

```python
def estimate_access_frequency(ref_path: str, skill_type: str) -> float:
    """Estimate how often a reference will be accessed."""

    # Base frequencies by document type
    base_frequencies = {
        "overview.md": 0.9,
        "quickstart.md": 0.85,
        "workflow.md": 0.8,
        "api.md": 0.75,
        "examples.md": 0.7,
        "patterns.md": 0.5,
        "configuration.md": 0.6,
        "troubleshooting.md": 0.65,
        "faq.md": 0.4,
        "glossary.md": 0.3,
        "internals.md": 0.2,
        "changelog.md": 0.1,
    }

    base = base_frequencies.get(ref_path, 0.5)

    # Adjust by skill type
    type_boosts = {
        "builder": {"templates.md": 0.2, "workflow.md": 0.1},
        "automation": {"configuration.md": 0.2, "troubleshooting.md": 0.15},
        "analyzer": {"output-formats.md": 0.2, "api.md": 0.1},
        "validator": {"rules.md": 0.2, "examples.md": 0.1},
    }

    boost = type_boosts.get(skill_type, {}).get(ref_path, 0)

    return min(base + boost, 1.0)
```

## Priority Visualization

```python
def visualize_priority_order(refs: list[PrioritizedReference]) -> str:
    """Visualize reference priority ordering."""
    lines = [
        "# Reference Priority Order",
        "",
        "| Priority | Reference | Score | Dependencies |",
        "|----------|-----------|-------|--------------|",
    ]

    priority_icons = {
        ReferencePriority.CRITICAL: "🔴",
        ReferencePriority.HIGH: "🟠",
        ReferencePriority.MEDIUM: "🟡",
        ReferencePriority.LOW: "🟢",
        ReferencePriority.SUPPLEMENTARY: "⚪",
    }

    for ref in refs:
        icon = priority_icons.get(ref.priority, "⚪")
        deps = ", ".join(ref.depends_on) if ref.depends_on else "none"
        lines.append(
            f"| {icon} {ref.priority.name} | {ref.path} | "
            f"{ref.usefulness_score:.2f} | {deps} |"
        )

    return "\n".join(lines)
```

## Integration

```python
def prioritize_skill_references(
    skill_name: str,
    skill_type: str,
    references: dict[str, str]
) -> list[PrioritizedReference]:
    """Create prioritized reference list for a skill."""

    prioritized = []

    for path in references:
        # Determine base priority
        if path in SKILL_TYPE_PRIORITIES.get(skill_type, {}):
            priority = SKILL_TYPE_PRIORITIES[skill_type][path]
        elif path in REFERENCE_PRIORITIES:
            priority = REFERENCE_PRIORITIES[path]
        else:
            priority = ReferencePriority.MEDIUM

        # Estimate access frequency
        frequency = estimate_access_frequency(path, skill_type)

        # Detect dependencies from content
        content = references[path]
        depends_on = detect_dependencies(content, list(references.keys()))

        prioritized.append(PrioritizedReference(
            path=path,
            priority=priority,
            access_frequency=frequency,
            prerequisite_of=[],  # Filled in next pass
            depends_on=depends_on,
            usefulness_score=0.0
        ))

    # Fill in prerequisite_of (reverse of depends_on)
    for ref in prioritized:
        for dep in ref.depends_on:
            for other in prioritized:
                if other.path == dep:
                    other.prerequisite_of.append(ref.path)

    # Order by usefulness
    return order_references(prioritized)


def detect_dependencies(content: str, all_refs: list[str]) -> list[str]:
    """Detect which references this content depends on."""
    import re
    deps = []

    # Find links to other references
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(link_pattern, content):
        target = match.group(2)
        if target in all_refs or target.lstrip("./") in all_refs:
            deps.append(target.lstrip("./"))

    # Detect "see X" patterns
    see_pattern = r'[Ss]ee\s+\[?([a-z-]+\.md)\]?'
    for match in re.finditer(see_pattern, content):
        ref = match.group(1)
        if ref in all_refs and ref not in deps:
            deps.append(ref)

    return deps
```
