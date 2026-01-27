"""Tests for validate-skill.sh --profile flag.

Tests cover:
- strict profile rejects skills missing required sections (score < 7)
- spec profile accepts upstream-style skills without sections (score >= 7)
- default profile is strict
- invalid profile name returns error
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import create_skill_md

UPSTREAM_STYLE_CONTENT = """\
This skill creates frontend interfaces with high design quality.

The user provides requirements and the skill generates code.

## Design Thinking

Choose a bold aesthetic direction and implement it.

## Frontend Aesthetics Guidelines

Focus on typography, color, motion, and spatial composition.
"""

STRICT_STYLE_CONTENT = """\
# Test Skill

## Overview

This skill does something useful.

## Workflow

1. Step one
2. Step two

## Examples

```bash
example usage
```

## Output Checklist

- [ ] Item one
- [ ] Item two
"""


class TestProfileStrict:
    """Tests for strict profile (default)."""

    @pytest.mark.profile
    def test_strict_rejects_missing_sections(
        self, temp_skill_dir: Path, run_validate_skill
    ) -> None:
        """Strict profile fails when Overview/Workflow/Examples/Checklist missing."""
        create_skill_md(
            temp_skill_dir,
            name="upstream-skill",
            description="An upstream skill without our required sections.",
            content=UPSTREAM_STYLE_CONTENT,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert result.returncode != 0
        assert "FAIL" in result.stdout

    @pytest.mark.profile
    def test_strict_passes_with_all_sections(
        self, temp_skill_dir: Path, run_validate_skill
    ) -> None:
        """Strict profile passes when all recommended sections present."""
        create_skill_md(
            temp_skill_dir,
            name="complete-skill",
            description="A skill with all required sections for strict validation.",
            content=STRICT_STYLE_CONTENT,
        )
        result = run_validate_skill(temp_skill_dir, profile="strict")
        assert result.returncode == 0
        assert "PASS" in result.stdout


class TestProfileSpec:
    """Tests for spec profile (agentskills.io compliance)."""

    @pytest.mark.profile
    def test_spec_accepts_upstream_style(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """Spec profile passes upstream-style skills without our sections."""
        create_skill_md(
            temp_skill_dir,
            name="upstream-skill",
            description="An upstream skill without our required sections.",
            content=UPSTREAM_STYLE_CONTENT,
        )
        result = run_validate_skill(temp_skill_dir, profile="spec")
        assert result.returncode == 0
        assert "PASS" in result.stdout

    @pytest.mark.profile
    def test_spec_shows_info_not_warning(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """Spec profile shows INFO for missing sections, not warnings."""
        create_skill_md(
            temp_skill_dir,
            name="upstream-skill",
            description="An upstream skill without our required sections.",
            content=UPSTREAM_STYLE_CONTENT,
        )
        result = run_validate_skill(temp_skill_dir, profile="spec")
        assert "INFO" in result.stdout
        assert "WARN" not in result.stdout or "Warnings: 0" in result.stdout


class TestProfileDefault:
    """Tests for default behavior (no --profile flag)."""

    @pytest.mark.profile
    def test_default_is_strict(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """No --profile flag defaults to strict behavior."""
        create_skill_md(
            temp_skill_dir,
            name="upstream-skill",
            description="An upstream skill without our required sections.",
            content=UPSTREAM_STYLE_CONTENT,
        )
        # No profile argument = default
        result = run_validate_skill(temp_skill_dir)
        assert result.returncode != 0
        assert "FAIL" in result.stdout


class TestProfileInvalid:
    """Tests for invalid profile names."""

    @pytest.mark.profile
    def test_invalid_profile_errors(self, temp_skill_dir: Path, run_validate_skill) -> None:
        """Invalid profile name produces error."""
        create_skill_md(
            temp_skill_dir,
            name="test-skill",
            description="A test skill.",
            content="# Content\n",
        )
        result = run_validate_skill(temp_skill_dir, profile="invalid")
        assert result.returncode != 0
        assert "Invalid profile" in result.stderr
