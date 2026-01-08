# Troubleshooting.md Generator

Generate problem-solution documentation for common issues.

## Document Structure

```markdown
# Troubleshooting

Common issues and solutions when using this skill.

## Problem: [Problem Title]

**Symptoms:**
- [Observable symptom 1]
- [Observable symptom 2]

**Cause:**
[Root cause explanation]

**Solution:**
[Step-by-step solution]

**Prevention:**
[How to avoid this issue]

---

## Problem: [Next Problem]
...
```

## Problem Model

```python
from dataclasses import dataclass

@dataclass
class Problem:
    title: str
    symptoms: list[str]
    cause: str
    solution: str
    solution_steps: list[str]
    prevention: str | None
    related_problems: list[str]
    severity: str  # low, medium, high, critical
    category: str  # installation, configuration, runtime, output

@dataclass
class TroubleshootingDocument:
    skill_name: str
    problems: list[Problem]
    categories: list[str]
    quick_fixes: dict[str, str]  # symptom -> quick fix
```

## Problem Categories

### By Skill Type

```python
PROBLEM_TEMPLATES = {
    "builder": [
        Problem(
            title="Output Generation Failed",
            symptoms=[
                "No output file created",
                "Empty output file",
                "Process exits without error"
            ],
            cause="Input file not found or template missing",
            solution="Verify input file exists and template path is correct",
            solution_steps=[
                "Check if input file exists: ls -la <input-file>",
                "Verify template directory: ls templates/",
                "Run with --verbose for detailed output"
            ],
            prevention="Always validate input paths before running",
            related_problems=["Template Not Found"],
            severity="medium",
            category="runtime"
        ),
        Problem(
            title="Template Not Found",
            symptoms=[
                "Error: Template 'X' not found",
                "FileNotFoundError on template load"
            ],
            cause="Template file missing or incorrect path",
            solution="Install templates or specify correct path",
            solution_steps=[
                "List available templates: /{skill} --list-templates",
                "Copy template to expected location",
                "Use --template-dir to specify custom location"
            ],
            prevention="Verify template installation during setup",
            related_problems=["Output Generation Failed"],
            severity="medium",
            category="configuration"
        ),
    ],
    "automation": [
        Problem(
            title="Script Permission Denied",
            symptoms=[
                "Permission denied error",
                "Cannot execute script",
                "Exit code 126"
            ],
            cause="Script file lacks execute permission",
            solution="Add execute permission to script",
            solution_steps=[
                "Check permissions: ls -la scripts/",
                "Add execute: chmod +x scripts/*.sh",
                "Retry the command"
            ],
            prevention="Scripts should include chmod in installation",
            related_problems=[],
            severity="low",
            category="installation"
        ),
        Problem(
            title="Dependency Not Found",
            symptoms=[
                "command not found: <tool>",
                "ModuleNotFoundError",
                "Import error"
            ],
            cause="Required dependency not installed",
            solution="Install missing dependency",
            solution_steps=[
                "Check required dependencies in script header",
                "Install using package manager",
                "Verify installation: command -v <tool>"
            ],
            prevention="Run dependency check before first use",
            related_problems=[],
            severity="high",
            category="installation"
        ),
    ],
    "validator": [
        Problem(
            title="False Positive Validation Error",
            symptoms=[
                "Valid input marked as invalid",
                "Unexpected validation failure",
                "Strict mode too restrictive"
            ],
            cause="Validation rules too strict or edge case",
            solution="Adjust validation settings or report bug",
            solution_steps=[
                "Run with --verbose to see exact rule",
                "Check if input matches documented format",
                "Try --lenient mode if available",
                "Report as issue if truly false positive"
            ],
            prevention="Review validation rules in documentation",
            related_problems=["Validation Timeout"],
            severity="medium",
            category="runtime"
        ),
    ],
    "analyzer": [
        Problem(
            title="Analysis Timeout",
            symptoms=[
                "Process hangs",
                "No output after long wait",
                "Memory usage grows continuously"
            ],
            cause="Input too large or infinite loop in analysis",
            solution="Reduce input size or increase timeout",
            solution_steps=[
                "Cancel current process: Ctrl+C",
                "Split large input into smaller parts",
                "Use --max-size to limit scope",
                "Increase timeout: --timeout 600"
            ],
            prevention="Set appropriate limits for large codebases",
            related_problems=[],
            severity="medium",
            category="runtime"
        ),
    ],
    "guide": [
        Problem(
            title="Content Not Found",
            symptoms=[
                "Topic not covered",
                "No results for search",
                "Empty response"
            ],
            cause="Topic not documented or search terms mismatch",
            solution="Try alternative search terms or request addition",
            solution_steps=[
                "List available topics: /{skill} --topics",
                "Try related keywords",
                "Check table of contents",
                "Submit request for new content"
            ],
            prevention="Review available topics before detailed queries",
            related_problems=[],
            severity="low",
            category="runtime"
        ),
    ],
}
```

## Common Problems (All Skills)

```python
COMMON_PROBLEMS = [
    Problem(
        title="Installation Failed",
        symptoms=[
            "Skill not found after install",
            "Command not recognized",
            "Files missing"
        ],
        cause="Installation incomplete or path not updated",
        solution="Reinstall skill and verify paths",
        solution_steps=[
            "Remove existing installation",
            "Run installation again",
            "Verify files: ls ~/.claude/skills/<name>/",
            "Restart Claude Code CLI"
        ],
        prevention="Follow installation instructions exactly",
        related_problems=[],
        severity="high",
        category="installation"
    ),
    Problem(
        title="Unexpected Output Format",
        symptoms=[
            "Output not in expected format",
            "Parsing errors in downstream tools",
            "Missing sections"
        ],
        cause="Wrong output format selected or version mismatch",
        solution="Specify correct output format explicitly",
        solution_steps=[
            "Check available formats: --help",
            "Use explicit format flag: --format json",
            "Verify version compatibility"
        ],
        prevention="Always specify format explicitly in scripts",
        related_problems=[],
        severity="medium",
        category="output"
    ),
    Problem(
        title="Performance Issues",
        symptoms=[
            "Slow execution",
            "High memory usage",
            "System becomes unresponsive"
        ],
        cause="Large input or inefficient processing",
        solution="Reduce scope or enable streaming",
        solution_steps=[
            "Use --limit to restrict scope",
            "Enable streaming: --stream",
            "Process in batches",
            "Check system resources"
        ],
        prevention="Set resource limits for large inputs",
        related_problems=["Analysis Timeout"],
        severity="medium",
        category="runtime"
    ),
]
```

## Generator Implementation

```python
def generate_troubleshooting_md(
    skill_name: str,
    skill_type: str,
    domain_problems: list[Problem] | None = None
) -> str:
    """Generate troubleshooting.md for a skill."""

    # Collect all problems
    problems = COMMON_PROBLEMS.copy()

    # Add type-specific problems
    type_problems = PROBLEM_TEMPLATES.get(skill_type, [])
    problems.extend(type_problems)

    # Add domain-specific problems
    if domain_problems:
        problems.extend(domain_problems)

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    problems.sort(key=lambda p: severity_order.get(p.severity, 2))

    # Build document
    lines = [
        "# Troubleshooting",
        "",
        f"Common issues and solutions for {skill_name}.",
        "",
        "## Quick Reference",
        "",
        "| Symptom | Quick Fix |",
        "|---------|-----------|",
    ]

    # Quick reference table
    for problem in problems[:5]:  # Top 5 most severe
        symptom = problem.symptoms[0] if problem.symptoms else problem.title
        quick_fix = problem.solution_steps[0] if problem.solution_steps else problem.solution
        lines.append(f"| {symptom} | {quick_fix} |")

    lines.extend(["", "---", ""])

    # Group by category
    categories = {}
    for problem in problems:
        cat = problem.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(problem)

    # Category order
    cat_order = ["installation", "configuration", "runtime", "output"]
    for cat in cat_order:
        if cat not in categories:
            continue

        lines.extend([
            f"## {cat.title()} Issues",
            "",
        ])

        for problem in categories[cat]:
            lines.extend(format_problem(problem))
            lines.extend(["", "---", ""])

        # Remove trailing separator
        if lines[-2] == "---":
            lines = lines[:-2]
        lines.append("")

    return "\n".join(lines)


def format_problem(problem: Problem) -> list[str]:
    """Format a single problem as markdown."""
    lines = [
        f"### {problem.title}",
        "",
    ]

    # Severity badge
    severity_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    icon = severity_icons.get(problem.severity, "⚪")
    lines.append(f"**Severity:** {icon} {problem.severity.title()}")
    lines.append("")

    # Symptoms
    lines.append("**Symptoms:**")
    lines.append("")
    for symptom in problem.symptoms:
        lines.append(f"- {symptom}")
    lines.append("")

    # Cause
    lines.append("**Cause:**")
    lines.append("")
    lines.append(problem.cause)
    lines.append("")

    # Solution
    lines.append("**Solution:**")
    lines.append("")
    if problem.solution_steps:
        for i, step in enumerate(problem.solution_steps, 1):
            lines.append(f"{i}. {step}")
    else:
        lines.append(problem.solution)
    lines.append("")

    # Prevention
    if problem.prevention:
        lines.append("**Prevention:**")
        lines.append("")
        lines.append(problem.prevention)
        lines.append("")

    # Related
    if problem.related_problems:
        lines.append("**See Also:**")
        lines.append("")
        for related in problem.related_problems:
            lines.append(f"- [{related}](#{related.lower().replace(' ', '-')})")

    return lines
```

## Domain Problem Detection

```python
DOMAIN_PROBLEM_INDICATORS = {
    "api": [
        Problem(
            title="API Connection Failed",
            symptoms=[
                "Connection refused",
                "Timeout error",
                "Network unreachable"
            ],
            cause="API server unavailable or network issues",
            solution="Check network and API status",
            solution_steps=[
                "Verify internet connection",
                "Check API status page",
                "Try with --retry 3",
                "Check firewall settings"
            ],
            prevention="Implement retry logic for network calls",
            related_problems=["Authentication Failed"],
            severity="high",
            category="runtime"
        ),
        Problem(
            title="Authentication Failed",
            symptoms=[
                "401 Unauthorized",
                "Invalid API key",
                "Token expired"
            ],
            cause="Missing or invalid credentials",
            solution="Update API credentials",
            solution_steps=[
                "Verify API key is set: echo $API_KEY",
                "Check key format and permissions",
                "Regenerate key if expired",
                "Update configuration file"
            ],
            prevention="Store credentials securely, monitor expiration",
            related_problems=["API Connection Failed"],
            severity="high",
            category="configuration"
        ),
    ],
    "file": [
        Problem(
            title="File Access Denied",
            symptoms=[
                "Permission denied",
                "Cannot read/write file",
                "EACCES error"
            ],
            cause="Insufficient file permissions",
            solution="Check and fix file permissions",
            solution_steps=[
                "Check permissions: ls -la <file>",
                "Fix read: chmod +r <file>",
                "Fix write: chmod +w <file>",
                "Check directory permissions too"
            ],
            prevention="Run with appropriate user permissions",
            related_problems=[],
            severity="medium",
            category="runtime"
        ),
    ],
    "git": [
        Problem(
            title="Git Repository Not Found",
            symptoms=[
                "Not a git repository",
                "fatal: .git not found",
                "git operation failed"
            ],
            cause="Running outside git repository",
            solution="Navigate to repository root",
            solution_steps=[
                "Find repo root: git rev-parse --show-toplevel",
                "Navigate there: cd <repo-root>",
                "Or initialize: git init"
            ],
            prevention="Verify directory before git operations",
            related_problems=[],
            severity="low",
            category="runtime"
        ),
    ],
}

def detect_domain_problems(
    description: str,
    requirements: list[str]
) -> list[Problem]:
    """Detect relevant problems from domain keywords."""
    problems = []
    combined = (description + " " + " ".join(requirements)).lower()

    for keyword, domain_problems in DOMAIN_PROBLEM_INDICATORS.items():
        if keyword in combined:
            problems.extend(domain_problems)

    return problems
```

## Example Output

```markdown
# Troubleshooting

Common issues and solutions for api-doc-generator.

## Quick Reference

| Symptom | Quick Fix |
|---------|-----------|
| 401 Unauthorized | Verify API key is set: echo $API_KEY |
| Connection refused | Verify internet connection |
| No output file created | Check if input file exists: ls -la <input-file> |

---

## Installation Issues

### Installation Failed

**Severity:** 🟠 High

**Symptoms:**

- Skill not found after install
- Command not recognized
- Files missing

**Cause:**

Installation incomplete or path not updated

**Solution:**

1. Remove existing installation
2. Run installation again
3. Verify files: ls ~/.claude/skills/<name>/
4. Restart Claude Code CLI

**Prevention:**

Follow installation instructions exactly

---

## Runtime Issues

### API Connection Failed

**Severity:** 🟠 High

**Symptoms:**

- Connection refused
- Timeout error
- Network unreachable

**Cause:**

API server unavailable or network issues

**Solution:**

1. Verify internet connection
2. Check API status page
3. Try with --retry 3
4. Check firewall settings

**Prevention:**

Implement retry logic for network calls

**See Also:**

- [Authentication Failed](#authentication-failed)
```

## Integration

```python
def plan_troubleshooting(
    skill_name: str,
    skill_type: str,
    requirements: list[str]
) -> list[Problem]:
    """Plan troubleshooting content based on skill requirements."""
    problems = []

    # Always include common problems
    problems.extend(COMMON_PROBLEMS)

    # Add type-specific
    problems.extend(PROBLEM_TEMPLATES.get(skill_type, []))

    # Detect domain-specific
    domain_problems = detect_domain_problems(
        skill_name,
        requirements
    )
    problems.extend(domain_problems)

    # Deduplicate by title
    seen = set()
    unique = []
    for p in problems:
        if p.title not in seen:
            seen.add(p.title)
            unique.append(p)

    return unique
```
