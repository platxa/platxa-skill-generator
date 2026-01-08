# Content Quality Scorer

Score generated skill content on clarity, completeness, and usefulness.

## Purpose

Evaluate the quality of generated skill content beyond structural compliance. This scorer assesses whether the content would actually help users accomplish tasks.

## Quality Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Clarity | 30% | How understandable is the content? |
| Completeness | 30% | Does it cover all necessary aspects? |
| Usefulness | 25% | Will it help users succeed? |
| Accuracy | 15% | Is the content technically correct? |

## Scoring Algorithm

```python
from dataclasses import dataclass

@dataclass
class QualityScore:
    total: float           # 0.0 - 10.0
    clarity: float         # 0.0 - 10.0
    completeness: float    # 0.0 - 10.0
    usefulness: float      # 0.0 - 10.0
    accuracy: float        # 0.0 - 10.0
    details: dict
    suggestions: list[str]

def score_content_quality(
    skill_content: str,
    discovery: dict,
    skill_type: str
) -> QualityScore:
    """
    Score skill content quality across all dimensions.

    Args:
        skill_content: Full SKILL.md content
        discovery: Discovery findings for context
        skill_type: builder, guide, automation, analyzer, validator

    Returns:
        QualityScore with dimension breakdowns
    """
    clarity = score_clarity(skill_content)
    completeness = score_completeness(skill_content, discovery, skill_type)
    usefulness = score_usefulness(skill_content, skill_type)
    accuracy = score_accuracy(skill_content, discovery)

    # Weighted total
    total = (
        clarity.score * 0.30 +
        completeness.score * 0.30 +
        usefulness.score * 0.25 +
        accuracy.score * 0.15
    )

    suggestions = []
    suggestions.extend(clarity.suggestions)
    suggestions.extend(completeness.suggestions)
    suggestions.extend(usefulness.suggestions)
    suggestions.extend(accuracy.suggestions)

    return QualityScore(
        total=round(total, 1),
        clarity=clarity.score,
        completeness=completeness.score,
        usefulness=usefulness.score,
        accuracy=accuracy.score,
        details={
            'clarity': clarity.details,
            'completeness': completeness.details,
            'usefulness': usefulness.details,
            'accuracy': accuracy.details,
        },
        suggestions=suggestions
    )
```

## Clarity Scoring

```python
@dataclass
class ClarityResult:
    score: float
    details: dict
    suggestions: list[str]

def score_clarity(content: str) -> ClarityResult:
    """
    Score content clarity.

    Evaluates:
    - Sentence complexity
    - Technical jargon density
    - Structure and organization
    - Heading hierarchy
    """
    details = {}
    suggestions = []
    score = 10.0  # Start at perfect, deduct for issues

    # 1. Sentence length analysis
    sentences = extract_sentences(content)
    avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    details['avg_sentence_length'] = avg_length

    if avg_length > 25:
        score -= 1.5
        suggestions.append("Consider shorter sentences (avg > 25 words)")
    elif avg_length > 20:
        score -= 0.5
        suggestions.append("Some sentences are long (avg > 20 words)")

    # 2. Passive voice detection
    passive_count = count_passive_voice(content)
    passive_ratio = passive_count / max(len(sentences), 1)
    details['passive_voice_ratio'] = passive_ratio

    if passive_ratio > 0.3:
        score -= 1.0
        suggestions.append("Reduce passive voice (> 30% of sentences)")

    # 3. Heading structure
    headings = extract_headings(content)
    details['heading_count'] = len(headings)

    if len(headings) < 3:
        score -= 1.0
        suggestions.append("Add more section headings for organization")

    # Check heading hierarchy
    if not is_valid_heading_hierarchy(headings):
        score -= 0.5
        suggestions.append("Fix heading hierarchy (don't skip levels)")

    # 4. Code block clarity
    code_blocks = extract_code_blocks(content)
    unlabeled = sum(1 for b in code_blocks if not b.language)
    if unlabeled > 0:
        score -= 0.5 * min(unlabeled, 2)
        suggestions.append(f"Add language labels to {unlabeled} code blocks")

    # 5. Jargon density
    jargon_ratio = calculate_jargon_ratio(content)
    details['jargon_ratio'] = jargon_ratio

    if jargon_ratio > 0.15:
        score -= 1.0
        suggestions.append("Consider defining technical terms (high jargon density)")

    return ClarityResult(
        score=max(0, score),
        details=details,
        suggestions=suggestions
    )
```

## Completeness Scoring

```python
def score_completeness(
    content: str,
    discovery: dict,
    skill_type: str
) -> ClarityResult:
    """
    Score content completeness.

    Evaluates:
    - Required sections present
    - Key concepts covered
    - Edge cases addressed
    - Error handling documented
    """
    details = {}
    suggestions = []
    score = 10.0

    # 1. Required sections
    required_sections = get_required_sections(skill_type)
    present_sections = extract_section_names(content)

    missing = [s for s in required_sections if s.lower() not in
               [p.lower() for p in present_sections]]
    details['missing_sections'] = missing

    if missing:
        score -= len(missing) * 1.0
        suggestions.append(f"Add missing sections: {', '.join(missing)}")

    # 2. Discovery coverage
    if discovery:
        concepts = discovery.get('key_concepts', [])
        covered = count_concepts_mentioned(content, concepts)
        coverage_ratio = covered / max(len(concepts), 1)
        details['concept_coverage'] = coverage_ratio

        if coverage_ratio < 0.7:
            score -= 2.0
            suggestions.append(
                f"Cover more key concepts ({covered}/{len(concepts)} mentioned)"
            )

    # 3. Example coverage
    examples = extract_examples(content)
    details['example_count'] = len(examples)

    min_examples = get_min_examples(skill_type)
    if len(examples) < min_examples:
        score -= 1.5
        suggestions.append(
            f"Add more examples ({len(examples)}/{min_examples} minimum)"
        )

    # 4. Error handling
    has_error_section = 'error' in content.lower() or 'troubleshoot' in content.lower()
    details['has_error_handling'] = has_error_section

    if not has_error_section and skill_type in ['automation', 'builder', 'validator']:
        score -= 1.0
        suggestions.append("Add error handling or troubleshooting section")

    # 5. Edge cases
    edge_case_indicators = ['edge case', 'special case', 'exception', 'note:', 'warning:']
    has_edge_cases = any(ind in content.lower() for ind in edge_case_indicators)
    details['addresses_edge_cases'] = has_edge_cases

    if not has_edge_cases:
        score -= 0.5
        suggestions.append("Consider documenting edge cases or special scenarios")

    return ClarityResult(
        score=max(0, score),
        details=details,
        suggestions=suggestions
    )
```

## Usefulness Scoring

```python
def score_usefulness(content: str, skill_type: str) -> ClarityResult:
    """
    Score content usefulness.

    Evaluates:
    - Actionable instructions
    - Practical examples
    - Clear workflow
    - Output descriptions
    """
    details = {}
    suggestions = []
    score = 10.0

    # 1. Actionable language
    action_verbs = count_action_verbs(content)
    verb_ratio = action_verbs / max(word_count(content) / 100, 1)
    details['action_verb_density'] = verb_ratio

    if verb_ratio < 2.0:
        score -= 1.5
        suggestions.append("Use more action verbs (run, create, check, etc.)")

    # 2. Step-by-step instructions
    has_numbered_steps = bool(re.search(r'^\d+\.', content, re.MULTILINE))
    has_bullet_steps = bool(re.search(r'^[-*]\s', content, re.MULTILINE))
    details['has_steps'] = has_numbered_steps or has_bullet_steps

    if not (has_numbered_steps or has_bullet_steps):
        score -= 1.5
        suggestions.append("Add numbered or bulleted step-by-step instructions")

    # 3. Code examples that can be copied
    code_blocks = extract_code_blocks(content)
    copyable = [b for b in code_blocks if len(b.code) > 20]
    details['copyable_examples'] = len(copyable)

    if skill_type in ['builder', 'automation'] and len(copyable) < 2:
        score -= 1.0
        suggestions.append("Add more copy-paste ready code examples")

    # 4. Output descriptions
    output_indicators = ['output', 'result', 'returns', 'produces', 'generates']
    has_output_desc = any(ind in content.lower() for ind in output_indicators)
    details['describes_output'] = has_output_desc

    if not has_output_desc:
        score -= 1.0
        suggestions.append("Describe what output/results the skill produces")

    # 5. Verification steps
    verify_indicators = ['verify', 'check', 'confirm', 'validate', 'test']
    has_verification = any(ind in content.lower() for ind in verify_indicators)
    details['has_verification'] = has_verification

    if not has_verification:
        score -= 0.5
        suggestions.append("Add steps to verify successful completion")

    return ClarityResult(
        score=max(0, score),
        details=details,
        suggestions=suggestions
    )
```

## Accuracy Scoring

```python
def score_accuracy(content: str, discovery: dict) -> ClarityResult:
    """
    Score content accuracy against discovery findings.

    Evaluates:
    - Terminology usage
    - Technical correctness
    - No placeholder content
    - Consistency with discovery
    """
    details = {}
    suggestions = []
    score = 10.0

    # 1. Placeholder detection
    placeholders = find_placeholders(content)
    details['placeholder_count'] = len(placeholders)

    if placeholders:
        score -= len(placeholders) * 2.0
        suggestions.append(f"Remove placeholder content: {placeholders[:3]}")

    # 2. Terminology consistency
    if discovery:
        terms = discovery.get('terminology', {})
        misused = check_term_usage(content, terms)
        details['term_misuse'] = misused

        if misused:
            score -= len(misused) * 0.5
            suggestions.append(f"Check terminology usage: {misused[:3]}")

    # 3. Broken references
    broken_links = find_broken_internal_links(content)
    details['broken_links'] = broken_links

    if broken_links:
        score -= len(broken_links) * 0.5
        suggestions.append(f"Fix broken references: {broken_links[:3]}")

    # 4. Code syntax validity
    code_blocks = extract_code_blocks(content)
    for block in code_blocks:
        if block.language and not is_valid_syntax(block.code, block.language):
            score -= 0.5
            details.setdefault('syntax_errors', []).append(block.language)

    if details.get('syntax_errors'):
        suggestions.append("Fix code syntax errors in examples")

    return ClarityResult(
        score=max(0, score),
        details=details,
        suggestions=suggestions
    )
```

## Helper Functions

```python
PLACEHOLDER_PATTERNS = [
    r'\[.*?\]',           # [placeholder]
    r'TODO',
    r'TBD',
    r'FIXME',
    r'XXX',
    r'lorem ipsum',
    r'example\s*\d+',     # Example 1, Example 2
    r'your\s+\w+\s+here',  # your code here
]

def find_placeholders(content: str) -> list[str]:
    """Find placeholder content in text."""
    found = []
    content_lower = content.lower()

    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, content_lower, re.IGNORECASE)
        found.extend(matches[:5])  # Limit matches

    return list(set(found))

ACTION_VERBS = {
    'run', 'execute', 'create', 'build', 'generate', 'install',
    'configure', 'set', 'add', 'remove', 'update', 'modify',
    'check', 'verify', 'validate', 'test', 'review', 'analyze',
    'read', 'write', 'edit', 'copy', 'move', 'delete',
    'start', 'stop', 'restart', 'deploy', 'publish'
}

def count_action_verbs(content: str) -> int:
    """Count action verbs in content."""
    words = content.lower().split()
    return sum(1 for w in words if w in ACTION_VERBS)
```

## Output Format

```json
{
  "content_quality": {
    "total": 7.8,
    "passed": true,
    "dimensions": {
      "clarity": 8.5,
      "completeness": 7.0,
      "usefulness": 8.0,
      "accuracy": 7.5
    },
    "details": {
      "clarity": {
        "avg_sentence_length": 18,
        "passive_voice_ratio": 0.15,
        "heading_count": 8
      },
      "completeness": {
        "missing_sections": [],
        "concept_coverage": 0.85,
        "example_count": 4
      }
    },
    "suggestions": [
      "Add more examples (4/5 minimum)",
      "Consider documenting edge cases"
    ]
  }
}
```

## Pass Criteria

| Score Range | Result | Action |
|-------------|--------|--------|
| 8.0 - 10.0 | Excellent | Approve |
| 7.0 - 7.9 | Good | Approve with minor suggestions |
| 5.0 - 6.9 | Needs Work | Revise before approval |
| < 5.0 | Poor | Reject, significant rewrite needed |
