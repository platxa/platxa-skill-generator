---
name: duplicate-code-detector
description: Proactive duplicate code detection at feature boundaries. Classifies clones by type (exact, renamed, structural, semantic), scans incrementally on changed files, and reports findings with similarity scores and refactoring actions.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
metadata:
  version: "2.0.0"
  tags:
    - code-quality
    - refactoring
    - duplicate-detection
    - analyzer
---

# Duplicate Code Detector

Detect and prevent code duplication at feature boundaries using incremental, tool-driven analysis.

## Overview

This skill performs targeted duplicate code scans at key development moments: when starting a feature, before committing, or on demand. It uses Claude Code's built-in tools (Grep, Glob, Read) instead of external dependencies, making it zero-setup and language-agnostic.

The detector classifies findings using the industry-standard clone taxonomy (Type-1 through Type-4), reports similarity scores, and provides actionable refactoring suggestions with exact file locations.

**Design principle:** Scan only changed or relevant files incrementally, never the entire codebase.

## Clone Type Classification

| Type | Name | Description | Detection Method |
|------|------|-------------|-----------------|
| Type-1 | Exact | Identical code, differs only in whitespace/comments | Grep exact patterns |
| Type-2 | Renamed | Identical structure, renamed identifiers or changed literals | Grep function signatures, compare structure |
| Type-3 | Structural | Similar code with added/removed/modified statements | Read and compare logic blocks |
| Type-4 | Semantic | Different syntax, same functionality | Manual review of candidates |

## Analysis Checklist

### Function-Level Checks
- [ ] Search for functions with identical or similar names across the codebase
- [ ] Compare parameter signatures of related functions
- [ ] Check for functions with identical return types and similar bodies
- [ ] Identify wrapper functions that add no logic

### File-Level Checks
- [ ] Compare import blocks between files in the same directory
- [ ] Search for files with matching class hierarchies
- [ ] Detect repeated configuration or setup patterns
- [ ] Flag files with overlapping responsibilities

### Pattern-Level Checks
- [ ] Identify repeated error handling blocks (try/catch with same structure)
- [ ] Find duplicated validation logic
- [ ] Detect copy-pasted API call patterns
- [ ] Search for repeated data transformation pipelines

## Workflow

### 1. Feature Start Scan

When beginning a feature, identify existing code to reuse:

```
1. Glob for files in the target area matching the feature domain
2. Grep for function/class names related to the feature keywords
3. Read top candidates (limit to 5-10 files) and catalog:
   - Existing utility functions
   - Helper classes
   - Shared constants and types
4. Report reuse opportunities before any code is written
```

### 2. Pre-Commit Scan

Before committing, compare staged changes against the codebase:

```
1. Run: git diff --cached --name-only (Bash)
2. For each changed file:
   a. Extract new/modified function signatures (Read)
   b. Grep the codebase for matching signatures (Grep)
   c. Read matches and assess similarity (Read)
3. Flag duplicates above the similarity threshold
4. Suggest refactoring: extract to shared module or import existing
```

### 3. Ad-Hoc Scan

Run on any set of files or directories when requested:

```
1. Glob for target files by pattern (e.g., "src/services/**/*.ts")
2. Cross-compare function signatures within the file set
3. Report clusters of similar code with locations
```

## Detection Strategies

### Function Signature Matching

Use Grep to find functions with similar names or parameter patterns:

```
Grep pattern: "def (calculate|compute|get)_\w+" in *.py files
Grep pattern: "function (validate|check|verify)\w+" in *.ts files
Grep pattern: "func (Parse|Format|Convert)\w+" in *.go files
```

Compare matches by: name similarity, parameter count, return type.

### Import Clustering

Files importing the same set of modules often contain similar logic:

```
1. Grep for import statements across the target directory
2. Group files by shared imports (3+ identical imports = candidate)
3. Read grouped files and compare exported functions
```

### Structural Pattern Search

Detect repeated code structures:

```
Grep for repeated patterns:
- "try {" ... "catch" blocks with identical error types
- Switch/match statements with the same case structure
- Builder or factory patterns with identical method chains
```

## Metrics and Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Minimum lines to flag | 5 lines | Ignore blocks shorter than this |
| Exact match (Type-1) | 100% | Always flag |
| Near match (Type-2) | ≥ 80% similar | Flag with refactoring suggestion |
| Structural match (Type-3) | ≥ 70% similar | Flag as review candidate |
| Maximum files per scan | 50 files | Limit scope for performance |
| Scan exclusions | `node_modules/`, `vendor/`, `dist/`, `*.min.*`, `__pycache__/` | Always skip |

## Report Format

### Summary

```
DUPLICATE SCAN RESULTS
──────────────────────
Scope:    12 files analyzed (src/services/)
Trigger:  Pre-commit scan
Findings: 3 duplicates, 1 reuse opportunity
```

### Detailed Findings

```
🔴 CRITICAL — Type-1 Exact Duplicate
   Source: src/services/auth.py:45-67 (23 lines)
   Match:  src/services/session.py:112-134 (23 lines)
   Score:  100% identical
   Action: Extract to src/common/token_utils.py

🟠 HIGH — Type-2 Renamed Clone
   Source: src/handlers/order.ts:20-38 (19 lines)
   Match:  src/handlers/invoice.ts:55-73 (19 lines)
   Score:  91% similar (only variable names differ)
   Action: Parameterize into shared handler function

🟡 MEDIUM — Type-3 Structural Clone
   Source: src/api/users.py:100-125 (26 lines)
   Match:  src/api/products.py:80-108 (29 lines)
   Score:  74% similar (3 extra statements in match)
   Action: Review for extraction into base API class

🟢 REUSE OPPORTUNITY
   New code:  src/feature/validate.py:10-22
   Existing:  src/utils/validators.py:validate_email()
   Action:    Import existing function instead of reimplementing
```

### Priority Levels

| Priority | Meaning | Action Required |
|----------|---------|-----------------|
| 🔴 Critical | Exact duplicate, must fix | Extract before merging |
| 🟠 High | Near-duplicate, strong match | Refactor recommended |
| 🟡 Medium | Structural similarity | Review and decide |
| 🟢 Info | Reuse opportunity | Consider importing |

## Examples

### Example 1: Feature Start Scan

```
User: I'm about to add a discount calculation feature to the sales module
Assistant: Running duplicate scan on sales module...

Scanning src/sales/ for existing discount/pricing logic:
- Glob: src/sales/**/*.py → 8 files found
- Grep: "def.*discount\|def.*price\|def.*calculate" → 3 matches

REUSE OPPORTUNITIES FOUND:
🟢 src/sales/pricing.py:45 — calculate_line_discount()
   Already handles percentage and fixed discounts
🟢 src/sales/utils.py:12 — apply_tax_rules()
   Includes discount-before-tax logic
🟢 src/common/money.py:8 — round_currency()
   Currency rounding utility

Recommendation: Extend calculate_line_discount() in pricing.py
rather than creating a new discount function.
```

### Example 2: Pre-Commit Duplicate Detection

```
User: Check my staged changes for duplicates before I commit
Assistant: Scanning staged files...

Staged files: 3 modified
- src/api/orders.py (42 lines changed)
- src/api/returns.py (38 lines changed)
- src/models/refund.py (15 lines changed)

🟠 HIGH — Type-2 Clone Detected
   src/api/orders.py:88-105 ≈ src/api/returns.py:62-79
   Both implement validate_line_items() with identical logic,
   only the variable name differs (order_lines vs return_lines).
   Score: 94% similar

   Action: Extract to src/api/common.py:validate_line_items(lines)
   and call from both modules.

No other duplicates found. 1 issue to resolve before commit.
```

## Exclusions

Always skip these during scans:
- **Generated code**: protobuf, GraphQL schema outputs, OpenAPI clients
- **Vendor/dependencies**: `node_modules/`, `vendor/`, `.venv/`
- **Build artifacts**: `dist/`, `build/`, `__pycache__/`
- **Test fixtures**: Mock data files, snapshot files
- **Minified files**: `*.min.js`, `*.min.css`
- **Lock files**: `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`

## Output Checklist

- [ ] All staged/target files were scanned
- [ ] Clone type classification applied to each finding
- [ ] Similarity score reported for each match
- [ ] File paths include line numbers (file:line-line)
- [ ] Refactoring action suggested for each finding
- [ ] Priority level assigned (Critical/High/Medium/Info)
- [ ] Exclusion patterns respected (no vendor/generated code flagged)
- [ ] Findings sorted by priority (critical first)
