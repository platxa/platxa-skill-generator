# Patterns.md Generator

Generate pattern documentation with examples and usage guidance.

## Pattern Document Structure

```markdown
# Patterns

Common patterns and best practices for using this skill.

## Pattern: [Pattern Name]

### When to Use

[Conditions that indicate this pattern should be used]

### How It Works

[Explanation of the pattern]

### Example

[Code or usage example]

### Variations

[Alternative approaches or modifications]

---

## Pattern: [Next Pattern]
...
```

## Pattern Model

```python
from dataclasses import dataclass

@dataclass
class Pattern:
    name: str
    description: str
    when_to_use: list[str]
    how_it_works: str
    example: str
    example_language: str  # For code highlighting
    variations: list[str]
    anti_patterns: list[str]  # What NOT to do
    related_patterns: list[str]

@dataclass
class PatternsDocument:
    skill_name: str
    patterns: list[Pattern]
    introduction: str
```

## Pattern Categories

### By Skill Type

```python
PATTERN_TEMPLATES = {
    "builder": [
        Pattern(
            name="Template-Based Generation",
            description="Generate output from predefined templates",
            when_to_use=[
                "Output structure is consistent",
                "Multiple similar outputs needed",
                "Customization through variables"
            ],
            how_it_works="Load template, substitute variables, validate output",
            example="...",
            example_language="bash",
            variations=["Jinja2 templates", "Mustache templates"],
            anti_patterns=["Hardcoding output structure"],
            related_patterns=["Variable Substitution"]
        ),
        Pattern(
            name="Incremental Building",
            description="Build output step by step",
            when_to_use=[
                "Complex output with dependencies",
                "Need progress feedback",
                "Partial results useful"
            ],
            how_it_works="...",
            example="...",
            example_language="python",
            variations=[],
            anti_patterns=["All-at-once generation without feedback"],
            related_patterns=["Progressive Enhancement"]
        ),
    ],
    "guide": [
        Pattern(
            name="Progressive Disclosure",
            description="Present information from simple to complex",
            when_to_use=[
                "Teaching new concepts",
                "Users have varying expertise",
                "Content is hierarchical"
            ],
            how_it_works="Start with overview, link to details",
            example="...",
            example_language="markdown",
            variations=["Accordion pattern", "Drill-down"],
            anti_patterns=["Information overload upfront"],
            related_patterns=["Layered Documentation"]
        ),
    ],
    "automation": [
        Pattern(
            name="Idempotent Operations",
            description="Operations that produce same result when repeated",
            when_to_use=[
                "Scripts may be re-run",
                "Recovery from partial failure",
                "CI/CD pipelines"
            ],
            how_it_works="Check state before acting, skip if done",
            example="...",
            example_language="bash",
            variations=[],
            anti_patterns=["Assuming fresh state"],
            related_patterns=["State Checking"]
        ),
    ],
    "analyzer": [
        Pattern(
            name="Filter and Report",
            description="Collect findings, filter by severity, report",
            when_to_use=[
                "Many potential findings",
                "Configurable sensitivity",
                "Different output audiences"
            ],
            how_it_works="Gather all findings, apply filters, format report",
            example="...",
            example_language="python",
            variations=["Streaming analysis", "Batch analysis"],
            anti_patterns=["Reporting everything without filtering"],
            related_patterns=["Severity Classification"]
        ),
    ],
    "validator": [
        Pattern(
            name="Fail Fast",
            description="Stop at first critical error",
            when_to_use=[
                "Errors are blocking",
                "Quick feedback needed",
                "Resources are limited"
            ],
            how_it_works="Check critical rules first, exit on failure",
            example="...",
            example_language="bash",
            variations=["Collect all errors", "Warnings continue"],
            anti_patterns=["Continuing past fatal errors"],
            related_patterns=["Error Collection"]
        ),
    ],
}
```

## Generator Implementation

```python
def generate_patterns_md(
    skill_name: str,
    skill_type: str,
    domain_patterns: list[Pattern] | None = None
) -> str:
    """Generate patterns.md for a skill."""

    # Get base patterns for skill type
    base_patterns = PATTERN_TEMPLATES.get(skill_type, [])

    # Merge with domain-specific patterns
    all_patterns = base_patterns + (domain_patterns or [])

    # Build document
    lines = [
        "# Patterns",
        "",
        f"Common patterns and best practices for {skill_name}.",
        "",
    ]

    for pattern in all_patterns:
        lines.extend(format_pattern(pattern))
        lines.append("")
        lines.append("---")
        lines.append("")

    # Remove trailing separator
    if lines[-2] == "---":
        lines = lines[:-2]

    return "\n".join(lines)

def format_pattern(pattern: Pattern) -> list[str]:
    """Format a single pattern as markdown."""
    lines = [
        f"## Pattern: {pattern.name}",
        "",
        pattern.description,
        "",
        "### When to Use",
        "",
    ]

    for condition in pattern.when_to_use:
        lines.append(f"- {condition}")

    lines.extend([
        "",
        "### How It Works",
        "",
        pattern.how_it_works,
        "",
        "### Example",
        "",
        f"```{pattern.example_language}",
        pattern.example,
        "```",
    ])

    if pattern.variations:
        lines.extend([
            "",
            "### Variations",
            "",
        ])
        for variation in pattern.variations:
            lines.append(f"- {variation}")

    if pattern.anti_patterns:
        lines.extend([
            "",
            "### Anti-Patterns (Avoid)",
            "",
        ])
        for anti in pattern.anti_patterns:
            lines.append(f"- ❌ {anti}")

    if pattern.related_patterns:
        lines.extend([
            "",
            "### Related Patterns",
            "",
        ])
        for related in pattern.related_patterns:
            lines.append(f"- {related}")

    return lines
```

## Domain Pattern Detection

```python
DOMAIN_PATTERN_INDICATORS = {
    "api": [
        Pattern(
            name="Request-Response Logging",
            description="Log API requests and responses for debugging",
            when_to_use=["API integration", "Debugging needed"],
            how_it_works="Intercept requests, log details, continue",
            example="curl -v https://api.example.com",
            example_language="bash",
            variations=["Selective logging", "Structured logs"],
            anti_patterns=["Logging sensitive data"],
            related_patterns=["Audit Trail"]
        ),
    ],
    "file": [
        Pattern(
            name="Atomic File Operations",
            description="Write to temp file, then rename",
            when_to_use=["Data integrity critical", "Concurrent access"],
            how_it_works="Write to .tmp, sync, rename",
            example="write temp; sync; mv temp final",
            example_language="bash",
            variations=["Backup original first"],
            anti_patterns=["Direct overwrite"],
            related_patterns=["Backup Before Modify"]
        ),
    ],
    "validation": [
        Pattern(
            name="Schema Validation",
            description="Validate against formal schema",
            when_to_use=["Structured input", "Strict requirements"],
            how_it_works="Parse input, validate against schema, report errors",
            example="jsonschema --validate data.json schema.json",
            example_language="bash",
            variations=["Partial validation", "Coercion"],
            anti_patterns=["Ad-hoc validation only"],
            related_patterns=["Type Checking"]
        ),
    ],
}

def detect_domain_patterns(
    description: str,
    requirements: list[str]
) -> list[Pattern]:
    """Detect relevant patterns from domain keywords."""
    patterns = []
    combined = (description + " " + " ".join(requirements)).lower()

    for keyword, domain_patterns in DOMAIN_PATTERN_INDICATORS.items():
        if keyword in combined:
            patterns.extend(domain_patterns)

    return patterns
```

## Example Output

```markdown
# Patterns

Common patterns and best practices for api-doc-generator.

## Pattern: Template-Based Generation

Generate output from predefined templates.

### When to Use

- Output structure is consistent
- Multiple similar outputs needed
- Customization through variables

### How It Works

Load template, substitute variables, validate output.

### Example

```bash
# Load template
template=$(cat templates/endpoint.md.template)

# Substitute variables
output="${template//\{\{endpoint\}\}/$ENDPOINT}"
output="${output//\{\{method\}\}/$METHOD}"

# Write output
echo "$output" > "docs/${ENDPOINT}.md"
```

### Variations

- Jinja2 templates
- Mustache templates

### Anti-Patterns (Avoid)

- ❌ Hardcoding output structure

### Related Patterns

- Variable Substitution

---

## Pattern: Request-Response Logging

Log API requests and responses for debugging.

### When to Use

- API integration
- Debugging needed

### How It Works

Intercept requests, log details, continue.

### Example

```bash
curl -v https://api.example.com/endpoint 2>&1 | tee api.log
```

### Anti-Patterns (Avoid)

- ❌ Logging sensitive data

### Related Patterns

- Audit Trail
```
