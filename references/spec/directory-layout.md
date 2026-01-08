# Skill Directory Layout

ASCII tree diagrams showing skill directory structures.

## Minimal Skill

```
skill-name/
└── SKILL.md                 # Required: Main skill file
```

**Use when:** Simple skills with no external references.

## Standard Skill

```
skill-name/
├── SKILL.md                 # Required: Main skill file
└── references/              # Optional: Additional context
    ├── overview.md          # High-level documentation
    ├── workflow.md          # Step-by-step process
    └── examples.md          # Usage examples
```

**Use when:** Skills needing detailed documentation.

## Full Skill

```
skill-name/
├── SKILL.md                 # Required: Main skill file
├── README.md                # Optional: External documentation
├── references/              # Optional: Additional context
│   ├── overview.md          # High-level documentation
│   ├── workflow.md          # Step-by-step process
│   ├── api.md               # API reference
│   ├── examples.md          # Usage examples
│   └── troubleshooting.md   # Common issues
└── scripts/                 # Optional: Helper scripts
    ├── validate.sh          # Validation script
    └── generate.sh          # Generation script
```

**Use when:** Complex skills with automation needs.

## By Skill Type

### Builder Skill

```
builder-skill/
├── SKILL.md
├── references/
│   ├── templates.md         # Output templates
│   ├── patterns.md          # Common patterns
│   └── customization.md     # Configuration options
└── scripts/
    └── generate.sh          # Generation helper
```

### Guide Skill

```
guide-skill/
├── SKILL.md
└── references/
    ├── steps.md             # Detailed steps
    ├── tips.md              # Best practices
    └── faq.md               # Common questions
```

### Automation Skill

```
automation-skill/
├── SKILL.md
├── references/
│   ├── commands.md          # Available commands
│   └── configuration.md     # Settings
└── scripts/
    ├── run.sh               # Main automation
    └── cleanup.sh           # Cleanup script
```

### Analyzer Skill

```
analyzer-skill/
├── SKILL.md
└── references/
    ├── metrics.md           # Metrics definitions
    ├── thresholds.md        # Score thresholds
    └── report-format.md     # Output format
```

### Validator Skill

```
validator-skill/
├── SKILL.md
└── references/
    ├── rules.md             # Validation rules
    ├── severity.md          # Issue severity
    └── fixes.md             # Fix suggestions
```

## Installation Locations

### User Skills (Global)

```
~/.claude/
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    ├── skill-two/
    │   ├── SKILL.md
    │   └── references/
    └── skill-three/
        ├── SKILL.md
        ├── references/
        └── scripts/
```

### Project Skills (Local)

```
project/
├── .claude/
│   └── skills/
│       └── project-skill/
│           └── SKILL.md
├── src/
└── package.json
```

## File Descriptions

| File/Directory | Required | Purpose |
|----------------|----------|---------|
| `SKILL.md` | Yes | Main skill instructions with YAML frontmatter |
| `README.md` | No | External documentation for humans |
| `references/` | No | Additional context files |
| `scripts/` | No | Helper shell scripts |
| `*.md` | - | Markdown files for documentation |
| `*.sh` | - | Shell scripts for automation |

## Token Budget Layout

```
skill-name/                    Total: ≤15,000 tokens
├── SKILL.md                   ≤5,000 tokens
└── references/                ≤10,000 tokens total
    ├── overview.md            ~2,000 tokens
    ├── workflow.md            ~3,000 tokens
    ├── api.md                 ~2,500 tokens
    └── examples.md            ~2,500 tokens
```

## Tree Generator

```python
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TreeNode:
    name: str
    is_dir: bool
    children: list['TreeNode']
    comment: str | None = None

class TreeGenerator:
    """Generate ASCII tree diagrams."""

    def generate(self, root: Path, max_depth: int = 3) -> str:
        """Generate tree from directory."""
        tree = self._build_tree(root, 0, max_depth)
        return self._render(tree)

    def _build_tree(self, path: Path, depth: int, max_depth: int) -> TreeNode:
        """Build tree structure."""
        children = []

        if path.is_dir() and depth < max_depth:
            for child in sorted(path.iterdir()):
                if child.name.startswith('.'):
                    continue
                children.append(self._build_tree(child, depth + 1, max_depth))

        return TreeNode(
            name=path.name,
            is_dir=path.is_dir(),
            children=children,
            comment=self._get_comment(path)
        )

    def _render(self, node: TreeNode, prefix: str = "", is_last: bool = True) -> str:
        """Render tree as ASCII."""
        lines = []

        # Current node
        connector = "└── " if is_last else "├── "
        suffix = "/" if node.is_dir else ""
        comment = f"  # {node.comment}" if node.comment else ""

        if prefix:
            lines.append(f"{prefix}{connector}{node.name}{suffix}{comment}")
        else:
            lines.append(f"{node.name}{suffix}{comment}")

        # Children
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            is_child_last = (i == len(node.children) - 1)
            lines.append(self._render(child, child_prefix, is_child_last))

        return "\n".join(lines)

    def _get_comment(self, path: Path) -> str | None:
        """Get comment for file type."""
        comments = {
            "SKILL.md": "Required: Main skill file",
            "README.md": "Optional: External documentation",
            "references": "Optional: Additional context",
            "scripts": "Optional: Helper scripts",
        }
        return comments.get(path.name)
```

## Validation

```python
def validate_layout(skill_path: Path) -> list[str]:
    """Validate skill directory layout."""
    errors = []

    # Required: SKILL.md
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing required file: SKILL.md")

    # Check for unexpected files
    allowed_extensions = {".md", ".sh", ".json", ".yaml", ".yml"}
    for file in skill_path.rglob("*"):
        if file.is_file() and file.suffix not in allowed_extensions:
            errors.append(f"Unexpected file type: {file.name}")

    # Check directory names
    allowed_dirs = {"references", "scripts"}
    for dir in skill_path.iterdir():
        if dir.is_dir() and dir.name not in allowed_dirs:
            errors.append(f"Unexpected directory: {dir.name}")

    return errors
```
