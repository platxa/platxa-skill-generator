"""Tests for regenerate-skill.sh — argument parsing, validation, and error handling.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations. Tests focus on the validation layer which exits
before any external tool invocation.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from helpers import create_skill_md


@pytest.fixture
def regenerate_script(scripts_dir: Path) -> Path:
    """Path to the regenerate-skill.sh script."""
    return scripts_dir / "regenerate-skill.sh"


def _run_regenerate(
    script: Path,
    args: list[str],
    *,
    env_override: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run regenerate-skill.sh with given arguments."""
    env = {**os.environ, "TERM": "dumb"}
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["bash", str(script), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _create_upstream_skill(base: Path, name: str = "upstream-skill") -> Path:
    """Create a minimal upstream skill directory with SKILL.md."""
    skill_dir = base / name
    skill_dir.mkdir(parents=True)
    create_skill_md(skill_dir, name, f"An upstream {name} for testing.")
    return skill_dir


def _create_intent_file(base: Path, name: str = "test-skill") -> Path:
    """Create a valid intent JSON file."""
    intent = {
        "skill_name": name,
        "skill_type": "guide",
        "description": f"A {name} for regeneration testing",
        "domain": "testing",
        "gaps": ["missing examples", "no reference docs"],
    }
    intent_file = base / f"{name}.json"
    intent_file.write_text(json.dumps(intent, indent=2))
    return intent_file


# ── Help and usage ───────────────────────────────────────────────


class TestHelpAndUsage:
    """Tests for help flag and usage output."""

    @pytest.mark.regenerate
    def test_help_flag_shows_usage(self, regenerate_script: Path) -> None:
        """--help shows usage information and exits 0."""
        result = _run_regenerate(regenerate_script, ["--help"])
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()

    @pytest.mark.regenerate
    def test_short_help_flag(self, regenerate_script: Path) -> None:
        """-h also shows usage information and exits 0."""
        result = _run_regenerate(regenerate_script, ["-h"])
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()

    @pytest.mark.regenerate
    def test_help_lists_all_options(self, regenerate_script: Path) -> None:
        """Usage output documents all supported options."""
        result = _run_regenerate(regenerate_script, ["--help"])
        assert result.returncode == 0
        assert "--dry-run" in result.stdout
        assert "--intent-file" in result.stdout
        assert "--output-dir" in result.stdout
        assert "--batch" in result.stdout

    @pytest.mark.regenerate
    def test_help_lists_examples(self, regenerate_script: Path) -> None:
        """Usage output includes example commands."""
        result = _run_regenerate(regenerate_script, ["--help"])
        assert result.returncode == 0
        assert "examples" in result.stdout.lower()
        assert "regenerate-skill.sh" in result.stdout


# ── Input validation ─────────────────────────────────────────────


class TestInputValidation:
    """Tests for argument parsing and input validation error paths."""

    @pytest.mark.regenerate
    def test_no_arguments_shows_error_and_usage(self, regenerate_script: Path) -> None:
        """Running without arguments prints error to stderr and shows usage."""
        result = _run_regenerate(regenerate_script, [])
        assert "provide" in result.stderr.lower() or "error" in result.stderr.lower()
        assert "usage" in result.stdout.lower()

    @pytest.mark.regenerate
    def test_unknown_option_fails(self, regenerate_script: Path) -> None:
        """Unknown option produces error and non-zero exit."""
        result = _run_regenerate(regenerate_script, ["--nonexistent-flag"])
        assert result.returncode != 0
        assert "unknown option" in result.stderr.lower() or "error" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_skill_dir_and_intent_file_mutually_exclusive(
        self, regenerate_script: Path, tmp_path: Path
    ) -> None:
        """Cannot use both <skill-dir> and --intent-file together."""
        skill_dir = _create_upstream_skill(tmp_path)
        intent_file = _create_intent_file(tmp_path)
        result = _run_regenerate(
            regenerate_script, [str(skill_dir), "--intent-file", str(intent_file)]
        )
        assert result.returncode != 0
        assert "cannot use both" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_missing_skill_md_in_directory(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Skill directory without SKILL.md produces error."""
        empty_dir = tmp_path / "no-skill-md"
        empty_dir.mkdir()
        result = _run_regenerate(regenerate_script, [str(empty_dir)])
        assert result.returncode != 0
        assert "skill.md not found" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_nonexistent_skill_directory(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Nonexistent skill directory path produces error."""
        result = _run_regenerate(regenerate_script, [str(tmp_path / "does-not-exist")])
        assert result.returncode != 0
        # Either "SKILL.md not found" or a generic error
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_nonexistent_intent_file(self, regenerate_script: Path, tmp_path: Path) -> None:
        """--intent-file pointing to nonexistent file produces error."""
        result = _run_regenerate(
            regenerate_script, ["--intent-file", str(tmp_path / "missing.json")]
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_intent_file_error_mentions_path(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Error for missing intent file includes the file path."""
        missing = tmp_path / "nonexistent-intent.json"
        result = _run_regenerate(regenerate_script, ["--intent-file", str(missing)])
        assert result.returncode != 0
        assert "nonexistent-intent.json" in result.stderr

    @pytest.mark.regenerate
    def test_skill_dir_error_mentions_path(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Error for missing SKILL.md includes the directory path."""
        no_skill = tmp_path / "my-broken-skill"
        no_skill.mkdir()
        result = _run_regenerate(regenerate_script, [str(no_skill)])
        assert result.returncode != 0
        assert "my-broken-skill" in result.stderr


# ── Environment checks ───────────────────────────────────────────


class TestEnvironmentChecks:
    """Tests for environment dependency validation."""

    @pytest.mark.regenerate
    def test_missing_claude_cli_fails(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Script fails when claude CLI is not on PATH."""
        skill_dir = _create_upstream_skill(tmp_path)
        # Run with a minimal PATH that excludes claude
        result = _run_regenerate(
            regenerate_script,
            [str(skill_dir)],
            env_override={"PATH": "/usr/bin:/bin"},
        )
        assert result.returncode != 0
        assert "claude" in result.stderr.lower()
        assert "not found" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_missing_claude_for_intent_mode(self, regenerate_script: Path, tmp_path: Path) -> None:
        """Intent-file mode also requires claude CLI on PATH."""
        intent_file = _create_intent_file(tmp_path)
        result = _run_regenerate(
            regenerate_script,
            ["--intent-file", str(intent_file)],
            env_override={"PATH": "/usr/bin:/bin"},
        )
        assert result.returncode != 0
        assert "claude" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_missing_claude_for_batch_mode(self, regenerate_script: Path) -> None:
        """Batch mode also requires claude CLI on PATH."""
        result = _run_regenerate(
            regenerate_script,
            ["--batch"],
            env_override={"PATH": "/usr/bin:/bin"},
        )
        assert result.returncode != 0
        assert "claude" in result.stderr.lower()


# ── Dry-run flag parsing ─────────────────────────────────────────


class TestDryRunFlagParsing:
    """Tests that --dry-run is accepted alongside valid inputs."""

    @pytest.mark.regenerate
    def test_dry_run_with_missing_skill_md_still_validates(
        self, regenerate_script: Path, tmp_path: Path
    ) -> None:
        """--dry-run doesn't skip validation — missing SKILL.md still fails."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = _run_regenerate(regenerate_script, [str(empty_dir), "--dry-run"])
        assert result.returncode != 0
        assert "skill.md not found" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_dry_run_with_missing_intent_still_validates(
        self, regenerate_script: Path, tmp_path: Path
    ) -> None:
        """--dry-run doesn't skip validation — missing intent file still fails."""
        result = _run_regenerate(
            regenerate_script,
            ["--intent-file", str(tmp_path / "nope.json"), "--dry-run"],
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    @pytest.mark.regenerate
    def test_dry_run_with_mutual_exclusion_still_validates(
        self, regenerate_script: Path, tmp_path: Path
    ) -> None:
        """--dry-run doesn't skip mutual exclusion check."""
        skill_dir = _create_upstream_skill(tmp_path)
        intent_file = _create_intent_file(tmp_path)
        result = _run_regenerate(
            regenerate_script,
            [str(skill_dir), "--intent-file", str(intent_file), "--dry-run"],
        )
        assert result.returncode != 0
        assert "cannot use both" in result.stderr.lower()
