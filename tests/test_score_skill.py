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
description: A well-written skill for testing the quality scorer with real content. Use when validating skill quality or when the user asks for a quality check.
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
