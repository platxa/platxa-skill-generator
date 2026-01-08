# Reusability Scorer

Score skill reusability by measuring the balance between variable and constant content.

## Reusability Principles

A reusable skill should:
1. **Parameterize** varying inputs (not hardcode)
2. **Template** common patterns (not repeat)
3. **Abstract** domain logic (not embed specifics)
4. **Configure** behavior (not assume contexts)

## Balance Metrics

| Metric | Ideal Range | Too Low | Too High |
|--------|-------------|---------|----------|
| Variable ratio | 20-40% | Inflexible | Over-engineered |
| Template coverage | 40-60% | Repetitive | Too abstract |
| Configuration points | 5-15 | Limited | Complex |
| Hardcoded values | <10% | N/A | Not reusable |

## Reusability Model

```python
from dataclasses import dataclass
from enum import Enum

class ReusabilityLevel(Enum):
    EXCELLENT = "excellent"     # 9-10
    GOOD = "good"               # 7-8.9
    MODERATE = "moderate"       # 5-6.9
    LIMITED = "limited"         # 3-4.9
    SINGLE_USE = "single_use"   # 0-2.9

@dataclass
class ReusabilityScore:
    variable_ratio: float      # % of content that varies
    constant_ratio: float      # % of content that's fixed
    template_coverage: float   # % using templates
    config_points: int         # Number of configuration options
    hardcoded_count: int       # Count of hardcoded values
    abstraction_level: float   # 0-10 abstraction score
    overall: float             # Weighted final score
    level: ReusabilityLevel
    findings: list[str]
    recommendations: list[str]
```

## Scorer Implementation

```python
class ReusabilityScorer:
    """Score skill reusability based on varies-vs-constant balance."""

    # Ideal ratios
    IDEAL_VARIABLE_MIN = 0.20
    IDEAL_VARIABLE_MAX = 0.40
    IDEAL_TEMPLATE_MIN = 0.40
    IDEAL_TEMPLATE_MAX = 0.60
    IDEAL_CONFIG_MIN = 5
    IDEAL_CONFIG_MAX = 15
    MAX_HARDCODED = 10

    def score(self, skill_content: dict[str, str]) -> ReusabilityScore:
        """Score reusability of a skill."""
        findings = []
        recommendations = []

        # Analyze all content
        all_content = "\n".join(skill_content.values())

        # Calculate metrics
        variable_ratio = self._calculate_variable_ratio(all_content, findings)
        constant_ratio = 1.0 - variable_ratio
        template_coverage = self._calculate_template_coverage(all_content, findings)
        config_points = self._count_config_points(all_content, findings)
        hardcoded_count = self._count_hardcoded_values(all_content, findings)
        abstraction_level = self._score_abstraction(all_content, findings)

        # Generate recommendations
        self._generate_recommendations(
            variable_ratio, template_coverage, config_points,
            hardcoded_count, recommendations
        )

        # Calculate overall score
        overall = self._calculate_overall(
            variable_ratio, template_coverage,
            config_points, hardcoded_count, abstraction_level
        )

        return ReusabilityScore(
            variable_ratio=variable_ratio,
            constant_ratio=constant_ratio,
            template_coverage=template_coverage,
            config_points=config_points,
            hardcoded_count=hardcoded_count,
            abstraction_level=abstraction_level,
            overall=overall,
            level=self._determine_level(overall),
            findings=findings,
            recommendations=recommendations
        )

    def _determine_level(self, score: float) -> ReusabilityLevel:
        if score >= 9.0:
            return ReusabilityLevel.EXCELLENT
        elif score >= 7.0:
            return ReusabilityLevel.GOOD
        elif score >= 5.0:
            return ReusabilityLevel.MODERATE
        elif score >= 3.0:
            return ReusabilityLevel.LIMITED
        else:
            return ReusabilityLevel.SINGLE_USE
```

## Variable Ratio Analysis

```python
def _calculate_variable_ratio(
    self,
    content: str,
    findings: list[str]
) -> float:
    """Calculate ratio of variable vs constant content."""
    import re

    total_tokens = len(content.split())
    if total_tokens == 0:
        return 0.0

    variable_tokens = 0

    # Count template variables
    template_patterns = [
        r'\{\{(\w+)\}\}',           # {{variable}}
        r'\$\{(\w+)\}',             # ${variable}
        r'\{(\w+)\}',               # {variable}
        r'<(\w+)>',                 # <placeholder>
        r'\[(\w+)\]',               # [parameter]
    ]

    for pattern in template_patterns:
        matches = re.findall(pattern, content)
        variable_tokens += len(matches) * 2  # Variable name + marker

    # Count parameterized sections
    param_sections = re.findall(
        r'(?:--\w+\s+)?(?:VALUE|PATH|NAME|URL|ID)\b',
        content, re.IGNORECASE
    )
    variable_tokens += len(param_sections)

    # Count conditional blocks
    conditionals = re.findall(
        r'(?:if|when|unless|else)\s+[\w\s]+:',
        content, re.IGNORECASE
    )
    variable_tokens += len(conditionals) * 5

    ratio = variable_tokens / total_tokens
    findings.append(f"Variable content: {ratio*100:.1f}%")

    return ratio

def _is_in_ideal_range(self, value: float, min_val: float, max_val: float) -> bool:
    return min_val <= value <= max_val
```

## Template Coverage Analysis

```python
def _calculate_template_coverage(
    self,
    content: str,
    findings: list[str]
) -> float:
    """Calculate how much content uses templates/patterns."""
    import re

    lines = content.split('\n')
    total_lines = len([l for l in lines if l.strip()])
    if total_lines == 0:
        return 0.0

    templated_lines = 0

    for line in lines:
        if not line.strip():
            continue

        # Check for template usage
        is_templated = any([
            '{{' in line,
            '${' in line,
            re.search(r'\{[a-z_]+\}', line),
            re.search(r'<[A-Z_]+>', line),
            'template' in line.lower(),
            'pattern' in line.lower(),
        ])

        if is_templated:
            templated_lines += 1

    coverage = templated_lines / total_lines
    findings.append(f"Template coverage: {coverage*100:.1f}%")

    return coverage
```

## Configuration Points

```python
def _count_config_points(
    self,
    content: str,
    findings: list[str]
) -> int:
    """Count configuration/customization points."""
    import re

    config_patterns = [
        r'--(\w+)',                    # CLI flags
        r'(?:option|config)\s*[:\[]',  # Option definitions
        r'(?:default|fallback)\s*[:=]', # Default values
        r'(?:can be|may be)\s+\w+',    # Optional behaviors
        r'(?:if|when)\s+\w+\s+is',     # Conditional configs
    ]

    config_points = set()
    for pattern in config_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        config_points.update(matches)

    count = len(config_points)
    findings.append(f"Configuration points: {count}")

    return count
```

## Hardcoded Value Detection

```python
def _count_hardcoded_values(
    self,
    content: str,
    findings: list[str]
) -> int:
    """Detect hardcoded values that reduce reusability."""
    import re

    hardcoded_patterns = [
        # Absolute paths
        (r'/(?:home|Users)/\w+/[\w/]+', "Absolute user path"),
        (r'C:\\(?:Users|Program Files)\\[\w\\]+', "Windows absolute path"),

        # Hardcoded URLs
        (r'https?://(?!example\.com)[a-z0-9.-]+\.[a-z]{2,}', "Hardcoded URL"),

        # Hardcoded IPs
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "Hardcoded IP"),

        # Hardcoded ports (non-standard)
        (r':\d{4,5}\b', "Hardcoded port"),

        # Hardcoded credentials (should never appear)
        (r'password\s*[=:]\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api[_-]?key\s*[=:]\s*["\'][^"\']+["\']', "Hardcoded API key"),

        # Magic numbers
        (r'\b(?:86400|3600|60000|1000)\b', "Magic number (time)"),
    ]

    hardcoded = []
    for pattern, desc in hardcoded_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            hardcoded.append((match, desc))

    if hardcoded:
        findings.append(f"Hardcoded values found: {len(hardcoded)}")
        for value, desc in hardcoded[:3]:  # Show first 3
            findings.append(f"  - {desc}: {value[:30]}...")

    return len(hardcoded)
```

## Abstraction Scoring

```python
def _score_abstraction(
    self,
    content: str,
    findings: list[str]
) -> float:
    """Score level of abstraction in the skill."""
    score = 5.0  # Start at middle

    # Positive: Generic patterns
    generic_indicators = [
        (r'\bany\s+\w+\b', 0.5, "Generic 'any' usage"),
        (r'\ball\s+\w+s?\b', 0.5, "Generic 'all' usage"),
        (r'\btype\s+of\b', 0.3, "Type abstraction"),
        (r'\bpattern\b', 0.3, "Pattern reference"),
        (r'\btemplate\b', 0.3, "Template reference"),
        (r'\b(?:input|output)\s+format\b', 0.4, "Format abstraction"),
    ]

    for pattern, boost, desc in generic_indicators:
        import re
        if re.search(pattern, content, re.IGNORECASE):
            score += boost
            findings.append(f"Good abstraction: {desc}")

    # Negative: Specific implementations
    specific_indicators = [
        (r'\bonly works with\b', -1.0, "Limited compatibility"),
        (r'\brequires\s+\w+\s+version\b', -0.5, "Version dependency"),
        (r'\bspecifically for\b', -0.8, "Narrow purpose"),
        (r'\bhardcoded\b', -1.0, "Explicit hardcoding"),
    ]

    for pattern, penalty, desc in specific_indicators:
        import re
        if re.search(pattern, content, re.IGNORECASE):
            score += penalty
            findings.append(f"Limited abstraction: {desc}")

    return max(0.0, min(10.0, score))
```

## Overall Score Calculation

```python
def _calculate_overall(
    self,
    variable_ratio: float,
    template_coverage: float,
    config_points: int,
    hardcoded_count: int,
    abstraction_level: float
) -> float:
    """Calculate weighted overall reusability score."""

    # Variable ratio score (0-10)
    if self.IDEAL_VARIABLE_MIN <= variable_ratio <= self.IDEAL_VARIABLE_MAX:
        var_score = 10.0
    elif variable_ratio < self.IDEAL_VARIABLE_MIN:
        var_score = (variable_ratio / self.IDEAL_VARIABLE_MIN) * 7
    else:
        excess = variable_ratio - self.IDEAL_VARIABLE_MAX
        var_score = max(3.0, 10.0 - excess * 20)

    # Template coverage score (0-10)
    if self.IDEAL_TEMPLATE_MIN <= template_coverage <= self.IDEAL_TEMPLATE_MAX:
        template_score = 10.0
    else:
        template_score = 5.0 + template_coverage * 5

    # Config points score (0-10)
    if self.IDEAL_CONFIG_MIN <= config_points <= self.IDEAL_CONFIG_MAX:
        config_score = 10.0
    elif config_points < self.IDEAL_CONFIG_MIN:
        config_score = (config_points / self.IDEAL_CONFIG_MIN) * 7
    else:
        config_score = max(4.0, 10.0 - (config_points - self.IDEAL_CONFIG_MAX) * 0.5)

    # Hardcoded penalty
    hardcoded_penalty = min(hardcoded_count * 0.5, 3.0)

    # Weighted average
    overall = (
        var_score * 0.25 +
        template_score * 0.25 +
        config_score * 0.20 +
        abstraction_level * 0.30
    ) - hardcoded_penalty

    return max(0.0, min(10.0, overall))


def _generate_recommendations(
    self,
    variable_ratio: float,
    template_coverage: float,
    config_points: int,
    hardcoded_count: int,
    recommendations: list[str]
) -> None:
    """Generate improvement recommendations."""

    if variable_ratio < self.IDEAL_VARIABLE_MIN:
        recommendations.append(
            "Add more parameterization - skill is too rigid"
        )
    elif variable_ratio > self.IDEAL_VARIABLE_MAX:
        recommendations.append(
            "Reduce variables - skill is over-engineered"
        )

    if template_coverage < self.IDEAL_TEMPLATE_MIN:
        recommendations.append(
            "Extract repeated patterns into templates"
        )

    if config_points < self.IDEAL_CONFIG_MIN:
        recommendations.append(
            "Add configuration options for flexibility"
        )
    elif config_points > self.IDEAL_CONFIG_MAX:
        recommendations.append(
            "Simplify configuration - too many options"
        )

    if hardcoded_count > 0:
        recommendations.append(
            f"Replace {hardcoded_count} hardcoded values with parameters"
        )
```

## Report Generation

```python
def format_reusability_report(score: ReusabilityScore) -> str:
    """Format reusability score as readable report."""
    lines = [
        "# Reusability Analysis",
        "",
        f"**Overall Score:** {score.overall:.1f}/10 ({score.level.value})",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Status |",
        "|--------|-------|--------|",
    ]

    # Variable ratio
    var_status = "✓" if 0.20 <= score.variable_ratio <= 0.40 else "⚠"
    lines.append(f"| Variable Content | {score.variable_ratio*100:.0f}% | {var_status} |")

    # Template coverage
    tmpl_status = "✓" if 0.40 <= score.template_coverage <= 0.60 else "⚠"
    lines.append(f"| Template Coverage | {score.template_coverage*100:.0f}% | {tmpl_status} |")

    # Config points
    cfg_status = "✓" if 5 <= score.config_points <= 15 else "⚠"
    lines.append(f"| Config Points | {score.config_points} | {cfg_status} |")

    # Hardcoded
    hc_status = "✓" if score.hardcoded_count == 0 else "✗"
    lines.append(f"| Hardcoded Values | {score.hardcoded_count} | {hc_status} |")

    # Abstraction
    abs_status = "✓" if score.abstraction_level >= 7 else "⚠"
    lines.append(f"| Abstraction Level | {score.abstraction_level:.1f}/10 | {abs_status} |")

    if score.recommendations:
        lines.extend([
            "",
            "## Recommendations",
            "",
        ])
        for rec in score.recommendations:
            lines.append(f"- {rec}")

    return "\n".join(lines)
```
