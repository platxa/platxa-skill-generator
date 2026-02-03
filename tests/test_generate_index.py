"""Tests for generate-index.py — index.json structure, token counts, and categories.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml
from helpers import create_reference_file, create_skill_md


@pytest.fixture
def run_generate_index(scripts_dir: Path):
    """Fixture to run generate-index.py via subprocess."""
    script_path = scripts_dir / "generate-index.py"

    def _run(
        skills_dir: Path,
        *,
        pretty: bool = True,
        output: Path | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if pretty:
            cmd.append("--pretty")
        if output:
            cmd.extend(["-o", str(output)])
        cmd.append(str(skills_dir))
        return subprocess.run(cmd, capture_output=True, text=True)

    return _run


def _make_skills_dir(
    base: Path,
    skills: list[dict],
    manifest_skills: dict | None = None,
) -> Path:
    """Create a skills/ directory with skill subdirs and manifest.yaml."""
    skills_dir = base / "skills"
    skills_dir.mkdir(exist_ok=True)

    for skill in skills:
        name = skill["name"]
        desc = skill.get("description", f"Description for {name}")
        tools = skill.get("tools")
        sd = skills_dir / name
        sd.mkdir(exist_ok=True)
        create_skill_md(sd, name, desc, tools=tools)

    if manifest_skills is None:
        manifest_skills = {
            s["name"]: {
                "local": True,
                "tier": 0,
                "category": s.get("category", "general"),
            }
            for s in skills
        }

    (skills_dir / "manifest.yaml").write_text(
        yaml.dump({"version": "1.0", "skills": manifest_skills})
    )
    return skills_dir


# ── Top-level index structure ─────────────────────────────────────


class TestIndexTopLevel:
    """Tests for the top-level index.json structure."""

    @pytest.mark.index
    def test_version_and_required_keys(self, tmp_path: Path, run_generate_index) -> None:
        """Index contains version, generated_at, skills_count, skills, categories."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "skill-a"}, {"name": "skill-b"}])
        result = run_generate_index(skills_dir)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        index = json.loads(result.stdout)
        assert index["version"] == "1.0.0"
        assert "generated_at" in index
        assert index["skills_count"] == 2
        assert "skills" in index
        assert "categories" in index

    @pytest.mark.index
    def test_generated_at_is_iso_format(self, tmp_path: Path, run_generate_index) -> None:
        """generated_at is ISO 8601 with trailing Z."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "s"}])
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        ts = index["generated_at"]
        assert ts.endswith("Z")
        assert "T" in ts
        assert len(ts) == 20

    @pytest.mark.index
    def test_skills_count_matches_entries(self, tmp_path: Path, run_generate_index) -> None:
        """skills_count equals the number of entries in skills dict."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "a"}, {"name": "b"}, {"name": "c"}])
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills_count"] == 3
        assert len(index["skills"]) == 3

    @pytest.mark.index
    def test_skills_sorted_alphabetically(self, tmp_path: Path, run_generate_index) -> None:
        """Skill keys are sorted alphabetically."""
        skills_dir = _make_skills_dir(
            tmp_path, [{"name": "zebra"}, {"name": "alpha"}, {"name": "middle"}]
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        skill_names = list(index["skills"].keys())
        assert skill_names == sorted(skill_names)


# ── Skill entry fields ────────────────────────────────────────────


class TestSkillEntries:
    """Tests for individual skill entry content."""

    @pytest.mark.index
    def test_entry_has_required_fields(self, tmp_path: Path, run_generate_index) -> None:
        """Each entry has name, description, category, tier, source, token_counts."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "test-skill"}])
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        entry = index["skills"]["test-skill"]
        assert entry["name"] == "test-skill"
        assert entry["description"] == "Description for test-skill"
        assert entry["category"] == "general"
        assert entry["tier"] == 0
        assert entry["source"] == "local"
        assert "token_counts" in entry

    @pytest.mark.index
    def test_token_counts_structure(self, tmp_path: Path, run_generate_index) -> None:
        """token_counts contains skill_md, references, total as integers."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "my-skill"}])
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        tc = index["skills"]["my-skill"]["token_counts"]
        assert "skill_md" in tc
        assert "references" in tc
        assert "total" in tc
        assert isinstance(tc["skill_md"], int)
        assert isinstance(tc["references"], int)
        assert isinstance(tc["total"], int)
        assert tc["total"] >= tc["skill_md"]

    @pytest.mark.index
    def test_token_counts_are_positive(self, tmp_path: Path, run_generate_index) -> None:
        """skill_md tokens are positive for a skill with content."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "my-skill"}])
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        tc = index["skills"]["my-skill"]["token_counts"]
        assert tc["skill_md"] > 0
        assert tc["total"] > 0

    @pytest.mark.index
    def test_manifest_overrides_category_tier_source(
        self, tmp_path: Path, run_generate_index
    ) -> None:
        """Manifest values override defaults for category, tier, source."""
        manifest_skills = {
            "test-skill": {"local": True, "tier": 2, "category": "frontend"},
        }
        skills_dir = _make_skills_dir(
            tmp_path,
            [{"name": "test-skill"}],
            manifest_skills=manifest_skills,
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        entry = index["skills"]["test-skill"]
        assert entry["category"] == "frontend"
        assert entry["tier"] == 2
        assert entry["source"] == "local"

    @pytest.mark.index
    def test_external_source_from_manifest(self, tmp_path: Path, run_generate_index) -> None:
        """Non-local manifest entry produces the specified source."""
        manifest_skills = {
            "test-skill": {"source": "anthropic", "tier": 1, "category": "devtools"},
        }
        skills_dir = _make_skills_dir(
            tmp_path,
            [{"name": "test-skill"}],
            manifest_skills=manifest_skills,
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills"]["test-skill"]["source"] == "anthropic"

    @pytest.mark.index
    def test_includes_allowed_tools_from_tools_field(
        self, tmp_path: Path, run_generate_index
    ) -> None:
        """Entry includes allowed_tools when SKILL.md has tools: field."""
        skills_dir = _make_skills_dir(
            tmp_path,
            [{"name": "tool-skill", "tools": ["Read", "Bash"]}],
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills"]["tool-skill"]["allowed_tools"] == ["Read", "Bash"]

    @pytest.mark.index
    def test_includes_allowed_tools_from_allowed_tools_field(
        self, tmp_path: Path, run_generate_index
    ) -> None:
        """Entry works with allowed-tools: field name in frontmatter."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "at-skill"}])
        # Overwrite SKILL.md with allowed-tools: syntax
        skill_md = skills_dir / "at-skill" / "SKILL.md"
        skill_md.write_text(
            "---\nname: at-skill\ndescription: d\n"
            "allowed-tools:\n  - Grep\n  - Write\n---\n\n# Content\n"
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills"]["at-skill"]["allowed_tools"] == ["Grep", "Write"]

    @pytest.mark.index
    def test_includes_sha_and_ref(self, tmp_path: Path, run_generate_index) -> None:
        """Entry includes sha and ref when present in manifest."""
        manifest_skills = {
            "test-skill": {
                "source": "anthropic",
                "ref": "main",
                "sha": "abc123",
                "tier": 1,
                "category": "devtools",
            },
        }
        skills_dir = _make_skills_dir(
            tmp_path,
            [{"name": "test-skill"}],
            manifest_skills=manifest_skills,
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        entry = index["skills"]["test-skill"]
        assert entry["sha"] == "abc123"
        assert entry["ref"] == "main"

    @pytest.mark.index
    def test_includes_compatibility(self, tmp_path: Path, run_generate_index) -> None:
        """Entry includes compatibility when present in manifest."""
        manifest_skills = {
            "test-skill": {
                "local": True,
                "tier": 0,
                "category": "infra",
                "compatibility": "Requires kubectl, helm",
            },
        }
        skills_dir = _make_skills_dir(
            tmp_path,
            [{"name": "test-skill"}],
            manifest_skills=manifest_skills,
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills"]["test-skill"]["compatibility"] == "Requires kubectl, helm"

    @pytest.mark.index
    def test_includes_metadata_from_frontmatter(self, tmp_path: Path, run_generate_index) -> None:
        """Entry includes metadata when present in SKILL.md frontmatter."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "meta-skill"}])
        # Overwrite SKILL.md with metadata block
        skill_md = skills_dir / "meta-skill" / "SKILL.md"
        skill_md.write_text(
            "---\nname: meta-skill\ndescription: d\n"
            "metadata:\n  version: '1.0'\n  author: Test\n---\n\n# Content\n"
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        entry = index["skills"]["meta-skill"]
        assert entry["metadata"] == {"version": "1.0", "author": "Test"}

    @pytest.mark.index
    def test_references_contribute_to_token_count(self, tmp_path: Path, run_generate_index) -> None:
        """References directory content adds to total token count."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "ref-skill"}])
        refs_dir = skills_dir / "ref-skill" / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nReference content here.\n")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        tc = index["skills"]["ref-skill"]["token_counts"]
        assert tc["references"] > 0
        assert tc["total"] > tc["skill_md"]


# ── Category aggregation ──────────────────────────────────────────


class TestCategoryAggregation:
    """Tests for category counts in the index."""

    @pytest.mark.index
    def test_category_counts(self, tmp_path: Path, run_generate_index) -> None:
        """Categories dict aggregates skill counts correctly."""
        manifest_skills = {
            "front-1": {"local": True, "tier": 0, "category": "frontend"},
            "front-2": {"local": True, "tier": 0, "category": "frontend"},
            "back-1": {"local": True, "tier": 0, "category": "backend"},
        }
        skills_dir = _make_skills_dir(
            tmp_path,
            [
                {"name": "front-1", "category": "frontend"},
                {"name": "front-2", "category": "frontend"},
                {"name": "back-1", "category": "backend"},
            ],
            manifest_skills=manifest_skills,
        )
        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["categories"]["frontend"] == 2
        assert index["categories"]["backend"] == 1


# ── Edge cases ────────────────────────────────────────────────────


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.index
    def test_empty_skills_directory(self, tmp_path: Path, run_generate_index) -> None:
        """Empty skills directory produces zero skills and categories."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "manifest.yaml").write_text(yaml.dump({"version": "1.0", "skills": {}}))

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills_count"] == 0
        assert index["skills"] == {}
        assert index["categories"] == {}

    @pytest.mark.index
    def test_skips_directories_without_skill_md(self, tmp_path: Path, run_generate_index) -> None:
        """Directories without SKILL.md are not included."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "valid-skill"}])
        (skills_dir / "not-a-skill").mkdir()
        (skills_dir / "not-a-skill" / "README.md").write_text("Not a skill")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills_count"] == 1
        assert "not-a-skill" not in index["skills"]

    @pytest.mark.index
    def test_skips_special_directories(self, tmp_path: Path, run_generate_index) -> None:
        """overrides and __pycache__ directories are skipped."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "real-skill"}])
        for name in ("overrides", "__pycache__"):
            d = skills_dir / name
            d.mkdir()
            (d / "SKILL.md").write_text("---\nname: fake\ndescription: d\n---\n")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills_count"] == 1
        assert "overrides" not in index["skills"]
        assert "__pycache__" not in index["skills"]

    @pytest.mark.index
    def test_skips_files_at_root(self, tmp_path: Path, run_generate_index) -> None:
        """Non-directory entries at root level are ignored."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "only-skill"}])
        (skills_dir / "README.md").write_text("# README")
        (skills_dir / "index.json").write_text("{}")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert index["skills_count"] == 1

    @pytest.mark.index
    def test_missing_name_in_frontmatter_skipped(self, tmp_path: Path, run_generate_index) -> None:
        """Skill with SKILL.md but no name in frontmatter is skipped."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "valid"}])
        no_name = skills_dir / "no-name"
        no_name.mkdir()
        (no_name / "SKILL.md").write_text("---\ndescription: no name\n---\n")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert "no-name" not in index["skills"]
        assert index["skills_count"] == 1

    @pytest.mark.index
    def test_missing_frontmatter_skipped(self, tmp_path: Path, run_generate_index) -> None:
        """Skill with SKILL.md but no frontmatter delimiters is skipped."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "valid"}])
        no_fm = skills_dir / "no-frontmatter"
        no_fm.mkdir()
        (no_fm / "SKILL.md").write_text("# No frontmatter\n\nJust content.\n")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert "no-frontmatter" not in index["skills"]

    @pytest.mark.index
    def test_empty_frontmatter_skipped(self, tmp_path: Path, run_generate_index) -> None:
        """Skill with empty frontmatter (---\\n---) is skipped."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "valid"}])
        empty_fm = skills_dir / "empty-fm"
        empty_fm.mkdir()
        (empty_fm / "SKILL.md").write_text("---\n---\n\nContent\n")

        result = run_generate_index(skills_dir)
        index = json.loads(result.stdout)

        assert "empty-fm" not in index["skills"]


# ── Output modes ──────────────────────────────────────────────────


class TestOutputModes:
    """Tests for output file and formatting options."""

    @pytest.mark.index
    def test_output_to_file(self, tmp_path: Path, run_generate_index) -> None:
        """-o flag writes JSON to specified file."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "s"}])
        output_path = tmp_path / "out" / "index.json"

        result = run_generate_index(skills_dir, output=output_path)
        assert result.returncode == 0

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["skills_count"] == 1

    @pytest.mark.index
    def test_stdout_is_valid_json(self, tmp_path: Path, run_generate_index) -> None:
        """Default output to stdout is valid parseable JSON."""
        skills_dir = _make_skills_dir(tmp_path, [{"name": "s"}])

        result = run_generate_index(skills_dir, pretty=False)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "version" in data
