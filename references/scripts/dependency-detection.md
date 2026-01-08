# Script Dependency Detection

Detect and document external tool dependencies in scripts.

## Dependency Header Format

### Bash Scripts

```bash
#!/bin/bash
# script-name.sh - Description
#
# Dependencies:
#   jq        - JSON processor (required)
#   curl      - HTTP client (required)
#   yq        - YAML processor (optional)
#   shellcheck - Script linter (development only)
#
# Install dependencies:
#   Ubuntu/Debian: apt install jq curl
#   macOS: brew install jq curl
```

### Python Scripts

```python
#!/usr/bin/env python3
"""Script description.

Dependencies:
    Python 3.8+
    pyyaml     - YAML parsing (pip install pyyaml)
    requests   - HTTP client (pip install requests)
    tiktoken   - Token counting (pip install tiktoken)

Install:
    pip install pyyaml requests tiktoken
"""
```

## Dependency Categories

| Category | Description | Example |
|----------|-------------|---------|
| Required | Script fails without it | `jq`, `curl` |
| Optional | Enhanced functionality | `yq`, `bat` |
| Development | For testing/linting | `shellcheck`, `pytest` |
| Runtime | Language/interpreter | `python3`, `bash 4+` |

## Bash Dependency Detection

```python
import re
from dataclasses import dataclass

@dataclass
class Dependency:
    name: str
    category: str  # required, optional, development
    description: str
    install_cmd: dict[str, str]  # platform -> command

# Common bash command patterns
BASH_COMMANDS = {
    # Core utilities
    "jq": ("JSON processor", {"apt": "jq", "brew": "jq"}),
    "yq": ("YAML processor", {"apt": "yq", "brew": "yq"}),
    "curl": ("HTTP client", {"apt": "curl", "brew": "curl"}),
    "wget": ("HTTP downloader", {"apt": "wget", "brew": "wget"}),

    # Text processing
    "sed": ("Stream editor", {"builtin": True}),
    "awk": ("Text processor", {"builtin": True}),
    "grep": ("Pattern matcher", {"builtin": True}),

    # Development
    "shellcheck": ("Script linter", {"apt": "shellcheck", "brew": "shellcheck"}),
    "shfmt": ("Script formatter", {"apt": "shfmt", "brew": "shfmt"}),

    # Build tools
    "make": ("Build automation", {"apt": "make", "brew": "make"}),
    "docker": ("Container runtime", {"apt": "docker.io", "brew": "docker"}),

    # Version control
    "git": ("Version control", {"apt": "git", "brew": "git"}),
    "gh": ("GitHub CLI", {"apt": "gh", "brew": "gh"}),
}

def detect_bash_dependencies(content: str) -> list[Dependency]:
    """Detect external command dependencies in bash script."""
    dependencies = []
    found = set()

    # Pattern for command usage
    patterns = [
        r'^(\w+)\s',           # Command at line start
        r'\$\((\w+)\s',        # Command substitution
        r'\|\s*(\w+)\s',       # Piped command
        r'&&\s*(\w+)\s',       # Chained command
        r'command\s+-v\s+(\w+)', # command -v check
        r'which\s+(\w+)',      # which check
        r'type\s+(\w+)',       # type check
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            cmd = match.group(1)
            if cmd in BASH_COMMANDS and cmd not in found:
                found.add(cmd)
                desc, install = BASH_COMMANDS[cmd]
                if not install.get("builtin"):
                    dependencies.append(Dependency(
                        name=cmd,
                        category="required",
                        description=desc,
                        install_cmd=install
                    ))

    return dependencies
```

## Python Dependency Detection

```python
import ast

PYTHON_PACKAGES = {
    # Standard library (no install needed)
    "os": None,
    "sys": None,
    "re": None,
    "json": None,
    "pathlib": None,
    "subprocess": None,
    "argparse": None,

    # Common packages
    "yaml": ("pyyaml", "YAML parsing"),
    "pyyaml": ("pyyaml", "YAML parsing"),
    "requests": ("requests", "HTTP client"),
    "tiktoken": ("tiktoken", "Token counting"),
    "click": ("click", "CLI framework"),
    "rich": ("rich", "Terminal formatting"),
    "pytest": ("pytest", "Testing framework"),
    "pyright": ("pyright", "Type checker"),
}

def detect_python_dependencies(content: str) -> list[Dependency]:
    """Detect package dependencies in Python script."""
    dependencies = []
    found = set()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return dependencies

    for node in ast.walk(tree):
        # import x
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".")[0]
                if module not in found:
                    found.add(module)
                    if module in PYTHON_PACKAGES and PYTHON_PACKAGES[module]:
                        pkg, desc = PYTHON_PACKAGES[module]
                        dependencies.append(Dependency(
                            name=pkg,
                            category="required",
                            description=desc,
                            install_cmd={"pip": pkg}
                        ))

        # from x import y
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split(".")[0]
                if module not in found:
                    found.add(module)
                    if module in PYTHON_PACKAGES and PYTHON_PACKAGES[module]:
                        pkg, desc = PYTHON_PACKAGES[module]
                        dependencies.append(Dependency(
                            name=pkg,
                            category="required",
                            description=desc,
                            install_cmd={"pip": pkg}
                        ))

    return dependencies
```

## Dependency Check Functions

### Bash Check

```bash
# Dependencies:
#   jq        - JSON processor (required)
#   curl      - HTTP client (required)

check_dependencies() {
    local missing=()

    for cmd in jq curl; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required dependencies: ${missing[*]}" >&2
        echo "" >&2
        echo "Install with:" >&2
        echo "  Ubuntu/Debian: sudo apt install ${missing[*]}" >&2
        echo "  macOS: brew install ${missing[*]}" >&2
        exit 1
    fi
}

# Call at script start
check_dependencies
```

### Python Check

```python
def check_dependencies() -> None:
    """Check for required Python packages."""
    missing = []

    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")

    try:
        import requests
    except ImportError:
        missing.append("requests")

    if missing:
        print(f"Error: Missing required packages: {', '.join(missing)}", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)

# Call at module load
check_dependencies()
```

## Header Generator

```python
def generate_dependency_header(
    dependencies: list[Dependency],
    script_type: str
) -> str:
    """Generate dependency documentation header."""

    if not dependencies:
        return ""

    lines = []

    if script_type == "bash":
        lines.append("# Dependencies:")
        for dep in dependencies:
            status = "(required)" if dep.category == "required" else f"({dep.category})"
            lines.append(f"#   {dep.name:<12} - {dep.description} {status}")
        lines.append("#")
        lines.append("# Install dependencies:")

        # Group by platform
        apt_deps = [d.name for d in dependencies if "apt" in d.install_cmd]
        brew_deps = [d.name for d in dependencies if "brew" in d.install_cmd]

        if apt_deps:
            lines.append(f"#   Ubuntu/Debian: apt install {' '.join(apt_deps)}")
        if brew_deps:
            lines.append(f"#   macOS: brew install {' '.join(brew_deps)}")

    elif script_type == "python":
        lines.append("Dependencies:")
        for dep in dependencies:
            lines.append(f"    {dep.name:<12} - {dep.description} (pip install {dep.name})")
        lines.append("")
        pip_deps = [d.name for d in dependencies if "pip" in d.install_cmd]
        if pip_deps:
            lines.append(f"Install:")
            lines.append(f"    pip install {' '.join(pip_deps)}")

    return "\n".join(lines)
```

## Complete Detection Flow

```python
def analyze_script_dependencies(script_path: str) -> DependencyReport:
    """Analyze script and generate dependency report."""

    content = Path(script_path).read_text()

    if script_path.endswith(".sh"):
        deps = detect_bash_dependencies(content)
        script_type = "bash"
    elif script_path.endswith(".py"):
        deps = detect_python_dependencies(content)
        script_type = "python"
    else:
        return DependencyReport(dependencies=[], header="")

    # Generate header
    header = generate_dependency_header(deps, script_type)

    # Generate check function
    check_code = generate_check_function(deps, script_type)

    return DependencyReport(
        dependencies=deps,
        header=header,
        check_function=check_code,
        install_commands=generate_install_commands(deps)
    )
```

## Output Example

```json
{
  "script": "scripts/generate.sh",
  "dependencies": [
    {
      "name": "jq",
      "category": "required",
      "description": "JSON processor",
      "install": {
        "apt": "apt install jq",
        "brew": "brew install jq"
      }
    },
    {
      "name": "curl",
      "category": "required",
      "description": "HTTP client",
      "install": {
        "apt": "apt install curl",
        "brew": "brew install curl"
      }
    }
  ],
  "header": "# Dependencies:\n#   jq           - JSON processor (required)\n#   curl         - HTTP client (required)",
  "check_function": "check_dependencies() { ... }"
}
```
