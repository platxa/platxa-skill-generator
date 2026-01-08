# Allowed-Tools List Generator

Generate minimal tool list for skill frontmatter based on requirements.

## Available Tools

```python
VALID_TOOLS = {
    # File operations
    "Read": "Read file contents",
    "Write": "Create or overwrite files",
    "Edit": "Edit existing files",
    "MultiEdit": "Multiple edits in one operation",
    "NotebookEdit": "Edit Jupyter notebooks",

    # Search & navigation
    "Glob": "Find files by pattern",
    "Grep": "Search file contents",
    "LS": "List directory contents",

    # Execution
    "Bash": "Execute shell commands",
    "Task": "Launch subagent tasks",

    # Web
    "WebFetch": "Fetch web content",
    "WebSearch": "Search the web",

    # User interaction
    "AskUserQuestion": "Ask user questions",

    # Planning & management
    "TodoWrite": "Manage todo lists",
    "KillShell": "Kill background processes",
    "BashOutput": "Get background process output",
}
```

## Tool Selection by Skill Type

```python
SKILL_TYPE_BASE_TOOLS = {
    "builder": ["Read", "Write", "Glob"],
    "guide": ["Read", "Glob", "Grep"],
    "automation": ["Read", "Write", "Bash", "Glob"],
    "analyzer": ["Read", "Glob", "Grep", "Bash"],
    "validator": ["Read", "Glob", "Grep", "Bash"],
}
```

## Requirement-Based Tool Detection

```python
REQUIREMENT_TOOL_MAPPING = {
    # File operations
    "read file": ["Read"],
    "read files": ["Read", "Glob"],
    "write file": ["Write"],
    "create file": ["Write"],
    "edit file": ["Edit"],
    "modify file": ["Edit"],
    "update file": ["Edit"],

    # Search operations
    "search": ["Grep", "Glob"],
    "find file": ["Glob"],
    "find files": ["Glob"],
    "search content": ["Grep"],
    "pattern match": ["Grep"],

    # Execution
    "run command": ["Bash"],
    "execute": ["Bash"],
    "shell": ["Bash"],
    "script": ["Bash"],
    "compile": ["Bash"],
    "build": ["Bash"],
    "test": ["Bash"],

    # Web operations
    "fetch url": ["WebFetch"],
    "download": ["WebFetch"],
    "api call": ["WebFetch"],
    "web search": ["WebSearch"],
    "search web": ["WebSearch"],

    # User interaction
    "ask user": ["AskUserQuestion"],
    "user input": ["AskUserQuestion"],
    "prompt user": ["AskUserQuestion"],
    "clarify": ["AskUserQuestion"],

    # Task management
    "subtask": ["Task"],
    "subagent": ["Task"],
    "parallel": ["Task"],
    "delegate": ["Task"],

    # Notebook
    "notebook": ["NotebookEdit"],
    "jupyter": ["NotebookEdit"],
    "ipynb": ["NotebookEdit"],
}

def detect_tools_from_requirements(requirements: list[Requirement]) -> set[str]:
    """Detect needed tools from requirement descriptions."""
    tools = set()

    for req in requirements:
        req_lower = req.description.lower()

        for keyword, tool_list in REQUIREMENT_TOOL_MAPPING.items():
            if keyword in req_lower:
                tools.update(tool_list)

    return tools
```

## Tool List Generator

```python
from dataclasses import dataclass

@dataclass
class ToolListResult:
    tools: list[str]
    reasoning: dict[str, str]  # tool -> reason
    warnings: list[str]

def generate_tool_list(
    skill_type: str,
    requirements: list[Requirement],
    explicit_tools: list[str] | None = None
) -> ToolListResult:
    """Generate minimal tool list for skill."""

    tools = set()
    reasoning = {}
    warnings = []

    # 1. Start with skill type base tools
    base_tools = SKILL_TYPE_BASE_TOOLS.get(skill_type, ["Read", "Glob"])
    for tool in base_tools:
        tools.add(tool)
        reasoning[tool] = f"Base tool for {skill_type} skills"

    # 2. Add tools from requirement analysis
    detected = detect_tools_from_requirements(requirements)
    for tool in detected:
        if tool not in tools:
            tools.add(tool)
            reasoning[tool] = "Detected from requirements"

    # 3. Add explicit tools (user-specified)
    if explicit_tools:
        for tool in explicit_tools:
            if tool in VALID_TOOLS:
                if tool not in tools:
                    tools.add(tool)
                    reasoning[tool] = "Explicitly requested"
            else:
                warnings.append(f"Unknown tool '{tool}' ignored")

    # 4. Add implied dependencies
    tools, reasoning = add_tool_dependencies(tools, reasoning)

    # 5. Remove unnecessary tools
    tools, reasoning, removed = minimize_tool_list(tools, reasoning, requirements)
    for tool in removed:
        warnings.append(f"Removed unused tool: {tool}")

    # 6. Validate final list
    validation_warnings = validate_tool_list(tools, skill_type)
    warnings.extend(validation_warnings)

    return ToolListResult(
        tools=sorted(tools),
        reasoning=reasoning,
        warnings=warnings
    )
```

## Tool Dependencies

```python
TOOL_DEPENDENCIES = {
    # Write often needs Read for context
    "Write": ["Read"],
    # Edit requires Read to see current content
    "Edit": ["Read"],
    # MultiEdit requires Read
    "MultiEdit": ["Read"],
    # Grep works better with Glob for file selection
    "Grep": ["Glob"],
}

def add_tool_dependencies(
    tools: set[str],
    reasoning: dict[str, str]
) -> tuple[set[str], dict[str, str]]:
    """Add dependent tools."""

    added = True
    while added:
        added = False
        for tool in list(tools):
            deps = TOOL_DEPENDENCIES.get(tool, [])
            for dep in deps:
                if dep not in tools:
                    tools.add(dep)
                    reasoning[dep] = f"Dependency of {tool}"
                    added = True

    return tools, reasoning
```

## Tool Minimization

```python
def minimize_tool_list(
    tools: set[str],
    reasoning: dict[str, str],
    requirements: list[Requirement]
) -> tuple[set[str], dict[str, str], list[str]]:
    """Remove tools that aren't actually needed."""

    removed = []
    requirements_text = " ".join(r.description.lower() for r in requirements)

    # Check each tool for actual usage
    optional_tools = {"LS", "KillShell", "BashOutput", "TodoWrite"}

    for tool in list(tools):
        if tool in optional_tools:
            # Check if explicitly needed
            if not is_tool_needed(tool, requirements_text):
                tools.remove(tool)
                del reasoning[tool]
                removed.append(tool)

    return tools, reasoning, removed

def is_tool_needed(tool: str, requirements_text: str) -> bool:
    """Check if tool is actually needed based on requirements."""

    tool_indicators = {
        "LS": ["list directory", "directory contents", "folder contents"],
        "KillShell": ["background", "long-running", "kill process"],
        "BashOutput": ["background", "async", "process output"],
        "TodoWrite": ["track progress", "todo", "task list", "multi-step"],
    }

    indicators = tool_indicators.get(tool, [])
    return any(ind in requirements_text for ind in indicators)
```

## Validation

```python
def validate_tool_list(tools: set[str], skill_type: str) -> list[str]:
    """Validate tool list for potential issues."""
    warnings = []

    # Check for potentially dangerous combinations
    if "Bash" in tools and "Write" not in tools:
        # Bash can write files, but explicit Write is clearer
        pass  # Not a warning, just a note

    # Check for missing common tools
    if skill_type == "builder" and "Write" not in tools:
        warnings.append("Builder skill without Write tool - may limit functionality")

    if skill_type == "analyzer" and "Grep" not in tools:
        warnings.append("Analyzer skill without Grep tool - may limit search capability")

    # Check for excessive tools
    if len(tools) > 8:
        warnings.append(f"Many tools ({len(tools)}) - consider if all are needed")

    # Check for web tools without clear need
    if "WebFetch" in tools or "WebSearch" in tools:
        warnings.append("Web tools included - ensure network access is intended")

    return warnings
```

## Output Format

### YAML Frontmatter

```yaml
---
name: api-doc-generator
description: Generate API documentation from OpenAPI specs
tools:
  - Read
  - Write
  - Glob
  - Grep
---
```

### JSON Report

```json
{
  "tools": ["Glob", "Grep", "Read", "Write"],
  "reasoning": {
    "Read": "Base tool for builder skills",
    "Write": "Base tool for builder skills",
    "Glob": "Base tool for builder skills",
    "Grep": "Detected from requirements"
  },
  "warnings": [],
  "count": 4
}
```

## Integration

```python
def format_tools_for_frontmatter(tools: list[str]) -> str:
    """Format tool list for YAML frontmatter."""
    if not tools:
        return "tools: []"

    lines = ["tools:"]
    for tool in sorted(tools):
        lines.append(f"  - {tool}")

    return "\n".join(lines)

# Usage in generation
tool_result = generate_tool_list(
    skill_type="builder",
    requirements=discovery_findings.requirements,
    explicit_tools=user_specified_tools
)

frontmatter_tools = format_tools_for_frontmatter(tool_result.tools)
```
