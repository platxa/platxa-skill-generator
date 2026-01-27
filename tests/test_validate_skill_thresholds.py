"""Tests for validate-skill.sh token/line thresholds.

Token counts are produced by count-tokens.py (tiktoken cl100k_base).

Tests cover:
- Warning (score -1) at 501-1000 lines, still passes (score >= 7)
- Error (score -2) at 1001+ lines, fails
- Warning (score -1) at 5001-10000 tokens, still passes
- Error (score -2) at 10001+ tokens, fails
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import create_skill_md, generate_long_lines


def _build_content_with_sections(body: str) -> str:
    """Wrap body in required sections so only the threshold under test triggers."""
    return f"""# Test Skill

## Overview

Testing thresholds.

## Workflow

1. Step one

## Examples

```bash
echo test
```

## Output Checklist

- [ ] Item

{body}
"""


def _words_for_token_count(target_tokens: int) -> str:
    """Generate text that produces approximately target_tokens via tiktoken cl100k_base.

    count-tokens.py (the single source of truth for token counting) uses tiktoken.
    Simple English words are ~1 token each in cl100k_base, so word_count ≈ token_count.
    """
    base_words = [
        "the",
        "skill",
        "provides",
        "functionality",
        "for",
        "testing",
        "validation",
        "code",
        "development",
        "automation",
        "system",
        "process",
        "data",
        "output",
        "input",
        "configuration",
        "setup",
    ]
    words = [base_words[i % len(base_words)] for i in range(target_tokens)]
    return " ".join(words)


class TestLineThresholdWarning:
    """Tests for 501-1000 line warning (score -1, still passes)."""

    @pytest.mark.profile
    def test_warning_at_600_lines_still_passes(
        self, temp_skill_dir: Path, run_validate_skill
    ) -> None:
        """501-1000 lines produces warning but score >= 7 (PASS)."""
        # Generate 600 lines of body content; with sections overhead ~640 total
        body = generate_long_lines(600)
        content = _build_content_with_sections(body)
        create_skill_md(
            temp_skill_dir,
            name="warn-lines-skill",
            description="A skill testing line warning threshold.",
            content=content,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert result.returncode == 0, f"Expected PASS for 600 lines.\nstdout: {result.stdout}"
        assert "WARN" in result.stdout
        assert "PASS" in result.stdout


class TestLineThresholdError:
    """Tests for 1001+ line error (score -2).

    A single error deducts 2 points (score 8, still passes ≥7).
    Verify the error is emitted; the score-based pass/fail is tested separately.
    """

    @pytest.mark.profile
    def test_error_emitted_at_1100_lines(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """1001+ lines produces an ERROR message in output."""
        body = generate_long_lines(1100)
        content = _build_content_with_sections(body)
        create_skill_md(
            temp_skill_dir,
            name="error-lines-skill",
            description="A skill testing line error threshold.",
            content=content,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert "ERROR" in result.stdout
        assert "hard limit 1000" in result.stdout


class TestTokenThresholdWarning:
    """Tests for 5001-10000 estimated token warning (score -1, still passes)."""

    @pytest.mark.profile
    def test_warning_at_7000_tokens_still_passes(
        self, temp_skill_dir: Path, run_validate_skill
    ) -> None:
        """5001-10000 estimated tokens produces warning but score >= 7 (PASS)."""
        word_body = _words_for_token_count(7000)
        content = _build_content_with_sections(word_body)
        create_skill_md(
            temp_skill_dir,
            name="warn-tokens-skill",
            description="A skill testing token warning threshold.",
            content=content,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert result.returncode == 0, f"Expected PASS for ~7000 tokens.\nstdout: {result.stdout}"
        assert "WARN" in result.stdout
        assert "PASS" in result.stdout


class TestTokenThresholdError:
    """Tests for 10001+ estimated token error (score -2).

    A single error deducts 2 points (score 8, still passes ≥7).
    Verify the error is emitted; the score-based pass/fail is tested separately.
    """

    @pytest.mark.profile
    def test_error_emitted_at_12000_tokens(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """10001+ tokens (tiktoken) produces an ERROR message in output."""
        word_body = _words_for_token_count(12000)
        content = _build_content_with_sections(word_body)
        create_skill_md(
            temp_skill_dir,
            name="error-tokens-skill",
            description="A skill testing token error threshold.",
            content=content,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert "ERROR" in result.stdout
        assert "hard limit 10000" in result.stdout
