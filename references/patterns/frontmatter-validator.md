# Frontmatter Validator

Parse and validate SKILL.md YAML frontmatter against Agent Skills Spec v1.0.

## Purpose

Ensure frontmatter is syntactically correct YAML and meets all spec field constraints before the skill can be installed.

## Frontmatter Schema

```yaml
# Required fields
name: string          # ≤64 chars, hyphen-case
description: string   # ≤1024 chars, non-empty

# Optional fields
tools: list[string]   # Valid tool names
subagent_type: string # Valid subagent type
model: string         # opus | sonnet | haiku
run_in_background: boolean
```

## Parsing Algorithm

```python
import re
import yaml
from dataclasses import dataclass
from typing import Any

@dataclass
class FrontmatterResult:
    valid: bool
    data: dict[str, Any]
    errors: list[str]
    warnings: list[str]
    raw_yaml: str

def parse_frontmatter(content: str) -> FrontmatterResult:
    """
    Parse YAML frontmatter from SKILL.md content.

    Expected format:
    ---
    name: skill-name
    description: |
      Multi-line description
    ---
    # Content...
    """
    errors = []
    warnings = []

    # Check starts with ---
    if not content.startswith('---'):
        return FrontmatterResult(
            valid=False,
            data={},
            errors=["Content must start with --- (frontmatter delimiter)"],
            warnings=[],
            raw_yaml=""
        )

    # Find closing ---
    parts = content.split('---', 2)
    if len(parts) < 3:
        return FrontmatterResult(
            valid=False,
            data={},
            errors=["Frontmatter not properly closed (missing second ---)"],
            warnings=[],
            raw_yaml=""
        )

    raw_yaml = parts[1].strip()

    # Check not empty
    if not raw_yaml:
        return FrontmatterResult(
            valid=False,
            data={},
            errors=["Frontmatter is empty"],
            warnings=[],
            raw_yaml=""
        )

    # Parse YAML
    try:
        data = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as e:
        return FrontmatterResult(
            valid=False,
            data={},
            errors=[f"Invalid YAML syntax: {e}"],
            warnings=[],
            raw_yaml=raw_yaml
        )

    # Check is dict
    if not isinstance(data, dict):
        return FrontmatterResult(
            valid=False,
            data={},
            errors=["Frontmatter must be a YAML mapping (key: value pairs)"],
            warnings=[],
            raw_yaml=raw_yaml
        )

    return FrontmatterResult(
        valid=True,
        data=data,
        errors=[],
        warnings=[],
        raw_yaml=raw_yaml
    )
```

## Field Validators

### Name Validator

```python
NAME_PATTERN = re.compile(r'^[a-z][a-z0-9-]*[a-z0-9]$')
NAME_MAX_LENGTH = 64

def validate_name(name: Any) -> list[str]:
    """Validate skill name field."""
    errors = []

    # Type check
    if not isinstance(name, str):
        return [f"name must be a string, got {type(name).__name__}"]

    # Length check
    if len(name) > NAME_MAX_LENGTH:
        errors.append(f"name too long: {len(name)} chars (max {NAME_MAX_LENGTH})")

    if len(name) < 2:
        errors.append("name must be at least 2 characters")

    # Format check
    if not NAME_PATTERN.match(name):
        errors.append(
            "name must be hyphen-case: "
            "lowercase letters/numbers, hyphens in middle only"
        )

    # Double hyphen check
    if '--' in name:
        errors.append("name cannot contain consecutive hyphens")

    # Reserved names
    RESERVED = {'skill', 'claude', 'anthropic', 'test', 'example'}
    if name.lower() in RESERVED:
        errors.append(f"name '{name}' is reserved")

    return errors
```

### Description Validator

```python
DESC_MAX_LENGTH = 1024

def validate_description(desc: Any) -> list[str]:
    """Validate skill description field."""
    errors = []

    # Type check
    if not isinstance(desc, str):
        return [f"description must be a string, got {type(desc).__name__}"]

    # Strip and check
    desc = desc.strip()

    # Empty check
    if not desc:
        return ["description cannot be empty"]

    # Length check
    if len(desc) > DESC_MAX_LENGTH:
        errors.append(
            f"description too long: {len(desc)} chars (max {DESC_MAX_LENGTH})"
        )

    # Quality checks
    if desc.endswith('...'):
        errors.append("description appears incomplete (ends with ...)")

    # Placeholder detection
    PLACEHOLDERS = [
        'TODO', 'TBD', 'FIXME', 'XXX',
        '[add', '[insert', '[description',
        'placeholder', 'lorem ipsum'
    ]
    desc_lower = desc.lower()
    for p in PLACEHOLDERS:
        if p.lower() in desc_lower:
            errors.append(f"description contains placeholder text: '{p}'")
            break

    # Minimum quality
    if len(desc) < 20:
        errors.append("description too short (min 20 chars recommended)")

    return errors
```

### Tools Validator

```python
VALID_TOOLS = {
    # File operations
    'Read', 'Write', 'Edit', 'MultiEdit', 'NotebookEdit',
    # Search & navigation
    'Glob', 'Grep', 'LS',
    # Execution
    'Bash', 'Task',
    # Web
    'WebFetch', 'WebSearch',
    # User interaction
    'AskUserQuestion',
    # Planning & management
    'TodoWrite', 'KillShell', 'BashOutput',
}

def validate_tools(tools: Any) -> list[str]:
    """Validate tools field."""
    errors = []

    # Type check
    if not isinstance(tools, list):
        return [f"tools must be a list, got {type(tools).__name__}"]

    # Empty is valid (tools are optional)
    if not tools:
        return []

    # Validate each tool
    invalid = []
    for tool in tools:
        if not isinstance(tool, str):
            errors.append(f"tool must be string, got {type(tool).__name__}")
        elif tool not in VALID_TOOLS:
            invalid.append(tool)

    if invalid:
        errors.append(f"invalid tools: {', '.join(invalid)}")
        errors.append(f"valid tools: {', '.join(sorted(VALID_TOOLS))}")

    # Duplicates
    if len(tools) != len(set(tools)):
        seen = set()
        dupes = [t for t in tools if t in seen or seen.add(t)]
        errors.append(f"duplicate tools: {', '.join(dupes)}")

    return errors
```

### Model Validator

```python
VALID_MODELS = {'opus', 'sonnet', 'haiku'}

def validate_model(model: Any) -> list[str]:
    """Validate model field."""
    if not isinstance(model, str):
        return [f"model must be a string, got {type(model).__name__}"]

    if model not in VALID_MODELS:
        return [f"invalid model '{model}', must be one of: {', '.join(VALID_MODELS)}"]

    return []
```

### Subagent Type Validator

```python
VALID_SUBAGENT_TYPES = {
    'general-purpose', 'Explore', 'Plan',
    'code-reviewer', 'security-gate', 'quality-gate'
}

def validate_subagent_type(subagent_type: Any) -> list[str]:
    """Validate subagent_type field."""
    if not isinstance(subagent_type, str):
        return [f"subagent_type must be a string, got {type(subagent_type).__name__}"]

    if subagent_type not in VALID_SUBAGENT_TYPES:
        return [
            f"unknown subagent_type '{subagent_type}'",
            f"known types: {', '.join(sorted(VALID_SUBAGENT_TYPES))}"
        ]

    return []
```

## Complete Validation

```python
def validate_frontmatter(content: str) -> FrontmatterValidation:
    """
    Complete frontmatter validation.

    Returns validation result with all field errors and warnings.
    """
    # Parse
    parsed = parse_frontmatter(content)
    if not parsed.valid:
        return FrontmatterValidation(
            valid=False,
            errors=parsed.errors,
            warnings=[],
            data={}
        )

    data = parsed.data
    errors = []
    warnings = []

    # Required: name
    if 'name' not in data:
        errors.append("missing required field: name")
    else:
        errors.extend(validate_name(data['name']))

    # Required: description
    if 'description' not in data:
        errors.append("missing required field: description")
    else:
        errors.extend(validate_description(data['description']))

    # Optional: tools
    if 'tools' in data:
        errors.extend(validate_tools(data['tools']))

    # Optional: model
    if 'model' in data:
        errors.extend(validate_model(data['model']))

    # Optional: subagent_type
    if 'subagent_type' in data:
        errors.extend(validate_subagent_type(data['subagent_type']))

    # Optional: run_in_background
    if 'run_in_background' in data:
        if not isinstance(data['run_in_background'], bool):
            errors.append("run_in_background must be boolean")

    # Unknown fields warning
    # Core fields + metadata fields (version, author, tags)
    KNOWN_FIELDS = {'name', 'description', 'tools', 'model', 'subagent_type', 'run_in_background', 'version', 'author', 'tags'}
    unknown = set(data.keys()) - KNOWN_FIELDS
    if unknown:
        warnings.append(f"unknown fields will be ignored: {', '.join(unknown)}")

    return FrontmatterValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        data=data
    )
```

## Output Format

```json
{
  "frontmatter_validation": {
    "valid": true,
    "errors": [],
    "warnings": ["unknown fields will be ignored: custom_field"],
    "data": {
      "name": "api-doc-generator",
      "description": "Generate API documentation from OpenAPI specs.",
      "tools": ["Read", "Write", "Glob", "Grep"],
      "model": "sonnet"
    }
  }
}
```

## Integration

```python
# Called during validation phase
result = validate_frontmatter(skill_md_content)

if not result.valid:
    return ValidationResult(
        passed=False,
        phase="frontmatter",
        errors=result.errors
    )

# Use validated data for further checks
skill_name = result.data['name']
```
