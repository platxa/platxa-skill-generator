# Quality Report Generator

Generate comprehensive quality reports showing all scores and improvement suggestions.

## Report Structure

```
┌─────────────────────────────────────────────────┐
│           SKILL QUALITY REPORT                  │
├─────────────────────────────────────────────────┤
│  Overall Score: 7.8/10  ████████░░  PASSED     │
├─────────────────────────────────────────────────┤
│  DIMENSION SCORES                               │
│  ─────────────────                              │
│  Clarity       8.5  █████████░                 │
│  Completeness  7.2  ███████░░░                 │
│  Accuracy      9.0  █████████░                 │
│  Examples      6.5  ███████░░░                 │
│  Structure     8.0  ████████░░                 │
│  Tokens        7.5  ████████░░                 │
├─────────────────────────────────────────────────┤
│  TOP IMPROVEMENTS                               │
│  ─────────────────                              │
│  1. Add more realistic examples (+0.8)          │
│  2. Complete troubleshooting guide (+0.5)       │
└─────────────────────────────────────────────────┘
```

## Report Model

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ReportFormat(Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"

class QualityLevel(Enum):
    EXCELLENT = "excellent"   # 9-10
    GOOD = "good"             # 7-8.9
    ACCEPTABLE = "acceptable" # 5-6.9
    POOR = "poor"             # 3-4.9
    FAILING = "failing"       # 0-2.9

@dataclass
class DimensionScore:
    name: str
    score: float
    max_score: float
    weight: float
    status: str  # pass/warn/fail
    details: list[str]

@dataclass
class QualityReport:
    skill_name: str
    generated_at: datetime
    overall_score: float
    quality_level: QualityLevel
    passed: bool
    dimensions: list[DimensionScore]
    improvements: list[dict]
    token_usage: dict[str, int]
    files_analyzed: list[str]
    warnings: list[str]
    errors: list[str]
```

## Report Generator

```python
class QualityReportGenerator:
    """Generate comprehensive quality reports."""

    PASS_THRESHOLD = 7.0

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.dimensions: list[DimensionScore] = []
        self.improvements: list[dict] = []
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.token_usage: dict[str, int] = {}
        self.files_analyzed: list[str] = []

    def add_dimension(
        self,
        name: str,
        score: float,
        max_score: float = 10.0,
        weight: float = 1.0,
        details: list[str] | None = None
    ) -> None:
        """Add a quality dimension score."""
        status = "pass" if score >= 7.0 else ("warn" if score >= 5.0 else "fail")
        self.dimensions.append(DimensionScore(
            name=name,
            score=score,
            max_score=max_score,
            weight=weight,
            status=status,
            details=details or []
        ))

    def add_improvement(
        self,
        description: str,
        impact: float,
        priority: str,
        location: str
    ) -> None:
        """Add an improvement suggestion."""
        self.improvements.append({
            "description": description,
            "impact": impact,
            "priority": priority,
            "location": location
        })

    def generate(self) -> QualityReport:
        """Generate the quality report."""
        overall = self._calculate_overall()
        level = self._determine_level(overall)

        return QualityReport(
            skill_name=self.skill_name,
            generated_at=datetime.now(),
            overall_score=overall,
            quality_level=level,
            passed=overall >= self.PASS_THRESHOLD,
            dimensions=self.dimensions,
            improvements=sorted(
                self.improvements,
                key=lambda x: -x["impact"]
            ),
            token_usage=self.token_usage,
            files_analyzed=self.files_analyzed,
            warnings=self.warnings,
            errors=self.errors
        )

    def _calculate_overall(self) -> float:
        if not self.dimensions:
            return 0.0

        total_weight = sum(d.weight for d in self.dimensions)
        weighted_sum = sum(d.score * d.weight for d in self.dimensions)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _determine_level(self, score: float) -> QualityLevel:
        if score >= 9.0:
            return QualityLevel.EXCELLENT
        elif score >= 7.0:
            return QualityLevel.GOOD
        elif score >= 5.0:
            return QualityLevel.ACCEPTABLE
        elif score >= 3.0:
            return QualityLevel.POOR
        else:
            return QualityLevel.FAILING
```

## Format Renderers

### Text Format

```python
def render_text(report: QualityReport) -> str:
    """Render report as plain text."""
    width = 60
    lines = []

    # Header
    lines.append("=" * width)
    lines.append(f"  SKILL QUALITY REPORT: {report.skill_name}".center(width))
    lines.append("=" * width)
    lines.append("")

    # Overall score
    bar = _score_bar(report.overall_score, 10)
    status = "PASSED" if report.passed else "FAILED"
    lines.append(f"  Overall Score: {report.overall_score:.1f}/10  {bar}  {status}")
    lines.append(f"  Quality Level: {report.quality_level.value.upper()}")
    lines.append("")

    # Dimension scores
    lines.append("-" * width)
    lines.append("  DIMENSION SCORES")
    lines.append("-" * width)

    for dim in report.dimensions:
        bar = _score_bar(dim.score, 10)
        icon = "✓" if dim.status == "pass" else ("⚠" if dim.status == "warn" else "✗")
        lines.append(f"  {icon} {dim.name:<15} {dim.score:>4.1f}  {bar}")

    lines.append("")

    # Top improvements
    if report.improvements:
        lines.append("-" * width)
        lines.append("  TOP IMPROVEMENTS")
        lines.append("-" * width)

        for i, imp in enumerate(report.improvements[:5], 1):
            lines.append(f"  {i}. {imp['description']} (+{imp['impact']:.1f})")

    lines.append("")

    # Token usage
    if report.token_usage:
        lines.append("-" * width)
        lines.append("  TOKEN USAGE")
        lines.append("-" * width)
        total = sum(report.token_usage.values())
        for component, tokens in report.token_usage.items():
            lines.append(f"  {component:<20} {tokens:>6,} tokens")
        lines.append(f"  {'TOTAL':<20} {total:>6,} tokens")

    lines.append("")

    # Warnings/Errors
    if report.errors:
        lines.append("-" * width)
        lines.append("  ERRORS")
        lines.append("-" * width)
        for error in report.errors:
            lines.append(f"  ✗ {error}")
        lines.append("")

    if report.warnings:
        lines.append("-" * width)
        lines.append("  WARNINGS")
        lines.append("-" * width)
        for warning in report.warnings:
            lines.append(f"  ⚠ {warning}")
        lines.append("")

    lines.append("=" * width)
    lines.append(f"  Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * width)

    return "\n".join(lines)


def _score_bar(score: float, max_score: float, width: int = 10) -> str:
    """Generate ASCII score bar."""
    filled = int(score / max_score * width)
    empty = width - filled
    return "█" * filled + "░" * empty
```

### Markdown Format

```python
def render_markdown(report: QualityReport) -> str:
    """Render report as markdown."""
    lines = [
        f"# Quality Report: {report.skill_name}",
        "",
        f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Overall Score | {report.overall_score:.1f}/10 |",
        f"| Quality Level | {report.quality_level.value} |",
        f"| Status | {'✓ PASSED' if report.passed else '✗ FAILED'} |",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score | Status |",
        "|-----------|-------|--------|",
    ]

    for dim in report.dimensions:
        icon = "✓" if dim.status == "pass" else ("⚠" if dim.status == "warn" else "✗")
        lines.append(f"| {dim.name} | {dim.score:.1f}/{dim.max_score:.0f} | {icon} |")

    lines.append("")

    if report.improvements:
        lines.extend([
            "## Improvement Suggestions",
            "",
            "| Priority | Suggestion | Impact |",
            "|----------|------------|--------|",
        ])

        for imp in report.improvements:
            lines.append(
                f"| {imp['priority']} | {imp['description']} | +{imp['impact']:.1f} |"
            )
        lines.append("")

    if report.token_usage:
        lines.extend([
            "## Token Usage",
            "",
            "| Component | Tokens |",
            "|-----------|--------|",
        ])

        for component, tokens in report.token_usage.items():
            lines.append(f"| {component} | {tokens:,} |")

        total = sum(report.token_usage.values())
        lines.append(f"| **Total** | **{total:,}** |")
        lines.append("")

    if report.errors:
        lines.extend([
            "## Errors",
            "",
        ])
        for error in report.errors:
            lines.append(f"- ✗ {error}")
        lines.append("")

    if report.warnings:
        lines.extend([
            "## Warnings",
            "",
        ])
        for warning in report.warnings:
            lines.append(f"- ⚠ {warning}")
        lines.append("")

    return "\n".join(lines)
```

### JSON Format

```python
import json
from dataclasses import asdict

def render_json(report: QualityReport) -> str:
    """Render report as JSON."""
    data = {
        "skill_name": report.skill_name,
        "generated_at": report.generated_at.isoformat(),
        "overall_score": report.overall_score,
        "quality_level": report.quality_level.value,
        "passed": report.passed,
        "dimensions": [
            {
                "name": d.name,
                "score": d.score,
                "max_score": d.max_score,
                "weight": d.weight,
                "status": d.status,
                "details": d.details
            }
            for d in report.dimensions
        ],
        "improvements": report.improvements,
        "token_usage": report.token_usage,
        "files_analyzed": report.files_analyzed,
        "warnings": report.warnings,
        "errors": report.errors
    }

    return json.dumps(data, indent=2)
```

## Integration

```python
def generate_quality_report(
    skill_dir: Path,
    format: ReportFormat = ReportFormat.MARKDOWN
) -> str:
    """Generate complete quality report for a skill."""

    skill_name = skill_dir.name
    generator = QualityReportGenerator(skill_name)

    # Run all validators and collect scores
    # (These would call the actual validator implementations)

    # Structure validation
    structure_score = validate_structure(skill_dir)
    generator.add_dimension("Structure", structure_score)

    # Content clarity
    clarity_score = validate_clarity(skill_dir)
    generator.add_dimension("Clarity", clarity_score)

    # Completeness check
    completeness_score = validate_completeness(skill_dir)
    generator.add_dimension("Completeness", completeness_score)

    # Reference accuracy
    accuracy_score = validate_references(skill_dir)
    generator.add_dimension("Accuracy", accuracy_score)

    # Example quality
    example_score = validate_examples(skill_dir)
    generator.add_dimension("Examples", example_score)

    # Token budget
    token_score, token_usage = validate_tokens(skill_dir)
    generator.add_dimension("Tokens", token_score)
    generator.token_usage = token_usage

    # Collect files analyzed
    generator.files_analyzed = [
        str(f.relative_to(skill_dir))
        for f in skill_dir.rglob("*.md")
    ]

    # Generate improvement suggestions
    report = generator.generate()
    improvements = suggest_improvements(
        {d.name: d.score for d in report.dimensions}
    )
    generator.improvements = improvements

    # Re-generate with improvements
    report = generator.generate()

    # Render in requested format
    renderers = {
        ReportFormat.TEXT: render_text,
        ReportFormat.MARKDOWN: render_markdown,
        ReportFormat.JSON: render_json,
    }

    renderer = renderers.get(format, render_markdown)
    return renderer(report)
```

## Example Output

```markdown
# Quality Report: api-doc-generator

**Generated:** 2024-01-15 14:32:18

## Summary

| Metric | Value |
|--------|-------|
| Overall Score | 7.8/10 |
| Quality Level | good |
| Status | ✓ PASSED |

## Dimension Scores

| Dimension | Score | Status |
|-----------|-------|--------|
| Structure | 8.5/10 | ✓ |
| Clarity | 8.0/10 | ✓ |
| Completeness | 7.2/10 | ✓ |
| Accuracy | 9.0/10 | ✓ |
| Examples | 6.5/10 | ⚠ |
| Tokens | 7.5/10 | ✓ |

## Improvement Suggestions

| Priority | Suggestion | Impact |
|----------|------------|--------|
| high | Add more realistic examples | +0.8 |
| medium | Complete troubleshooting guide | +0.5 |
| low | Simplify verbose prose | +0.3 |

## Token Usage

| Component | Tokens |
|-----------|--------|
| SKILL.md | 1,234 |
| references/ | 4,567 |
| scripts/ | 890 |
| **Total** | **6,691** |

## Warnings

- ⚠ Examples use placeholder data
- ⚠ Missing edge case examples
```
