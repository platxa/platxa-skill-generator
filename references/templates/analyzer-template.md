# Analyzer Skill Template

Template for skills that inspect or audit code/data.

## SKILL.md Structure

```yaml
---
name: {skill-name}
description: {Analyzes X for Y. Reports on Z metrics.}
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
metadata:
  version: "1.0.0"
  author: "{author}"
  tags:
    - analyzer
    - audit
    - {domain}
---

# {Skill Name}

{One-line description of what this skill analyzes.}

## Overview

This skill analyzes {target} to identify {what it finds}. It's designed for {target users} who need to understand {aspect}.

**What it analyzes:**
- {Analysis target 1}
- {Analysis target 2}

**What it reports:**
- {Report output 1}
- {Report output 2}

## Analysis Checklist

### {Category 1}

- [ ] {Check item 1}
- [ ] {Check item 2}
- [ ] {Check item 3}

### {Category 2}

- [ ] {Check item 1}
- [ ] {Check item 2}

### {Category 3}

- [ ] {Check item 1}
- [ ] {Check item 2}

## Metrics

### {Metric Category 1}

| Metric | Description | Good | Warning | Bad |
|--------|-------------|------|---------|-----|
| {metric1} | {what it measures} | {range} | {range} | {range} |
| {metric2} | {what it measures} | {range} | {range} | {range} |

### {Metric Category 2}

| Metric | Description | Target |
|--------|-------------|--------|
| {metric1} | {what it measures} | {value} |
| {metric2} | {what it measures} | {value} |

## Report Format

### Summary

```
{Skill Name} Analysis Report
============================
Target: {what was analyzed}
Date: {timestamp}

Overall Score: X/10

Key Findings:
- {Finding 1}
- {Finding 2}
```

### Detailed Report

```
## {Section 1}
{Detailed findings}

## {Section 2}
{Detailed findings}

## Recommendations
1. {Recommendation 1}
2. {Recommendation 2}
```

## Examples

### Example 1: {Standard Analysis}

```
User: /{skill-command} {target}
Assistant: Analyzing {target}...

## Analysis Report

**Score: 7.5/10**

### {Category 1}
✓ {Passed check}
⚠ {Warning}
✗ {Failed check}

### Recommendations
1. {What to improve}
```

### Example 2: {Focused Analysis}

```
User: /{skill-command} --focus {category}
Assistant: Focused analysis on {category}:
{Detailed category-specific report}
```

## Interpretation Guide

### Score Meanings

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Excellent | Maintain current practices |
| 7-8 | Good | Minor improvements suggested |
| 5-6 | Fair | Significant improvements needed |
| <5 | Poor | Immediate attention required |

### Priority Levels

- 🔴 **Critical**: Must address immediately
- 🟠 **High**: Address soon
- 🟡 **Medium**: Plan to address
- 🟢 **Low**: Nice to have
```

## Visual Output (Optional)

For data-rich analyzer skills, consider bundling a Python script that generates an
interactive HTML report:

```python
# scripts/visualize.py — generates self-contained HTML report
# Usage: python scripts/visualize.py <analysis-output.json>
# Opens in browser automatically

import json, webbrowser
from pathlib import Path

def generate_html(data: dict, output: Path) -> None:
    # Build self-contained HTML with embedded CSS/JS
    # Include: summary sidebar, bar charts, collapsible sections
    html = f"<!DOCTYPE html>..."  # Full HTML with data embedded
    output.write_text(html)

if __name__ == "__main__":
    # Load analysis data, generate HTML, open in browser
    webbrowser.open(f"file://{output.absolute()}")
```

This pattern works for: dependency graphs, coverage reports, metric dashboards, schema visualizations.

## Key Sections for Analyzers

1. **Checklist**: What to inspect
2. **Metrics**: Quantitative measures
3. **Report Format**: Output structure
4. **Interpretation**: Help users understand results
5. **Visual Output**: Optional HTML visualization script
