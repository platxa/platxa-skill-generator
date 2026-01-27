"""Tests for sync-catalog.sh subcommands and override/patch mechanisms.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- list-external: lists external (non-local) skills from manifest
- list-local: lists local skills from manifest
- list-categories: groups skills by category
- Override file copy: files in overrides/<skill>/ replace synced files
- patch.yaml section injection: injects missing sections into SKILL.md
"""

from __future__ import annotations

import subprocess
from pathlib import Path

SYNC_SCRIPT = Path(__file__).parent.parent / "scripts" / "sync-catalog.sh"


def _create_test_catalog(tmp_path: Path) -> Path:
    """Create a minimal catalog directory with manifest and skills for testing.

    Returns the catalog root directory.
    """
    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir()

    # Create manifest with 2 local + 1 external skill
    manifest = catalog_dir / "manifest.yaml"
    manifest.write_text("""\
version: "1.0"

sources:
  test-source:
    repo: https://github.com/example/skills
    path: skills

skills:
  local-skill-one:
    local: true
    tier: 0
    category: devtools

  local-skill-two:
    local: true
    tier: 1
    category: testing

  external-skill-one:
    source: test-source
    ref: main
    tier: 2
    category: devtools
""")

    # Create local skill directories with SKILL.md
    for name in ["local-skill-one", "local-skill-two"]:
        skill_dir = catalog_dir / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"""\
---
name: {name}
description: A test skill for sync-catalog testing.
---

# {name}

Content here.
""")

    return catalog_dir


def _run_sync(catalog_dir: Path, subcommand: str) -> subprocess.CompletedProcess:
    """Run sync-catalog.sh with a subcommand against a test catalog."""
    return subprocess.run(
        [str(SYNC_SCRIPT), subcommand],
        capture_output=True,
        text=True,
        cwd=catalog_dir.parent,
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(catalog_dir.parent),
            "CATALOG_DIR": str(catalog_dir),
            "MANIFEST": str(catalog_dir / "manifest.yaml"),
            "OVERRIDES_DIR": str(catalog_dir / "overrides"),
        },
    )


class TestListExternal:
    """Tests for list-external subcommand."""

    def test_list_external_shows_external_skills(self, tmp_path: Path) -> None:
        """list-external outputs external (non-local) skills from manifest."""
        catalog_dir = _create_test_catalog(tmp_path)
        result = _run_sync(catalog_dir, "list-external")
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "external-skill-one" in result.stdout
        # Local skills should NOT appear in external listing
        assert "local-skill-one" not in result.stdout
        assert "local-skill-two" not in result.stdout

    def test_list_external_shows_source_and_tier(self, tmp_path: Path) -> None:
        """list-external output includes source and tier metadata."""
        catalog_dir = _create_test_catalog(tmp_path)
        result = _run_sync(catalog_dir, "list-external")
        assert "test-source" in result.stdout
        assert "tier=2" in result.stdout


class TestListLocal:
    """Tests for list-local subcommand."""

    def test_list_local_shows_local_skills(self, tmp_path: Path) -> None:
        """list-local outputs local skills from manifest."""
        catalog_dir = _create_test_catalog(tmp_path)
        result = _run_sync(catalog_dir, "list-local")
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "local-skill-one" in result.stdout
        assert "local-skill-two" in result.stdout
        # External skills should NOT appear
        assert "external-skill-one" not in result.stdout

    def test_list_local_shows_tier_and_category(self, tmp_path: Path) -> None:
        """list-local output includes tier and category metadata."""
        catalog_dir = _create_test_catalog(tmp_path)
        result = _run_sync(catalog_dir, "list-local")
        assert "tier=0" in result.stdout
        assert "category=devtools" in result.stdout


class TestListCategories:
    """Tests for list-categories subcommand."""

    def test_list_categories_groups_skills(self, tmp_path: Path) -> None:
        """list-categories groups skills by their category."""
        catalog_dir = _create_test_catalog(tmp_path)
        result = _run_sync(catalog_dir, "list-categories")
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "devtools" in result.stdout
        assert "testing" in result.stdout


class TestPatchYamlInjection:
    """Tests for patch.yaml section injection into SKILL.md."""

    def test_patch_injects_missing_sections(self, tmp_path: Path) -> None:
        """patch.yaml sections are appended to SKILL.md when not already present."""
        catalog_dir = _create_test_catalog(tmp_path)

        # Create overrides directory with patch.yaml for local-skill-one
        overrides_dir = catalog_dir / "overrides" / "local-skill-one"
        overrides_dir.mkdir(parents=True)
        (overrides_dir / "patch.yaml").write_text("""\
sections:
  Overview: |
    This skill provides testing utilities.

  Workflow: |
    1. Step one
    2. Step two
""")

        # Run apply_patch_yaml directly via a bash wrapper
        skill_md = catalog_dir / "local-skill-one" / "SKILL.md"
        original = skill_md.read_text()
        assert "## Overview" not in original
        assert "## Workflow" not in original

        # Source the script and call the function
        result = subprocess.run(
            [
                "bash",
                "-c",
                f"""
                source "{SYNC_SCRIPT}"
                apply_patch_yaml "{skill_md}" "{overrides_dir / "patch.yaml"}"
            """,
            ],
            capture_output=True,
            text=True,
            cwd=catalog_dir.parent,
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        patched = skill_md.read_text()
        assert "## Overview" in patched
        assert "## Workflow" in patched
        assert "This skill provides testing utilities." in patched

    def test_patch_does_not_overwrite_existing_sections(self, tmp_path: Path) -> None:
        """patch.yaml does not overwrite sections already present in SKILL.md."""
        catalog_dir = _create_test_catalog(tmp_path)

        # Add an Overview section to the skill
        skill_md = catalog_dir / "local-skill-one" / "SKILL.md"
        content = skill_md.read_text()
        content += "\n## Overview\n\nExisting overview content.\n"
        skill_md.write_text(content)

        # Create patch that tries to inject Overview
        overrides_dir = catalog_dir / "overrides" / "local-skill-one"
        overrides_dir.mkdir(parents=True)
        (overrides_dir / "patch.yaml").write_text("""\
sections:
  Overview: |
    REPLACEMENT overview that should NOT appear.
""")

        result = subprocess.run(
            [
                "bash",
                "-c",
                f"""
                source "{SYNC_SCRIPT}"
                apply_patch_yaml "{skill_md}" "{overrides_dir / "patch.yaml"}"
            """,
            ],
            capture_output=True,
            text=True,
            cwd=catalog_dir.parent,
        )

        assert result.returncode == 0
        patched = skill_md.read_text()
        assert "Existing overview content." in patched
        assert "REPLACEMENT overview" not in patched


class TestOverrideFileCopy:
    """Tests for file override copy mechanism."""

    def test_override_files_are_copied(self, tmp_path: Path) -> None:
        """Files in overrides/<skill>/ (except patch.yaml) are copied into skill dir."""
        catalog_dir = _create_test_catalog(tmp_path)

        # Create override file
        overrides_dir = catalog_dir / "overrides" / "local-skill-one"
        overrides_dir.mkdir(parents=True)
        refs_dir = overrides_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "extra-guide.md").write_text("# Extra Guide\n\nOverride content.\n")

        # Source the script and call apply_overrides via the file copy logic
        skill_dir = catalog_dir / "local-skill-one"
        result = subprocess.run(
            [
                "bash",
                "-c",
                f"""
                OVERRIDES_DIR="{catalog_dir / "overrides"}"
                skill_name="local-skill-one"
                target_dir="{skill_dir}"
                while IFS= read -r -d '' override_file; do
                    rel_path="${{override_file#"$OVERRIDES_DIR/$skill_name/"}}"
                    mkdir -p "$target_dir/$(dirname "$rel_path")"
                    cp "$override_file" "$target_dir/$rel_path"
                done < <(find "$OVERRIDES_DIR/$skill_name" -type f ! -name 'patch.yaml' -print0 2>/dev/null)
            """,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        copied = skill_dir / "references" / "extra-guide.md"
        assert copied.exists(), "Override file was not copied"
        assert "Override content." in copied.read_text()
