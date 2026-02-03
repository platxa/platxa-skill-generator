"""Tests for generate-badges.py — SVG trust badge generation.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from helpers import create_skill_md


@pytest.fixture
def run_generate_badges(scripts_dir: Path):
    """Fixture to run generate-badges.py via subprocess."""
    script_path = scripts_dir / "generate-badges.py"

    def _run(
        skills_dir: Path,
        output_dir: Path | None = None,
        *,
        json_output: bool = False,
        dry_run: bool = False,
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path), "--skills-dir", str(skills_dir)]
        if output_dir is not None:
            cmd.extend(["-o", str(output_dir)])
        if json_output:
            cmd.append("--json")
        if dry_run:
            cmd.append("--dry-run")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    return _run


def _create_minimal_skill(base: Path, name: str, description: str = "") -> Path:
    """Create a minimal skill directory with valid SKILL.md."""
    skill_dir = base / name
    skill_dir.mkdir(parents=True)
    desc = description or f"A skill named {name} for testing badge generation"
    create_skill_md(
        skill_dir,
        name=name,
        description=desc,
        tools=["Read", "Write", "Bash"],
        content=f"# {name.replace('-', ' ').title()}\n\nInstructions for {name}.\n\n## Usage\n\nUse this skill.\n",
    )
    return skill_dir


class TestGenerateBadgeSvg:
    """Tests for SVG badge generation output format."""

    def test_badge_is_valid_svg(self, temp_skill_dir: Path, run_generate_badges):
        """Generated badges are valid SVG files."""
        _create_minimal_skill(temp_skill_dir, "my-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)

        badge = out_dir / "my-skill.svg"
        assert badge.exists(), "Badge SVG not created"
        content = badge.read_text()
        assert content.startswith("<svg"), "Not a valid SVG"
        assert "</svg>" in content, "SVG not closed"
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_badge_has_accessibility(self, temp_skill_dir: Path, run_generate_badges):
        """Badges include accessibility attributes."""
        _create_minimal_skill(temp_skill_dir, "acc-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)

        content = (out_dir / "acc-skill.svg").read_text()
        assert 'role="img"' in content
        assert "<title>" in content
        assert 'aria-label="' in content

    def test_badge_contains_trust_label(self, temp_skill_dir: Path, run_generate_badges):
        """Badge SVG text includes 'trust' label."""
        _create_minimal_skill(temp_skill_dir, "label-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)

        content = (out_dir / "label-skill.svg").read_text()
        assert "trust" in content


class TestStaticBadgeTemplates:
    """Tests for the static per-level badge templates."""

    def test_creates_all_level_templates(self, temp_skill_dir: Path, run_generate_badges):
        """Static badge templates are created for all four trust levels."""
        _create_minimal_skill(temp_skill_dir, "any-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)

        for level in ("verified", "reviewed", "unverified", "flagged"):
            template = out_dir / f"_{level}.svg"
            assert template.exists(), f"Missing static template: _{level}.svg"
            content = template.read_text()
            assert "<svg" in content
            assert level.capitalize() in content

    def test_verified_badge_is_green(self, temp_skill_dir: Path, run_generate_badges):
        """Verified badge template uses green color."""
        _create_minimal_skill(temp_skill_dir, "t-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)
        content = (out_dir / "_verified.svg").read_text()
        assert "#4c1" in content

    def test_flagged_badge_is_red(self, temp_skill_dir: Path, run_generate_badges):
        """Flagged badge template uses red color."""
        _create_minimal_skill(temp_skill_dir, "t-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)
        content = (out_dir / "_flagged.svg").read_text()
        assert "#e05d44" in content

    def test_reviewed_badge_is_blue(self, temp_skill_dir: Path, run_generate_badges):
        """Reviewed badge template uses blue color."""
        _create_minimal_skill(temp_skill_dir, "t-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)
        content = (out_dir / "_reviewed.svg").read_text()
        assert "#007ec6" in content

    def test_unverified_badge_is_yellow(self, temp_skill_dir: Path, run_generate_badges):
        """Unverified badge template uses yellow color."""
        _create_minimal_skill(temp_skill_dir, "t-skill")
        out_dir = temp_skill_dir / "badges"
        run_generate_badges(temp_skill_dir, out_dir)
        content = (out_dir / "_unverified.svg").read_text()
        assert "#dfb317" in content


class TestJsonOutput:
    """Tests for --json output mode."""

    def test_json_output_structure(self, temp_skill_dir: Path, run_generate_badges):
        """JSON output contains expected top-level keys."""
        _create_minimal_skill(temp_skill_dir, "json-skill")
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "total" in data
        assert "badges" in data
        assert "skills" in data
        assert "output_dir" in data

    def test_json_skills_have_badge_and_score(self, temp_skill_dir: Path, run_generate_badges):
        """Each skill in JSON output has name, score, and badge."""
        _create_minimal_skill(temp_skill_dir, "scored-skill")
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        data = json.loads(result.stdout)
        assert data["total"] == 1
        skill = data["skills"][0]
        assert skill["name"] == "scored-skill"
        assert isinstance(skill["score"], (int, float))
        assert skill["badge"] in ("Verified", "Reviewed", "Unverified", "Flagged")

    def test_json_badge_counts(self, temp_skill_dir: Path, run_generate_badges):
        """Badge counts in JSON match expected levels."""
        _create_minimal_skill(temp_skill_dir, "count-skill")
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        data = json.loads(result.stdout)
        badges = data["badges"]
        assert set(badges.keys()) == {"Verified", "Reviewed", "Unverified", "Flagged"}
        total_badges = sum(badges.values())
        assert total_badges == data["total"]


class TestDryRun:
    """Tests for --dry-run mode."""

    def test_dry_run_no_files_written(self, temp_skill_dir: Path, run_generate_badges):
        """Dry run does not create any SVG files."""
        _create_minimal_skill(temp_skill_dir, "dry-skill")
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, dry_run=True)

        assert result.returncode == 0
        assert not out_dir.exists() or len(list(out_dir.glob("*.svg"))) == 0

    def test_dry_run_json_still_works(self, temp_skill_dir: Path, run_generate_badges):
        """Dry run with --json still produces valid output."""
        _create_minimal_skill(temp_skill_dir, "dry-json")
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True, dry_run=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 1


class TestMultipleSkills:
    """Tests with multiple skills in the directory."""

    def test_generates_badge_per_skill(self, temp_skill_dir: Path, run_generate_badges):
        """Each skill gets its own SVG badge."""
        for name in ("alpha-skill", "beta-skill", "gamma-skill"):
            _create_minimal_skill(temp_skill_dir, name)
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 3
        for name in ("alpha-skill", "beta-skill", "gamma-skill"):
            assert (out_dir / f"{name}.svg").exists()

    def test_empty_skills_dir(self, temp_skill_dir: Path, run_generate_badges):
        """Empty skills directory produces zero badges."""
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_nonexistent_skills_dir(self, temp_skill_dir: Path, run_generate_badges):
        """Nonexistent skills directory returns error."""
        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir / "nope", out_dir)
        assert result.returncode != 0

    def test_directory_without_skill_md_skipped(self, temp_skill_dir: Path, run_generate_badges):
        """Directories without SKILL.md are silently skipped."""
        (temp_skill_dir / "not-a-skill").mkdir()
        (temp_skill_dir / "not-a-skill" / "README.md").write_text("# Not a skill")
        _create_minimal_skill(temp_skill_dir, "real-skill")

        out_dir = temp_skill_dir / "badges"
        result = run_generate_badges(temp_skill_dir, out_dir, json_output=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 1
        assert data["skills"][0]["name"] == "real-skill"

    def test_creates_output_directory(self, temp_skill_dir: Path, run_generate_badges):
        """Output directory is created if it does not exist."""
        _create_minimal_skill(temp_skill_dir, "mkdir-skill")
        out_dir = temp_skill_dir / "deep" / "nested" / "badges"
        assert not out_dir.exists()

        result = run_generate_badges(temp_skill_dir, out_dir)
        assert result.returncode == 0
        assert out_dir.exists()
        assert (out_dir / "mkdir-skill.svg").exists()
