# Reference Token Optimization

Optimize token usage in reference documents for focused, non-redundant content.

## Token Budgets

| Component | Budget | Priority |
|-----------|--------|----------|
| SKILL.md | <5,000 tokens | Critical |
| references/ total | <10,000 tokens | High |
| Single reference | <2,000 tokens | Medium |
| scripts/ total | <3,000 tokens | Medium |

## Optimization Strategies

### 1. Content Compression

```python
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    original_tokens: int
    optimized_tokens: int
    savings_percent: float
    changes: list[str]

class TokenOptimizer:
    """Optimize content for minimal token usage."""

    def __init__(self, target_tokens: int):
        self.target = target_tokens
        self.changes: list[str] = []

    def optimize(self, content: str) -> tuple[str, OptimizationResult]:
        """Apply all optimizations."""
        original = count_tokens(content)

        # Apply optimizations in order of impact
        content = self.remove_redundancy(content)
        content = self.compress_examples(content)
        content = self.simplify_prose(content)
        content = self.deduplicate_code(content)
        content = self.trim_whitespace(content)

        optimized = count_tokens(content)
        savings = (original - optimized) / original * 100

        return content, OptimizationResult(
            original_tokens=original,
            optimized_tokens=optimized,
            savings_percent=savings,
            changes=self.changes
        )
```

### 2. Redundancy Removal

```python
def remove_redundancy(self, content: str) -> str:
    """Remove redundant content."""

    # Remove duplicate explanations
    content = self._dedupe_explanations(content)

    # Remove restated information
    content = self._remove_restatements(content)

    # Collapse repeated patterns
    content = self._collapse_patterns(content)

    return content

def _dedupe_explanations(self, content: str) -> str:
    """Remove duplicate explanations of same concept."""
    import re

    # Find repeated concept explanations
    concept_pattern = r'(?:This|The|A)\s+(\w+)\s+(?:is|are|means|refers to)'
    concepts_explained = {}

    lines = content.split('\n')
    result = []

    for line in lines:
        match = re.search(concept_pattern, line)
        if match:
            concept = match.group(1).lower()
            if concept in concepts_explained:
                # Skip duplicate explanation
                self.changes.append(f"Removed duplicate: {concept}")
                continue
            concepts_explained[concept] = True

        result.append(line)

    return '\n'.join(result)

def _remove_restatements(self, content: str) -> str:
    """Remove phrases that restate previous content."""
    restatement_phrases = [
        r"As mentioned (?:above|earlier|previously),?\s*",
        r"To reiterate,?\s*",
        r"In other words,?\s*",
        r"Put simply,?\s*",
        r"That is to say,?\s*",
    ]

    for phrase in restatement_phrases:
        import re
        matches = re.findall(phrase, content)
        if matches:
            self.changes.append(f"Removed restatements: {len(matches)}")
        content = re.sub(phrase, "", content)

    return content

def _collapse_patterns(self, content: str) -> str:
    """Collapse repeated structural patterns."""
    import re

    # Find repeated bullet patterns
    bullet_groups = re.findall(r'((?:^[-*]\s+.+$\n?){3,})', content, re.MULTILINE)

    for group in bullet_groups:
        bullets = group.strip().split('\n')
        if len(bullets) > 5:
            # Keep first 3, add ellipsis note
            collapsed = '\n'.join(bullets[:3])
            collapsed += f'\n- *(and {len(bullets) - 3} more...)*'
            content = content.replace(group, collapsed + '\n')
            self.changes.append(f"Collapsed bullet list: {len(bullets)} → 4")

    return content
```

### 3. Example Compression

```python
def compress_examples(self, content: str) -> str:
    """Compress code examples while preserving meaning."""
    import re

    # Find code blocks
    code_pattern = r'```(\w*)\n(.*?)```'

    def compress_code(match):
        lang = match.group(1)
        code = match.group(2)

        # Remove excessive comments
        code = self._strip_obvious_comments(code, lang)

        # Remove blank lines
        code = re.sub(r'\n\s*\n', '\n', code)

        # Truncate very long examples
        lines = code.split('\n')
        if len(lines) > 15:
            code = '\n'.join(lines[:12])
            code += f'\n# ... ({len(lines) - 12} more lines)'
            self.changes.append(f"Truncated code block: {len(lines)} → 13 lines")

        return f'```{lang}\n{code}```'

    return re.sub(code_pattern, compress_code, content, flags=re.DOTALL)

def _strip_obvious_comments(self, code: str, lang: str) -> str:
    """Remove comments that state the obvious."""
    obvious_patterns = [
        r'#\s*(?:import|define|set|create|initialize)\s+\w+\s*$',
        r'//\s*(?:import|define|set|create|initialize)\s+\w+\s*$',
        r'#\s*TODO:?\s*$',
        r'#\s*FIXME:?\s*$',
    ]

    for pattern in obvious_patterns:
        import re
        code = re.sub(pattern, '', code, flags=re.MULTILINE | re.IGNORECASE)

    return code
```

### 4. Prose Simplification

```python
def simplify_prose(self, content: str) -> str:
    """Simplify verbose prose."""

    # Replace verbose phrases with concise ones
    replacements = {
        r"in order to": "to",
        r"due to the fact that": "because",
        r"at this point in time": "now",
        r"in the event that": "if",
        r"for the purpose of": "for",
        r"with regard to": "about",
        r"in addition to": "besides",
        r"prior to": "before",
        r"subsequent to": "after",
        r"in spite of": "despite",
        r"on a regular basis": "regularly",
        r"at the present time": "currently",
        r"it is important to note that": "",
        r"it should be noted that": "",
        r"please note that": "",
    }

    import re
    for verbose, concise in replacements.items():
        matches = re.findall(verbose, content, re.IGNORECASE)
        if matches:
            self.changes.append(f"Simplified: '{verbose}' × {len(matches)}")
        content = re.sub(verbose, concise, content, flags=re.IGNORECASE)

    return content
```

### 5. Code Deduplication

```python
def deduplicate_code(self, content: str) -> str:
    """Replace duplicate code blocks with references."""
    import re
    import hashlib

    code_pattern = r'```(\w*)\n(.*?)```'
    code_blocks: dict[str, list[int]] = {}  # hash -> positions

    # Find all code blocks and their positions
    for i, match in enumerate(re.finditer(code_pattern, content, re.DOTALL)):
        code = match.group(2).strip()
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]

        if code_hash not in code_blocks:
            code_blocks[code_hash] = []
        code_blocks[code_hash].append(i)

    # Replace duplicates with references
    for code_hash, positions in code_blocks.items():
        if len(positions) > 1:
            self.changes.append(f"Deduplicated code block: {len(positions)} instances")
            # Keep first, reference others
            # (Implementation would modify content)

    return content
```

## Token Counting

```python
def count_tokens(text: str) -> int:
    """Count tokens in text (approximate)."""
    # Approximate: 1 token ≈ 4 characters for English
    # More accurate: use tiktoken for exact count

    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback approximation
        return len(text) // 4
```

## Budget Enforcement

```python
@dataclass
class TokenBudget:
    component: str
    budget: int
    actual: int
    over_budget: bool
    suggested_cuts: list[str]

def enforce_budget(
    files: dict[str, str],
    budgets: dict[str, int]
) -> list[TokenBudget]:
    """Enforce token budgets on generated files."""
    results = []

    for path, content in files.items():
        # Determine budget category
        if path == "SKILL.md":
            budget = budgets.get("skill_md", 5000)
        elif path.startswith("references/"):
            budget = budgets.get("single_reference", 2000)
        elif path.startswith("scripts/"):
            budget = budgets.get("single_script", 1000)
        else:
            budget = budgets.get("default", 2000)

        actual = count_tokens(content)
        over = actual > budget

        # Suggest cuts if over budget
        cuts = []
        if over:
            excess = actual - budget
            cuts = suggest_cuts(content, excess)

        results.append(TokenBudget(
            component=path,
            budget=budget,
            actual=actual,
            over_budget=over,
            suggested_cuts=cuts
        ))

    return results


def suggest_cuts(content: str, excess_tokens: int) -> list[str]:
    """Suggest what to cut to meet budget."""
    suggestions = []

    # Count different content types
    import re

    code_blocks = re.findall(r'```.*?```', content, re.DOTALL)
    code_tokens = sum(count_tokens(b) for b in code_blocks)

    bullet_lists = re.findall(r'(?:^[-*]\s+.+$\n?){3,}', content, re.MULTILINE)
    bullet_tokens = sum(count_tokens(b) for b in bullet_lists)

    # Suggest based on what's largest
    if code_tokens > excess_tokens:
        suggestions.append(f"Trim code examples (-{code_tokens} tokens available)")

    if bullet_tokens > excess_tokens / 2:
        suggestions.append(f"Condense bullet lists (-{bullet_tokens} tokens available)")

    suggestions.append("Remove redundant explanations")
    suggestions.append("Use references instead of duplicating content")

    return suggestions
```

## Reference-Instead-of-Repeat

```python
def apply_references(content: str, definitions: dict[str, str]) -> str:
    """Replace repeated content with references to definitions."""

    for term, definition in definitions.items():
        if definition in content:
            # Count occurrences
            count = content.count(definition)
            if count > 1:
                # Keep first, replace rest with reference
                first_pos = content.find(definition)
                before = content[:first_pos + len(definition)]
                after = content[first_pos + len(definition):]

                # Replace in "after" portion
                after = after.replace(
                    definition,
                    f"(see [{term}](#glossary))"
                )
                content = before + after

    return content
```

## Optimization Pipeline

```python
def optimize_references(skill_dir: Path) -> dict[str, OptimizationResult]:
    """Run full optimization pipeline on references."""

    results = {}
    budgets = {
        "skill_md": 5000,
        "single_reference": 2000,
        "references_total": 10000,
        "single_script": 1000,
    }

    # Load all files
    files = {}
    for md_file in skill_dir.rglob("*.md"):
        rel_path = md_file.relative_to(skill_dir)
        files[str(rel_path)] = md_file.read_text()

    # Optimize each file
    for path, content in files.items():
        if path.startswith("references/"):
            budget = budgets["single_reference"]
        else:
            budget = budgets.get("skill_md", 5000)

        optimizer = TokenOptimizer(budget)
        optimized, result = optimizer.optimize(content)

        # Write back optimized content
        (skill_dir / path).write_text(optimized)
        results[path] = result

    # Check total budget
    total_tokens = sum(
        count_tokens(files[p])
        for p in files if p.startswith("references/")
    )
    if total_tokens > budgets["references_total"]:
        print(f"Warning: references/ total ({total_tokens}) exceeds budget ({budgets['references_total']})")

    return results
```

## Output Report

```python
def format_optimization_report(results: dict[str, OptimizationResult]) -> str:
    """Format optimization results as report."""
    lines = [
        "# Token Optimization Report",
        "",
        "| File | Original | Optimized | Savings |",
        "|------|----------|-----------|---------|",
    ]

    total_original = 0
    total_optimized = 0

    for path, result in sorted(results.items()):
        total_original += result.original_tokens
        total_optimized += result.optimized_tokens
        lines.append(
            f"| {path} | {result.original_tokens:,} | "
            f"{result.optimized_tokens:,} | {result.savings_percent:.1f}% |"
        )

    total_savings = (total_original - total_optimized) / total_original * 100
    lines.extend([
        "",
        f"**Total:** {total_original:,} → {total_optimized:,} tokens ({total_savings:.1f}% savings)",
    ])

    return "\n".join(lines)
```
