# Discovery Quality Scorer

Score discovery phase output for coverage, depth, and reliability.

## Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Coverage | 40% | Completeness of requirements and constraints |
| Depth | 35% | Detail level of domain analysis |
| Reliability | 25% | Confidence and consistency of findings |

## Score Ranges

| Score | Level | Interpretation |
|-------|-------|----------------|
| 9-10 | Excellent | Proceed with high confidence |
| 7-8 | Good | Proceed, minor gaps acceptable |
| 5-6 | Adequate | Consider additional clarification |
| 3-4 | Poor | Requires more discovery work |
| 1-2 | Insufficient | Restart discovery phase |

## Coverage Scoring (40%)

### Criteria

```python
@dataclass
class CoverageScore:
    score: float  # 1-10
    components: dict[str, float]
    missing: list[str]
    recommendations: list[str]

def score_coverage(findings: DiscoveryFindings) -> CoverageScore:
    """Score completeness of discovery findings."""
    components = {}
    missing = []

    # 1. Skill identification (20%)
    if findings.skill_name and findings.skill_type:
        components["identification"] = 10.0
    elif findings.skill_name:
        components["identification"] = 6.0
        missing.append("skill_type not determined")
    else:
        components["identification"] = 2.0
        missing.append("skill_name missing")

    # 2. Requirements (30%)
    req_count = len(findings.requirements)
    must_count = sum(1 for r in findings.requirements if r.priority == "must")

    if req_count >= 5 and must_count >= 2:
        components["requirements"] = 10.0
    elif req_count >= 3 and must_count >= 1:
        components["requirements"] = 7.0
    elif req_count >= 1:
        components["requirements"] = 4.0
        missing.append("Need more detailed requirements")
    else:
        components["requirements"] = 1.0
        missing.append("No requirements identified")

    # 3. Constraints (15%)
    constraint_types = {c.type for c in findings.constraints}
    if len(constraint_types) >= 3:
        components["constraints"] = 10.0
    elif len(constraint_types) >= 1:
        components["constraints"] = 6.0
    else:
        components["constraints"] = 3.0
        missing.append("Constraints not analyzed")

    # 4. Tools specification (15%)
    if findings.tools_needed and len(findings.tools_needed) >= 2:
        components["tools"] = 10.0
    elif findings.tools_needed:
        components["tools"] = 6.0
    else:
        components["tools"] = 2.0
        missing.append("Tool requirements missing")

    # 5. Reference planning (10%)
    if findings.reference_topics and len(findings.reference_topics) >= 2:
        components["references"] = 10.0
    elif findings.reference_topics:
        components["references"] = 6.0
    else:
        components["references"] = 3.0
        missing.append("Reference topics not planned")

    # 6. Script planning (10%)
    if findings.script_needs:
        components["scripts"] = 10.0
    else:
        components["scripts"] = 5.0  # Not always needed

    # Calculate weighted score
    weights = {
        "identification": 0.20,
        "requirements": 0.30,
        "constraints": 0.15,
        "tools": 0.15,
        "references": 0.10,
        "scripts": 0.10
    }

    score = sum(
        components[k] * weights[k]
        for k in weights
    )

    return CoverageScore(
        score=score,
        components=components,
        missing=missing,
        recommendations=generate_coverage_recommendations(missing)
    )
```

## Depth Scoring (35%)

### Criteria

```python
@dataclass
class DepthScore:
    score: float  # 1-10
    components: dict[str, float]
    shallow_areas: list[str]
    recommendations: list[str]

def score_depth(findings: DiscoveryFindings) -> DepthScore:
    """Score depth of domain analysis."""
    components = {}
    shallow_areas = []

    # 1. Domain analysis depth (30%)
    domain = findings.domain
    domain_score = 0.0

    if domain.primary_domain and len(domain.primary_domain) > 10:
        domain_score += 3.0
    if domain.subdomains and len(domain.subdomains) >= 2:
        domain_score += 3.0
    if domain.expertise_level:
        domain_score += 2.0
    if domain.related_skills:
        domain_score += 2.0

    components["domain"] = domain_score
    if domain_score < 7:
        shallow_areas.append("Domain analysis lacks detail")

    # 2. Requirement detail (30%)
    detailed_reqs = sum(
        1 for r in findings.requirements
        if len(r.description) > 30
    )
    req_ratio = detailed_reqs / max(len(findings.requirements), 1)

    components["requirement_detail"] = min(10.0, req_ratio * 12)
    if components["requirement_detail"] < 6:
        shallow_areas.append("Requirements lack specificity")

    # 3. Constraint specificity (20%)
    specific_constraints = sum(
        1 for c in findings.constraints
        if len(c.description) > 20
    )
    constraint_ratio = specific_constraints / max(len(findings.constraints), 1)

    components["constraint_detail"] = min(10.0, constraint_ratio * 12)
    if components["constraint_detail"] < 6:
        shallow_areas.append("Constraints not well-defined")

    # 4. Description quality (20%)
    desc_len = len(findings.description)
    if desc_len > 200:
        components["description"] = 10.0
    elif desc_len > 100:
        components["description"] = 7.0
    elif desc_len > 50:
        components["description"] = 5.0
    else:
        components["description"] = 3.0
        shallow_areas.append("Description too brief")

    # Calculate weighted score
    weights = {
        "domain": 0.30,
        "requirement_detail": 0.30,
        "constraint_detail": 0.20,
        "description": 0.20
    }

    score = sum(
        components[k] * weights[k]
        for k in weights
    )

    return DepthScore(
        score=score,
        components=components,
        shallow_areas=shallow_areas,
        recommendations=generate_depth_recommendations(shallow_areas)
    )
```

## Reliability Scoring (25%)

### Criteria

```python
@dataclass
class ReliabilityScore:
    score: float  # 1-10
    components: dict[str, float]
    concerns: list[str]
    recommendations: list[str]

def score_reliability(findings: DiscoveryFindings) -> ReliabilityScore:
    """Score reliability and consistency of findings."""
    components = {}
    concerns = []

    # 1. Confidence score (30%)
    conf = findings.confidence_score
    components["confidence"] = conf * 10
    if conf < 0.6:
        concerns.append(f"Low confidence: {conf:.0%}")

    # 2. Source balance (25%)
    explicit = sum(1 for r in findings.requirements if r.source == "explicit")
    inferred = sum(1 for r in findings.requirements if r.source == "inferred")
    total = explicit + inferred

    if total == 0:
        components["source_balance"] = 1.0
        concerns.append("No requirements sourced")
    elif explicit >= inferred:
        components["source_balance"] = 10.0
    elif explicit > 0:
        ratio = explicit / total
        components["source_balance"] = max(4.0, ratio * 10)
        if ratio < 0.5:
            concerns.append("Many inferred requirements")
    else:
        components["source_balance"] = 3.0
        concerns.append("All requirements inferred")

    # 3. Unresolved clarifications (25%)
    blocking = [c for c in findings.clarifications_needed if c.blocking]
    non_blocking = [c for c in findings.clarifications_needed if not c.blocking]

    if not blocking and not non_blocking:
        components["clarifications"] = 10.0
    elif not blocking:
        components["clarifications"] = 8.0 - min(3, len(non_blocking)) * 0.5
    else:
        components["clarifications"] = max(2.0, 6.0 - len(blocking) * 2)
        concerns.append(f"{len(blocking)} blocking clarification(s)")

    # 4. Consistency check (20%)
    consistency_issues = check_consistency(findings)
    if not consistency_issues:
        components["consistency"] = 10.0
    else:
        components["consistency"] = max(3.0, 10.0 - len(consistency_issues) * 2)
        concerns.extend(consistency_issues)

    # Calculate weighted score
    weights = {
        "confidence": 0.30,
        "source_balance": 0.25,
        "clarifications": 0.25,
        "consistency": 0.20
    }

    score = sum(
        components[k] * weights[k]
        for k in weights
    )

    return ReliabilityScore(
        score=score,
        components=components,
        concerns=concerns,
        recommendations=generate_reliability_recommendations(concerns)
    )

def check_consistency(findings: DiscoveryFindings) -> list[str]:
    """Check for internal consistency issues."""
    issues = []

    # Tool-requirement consistency
    for req in findings.requirements:
        if "file" in req.description.lower():
            if "Read" not in findings.tools_needed and "Write" not in findings.tools_needed:
                issues.append("File operations mentioned but no file tools")
                break

    # Type-tool consistency
    if findings.skill_type == "automation" and "Bash" not in findings.tools_needed:
        issues.append("Automation skill without Bash tool")

    # Complexity-requirements consistency
    if findings.complexity_estimate == "simple" and len(findings.requirements) > 8:
        issues.append("Many requirements but marked as simple")

    return issues
```

## Aggregate Scoring

```python
@dataclass
class DiscoveryQualityScore:
    overall: float  # 1-10
    coverage: CoverageScore
    depth: DepthScore
    reliability: ReliabilityScore
    recommendation: Literal["proceed", "clarify", "redo"]
    summary: str

def score_discovery_quality(findings: DiscoveryFindings) -> DiscoveryQualityScore:
    """Calculate overall discovery quality score."""

    coverage = score_coverage(findings)
    depth = score_depth(findings)
    reliability = score_reliability(findings)

    # Weighted aggregate
    overall = (
        coverage.score * 0.40 +
        depth.score * 0.35 +
        reliability.score * 0.25
    )

    # Determine recommendation
    if overall >= 7.0 and reliability.score >= 6.0:
        recommendation = "proceed"
    elif overall >= 5.0:
        recommendation = "clarify"
    else:
        recommendation = "redo"

    # Generate summary
    summary = generate_quality_summary(overall, coverage, depth, reliability)

    return DiscoveryQualityScore(
        overall=round(overall, 1),
        coverage=coverage,
        depth=depth,
        reliability=reliability,
        recommendation=recommendation,
        summary=summary
    )

def generate_quality_summary(
    overall: float,
    coverage: CoverageScore,
    depth: DepthScore,
    reliability: ReliabilityScore
) -> str:
    """Generate human-readable quality summary."""

    level = (
        "Excellent" if overall >= 9 else
        "Good" if overall >= 7 else
        "Adequate" if overall >= 5 else
        "Poor" if overall >= 3 else
        "Insufficient"
    )

    parts = [f"Discovery quality: {level} ({overall:.1f}/10)"]

    # Highlight lowest dimension
    scores = [
        ("Coverage", coverage.score),
        ("Depth", depth.score),
        ("Reliability", reliability.score)
    ]
    lowest = min(scores, key=lambda x: x[1])

    if lowest[1] < 6:
        parts.append(f"Weakest area: {lowest[0]} ({lowest[1]:.1f}/10)")

    # Add top recommendation
    all_recs = (
        coverage.recommendations +
        depth.recommendations +
        reliability.recommendations
    )
    if all_recs:
        parts.append(f"Priority: {all_recs[0]}")

    return " | ".join(parts)
```

## Output Format

```json
{
  "overall": 7.8,
  "recommendation": "proceed",
  "summary": "Discovery quality: Good (7.8/10) | Weakest area: Depth (6.5/10)",
  "coverage": {
    "score": 8.5,
    "components": {
      "identification": 10.0,
      "requirements": 8.0,
      "constraints": 8.0,
      "tools": 10.0,
      "references": 7.0,
      "scripts": 8.0
    },
    "missing": [],
    "recommendations": []
  },
  "depth": {
    "score": 6.5,
    "components": {
      "domain": 7.0,
      "requirement_detail": 6.0,
      "constraint_detail": 6.0,
      "description": 7.0
    },
    "shallow_areas": ["Requirements lack specificity"],
    "recommendations": ["Add more detail to requirement descriptions"]
  },
  "reliability": {
    "score": 8.5,
    "components": {
      "confidence": 8.5,
      "source_balance": 9.0,
      "clarifications": 8.0,
      "consistency": 9.0
    },
    "concerns": [],
    "recommendations": []
  }
}
```
