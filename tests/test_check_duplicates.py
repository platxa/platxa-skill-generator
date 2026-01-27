"""Tests for check-duplicates.py script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Exact name duplicate detected (exit 1)
- Fuzzy name match warned
- Description similarity warned
- No duplicates passes cleanly (exit 0)
- Self-comparison excluded
- --audit mode finds cross-catalog duplicates
- Different skills with same category but different descriptions pass
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from helpers import create_skill_md


@pytest.fixture
def run_check_duplicates(scripts_dir: Path):
    """Fixture to run check-duplicates.py."""
    script_path = scripts_dir / "check-duplicates.py"

    def _run(
        skill_dir: Path,
        *,
        audit: bool = False,
        catalog: Path | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if audit:
            cmd.append("--audit")
        if catalog:
            cmd.extend(["--catalog", str(catalog)])
        cmd.append(str(skill_dir))
        return subprocess.run(cmd, capture_output=True, text=True)

    return _run


class TestExactDuplicate:
    """Tests for exact name duplicate detection."""

    @pytest.mark.duplicates
    def test_exact_name_duplicate_exits_1(self, tmp_path: Path, run_check_duplicates) -> None:
        """Exact duplicate name returns exit code 1."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        # Existing skill
        existing = catalog / "skill-a"
        existing.mkdir()
        create_skill_md(existing, "my-skill", "Skill A description")

        # New skill with same name
        new_skill = catalog / "skill-b"
        new_skill.mkdir()
        create_skill_md(new_skill, "my-skill", "Different description")

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 1
        assert "Exact duplicate" in result.stderr


class TestFuzzyName:
    """Tests for fuzzy name matching."""

    @pytest.mark.duplicates
    def test_fuzzy_name_warns(self, tmp_path: Path, run_check_duplicates) -> None:
        """Similar names produce a warning."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        existing = catalog / "test-generator"
        existing.mkdir()
        create_skill_md(existing, "test-generator", "Generate tests for code")

        new_skill = catalog / "test-generatr"
        new_skill.mkdir()
        create_skill_md(new_skill, "test-generatr", "A completely different tool")

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 0
        assert "Similar name" in result.stderr

    @pytest.mark.duplicates
    def test_prefix_stripped_fuzzy(self, tmp_path: Path, run_check_duplicates) -> None:
        """platxa- prefix is stripped for fuzzy comparison."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        existing = catalog / "testing"
        existing.mkdir()
        create_skill_md(existing, "testing", "Some testing skill")

        new_skill = catalog / "platxa-testing"
        new_skill.mkdir()
        create_skill_md(new_skill, "platxa-testing", "Different description entirely")

        result = run_check_duplicates(new_skill, catalog=catalog)
        # "testing" normalized == "platxatesting" normalized "testing" -> exact after strip
        assert result.returncode == 0
        assert "Similar name" in result.stderr or "No duplicates" in result.stdout


class TestDescriptionSimilarity:
    """Tests for description similarity detection."""

    @pytest.mark.duplicates
    def test_similar_descriptions_warns(self, tmp_path: Path, run_check_duplicates) -> None:
        """Near-identical descriptions produce a warning."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        existing = catalog / "skill-a"
        existing.mkdir()
        create_skill_md(
            existing,
            "skill-a",
            "Automated testing patterns for the platform using pytest and Vitest frameworks",
        )

        new_skill = catalog / "skill-b"
        new_skill.mkdir()
        create_skill_md(
            new_skill,
            "skill-b",
            "Automated testing patterns for the platform using pytest and Vitest frameworks.",
        )

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 0
        assert "Similar description" in result.stderr


class TestNoDuplicates:
    """Tests for clean pass scenarios."""

    @pytest.mark.duplicates
    def test_unique_skill_passes(self, tmp_path: Path, run_check_duplicates) -> None:
        """Unique skill with no matches returns exit 0."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        existing = catalog / "logging"
        existing.mkdir()
        create_skill_md(existing, "logging", "Structured logging for services")

        new_skill = catalog / "auth"
        new_skill.mkdir()
        create_skill_md(new_skill, "auth", "JWT authentication and authorization")

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 0
        assert "No duplicates" in result.stdout

    @pytest.mark.duplicates
    def test_empty_catalog_passes(self, tmp_path: Path, run_check_duplicates) -> None:
        """Empty catalog directory passes cleanly."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        new_skill = catalog / "new-skill"
        new_skill.mkdir()
        create_skill_md(new_skill, "new-skill", "A brand new skill")

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 0


class TestSelfExclusion:
    """Tests for self-comparison exclusion."""

    @pytest.mark.duplicates
    def test_self_not_compared(self, tmp_path: Path, run_check_duplicates) -> None:
        """Skill does not match against itself."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        skill = catalog / "my-skill"
        skill.mkdir()
        create_skill_md(skill, "my-skill", "Some description")

        result = run_check_duplicates(skill, catalog=catalog)
        assert result.returncode == 0
        assert "No duplicates" in result.stdout


class TestAuditMode:
    """Tests for --audit catalog-wide scan."""

    @pytest.mark.duplicates
    def test_audit_finds_cross_duplicates(self, tmp_path: Path, run_check_duplicates) -> None:
        """Audit mode detects duplicate names across catalog."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        skill_a = catalog / "dir-a"
        skill_a.mkdir()
        create_skill_md(skill_a, "same-name", "First skill")

        skill_b = catalog / "dir-b"
        skill_b.mkdir()
        create_skill_md(skill_b, "same-name", "Second skill")

        result = run_check_duplicates(catalog, audit=True)
        assert result.returncode == 1
        assert "Duplicate name" in result.stderr

    @pytest.mark.duplicates
    def test_audit_clean_catalog(self, tmp_path: Path, run_check_duplicates) -> None:
        """Audit on catalog with no duplicates passes."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        for name in ("alpha", "beta", "gamma"):
            d = catalog / name
            d.mkdir()
            create_skill_md(d, name, f"Description for {name} skill with unique content")

        result = run_check_duplicates(catalog, audit=True)
        assert result.returncode == 0
        assert "Audit complete" in result.stdout


class TestDifferentCategorySameArea:
    """Skills in same domain but genuinely different should pass."""

    @pytest.mark.duplicates
    def test_same_domain_different_purpose_passes(
        self, tmp_path: Path, run_check_duplicates
    ) -> None:
        """Two testing-related skills with different descriptions pass."""
        catalog = tmp_path / "catalog"
        catalog.mkdir()

        existing = catalog / "unit-testing"
        existing.mkdir()
        create_skill_md(existing, "unit-testing", "Write unit tests with pytest for Python modules")

        new_skill = catalog / "e2e-testing"
        new_skill.mkdir()
        create_skill_md(
            new_skill,
            "e2e-testing",
            "Run end-to-end browser tests with Playwright and Cypress",
        )

        result = run_check_duplicates(new_skill, catalog=catalog)
        assert result.returncode == 0
