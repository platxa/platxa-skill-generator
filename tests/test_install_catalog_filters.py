"""Tests for install-from-catalog.sh --tier and --category filter flags.

Tests cover:
- Tier filtering only installs skills at or below specified tier
- Category filtering only installs skills matching specified category
- Combined tier + category filtering

All tests use REAL file operations and run the actual install script.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
INSTALL_SCRIPT = SCRIPTS_DIR / "install-from-catalog.sh"

MANIFEST_YAML = """\
version: "1.0"
sources: {}
skills:
  alpha-skill:
    local: true
    tier: 0
    category: backend
  beta-skill:
    local: true
    tier: 1
    category: frontend
  gamma-skill:
    local: true
    tier: 2
    category: frontend
  delta-skill:
    local: true
    tier: 1
    category: backend
"""

SKILL_MD_TEMPLATE = """\
---
name: {name}
description: A test skill for {name}.
---

# {name}

Test content.
"""


@pytest.fixture
def catalog_env(tmp_path: Path) -> dict:
    """Create a temp project layout matching what install-from-catalog.sh expects.

    Layout:
        tmp_path/
            skills/
                manifest.yaml
                alpha-skill/SKILL.md
                beta-skill/SKILL.md
                gamma-skill/SKILL.md
                delta-skill/SKILL.md
            scripts/
                install-from-catalog.sh -> (symlink to real script)
            home/          (fake HOME for --user installs)
    """
    # Create skills dir with manifest and skill dirs
    catalog_dir = tmp_path / "skills"
    catalog_dir.mkdir()
    (catalog_dir / "manifest.yaml").write_text(MANIFEST_YAML)

    skill_names = ["alpha-skill", "beta-skill", "gamma-skill", "delta-skill"]
    for name in skill_names:
        skill_dir = catalog_dir / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(SKILL_MD_TEMPLATE.format(name=name))

    # Symlink scripts dir so BASH_SOURCE resolves to tmp_path/scripts/
    # This makes SCRIPT_DIR=tmp_path/scripts, PROJECT_DIR=tmp_path,
    # CATALOG_DIR=tmp_path/catalog (our test catalog)
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "install-from-catalog.sh").symlink_to(INSTALL_SCRIPT)

    # Fake HOME for --user installs
    install_home = tmp_path / "home"
    install_home.mkdir()

    return {
        "script": str(scripts_dir / "install-from-catalog.sh"),
        "install_home": install_home,
        "env": {**os.environ, "TERM": "dumb", "HOME": str(install_home)},
    }


def _run_install(catalog_env: dict, *extra_args: str) -> subprocess.CompletedProcess:
    """Run install-from-catalog.sh --all --user --no-validate --force with extra args."""
    cmd = [
        catalog_env["script"],
        "--all",
        "--user",
        "--no-validate",
        "--force",
        *extra_args,
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=catalog_env["env"],
        input="y\n",
    )


def _installed_skills(catalog_env: dict) -> set[str]:
    """Return set of skill names installed under the fake HOME."""
    skills_dir = catalog_env["install_home"] / ".claude" / "skills"
    if not skills_dir.exists():
        return set()
    return {d.name for d in skills_dir.iterdir() if d.is_dir()}


class TestTierFiltering:
    """Tests for --tier N flag."""

    def test_tier_0_installs_only_tier_0(self, catalog_env: dict) -> None:
        """--tier 0 should only install alpha-skill (tier 0)."""
        result = _run_install(catalog_env, "--tier", "0")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"alpha-skill"}, f"Expected only alpha-skill, got {installed}"

    def test_tier_1_installs_tier_0_and_1(self, catalog_env: dict) -> None:
        """--tier 1 should install alpha (0), beta (1), delta (1)."""
        result = _run_install(catalog_env, "--tier", "1")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"alpha-skill", "beta-skill", "delta-skill"}, f"Got {installed}"

    def test_tier_2_installs_all(self, catalog_env: dict) -> None:
        """--tier 2 should install all 4 skills (max tier is 2)."""
        result = _run_install(catalog_env, "--tier", "2")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"alpha-skill", "beta-skill", "gamma-skill", "delta-skill"}


class TestCategoryFiltering:
    """Tests for --category X flag."""

    def test_category_backend(self, catalog_env: dict) -> None:
        """--category backend should install alpha and delta."""
        result = _run_install(catalog_env, "--category", "backend")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"alpha-skill", "delta-skill"}, f"Got {installed}"

    def test_category_frontend(self, catalog_env: dict) -> None:
        """--category frontend should install beta and gamma."""
        result = _run_install(catalog_env, "--category", "frontend")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"beta-skill", "gamma-skill"}, f"Got {installed}"

    def test_category_nonexistent(self, catalog_env: dict) -> None:
        """--category nonexistent should install nothing."""
        result = _run_install(catalog_env, "--category", "nonexistent")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == set(), f"Expected nothing, got {installed}"


class TestCombinedFilters:
    """Tests for --tier + --category together."""

    def test_tier_1_category_frontend(self, catalog_env: dict) -> None:
        """--tier 1 --category frontend should install only beta (tier 1, frontend)."""
        result = _run_install(catalog_env, "--tier", "1", "--category", "frontend")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == {"beta-skill"}, f"Got {installed}"

    def test_tier_0_category_frontend(self, catalog_env: dict) -> None:
        """--tier 0 --category frontend should install nothing (no tier-0 frontend skills)."""
        result = _run_install(catalog_env, "--tier", "0", "--category", "frontend")
        assert result.returncode == 0, (
            f"Script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        installed = _installed_skills(catalog_env)
        assert installed == set(), f"Expected nothing, got {installed}"
