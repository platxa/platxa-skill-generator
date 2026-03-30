"""Tests for detect-circular-deps.sh script.

Covers: simple cycle, diamond, long chain, self-reference, no deps, JSON output.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "detect-circular-deps.sh"


def _make_skill(skills_dir: Path, name: str, depends_on: list[str] | None = None) -> None:
    """Create a minimal skill with optional depends-on."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    deps = ""
    if depends_on:
        deps = "depends-on:\n" + "".join(f"  - {d}\n" for d in depends_on)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill.\n{deps}---\n# {name}\n"
    )


def _run(skills_dir: Path, *, json_output: bool = False) -> subprocess.CompletedProcess:
    cmd = [str(SCRIPT), "--dir", str(skills_dir)]
    if json_output:
        cmd.append("--json")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)


class TestNoCycles:
    def test_no_deps(self, temp_skill_dir: Path) -> None:
        _make_skill(temp_skill_dir, "alpha")
        _make_skill(temp_skill_dir, "beta")
        result = _run(temp_skill_dir)
        assert result.returncode == 0

    def test_valid_chain(self, temp_skill_dir: Path) -> None:
        """A → B → C (no cycle)."""
        _make_skill(temp_skill_dir, "skill-c")
        _make_skill(temp_skill_dir, "skill-b", ["skill-c"])
        _make_skill(temp_skill_dir, "skill-a", ["skill-b"])
        result = _run(temp_skill_dir)
        assert result.returncode == 0

    def test_diamond_no_cycle(self, temp_skill_dir: Path) -> None:
        """A → B, A → C, B → D, C → D (diamond, no cycle)."""
        _make_skill(temp_skill_dir, "skill-d")
        _make_skill(temp_skill_dir, "skill-b", ["skill-d"])
        _make_skill(temp_skill_dir, "skill-c", ["skill-d"])
        _make_skill(temp_skill_dir, "skill-a", ["skill-b", "skill-c"])
        result = _run(temp_skill_dir)
        assert result.returncode == 0


class TestCycleDetection:
    def test_simple_cycle(self, temp_skill_dir: Path) -> None:
        """A → B → A."""
        _make_skill(temp_skill_dir, "skill-a", ["skill-b"])
        _make_skill(temp_skill_dir, "skill-b", ["skill-a"])
        result = _run(temp_skill_dir)
        assert result.returncode == 1
        assert "skill-a" in result.stdout
        assert "skill-b" in result.stdout

    def test_long_cycle(self, temp_skill_dir: Path) -> None:
        """A → B → C → D → A."""
        _make_skill(temp_skill_dir, "skill-a", ["skill-b"])
        _make_skill(temp_skill_dir, "skill-b", ["skill-c"])
        _make_skill(temp_skill_dir, "skill-c", ["skill-d"])
        _make_skill(temp_skill_dir, "skill-d", ["skill-a"])
        result = _run(temp_skill_dir)
        assert result.returncode == 1

    def test_self_reference(self, temp_skill_dir: Path) -> None:
        """A → A (self-dependency)."""
        _make_skill(temp_skill_dir, "skill-a", ["skill-a"])
        result = _run(temp_skill_dir)
        assert result.returncode == 1
        assert "skill-a" in result.stdout

    def test_cycle_json_output(self, temp_skill_dir: Path) -> None:
        """JSON output includes cycle details."""
        _make_skill(temp_skill_dir, "skill-x", ["skill-y"])
        _make_skill(temp_skill_dir, "skill-y", ["skill-x"])
        result = _run(temp_skill_dir, json_output=True)
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["has_cycles"] is True
        assert len(data["cycles"]) > 0


class TestEdgeCases:
    def test_empty_directory(self, temp_skill_dir: Path) -> None:
        result = _run(temp_skill_dir)
        assert result.returncode == 0

    def test_dep_on_nonexistent_skill(self, temp_skill_dir: Path) -> None:
        """Dep on skill not in the directory is ignored (not a cycle)."""
        _make_skill(temp_skill_dir, "skill-a", ["nonexistent"])
        result = _run(temp_skill_dir)
        assert result.returncode == 0
