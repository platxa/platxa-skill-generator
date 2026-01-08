# Template Variable Substitution

Replace template placeholders with actual values during skill generation.

## Variable Syntax

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{variable}}` | Simple substitution | `{{name}}` → `my-skill` |
| `{{variable\|filter}}` | With filter | `{{name\|title}}` → `My Skill` |
| `{{variable:default}}` | With default | `{{author:anonymous}}` |
| `{{{variable}}}` | Unescaped HTML | Raw content |

## Variable Model

```python
from dataclasses import dataclass
from enum import Enum
import re

class VariableFilter(Enum):
    NONE = "none"
    TITLE = "title"       # Title Case
    UPPER = "upper"       # UPPERCASE
    LOWER = "lower"       # lowercase
    KEBAB = "kebab"       # kebab-case
    SNAKE = "snake"       # snake_case
    CAMEL = "camel"       # camelCase
    PASCAL = "pascal"     # PascalCase

@dataclass
class TemplateVariable:
    name: str
    filter: VariableFilter
    default: str | None
    required: bool

@dataclass
class SubstitutionResult:
    content: str
    variables_replaced: int
    missing_variables: list[str]
    warnings: list[str]
```

## Variable Registry

```python
# Standard variables available in all templates
STANDARD_VARIABLES = {
    # Required
    "name": {
        "description": "Skill name in kebab-case",
        "required": True,
        "example": "api-doc-generator"
    },
    "description": {
        "description": "One-line skill description",
        "required": True,
        "example": "Generate API documentation from source code"
    },

    # Optional with defaults
    "version": {
        "description": "Skill version",
        "required": False,
        "default": "1.0.0"
    },
    "author": {
        "description": "Skill author name",
        "required": False,
        "default": "Anonymous"
    },

    # Derived (auto-generated)
    "skill-title": {
        "description": "Title case skill name",
        "derived_from": "name",
        "filter": "title"
    },
    "skill-command": {
        "description": "Slash command name",
        "derived_from": "name",
        "filter": "none"
    },
    "timestamp": {
        "description": "Generation timestamp",
        "derived": True
    },
    "year": {
        "description": "Current year",
        "derived": True
    }
}
```

## Template Substituter

```python
import re
from datetime import datetime

class TemplateSubstituter:
    """Replace template variables with values."""

    VARIABLE_PATTERN = re.compile(
        r'\{\{([a-zA-Z_][a-zA-Z0-9_-]*)(?:\|([a-z]+))?(?::([^}]*))?\}\}'
    )

    def __init__(self, variables: dict[str, str]):
        self.variables = variables
        self.missing: list[str] = []
        self.warnings: list[str] = []

    def substitute(self, template: str) -> SubstitutionResult:
        """Substitute all variables in template."""
        self.missing = []
        self.warnings = []
        replaced_count = 0

        def replace_match(match: re.Match) -> str:
            nonlocal replaced_count
            var_name = match.group(1)
            filter_name = match.group(2)
            default = match.group(3)

            value = self._get_value(var_name, default)

            if value is None:
                self.missing.append(var_name)
                return match.group(0)  # Keep original

            if filter_name:
                value = self._apply_filter(value, filter_name)

            replaced_count += 1
            return value

        result = self.VARIABLE_PATTERN.sub(replace_match, template)

        return SubstitutionResult(
            content=result,
            variables_replaced=replaced_count,
            missing_variables=self.missing,
            warnings=self.warnings
        )

    def _get_value(self, name: str, default: str | None) -> str | None:
        """Get variable value."""
        # Check explicit variables
        if name in self.variables:
            return self.variables[name]

        # Check derived variables
        derived = self._get_derived(name)
        if derived is not None:
            return derived

        # Use default
        if default is not None:
            return default

        # Check standard defaults
        if name in STANDARD_VARIABLES:
            std = STANDARD_VARIABLES[name]
            if "default" in std:
                return std["default"]

        return None

    def _get_derived(self, name: str) -> str | None:
        """Get derived variable value."""
        if name == "timestamp":
            return datetime.now().isoformat()
        elif name == "year":
            return str(datetime.now().year)
        elif name == "skill-title" and "name" in self.variables:
            return self._apply_filter(self.variables["name"], "title")
        elif name == "skill-command" and "name" in self.variables:
            return self.variables["name"]
        return None

    def _apply_filter(self, value: str, filter_name: str) -> str:
        """Apply filter to value."""
        filters = {
            "title": self._to_title,
            "upper": str.upper,
            "lower": str.lower,
            "kebab": self._to_kebab,
            "snake": self._to_snake,
            "camel": self._to_camel,
            "pascal": self._to_pascal,
        }

        filter_func = filters.get(filter_name)
        if filter_func:
            return filter_func(value)

        self.warnings.append(f"Unknown filter: {filter_name}")
        return value

    def _to_title(self, s: str) -> str:
        """Convert to Title Case."""
        return " ".join(word.capitalize() for word in s.replace("-", " ").replace("_", " ").split())

    def _to_kebab(self, s: str) -> str:
        """Convert to kebab-case."""
        s = re.sub(r'([A-Z])', r'-\1', s)
        s = re.sub(r'[_\s]+', '-', s)
        return s.lower().strip('-')

    def _to_snake(self, s: str) -> str:
        """Convert to snake_case."""
        s = re.sub(r'([A-Z])', r'_\1', s)
        s = re.sub(r'[-\s]+', '_', s)
        return s.lower().strip('_')

    def _to_camel(self, s: str) -> str:
        """Convert to camelCase."""
        parts = re.split(r'[-_\s]+', s)
        return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

    def _to_pascal(self, s: str) -> str:
        """Convert to PascalCase."""
        parts = re.split(r'[-_\s]+', s)
        return ''.join(p.capitalize() for p in parts)
```

## Variable Extractor

```python
class VariableExtractor:
    """Extract variables from template."""

    VARIABLE_PATTERN = re.compile(
        r'\{\{([a-zA-Z_][a-zA-Z0-9_-]*)(?:\|[a-z]+)?(?::[^}]*)?\}\}'
    )

    def extract(self, template: str) -> list[TemplateVariable]:
        """Extract all variables from template."""
        variables = {}

        for match in self.VARIABLE_PATTERN.finditer(template):
            full_match = match.group(0)
            var_name = match.group(1)

            if var_name in variables:
                continue

            # Parse filter and default
            filter_match = re.search(r'\|([a-z]+)', full_match)
            default_match = re.search(r':([^}]*)\}\}', full_match)

            filter_type = VariableFilter.NONE
            if filter_match:
                try:
                    filter_type = VariableFilter(filter_match.group(1))
                except ValueError:
                    filter_type = VariableFilter.NONE

            default = default_match.group(1) if default_match else None
            required = var_name in STANDARD_VARIABLES and STANDARD_VARIABLES[var_name].get("required", False)

            variables[var_name] = TemplateVariable(
                name=var_name,
                filter=filter_type,
                default=default,
                required=required
            )

        return list(variables.values())

    def get_required_variables(self, template: str) -> list[str]:
        """Get list of required variable names."""
        all_vars = self.extract(template)
        return [v.name for v in all_vars if v.required and v.default is None]
```

## Validation

```python
class VariableValidator:
    """Validate variable values."""

    def validate(self, variables: dict[str, str]) -> list[str]:
        """Validate variable values."""
        errors = []

        # Check name format
        if "name" in variables:
            name = variables["name"]
            if not re.match(r'^[a-z][a-z0-9-]*$', name):
                errors.append(f"Invalid name format: {name} (must be kebab-case)")
            if len(name) > 64:
                errors.append(f"Name too long: {len(name)} > 64 chars")

        # Check description
        if "description" in variables:
            desc = variables["description"]
            if len(desc) < 10:
                errors.append("Description too short (min 10 chars)")
            if len(desc) > 200:
                errors.append("Description too long (max 200 chars)")

        # Check version format
        if "version" in variables:
            version = variables["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append(f"Invalid version format: {version}")

        return errors
```

## Integration

```python
def substitute_template(
    template: str,
    variables: dict[str, str]
) -> tuple[str, list[str]]:
    """Substitute variables in template."""
    # Validate variables
    validator = VariableValidator()
    errors = validator.validate(variables)

    if errors:
        return template, errors

    # Extract required variables
    extractor = VariableExtractor()
    required = extractor.get_required_variables(template)

    missing = [v for v in required if v not in variables]
    if missing:
        return template, [f"Missing required variable: {v}" for v in missing]

    # Perform substitution
    substituter = TemplateSubstituter(variables)
    result = substituter.substitute(template)

    if result.missing_variables:
        return result.content, [f"Unresolved variable: {v}" for v in result.missing_variables]

    return result.content, []
```

## Example Usage

```python
template = """---
name: {{name}}
description: {{description}}
version: {{version:1.0.0}}
author: {{author:Anonymous}}
---

# {{name|title}}

{{description}}

## Usage

To use this skill, type:

    /{{skill-command}}

Generated on {{timestamp}}
"""

variables = {
    "name": "api-doc-generator",
    "description": "Generate API documentation from source code"
}

result, errors = substitute_template(template, variables)
# Result:
# ---
# name: api-doc-generator
# description: Generate API documentation from source code
# version: 1.0.0
# author: Anonymous
# ---
#
# # Api Doc Generator
#
# Generate API documentation from source code
#
# ## Usage
#
# To use this skill, type:
#
#     /api-doc-generator
#
# Generated on 2024-01-15T14:30:22
```
