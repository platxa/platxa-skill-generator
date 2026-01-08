# Script Output Formatting

Standard output formats for human and machine consumption.

## Output Modes

| Flag | Output | Use Case |
|------|--------|----------|
| (default) | Human-readable text | Interactive use |
| `--json` | JSON | Piping, scripting |
| `--quiet` | Minimal/none | CI/CD, batch |
| `--verbose` | Detailed text | Debugging |

## Human-Readable Format

### Success Output

```
══════════════════════════════════════════════════════════════════════
  ✓ SKILL VALIDATED SUCCESSFULLY
══════════════════════════════════════════════════════════════════════

  Skill Name:    api-doc-generator
  Files:         6 files checked
  Token Count:   4,918 tokens

  Quality Score: 8.2/10.0 ████████░░

──────────────────────────────────────────────────────────────────────
  RESULTS
──────────────────────────────────────────────────────────────────────

  ✓ Structure     Valid directory layout
  ✓ Frontmatter   All required fields present
  ✓ Tokens        Within budget (4,918 < 10,000)
  ✓ Content       Quality score passed

══════════════════════════════════════════════════════════════════════
```

### Error Output

```
══════════════════════════════════════════════════════════════════════
  ✗ VALIDATION FAILED
══════════════════════════════════════════════════════════════════════

  Skill Name:    broken-skill

──────────────────────────────────────────────────────────────────────
  ERRORS (2)
──────────────────────────────────────────────────────────────────────

  1. [Structure] Missing SKILL.md file
     Expected: SKILL.md in skill root directory

  2. [Frontmatter] Invalid name format
     Found: "Broken Skill"
     Expected: hyphen-case (e.g., "broken-skill")

══════════════════════════════════════════════════════════════════════
```

## JSON Format

### Success JSON

```json
{
  "status": "success",
  "skill_name": "api-doc-generator",
  "summary": {
    "files_checked": 6,
    "token_count": 4918,
    "quality_score": 8.2
  },
  "results": {
    "structure": {"passed": true, "message": "Valid directory layout"},
    "frontmatter": {"passed": true, "message": "All required fields present"},
    "tokens": {"passed": true, "message": "Within budget (4918 < 10000)"},
    "content": {"passed": true, "message": "Quality score passed"}
  },
  "errors": [],
  "warnings": []
}
```

### Error JSON

```json
{
  "status": "error",
  "skill_name": "broken-skill",
  "summary": {
    "files_checked": 0,
    "errors_count": 2,
    "warnings_count": 0
  },
  "results": {
    "structure": {"passed": false, "message": "Missing SKILL.md file"},
    "frontmatter": {"passed": false, "message": "Invalid name format"}
  },
  "errors": [
    {
      "code": "MISSING_FILE",
      "category": "structure",
      "message": "Missing SKILL.md file",
      "details": "Expected: SKILL.md in skill root directory"
    },
    {
      "code": "INVALID_NAME",
      "category": "frontmatter",
      "message": "Invalid name format",
      "details": "Found: \"Broken Skill\", Expected: hyphen-case"
    }
  ],
  "warnings": []
}
```

## Bash Implementation

```bash
#!/bin/bash
# Output formatting utilities

# Output mode
JSON_OUTPUT=false

# Parse --json flag
parse_output_args() {
    for arg in "$@"; do
        case $arg in
            --json)
                JSON_OUTPUT=true
                ;;
        esac
    done
}

# Accumulate results
declare -A RESULTS
ERRORS=()
WARNINGS=()

add_result() {
    local category="$1"
    local passed="$2"
    local message="$3"
    RESULTS["$category"]="$passed|$message"
}

add_error() {
    local code="$1"
    local category="$2"
    local message="$3"
    local details="$4"
    ERRORS+=("$code|$category|$message|$details")
}

add_warning() {
    local message="$1"
    WARNINGS+=("$message")
}

# Output functions
output_human() {
    local status="$1"
    local skill_name="$2"

    echo "══════════════════════════════════════════════════════════════════════"
    if [[ "$status" == "success" ]]; then
        echo "  ✓ VALIDATION PASSED"
    else
        echo "  ✗ VALIDATION FAILED"
    fi
    echo "══════════════════════════════════════════════════════════════════════"
    echo ""
    echo "  Skill Name: $skill_name"
    echo ""

    # Results
    echo "──────────────────────────────────────────────────────────────────────"
    echo "  RESULTS"
    echo "──────────────────────────────────────────────────────────────────────"
    for key in "${!RESULTS[@]}"; do
        IFS='|' read -r passed message <<< "${RESULTS[$key]}"
        if [[ "$passed" == "true" ]]; then
            echo "  ✓ $key: $message"
        else
            echo "  ✗ $key: $message"
        fi
    done

    # Errors
    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        echo ""
        echo "──────────────────────────────────────────────────────────────────────"
        echo "  ERRORS (${#ERRORS[@]})"
        echo "──────────────────────────────────────────────────────────────────────"
        local i=1
        for error in "${ERRORS[@]}"; do
            IFS='|' read -r code category message details <<< "$error"
            echo "  $i. [$category] $message"
            echo "     $details"
            ((i++))
        done
    fi

    echo "══════════════════════════════════════════════════════════════════════"
}

output_json() {
    local status="$1"
    local skill_name="$2"

    # Build JSON manually (no jq dependency)
    echo "{"
    echo "  \"status\": \"$status\","
    echo "  \"skill_name\": \"$skill_name\","

    # Results
    echo "  \"results\": {"
    local first=true
    for key in "${!RESULTS[@]}"; do
        IFS='|' read -r passed message <<< "${RESULTS[$key]}"
        $first || echo ","
        first=false
        echo -n "    \"$key\": {\"passed\": $passed, \"message\": \"$message\"}"
    done
    echo ""
    echo "  },"

    # Errors
    echo "  \"errors\": ["
    local first=true
    for error in "${ERRORS[@]}"; do
        IFS='|' read -r code category message details <<< "$error"
        $first || echo ","
        first=false
        echo -n "    {\"code\": \"$code\", \"category\": \"$category\", \"message\": \"$message\"}"
    done
    echo ""
    echo "  ]"

    echo "}"
}

output_results() {
    local status="$1"
    local skill_name="$2"

    if $JSON_OUTPUT; then
        output_json "$status" "$skill_name"
    else
        output_human "$status" "$skill_name"
    fi
}
```

## Python Implementation

```python
#!/usr/bin/env python3
"""Output formatting utilities."""

import json
import sys
from dataclasses import dataclass, asdict
from typing import Literal

@dataclass
class Result:
    passed: bool
    message: str

@dataclass
class Error:
    code: str
    category: str
    message: str
    details: str = ""

@dataclass
class OutputData:
    status: Literal["success", "error"]
    skill_name: str
    results: dict[str, Result]
    errors: list[Error]
    warnings: list[str]


class OutputFormatter:
    """Format output for human or machine consumption."""

    def __init__(self, json_mode: bool = False, quiet: bool = False):
        self.json_mode = json_mode
        self.quiet = quiet
        self.results: dict[str, Result] = {}
        self.errors: list[Error] = []
        self.warnings: list[str] = []

    def add_result(self, category: str, passed: bool, message: str) -> None:
        self.results[category] = Result(passed=passed, message=message)

    def add_error(
        self,
        code: str,
        category: str,
        message: str,
        details: str = ""
    ) -> None:
        self.errors.append(Error(
            code=code,
            category=category,
            message=message,
            details=details
        ))

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def output(self, skill_name: str) -> None:
        """Output formatted results."""
        status = "success" if not self.errors else "error"

        if self.json_mode:
            self._output_json(status, skill_name)
        elif not self.quiet:
            self._output_human(status, skill_name)

    def _output_json(self, status: str, skill_name: str) -> None:
        """Output JSON format."""
        data = {
            "status": status,
            "skill_name": skill_name,
            "results": {k: asdict(v) for k, v in self.results.items()},
            "errors": [asdict(e) for e in self.errors],
            "warnings": self.warnings
        }
        print(json.dumps(data, indent=2))

    def _output_human(self, status: str, skill_name: str) -> None:
        """Output human-readable format."""
        separator = "═" * 70

        print(separator)
        if status == "success":
            print("  ✓ VALIDATION PASSED")
        else:
            print("  ✗ VALIDATION FAILED")
        print(separator)
        print(f"\n  Skill Name: {skill_name}\n")

        # Results
        print("─" * 70)
        print("  RESULTS")
        print("─" * 70)
        for category, result in self.results.items():
            icon = "✓" if result.passed else "✗"
            print(f"  {icon} {category}: {result.message}")

        # Errors
        if self.errors:
            print(f"\n{'─' * 70}")
            print(f"  ERRORS ({len(self.errors)})")
            print("─" * 70)
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. [{error.category}] {error.message}")
                if error.details:
                    print(f"     {error.details}")

        # Warnings
        if self.warnings:
            print(f"\n{'─' * 70}")
            print(f"  WARNINGS ({len(self.warnings)})")
            print("─" * 70)
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        print(separator)


# Usage
def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    formatter = OutputFormatter(json_mode=args.json, quiet=args.quiet)

    # Add results
    formatter.add_result("structure", True, "Valid layout")
    formatter.add_result("frontmatter", False, "Invalid name")

    # Add error
    formatter.add_error(
        code="INVALID_NAME",
        category="frontmatter",
        message="Invalid name format",
        details="Expected hyphen-case"
    )

    formatter.output("test-skill")


if __name__ == "__main__":
    main()
```

## Visual Elements

### Progress Bars

```python
def progress_bar(current: int, total: int, width: int = 40) -> str:
    """Generate ASCII progress bar."""
    filled = int(width * current / total)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    percent = current / total * 100
    return f"[{bar}] {percent:.0f}%"

# Output: [████████░░░░░░░░░░░░] 40%
```

### Score Visualization

```python
def score_bar(score: float, max_score: float = 10.0) -> str:
    """Generate score visualization."""
    filled = int(score)
    empty = int(max_score) - filled
    return f"{score:.1f}/{max_score:.0f} {'█' * filled}{'░' * empty}"

# Output: 8.2/10 ████████░░
```

### Status Icons

```python
ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "pending": "○",
    "running": "▶",
}
```
