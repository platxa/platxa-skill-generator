"""Tests for check-dependencies.sh script.

Validates dependency checking behavior:
- Missing dependencies return exit 1 with names listed
- Satisfied dependencies return exit 0
- No depends-on field returns exit 0
- JSON output mode works correctly
- Both user and project skill directories are checked
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from helpers import create_skill_md

SCRIPT = Path(__file__).parent.parent / "scripts" / "check-dependencies.sh"


def run_check_deps(
    skill_dir: Path,
    *,
    project_dir: Path | None = None,
    json_output: bool = False,
) -> subprocess.CompletedProcess:
    cmd = [str(SCRIPT), str(skill_dir)]
    if project_dir:
        cmd.extend(["--project-dir", str(project_dir)])
    if json_output:
        cmd.append("--json")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)


class TestNoDependencies:
    """Skills with no depends-on field should always pass."""

    def test_no_depends_on_passes(self, temp_skill_dir: Path) -> None:
        create_skill_md(
            temp_skill_dir,
            "no-deps",
            "A skill with no dependencies declared.",
        )
        result = run_check_deps(temp_skill_dir)
        assert result.returncode == 0

    def test_no_depends_on_json(self, temp_skill_dir: Path) -> None:
        create_skill_md(
            temp_skill_dir,
            "no-deps",
            "A skill with no dependencies declared.",
        )
        result = run_check_deps(temp_skill_dir, json_output=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["satisfied"] is True
        assert data["dependencies"] == []
        assert data["missing"] == []


class TestMissingDependencies:
    """Skills with uninstalled dependencies should fail."""

    def test_missing_deps_fails(self, temp_skill_dir: Path) -> None:
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: needs-deps\n"
            "description: A skill that needs missing dependencies.\n"
            "depends-on:\n"
            "  - nonexistent-skill-aaa\n"
            "  - nonexistent-skill-bbb\n"
            "---\n\n# Test\n"
        )
        result = run_check_deps(temp_skill_dir)
        assert result.returncode == 1
        assert "nonexistent-skill-aaa" in result.stdout
        assert "nonexistent-skill-bbb" in result.stdout

    def test_missing_deps_json(self, temp_skill_dir: Path) -> None:
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: needs-deps\n"
            "description: A skill that needs missing dependencies.\n"
            "depends-on:\n"
            "  - nonexistent-skill-ccc\n"
            "---\n\n# Test\n"
        )
        result = run_check_deps(temp_skill_dir, json_output=True)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["satisfied"] is False
        assert "nonexistent-skill-ccc" in data["missing"]


class TestSatisfiedDependencies:
    """Skills whose dependencies exist should pass."""

    def test_deps_in_project_dir(self, temp_skill_dir: Path) -> None:
        """Create a fake project skills dir with the dependency installed."""
        # Set up the skill being checked
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: consumer-skill\n"
            "description: Depends on fake-dep.\n"
            "depends-on:\n"
            "  - fake-dep\n"
            "---\n\n# Test\n"
        )

        # Create a fake project dir with the dep installed
        project_dir = temp_skill_dir / "project"
        project_dir.mkdir()
        dep_dir = project_dir / ".claude" / "skills" / "fake-dep"
        dep_dir.mkdir(parents=True)
        (dep_dir / "SKILL.md").write_text("---\nname: fake-dep\ndescription: Fake.\n---\n# Fake\n")

        result = run_check_deps(temp_skill_dir, project_dir=project_dir)
        assert result.returncode == 0

    def test_mixed_found_and_missing(self, temp_skill_dir: Path) -> None:
        """One dep exists in project dir, another is missing."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: mixed-deps\n"
            "description: One found one missing.\n"
            "depends-on:\n"
            "  - existing-dep\n"
            "  - missing-dep\n"
            "---\n\n# Test\n"
        )

        project_dir = temp_skill_dir / "project"
        project_dir.mkdir()
        dep_dir = project_dir / ".claude" / "skills" / "existing-dep"
        dep_dir.mkdir(parents=True)
        (dep_dir / "SKILL.md").write_text(
            "---\nname: existing-dep\ndescription: Exists.\n---\n# E\n"
        )

        result = run_check_deps(temp_skill_dir, project_dir=project_dir, json_output=True)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "missing-dep" in data["missing"]
        assert "existing-dep" not in data["missing"]


class TestEdgeCases:
    """Edge cases and error handling."""

    def test_missing_skill_md_exits_2(self, temp_skill_dir: Path) -> None:
        result = run_check_deps(temp_skill_dir)
        assert result.returncode == 2

    def test_no_arguments_exits_2(self) -> None:
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True, timeout=10)
        assert result.returncode == 2
