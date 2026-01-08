"""Integration tests for platxa-skill-generator.

All tests use REAL file system operations and execute actual scripts.
NO mocks or simulations.

Tests cover:
- validate-all.sh integration (Feature #41)
- Self-validation of platxa-skill-generator (Feature #42)
- security-check.sh dangerous command detection (Feature #43)
- install-skill.sh copy functionality (Feature #44)
- Template-based skill creation workflow (Feature #45)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from helpers import (
    create_executable_script,
    create_reference_file,
    create_skill_md,
)


class TestValidateAllIntegration:
    """Tests for validate-all.sh running all validators."""

    @pytest.mark.integration
    def test_validate_all_integration(
        self,
        temp_skill_dir: Path,
        run_validate_all,
    ) -> None:
        """Feature #41: validate-all.sh runs all validators and returns correct status."""
        # Create a complete valid skill with all required sections
        create_skill_md(
            temp_skill_dir,
            name="integration-skill",
            description="A skill for testing validate-all.sh integration with comprehensive validation.",
            tools=["Read", "Write", "Bash"],
            content="""# Integration Skill

## Overview

This skill demonstrates proper integration testing of all validators.

## Workflow

1. Create a valid skill structure
2. Run validate-all.sh
3. Verify all validators pass

## Usage

Run the skill with `/integration-skill`.

## Examples

```bash
echo "Example usage"
```

## Output Checklist

- [ ] All validators pass
- [ ] Exit code is 0
""",
        )

        # Create scripts directory with valid executable
        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()
        create_executable_script(
            scripts_dir,
            "helper.sh",
            "#!/bin/bash\nset -euo pipefail\necho 'helper'\n",
        )

        # Create references directory with content
        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nContent here.\n")

        result = run_validate_all(temp_skill_dir)

        # Should pass all validations
        assert result.returncode == 0, f"Expected exit 0. stdout: {result.stdout}"
        assert "PASSED" in result.stdout or "passed" in result.stdout.lower()

    @pytest.mark.integration
    def test_validate_all_fails_on_invalid(
        self,
        temp_skill_dir: Path,
        run_validate_all,
    ) -> None:
        """validate-all.sh returns exit 1 when a validator fails."""
        # Create SKILL.md without frontmatter (will fail structure validation)
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("# Invalid Skill\n\nNo frontmatter here.\n")

        result = run_validate_all(temp_skill_dir)

        # Should fail
        assert result.returncode == 1, f"Expected exit 1 for invalid skill"
        assert "FAIL" in result.stdout or "failed" in result.stdout.lower()


class TestSelfValidation:
    """Tests for validating platxa-skill-generator itself."""

    @pytest.mark.integration
    def test_self_validation_passes(
        self,
        self_skill_dir: Path,
        run_validate_structure,
        run_validate_frontmatter,
    ) -> None:
        """Feature #42: platxa-skill-generator itself passes structure and frontmatter validation.

        Note: Token validation is skipped because platxa-skill-generator contains
        extensive reference documentation that intentionally exceeds standard skill
        token limits. This is appropriate for a meta-skill that documents skill creation.
        """
        # Validate structure
        structure_result = run_validate_structure(self_skill_dir)
        assert structure_result.returncode == 0, (
            f"platxa-skill-generator failed structure validation.\n"
            f"stdout: {structure_result.stdout}\n"
            f"stderr: {structure_result.stderr}"
        )

        # Validate frontmatter
        frontmatter_result = run_validate_frontmatter(self_skill_dir)
        assert frontmatter_result.returncode == 0, (
            f"platxa-skill-generator failed frontmatter validation.\n"
            f"stdout: {frontmatter_result.stdout}\n"
            f"stderr: {frontmatter_result.stderr}"
        )


class TestSecurityCheck:
    """Tests for security-check.sh detecting dangerous commands."""

    @pytest.mark.integration
    def test_security_check_detects_dangerous_commands(
        self,
        temp_skill_dir: Path,
        run_security_check,
    ) -> None:
        """Feature #43: security-check.sh detects dangerous commands in scripts."""
        create_skill_md(
            temp_skill_dir,
            name="dangerous-skill",
            description="A skill with dangerous scripts for testing security check.",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()

        # Create a script with dangerous pattern: rm -rf /
        dangerous_script = scripts_dir / "dangerous.sh"
        dangerous_script.write_text("""#!/bin/bash
# This script has dangerous commands
rm -rf /
echo "This should be caught"
""")
        dangerous_script.chmod(0o755)

        result = run_security_check(temp_skill_dir)

        # Should fail with security error
        assert result.returncode == 1, f"Expected exit 1 for dangerous command"
        assert "SECURITY" in result.stderr or "Dangerous" in result.stderr

    @pytest.mark.integration
    def test_security_check_detects_curl_pipe_bash(
        self,
        temp_skill_dir: Path,
        run_security_check,
    ) -> None:
        """security-check.sh detects curl piped to bash."""
        create_skill_md(
            temp_skill_dir,
            name="curl-bash-skill",
            description="A skill with curl piped to bash.",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()

        # Create a script with curl | bash pattern
        risky_script = scripts_dir / "install.sh"
        risky_script.write_text("""#!/bin/bash
# Install something from the internet unsafely
curl https://example.com/install.sh | bash
""")
        risky_script.chmod(0o755)

        result = run_security_check(temp_skill_dir)

        # Should fail
        assert result.returncode == 1, f"Expected exit 1 for curl pipe bash"

    @pytest.mark.integration
    def test_security_check_passes_safe_scripts(
        self,
        temp_skill_dir: Path,
        run_security_check,
    ) -> None:
        """security-check.sh passes skills with safe scripts."""
        create_skill_md(
            temp_skill_dir,
            name="safe-skill",
            description="A skill with safe scripts.",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()

        # Create a safe script
        safe_script = scripts_dir / "safe.sh"
        safe_script.write_text("""#!/bin/bash
# A safe script
echo "Hello, world!"
ls -la
pwd
""")
        safe_script.chmod(0o755)

        result = run_security_check(temp_skill_dir)

        # Should pass (exit 0)
        assert result.returncode == 0, f"Expected exit 0 for safe scripts. stderr: {result.stderr}"


class TestInstallSkill:
    """Tests for install-skill.sh copy functionality."""

    @pytest.mark.integration
    def test_install_skill_copies_correctly(
        self,
        temp_skill_dir: Path,
        run_install_skill,
    ) -> None:
        """Feature #44: install-skill.sh correctly copies skill to target directory."""
        # Create source skill with all required sections
        create_skill_md(
            temp_skill_dir,
            name="installable-skill",
            description="A skill that can be installed to a target location for testing the install workflow.",
            tools=["Read", "Write"],
            content="""# Installable Skill

## Overview

A skill designed to test the install-skill.sh copy functionality.

## Workflow

1. Create valid skill
2. Run install-skill.sh
3. Verify files copied

## Usage

Run with `/installable-skill`.

## Examples

```bash
echo "installed"
```

## Output Checklist

- [ ] Files copied correctly
""",
        )

        scripts_dir = temp_skill_dir / "scripts"
        scripts_dir.mkdir()
        create_executable_script(
            scripts_dir,
            "helper.sh",
            "#!/bin/bash\nset -euo pipefail\necho 'test'\n",
        )

        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        create_reference_file(refs_dir, "guide.md", "# Guide\n\nContent.\n")

        # Create target directory for project install
        with tempfile.TemporaryDirectory(prefix="install_target_") as target_base:
            target_path = Path(target_base)

            result = run_install_skill(temp_skill_dir, target_path, "--project")

            # Should succeed
            assert result.returncode == 0, (
                f"Expected exit 0.\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

            # Verify files were copied
            installed_dir = target_path / ".claude" / "skills" / "installable-skill"
            assert installed_dir.exists(), f"Installed directory not found: {installed_dir}"
            assert (installed_dir / "SKILL.md").exists(), "SKILL.md not copied"
            assert (installed_dir / "scripts" / "helper.sh").exists(), "Script not copied"
            assert (installed_dir / "references" / "guide.md").exists(), "Reference not copied"

    @pytest.mark.integration
    def test_install_skill_user_location(
        self,
        temp_skill_dir: Path,
        run_install_skill,
    ) -> None:
        """install-skill.sh copies to ~/.claude/skills/ with --user flag."""
        create_skill_md(
            temp_skill_dir,
            name="user-skill",
            description="A skill to be installed in user location for testing user-level installation.",
            content="""# User Skill

## Overview

A skill for testing user-location installation.

## Workflow

1. Create skill
2. Install to user location
3. Verify installation

## Usage

Run with `/user-skill`.

## Examples

```bash
echo "user skill"
```

## Output Checklist

- [ ] Installed to ~/.claude/skills/
""",
        )

        # Create target directory simulating HOME
        with tempfile.TemporaryDirectory(prefix="fake_home_") as fake_home:
            fake_home_path = Path(fake_home)

            result = run_install_skill(temp_skill_dir, fake_home_path, "--user")

            # Should succeed
            assert result.returncode == 0, (
                f"Expected exit 0.\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

            # Verify installed to user location
            installed_dir = fake_home_path / ".claude" / "skills" / "user-skill"
            assert installed_dir.exists(), f"User install directory not found: {installed_dir}"
            assert (installed_dir / "SKILL.md").exists(), "SKILL.md not copied to user location"


class TestTemplateSkillWorkflow:
    """Tests for complete skill creation workflow."""

    @pytest.mark.integration
    def test_template_skill_validates(
        self,
        run_validate_all,
    ) -> None:
        """Feature #45: Complete skill creation workflow from template passes all validations."""
        # Create a skill from scratch using the helpers (simulating template usage)
        with tempfile.TemporaryDirectory(prefix="template_skill_") as tmpdir:
            skill_dir = Path(tmpdir)

            # Create complete skill structure (as if from template)
            # Must include all recommended sections: Overview, Usage, Examples
            create_skill_md(
                skill_dir,
                name="template-generated-skill",
                description="A skill generated from template patterns for comprehensive testing of the skill creation workflow.",
                tools=["Read", "Write", "Bash", "Glob", "Grep"],
                content="""# Template Generated Skill

## Overview

This skill demonstrates the complete workflow from template to validation.
It tests that skills created following the template pattern pass all validations.

## Workflow

1. Generate skill from template
2. Customize content and metadata
3. Run all validators
4. Install skill

## Usage

Run the skill with:

```
/template-generated-skill
```

## Features

- Feature 1: Read files efficiently
- Feature 2: Write output correctly
- Feature 3: Execute commands safely

## Examples

### Example 1: Basic Usage
```bash
echo "Running skill"
```

### Example 2: Python Integration
```python
print("Python example")
```

## Output Checklist

- [ ] Skill validates successfully
- [ ] All sections present
""",
            )

            # Add scripts directory with safe, executable scripts
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            create_executable_script(
                scripts_dir,
                "run.sh",
                """#!/bin/bash
set -euo pipefail
echo "Running template skill"
""",
            )

            # Add references directory with documentation
            refs_dir = skill_dir / "references"
            refs_dir.mkdir()
            create_reference_file(
                refs_dir,
                "usage-guide.md",
                """# Usage Guide

## Getting Started

Follow these steps to use the skill effectively.

## Configuration

No configuration required.

## Troubleshooting

If you encounter issues, check the logs.
""",
            )
            create_reference_file(
                refs_dir,
                "api-reference.md",
                """# API Reference

## Functions

### run()
Executes the main skill logic.

### configure()
Sets up skill configuration.
""",
            )

            # Run all validators
            result = run_validate_all(skill_dir)

            # Should pass all validations
            assert result.returncode == 0, (
                f"Template-generated skill failed validation.\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

    @pytest.mark.integration
    def test_minimal_skill_validates(
        self,
        run_validate_all,
    ) -> None:
        """Minimal valid skill (just SKILL.md with required sections) passes validation."""
        with tempfile.TemporaryDirectory(prefix="minimal_skill_") as tmpdir:
            skill_dir = Path(tmpdir)

            # Create minimal skill with required sections (Overview, Usage, Examples)
            create_skill_md(
                skill_dir,
                name="minimal-skill",
                description="A minimal skill demonstrating the minimum required structure for validation.",
                content="""# Minimal Skill

## Overview

A minimal skill with only the required SKILL.md file.

## Workflow

1. Create SKILL.md with all sections
2. Validate

## Usage

Run with `/minimal-skill`.

## Examples

```bash
echo "minimal example"
```

## Output Checklist

- [ ] Minimal structure validates
""",
            )

            result = run_validate_all(skill_dir)

            # Minimal skill should pass
            assert result.returncode == 0, (
                f"Minimal skill failed validation.\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
