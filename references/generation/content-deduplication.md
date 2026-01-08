# Content Deduplication

Detect and eliminate repeated content between skill components.

## Deduplication Goals

| Goal | Description |
|------|-------------|
| Token efficiency | Avoid wasting tokens on repeated content |
| Maintainability | Single source of truth for each concept |
| Clarity | Each file has distinct purpose |
| Quality | Reference links instead of duplicating |

## Duplication Types

### 1. Exact Duplicates

Identical text blocks appearing in multiple files.

```python
def find_exact_duplicates(
    files: dict[str, str],
    min_length: int = 50
) -> list[DuplicateMatch]:
    """Find exact text duplicates across files."""
    duplicates = []

    # Extract all paragraphs
    paragraphs: dict[str, list[tuple[str, int]]] = {}  # text -> [(file, line)]

    for filepath, content in files.items():
        for i, para in enumerate(split_paragraphs(content)):
            if len(para) >= min_length:
                normalized = normalize_text(para)
                if normalized not in paragraphs:
                    paragraphs[normalized] = []
                paragraphs[normalized].append((filepath, i))

    # Find duplicates
    for text, locations in paragraphs.items():
        if len(locations) > 1:
            duplicates.append(DuplicateMatch(
                type="exact",
                text=text[:100] + "..." if len(text) > 100 else text,
                locations=locations,
                similarity=1.0
            ))

    return duplicates
```

### 2. Near Duplicates

Similar text with minor variations.

```python
from difflib import SequenceMatcher

def find_near_duplicates(
    files: dict[str, str],
    similarity_threshold: float = 0.85,
    min_length: int = 100
) -> list[DuplicateMatch]:
    """Find near-duplicate content across files."""
    duplicates = []

    # Extract sections
    sections: list[tuple[str, str, str]] = []  # (file, section_id, text)

    for filepath, content in files.items():
        for section_id, section_text in extract_sections(content):
            if len(section_text) >= min_length:
                sections.append((filepath, section_id, section_text))

    # Compare all pairs
    for i, (file1, sec1, text1) in enumerate(sections):
        for file2, sec2, text2 in sections[i+1:]:
            if file1 == file2:
                continue  # Skip same-file comparisons

            similarity = calculate_similarity(text1, text2)
            if similarity >= similarity_threshold:
                duplicates.append(DuplicateMatch(
                    type="near",
                    text=f"{sec1} vs {sec2}",
                    locations=[(file1, sec1), (file2, sec2)],
                    similarity=similarity
                ))

    return duplicates

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity ratio."""
    return SequenceMatcher(None, text1, text2).ratio()
```

### 3. Concept Duplicates

Same concept explained differently in multiple places.

```python
CONCEPT_PATTERNS = {
    "workflow": [
        r"## Workflow",
        r"### Steps",
        r"step\s+\d+:",
        r"1\.\s+\w+\s+2\.\s+\w+"
    ],
    "examples": [
        r"## Examples?",
        r"<example>",
        r"```\w+\n.*?```"
    ],
    "configuration": [
        r"## Config",
        r"### Options",
        r"--\w+\s+<"
    ]
}

def find_concept_duplicates(
    files: dict[str, str]
) -> list[ConceptDuplicate]:
    """Find concepts that appear in multiple files."""
    duplicates = []

    for concept, patterns in CONCEPT_PATTERNS.items():
        locations = []

        for filepath, content in files.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    locations.append(filepath)
                    break

        if len(set(locations)) > 1:
            duplicates.append(ConceptDuplicate(
                concept=concept,
                locations=list(set(locations)),
                recommendation=get_concept_recommendation(concept)
            ))

    return duplicates
```

## Deduplication Strategies

### Strategy 1: Reference Instead of Repeat

Replace duplicated content with references.

```python
def create_reference_link(
    source_file: str,
    target_file: str,
    section: str | None = None
) -> str:
    """Create markdown reference link."""
    rel_path = os.path.relpath(target_file, os.path.dirname(source_file))

    if section:
        return f"See [{section}]({rel_path}#{section.lower().replace(' ', '-')})"
    else:
        return f"See [{os.path.basename(target_file)}]({rel_path})"

# Example transformation
# Before (SKILL.md):
#   ## Configuration
#   Set the following options:
#   - --output: Output directory
#   - --format: Output format (md, html)
#   ...

# After (SKILL.md):
#   ## Configuration
#   See [Configuration Reference](references/config-options.md) for all options.
```

### Strategy 2: Summarize and Link

Keep summary in SKILL.md, detail in references.

```python
def apply_summarize_strategy(
    skill_md: str,
    reference_content: str,
    section: str
) -> tuple[str, str]:
    """Replace detailed section with summary + link."""

    # Extract first paragraph as summary
    paragraphs = reference_content.split("\n\n")
    summary = paragraphs[0] if paragraphs else ""

    # Create link
    link = create_reference_link("SKILL.md", f"references/{section}.md")

    # Replace in SKILL.md
    new_section = f"## {section.title()}\n\n{summary}\n\n{link} for details."

    return new_section, reference_content
```

### Strategy 3: Consolidate to Single Location

Move all instances to one authoritative location.

```python
def consolidate_content(
    duplicates: list[DuplicateMatch],
    files: dict[str, str]
) -> dict[str, str]:
    """Consolidate duplicate content to single location."""

    for dup in duplicates:
        # Determine best location
        best_location = choose_best_location(dup.locations)

        # Keep content in best location
        # Replace in other locations with references
        for location in dup.locations:
            if location != best_location:
                files[location[0]] = replace_with_reference(
                    files[location[0]],
                    dup.text,
                    best_location
                )

    return files

def choose_best_location(locations: list[tuple[str, str]]) -> tuple[str, str]:
    """Choose best location for consolidated content."""
    # Priority: references/ > SKILL.md > scripts/
    priority = {
        "references/": 1,
        "SKILL.md": 2,
        "scripts/": 3
    }

    return min(locations, key=lambda x: priority.get(
        x[0].split("/")[0] + "/" if "/" in x[0] else x[0],
        99
    ))
```

## Content Placement Rules

### SKILL.md Content

| Include | Exclude |
|---------|---------|
| High-level overview | Detailed specifications |
| Core workflow (summary) | Step-by-step tutorials |
| 2-3 key examples | Exhaustive examples |
| Quick reference | Full API reference |

### References Content

| Include | Exclude |
|---------|---------|
| Detailed explanations | Overview (belongs in SKILL.md) |
| Complete specifications | Duplicates of SKILL.md |
| All edge cases | Basic examples only |
| Troubleshooting guides | Installation steps |

## Deduplication Report

```python
@dataclass
class DeduplicationReport:
    exact_duplicates: list[DuplicateMatch]
    near_duplicates: list[DuplicateMatch]
    concept_duplicates: list[ConceptDuplicate]
    recommendations: list[str]
    token_savings: int

def generate_deduplication_report(
    files: dict[str, str]
) -> DeduplicationReport:
    """Generate comprehensive deduplication report."""

    exact = find_exact_duplicates(files)
    near = find_near_duplicates(files)
    concepts = find_concept_duplicates(files)

    recommendations = []
    token_savings = 0

    for dup in exact:
        savings = estimate_token_savings(dup)
        token_savings += savings
        recommendations.append(
            f"Remove exact duplicate: '{dup.text[:50]}...' "
            f"(saves ~{savings} tokens)"
        )

    for dup in near:
        if dup.similarity > 0.9:
            recommendations.append(
                f"Consolidate near-duplicate ({dup.similarity:.0%}): "
                f"{dup.locations[0][0]} and {dup.locations[1][0]}"
            )

    for concept in concepts:
        recommendations.append(
            f"Concept '{concept.concept}' appears in {len(concept.locations)} files: "
            f"{concept.recommendation}"
        )

    return DeduplicationReport(
        exact_duplicates=exact,
        near_duplicates=near,
        concept_duplicates=concepts,
        recommendations=recommendations,
        token_savings=token_savings
    )
```

## Output Format

```json
{
  "exact_duplicates": [
    {
      "type": "exact",
      "text": "This workflow consists of three steps...",
      "locations": [
        ["SKILL.md", "workflow"],
        ["references/workflow.md", "overview"]
      ],
      "similarity": 1.0
    }
  ],
  "near_duplicates": [
    {
      "type": "near",
      "text": "Configuration section vs Options section",
      "locations": [
        ["SKILL.md", "configuration"],
        ["references/config.md", "options"]
      ],
      "similarity": 0.92
    }
  ],
  "concept_duplicates": [
    {
      "concept": "examples",
      "locations": ["SKILL.md", "references/examples.md"],
      "recommendation": "Keep examples in references/examples.md, link from SKILL.md"
    }
  ],
  "recommendations": [
    "Remove exact duplicate in workflow sections (saves ~150 tokens)",
    "Consolidate configuration content to references/config.md"
  ],
  "token_savings": 320
}
```

## Integration

```python
def validate_no_duplication(files: dict[str, str]) -> ValidationResult:
    """Validate skill has no content duplication."""
    report = generate_deduplication_report(files)

    errors = []
    warnings = []

    # Exact duplicates are errors
    for dup in report.exact_duplicates:
        errors.append(f"Exact duplicate found: {dup.text[:50]}...")

    # High-similarity near duplicates are warnings
    for dup in report.near_duplicates:
        if dup.similarity > 0.9:
            warnings.append(f"Near duplicate ({dup.similarity:.0%}): {dup.text}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=report
    )
```
