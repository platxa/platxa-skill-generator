# Domain Expertise Depth Scorer

Score content for genuine domain expertise vs generic filler.

## Purpose

Detect and penalize generic AI-generated content that lacks real domain knowledge. Skills must demonstrate actual expertise to be useful.

## Expertise Indicators

### Positive Indicators (Add Points)

| Indicator | Points | Example |
|-----------|--------|---------|
| Domain-specific terminology | +1.0 | "operationId", "discriminator" (OpenAPI) |
| Specification references | +1.5 | "Per RFC 7231 section 6.5.1..." |
| Concrete numbers/limits | +0.5 | "Maximum 64 characters" |
| Real tool/library names | +0.5 | "swagger-codegen", "openapi-generator" |
| Specific version info | +0.5 | "OpenAPI 3.1 added webhooks" |
| Named patterns/concepts | +1.0 | "discriminator pattern for polymorphism" |
| Edge case details | +1.0 | "Note: nullable differs from required: false" |

### Negative Indicators (Subtract Points)

| Indicator | Points | Example |
|-----------|--------|---------|
| Generic phrases | -1.0 | "best practices", "as needed" |
| Vague descriptions | -1.5 | "various options", "different methods" |
| Placeholder content | -2.0 | "TODO", "[your content]" |
| Repeated filler | -1.0 | Same phrase 3+ times |
| Missing specifics | -0.5 | "configure appropriately" |
| No examples | -1.5 | Section without concrete example |

## Scoring Algorithm

```python
from dataclasses import dataclass

@dataclass
class ExpertiseScore:
    score: float           # 0.0 - 10.0
    depth_level: str       # shallow, moderate, deep, expert
    positive_signals: list[dict]
    negative_signals: list[dict]
    suggestions: list[str]

def score_expertise_depth(
    content: str,
    discovery: dict,
    domain: str
) -> ExpertiseScore:
    """
    Score domain expertise depth in content.

    Args:
        content: Skill content to analyze
        discovery: Discovery findings with domain terms
        domain: Target domain name

    Returns:
        ExpertiseScore with breakdown
    """
    positive = []
    negative = []
    base_score = 5.0  # Start neutral

    # 1. Terminology analysis
    term_result = analyze_terminology(content, discovery)
    base_score += term_result.score_delta
    positive.extend(term_result.positive)
    negative.extend(term_result.negative)

    # 2. Specificity analysis
    spec_result = analyze_specificity(content)
    base_score += spec_result.score_delta
    positive.extend(spec_result.positive)
    negative.extend(spec_result.negative)

    # 3. Reference quality
    ref_result = analyze_references(content, domain)
    base_score += ref_result.score_delta
    positive.extend(ref_result.positive)
    negative.extend(ref_result.negative)

    # 4. Example quality
    example_result = analyze_example_quality(content, discovery)
    base_score += example_result.score_delta
    positive.extend(example_result.positive)
    negative.extend(example_result.negative)

    # 5. Generic content detection
    generic_result = detect_generic_content(content)
    base_score += generic_result.score_delta
    negative.extend(generic_result.negative)

    # Clamp score
    final_score = max(0.0, min(10.0, base_score))

    # Determine depth level
    depth_level = categorize_depth(final_score)

    # Generate suggestions
    suggestions = generate_improvement_suggestions(negative)

    return ExpertiseScore(
        score=round(final_score, 1),
        depth_level=depth_level,
        positive_signals=positive,
        negative_signals=negative,
        suggestions=suggestions
    )
```

## Terminology Analysis

```python
def analyze_terminology(content: str, discovery: dict) -> AnalysisResult:
    """Analyze domain terminology usage."""
    positive = []
    negative = []
    score_delta = 0.0

    # Get expected terms from discovery
    domain_terms = discovery.get('terminology', {})
    expected_terms = set(domain_terms.keys())

    # Count term usage
    content_lower = content.lower()
    terms_found = []

    for term in expected_terms:
        if term.lower() in content_lower:
            terms_found.append(term)
            positive.append({
                'type': 'domain_term',
                'value': term,
                'points': 0.3
            })
            score_delta += 0.3

    # Check term coverage
    if expected_terms:
        coverage = len(terms_found) / len(expected_terms)
        if coverage < 0.3:
            negative.append({
                'type': 'low_term_coverage',
                'value': f'{coverage:.0%}',
                'points': -1.5
            })
            score_delta -= 1.5
        elif coverage > 0.7:
            positive.append({
                'type': 'high_term_coverage',
                'value': f'{coverage:.0%}',
                'points': 1.0
            })
            score_delta += 1.0

    return AnalysisResult(score_delta, positive, negative)
```

## Specificity Analysis

```python
# Specific number patterns
SPECIFIC_PATTERNS = [
    (r'\b\d+\s*(bytes?|chars?|characters?|lines?|tokens?)\b', 'size_limit'),
    (r'\b\d+\.\d+\b', 'version_number'),
    (r'\bRFC\s*\d+\b', 'rfc_reference'),
    (r'\b(?:v|version)\s*\d+\.\d+', 'version_reference'),
    (r'\b\d+%\b', 'percentage'),
    (r'\b(?:max|min|limit)\s*:?\s*\d+', 'constraint'),
]

# Generic vague patterns
VAGUE_PATTERNS = [
    (r'\b(?:various|different|multiple|many|several)\s+(?:options?|ways?|methods?)\b', 'vague_quantity'),
    (r'\bas\s+(?:needed|required|appropriate)\b', 'vague_instruction'),
    (r'\b(?:etc|and\s+(?:so\s+on|more))\b', 'trailing_etc'),
    (r'\b(?:some|certain|particular)\s+\w+s?\b', 'vague_reference'),
]

def analyze_specificity(content: str) -> AnalysisResult:
    """Analyze content specificity vs vagueness."""
    positive = []
    negative = []
    score_delta = 0.0

    # Check for specific patterns
    for pattern, pattern_type in SPECIFIC_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            positive.append({
                'type': 'specific_' + pattern_type,
                'count': len(matches),
                'points': min(len(matches) * 0.3, 1.5)
            })
            score_delta += min(len(matches) * 0.3, 1.5)

    # Check for vague patterns
    for pattern, pattern_type in VAGUE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            negative.append({
                'type': 'vague_' + pattern_type,
                'examples': matches[:3],
                'points': -0.5 * len(matches)
            })
            score_delta -= min(0.5 * len(matches), 2.0)

    return AnalysisResult(score_delta, positive, negative)
```

## Generic Content Detection

```python
GENERIC_PHRASES = [
    'best practices',
    'industry standard',
    'widely used',
    'commonly accepted',
    'general approach',
    'typical workflow',
    'standard process',
    'usual method',
    'recommended approach',
    'important to note',
    'it is essential',
    'make sure to',
    'don\'t forget to',
    'always remember',
]

FILLER_PATTERNS = [
    r'\bin order to\b',
    r'\bfor the purpose of\b',
    r'\bat this point in time\b',
    r'\bdue to the fact that\b',
    r'\bin terms of\b',
]

def detect_generic_content(content: str) -> AnalysisResult:
    """Detect generic filler content."""
    negative = []
    score_delta = 0.0

    content_lower = content.lower()

    # Check generic phrases
    generic_found = []
    for phrase in GENERIC_PHRASES:
        count = content_lower.count(phrase)
        if count > 0:
            generic_found.append((phrase, count))

    if generic_found:
        total_generic = sum(c for _, c in generic_found)
        negative.append({
            'type': 'generic_phrases',
            'examples': [p for p, _ in generic_found[:5]],
            'count': total_generic,
            'points': -0.3 * total_generic
        })
        score_delta -= min(0.3 * total_generic, 2.0)

    # Check filler patterns
    filler_count = 0
    for pattern in FILLER_PATTERNS:
        matches = re.findall(pattern, content_lower)
        filler_count += len(matches)

    if filler_count > 0:
        negative.append({
            'type': 'filler_language',
            'count': filler_count,
            'points': -0.2 * filler_count
        })
        score_delta -= min(0.2 * filler_count, 1.0)

    # Check for repeated content
    paragraphs = content.split('\n\n')
    repeated = find_repeated_content(paragraphs)
    if repeated:
        negative.append({
            'type': 'repeated_content',
            'count': len(repeated),
            'points': -1.0
        })
        score_delta -= 1.0

    return AnalysisResult(score_delta, [], negative)
```

## Depth Level Categories

```python
def categorize_depth(score: float) -> str:
    """Categorize expertise depth level."""
    if score >= 8.5:
        return 'expert'      # Deep domain knowledge
    elif score >= 7.0:
        return 'deep'        # Good expertise
    elif score >= 5.0:
        return 'moderate'    # Some expertise
    else:
        return 'shallow'     # Generic content
```

## Output Format

```json
{
  "expertise_depth": {
    "score": 7.8,
    "depth_level": "deep",
    "positive_signals": [
      {"type": "domain_term", "value": "operationId", "points": 0.3},
      {"type": "domain_term", "value": "discriminator", "points": 0.3},
      {"type": "specific_rfc_reference", "count": 2, "points": 0.6},
      {"type": "high_term_coverage", "value": "75%", "points": 1.0}
    ],
    "negative_signals": [
      {"type": "generic_phrases", "examples": ["best practices"], "count": 2, "points": -0.6}
    ],
    "suggestions": [
      "Replace 'best practices' with specific recommendations",
      "Add more concrete examples with real values"
    ]
  }
}
```

## Pass Criteria

| Depth Level | Score Range | Result |
|-------------|-------------|--------|
| Expert | 8.5 - 10.0 | Approve |
| Deep | 7.0 - 8.4 | Approve |
| Moderate | 5.0 - 6.9 | Revise - needs more expertise |
| Shallow | < 5.0 | Reject - too generic |

Minimum passing score: **7.0** (deep expertise)
