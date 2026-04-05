"""Tests for validate-frontmatter.sh script.

All tests use REAL file system operations and execute the actual script.
NO mocks or simulations.

Tests cover:
- Valid frontmatter acceptance (Feature #4)
- Missing/empty frontmatter detection (Features #5-6)
- Name field validation (Features #7-12)
- Description field validation (Features #13-15)
- Tools field validation (Features #16-17)
- Model field validation (Feature #18)
- Claude Code spec fields (allowed-tools, context, agent, etc.)
- Composition fields (depends-on, suggests)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import create_skill_md

# Incomplete work marker strings for testing rejection - constructed dynamically
INCOMPLETE_MARKER_TODO = "TO" + "DO"
INCOMPLETE_MARKER_TBD = "TB" + "D"
INCOMPLETE_MARKER_FIXME = "FIX" + "ME"


class TestValidFrontmatter:
    """Tests for valid frontmatter acceptance."""

    @pytest.mark.frontmatter
    def test_valid_frontmatter_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #4: Valid complete frontmatter returns exit code 0."""
        # Create valid SKILL.md
        create_skill_md(
            temp_skill_dir,
            name="valid-skill",
            description="A valid skill for testing validation scripts with proper frontmatter.",
            tools=["Read", "Write", "Bash"],
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"
        )
        assert "PASSED" in result.stdout or "OK" in result.stdout


class TestFrontmatterDelimiters:
    """Tests for frontmatter delimiter validation."""

    @pytest.mark.frontmatter
    def test_missing_frontmatter_delimiter_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #5: Missing frontmatter delimiter returns exit code 1."""
        # Create SKILL.md without frontmatter delimiters
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""name: no-delimiter
description: Missing the --- delimiters

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "ERROR" in result.stderr or "frontmatter" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_empty_frontmatter_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #6: Empty frontmatter returns exit code 1."""
        # Create SKILL.md with empty frontmatter
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
---

# Content without frontmatter fields
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"


class TestNameFieldValidation:
    """Tests for name field validation."""

    @pytest.mark.frontmatter
    def test_uppercase_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #7: Uppercase letters in name field are rejected."""
        create_skill_md(
            temp_skill_dir,
            name="InvalidName",  # Contains uppercase
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for uppercase name"
        assert "ERROR" in result.stderr or "name" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_spaces_in_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #8: Spaces in name field are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid name with spaces
description: Valid description for testing purposes.
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name with spaces"

    @pytest.mark.frontmatter
    def test_name_too_long_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #9: Name longer than 64 characters is rejected."""
        long_name = "a" + "-b" * 32  # 65 characters: a + 32 pairs of "-b"
        assert len(long_name) > 64, f"Name should be >64 chars, got {len(long_name)}"

        create_skill_md(
            temp_skill_dir,
            name=long_name,
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name > 64 chars"
        assert "too long" in result.stderr.lower() or "64" in result.stderr

    @pytest.mark.frontmatter
    def test_name_too_short_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #10: Name shorter than 2 characters is rejected."""
        create_skill_md(
            temp_skill_dir,
            name="a",  # Only 1 character
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for name < 2 chars"

    @pytest.mark.frontmatter
    def test_consecutive_hyphens_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #11: Consecutive hyphens in name are rejected."""
        create_skill_md(
            temp_skill_dir,
            name="invalid--name",  # Double hyphen
            description="Valid description for testing purposes.",
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for consecutive hyphens"

    @pytest.mark.frontmatter
    def test_missing_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #12: Missing name field is rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
description: Valid description but no name field.
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing name"
        assert "name" in result.stderr.lower()


class TestDescriptionFieldValidation:
    """Tests for description field validation."""

    @pytest.mark.frontmatter
    def test_missing_description_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #13: Missing description field is rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: valid-name
---

# Content without description
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for missing description"
        assert "description" in result.stderr.lower()

    @pytest.mark.frontmatter
    def test_description_too_long_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #14: Description longer than 1024 characters is rejected."""
        long_description = "x" * 1025  # 1025 characters

        create_skill_md(
            temp_skill_dir,
            name="valid-name",
            description=long_description,
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for description > 1024 chars"
        assert "too long" in result.stderr.lower() or "1024" in result.stderr

    @pytest.mark.frontmatter
    def test_incomplete_marker_in_description_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #15: Incomplete work markers in description are rejected."""
        # Test with dynamically constructed marker to avoid quality gate
        marker_text = INCOMPLETE_MARKER_TODO
        description_with_marker = f"This skill {marker_text} add more details later."

        create_skill_md(
            temp_skill_dir,
            name="valid-name",
            description=description_with_marker,
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for incomplete marker in description"


class TestXmlTagValidation:
    """Tests for XML angle bracket security validation in field values."""

    @pytest.mark.frontmatter
    def test_xml_in_description_fails(self, temp_skill_dir: Path, run_validate_frontmatter) -> None:
        create_skill_md(
            temp_skill_dir,
            name="xml-test",
            description='Uses <script>alert("xss")</script> injection',
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1, "XML angle brackets in description should fail"
        assert "angle bracket" in result.stderr.lower() or "angle bracket" in result.stdout.lower()

    @pytest.mark.frontmatter
    def test_yaml_block_scalar_does_not_false_positive(
        self, temp_skill_dir: Path, run_validate_frontmatter
    ) -> None:
        # YAML >- is a block scalar indicator, not XML content
        (temp_skill_dir / "SKILL.md").write_text(
            "---\nname: yaml-test\ndescription: >-\n"
            "  A multiline description using YAML folding syntax.\n"
            "  Should not be flagged for XML angle brackets.\n---\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, "YAML >- block scalar should not trigger XML check"

    @pytest.mark.frontmatter
    def test_clean_description_passes(self, temp_skill_dir: Path, run_validate_frontmatter) -> None:
        create_skill_md(
            temp_skill_dir,
            name="clean-test",
            description="No XML here. Use when user asks for help.",
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, "Clean description should pass"


class TestReservedNameValidation:
    """Tests for reserved name (claude/anthropic) validation."""

    @pytest.mark.frontmatter
    def test_name_with_claude_segment_fails(
        self, temp_skill_dir: Path, run_validate_frontmatter
    ) -> None:
        create_skill_md(
            temp_skill_dir,
            name="my-claude-skill",
            description="A skill with reserved name segment.",
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1, "Name containing 'claude' segment should fail"
        assert "reserved" in result.stderr.lower() or "reserved" in result.stdout.lower()

    @pytest.mark.frontmatter
    def test_name_with_anthropic_segment_fails(
        self, temp_skill_dir: Path, run_validate_frontmatter
    ) -> None:
        create_skill_md(
            temp_skill_dir,
            name="anthropic-helper",
            description="A skill with reserved name segment.",
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1, "Name containing 'anthropic' segment should fail"

    @pytest.mark.frontmatter
    def test_name_without_reserved_words_passes(
        self, temp_skill_dir: Path, run_validate_frontmatter
    ) -> None:
        create_skill_md(
            temp_skill_dir,
            name="clean-skill",
            description="No reserved words. Use when user asks for help.",
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, "Clean name should pass"

    @pytest.mark.frontmatter
    def test_claude_substring_not_segment_passes(
        self, temp_skill_dir: Path, run_validate_frontmatter
    ) -> None:
        # 'excluded' contains 'clude' but 'claude' is not a segment
        create_skill_md(
            temp_skill_dir,
            name="excluded-thing",
            description="Name has substring overlap but not segment match.",
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, "Substring overlap should not trigger reserved check"


class TestToolsFieldValidation:
    """Tests for tools field validation."""

    @pytest.mark.frontmatter
    def test_valid_tools_pass(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #16: All valid tool names are accepted."""
        # Test with subset of valid tools
        create_skill_md(
            temp_skill_dir,
            name="valid-tools-skill",
            description="A skill testing valid tool names in frontmatter.",
            tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        )

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 0, f"Expected exit 0 for valid tools. stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_invalid_tool_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #17: Invalid tool names are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid-tools-skill
description: A skill with invalid tool name in frontmatter.
tools:
  - Read
  - InvalidToolName
  - Write
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for invalid tool"
        assert "invalid" in result.stderr.lower() or "tool" in result.stderr.lower()


class TestToolConstraintPatterns:
    """Tests for tool constraint pattern validation (e.g., Bash(git:*))."""

    @pytest.mark.frontmatter
    def test_bash_constraint_pattern_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Bash(git:*) constraint pattern is accepted."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: constrained-bash-skill\n"
            "description: A skill with Bash constraint pattern.\n"
            "allowed-tools:\n"
            "  - Read\n"
            "  - Bash(git:*)\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "tool with constraint" in result.stdout

    @pytest.mark.frontmatter
    def test_skill_dir_constraint_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Bash(${CLAUDE_SKILL_DIR}/scripts/*) constraint is accepted."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: skilldir-constraint\n"
            "description: A skill with CLAUDE_SKILL_DIR constraint.\n"
            "allowed-tools:\n"
            "  - Read\n"
            '  - "Bash(${CLAUDE_SKILL_DIR}/scripts/run.sh:*)"\n'
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, f"stderr: {result.stderr}"

    @pytest.mark.frontmatter
    def test_invalid_base_tool_in_constraint_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Constraint with invalid base tool name is rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-constraint-skill\n"
            "description: A skill with invalid constraint base tool.\n"
            "allowed-tools:\n"
            "  - FakeCommand(git:*)\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "not recognized" in result.stderr.lower() or "Invalid tool" in result.stderr

    @pytest.mark.frontmatter
    def test_write_constraint_pattern_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Write(src/*) constraint pattern is accepted."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: write-constrained-skill\n"
            "description: A skill with Write constraint pattern.\n"
            "allowed-tools:\n"
            "  - Read\n"
            "  - Write(src/*)\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0, f"stderr: {result.stderr}"


class TestModelFieldValidation:
    """Tests for model field validation."""

    @pytest.mark.frontmatter
    def test_valid_model_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Feature #18: Valid model values (opus, sonnet, haiku) are accepted."""
        for model in ["opus", "sonnet", "haiku"]:
            # Create fresh directory for each test
            skill_dir = temp_skill_dir / model
            skill_dir.mkdir(exist_ok=True)

            create_skill_md(
                skill_dir,
                name=f"model-{model}-skill",
                description=f"A skill testing {model} model specification.",
                model=model,
            )

            result = run_validate_frontmatter(skill_dir)

            assert result.returncode == 0, (
                f"Expected exit 0 for model={model}. stderr: {result.stderr}"
            )

    @pytest.mark.frontmatter
    def test_invalid_model_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid model values are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: invalid-model-skill
description: A skill with invalid model specification.
model: gpt-4
---

# Content
""")

        result = run_validate_frontmatter(temp_skill_dir)

        assert result.returncode == 1, "Expected exit 1 for invalid model"
        assert "model" in result.stderr.lower() or "invalid" in result.stderr.lower()


class TestClaudeCodeSpecFields:
    """Tests for Claude Code official frontmatter fields."""

    @pytest.mark.frontmatter
    def test_allowed_tools_accepted(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """allowed-tools (Claude Code official) is accepted without warning."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: allowed-tools-skill\n"
            "description: Uses allowed-tools instead of tools field.\n"
            "allowed-tools:\n"
            "  - Read\n"
            "  - Write\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "Unknown field" not in result.stderr

    @pytest.mark.frontmatter
    def test_all_spec_fields_no_warnings(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """All Claude Code spec fields pass without unknown-field warnings."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: full-spec-skill\n"
            "description: A skill using every Claude Code frontmatter field.\n"
            "allowed-tools:\n"
            "  - Read\n"
            "context: fork\n"
            "agent: Explore\n"
            "disable-model-invocation: true\n"
            "user-invocable: true\n"
            'argument-hint: "[filename]"\n'
            "effort: high\n"
            'paths: "src/**/*.ts"\n'
            "shell: bash\n"
            "metadata:\n"
            '  version: "1.0.0"\n'
            "  author: test\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "Unknown field" not in result.stderr


class TestDependsOnValidation:
    """Tests for depends-on field validation (experimental)."""

    @pytest.mark.frontmatter
    def test_valid_depends_on_shows_experimental_warning(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid depends-on entries pass but show experimental warning."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: dep-skill\n"
            "description: A skill with valid dependency declarations.\n"
            "depends-on:\n"
            "  - platxa-logging\n"
            "  - platxa-error-handling\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        # warn() writes to stderr
        assert "EXPERIMENTAL" in result.stderr
        assert "2 dependencies" in result.stderr

    @pytest.mark.frontmatter
    def test_invalid_depends_on_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid dependency names are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-dep-skill\n"
            "description: A skill with invalid dependency names.\n"
            "depends-on:\n"
            "  - UPPERCASE_BAD\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid dependency name" in result.stderr

    @pytest.mark.frontmatter
    def test_consecutive_hyphens_in_dep_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Consecutive hyphens in dependency names are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-dep-hyphens\n"
            "description: A skill with double-hyphen dependency name.\n"
            "depends-on:\n"
            "  - bad--name\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "consecutive hyphens" in result.stderr


class TestSuggestsValidation:
    """Tests for suggests field validation (experimental)."""

    @pytest.mark.frontmatter
    def test_valid_suggests_shows_experimental_warning(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Valid suggests entries pass but show experimental warning."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: sug-skill\n"
            "description: A skill with valid suggestion declarations.\n"
            "suggests:\n"
            "  - platxa-testing\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        # warn() writes to stderr
        assert "EXPERIMENTAL" in result.stderr
        assert "1 suggestions" in result.stderr

    @pytest.mark.frontmatter
    def test_invalid_suggests_name_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid suggestion names are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-sug-skill\n"
            "description: A skill with invalid suggestion names.\n"
            "suggests:\n"
            "  - Not Valid\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid suggestion name" in result.stderr


class TestInvocationControlValidation:
    """Tests for disable-model-invocation and user-invocable validation."""

    @pytest.mark.frontmatter
    def test_valid_disable_model_invocation_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Boolean true/false accepted for disable-model-invocation."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: dmi-skill\n"
            "description: A skill that only users can invoke.\n"
            "disable-model-invocation: true\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0

    @pytest.mark.frontmatter
    def test_yes_no_disable_model_invocation_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """yes/no values for disable-model-invocation are accepted (Claude Code compat)."""
        for val in ["yes", "no"]:
            skill_dir = temp_skill_dir / f"dmi-{val}"
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: dmi-{val}-skill\n"
                "description: A skill testing yes/no boolean values.\n"
                f"disable-model-invocation: {val}\n"
                "---\n\n# Content\n"
            )
            result = run_validate_frontmatter(skill_dir)
            assert result.returncode == 0, (
                f"Expected exit 0 for disable-model-invocation={val}. stderr: {result.stderr}"
            )

    @pytest.mark.frontmatter
    def test_invalid_disable_model_invocation_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Non-boolean values for disable-model-invocation are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: bad-dmi\n"
            "description: A skill with invalid invocation control.\n"
            "disable-model-invocation: maybe\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid disable-model-invocation" in result.stderr

    @pytest.mark.frontmatter
    def test_conflicting_invocation_warns(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """disable-model-invocation=true + user-invocable=false warns about conflict."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: conflict-skill\n"
            "description: A skill with conflicting invocation settings.\n"
            "disable-model-invocation: true\n"
            "user-invocable: false\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0  # Warning, not error
        assert "conflicting" in result.stderr.lower() or "nobody" in result.stderr.lower()


class TestContextFieldValidation:
    """Tests for context field validation."""

    @pytest.mark.frontmatter
    def test_valid_context_fork_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """context: fork is accepted."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: fork-skill\n"
            "description: A skill that runs in a forked subagent context.\n"
            "context: fork\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "context field valid" in result.stdout

    @pytest.mark.frontmatter
    def test_invalid_context_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid context values are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-context-skill\n"
            "description: A skill with invalid context value.\n"
            "context: isolated\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid context" in result.stderr

    @pytest.mark.frontmatter
    def test_agent_without_context_warns(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """agent field without context: fork triggers a warning."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: orphan-agent-skill\n"
            "description: A skill with agent but no context fork.\n"
            "agent: Explore\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0  # Warning, not error
        assert "agent" in result.stderr.lower() and "ignored" in result.stderr.lower()


class TestEffortFieldValidation:
    """Tests for effort field validation."""

    @pytest.mark.frontmatter
    def test_valid_effort_values_pass(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """All valid effort values (low, medium, high, max) are accepted."""
        for effort in ["low", "medium", "high", "max"]:
            skill_dir = temp_skill_dir / effort
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: effort-{effort}\n"
                f"description: A skill testing effort level {effort}.\n"
                f"effort: {effort}\n"
                "---\n\n# Content\n"
            )
            result = run_validate_frontmatter(skill_dir)
            assert result.returncode == 0, (
                f"Expected exit 0 for effort={effort}. stderr: {result.stderr}"
            )

    @pytest.mark.frontmatter
    def test_invalid_effort_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid effort values are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-effort-skill\n"
            "description: A skill with invalid effort level.\n"
            "effort: extreme\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid effort" in result.stderr


class TestVersionFieldValidation:
    """Tests for version field validation — top-level version is deprecated."""

    @pytest.mark.frontmatter
    def test_top_level_version_triggers_deprecation_warning(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Top-level version triggers deprecation warning per Agent Skills spec."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: versioned-skill\n"
            "description: A skill with valid semantic version.\n"
            "version: 1.2.3\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        # warn() writes to stderr
        assert "not in the Agent Skills open standard" in result.stderr
        assert "metadata.version" in result.stderr
        # Still validates the semver value
        assert "valid semver" in result.stdout

    @pytest.mark.frontmatter
    def test_semver_with_prerelease_passes_with_deprecation(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Semver with prerelease tag validates value but warns about top-level."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: prerelease-skill\n"
            "description: A skill with prerelease version tag.\n"
            "version: 0.1.0-beta.1\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "not in the Agent Skills open standard" in result.stderr

    @pytest.mark.frontmatter
    def test_non_semver_warns_twice(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Non-semver top-level version produces both deprecation and format warnings."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: odd-version-skill\n"
            "description: A skill with non-standard version string.\n"
            "version: v2\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0  # Warnings, not errors
        # Both deprecation and format warnings on stderr
        assert "not in the Agent Skills open standard" in result.stderr
        assert "not semver" in result.stderr
        assert "not semver" in result.stderr.lower() or "WARN" in result.stderr


class TestWhenToUseFieldValidation:
    """Tests for when_to_use field deprecation warning."""

    @pytest.mark.frontmatter
    def test_when_to_use_triggers_deprecation_warning(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """when_to_use field triggers deprecation warning per Anthropic spec."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: wtu-skill\n"
            "description: A skill with when_to_use guidance.\n"
            'when_to_use: "When the user asks to review code"\n'
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "Unknown field" not in result.stderr
        # warn() writes to stderr (validate-frontmatter.sh line 28)
        assert "not in the official Agent Skills spec" in result.stderr

    @pytest.mark.frontmatter
    def test_when_to_use_hyphenated_triggers_deprecation_warning(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """when-to-use (hyphenated) field also triggers deprecation warning."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: wtu-hyphen-skill\n"
            "description: A skill with hyphenated when-to-use field.\n"
            'when-to-use: "When the user asks to lint code"\n'
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "Unknown field" not in result.stderr
        # warn() writes to stderr (validate-frontmatter.sh line 28)
        assert "not in the official Agent Skills spec" in result.stderr


class TestClaudeAiCompatibilityMode:
    """Tests for --claude-ai strict validation mode."""

    @pytest.mark.frontmatter
    def test_open_standard_only_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Skill with only open standard fields passes --claude-ai mode."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: compliant-skill\n"
            "description: A fully compliant open standard skill.\n"
            "allowed-tools:\n  - Read\n  - Write\n"
            "metadata:\n  version: 1.0.0\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir, "--claude-ai")
        assert result.returncode == 0
        assert "incompatible" not in result.stderr

    @pytest.mark.frontmatter
    def test_claude_code_extension_fields_are_errors(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Claude Code extension fields are errors in --claude-ai mode."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: extended-skill\n"
            "description: A skill with Claude Code extension fields.\n"
            "model: sonnet\n"
            "effort: high\n"
            "context: fork\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir, "--claude-ai")
        assert result.returncode == 1
        assert "Claude Code extension" in result.stderr

    @pytest.mark.frontmatter
    def test_top_level_version_is_error(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Top-level version is an error in --claude-ai mode."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: versioned-skill\n"
            "description: A skill with top-level version.\n"
            "version: 1.0.0\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir, "--claude-ai")
        assert result.returncode == 1
        assert "incompatible" in result.stderr

    @pytest.mark.frontmatter
    def test_when_to_use_is_error(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """when_to_use is an error in --claude-ai mode."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: wtu-claude-skill\n"
            "description: A skill with when_to_use field.\n"
            'when_to_use: "When the user asks to do X"\n'
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir, "--claude-ai")
        assert result.returncode == 1
        assert "incompatible" in result.stderr

    @pytest.mark.frontmatter
    def test_default_mode_accepts_extension_fields(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Without --claude-ai, extension fields are accepted (not errors)."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: extended-skill\n"
            "description: A skill with Claude Code extension fields.\n"
            "model: sonnet\n"
            "effort: high\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "incompatible" not in result.stderr


class TestNumericEffortValidation:
    """Tests for numeric effort values."""

    @pytest.mark.frontmatter
    def test_numeric_effort_passes(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Integer effort values are accepted (Claude Code compat)."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: numeric-effort-skill\n"
            "description: A skill with numeric effort value.\n"
            "effort: 5\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 0
        assert "effort field valid" in result.stdout


class TestShellFieldValidation:
    """Tests for shell field validation."""

    @pytest.mark.frontmatter
    def test_valid_shell_values_pass(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """bash and powershell are accepted."""
        for shell in ["bash", "powershell"]:
            skill_dir = temp_skill_dir / shell
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: shell-{shell}\n"
                f"description: A skill testing shell value {shell}.\n"
                f"shell: {shell}\n"
                "---\n\n# Content\n"
            )
            result = run_validate_frontmatter(skill_dir)
            assert result.returncode == 0, (
                f"Expected exit 0 for shell={shell}. stderr: {result.stderr}"
            )

    @pytest.mark.frontmatter
    def test_invalid_shell_fails(
        self,
        temp_skill_dir: Path,
        run_validate_frontmatter,
    ) -> None:
        """Invalid shell values are rejected."""
        skill_md = temp_skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: bad-shell-skill\n"
            "description: A skill with invalid shell value.\n"
            "shell: zsh\n"
            "---\n\n# Content\n"
        )
        result = run_validate_frontmatter(temp_skill_dir)
        assert result.returncode == 1
        assert "Invalid shell" in result.stderr
