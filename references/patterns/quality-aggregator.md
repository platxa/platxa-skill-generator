# Quality Score Aggregator

Aggregate all quality dimensions into final skill assessment.

## Purpose

Combine results from all quality validators into a single weighted score and pass/fail decision with actionable feedback.

## Quality Components

| Component | Weight | Source | Hard Fail |
|-----------|--------|--------|-----------|
| Spec Compliance | 25% | spec-compliance.md | Yes |
| Structure | 10% | structure-validator.md | Yes |
| Token Budget | 10% | token-budget-validator.md | Yes |
| Frontmatter | 10% | frontmatter-validator.md | Yes |
| Content Quality | 20% | content-quality-scorer.md | No |
| Domain Expertise | 15% | expertise-depth-scorer.md | No |
| Script Functionality | 10% | script-tester.md | Yes (if scripts) |

## Aggregation Algorithm

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ComponentScore:
    name: str
    score: float           # 0.0 - 10.0
    weight: float          # 0.0 - 1.0
    passed: bool
    hard_fail: bool        # If true, failure = overall fail
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

@dataclass
class AggregatedQuality:
    overall_score: float   # 0.0 - 10.0
    passed: bool
    recommendation: str    # APPROVE, REVISE, REJECT
    components: dict[str, ComponentScore]
    blocking_issues: list[str]
    improvements: list[str]
    summary: str

def aggregate_quality(
    spec_compliance: dict,
    structure: dict,
    token_budget: dict,
    frontmatter: dict,
    content_quality: dict,
    expertise_depth: dict,
    script_tests: Optional[dict] = None
) -> AggregatedQuality:
    """
    Aggregate all quality scores into final assessment.

    Args:
        All component validation results

    Returns:
        AggregatedQuality with overall score and recommendation
    """
    components = {}
    blocking_issues = []
    improvements = []

    # 1. Build component scores
    components['spec_compliance'] = ComponentScore(
        name='Spec Compliance',
        score=spec_compliance.get('score', 0) * 10,  # Normalize to 0-10
        weight=0.25,
        passed=spec_compliance.get('passed', False),
        hard_fail=True,
        errors=spec_compliance.get('errors', []),
        warnings=spec_compliance.get('warnings', [])
    )

    components['structure'] = ComponentScore(
        name='Structure',
        score=structure.get('completeness_score', 0) * 10,
        weight=0.10,
        passed=structure.get('passed', False),
        hard_fail=True,
        errors=structure.get('errors', []),
        warnings=structure.get('warnings', [])
    )

    components['token_budget'] = ComponentScore(
        name='Token Budget',
        score=10.0 if token_budget.get('passed', False) else 5.0,
        weight=0.10,
        passed=token_budget.get('passed', False),
        hard_fail=True,
        errors=token_budget.get('errors', []),
        warnings=token_budget.get('warnings', [])
    )

    components['frontmatter'] = ComponentScore(
        name='Frontmatter',
        score=10.0 if frontmatter.get('valid', False) else 0.0,
        weight=0.10,
        passed=frontmatter.get('valid', False),
        hard_fail=True,
        errors=frontmatter.get('errors', []),
        warnings=frontmatter.get('warnings', [])
    )

    components['content_quality'] = ComponentScore(
        name='Content Quality',
        score=content_quality.get('total', 5.0),
        weight=0.20,
        passed=content_quality.get('total', 0) >= 7.0,
        hard_fail=False,
        errors=[],
        warnings=content_quality.get('suggestions', [])
    )

    components['expertise_depth'] = ComponentScore(
        name='Domain Expertise',
        score=expertise_depth.get('score', 5.0),
        weight=0.15,
        passed=expertise_depth.get('score', 0) >= 7.0,
        hard_fail=False,
        errors=[],
        warnings=expertise_depth.get('suggestions', [])
    )

    # Script tests (if applicable)
    if script_tests:
        components['scripts'] = ComponentScore(
            name='Script Functionality',
            score=10.0 if script_tests.get('passed', False) else 3.0,
            weight=0.10,
            passed=script_tests.get('passed', False),
            hard_fail=True,
            errors=[r.get('error', '') for r in script_tests.get('results', [])
                    if not r.get('passed', True)],
            warnings=[]
        )
    else:
        # Redistribute weight if no scripts
        components['content_quality'].weight += 0.05
        components['expertise_depth'].weight += 0.05

    # 2. Check for hard failures
    for comp in components.values():
        if comp.hard_fail and not comp.passed:
            blocking_issues.extend(comp.errors)

    # 3. Calculate weighted score
    total_weight = sum(c.weight for c in components.values())
    weighted_sum = sum(c.score * c.weight for c in components.values())
    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    # 4. Determine pass/fail
    passed = len(blocking_issues) == 0 and overall_score >= 7.0

    # 5. Generate recommendation
    recommendation = determine_recommendation(
        overall_score, blocking_issues, components
    )

    # 6. Collect improvements
    for comp in components.values():
        improvements.extend(comp.warnings[:3])  # Top 3 per component

    # 7. Generate summary
    summary = generate_summary(overall_score, passed, recommendation, components)

    return AggregatedQuality(
        overall_score=round(overall_score, 1),
        passed=passed,
        recommendation=recommendation,
        components={k: asdict(v) for k, v in components.items()},
        blocking_issues=blocking_issues,
        improvements=improvements[:10],  # Top 10 overall
        summary=summary
    )
```

## Recommendation Logic

```python
def determine_recommendation(
    score: float,
    blocking_issues: list,
    components: dict
) -> str:
    """
    Determine final recommendation.

    Returns:
        APPROVE - Ready to install
        REVISE - Minor improvements needed
        REJECT - Significant issues, regenerate
    """
    # Hard failures always reject
    if blocking_issues:
        return 'REJECT'

    # Score-based recommendation
    if score >= 8.0:
        return 'APPROVE'
    elif score >= 7.0:
        # Check if any component is critically low
        low_components = [
            c for c in components.values()
            if c.score < 6.0 and c.weight >= 0.15
        ]
        if low_components:
            return 'REVISE'
        return 'APPROVE'
    elif score >= 5.0:
        return 'REVISE'
    else:
        return 'REJECT'
```

## Summary Generation

```python
def generate_summary(
    score: float,
    passed: bool,
    recommendation: str,
    components: dict
) -> str:
    """Generate human-readable summary."""

    # Find strongest and weakest
    sorted_comps = sorted(
        components.items(),
        key=lambda x: x[1].score,
        reverse=True
    )
    strongest = sorted_comps[0]
    weakest = sorted_comps[-1]

    if recommendation == 'APPROVE':
        return (
            f"Skill quality assessment PASSED with score {score:.1f}/10. "
            f"Strongest area: {strongest[1].name} ({strongest[1].score:.1f}). "
            f"Ready for installation."
        )
    elif recommendation == 'REVISE':
        return (
            f"Skill needs revision. Score: {score:.1f}/10. "
            f"Focus on improving: {weakest[1].name} ({weakest[1].score:.1f}). "
            f"Address suggestions before resubmitting."
        )
    else:
        return (
            f"Skill REJECTED. Score: {score:.1f}/10. "
            f"Critical issues in: {weakest[1].name}. "
            f"Regeneration recommended."
        )
```

## Output Format

```json
{
  "quality_assessment": {
    "overall_score": 8.2,
    "passed": true,
    "recommendation": "APPROVE",
    "components": {
      "spec_compliance": {
        "name": "Spec Compliance",
        "score": 10.0,
        "weight": 0.25,
        "passed": true,
        "hard_fail": true,
        "errors": [],
        "warnings": []
      },
      "structure": {
        "name": "Structure",
        "score": 9.2,
        "weight": 0.10,
        "passed": true,
        "hard_fail": true,
        "errors": [],
        "warnings": []
      },
      "token_budget": {
        "name": "Token Budget",
        "score": 10.0,
        "weight": 0.10,
        "passed": true,
        "hard_fail": true,
        "errors": [],
        "warnings": ["Approaching 80% of token limit"]
      },
      "frontmatter": {
        "name": "Frontmatter",
        "score": 10.0,
        "weight": 0.10,
        "passed": true,
        "hard_fail": true,
        "errors": [],
        "warnings": []
      },
      "content_quality": {
        "name": "Content Quality",
        "score": 7.8,
        "weight": 0.20,
        "passed": true,
        "hard_fail": false,
        "errors": [],
        "warnings": ["Add more examples"]
      },
      "expertise_depth": {
        "name": "Domain Expertise",
        "score": 7.2,
        "weight": 0.15,
        "passed": true,
        "hard_fail": false,
        "errors": [],
        "warnings": ["Reduce generic phrases"]
      }
    },
    "blocking_issues": [],
    "improvements": [
      "Approaching 80% of token limit",
      "Add more examples",
      "Reduce generic phrases"
    ],
    "summary": "Skill quality assessment PASSED with score 8.2/10. Strongest area: Spec Compliance (10.0). Ready for installation."
  }
}
```

## Pass Criteria

| Criteria | Threshold |
|----------|-----------|
| Overall Score | ≥ 7.0 |
| Spec Compliance | Must pass |
| Structure | Must pass |
| Token Budget | Must pass |
| Frontmatter | Must pass |
| Scripts (if any) | Must pass |

## Integration

```python
# In validation phase
quality = aggregate_quality(
    spec_compliance=check_spec_compliance(skill_dir),
    structure=validate_structure(skill_dir, skill_type),
    token_budget=validate_token_budget(skill_dir),
    frontmatter=validate_frontmatter(skill_md_content),
    content_quality=score_content_quality(content, discovery, skill_type),
    expertise_depth=score_expertise_depth(content, discovery, domain),
    script_tests=test_all_scripts(skill_dir) if has_scripts else None
)

if quality.recommendation == 'APPROVE':
    proceed_to_installation()
elif quality.recommendation == 'REVISE':
    show_improvements(quality.improvements)
else:
    trigger_regeneration(quality.blocking_issues)
```
