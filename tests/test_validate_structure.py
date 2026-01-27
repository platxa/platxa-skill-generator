"""Tests for validate-structure.sh script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Valid structure acceptance (Feature #19)
- Missing/empty SKILL.md detection (Features #20-22)
- References directory validation (Features #23-24)
- Scripts directory validation (Features #25-26)
- Hidden files and large files warnings (Features #27-30)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import (
    create_executable_script,
    create_reference_file,
    create_skill_md,
)


class TestValidStructure:
    """Tests for valid structure acceptance."""

    @pytest.mark.structure
    def test_valid_structure_passes(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #19: Complete valid skill directory returns exit code 0."""
        # Create a complete valid skill
        create_skill_md(
            temp_skill_dir,
            name="valid-skill",
            description="A complete valid skill for structure validation testing.",
            tools=["Read", "Write"],
        )

        # Create scripts directory with executable
        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()
        create_executable_script(scripts_dir, "helper.sh")

        # Create references directory with markdown
        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "PASSED" in result.stdout


class TestSkillMdValidation:
    """Tests for SKILL.md file validation."""

    @pytest.mark.structure
    def test_missing_skill_md_fails(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #20: Missing SKILL.md returns exit code 1."""
        # Create directory without SKILL.md
        # temp_skill_dir is already empty

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing SKILL.md"
        assert "SKILL.md" in result.stderr or "not found" in result.stderr.lower()

    @pytest.mark.structure
    def test_empty_skill_md_fails(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #21: Empty SKILL.md returns exit code 1."""
        # Create empty SKILL.md
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for empty SKILL.md"
        assert "empty" in result.stderr.lower() or "ERROR" in result.stderr

    @pytest.mark.structure
    def test_skill_md_no_frontmatter_fails(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #22: SKILL.md without frontmatter returns exit code 1."""
        # Create SKILL.md without frontmatter
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""# My Skill

This skill does things but has no YAML frontmatter.

## Usage

Just use it.
""")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing frontmatter"
        assert "frontmatter" in result.stderr.lower() or "---" in result.stderr


class TestReferencesDirectoryValidation:
    """Tests for references/ directory validation."""

    @pytest.mark.structure
    def test_references_directory_valid(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #23: Valid references/ directory with markdown files passes."""
        create_skill_md(
            temp_skill_dir,
            name="skill-with-refs",
            description="A skill with valid references directory.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nContent here.")
        create_reference_file(refs_dir, "patterns.md", "# Patterns\n\nMore content.")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "reference" in result.stdout.lower()

    @pytest.mark.structure
    def test_empty_references_warns(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #24: Empty references/ directory generates warning."""
        create_skill_md(
            temp_skill_dir,
            name="skill-empty-refs",
            description="A skill with empty references directory.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        # Leave directory empty

        result = run_validate_structure(temp_skill_dir)

        # Should pass but with warning
        assert result.returncode == 0, "Expected exit 0 (warning only)"
        assert "empty" in result.stderr.lower() or "WARN" in result.stderr


class TestScriptsDirectoryValidation:
    """Tests for scripts/ directory validation."""

    @pytest.mark.structure
    def test_scripts_directory_valid(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #25: Valid scripts/ directory with executables passes."""
        create_skill_md(
            temp_skill_dir,
            name="skill-with-scripts",
            description="A skill with valid scripts directory.",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()
        create_executable_script(scripts_dir, "run.sh", "#!/bin/bash\necho 'test'")
        create_executable_script(scripts_dir, "build.sh", "#!/bin/bash\necho 'build'")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        assert "script" in result.stdout.lower()

    @pytest.mark.structure
    def test_non_executable_script_fails(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #26: Non-executable .sh scripts return exit code 1."""
        create_skill_md(
            temp_skill_dir,
            name="skill-bad-scripts",
            description="A skill with non-executable scripts.",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()

        # Create non-executable script
        script = scripts_dir / "run.sh"
        script.write_text("#!/bin/bash\necho 'test'")
        script.chmod(0o644)  # Not executable

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for non-executable script"
        assert "executable" in result.stderr.lower() or "permission" in result.stderr.lower()


class TestUnexpectedFilesValidation:
    """Tests for unexpected files validation."""

    @pytest.mark.structure
    def test_unexpected_root_files_warns(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #27: Unexpected files in root directory generate warning."""
        create_skill_md(
            temp_skill_dir,
            name="skill-extra-files",
            description="A skill with unexpected files in root.",
        )

        # Create unexpected file
        unexpected = temp_skill_dir / "random.txt"
        unexpected.write_text("This file should not be here")

        result = run_validate_structure(temp_skill_dir)

        # Should pass but with warning
        assert result.returncode == 0, "Expected exit 0 (warning only)"
        assert "unexpected" in result.stderr.lower() or "WARN" in result.stderr

    @pytest.mark.structure
    def test_hidden_files_warns(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #28: Hidden files (except .gitkeep) generate warning."""
        create_skill_md(
            temp_skill_dir,
            name="skill-hidden-files",
            description="A skill with hidden files.",
        )

        # Create hidden file
        hidden = temp_skill_dir / ".hidden_config"
        hidden.write_text("hidden content")

        result = run_validate_structure(temp_skill_dir)

        # Should pass but with warning
        assert result.returncode == 0, "Expected exit 0 (warning only)"
        assert "hidden" in result.stderr.lower() or "WARN" in result.stderr


class TestFileSizeValidation:
    """Tests for file size validation."""

    @pytest.mark.structure
    @pytest.mark.slow
    def test_large_files_warns(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #29: Files larger than 100KB generate warning."""
        create_skill_md(
            temp_skill_dir,
            name="skill-large-files",
            description="A skill with large files.",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()

        # Create file > 100KB
        large_file = refs_dir / "large.md"
        large_file.write_text("x" * (101 * 1024))  # 101 KB

        result = run_validate_structure(temp_skill_dir)

        # Should pass but with warning
        assert result.returncode == 0, "Expected exit 0 (warning only)"
        assert "100" in result.stderr or "large" in result.stderr.lower() or "WARN" in result.stderr


class TestGitkeepAllowed:
    """Tests for .gitkeep handling."""

    @pytest.mark.structure
    def test_gitkeep_allowed(
        self,
        temp_skill_dir: Path,
        run_validate_structure,
    ) -> None:
        """Feature #30: .gitkeep files are accepted without warning."""
        create_skill_md(
            temp_skill_dir,
            name="skill-with-gitkeep",
            description="A skill with .gitkeep files.",
        )

        # Create directories with .gitkeep
        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / ".gitkeep").write_text("")

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / ".gitkeep").write_text("")

        result = run_validate_structure(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0. stderr: {result.stderr}"
        # .gitkeep should not trigger hidden file warning
        output = result.stdout + result.stderr
        assert ".gitkeep" not in output or "OK" in output
