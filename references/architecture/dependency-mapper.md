# Component Dependency Mapper

Map dependencies between skill components for generation ordering.

## Dependency Model

```python
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

class DependencyType(Enum):
    REFERENCES = "references"      # A references content from B
    REQUIRES = "requires"          # A requires B to exist
    VALIDATES = "validates"        # A validates B
    GENERATES = "generates"        # A generates B
    INCLUDES = "includes"          # A includes/imports B

@dataclass
class Component:
    id: str
    path: str
    type: Literal["skill_md", "reference", "script", "template"]
    description: str

@dataclass
class Dependency:
    source: str      # Component ID
    target: str      # Component ID
    type: DependencyType
    required: bool   # True = hard dependency, False = soft
    description: str

@dataclass
class DependencyGraph:
    components: list[Component]
    dependencies: list[Dependency]
    generation_order: list[str]  # Topologically sorted component IDs
    parallel_groups: list[list[str]]  # Components that can be generated together
```

## Standard Skill Dependencies

### Component Hierarchy

```
SKILL.md (root)
├── references/
│   ├── concepts.md      ← SKILL.md references
│   ├── workflow.md      ← SKILL.md references
│   └── templates.md     ← scripts may use
└── scripts/
    ├── generate.sh      ← uses templates.md
    └── validate.sh      ← validates SKILL.md
```

### Dependency Rules

```python
STANDARD_DEPENDENCIES = [
    # SKILL.md references documentation
    Dependency(
        source="skill_md",
        target="concepts_md",
        type=DependencyType.REFERENCES,
        required=False,
        description="SKILL.md may reference concepts"
    ),
    Dependency(
        source="skill_md",
        target="workflow_md",
        type=DependencyType.REFERENCES,
        required=False,
        description="SKILL.md may reference workflow details"
    ),

    # Scripts validate/generate from SKILL.md
    Dependency(
        source="validate_sh",
        target="skill_md",
        type=DependencyType.VALIDATES,
        required=True,
        description="validate.sh validates SKILL.md structure"
    ),
    Dependency(
        source="generate_sh",
        target="templates_md",
        type=DependencyType.REQUIRES,
        required=False,
        description="generate.sh may use templates"
    ),
]
```

## Dependency Detection

### Automatic Detection

```python
def detect_dependencies(
    components: list[Component],
    content_map: dict[str, str]
) -> list[Dependency]:
    """Automatically detect dependencies from content analysis."""
    dependencies = []

    for component in components:
        content = content_map.get(component.id, "")

        # Detect file references
        for other in components:
            if other.id == component.id:
                continue

            # Check for path references
            if other.path in content:
                dependencies.append(Dependency(
                    source=component.id,
                    target=other.id,
                    type=DependencyType.REFERENCES,
                    required=False,
                    description=f"{component.path} references {other.path}"
                ))

            # Check for markdown links
            link_pattern = f"[{other.path}]" or f"({other.path})"
            if link_pattern in content:
                dependencies.append(Dependency(
                    source=component.id,
                    target=other.id,
                    type=DependencyType.INCLUDES,
                    required=True,
                    description=f"{component.path} links to {other.path}"
                ))

    return dependencies
```

### Pattern-Based Detection

```python
REFERENCE_PATTERNS = {
    # Markdown reference patterns
    r"See \[([^\]]+)\]": DependencyType.REFERENCES,
    r"Refer to `([^`]+\.md)`": DependencyType.REFERENCES,
    r"documented in ([^\s]+\.md)": DependencyType.REFERENCES,

    # Script patterns
    r"source\s+([^\s]+\.sh)": DependencyType.INCLUDES,
    r"\.\s+([^\s]+\.sh)": DependencyType.INCLUDES,

    # Template patterns
    r"template:\s*([^\s]+)": DependencyType.REQUIRES,
    r"--template\s+([^\s]+)": DependencyType.REQUIRES,
}

def detect_pattern_dependencies(
    component: Component,
    content: str
) -> list[Dependency]:
    """Detect dependencies using regex patterns."""
    dependencies = []

    for pattern, dep_type in REFERENCE_PATTERNS.items():
        matches = re.findall(pattern, content)
        for match in matches:
            dependencies.append(Dependency(
                source=component.id,
                target=normalize_path(match),
                type=dep_type,
                required=dep_type != DependencyType.REFERENCES,
                description=f"Pattern match: {pattern}"
            ))

    return dependencies
```

## Graph Construction

```python
def build_dependency_graph(
    skill_type: str,
    planned_components: list[Component]
) -> DependencyGraph:
    """Build complete dependency graph for skill."""

    # Start with standard dependencies for skill type
    dependencies = get_standard_dependencies(skill_type)

    # Add type-specific dependencies
    if skill_type == "builder":
        dependencies.extend([
            Dependency("generate_sh", "skill_md", DependencyType.REQUIRES, True, ""),
            Dependency("generate_sh", "templates_md", DependencyType.REQUIRES, False, ""),
        ])
    elif skill_type == "validator":
        dependencies.extend([
            Dependency("validate_sh", "skill_md", DependencyType.VALIDATES, True, ""),
        ])

    # Filter to only include planned components
    component_ids = {c.id for c in planned_components}
    dependencies = [
        d for d in dependencies
        if d.source in component_ids and d.target in component_ids
    ]

    # Calculate generation order
    generation_order = topological_sort(planned_components, dependencies)

    # Identify parallel groups
    parallel_groups = identify_parallel_groups(planned_components, dependencies)

    return DependencyGraph(
        components=planned_components,
        dependencies=dependencies,
        generation_order=generation_order,
        parallel_groups=parallel_groups
    )
```

## Topological Sort

```python
def topological_sort(
    components: list[Component],
    dependencies: list[Dependency]
) -> list[str]:
    """Sort components by dependency order."""

    # Build adjacency list
    graph: dict[str, list[str]] = {c.id: [] for c in components}
    in_degree: dict[str, int] = {c.id: 0 for c in components}

    for dep in dependencies:
        if dep.required:  # Only consider hard dependencies
            graph[dep.target].append(dep.source)
            in_degree[dep.source] += 1

    # Kahn's algorithm
    queue = [c for c in in_degree if in_degree[c] == 0]
    result = []

    while queue:
        # Sort queue for deterministic ordering
        queue.sort()
        node = queue.pop(0)
        result.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles
    if len(result) != len(components):
        cycle = detect_cycle(components, dependencies)
        raise DependencyCycleError(f"Circular dependency: {cycle}")

    return result
```

## Parallel Groups

```python
def identify_parallel_groups(
    components: list[Component],
    dependencies: list[Dependency]
) -> list[list[str]]:
    """Identify components that can be generated in parallel."""

    # Build dependency sets
    depends_on: dict[str, set[str]] = {c.id: set() for c in components}
    for dep in dependencies:
        if dep.required:
            depends_on[dep.source].add(dep.target)

    # Group by depth level
    levels: dict[str, int] = {}

    def get_level(component_id: str) -> int:
        if component_id in levels:
            return levels[component_id]

        deps = depends_on[component_id]
        if not deps:
            levels[component_id] = 0
        else:
            levels[component_id] = 1 + max(get_level(d) for d in deps)

        return levels[component_id]

    for c in components:
        get_level(c.id)

    # Group by level
    groups: dict[int, list[str]] = {}
    for component_id, level in levels.items():
        if level not in groups:
            groups[level] = []
        groups[level].append(component_id)

    # Return sorted groups
    return [groups[i] for i in sorted(groups.keys())]
```

## Visualization

### Text Format

```
Dependency Graph: api-doc-generator
══════════════════════════════════════════════════════════════════════

Components:
  [1] SKILL.md              (skill_md)
  [2] references/concepts.md (reference)
  [3] references/workflow.md (reference)
  [4] scripts/generate.sh   (script)
  [5] scripts/validate.sh   (script)

Dependencies:
  [1] ──references──▶ [2] concepts.md
  [1] ──references──▶ [3] workflow.md
  [4] ──requires────▶ [1] SKILL.md
  [5] ──validates───▶ [1] SKILL.md

Generation Order:
  Level 0: [2] concepts.md, [3] workflow.md  (parallel)
  Level 1: [1] SKILL.md
  Level 2: [4] generate.sh, [5] validate.sh  (parallel)

══════════════════════════════════════════════════════════════════════
```

### JSON Format

```json
{
  "components": [
    {"id": "skill_md", "path": "SKILL.md", "type": "skill_md"},
    {"id": "concepts_md", "path": "references/concepts.md", "type": "reference"},
    {"id": "workflow_md", "path": "references/workflow.md", "type": "reference"},
    {"id": "generate_sh", "path": "scripts/generate.sh", "type": "script"},
    {"id": "validate_sh", "path": "scripts/validate.sh", "type": "script"}
  ],
  "dependencies": [
    {"source": "skill_md", "target": "concepts_md", "type": "references", "required": false},
    {"source": "skill_md", "target": "workflow_md", "type": "references", "required": false},
    {"source": "generate_sh", "target": "skill_md", "type": "requires", "required": true},
    {"source": "validate_sh", "target": "skill_md", "type": "validates", "required": true}
  ],
  "generation_order": ["concepts_md", "workflow_md", "skill_md", "generate_sh", "validate_sh"],
  "parallel_groups": [
    ["concepts_md", "workflow_md"],
    ["skill_md"],
    ["generate_sh", "validate_sh"]
  ]
}
```

## Integration

```python
def plan_generation_sequence(graph: DependencyGraph) -> list[GenerationStep]:
    """Convert dependency graph to generation steps."""
    steps = []

    for group in graph.parallel_groups:
        if len(group) == 1:
            # Sequential step
            component = next(c for c in graph.components if c.id == group[0])
            steps.append(GenerationStep(
                components=[component],
                parallel=False,
                dependencies=[
                    d for d in graph.dependencies
                    if d.source == component.id
                ]
            ))
        else:
            # Parallel step
            components = [c for c in graph.components if c.id in group]
            steps.append(GenerationStep(
                components=components,
                parallel=True,
                dependencies=[
                    d for d in graph.dependencies
                    if d.source in group
                ]
            ))

    return steps
```
