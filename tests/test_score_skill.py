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
description: A well-written skill for testing the quality scorer with real content.
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
