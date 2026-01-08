# Token Budget Validator

Validate skill files against token budget constraints.

## Purpose

Ensure generated skills don't exceed token limits that would impact Claude's performance or cause loading failures.

## Budget Constraints

| Component | Line Limit | Token Target | Token Max |
|-----------|------------|--------------|-----------|
| SKILL.md | 500 lines | 4000 tokens | 5000 tokens |
| Frontmatter | 20 lines | 80 tokens | 100 tokens |
| Single reference | - | 1500 tokens | 2000 tokens |
| Total references | - | 8000 tokens | 10000 tokens |
| Total skill | - | 12000 tokens | 15000 tokens |

## Token Estimation

```python
def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text.

    Uses word-based approximation:
    - Average ~1.3 tokens per word for English
    - Code tends to be ~1.5 tokens per word
    - YAML/markdown ~1.2 tokens per word

    For accuracy, use tiktoken with cl100k_base encoding.
    """
    words = len(text.split())
    return int(words * 1.3)


def estimate_tokens_accurate(text: str) -> int:
    """
    Accurate token count using tiktoken.

    Requires: pip install tiktoken
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback to estimation
        return estimate_tokens(text)
```

## Validation Algorithm

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class BudgetResult:
    passed: bool
    errors: list[str]
    warnings: list[str]
    metrics: dict

# Budget limits
LIMITS = {
    'skill_md_lines': 500,
    'skill_md_tokens': 5000,
    'frontmatter_tokens': 100,
    'single_ref_tokens': 2000,
    'total_ref_tokens': 10000,
    'total_skill_tokens': 15000,
}

# Warning thresholds (80% of limit)
WARN_THRESHOLDS = {k: int(v * 0.8) for k, v in LIMITS.items()}


def validate_token_budget(skill_dir: Path) -> BudgetResult:
    """
    Validate all token budgets for a skill.

    Args:
        skill_dir: Path to skill directory

    Returns:
        BudgetResult with pass/fail and metrics
    """
    errors = []
    warnings = []
    metrics = {}

    skill_md = skill_dir / "SKILL.md"

    # 1. SKILL.md validation
    if not skill_md.exists():
        return BudgetResult(
            passed=False,
            errors=["SKILL.md not found"],
            warnings=[],
            metrics={}
        )

    content = skill_md.read_text()

    # Line count
    lines = len(content.split('\n'))
    metrics['skill_md_lines'] = lines

    if lines > LIMITS['skill_md_lines']:
        errors.append(
            f"SKILL.md exceeds line limit: {lines} lines "
            f"(max {LIMITS['skill_md_lines']})"
        )
    elif lines > WARN_THRESHOLDS['skill_md_lines']:
        warnings.append(
            f"SKILL.md approaching line limit: {lines} lines "
            f"(max {LIMITS['skill_md_lines']})"
        )

    # Token count
    tokens = estimate_tokens_accurate(content)
    metrics['skill_md_tokens'] = tokens

    if tokens > LIMITS['skill_md_tokens']:
        errors.append(
            f"SKILL.md exceeds token limit: {tokens} tokens "
            f"(max {LIMITS['skill_md_tokens']})"
        )
    elif tokens > WARN_THRESHOLDS['skill_md_tokens']:
        warnings.append(
            f"SKILL.md approaching token limit: {tokens} tokens "
            f"(max {LIMITS['skill_md_tokens']})"
        )

    # 2. Frontmatter validation
    fm_result = validate_frontmatter_budget(content)
    metrics['frontmatter_tokens'] = fm_result.tokens
    errors.extend(fm_result.errors)
    warnings.extend(fm_result.warnings)

    # 3. References validation
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        ref_result = validate_references_budget(refs_dir)
        metrics.update(ref_result.metrics)
        errors.extend(ref_result.errors)
        warnings.extend(ref_result.warnings)

    # 4. Total skill budget
    total_tokens = metrics.get('skill_md_tokens', 0)
    total_tokens += metrics.get('total_ref_tokens', 0)
    metrics['total_skill_tokens'] = total_tokens

    if total_tokens > LIMITS['total_skill_tokens']:
        errors.append(
            f"Total skill exceeds token limit: {total_tokens} tokens "
            f"(max {LIMITS['total_skill_tokens']})"
        )
    elif total_tokens > WARN_THRESHOLDS['total_skill_tokens']:
        warnings.append(
            f"Total skill approaching token limit: {total_tokens} tokens "
            f"(max {LIMITS['total_skill_tokens']})"
        )

    return BudgetResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )
```

## Frontmatter Budget Validation

```python
@dataclass
class FrontmatterBudget:
    tokens: int
    errors: list[str]
    warnings: list[str]

def validate_frontmatter_budget(content: str) -> FrontmatterBudget:
    """Validate frontmatter stays within token budget."""
    errors = []
    warnings = []

    # Extract frontmatter
    if not content.startswith('---'):
        return FrontmatterBudget(tokens=0, errors=[], warnings=[])

    parts = content.split('---', 2)
    if len(parts) < 3:
        return FrontmatterBudget(tokens=0, errors=[], warnings=[])

    frontmatter = parts[1]
    tokens = estimate_tokens_accurate(frontmatter)

    if tokens > LIMITS['frontmatter_tokens']:
        errors.append(
            f"Frontmatter exceeds token limit: {tokens} tokens "
            f"(max {LIMITS['frontmatter_tokens']})"
        )
    elif tokens > WARN_THRESHOLDS['frontmatter_tokens']:
        warnings.append(
            f"Frontmatter approaching limit: {tokens} tokens "
            f"(max {LIMITS['frontmatter_tokens']})"
        )

    return FrontmatterBudget(
        tokens=tokens,
        errors=errors,
        warnings=warnings
    )
```

## References Budget Validation

```python
@dataclass
class RefBudgetResult:
    metrics: dict
    errors: list[str]
    warnings: list[str]

def validate_references_budget(refs_dir: Path) -> RefBudgetResult:
    """Validate references directory token budgets."""
    errors = []
    warnings = []
    metrics = {
        'ref_file_count': 0,
        'total_ref_tokens': 0,
        'ref_files': {}
    }

    ref_files = list(refs_dir.rglob("*.md"))
    metrics['ref_file_count'] = len(ref_files)

    total_tokens = 0

    for ref_file in ref_files:
        content = ref_file.read_text()
        tokens = estimate_tokens_accurate(content)

        rel_path = str(ref_file.relative_to(refs_dir))
        metrics['ref_files'][rel_path] = tokens
        total_tokens += tokens

        # Per-file check
        if tokens > LIMITS['single_ref_tokens']:
            errors.append(
                f"Reference {rel_path} exceeds limit: {tokens} tokens "
                f"(max {LIMITS['single_ref_tokens']})"
            )
        elif tokens > WARN_THRESHOLDS['single_ref_tokens']:
            warnings.append(
                f"Reference {rel_path} approaching limit: {tokens} tokens "
                f"(max {LIMITS['single_ref_tokens']})"
            )

    metrics['total_ref_tokens'] = total_tokens

    # Total references check
    if total_tokens > LIMITS['total_ref_tokens']:
        errors.append(
            f"Total references exceed limit: {total_tokens} tokens "
            f"(max {LIMITS['total_ref_tokens']})"
        )
    elif total_tokens > WARN_THRESHOLDS['total_ref_tokens']:
        warnings.append(
            f"Total references approaching limit: {total_tokens} tokens "
            f"(max {LIMITS['total_ref_tokens']})"
        )

    return RefBudgetResult(
        metrics=metrics,
        errors=errors,
        warnings=warnings
    )
```

## Output Format

```json
{
  "token_budget_validation": {
    "passed": true,
    "errors": [],
    "warnings": [
      "SKILL.md approaching token limit: 4200 tokens (max 5000)"
    ],
    "metrics": {
      "skill_md_lines": 380,
      "skill_md_tokens": 4200,
      "frontmatter_tokens": 65,
      "ref_file_count": 3,
      "total_ref_tokens": 4500,
      "total_skill_tokens": 8700,
      "ref_files": {
        "concepts.md": 1200,
        "best-practices.md": 1800,
        "workflow.md": 1500
      }
    }
  }
}
```

## Budget Optimization Suggestions

```python
def suggest_optimizations(metrics: dict) -> list[str]:
    """Suggest ways to reduce token usage."""
    suggestions = []

    # SKILL.md too large
    if metrics.get('skill_md_tokens', 0) > 4000:
        suggestions.append(
            "Consider moving detailed content to references/ "
            "and adding brief summaries in SKILL.md"
        )

    # Large reference files
    for ref, tokens in metrics.get('ref_files', {}).items():
        if tokens > 1500:
            suggestions.append(
                f"Consider splitting {ref} into smaller files "
                f"or removing less essential content"
            )

    # Many reference files
    if metrics.get('ref_file_count', 0) > 5:
        suggestions.append(
            "Consider consolidating reference files - "
            "fewer, focused files are easier to maintain"
        )

    return suggestions
```

## CLI Integration

```bash
# In validate-skill.sh
check_token_budget() {
    local skill_dir="$1"
    local skill_md="$skill_dir/SKILL.md"

    # Line count
    local lines=$(wc -l < "$skill_md")
    if [[ $lines -gt 500 ]]; then
        error "SKILL.md too long: $lines lines (max 500)"
        return 1
    fi

    # Token estimate (words * 1.3)
    local words=$(wc -w < "$skill_md")
    local tokens=$((words * 13 / 10))
    if [[ $tokens -gt 5000 ]]; then
        error "SKILL.md token estimate: $tokens (max 5000)"
        return 1
    fi

    info "Token budget OK: ~$tokens tokens, $lines lines"
    return 0
}
```
