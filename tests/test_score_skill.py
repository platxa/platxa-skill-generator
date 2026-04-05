"""Tests for score-skill.py quality scorer.

Tests each dimension and overall scoring behavior.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "score-skill.py"

VALID_SKILL = """\
---
name: test-scorer-skill
description: Validates skill quality by checking frontmatter, content depth, and token budgets. Use when the user asks to "score a skill", "check quality", or "validate a skill". Supports scoring across all five quality dimensions including spec compliance and example quality.
allowed-tools:
  - Read
  - Write
  - Bash
---

# Test Scorer Skill

## Overview

This skill demonstrates proper structure with real content.
It provides concrete instructions for a specific task.
Each section contains substantive information.

## Workflow

### Step 1: Read the input

Read the target file using the Read tool.

### Step 2: Process the content

Apply transformations based on the configuration.

```python
def process(content: str) -> str:
    lines = content.splitlines()
    return "\\n".join(line.strip() for line in lines)
```

### Step 3: Write the output

Write the processed content back to the file.

```bash
echo "Processing complete"
```

## Examples

### Example 1: Basic usage

```bash
/test-scorer-skill src/main.py
```

### Example 2: With options

```python
result = process("hello world")
assert result == "hello world"
```

## Output Checklist

- [ ] Input file was read successfully
- [ ] Content was processed correctly
- [ ] Output file was written
"""


def run_scorer(skill_dir: Path, *, json_output: bool = True) -> subprocess.CompletedProcess:
    cmd = ["python3", str(SCRIPT), str(skill_dir)]
    if json_output:
        cmd.append("--json")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)


def get_score(skill_dir: Path) -> dict:
    result = run_scorer(skill_dir)
    return json.loads(result.stdout)


class TestOverallScoring:
    def test_valid_skill_scores_high(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["overall_score"] >= 7.0
        assert data["passed"] is True
        assert data["recommendation"] == "APPROVE"

    def test_missing_skill_md_scores_zero(self, temp_skill_dir: Path) -> None:
        data = get_score(temp_skill_dir)
        assert data["overall_score"] == 0.0
        assert data["passed"] is False
        assert data["recommendation"] == "REJECT"

    def test_json_output_is_valid(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        result = run_scorer(temp_skill_dir)
        data = json.loads(result.stdout)
        assert "overall_score" in data
        assert "dimensions" in data
        assert len(data["dimensions"]) == 5

    def test_exit_code_0_when_passing(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        result = run_scorer(temp_skill_dir)
        assert result.returncode == 0

    def test_exit_code_1_when_failing(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text("no frontmatter here\n")
        result = run_scorer(temp_skill_dir)
        assert result.returncode == 1


class TestSpecCompliance:
    def test_valid_frontmatter_scores_10(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["spec_compliance"]["score"] == 10.0

    def test_missing_name_scores_low(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(
            "---\ndescription: No name field here.\n---\n\n# Test\n"
        )
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["spec_compliance"]["score"] < 7.0

    def test_missing_description_scores_low(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text("---\nname: no-desc\n---\n\n# Test\n")
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["spec_compliance"]["score"] <= 7.0

    def test_first_person_description_penalized(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: bad-desc\n"
            "description: I can help you process PDF files and extract text from them.\n"
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert spec["score"] < 10.0
        assert any("first person" in s.lower() for s in spec["negative"])

    def test_second_person_description_penalized(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: bad-desc\n"
            "description: You can use this to process PDF files and extract text.\n"
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert spec["score"] < 10.0
        assert any("second person" in s.lower() for s in spec["negative"])

    def test_third_person_description_not_penalized(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: good-desc\n"
            "description: Processes PDF files and extracts text. Use when working with PDF documents.\n"
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert not any("person" in s.lower() for s in spec["negative"])

    def test_description_with_trigger_context_gets_positive(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: trigger-desc\n"
            "description: Extracts text from PDFs. Use when working with PDF files or documents.\n"
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert any("trigger context" in s.lower() for s in spec["positive"])

    def test_description_missing_trigger_context_flagged(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: no-trigger\n"
            "description: Extracts text from PDF files and converts them to markdown format.\n"
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert any("trigger context" in s.lower() for s in spec["negative"])

    def test_quoted_trigger_phrases_get_positive(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: quoted-triggers\n"
            'description: This skill should be used when the user asks to "review code", "check quality", or "audit changes".\n'
            "---\n\n# Test\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert any("quoted trigger" in s.lower() for s in spec["positive"])

    def test_vague_description_penalized(self, temp_skill_dir: Path) -> None:
        content = "---\nname: vague-desc\ndescription: Helps with documents\n---\n\n# Test\n"
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        spec = data["dimensions"]["spec_compliance"]
        assert spec["score"] < 9.0
        assert any("vague" in s.lower() for s in spec["negative"])


class TestContentDepth:
    def test_placeholder_heavy_scores_low(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: bad-skill\ndescription: A skill full of placeholders.\n---\n\n"
            "# Bad Skill\n\n## Overview\n\nTODO add overview.\n\n"
            "## Workflow\n\nFIXME implement this.\n\n"
            "## Examples\n\nTBD add examples later.\n\nTODO more content.\nTODO finish this.\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["content_depth"]["score"] < 5.0

    def test_real_content_scores_high(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["content_depth"]["score"] >= 7.0

    def test_checklist_mentioning_placeholders_not_penalized(self, temp_skill_dir: Path) -> None:
        """Lines like 'No placeholder content (TODO, TBD)' should not count as placeholders."""
        content = (
            "---\nname: checklist-skill\ndescription: Has a checklist warning about placeholders.\n---\n\n"
            "# Checklist Skill\n\n## Overview\n\nReal content here.\n\n"
            "## Workflow\n\n1. Do the thing.\n2. Check results.\n\n"
            "## Output Checklist\n\n"
            "- [ ] No placeholder content (TODO, TBD, FIXME)\n"
            "- [ ] Remove all TODO items\n"
            "- [ ] Avoid TBD markers\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        # Should not be heavily penalized — these are instructions, not placeholders
        assert data["dimensions"]["content_depth"]["score"] >= 6.0

    def test_over_explanation_penalized(self, temp_skill_dir: Path) -> None:
        """Explaining basic concepts Claude knows (e.g., what PDFs are) is penalized."""
        content = (
            "---\nname: verbose-skill\n"
            "description: A verbose skill that over-explains basic concepts.\n---\n\n"
            "# Verbose Skill\n\n## Overview\n\n"
            "PDF is a format that stores documents in a portable way.\n"
            "JSON is a format that represents structured data.\n"
            "Git is a tool that tracks version history.\n"
            "Before we begin, let us understand the basics.\n\n"
            "## Workflow\n\n1. Process the file.\n2. Output results.\n\n"
            "## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert any("over-explain" in s.lower() for s in depth["negative"])

    def test_concise_content_not_penalized(self, temp_skill_dir: Path) -> None:
        """Direct, actionable content without over-explanation scores well."""
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert not any("over-explain" in s.lower() for s in depth["negative"])

    def test_time_sensitive_content_penalized(self, temp_skill_dir: Path) -> None:
        """References to specific dates or versions that will become stale are penalized."""
        content = (
            "---\nname: dated-skill\n"
            "description: A skill with time-sensitive content.\n---\n\n"
            "# Dated Skill\n\n## Overview\n\n"
            "As of January 2025, the API uses v2 endpoints.\n"
            "Before March 2024, use the legacy format.\n"
            "Currently in version 3.2, the default behavior changed.\n\n"
            "## Workflow\n\n1. Check the version.\n\n"
            "## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert any("time-sensitive" in s.lower() for s in depth["negative"])

    def test_content_without_dates_not_penalized(self, temp_skill_dir: Path) -> None:
        """Content without temporal references is not flagged."""
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert not any("time-sensitive" in s.lower() for s in depth["negative"])

    def test_inconsistent_terminology_penalized(self, temp_skill_dir: Path) -> None:
        """Using multiple terms for same concept (endpoint/route, function/method) is penalized."""
        content = (
            "---\nname: mixed-terms\n"
            "description: A skill mixing terminology for the same concepts.\n---\n\n"
            "# Mixed Terms\n\n## Overview\n\n"
            "Call the endpoint to get data. The route accepts JSON.\n"
            "The function parses input. The method returns output.\n\n"
            "## Workflow\n\n1. Hit the API route.\n\n"
            "## Examples\n\n```bash\ncurl /endpoint\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert any("terminology" in s.lower() or "mixed" in s.lower() for s in depth["negative"])

    def test_consistent_terminology_not_penalized(self, temp_skill_dir: Path) -> None:
        """Using one term consistently is not flagged."""
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert not any(
            "terminology" in s.lower() or "mixed" in s.lower() for s in depth["negative"]
        )

    def test_unqualified_mcp_tool_penalized(self, temp_skill_dir: Path) -> None:
        """MCP tool references without ServerName: prefix are penalized."""
        content = (
            "---\nname: mcp-skill\n"
            "description: A skill using MCP tools.\n---\n\n"
            "# MCP Skill\n\n## Overview\n\n"
            "Use the bigquery_schema tool to get table info.\n\n"
            "## Workflow\n\n1. Query schema.\n\n"
            "## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert any("mcp" in s.lower() or "unqualified" in s.lower() for s in depth["negative"])

    def test_multiple_alternatives_penalized(self, temp_skill_dir: Path) -> None:
        """Offering too many alternatives without a default is penalized."""
        content = (
            "---\nname: many-options\n"
            "description: A skill offering too many choices.\n---\n\n"
            "# Many Options\n\n## Overview\n\n"
            "You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image for extraction.\n\n"
            "## Workflow\n\n1. Pick a library.\n\n"
            "## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        depth = data["dimensions"]["content_depth"]
        assert any("alternative" in s.lower() for s in depth["negative"])


class TestExampleQuality:
    def test_no_code_blocks_scores_low(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: no-examples\ndescription: A skill with no code blocks at all.\n---\n\n"
            "# No Examples\n\n## Overview\n\nJust text.\n\n"
            "## Workflow\n\n1. Do something.\n\n## Examples\n\nSee documentation.\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["example_quality"]["score"] < 4.0

    def test_labeled_code_blocks_score_high(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["example_quality"]["score"] >= 7.0

    def test_magic_numbers_penalized(self, temp_skill_dir: Path) -> None:
        """Undocumented numeric constants in code blocks are penalized."""
        content = (
            "---\nname: magic-nums\n"
            "description: A skill with undocumented magic numbers.\n---\n\n"
            "# Magic Nums\n\n## Overview\n\nConfig skill.\n\n"
            "## Workflow\n\n```python\n"
            "TIMEOUT = 47\n"
            "MAX_RETRIES = 99\n"
            "BATCH_SIZE = 256\n"
            "```\n\n## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        examples = data["dimensions"]["example_quality"]
        assert any("magic" in s.lower() for s in examples["negative"])

    def test_documented_constants_not_penalized(self, temp_skill_dir: Path) -> None:
        """Constants with comments explaining the value are not flagged."""
        content = (
            "---\nname: doc-nums\n"
            "description: A skill with documented constants.\n---\n\n"
            "# Doc Nums\n\n## Overview\n\nConfig skill.\n\n"
            "## Workflow\n\n```python\n"
            "TIMEOUT = 30  # HTTP requests typically complete within 30s\n"
            "MAX_RETRIES = 3  # Most failures resolve by second retry\n"
            "```\n\n## Examples\n\n```bash\necho done\n```\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        examples = data["dimensions"]["example_quality"]
        assert not any("magic" in s.lower() for s in examples["negative"])


class TestStructure:
    def test_missing_overview_scores_low(self, temp_skill_dir: Path) -> None:
        content = (
            "---\nname: no-overview\ndescription: Missing overview section.\n---\n\n"
            "# Skill\n\nSome content without an overview heading.\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["structure"]["score"] < 6.0

    def test_good_structure_scores_high(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["structure"]["score"] >= 8.0

    def test_heading_level_skip_penalized(self, temp_skill_dir: Path) -> None:
        """Jumping from ## to #### without ### is penalized."""
        content = (
            "---\nname: skip-headings\n"
            "description: Skill with heading level skips. Use when testing structure.\n"
            "---\n\n# Skill\n\n## Overview\n\nContent.\n\n"
            "#### Deep heading without ###\n\nMore content.\n\n"
            "## Workflow\n\n1. Do thing.\n\n## Examples\n\nSee docs.\n"
        )
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        struct = data["dimensions"]["structure"]
        assert any("heading" in s.lower() and "skip" in s.lower() for s in struct["negative"])

    def test_nested_references_penalized(self, temp_skill_dir: Path) -> None:
        """SKILL.md -> a.md -> b.md is a nested reference chain."""
        (temp_skill_dir / "SKILL.md").write_text(
            "---\nname: nested-refs\n"
            "description: Skill with nested references. Use when testing progressive disclosure.\n"
            "---\n\n# Skill\n\n## Overview\n\nSee [a.md](a.md) for details.\n\n"
            "## Workflow\n\n1. Read a.md.\n\n## Examples\n\nSee docs.\n"
        )
        (temp_skill_dir / "a.md").write_text("# A\n\nSee [b.md](b.md) for more.\n")
        (temp_skill_dir / "b.md").write_text("# B\n\nDeep content.\n")
        data = get_score(temp_skill_dir)
        struct = data["dimensions"]["structure"]
        assert any("nested" in s.lower() for s in struct["negative"])

    def test_one_level_references_not_penalized(self, temp_skill_dir: Path) -> None:
        """SKILL.md -> a.md (no further links) is fine."""
        (temp_skill_dir / "SKILL.md").write_text(
            "---\nname: flat-refs\n"
            "description: Skill with flat references. Use when testing progressive disclosure.\n"
            "---\n\n# Skill\n\n## Overview\n\nSee [ref.md](ref.md) for API details.\n\n"
            "## Workflow\n\n1. Read ref.md.\n\n## Examples\n\nSee docs.\n"
        )
        (temp_skill_dir / "ref.md").write_text("# Reference\n\nNo further links here.\n")
        data = get_score(temp_skill_dir)
        struct = data["dimensions"]["structure"]
        assert not any("nested" in s.lower() for s in struct["negative"])
        assert any("one level deep" in s.lower() for s in struct["positive"])

    def test_long_reference_without_toc_penalized(self, temp_skill_dir: Path) -> None:
        """Reference files >100 lines should have a TOC."""
        long_content = "# Long Reference\n\n" + "\n".join(
            f"Line {i}: Some content here." for i in range(120)
        )
        (temp_skill_dir / "SKILL.md").write_text(
            "---\nname: long-ref\n"
            "description: Skill with long reference. Use when testing TOC detection.\n"
            "---\n\n# Skill\n\n## Overview\n\nSee [long.md](long.md).\n\n"
            "## Workflow\n\n1. Read long.md.\n\n## Examples\n\nSee docs.\n"
        )
        (temp_skill_dir / "long.md").write_text(long_content)
        data = get_score(temp_skill_dir)
        struct = data["dimensions"]["structure"]
        assert any("toc" in s.lower() for s in struct["negative"])

    def test_long_reference_with_toc_not_penalized(self, temp_skill_dir: Path) -> None:
        """Reference files >100 lines with TOC are fine."""
        long_content = (
            "# Long Reference\n\n## Contents\n\n- Section A\n- Section B\n\n"
            + "\n".join(f"Line {i}: Some content here." for i in range(120))
        )
        (temp_skill_dir / "SKILL.md").write_text(
            "---\nname: long-ref-toc\n"
            "description: Skill with long reference with TOC. Use when testing TOC detection.\n"
            "---\n\n# Skill\n\n## Overview\n\nSee [long.md](long.md).\n\n"
            "## Workflow\n\n1. Read long.md.\n\n## Examples\n\nSee docs.\n"
        )
        (temp_skill_dir / "long.md").write_text(long_content)
        data = get_score(temp_skill_dir)
        struct = data["dimensions"]["structure"]
        assert not any("toc" in s.lower() for s in struct["negative"])


class TestTokenEfficiency:
    def test_too_short_scores_low(self, temp_skill_dir: Path) -> None:
        content = "---\nname: tiny\ndescription: Too short.\n---\n\n# Tiny\n\nHello.\n"
        (temp_skill_dir / "SKILL.md").write_text(content)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["token_efficiency"]["score"] < 5.0

    def test_right_sized_scores_high(self, temp_skill_dir: Path) -> None:
        (temp_skill_dir / "SKILL.md").write_text(VALID_SKILL)
        data = get_score(temp_skill_dir)
        assert data["dimensions"]["token_efficiency"]["score"] >= 7.0

    def test_heavy_skill_without_refs_penalized(self, temp_skill_dir: Path) -> None:
        """SKILL.md > 3000 tokens with no references/ gets progressive disclosure penalty."""
        # Generate a large body (~3500 tokens ≈ ~2700 words)
        big_body = (
            "---\nname: heavy-skill\n"
            "description: A heavy skill without references. Use when testing.\n"
            "---\n\n# Heavy Skill\n\n## Overview\n\n"
        )
        # Add enough content to exceed 3000 tokens
        for i in range(150):
            big_body += (
                f"### Section {i}\n\n"
                f"This section provides detailed analysis of component {i} "
                f"covering architecture patterns, implementation details, "
                f"performance considerations, and testing strategies.\n\n"
            )
        (temp_skill_dir / "SKILL.md").write_text(big_body)
        data = get_score(temp_skill_dir)
        negatives = data["dimensions"]["token_efficiency"]["negative"]
        assert any("no references" in s.lower() for s in negatives)

    def test_heavy_skill_with_refs_not_penalized(self, temp_skill_dir: Path) -> None:
        """SKILL.md > 3000 tokens WITH references/ does not get the penalty."""
        big_body = (
            "---\nname: heavy-with-refs\n"
            "description: A heavy skill with references. Use when testing.\n"
            "---\n\n# Heavy Skill\n\n## Overview\n\n"
        )
        for i in range(150):
            big_body += (
                f"### Section {i}\n\n"
                f"This section provides detailed analysis of component {i} "
                f"covering architecture patterns, implementation details, "
                f"performance considerations, and testing strategies.\n\n"
            )
        (temp_skill_dir / "SKILL.md").write_text(big_body)
        refs_dir = temp_skill_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "details.md").write_text("# Detailed reference content\n\nExtra detail.\n")
        data = get_score(temp_skill_dir)
        negatives = data["dimensions"]["token_efficiency"]["negative"]
        assert not any("no references" in s.lower() for s in negatives)


class TestAdvancedPatternBonuses:
    """Tests for bonus signals rewarding advanced skill patterns."""

    def _make_skill(self, temp_skill_dir: Path, frontmatter: str, body: str) -> dict:
        (temp_skill_dir / "SKILL.md").write_text(frontmatter + body)
        return get_score(temp_skill_dir)

    def _base_body(self) -> str:
        """Substantial body that scores well on other dimensions."""
        return (
            "\n# Analyzer Skill\n\n"
            "## Overview\n\n"
            "Analyzes code for quality and performance issues across Python and "
            "TypeScript codebases. Produces structured reports with severity levels.\n\n"
            "## Workflow\n\n"
            "### Step 1: Scope Detection\n\n"
            "Determine analysis target from git diff or user arguments.\n\n"
            "### Step 2: Analysis\n\n"
            "Evaluate code against quality and efficiency checklists.\n\n"
            "### Step 3: Report\n\n"
            "Generate structured findings with file:line references.\n\n"
            "## Examples\n\n"
            "### Example 1: Standard Review\n\n"
            "```bash\n/review src/auth/\n```\n\n"
            "### Example 2: Focused Review\n\n"
            "```python\ndef validate(data: dict) -> bool:\n    return bool(data.get('id'))\n```\n\n"
            "## Metrics\n\n"
            "| Metric | Good | Warning | Bad |\n"
            "|--------|------|---------|-----|\n"
            "| Cyclomatic complexity | 1-5 | 6-10 | >10 |\n"
            "| Function length | 1-25 | 26-50 | >50 |\n"
        )

    def test_parallel_agents_bonus(self, temp_skill_dir: Path) -> None:
        """Skills with Task tool and parallel workflow get bonus."""
        fm = (
            "---\nname: parallel-analyzer\n"
            "description: Analyzes code with parallel agents. Use when reviewing code quality.\n"
            "allowed-tools:\n  - Read\n  - Task\n---\n"
        )
        body = self._base_body().replace(
            "### Step 2: Analysis",
            "### Step 2: Parallel Analysis\n\n"
            "Launch all agents in a single message for concurrent execution.\n\n"
            "### Step 2b: Quality",
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        positives = data["dimensions"]["content_depth"]["positive"]
        assert any("parallel" in s.lower() for s in positives)

    def test_auto_fix_bonus(self, temp_skill_dir: Path) -> None:
        """Skills with Edit tool and fix workflow get bonus."""
        fm = (
            "---\nname: fixing-analyzer\n"
            "description: Analyzes and fixes code issues. Use when cleaning up code.\n"
            "allowed-tools:\n  - Read\n  - Edit\n---\n"
        )
        body = self._base_body() + (
            "\n## Fix Phase\n\nApply fixes for critical issues. Auto-fix unambiguous problems.\n"
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        positives = data["dimensions"]["content_depth"]["positive"]
        assert any("auto-fix" in s.lower() or "fix" in s.lower() for s in positives)

    def test_claude_md_integration_bonus(self, temp_skill_dir: Path) -> None:
        """Skills referencing CLAUDE.md conventions get bonus."""
        fm = (
            "---\nname: convention-analyzer\n"
            "description: Analyzes code respecting project conventions. Use when reviewing.\n"
            "allowed-tools:\n  - Read\n---\n"
        )
        body = self._base_body().replace(
            "### Step 1: Scope Detection",
            "### Step 0: Read Project Conventions\n\n"
            "Read the project's CLAUDE.md for coding standards and patterns.\n\n"
            "### Step 1: Scope Detection",
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        positives = data["dimensions"]["content_depth"]["positive"]
        assert any("claude.md" in s.lower() for s in positives)

    def test_argument_hint_bonus(self, temp_skill_dir: Path) -> None:
        """Skills with argument-hint get bonus."""
        fm = (
            "---\nname: hinted-analyzer\n"
            "description: Analyzes code with focus area support. Use when reviewing.\n"
            'argument-hint: "[focus area]"\n'
            "allowed-tools:\n  - Read\n---\n"
        )
        data = self._make_skill(temp_skill_dir, fm, self._base_body())
        positives = data["dimensions"]["content_depth"]["positive"]
        assert any("argument-hint" in s.lower() for s in positives)

    def test_claude_skill_dir_bonus(self, temp_skill_dir: Path) -> None:
        """Skills using ${CLAUDE_SKILL_DIR} for script refs get bonus."""
        fm = (
            "---\nname: portable-skill\n"
            "description: A skill with portable script references. Use when running scripts.\n"
            "allowed-tools:\n  - Read\n  - Bash\n---\n"
        )
        body = self._base_body().replace(
            "### Step 2: Analysis",
            "### Step 2: Run Script\n\n"
            "```bash\nbash ${CLAUDE_SKILL_DIR}/scripts/analyze.sh\n```\n\n"
            "### Step 2b: Analysis",
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        positives = data["dimensions"]["content_depth"]["positive"]
        assert any("CLAUDE_SKILL_DIR" in s for s in positives)

    def test_hardcoded_script_path_suggests_portable(self, temp_skill_dir: Path) -> None:
        """Skills with hardcoded scripts/ paths get a suggestion to use ${CLAUDE_SKILL_DIR}."""
        fm = (
            "---\nname: hardcoded-skill\n"
            "description: A skill with hardcoded script path. Use when running scripts.\n"
            "allowed-tools:\n  - Read\n  - Bash\n---\n"
        )
        body = self._base_body().replace(
            "### Step 2: Analysis",
            "### Step 2: Run Script\n\n"
            "```bash\nbash scripts/analyze.sh\n```\n\n"
            "### Step 2b: Analysis",
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        suggestions = data["dimensions"]["content_depth"]["suggestions"]
        assert any("CLAUDE_SKILL_DIR" in s for s in suggestions)

    def test_argument_hint_without_arguments_warns(self, temp_skill_dir: Path) -> None:
        """argument-hint declared but no $ARGUMENTS in body flags a warning."""
        fm = (
            "---\nname: hint-no-args\n"
            "description: A skill with argument hint but no placeholders. Use when testing.\n"
            'argument-hint: "[target]"\n'
            "allowed-tools:\n  - Read\n---\n"
        )
        data = self._make_skill(temp_skill_dir, fm, self._base_body())
        negatives = data["dimensions"]["content_depth"]["negative"]
        assert any("argument-hint" in s.lower() and "no $ARGUMENTS" in s for s in negatives)

    def test_arguments_without_hint_suggests(self, temp_skill_dir: Path) -> None:
        """$ARGUMENTS used but no argument-hint suggests adding it."""
        fm = (
            "---\nname: args-no-hint\n"
            "description: A skill using arguments without hint. Use when testing.\n"
            "allowed-tools:\n  - Read\n---\n"
        )
        body = self._base_body().replace(
            "### Step 1: Scope Detection",
            "### Step 1: Parse Arguments\n\n"
            "Target path is provided via $ARGUMENTS.\n\n"
            "### Step 1b: Scope Detection",
        )
        data = self._make_skill(temp_skill_dir, fm, body)
        suggestions = data["dimensions"]["content_depth"]["suggestions"]
        assert any("argument-hint" in s.lower() for s in suggestions)

    def test_no_bonus_without_patterns(self, temp_skill_dir: Path) -> None:
        """Skills without advanced patterns don't get false bonuses."""
        fm = (
            "---\nname: basic-analyzer\n"
            "description: Basic analysis skill. Use when reviewing code.\n"
            "allowed-tools:\n  - Read\n---\n"
        )
        data = self._make_skill(temp_skill_dir, fm, self._base_body())
        positives = data["dimensions"]["content_depth"]["positive"]
        assert not any("parallel" in s.lower() for s in positives)
        assert not any("auto-fix" in s.lower() for s in positives)
        assert not any("claude.md" in s.lower() for s in positives)
        assert not any("argument-hint" in s.lower() for s in positives)
