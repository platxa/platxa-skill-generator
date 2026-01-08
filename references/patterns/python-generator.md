# Python Script Generator

Generate type-hinted, documented Python scripts that work standalone.

## Requirements

- Type hints on all functions
- Docstrings (Google style)
- Works without installation (standalone)
- Uses only standard library (or minimal deps)

## Script Template

```python
#!/usr/bin/env python3
"""
{script_name} - {brief_description}

Usage:
    python {script_name}.py [OPTIONS] <arguments>

Options:
    -h, --help     Show this help message
    -v, --verbose  Enable verbose output
    -q, --quiet    Suppress non-error output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0=success, 1=error, 2=warning)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        return run(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    # Add script-specific arguments here
    return parser


def run(args: argparse.Namespace) -> int:
    """Run the main logic.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code
    """
    # Implementation here
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Type Hints

### Basic Types

```python
from typing import Optional, List, Dict, Tuple, Union, Any

def process_file(path: str) -> bool:
    """Process a single file."""
    ...

def process_files(paths: List[str]) -> Dict[str, bool]:
    """Process multiple files."""
    ...

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration value."""
    ...
```

### Modern Syntax (Python 3.10+)

```python
# Union with |
def process(data: str | bytes) -> str:
    ...

# Optional shorthand
def get_value(key: str, default: str | None = None) -> str | None:
    ...

# List/dict without typing import
def process_items(items: list[str]) -> dict[str, int]:
    ...
```

### Type Aliases

```python
from typing import TypeAlias

FilePath: TypeAlias = str | Path
Result: TypeAlias = tuple[bool, str]
Config: TypeAlias = dict[str, Any]
```

## Docstrings (Google Style)

```python
def validate_skill(path: Path, strict: bool = False) -> tuple[bool, list[str]]:
    """Validate a skill directory against the specification.

    Checks the skill structure, SKILL.md content, and optional
    scripts for compliance with the Agent Skills Spec v1.0.

    Args:
        path: Path to the skill directory to validate.
        strict: If True, treat warnings as errors.

    Returns:
        A tuple containing:
            - bool: True if validation passed, False otherwise.
            - list[str]: List of error/warning messages.

    Raises:
        FileNotFoundError: If the skill directory doesn't exist.
        PermissionError: If the directory is not readable.

    Example:
        >>> passed, messages = validate_skill(Path("./my-skill"))
        >>> if not passed:
        ...     for msg in messages:
        ...         print(msg)
    """
```

## Script Types

### Validation Script

```python
#!/usr/bin/env python3
"""Validate skill against Agent Skills Specification."""

from pathlib import Path
import re
import sys
from typing import NamedTuple


class ValidationResult(NamedTuple):
    """Result of validation check."""
    passed: bool
    errors: list[str]
    warnings: list[str]


def validate_name(name: str) -> list[str]:
    """Validate skill name format."""
    errors = []
    if len(name) > 64:
        errors.append(f"Name exceeds 64 chars: {len(name)}")
    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name):
        errors.append(f"Name not hyphen-case: {name}")
    return errors


def validate_skill(path: Path) -> ValidationResult:
    """Validate a skill directory."""
    errors: list[str] = []
    warnings: list[str] = []

    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md")
        return ValidationResult(False, errors, warnings)

    # Parse and validate...
    return ValidationResult(len(errors) == 0, errors, warnings)
```

### Installation Script

```python
#!/usr/bin/env python3
"""Install skill to user or project location."""

import shutil
from pathlib import Path
import sys


def install_skill(
    source: Path,
    destination: Path,
    overwrite: bool = False,
) -> bool:
    """Install skill to destination.

    Args:
        source: Source skill directory
        destination: Target installation directory
        overwrite: Whether to overwrite existing

    Returns:
        True if installation succeeded
    """
    if destination.exists() and not overwrite:
        print(f"ERROR: Destination exists: {destination}", file=sys.stderr)
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=overwrite)

    # Make scripts executable
    scripts_dir = destination / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            script.chmod(script.stat().st_mode | 0o111)

    print(f"Installed to: {destination}")
    return True
```

## Generation Algorithm

```markdown
FUNCTION generate_python_script(script_spec):
    content = []

    # Shebang and module docstring
    content.append("#!/usr/bin/env python3")
    content.append(f'"""{script_spec.description}"""')
    content.append("")

    # Future imports (for compatibility)
    content.append("from __future__ import annotations")
    content.append("")

    # Imports
    content.append(generate_imports(script_spec))

    # Type aliases (if any)
    IF script_spec.type_aliases:
        content.append(generate_type_aliases(script_spec))

    # Classes (if any)
    FOR class_def in script_spec.classes:
        content.append(generate_class(class_def))

    # Functions
    FOR func in script_spec.functions:
        content.append(generate_function(func))

    # Main function
    content.append(generate_main(script_spec))

    # Entry point
    content.append('if __name__ == "__main__":')
    content.append('    sys.exit(main())')

    RETURN "\n".join(content)
```

## Standalone Requirements

### No External Dependencies

```python
# Good: Standard library only
import json
import re
import sys
from pathlib import Path

# Avoid: External packages
# import yaml  # Requires pyyaml
# import requests  # Requires requests
```

### Self-Contained Utilities

```python
# Include simple JSON/YAML-like parsing if needed
def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML-like frontmatter from markdown."""
    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter = {}
    for line in content[3:end].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter
```

## Testing

```bash
# Test standalone execution
python scripts/validate.py --help
echo $?  # Should be 0

# Test with pyright
pyright scripts/validate.py

# Test with ruff
ruff check scripts/validate.py
```
