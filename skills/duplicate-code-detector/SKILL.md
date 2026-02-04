---
name: duplicate-code-detector
description: Proactive duplicate code detection at feature boundaries. Scans for exact, near, and structural duplicates using AST-aware analysis and suggests refactoring opportunities.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
metadata:
  version: "1.0.0"
  tags:
    - code-quality
    - refactoring
    - duplicate-detection
---

# Duplicate Code Detector

Proactive duplicate code detection that runs at feature boundaries to prevent code duplication before it happens.

## Overview

This skill replaces inline AST-based duplicate detection with a lightweight, subagent-driven approach. Instead of maintaining a persistent codebase index, it performs targeted scans at feature start and before commits.

**What it detects:**
- Exact duplicates (copy-pasted code blocks)
- Near-duplicates (similar logic with renamed variables or minor edits)
- Structural duplicates (same patterns across different files)
- Reuse opportunities (existing utilities that could replace new code)

## Workflow

### 1. Feature Start Scan

When a new feature begins, scan files likely to be modified:

```
1. Identify files in the feature's target area (Glob)
2. Search for similar function signatures (Grep)
3. Read candidate files and compare patterns (Read)
4. Report findings with file paths and line numbers
```

### 2. Pre-Commit Check

Before committing, scan changed files for duplication:

```
1. Get list of staged files (Bash: git diff --cached --name-only)
2. For each modified file, search for similar code elsewhere
3. Flag functions/classes that duplicate existing code
4. Suggest extraction into shared utilities
```

### 3. Detection Strategies

#### Function Signature Matching
Search for functions with similar names or parameter patterns:
```bash
# Find functions with similar names
grep -r "def calculate_" src/ --include="*.py"
grep -r "function validate" src/ --include="*.ts"
```

#### Import Pattern Analysis
Identify files importing the same modules (likely similar functionality):
```bash
# Find files with identical import blocks
grep -rn "^from.*import" src/ --include="*.py" | sort -t: -k2
```

#### Structural Pattern Matching
Look for repeated code structures:
- Multiple files with identical class hierarchies
- Repeated error handling patterns
- Duplicated configuration parsing

## Output Format

Report findings as:

```
DUPLICATE DETECTED:
  Source: src/module_a/handler.py:45-67
  Match:  src/module_b/processor.py:112-134
  Type:   Near-duplicate (92% similarity)
  Action: Extract to shared utility in src/common/helpers.py

REUSE OPPORTUNITY:
  New code: src/feature/validator.py:20-35
  Existing: src/utils/validation.py:validate_input()
  Action: Import existing function instead of reimplementing
```

## Configuration

The skill uses environment-based configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DUPLICATE_MIN_LINES` | `5` | Minimum lines for a block to be checked |
| `DUPLICATE_SCAN_DEPTH` | `3` | Directory depth for scanning |
| `DUPLICATE_EXTENSIONS` | `.py,.ts,.js` | File extensions to scan |

## Integration

This skill is designed to be invoked by the `duplicate-check` Task subagent during feature workflows. It can also be triggered manually for ad-hoc scans.
