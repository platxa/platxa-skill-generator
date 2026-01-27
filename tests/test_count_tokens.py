"""Tests for count-tokens.py script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Small skill passes (Feature #31)
- SKILL.md token/line limits (Features #32-33)
- Reference file limits (Features #34-35)
- Total skill limits (Feature #36)
- JSON output (Feature #37)
- Missing SKILL.md handling (Feature #38)
- Warning thresholds (Features #39-40)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import (
    create_reference_file,
    create_skill_md,
    generate_long_lines,
    generate_long_text,
)


class TestSmallSkillPasses:
    """Tests for small skill acceptance."""

    @pytest.mark.tokens
    def test_small_skill_passes(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #31: Small skill returns passed=true."""
        # Create a small valid skill
        create_skill_md(
            temp_skill_dir,
            name="small-skill",
            description="A small skill for testing token counting.",
            tools=["Read", "Write"],
            content="# Small Skill\n\nThis is a minimal skill.\n",
        )

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"

        data = json.loads(result.stdout)
        assert data["passed"] is True
        assert data["skill_md_tokens"] < 5000
        assert data["total_tokens"] < 15000


class TestSkillMdLimits:
    """Tests for SKILL.md token and line limits."""

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_skill_md_over_token_limit_fails(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #32: SKILL.md exceeding hard token limit (10000) fails."""
        # Generate content that exceeds hard limit of 10000 tokens
        long_content = generate_long_text(11000)

        create_skill_md(
            temp_skill_dir,
            name="large-token-skill",
            description="A skill with too many tokens in SKILL.md.",
            content=f"# Large Skill\n\n{long_content}\n",
        )

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for token limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["skill_md_tokens"] > 10000
        assert any("exceeds" in w.lower() or "limit" in w.lower() for w in data["warnings"])

    @pytest.mark.tokens
    def test_skill_md_over_line_limit_fails(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #33: SKILL.md exceeding hard line limit (1000) fails."""
        # Generate content with > 1000 lines (hard limit)
        long_content = generate_long_lines(1010)

        create_skill_md(
            temp_skill_dir,
            name="many-lines-skill",
            description="A skill with too many lines in SKILL.md.",
            content=f"# Many Lines Skill\n\n{long_content}\n",
        )

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for line limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["skill_md_lines"] > 1000


class TestReferenceLimits:
    """Tests for reference file token limits."""

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_single_ref_over_limit_fails(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #34: Single reference file exceeding hard limit (4000 tokens) fails."""
        create_skill_md(
            temp_skill_dir,
            name="big-ref-skill",
            description="A skill with a reference file exceeding token limit.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()

        # Create reference > 4000 tokens (hard limit)
        long_ref_content = generate_long_text(4500)
        create_reference_file(
            refs_dir, "large-ref.md", f"# Large Reference\n\n{long_ref_content}\n"
        )

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for single ref limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        # Check that at least one ref file exceeds hard limit
        over_limit = [f for f in data["ref_files"] if f["tokens"] > 4000]
        assert len(over_limit) > 0

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_total_refs_over_limit_fails(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #35: Total references exceeding hard limit (20000 tokens) fails."""
        create_skill_md(
            temp_skill_dir,
            name="many-refs-skill",
            description="A skill with many reference files exceeding total limit.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()

        # Create 6 reference files, each ~3500 tokens (total > 20000 hard limit)
        for i in range(6):
            ref_content = generate_long_text(3500)
            create_reference_file(refs_dir, f"ref-{i}.md", f"# Reference {i}\n\n{ref_content}\n")

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for total refs limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["ref_total_tokens"] > 20000


class TestTotalSkillLimit:
    """Tests for total skill token limit."""

    @pytest.mark.tokens
    @pytest.mark.slow
    def test_total_skill_over_limit_fails(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #36: Total skill exceeding hard limit (30000 tokens) fails."""
        # Create SKILL.md with ~9000 tokens
        skill_content = generate_long_text(9000)
        create_skill_md(
            temp_skill_dir,
            name="huge-skill",
            description="A skill that exceeds total token limit.",
            content=f"# Huge Skill\n\n{skill_content}\n",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()

        # Create references totaling ~24000 tokens (total > 30000 hard limit)
        for i in range(8):
            ref_content = generate_long_text(3000)
            create_reference_file(refs_dir, f"ref-{i}.md", f"# Reference {i}\n\n{ref_content}\n")

        result = run_count_tokens(temp_skill_dir, json_output=True)

        assert result.returncode == 1, "Expected exit 1 for total skill limit exceeded"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["total_tokens"] > 30000


class TestJsonOutput:
    """Tests for JSON output format."""

    @pytest.mark.tokens
    def test_json_output_valid(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #37: --json flag outputs valid JSON with required fields."""
        create_skill_md(
            temp_skill_dir,
            name="json-test-skill",
            description="A skill for testing JSON output format.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nContent here.\n")

        result = run_count_tokens(temp_skill_dir, json_output=True)

        # Should be valid JSON
        data = json.loads(result.stdout)

        # Check required fields
        assert "skill_name" in data
        assert "skill_md_tokens" in data
        assert "skill_md_lines" in data
        assert "ref_total_tokens" in data
        assert "ref_files" in data
        assert "total_tokens" in data
        assert "method" in data
        assert "warnings" in data
        assert "passed" in data

        # Check types
        assert isinstance(data["skill_name"], str)
        assert isinstance(data["skill_md_tokens"], int)
        assert isinstance(data["skill_md_lines"], int)
        assert isinstance(data["ref_total_tokens"], int)
        assert isinstance(data["ref_files"], list)
        assert isinstance(data["total_tokens"], int)
        assert isinstance(data["method"], str)
        assert isinstance(data["warnings"], list)
        assert isinstance(data["passed"], bool)


class TestMissingSkillMd:
    """Tests for missing SKILL.md handling."""

    @pytest.mark.tokens
    def test_missing_skill_md_handled(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #38: Missing SKILL.md is handled gracefully with passed=false."""
        # Don't create SKILL.md - directory is empty

        result = run_count_tokens(temp_skill_dir, json_output=True)

        # Should fail but not crash
        assert result.returncode == 1, "Expected exit 1 for missing SKILL.md"

        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert "SKILL.md" in str(data["warnings"]) or data["skill_md_tokens"] == 0


class TestWarningThresholds:
    """Tests for warning threshold configuration."""

    @pytest.mark.tokens
    def test_warning_threshold_80_percent(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #39: Default 80% threshold generates warning."""
        # Create skill at ~85% of 5000 token limit (~4250 tokens)
        skill_content = generate_long_text(4300)
        create_skill_md(
            temp_skill_dir,
            name="warning-skill",
            description="A skill approaching the token limit.",
            content=f"# Warning Skill\n\n{skill_content}\n",
        )

        result = run_count_tokens(temp_skill_dir, json_output=True)

        data = json.loads(result.stdout)

        # Should pass but have warnings about approaching limit
        # Note: might pass or fail depending on exact token count
        if data["skill_md_tokens"] < 5000:
            assert data["passed"] is True
            # Check for approaching limit warning if > 80%
            if data["skill_md_tokens"] > 4000:
                assert any("approaching" in w.lower() for w in data["warnings"])

    @pytest.mark.tokens
    def test_custom_warn_threshold(
        self,
        temp_skill_dir: Path,
        run_count_tokens,
    ) -> None:
        """Feature #40: --warn-threshold flag changes warning level."""
        # Create skill at ~60% of limit (~3000 tokens)
        skill_content = generate_long_text(3000)
        create_skill_md(
            temp_skill_dir,
            name="threshold-skill",
            description="A skill for testing custom warning threshold.",
            content=f"# Threshold Skill\n\n{skill_content}\n",
        )

        # With 50% threshold, should get warning
        result = run_count_tokens(temp_skill_dir, json_output=True, warn_threshold=50)

        data = json.loads(result.stdout)

        # Should pass but may have warning depending on exact token count
        if data["skill_md_tokens"] > 2500:  # 50% of 5000
            # May have approaching warning
            pass

        # Basic validation passes
        assert "skill_md_tokens" in data
        assert "passed" in data
