# Naming Conventions

File and directory naming standards for generated skills.

## Skill Name

| Rule | Example | Invalid |
|------|---------|---------|
| Hyphen-case | `api-doc-generator` | `apiDocGenerator` |
| Lowercase only | `code-review` | `Code-Review` |
| 2-64 characters | `my-skill` | `a`, `this-is-a-very-long-name...` |
| No double hyphens | `my-skill` | `my--skill` |
| Start with letter | `api-tool` | `123-tool` |
| End with alphanumeric | `tool-v2` | `tool-` |

```regex
^[a-z][a-z0-9-]*[a-z0-9]$
```

## File Names

### Reference Files

| Convention | Pattern | Example |
|------------|---------|---------|
| Hyphen-case | `{topic}.md` | `best-practices.md` |
| Lowercase | `*.md` | `workflow.md` |
| Descriptive | `{noun}-{noun}.md` | `domain-expertise.md` |
| No spaces | `file-name.md` | ~~`file name.md`~~ |

**Standard Names:**
- `concepts.md` - Domain terminology and concepts
- `best-practices.md` - Do/don't guidelines
- `workflow.md` - Detailed step instructions
- `templates.md` - Output templates

### Script Files

| Language | Pattern | Example |
|----------|---------|---------|
| Bash | `{verb}-{noun}.sh` | `validate-skill.sh` |
| Python | `{verb}_{noun}.py` | `count_tokens.py` |

**Standard Names:**
- `generate.sh` / `generate.py` - Main generation script
- `validate.sh` - Validation script
- `install.sh` - Installation script

### Template Files

| Pattern | Example |
|---------|---------|
| `{type}.template` | `component.template` |
| `{type}.{ext}.template` | `config.yaml.template` |

## Directory Names

| Directory | Purpose | Naming |
|-----------|---------|--------|
| `references/` | Supporting documentation | Fixed name |
| `scripts/` | Executable scripts | Fixed name |
| `templates/` | Output templates | Fixed name |
| Subdirectories | Organization | hyphen-case |

## Validation

```python
import re

def validate_skill_name(name: str) -> bool:
    """Validate skill name follows conventions."""
    pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
    return (
        bool(re.match(pattern, name)) and
        len(name) >= 2 and
        len(name) <= 64 and
        '--' not in name
    )

def validate_file_name(name: str, file_type: str) -> bool:
    """Validate file name follows conventions."""
    if file_type == 'reference':
        pattern = r'^[a-z][a-z0-9-]*\.md$'
    elif file_type == 'script_bash':
        pattern = r'^[a-z][a-z0-9-]*\.sh$'
    elif file_type == 'script_python':
        pattern = r'^[a-z][a-z0-9_]*\.py$'
    else:
        return True

    return bool(re.match(pattern, name))
```

## Examples

### Valid Names

```
skill-name/
├── SKILL.md                    # Fixed, uppercase
├── references/
│   ├── concepts.md             # hyphen-case
│   ├── best-practices.md       # hyphen-case
│   └── api-reference.md        # hyphen-case
├── scripts/
│   ├── generate.sh             # hyphen-case
│   └── validate-output.sh      # hyphen-case
└── templates/
    └── component.template      # hyphen-case
```

### Invalid Names

```
# DON'T:
MySkill/                 # PascalCase
my_skill/                # snake_case
References/              # Capitalized directory
best practices.md        # Spaces
BestPractices.md         # PascalCase
generate-script.SH       # Wrong extension case
```
