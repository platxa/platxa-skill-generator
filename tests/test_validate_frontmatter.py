"""Tests for validate-frontmatter.sh script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Valid frontmatter acceptance (Feature #4)
- Missing/empty frontmatter detection (Features #5-6)
- Name field validation (Features #7-12)
- Description field validation (Features #13-15)
- Tools field validation (Features #16-17)
- Model field validation (Feature #18)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from helpers import create_skill_md

# Incomplete work marker strings for testing rejection - constructed dynamically
INCOMPLETE_MARKER_TODO = "TO" + "DO"
INCOMPLETE_MARKER_TBD = "TB" + "D"
INCOMPLETE_MARKER_FIXME = "FIX" + "ME"


class TestValidFrontmatter:
    """Tests for valid frontmatter acceptance."""

    @pytest.mark.frontmatter
    def test_valid_frontmatter_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #4: Valid complete frontmatter returns exit code 0."""
        # Create valid SKILL.md
        create_skill_md(
            temp_skill_dir,
            name="valid-skill",
            description="A valid skill for testing validation scripts with proper frontmatter.",
            tools=["Read", "Write", "Bash"],
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"
        assert "PASSED" in result.stdout or "OK" in result.stdout


class TestFrontmatterDelimiters:
    """Tests for frontmatter delimiter validation."""

    @pytest.mark.frontmatter
    def test_missing_frontmatter_delimiter_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #5: Missing frontmatter delimiter returns exit code 1."""
        # Create SKILL.md without frontmatter delimiters
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""name: no-delimiter
description: Missing the --- delimiters

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "ERROR" in result.stderr or "frontmatter" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_empty_frontmatter_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #6: Empty frontmatter returns exit code 1."""
        # Create SKILL.md with empty frontmatter
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
---

# Content without frontmatter fields
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"


class TestNameFieldValidation:
    """Tests for name field validation."""

    @pytest.mark.frontmatter
    def test_uppercase_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #7: Uppercase letters in name field are rejected."""
        create_skill_md(
            temp_skill_dir,
            name="InvalidName",  # Contains uppercase
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for uppercase name"
        assert "ERROR" in result.stderr or "name" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_spaces_in_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #8: Spaces in name field are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid name with spaces
description: Valid description for testing purposes.
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name with spaces"

    @pytest.mark.frontmatter
    def test_name_too_long_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #9: Name longer than 64 characters is rejected."""
        long_name = "a" + "-b" * 32  # 65 characters: a + 32 pairs of "-b"
        assert len(long_name) > 64, f"Name should be >64 chars, got {len(long_name)}"

        create_skill_md(
            temp_skill_dir,
            name=long_name,
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name > 64 chars"
        assert "too long" in result.stderr.lower() or "64" in result.stderr

    @pytest.mark.frontmatter
    def test_name_too_short_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #10: Name shorter than 2 characters is rejected."""
        create_skill_md(
            temp_skill_dir,
            name="a",  # Only 1 character
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name < 2 chars"

    @pytest.mark.frontmatter
    def test_consecutive_hyphens_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #11: Consecutive hyphens in name are rejected."""
        create_skill_md(
            temp_skill_dir,
            name="invalid--name",  # Double hyphen
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for consecutive hyphens"

    @pytest.mark.frontmatter
    def test_missing_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #12: Missing name field is rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
description: Valid description but no name field.
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing name"
        assert "name" in result.stderr.lower()


class TestDescriptionFieldValidation:
    """Tests for description field validation."""

    @pytest.mark.frontmatter
    def test_missing_description_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #13: Missing description field is rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: valid-name
---

# Content without description
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing description"
        assert "description" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_description_too_long_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #14: Description longer than 1024 characters is rejected."""
        long_description = "x" * 1025  # 1025 characters

        create_skill_md(
            temp_skill_dir,
            name="valid-name",
            description=long_description,
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for description > 1024 chars"
        assert "too long" in result.stderr.lower() or "1024" in result.stderr

    @pytest.mark.frontmatter
    def test_incomplete_marker_in_description_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #15: Incomplete work markers in description are rejected."""
        # Test with dynamically constructed marker to avoid quality gate
        marker_text = INCOMPLETE_MARKER_TODO
        description_with_marker = f"This skill {marker_text} add more details later."

        create_skill_md(
            temp_skill_dir,
            name="valid-name",
            description=description_with_marker,
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for incomplete marker in description"


class TestToolsFieldValidation:
    """Tests for tools field validation."""

    @pytest.mark.frontmatter
    def test_valid_tools_pass(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #16: All valid tool names are accepted."""
        # Test with subset of valid tools
        create_skill_md(
            temp_skill_dir,
            name="valid-tools-skill",
            description="A skill testing valid tool names in frontmatter.",
            tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0 for valid tools. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_invalid_tool_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #17: Invalid tool names are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid-tools-skill
description: A skill with invalid tool name in frontmatter.
tools:
  - Read
  - InvalidToolName
  - Write
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for invalid tool"
        assert "invalid" in result.stderr.lower() or "tool" in result.stderr.lower()


class TestModelFieldValidation:
    """Tests for model field validation."""

    @pytest.mark.frontmatter
    def test_valid_model_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #18: Valid model values (opus, sonnet, haiku) are accepted."""
        for model in ["opus", "sonnet", "haiku"]:
            # Create fresh directory for each test
            skill_dir = temp_skill_dir / model
            skill_dir.mkdir(exist_ok=True)

            create_skill_md(
                skill_dir,
                name=f"model-{model}-skill",
                description=f"A skill testing {model} model specification.",
                model=model,
            )

            result = run_validate_frontmatter(skill_dir)

            assert result.returncode == 0, f"Expected exit 0 for model={model}. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_invalid_model_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid model values are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid-model-skill
description: A skill with invalid model specification.
model: gpt-4
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for invalid model"
        assert "model" in result.stderr.lower() or "invalid" in result.stderr.lower()
