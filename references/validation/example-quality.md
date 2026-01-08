# Example Quality Validator

Validate that examples are realistic, helpful, and production-ready.

## Quality Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Realism | 25% | Uses realistic, believable data |
| Helpfulness | 25% | Demonstrates useful patterns |
| Completeness | 20% | Shows full workflow, not fragments |
| Correctness | 20% | Syntactically and semantically correct |
| Clarity | 10% | Easy to understand and follow |

## Quality Model

```python
from dataclasses import dataclass
from enum import Enum

class ExampleQuality(Enum):
    EXCELLENT = "excellent"  # 9-10
    GOOD = "good"            # 7-8.9
    ACCEPTABLE = "acceptable" # 5-6.9
    POOR = "poor"            # 3-4.9
    UNACCEPTABLE = "unacceptable"  # 0-2.9

@dataclass
class ExampleScore:
    realism: float       # 0-10
    helpfulness: float   # 0-10
    completeness: float  # 0-10
    correctness: float   # 0-10
    clarity: float       # 0-10
    overall: float       # Weighted average
    quality: ExampleQuality
    issues: list[str]
    suggestions: list[str]

@dataclass
class ExampleValidation:
    example_path: str
    score: ExampleScore
    passed: bool
    blocking_issues: list[str]
```

## Validator Implementation

```python
class ExampleQualityValidator:
    """Validate example quality across all dimensions."""

    WEIGHTS = {
        "realism": 0.25,
        "helpfulness": 0.25,
        "completeness": 0.20,
        "correctness": 0.20,
        "clarity": 0.10,
    }

    PASS_THRESHOLD = 7.0

    def validate(self, example: dict) -> ExampleValidation:
        """Validate a single example."""
        issues = []
        suggestions = []

        # Score each dimension
        realism = self._score_realism(example, issues, suggestions)
        helpfulness = self._score_helpfulness(example, issues, suggestions)
        completeness = self._score_completeness(example, issues, suggestions)
        correctness = self._score_correctness(example, issues, suggestions)
        clarity = self._score_clarity(example, issues, suggestions)

        # Calculate weighted average
        overall = (
            realism * self.WEIGHTS["realism"] +
            helpfulness * self.WEIGHTS["helpfulness"] +
            completeness * self.WEIGHTS["completeness"] +
            correctness * self.WEIGHTS["correctness"] +
            clarity * self.WEIGHTS["clarity"]
        )

        # Determine quality level
        quality = self._determine_quality(overall)

        # Find blocking issues
        blocking = [i for i in issues if i.startswith("[BLOCKING]")]

        score = ExampleScore(
            realism=realism,
            helpfulness=helpfulness,
            completeness=completeness,
            correctness=correctness,
            clarity=clarity,
            overall=overall,
            quality=quality,
            issues=issues,
            suggestions=suggestions
        )

        return ExampleValidation(
            example_path=example.get("path", "unknown"),
            score=score,
            passed=overall >= self.PASS_THRESHOLD and not blocking,
            blocking_issues=blocking
        )

    def _determine_quality(self, score: float) -> ExampleQuality:
        if score >= 9.0:
            return ExampleQuality.EXCELLENT
        elif score >= 7.0:
            return ExampleQuality.GOOD
        elif score >= 5.0:
            return ExampleQuality.ACCEPTABLE
        elif score >= 3.0:
            return ExampleQuality.POOR
        else:
            return ExampleQuality.UNACCEPTABLE
```

## Realism Scoring

```python
def _score_realism(
    self,
    example: dict,
    issues: list[str],
    suggestions: list[str]
) -> float:
    """Score how realistic the example is."""
    score = 10.0
    content = example.get("input_content", "")
    expected = example.get("expected_output", "")

    # Check for placeholder data
    placeholder_patterns = [
        r'\bfoo\b', r'\bbar\b', r'\bbaz\b',
        r'\bexample\.com\b', r'\btest\b',
        r'\bxxx\b', r'\byyy\b', r'\bzzz\b',
        r'lorem ipsum', r'asdf', r'1234567890',
    ]

    import re
    for pattern in placeholder_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            score -= 1.5
            issues.append(f"Placeholder data detected: {pattern}")

    # Check for realistic structure
    if len(content) < 10:
        score -= 2.0
        issues.append("Input too short to be realistic")

    # Check for domain-appropriate content
    if not self._has_domain_content(example):
        score -= 1.0
        suggestions.append("Add domain-specific realistic data")

    # Check for believable values
    unrealistic_patterns = [
        (r'\$0\.00', "Zero dollar amounts"),
        (r'user@email\.com', "Generic email"),
        (r'123-456-7890', "Fake phone number"),
        (r'John Doe', "Placeholder name"),
    ]

    for pattern, desc in unrealistic_patterns:
        if re.search(pattern, content):
            score -= 0.5
            suggestions.append(f"Replace {desc} with realistic data")

    return max(0.0, score)

def _has_domain_content(self, example: dict) -> bool:
    """Check if example has domain-appropriate content."""
    content = example.get("input_content", "").lower()
    skill_type = example.get("skill_type", "")

    domain_keywords = {
        "builder": ["generate", "create", "template", "output"],
        "analyzer": ["analyze", "report", "metrics", "findings"],
        "validator": ["validate", "check", "error", "valid"],
        "automation": ["run", "execute", "script", "process"],
        "guide": ["how to", "step", "learn", "tutorial"],
    }

    keywords = domain_keywords.get(skill_type, [])
    return any(kw in content for kw in keywords)
```

## Helpfulness Scoring

```python
def _score_helpfulness(
    self,
    example: dict,
    issues: list[str],
    suggestions: list[str]
) -> float:
    """Score how helpful the example is."""
    score = 10.0

    # Must have description
    if not example.get("description"):
        score -= 3.0
        issues.append("[BLOCKING] Example missing description")

    # Must demonstrate a clear use case
    if not example.get("use_case"):
        score -= 1.0
        suggestions.append("Add explicit use case description")

    # Should show expected output
    if not example.get("expected_output"):
        score -= 2.0
        issues.append("Missing expected output - users can't verify results")

    # Should include command/usage
    if not example.get("command"):
        score -= 1.5
        issues.append("Missing command - users don't know how to run")

    # Should have notes for context
    if not example.get("notes"):
        score -= 0.5
        suggestions.append("Add notes explaining key points")

    # Check if example solves a real problem
    description = example.get("description", "").lower()
    problem_indicators = ["how to", "when", "solve", "fix", "create", "generate"]
    if not any(ind in description for ind in problem_indicators):
        score -= 1.0
        suggestions.append("Frame example around solving a specific problem")

    return max(0.0, score)
```

## Completeness Scoring

```python
def _score_completeness(
    self,
    example: dict,
    issues: list[str],
    suggestions: list[str]
) -> float:
    """Score how complete the example is."""
    score = 10.0

    required_fields = ["name", "input_content", "expected_output", "command"]
    for field in required_fields:
        if not example.get(field):
            score -= 2.0
            issues.append(f"Missing required field: {field}")

    # Check input has enough content
    input_content = example.get("input_content", "")
    if len(input_content) < 50:
        score -= 1.0
        suggestions.append("Input too minimal - add realistic content")

    # Check expected output is meaningful
    expected = example.get("expected_output", "")
    if len(expected) < 20:
        score -= 1.0
        suggestions.append("Expected output too minimal")

    # Check for complete workflow
    if not self._shows_full_workflow(example):
        score -= 1.5
        suggestions.append("Show complete workflow from start to finish")

    # Should have category assignment
    if not example.get("category"):
        score -= 0.5
        suggestions.append("Assign example to category (basic/advanced/edge-case)")

    return max(0.0, score)

def _shows_full_workflow(self, example: dict) -> bool:
    """Check if example demonstrates complete workflow."""
    command = example.get("command", "")
    expected = example.get("expected_output", "")

    # Has both input processing and output
    return bool(command) and bool(expected)
```

## Correctness Scoring

```python
def _score_correctness(
    self,
    example: dict,
    issues: list[str],
    suggestions: list[str]
) -> float:
    """Score syntactic and semantic correctness."""
    score = 10.0

    input_content = example.get("input_content", "")
    input_file = example.get("input_file", "")

    # Validate syntax based on file type
    if input_file.endswith(".json"):
        if not self._is_valid_json(input_content):
            score -= 4.0
            issues.append("[BLOCKING] Invalid JSON syntax in input")

    elif input_file.endswith(".yaml") or input_file.endswith(".yml"):
        if not self._is_valid_yaml(input_content):
            score -= 4.0
            issues.append("[BLOCKING] Invalid YAML syntax in input")

    elif input_file.endswith(".py"):
        if not self._is_valid_python(input_content):
            score -= 3.0
            issues.append("Invalid Python syntax in input")

    # Check command syntax
    command = example.get("command", "")
    if command and not self._is_valid_command(command):
        score -= 2.0
        issues.append("Command syntax appears invalid")

    # Check expected output makes sense
    expected = example.get("expected_output", "")
    if expected and input_content:
        if not self._output_relates_to_input(input_content, expected):
            score -= 1.0
            suggestions.append("Expected output should relate to input")

    return max(0.0, score)

def _is_valid_json(self, content: str) -> bool:
    import json
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

def _is_valid_yaml(self, content: str) -> bool:
    try:
        import yaml
        yaml.safe_load(content)
        return True
    except:
        return False

def _is_valid_python(self, content: str) -> bool:
    import ast
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False

def _is_valid_command(self, command: str) -> bool:
    # Basic command validation
    if not command.strip():
        return False
    # Should start with / for skill command or common shell
    return command.startswith("/") or command.split()[0] in [
        "python", "bash", "sh", "node", "npm", "pnpm"
    ]

def _output_relates_to_input(self, input_content: str, output: str) -> bool:
    # Check for some content overlap
    input_words = set(input_content.lower().split())
    output_words = set(output.lower().split())
    overlap = input_words & output_words
    return len(overlap) > 2
```

## Clarity Scoring

```python
def _score_clarity(
    self,
    example: dict,
    issues: list[str],
    suggestions: list[str]
) -> float:
    """Score how clear and understandable the example is."""
    score = 10.0

    # Check name is descriptive
    name = example.get("name", "")
    if len(name) < 5:
        score -= 1.0
        suggestions.append("Use more descriptive example name")

    if name.lower() in ["test", "example", "demo", "sample"]:
        score -= 1.5
        issues.append("Example name too generic")

    # Check description is clear
    description = example.get("description", "")
    if description and len(description) < 20:
        score -= 1.0
        suggestions.append("Expand description to be more helpful")

    # Check formatting
    input_content = example.get("input_content", "")
    if input_content:
        # Well-formatted content should have some structure
        if "\n" not in input_content and len(input_content) > 100:
            score -= 0.5
            suggestions.append("Break long input into multiple lines")

    # Check for inline comments in code examples
    if example.get("input_file", "").endswith((".py", ".js", ".sh")):
        if "#" not in input_content and "//" not in input_content:
            score -= 0.5
            suggestions.append("Add comments to explain code")

    return max(0.0, score)
```

## Batch Validation

```python
def validate_all_examples(
    examples_dir: Path
) -> dict[str, ExampleValidation]:
    """Validate all examples in a directory."""
    validator = ExampleQualityValidator()
    results = {}

    for example_file in examples_dir.rglob("*.txt"):
        example = load_example(example_file)
        result = validator.validate(example)
        results[str(example_file)] = result

    return results


def format_validation_report(results: dict[str, ExampleValidation]) -> str:
    """Format validation results as report."""
    lines = [
        "# Example Quality Report",
        "",
        "| Example | Score | Quality | Status |",
        "|---------|-------|---------|--------|",
    ]

    passed = 0
    failed = 0

    for path, validation in sorted(results.items()):
        status = "✓ Pass" if validation.passed else "✗ Fail"
        if validation.passed:
            passed += 1
        else:
            failed += 1

        lines.append(
            f"| {Path(path).name} | {validation.score.overall:.1f} | "
            f"{validation.score.quality.value} | {status} |"
        )

    lines.extend([
        "",
        f"**Summary:** {passed} passed, {failed} failed",
        "",
    ])

    # Add issues for failed examples
    if failed > 0:
        lines.append("## Issues")
        lines.append("")

        for path, validation in results.items():
            if not validation.passed:
                lines.append(f"### {Path(path).name}")
                for issue in validation.score.issues:
                    lines.append(f"- {issue}")
                lines.append("")

    return "\n".join(lines)
```
