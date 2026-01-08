# Workflow Completion Summary

Pattern for displaying comprehensive summary after skill generation.

## Summary Structure

```python
@dataclass
class CompletionSummary:
    skill_name: str
    skill_type: str
    status: Literal["success", "partial", "failed"]
    quality_score: float
    install_path: str
    files_created: list[FileInfo]
    total_tokens: int
    total_size_bytes: int
    elapsed_time: float
    iterations: int
    warnings: list[str]
    next_steps: list[str]

@dataclass
class FileInfo:
    path: str
    size_bytes: int
    token_count: int
    status: Literal["created", "updated", "unchanged"]
```

## Display Format

### Success Summary

```
══════════════════════════════════════════════════════════════════════
  ✓ SKILL GENERATED SUCCESSFULLY
══════════════════════════════════════════════════════════════════════

  Skill Name:    api-doc-generator
  Skill Type:    Builder
  Quality Score: 8.2/10.0 ████████░░

──────────────────────────────────────────────────────────────────────
  FILES CREATED
──────────────────────────────────────────────────────────────────────

  SKILL.md                      │  4,230 B  │  1,847 tokens  │ ✓
  references/concepts.md        │  2,156 B  │    892 tokens  │ ✓
  references/workflow.md        │  3,412 B  │  1,423 tokens  │ ✓
  references/templates.md       │  1,890 B  │    756 tokens  │ ✓
  scripts/generate.sh           │    892 B  │      -         │ ✓
  scripts/validate.sh           │    654 B  │      -         │ ✓
  ────────────────────────────────────────────────────────────────
  Total                         │ 13,234 B  │  4,918 tokens

──────────────────────────────────────────────────────────────────────
  QUALITY BREAKDOWN
──────────────────────────────────────────────────────────────────────

  Spec Compliance     10.0/10  ██████████  Required fields present
  Content Quality      8.0/10  ████████░░  Clear, well-structured
  User Experience      7.5/10  ███████░░░  Good examples
  Maintainability      8.0/10  ████████░░  Modular design
  Security            10.0/10  ██████████  No issues detected

──────────────────────────────────────────────────────────────────────
  INSTALLATION
──────────────────────────────────────────────────────────────────────

  Location: ~/.claude/skills/api-doc-generator/
  Status:   Installed and ready to use

──────────────────────────────────────────────────────────────────────
  TIMING
──────────────────────────────────────────────────────────────────────

  Total Time:  2m 34s
  Iterations:  1 (passed on first attempt)

══════════════════════════════════════════════════════════════════════
  NEXT STEPS
══════════════════════════════════════════════════════════════════════

  1. Test the skill: claude "Use /api-doc-generator to document my API"
  2. Review generated files: cat ~/.claude/skills/api-doc-generator/SKILL.md
  3. Customize if needed: Edit files in ~/.claude/skills/api-doc-generator/

══════════════════════════════════════════════════════════════════════
```

### Partial Success Summary

```
══════════════════════════════════════════════════════════════════════
  ⚠ SKILL GENERATED WITH WARNINGS
══════════════════════════════════════════════════════════════════════

  Skill Name:    data-validator
  Skill Type:    Validator
  Quality Score: 6.8/10.0 ██████░░░░

──────────────────────────────────────────────────────────────────────
  FILES CREATED
──────────────────────────────────────────────────────────────────────

  SKILL.md                      │  3,890 B  │  1,654 tokens  │ ✓
  references/validation-rules.md│  2,340 B  │    978 tokens  │ ✓
  scripts/validate.sh           │    756 B  │      -         │ ⚠
  ────────────────────────────────────────────────────────────────
  Total                         │  6,986 B  │  2,632 tokens

──────────────────────────────────────────────────────────────────────
  WARNINGS (2)
──────────────────────────────────────────────────────────────────────

  1. Quality score below target (6.8 < 7.0)
     → Consider adding more examples to improve UX score

  2. scripts/validate.sh has shellcheck warnings
     → Review SC2086: Double quote to prevent globbing

──────────────────────────────────────────────────────────────────────
  INSTALLATION
──────────────────────────────────────────────────────────────────────

  Location: ~/.claude/skills/data-validator/
  Status:   Installed (review warnings recommended)

══════════════════════════════════════════════════════════════════════
```

### Failure Summary

```
══════════════════════════════════════════════════════════════════════
  ✗ SKILL GENERATION FAILED
══════════════════════════════════════════════════════════════════════

  Skill Name:    complex-analyzer
  Skill Type:    Analyzer

──────────────────────────────────────────────────────────────────────
  FAILURE REASON
──────────────────────────────────────────────────────────────────────

  Phase:  Validation
  Error:  Token budget exceeded

  Details:
    SKILL.md: 6,234 tokens (limit: 5,000)
    Total:   12,456 tokens (limit: 10,000)

──────────────────────────────────────────────────────────────────────
  PARTIAL FILES (not installed)
──────────────────────────────────────────────────────────────────────

  Location: /tmp/skill-generator/complex-analyzer/

  SKILL.md                      │  6,234 tokens  │ ✗ Over limit
  references/analysis-guide.md  │  4,123 tokens  │ ✓
  references/patterns.md        │  2,099 tokens  │ ✓

──────────────────────────────────────────────────────────────────────
  RECOVERY OPTIONS
──────────────────────────────────────────────────────────────────────

  1. Reduce SKILL.md content:
     skill-generator retry --reduce-tokens

  2. Move content to references:
     skill-generator retry --split-content

  3. Start over with simpler scope:
     skill-generator new --name complex-analyzer --minimal

══════════════════════════════════════════════════════════════════════
```

## JSON Summary Format

```json
{
  "status": "success",
  "skill": {
    "name": "api-doc-generator",
    "type": "builder",
    "description": "Generate API documentation from OpenAPI specs"
  },
  "quality": {
    "score": 8.2,
    "max_score": 10.0,
    "passed": true,
    "dimensions": {
      "spec_compliance": 10.0,
      "content_quality": 8.0,
      "user_experience": 7.5,
      "maintainability": 8.0,
      "security": 10.0
    }
  },
  "files": [
    {
      "path": "SKILL.md",
      "size_bytes": 4230,
      "token_count": 1847,
      "status": "created"
    },
    {
      "path": "references/concepts.md",
      "size_bytes": 2156,
      "token_count": 892,
      "status": "created"
    }
  ],
  "totals": {
    "files": 6,
    "size_bytes": 13234,
    "token_count": 4918
  },
  "installation": {
    "path": "~/.claude/skills/api-doc-generator/",
    "status": "installed",
    "scope": "user"
  },
  "timing": {
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:32:34Z",
    "elapsed_seconds": 154,
    "iterations": 1
  },
  "warnings": [],
  "next_steps": [
    "Test the skill with a sample request",
    "Review and customize generated files"
  ]
}
```

## Summary Generator

```python
def generate_completion_summary(result: GenerationResult) -> CompletionSummary:
    """Generate completion summary from generation result."""

    files = []
    total_tokens = 0
    total_size = 0

    for file_path, content in result.files.items():
        token_count = count_tokens(content) if file_path.endswith('.md') else 0
        size = len(content.encode('utf-8'))

        files.append(FileInfo(
            path=file_path,
            size_bytes=size,
            token_count=token_count,
            status="created"
        ))

        total_tokens += token_count
        total_size += size

    # Determine status
    if result.quality_score >= 7.0 and not result.errors:
        status = "success"
    elif result.quality_score >= 5.0:
        status = "partial"
    else:
        status = "failed"

    # Generate next steps
    next_steps = generate_next_steps(result, status)

    return CompletionSummary(
        skill_name=result.skill_name,
        skill_type=result.skill_type,
        status=status,
        quality_score=result.quality_score,
        install_path=result.install_path,
        files_created=files,
        total_tokens=total_tokens,
        total_size_bytes=total_size,
        elapsed_time=result.elapsed_seconds,
        iterations=result.iterations,
        warnings=result.warnings,
        next_steps=next_steps
    )

def generate_next_steps(result: GenerationResult, status: str) -> list[str]:
    """Generate contextual next steps based on result."""

    if status == "success":
        return [
            f"Test the skill: claude \"Use /{result.skill_name} ...\"",
            f"Review files: cat {result.install_path}/SKILL.md",
            f"Customize if needed: Edit files in {result.install_path}/"
        ]
    elif status == "partial":
        return [
            "Review warnings and consider addressing them",
            f"Test the skill: claude \"Use /{result.skill_name} ...\"",
            "Run validation again after fixes: skill-generator validate"
        ]
    else:
        return [
            "Review error details above",
            "Try recovery options or restart with modified requirements",
            "Use --verbose flag for detailed error information"
        ]
```

## Display Helpers

```python
def format_file_table(files: list[FileInfo]) -> str:
    """Format files as aligned table."""
    lines = []
    for f in files:
        size = format_size(f.size_bytes)
        tokens = f"{f.token_count:,} tokens" if f.token_count else "-"
        status = "✓" if f.status == "created" else "⚠"
        lines.append(f"  {f.path:<30} │ {size:>8} │ {tokens:>14} │ {status}")
    return "\n".join(lines)

def format_quality_bar(score: float, max_score: float = 10.0) -> str:
    """Format quality score as visual bar."""
    filled = int((score / max_score) * 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty

def format_size(bytes: int) -> str:
    """Format bytes as human-readable size."""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"

def print_summary(summary: CompletionSummary) -> None:
    """Print formatted completion summary."""
    if summary.status == "success":
        print_success_summary(summary)
    elif summary.status == "partial":
        print_partial_summary(summary)
    else:
        print_failure_summary(summary)
```
