# Examples Directory Generator

Generate working examples categorized by use case.

## Directory Structure

```
skill-name/
├── references/
│   └── examples.md          # Examples index/documentation
└── examples/                 # Working example files
    ├── basic/
    │   ├── README.md         # Basic usage instructions
    │   ├── input.txt         # Sample input
    │   └── expected.md       # Expected output
    ├── advanced/
    │   ├── README.md
    │   ├── input.yaml
    │   └── expected.md
    └── edge-cases/
        ├── README.md
        ├── empty-input.txt
        └── special-chars.txt
```

## Example Model

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Example:
    name: str
    category: str  # basic, advanced, edge-case
    description: str
    input_file: str
    input_content: str
    expected_output: str
    command: str  # How to run
    notes: list[str]

@dataclass
class ExampleCategory:
    name: str
    description: str
    examples: list[Example]

@dataclass
class ExamplesDirectory:
    categories: list[ExampleCategory]
    readme_content: str
```

## Category Templates

```python
EXAMPLE_CATEGORIES = {
    "builder": [
        ExampleCategory(
            name="basic",
            description="Simple, common use cases",
            examples=[]
        ),
        ExampleCategory(
            name="advanced",
            description="Complex scenarios with multiple options",
            examples=[]
        ),
        ExampleCategory(
            name="templates",
            description="Custom template examples",
            examples=[]
        ),
    ],
    "guide": [
        ExampleCategory(
            name="tutorials",
            description="Step-by-step learning examples",
            examples=[]
        ),
        ExampleCategory(
            name="quick-reference",
            description="Common lookup scenarios",
            examples=[]
        ),
    ],
    "automation": [
        ExampleCategory(
            name="basic",
            description="Simple automation scenarios",
            examples=[]
        ),
        ExampleCategory(
            name="pipelines",
            description="Multi-step workflow examples",
            examples=[]
        ),
        ExampleCategory(
            name="error-handling",
            description="Recovery and retry examples",
            examples=[]
        ),
    ],
    "analyzer": [
        ExampleCategory(
            name="basic",
            description="Simple analysis examples",
            examples=[]
        ),
        ExampleCategory(
            name="reports",
            description="Different report format examples",
            examples=[]
        ),
    ],
    "validator": [
        ExampleCategory(
            name="valid",
            description="Examples that pass validation",
            examples=[]
        ),
        ExampleCategory(
            name="invalid",
            description="Examples that fail (for testing)",
            examples=[]
        ),
        ExampleCategory(
            name="edge-cases",
            description="Boundary condition examples",
            examples=[]
        ),
    ],
}
```

## Generator Implementation

```python
def generate_examples_directory(
    skill_name: str,
    skill_type: str,
    domain_examples: list[Example] | None = None
) -> dict[str, str]:
    """Generate examples directory structure."""

    files = {}

    # Get categories for skill type
    categories = EXAMPLE_CATEGORIES.get(skill_type, [
        ExampleCategory("basic", "Basic examples", []),
        ExampleCategory("advanced", "Advanced examples", [])
    ])

    # Add domain examples to appropriate categories
    if domain_examples:
        for example in domain_examples:
            for cat in categories:
                if cat.name == example.category:
                    cat.examples.append(example)
                    break

    # Generate main README
    files["examples/README.md"] = generate_examples_readme(
        skill_name, categories
    )

    # Generate category directories
    for category in categories:
        cat_path = f"examples/{category.name}"

        # Category README
        files[f"{cat_path}/README.md"] = generate_category_readme(
            category, skill_name
        )

        # Generate example files
        for example in category.examples:
            files[f"{cat_path}/{example.input_file}"] = example.input_content
            if example.expected_output:
                output_name = Path(example.input_file).stem + "-expected.md"
                files[f"{cat_path}/{output_name}"] = example.expected_output

    # Generate examples.md reference
    files["references/examples.md"] = generate_examples_reference(
        skill_name, categories
    )

    return files


def generate_examples_readme(
    skill_name: str,
    categories: list[ExampleCategory]
) -> str:
    """Generate main examples README."""
    lines = [
        "# Examples",
        "",
        f"Working examples for {skill_name}.",
        "",
        "## Categories",
        "",
    ]

    for cat in categories:
        lines.append(f"### [{cat.name}/]({cat.name}/)")
        lines.append("")
        lines.append(cat.description)
        lines.append("")
        if cat.examples:
            for ex in cat.examples:
                lines.append(f"- `{ex.input_file}` - {ex.description}")
            lines.append("")

    lines.extend([
        "## Running Examples",
        "",
        "Each example directory contains:",
        "- `README.md` - Instructions for this example",
        "- Input file(s) - Sample input data",
        "- `*-expected.md` - Expected output for verification",
        "",
        "To run an example:",
        "",
        "```bash",
        f"# From skill directory",
        f"/{skill_name} examples/basic/input.txt",
        "```",
    ])

    return "\n".join(lines)


def generate_category_readme(
    category: ExampleCategory,
    skill_name: str
) -> str:
    """Generate README for an example category."""
    lines = [
        f"# {category.name.title()} Examples",
        "",
        category.description,
        "",
        "## Examples",
        "",
    ]

    if category.examples:
        for ex in category.examples:
            lines.extend([
                f"### {ex.name}",
                "",
                ex.description,
                "",
                "**Input:**",
                f"```",
                ex.input_content[:200] + ("..." if len(ex.input_content) > 200 else ""),
                "```",
                "",
                "**Command:**",
                "```bash",
                ex.command,
                "```",
                "",
            ])
            if ex.notes:
                lines.append("**Notes:**")
                for note in ex.notes:
                    lines.append(f"- {note}")
                lines.append("")
    else:
        lines.append("*Examples will be generated based on skill requirements.*")

    return "\n".join(lines)


def generate_examples_reference(
    skill_name: str,
    categories: list[ExampleCategory]
) -> str:
    """Generate references/examples.md."""
    lines = [
        "# Examples Reference",
        "",
        f"Comprehensive examples for using {skill_name}.",
        "",
        "## Quick Examples",
        "",
    ]

    # Add inline examples for quick reference
    for cat in categories:
        if cat.examples:
            example = cat.examples[0]  # First example
            lines.extend([
                f"### {cat.name.title()}: {example.name}",
                "",
                example.description,
                "",
                "<example>",
                f'user: "{example.command}"',
                f'assistant: "Processing {example.input_file}..."',
                "</example>",
                "",
            ])

    lines.extend([
        "## All Examples",
        "",
        "See the [examples/](../examples/) directory for:",
        "",
    ])

    for cat in categories:
        lines.append(f"- **{cat.name}/** - {cat.description}")

    return "\n".join(lines)
```

## Example Content Templates

```python
EXAMPLE_TEMPLATES = {
    "basic_text": Example(
        name="Simple Text",
        category="basic",
        description="Process a simple text file",
        input_file="input.txt",
        input_content="""Hello, world!
This is a sample input file.
It contains multiple lines.
""",
        expected_output="""# Output

Processed content from input.txt

## Content

Hello, world!
This is a sample input file.
It contains multiple lines.
""",
        command="/{skill_name} examples/basic/input.txt",
        notes=["Most common use case", "Default options"]
    ),

    "yaml_config": Example(
        name="YAML Configuration",
        category="advanced",
        description="Process with YAML configuration",
        input_file="config.yaml",
        input_content="""name: example
options:
  format: markdown
  verbose: true
content:
  title: Example Document
  sections:
    - overview
    - details
""",
        expected_output="...",
        command="/{skill_name} --config examples/advanced/config.yaml",
        notes=["Uses configuration file", "All options shown"]
    ),

    "empty_input": Example(
        name="Empty Input",
        category="edge-cases",
        description="Handle empty input gracefully",
        input_file="empty.txt",
        input_content="",
        expected_output="",
        command="/{skill_name} examples/edge-cases/empty.txt",
        notes=["Should not error", "May produce warning"]
    ),
}
```

## Integration

```python
def plan_examples(
    skill_name: str,
    skill_type: str,
    requirements: list[str]
) -> list[Example]:
    """Plan examples based on skill requirements."""
    examples = []

    # Always include basic example
    basic = EXAMPLE_TEMPLATES["basic_text"]
    basic.command = basic.command.replace("{skill_name}", skill_name)
    examples.append(basic)

    # Add type-specific examples
    if skill_type == "builder":
        examples.append(EXAMPLE_TEMPLATES["yaml_config"])

    # Add edge case for validators
    if skill_type == "validator":
        examples.append(EXAMPLE_TEMPLATES["empty_input"])

    # Detect domain-specific examples
    req_text = " ".join(requirements).lower()
    if "yaml" in req_text or "config" in req_text:
        examples.append(EXAMPLE_TEMPLATES["yaml_config"])

    return examples
```
