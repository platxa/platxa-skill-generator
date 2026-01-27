"""Pytest configuration and fixtures for platxa-skill-generator tests.

This module provides fixtures for creating temporary skill directories
and helper functions for testing the validation scripts.

All tests use REAL file system operations - NO mocks or simulations.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from collections.abc import Callable, Generator
from pathlib import Path

import pytest

# Path to the skill generator root
SKILL_GENERATOR_ROOT = Path(__file__).parent.parent


@pytest.fixture
def temp_skill_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test skill files.

    This fixture creates a temporary directory that is automatically
    cleaned up after the test. Use this for creating test skill
    directories with various configurations.

    Yields:
        Path to the temporary directory

    Example:
        def test_valid_skill(temp_skill_dir):
            skill_md = temp_skill_dir / "SKILL.md"
            skill_md.write_text("---\\nname: test-skill\\n---")
    """
    with tempfile.TemporaryDirectory(prefix="skill_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def scripts_dir() -> Path:
    """Get the path to the scripts directory.

    Returns:
        Path to platxa-skill-generator/scripts/
    """
    return SKILL_GENERATOR_ROOT / "scripts"


@pytest.fixture
def run_validate_frontmatter(scripts_dir: Path) -> Callable[[Path], subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-frontmatter.sh.

    Returns:
        A callable that takes a skill directory and returns the subprocess result

    Example:
        def test_frontmatter(temp_skill_dir, run_validate_frontmatter):
            result = run_validate_frontmatter(temp_skill_dir)
            assert result.returncode == 0
    """
    script_path = scripts_dir / "validate-frontmatter.sh"

    def _run(skill_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(skill_dir)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},  # Disable colors for easier parsing
        )

    return _run


@pytest.fixture
def run_validate_structure(scripts_dir: Path) -> Callable[[Path], subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-structure.sh.

    Returns:
        A callable that takes a skill directory and returns the subprocess result

    Example:
        def test_structure(temp_skill_dir, run_validate_structure):
            result = run_validate_structure(temp_skill_dir)
            assert result.returncode == 0
    """
    script_path = scripts_dir / "validate-structure.sh"

    def _run(skill_dir: Path, verbose: bool = False) -> subprocess.CompletedProcess:
        cmd = [str(script_path)]
        if verbose:
            cmd.append("--verbose")
        cmd.append(str(skill_dir))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_count_tokens(scripts_dir: Path) -> Callable[[Path, bool, int], subprocess.CompletedProcess]:
    """Fixture that returns a function to run count-tokens.py.

    Returns:
        A callable that takes a skill directory and returns the subprocess result

    Example:
        def test_tokens(temp_skill_dir, run_count_tokens):
            result = run_count_tokens(temp_skill_dir, json_output=True)
            assert result.returncode == 0
    """
    script_path = scripts_dir / "count-tokens.py"

    def _run(
        skill_dir: Path, json_output: bool = False, warn_threshold: int = 80
    ) -> subprocess.CompletedProcess:
        cmd = ["python3", str(script_path)]
        if json_output:
            cmd.append("--json")
        if warn_threshold != 80:
            cmd.extend(["--warn-threshold", str(warn_threshold)])
        cmd.append(str(skill_dir))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

    return _run


@pytest.fixture
def run_security_check(scripts_dir: Path) -> Callable[[Path], subprocess.CompletedProcess]:
    """Fixture that returns a function to run security-check.sh.

    Returns:
        A callable that takes a skill directory and returns the subprocess result
    """
    script_path = scripts_dir / "security-check.sh"

    def _run(skill_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(skill_dir)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_validate_skill(scripts_dir: Path) -> Callable[[Path, str], subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-skill.sh.

    Returns:
        A callable that takes a skill directory and optional profile
    """
    script_path = scripts_dir / "validate-skill.sh"

    def _run(skill_dir: Path, profile: str = "") -> subprocess.CompletedProcess:
        cmd = [str(script_path)]
        if profile:
            cmd.append(f"--profile={profile}")
        cmd.append(str(skill_dir))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def run_validate_all(scripts_dir: Path) -> Callable[[Path], subprocess.CompletedProcess]:
    """Fixture that returns a function to run validate-all.sh.

    Returns:
        A callable that takes a skill directory and returns the subprocess result
    """
    script_path = scripts_dir / "validate-all.sh"

    def _run(skill_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(script_path), str(skill_dir)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
        )

    return _run


@pytest.fixture
def create_valid_skill(temp_skill_dir: Path) -> Callable[[], Path]:
    """Fixture that returns a function to create a valid skill directory.

    Creates a complete, valid skill directory structure with:
    - SKILL.md with valid frontmatter
    - scripts/ directory with executable script
    - references/ directory with markdown file

    Returns:
        A callable that creates and returns the skill directory path
    """

    def _create() -> Path:
        # Create SKILL.md with valid frontmatter
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill for validation purposes. This skill is used in automated testing.
tools:
  - Read
  - Write
  - Bash
---

# Test Skill

This is a test skill for validation.

## Usage

Use this skill for testing.
""")

        # Create scripts directory with executable script
        scripts = temp_skill_dir / "scripts"
        scripts.mkdir()

        test_script = scripts / "test.sh"
        test_script.write_text("""#!/bin/bash
echo "Test script"
""")
        test_script.chmod(0o755)

        # Create references directory with markdown
        refs = temp_skill_dir / "references"
        refs.mkdir()

        ref_file = refs / "guide.md"
        ref_file.write_text("""# Reference Guide

This is a reference document for the test skill.

## Section 1

Some content here.
""")

        return temp_skill_dir

    return _create


@pytest.fixture
def create_skill_md() -> Callable[[Path, str, str, list[str] | None, str | None], Path]:
    """Fixture that returns a function to create SKILL.md files.

    Returns:
        A callable that creates SKILL.md with specified frontmatter

    Example:
        def test_custom_skill(temp_skill_dir, create_skill_md):
            skill_md = create_skill_md(
                temp_skill_dir,
                name="my-skill",
                description="My custom skill",
                tools=["Read", "Write"]
            )
    """

    def _create(
        skill_dir: Path,
        name: str,
        description: str,
        tools: list[str] | None = None,
        model: str | None = None,
        content: str = "# Skill Content\n\nSkill instructions here.\n",
    ) -> Path:
        frontmatter_lines = [
            "---",
            f"name: {name}",
            f"description: {description}",
        ]

        if tools:
            frontmatter_lines.append("tools:")
            for tool in tools:
                frontmatter_lines.append(f"  - {tool}")

        if model:
            frontmatter_lines.append(f"model: {model}")

        frontmatter_lines.append("---")
        frontmatter_lines.append("")
        frontmatter_lines.append(content)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("\n".join(frontmatter_lines))

        return skill_md

    return _create


@pytest.fixture
def self_skill_dir() -> Path:
    """Get the path to the platxa-skill-generator itself for self-testing.

    Returns:
        Path to the platxa-skill-generator root directory
    """
    return SKILL_GENERATOR_ROOT


@pytest.fixture
def run_install_skill(
    scripts_dir: Path,
) -> Callable[[Path, Path, str], subprocess.CompletedProcess]:
    """Fixture that returns a function to run install-skill.sh.

    Returns:
        A callable that takes a skill directory, target base, and location flag
    """
    script_path = scripts_dir / "install-skill.sh"

    def _run(
        skill_dir: Path,
        target_base: Path,
        location: str = "--project",
    ) -> subprocess.CompletedProcess:
        # Set HOME to target_base for --user installs, or use target_base as project root
        env = {**os.environ, "TERM": "dumb"}
        if location == "--user":
            env["HOME"] = str(target_base)

        # For project installs, we run from the target_base directory
        cwd = str(target_base) if location == "--project" else None

        return subprocess.run(
            [str(script_path), str(skill_dir), location],
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            input="n\n",  # Auto-answer "no" to overwrite prompt
        )

    return _run
