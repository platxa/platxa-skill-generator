# Quality Improvement Suggester

Generate specific, actionable suggestions for improving low-scoring quality areas.

## Suggestion Principles

1. **Specific** - Point to exact location needing improvement
2. **Actionable** - Provide concrete steps to improve
3. **Prioritized** - Order by impact on overall quality
4. **Contextual** - Consider skill type and domain

## Suggestion Model

```python
from dataclasses import dataclass
from enum import Enum

class ImprovementPriority(Enum):
    CRITICAL = 1    # Must fix - blocks quality gate
    HIGH = 2        # Should fix - significant impact
    MEDIUM = 3      # Consider fixing - moderate impact
    LOW = 4         # Nice to have - minor impact

class ImprovementCategory(Enum):
    CONTENT = "content"
    STRUCTURE = "structure"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    EXAMPLES = "examples"
    TOKENS = "tokens"

@dataclass
class Improvement:
    category: ImprovementCategory
    priority: ImprovementPriority
    location: str           # File:line or section
    current_issue: str      # What's wrong
    suggestion: str         # How to fix
    expected_impact: float  # Score improvement estimate
    example_fix: str | None # Optional example

@dataclass
class ImprovementPlan:
    overall_score: float
    target_score: float
    improvements: list[Improvement]
    estimated_final_score: float
    effort_estimate: str  # "low", "medium", "high"
```

## Suggester Implementation

```python
class QualityImprovementSuggester:
    """Generate improvement suggestions for low-scoring areas."""

    # Score thresholds
    PASS_THRESHOLD = 7.0
    EXCELLENT_THRESHOLD = 9.0

    def __init__(self, quality_scores: dict[str, float]):
        self.scores = quality_scores
        self.improvements: list[Improvement] = []

    def generate_plan(self, target_score: float = 7.0) -> ImprovementPlan:
        """Generate improvement plan to reach target score."""

        overall = self._calculate_overall()

        # Analyze each dimension
        for dimension, score in self.scores.items():
            if score < target_score:
                suggestions = self._suggest_for_dimension(dimension, score)
                self.improvements.extend(suggestions)

        # Sort by priority and impact
        self.improvements.sort(
            key=lambda i: (i.priority.value, -i.expected_impact)
        )

        # Estimate final score
        estimated = self._estimate_final_score(overall)

        # Estimate effort
        effort = self._estimate_effort()

        return ImprovementPlan(
            overall_score=overall,
            target_score=target_score,
            improvements=self.improvements,
            estimated_final_score=estimated,
            effort_estimate=effort
        )

    def _calculate_overall(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def _estimate_final_score(self, current: float) -> float:
        total_impact = sum(i.expected_impact for i in self.improvements)
        return min(10.0, current + total_impact)

    def _estimate_effort(self) -> str:
        critical = sum(1 for i in self.improvements
                       if i.priority == ImprovementPriority.CRITICAL)
        high = sum(1 for i in self.improvements
                   if i.priority == ImprovementPriority.HIGH)

        if critical > 3 or (critical + high) > 6:
            return "high"
        elif critical > 0 or high > 2:
            return "medium"
        else:
            return "low"
```

## Dimension-Specific Suggestions

```python
def _suggest_for_dimension(
    self,
    dimension: str,
    score: float
) -> list[Improvement]:
    """Generate suggestions for a specific quality dimension."""

    suggestion_map = {
        "clarity": self._suggest_clarity,
        "completeness": self._suggest_completeness,
        "accuracy": self._suggest_accuracy,
        "examples": self._suggest_examples,
        "structure": self._suggest_structure,
        "tokens": self._suggest_tokens,
        "reusability": self._suggest_reusability,
    }

    suggester = suggestion_map.get(dimension, self._suggest_generic)
    return suggester(score)


def _suggest_clarity(self, score: float) -> list[Improvement]:
    """Suggest clarity improvements."""
    suggestions = []

    if score < 5.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.CLARITY,
            priority=ImprovementPriority.CRITICAL,
            location="SKILL.md:description",
            current_issue="Description unclear or too technical",
            suggestion="Rewrite description in plain language, focus on user benefit",
            expected_impact=1.5,
            example_fix="Before: 'Implements AST-based code transformation'\n"
                       "After: 'Automatically refactors your code to follow best practices'"
        ))

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.CLARITY,
            priority=ImprovementPriority.HIGH,
            location="references/overview.md",
            current_issue="Missing or weak overview",
            suggestion="Add clear overview with purpose, key features, and quick example",
            expected_impact=1.0,
            example_fix=None
        ))

        suggestions.append(Improvement(
            category=ImprovementCategory.CLARITY,
            priority=ImprovementPriority.MEDIUM,
            location="references/*.md",
            current_issue="Inconsistent terminology",
            suggestion="Create glossary and use terms consistently throughout",
            expected_impact=0.5,
            example_fix=None
        ))

    return suggestions


def _suggest_completeness(self, score: float) -> list[Improvement]:
    """Suggest completeness improvements."""
    suggestions = []

    if score < 5.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.COMPLETENESS,
            priority=ImprovementPriority.CRITICAL,
            location="references/",
            current_issue="Missing essential documentation",
            suggestion="Add workflow.md explaining how to use the skill step-by-step",
            expected_impact=2.0,
            example_fix=None
        ))

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.COMPLETENESS,
            priority=ImprovementPriority.HIGH,
            location="references/troubleshooting.md",
            current_issue="Missing troubleshooting guide",
            suggestion="Add common problems and solutions based on skill type",
            expected_impact=1.0,
            example_fix=None
        ))

        suggestions.append(Improvement(
            category=ImprovementCategory.COMPLETENESS,
            priority=ImprovementPriority.MEDIUM,
            location="examples/",
            current_issue="Insufficient examples",
            suggestion="Add at least 3 examples: basic, advanced, and edge case",
            expected_impact=0.8,
            example_fix=None
        ))

    return suggestions


def _suggest_accuracy(self, score: float) -> list[Improvement]:
    """Suggest accuracy improvements."""
    suggestions = []

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.ACCURACY,
            priority=ImprovementPriority.HIGH,
            location="references/*.md",
            current_issue="Broken or missing cross-references",
            suggestion="Validate all links point to existing files/sections",
            expected_impact=1.0,
            example_fix=None
        ))

        suggestions.append(Improvement(
            category=ImprovementCategory.ACCURACY,
            priority=ImprovementPriority.MEDIUM,
            location="examples/",
            current_issue="Example output may not match reality",
            suggestion="Verify all examples produce shown output when run",
            expected_impact=0.7,
            example_fix=None
        ))

    return suggestions


def _suggest_examples(self, score: float) -> list[Improvement]:
    """Suggest example improvements."""
    suggestions = []

    if score < 5.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.EXAMPLES,
            priority=ImprovementPriority.CRITICAL,
            location="examples/basic/",
            current_issue="No basic examples",
            suggestion="Add simple example showing minimal usage",
            expected_impact=1.5,
            example_fix="Create examples/basic/input.txt with realistic sample data"
        ))

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.EXAMPLES,
            priority=ImprovementPriority.HIGH,
            location="examples/",
            current_issue="Examples use placeholder data",
            suggestion="Replace foo/bar/test with realistic domain data",
            expected_impact=0.8,
            example_fix="Before: 'user: foo@bar.com'\n"
                       "After: 'user: developer@company.io'"
        ))

        suggestions.append(Improvement(
            category=ImprovementCategory.EXAMPLES,
            priority=ImprovementPriority.MEDIUM,
            location="examples/",
            current_issue="Missing expected output",
            suggestion="Add expected output file for each example",
            expected_impact=0.5,
            example_fix=None
        ))

    return suggestions


def _suggest_structure(self, score: float) -> list[Improvement]:
    """Suggest structure improvements."""
    suggestions = []

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.STRUCTURE,
            priority=ImprovementPriority.HIGH,
            location="SKILL.md",
            current_issue="Poor information hierarchy",
            suggestion="Reorganize: summary → quick start → details → references",
            expected_impact=0.8,
            example_fix=None
        ))

        suggestions.append(Improvement(
            category=ImprovementCategory.STRUCTURE,
            priority=ImprovementPriority.MEDIUM,
            location="references/",
            current_issue="Files not logically organized",
            suggestion="Group related content, use consistent naming",
            expected_impact=0.5,
            example_fix=None
        ))

    return suggestions


def _suggest_tokens(self, score: float) -> list[Improvement]:
    """Suggest token optimization improvements."""
    suggestions = []

    if score < 5.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.TOKENS,
            priority=ImprovementPriority.CRITICAL,
            location="references/",
            current_issue="Token budget exceeded",
            suggestion="Remove redundant content, use references instead of repeating",
            expected_impact=2.0,
            example_fix=None
        ))

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.TOKENS,
            priority=ImprovementPriority.MEDIUM,
            location="references/*.md",
            current_issue="Verbose prose",
            suggestion="Simplify language, remove filler words",
            expected_impact=0.5,
            example_fix="Before: 'In order to accomplish this task...'\n"
                       "After: 'To do this...'"
        ))

    return suggestions


def _suggest_reusability(self, score: float) -> list[Improvement]:
    """Suggest reusability improvements."""
    suggestions = []

    if score < 7.0:
        suggestions.append(Improvement(
            category=ImprovementCategory.CONTENT,
            priority=ImprovementPriority.HIGH,
            location="scripts/",
            current_issue="Hardcoded values reduce reusability",
            suggestion="Replace hardcoded paths/values with configuration options",
            expected_impact=1.0,
            example_fix="Before: '/home/user/data'\n"
                       "After: '${DATA_DIR:-./data}'"
        ))

    return suggestions


def _suggest_generic(self, score: float) -> list[Improvement]:
    """Generic suggestions for unknown dimensions."""
    return [Improvement(
        category=ImprovementCategory.CONTENT,
        priority=ImprovementPriority.MEDIUM,
        location="*",
        current_issue=f"Low score in this area ({score:.1f})",
        suggestion="Review and improve content quality",
        expected_impact=0.5,
        example_fix=None
    )]
```

## Report Generation

```python
def format_improvement_plan(plan: ImprovementPlan) -> str:
    """Format improvement plan as actionable report."""
    lines = [
        "# Quality Improvement Plan",
        "",
        f"**Current Score:** {plan.overall_score:.1f}/10",
        f"**Target Score:** {plan.target_score:.1f}/10",
        f"**Estimated After Fixes:** {plan.estimated_final_score:.1f}/10",
        f"**Effort Required:** {plan.effort_estimate}",
        "",
        "---",
        "",
    ]

    # Group by priority
    by_priority: dict[ImprovementPriority, list[Improvement]] = {}
    for imp in plan.improvements:
        if imp.priority not in by_priority:
            by_priority[imp.priority] = []
        by_priority[imp.priority].append(imp)

    priority_labels = {
        ImprovementPriority.CRITICAL: "🔴 Critical (Must Fix)",
        ImprovementPriority.HIGH: "🟠 High Priority",
        ImprovementPriority.MEDIUM: "🟡 Medium Priority",
        ImprovementPriority.LOW: "🟢 Nice to Have",
    }

    for priority in ImprovementPriority:
        if priority not in by_priority:
            continue

        lines.append(f"## {priority_labels[priority]}")
        lines.append("")

        for i, imp in enumerate(by_priority[priority], 1):
            lines.append(f"### {i}. {imp.current_issue}")
            lines.append("")
            lines.append(f"**Location:** `{imp.location}`")
            lines.append("")
            lines.append(f"**Action:** {imp.suggestion}")
            lines.append("")
            lines.append(f"**Impact:** +{imp.expected_impact:.1f} points")

            if imp.example_fix:
                lines.append("")
                lines.append("**Example:**")
                lines.append("```")
                lines.append(imp.example_fix)
                lines.append("```")

            lines.append("")
            lines.append("---")
            lines.append("")

    # Summary
    lines.extend([
        "## Summary",
        "",
        f"- Critical fixes: {len(by_priority.get(ImprovementPriority.CRITICAL, []))}",
        f"- High priority: {len(by_priority.get(ImprovementPriority.HIGH, []))}",
        f"- Medium priority: {len(by_priority.get(ImprovementPriority.MEDIUM, []))}",
        f"- Low priority: {len(by_priority.get(ImprovementPriority.LOW, []))}",
        "",
        f"Complete critical and high priority items to reach {plan.target_score:.1f} score.",
    ])

    return "\n".join(lines)
```

## Integration

```python
def suggest_improvements(
    quality_report: dict[str, float],
    target_score: float = 7.0
) -> str:
    """Generate improvement suggestions from quality report."""
    suggester = QualityImprovementSuggester(quality_report)
    plan = suggester.generate_plan(target_score)
    return format_improvement_plan(plan)
```
