---
name: platxa-code-review
description: >-
  Analyzes code for quality, security, efficiency, and maintainability across any language.
  Use when the user asks to "review code", "review my changes", "check code quality",
  "security review", "audit this code", "review the diff", or "code review".
  Reviews files or git diffs using parallel sub-agents per dimension, produces structured
  reports with weighted scores and actionable recommendations. Supports auto-fix for
  unambiguous issues and respects project conventions from CLAUDE.md.
metadata:
  version: "4.0.0"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Task
user-invocable: true
argument-hint: "[file|directory|--fix|--minimum SEVERITY|--focus DIMENSION|--codebase]"
---

# Platxa Code Review

Language-agnostic code review with parallel analysis, weighted scoring, and optional auto-fix.

## Overview

Analyzes code across four dimensions using parallel sub-agents:

| Dimension | Weight | What It Catches |
|-----------|--------|-----------------|
| Code Quality | 0.30 | Complexity, duplication, naming, SOLID violations |
| Security | 0.25 | Hardcoded secrets, injection, auth gaps, data exposure |
| Efficiency | 0.25 | N+1 queries, loop allocations, blocking I/O, unbounded growth |
| Maintainability | 0.20 | Type safety, error handling, documentation, testability |

**Modes:** File review, diff review (default), or systematic codebase review.
**Languages:** Python, TypeScript/JavaScript, Go, Java, Rust, C/C++, and any readable source.

## Workflow

### Step 0: Read Project Conventions

Check the project's CLAUDE.md files (loaded automatically by Claude Code):

- **Coding standards**: Style preferences, naming conventions, patterns
- **Prohibited patterns**: Things the project explicitly bans
- **Required patterns**: Mandatory conventions (test frameworks, linters)
- **Tech stack**: Frameworks, languages, libraries in use

Convention rules:
- If CLAUDE.md permits a pattern, suppress findings about it
- If CLAUDE.md prohibits a pattern, elevate findings to HIGH severity
- If no CLAUDE.md exists, use built-in defaults without warning

### Step 1: Determine Scope

Parse `$ARGUMENTS` for mode and options:

| Argument | Effect |
|----------|--------|
| `<path>` | Analyze specific file or directory |
| `--fix` | Enable auto-fix for unambiguous CRITICAL/HIGH issues |
| `--minimum <SEVERITY>` | Only report findings at or above this severity (default: MEDIUM) |
| `--focus <DIMENSION>` | Run single-dimension analysis inline (skip parallelism) |
| `--codebase` | Systematic full-project review (see `references/codebase-review-guide.md`) |

**Scope detection cascade** (first match wins):

1. User provided explicit path in `$ARGUMENTS` -- use it
2. Git has changes -- analyze changed files:

**Changed files in this repository:**
!`git diff --name-only 2>/dev/null | head -30`
!`git diff --cached --name-only 2>/dev/null | head -30`

3. Nothing found -- ask the user what to analyze

### Step 2: Automated Checks

Run helper scripts on target files:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/detect-secrets.sh <file-or-directory>
bash ${CLAUDE_SKILL_DIR}/scripts/analyze-complexity.sh <file-or-directory>
```

### Step 3: Parallel Deep Analysis

Launch four dimension agents in a SINGLE Task tool message for concurrent execution.
Each agent receives the file list and analyzes ONLY its assigned dimension.
Each agent outputs findings as: `file:line -- SEVERITY -- description (confidence: HIGH)`.

**Agent 1: Code Quality** (weight 0.30)
- Cyclomatic complexity per function (target: <10)
- Function length (target: <50 lines), nesting depth (target: <4)
- Code duplication (target: <5%), naming clarity
- SOLID principle adherence
- Dead code, unused imports

**Agent 2: Security** (weight 0.25)
- Hardcoded secrets (auto-fail if found)
- SQL/command injection, eval with dynamic input
- Input validation at boundaries, auth/access checks
- Sensitive data in logs or error messages
- Path traversal, SSRF vectors

**Agent 3: Efficiency** (weight 0.25)
- N+1 query patterns, fetch-all-then-filter
- String concatenation in loops, unnecessary allocations
- Unbounded collection growth, blocking I/O in async
- Missing early returns, redundant computation
- See `references/efficiency-patterns.md` for language-specific detection

**Agent 4: Maintainability** (weight 0.20)
- Type annotations on public APIs, no `any` types
- Specific exception handling (no bare catch-all, no empty catch)
- Public API documentation, inline comments for non-obvious logic
- Dependency injection, testability, consistent formatting

For focused reviews (`--focus <dimension>`), skip parallelism and analyze inline.

### Step 4: Aggregate and Filter

Merge findings from all agents. Apply filters before reporting:

1. **Auto-skip**: Remove findings in auto-generated, vendor, build output, and lock files
2. **Context filter**: Remove pattern matches in comments, strings, and documentation
3. **Confidence filter**: Only report HIGH confidence findings -- when uncertain, omit
4. **Deduplicate same location**: Same file:line across agents -- keep highest severity
5. **Deduplicate same pattern**: Same issue in multiple files -- group with count
6. **Root cause**: Multiple symptoms from one cause -- report cause once, list symptoms
7. **Actionability**: Skip if developer cannot act on it or fix cost exceeds value
8. **Minimum severity**: Apply `--minimum` threshold (default: MEDIUM)

Calculate weighted score per `references/scoring-framework.md`.

Apply hard-fail rules:
- Hardcoded secrets detected -- cap at 4.0
- Critical security vulnerability -- cap at 5.0
- Syntax errors present -- cap at 3.0

### Step 5: Report

Generate structured report (see Report Format below).

Prioritize recommendations:
- **Critical**: Must fix before merge
- **High**: Should fix before merge
- **Medium**: Plan to address
- **Low**: Consider improving

### Step 6: Auto-Fix (when invoked with --fix)

Only applies when the user passes `--fix` or explicitly requests fixes.

1. **Filter fixable issues**: CRITICAL and HIGH severity only, unambiguous single-solution
2. **Apply fixes**: Use Edit tool, one fix per call, preserve surrounding code
3. **Verify**: Re-run automated checks on modified files
4. **Report**: What was fixed vs what needs manual attention

Fixable: unused imports, hardcoded secrets to env var, missing type hints, string concat to join, missing null checks.
Not fixable: N+1 queries (architectural), SOLID violations (multiple approaches), auth flow issues (security decisions).

## Codebase Review Mode

For full-codebase reviews (`--codebase`), follow `references/codebase-review-guide.md`:

1. **Discovery** -- Map modules, count files by language, identify review order
2. **Automated Sweep** -- Run detect-secrets and analyze-complexity on entire codebase
3. **Module-by-Module** -- Score each module independently across all 4 dimensions
4. **Cross-Cutting** -- Check consistency, duplication, and dependency flow across modules
5. **Consolidated Report** -- Module scores table, hotspots, top priority fixes

Review order (highest risk first): auth > API > data access > business logic > utilities > config > tests.

## Analysis Checklist

### Code Quality
- [ ] Functions have single responsibility
- [ ] Cyclomatic complexity < 10 per function
- [ ] No functions > 50 lines
- [ ] Nesting depth < 4 levels
- [ ] No duplicated code blocks (3+ lines)
- [ ] Names are descriptive and consistent
- [ ] No dead code or unused imports

### Security
- [ ] No hardcoded secrets, API keys, or tokens
- [ ] No SQL string concatenation (use parameterized queries)
- [ ] No shell command injection (no unescaped user input)
- [ ] User input validated at system boundaries
- [ ] No eval() with dynamic input
- [ ] Sensitive data not logged or exposed in errors

### Efficiency
- [ ] No N+1 query patterns
- [ ] No unnecessary object creation in loops
- [ ] No string concatenation in loops (use builder/join)
- [ ] Collections have bounded growth
- [ ] Async operations not blocking event loop
- [ ] Early returns prevent unnecessary work

### Maintainability
- [ ] Type annotations on public APIs
- [ ] Errors handled with specific types (no bare catch-all)
- [ ] No silent failures (no empty catch blocks)
- [ ] Public functions have documentation
- [ ] Dependencies are injectable (testable)
- [ ] Consistent formatting throughout

## Metrics

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Cyclomatic complexity | 1-5 | 6-10 | >10 |
| Cognitive complexity | 1-9 | 10-19 | >19 |
| Function length | 1-25 | 26-50 | >50 |
| Nesting depth | 1-2 | 3 | >3 |
| File length | 1-300 | 301-500 | >500 |
| Duplication ratio | <5% | 5-10% | >10% |
| Type coverage | >90% | 70-90% | <70% |

## Report Format

```markdown
## Code Review Report

**Target:** {files or diff description}
**Date:** {timestamp}
**Files analyzed:** {count}
**Lines of code:** {total}

### Overall: {score}/10 (Grade {letter}) -- {verdict}

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Code Quality | {x}/10 | 0.30 | {w} |
| Security | {x}/10 | 0.25 | {w} |
| Efficiency | {x}/10 | 0.25 | {w} |
| Maintainability | {x}/10 | 0.20 | {w} |
| **Overall** | | | **{total}/10** |

### Issues Found

**Critical**
- [{id}] {file}:{line} -- {description}

**High**
- [{id}] {file}:{line} -- {description}

**Medium**
- [{id}] {file}:{line} -- {description}

### Recommendations
1. [Critical] {actionable fix}
2. [High] {actionable fix}
3. [Medium] {actionable fix}
```

| Score | Grade | Verdict |
|-------|-------|---------|
| 9.0-10.0 | A | APPROVE |
| 8.0-8.9 | B | APPROVE |
| 7.0-7.9 | C | APPROVE with suggestions |
| 5.0-6.9 | D | REQUEST CHANGES |
| <5.0 | F | REJECT |

## Examples

### Example 1: Review Git Diff (Default)

```
User: /platxa-code-review
Assistant: [Reads CLAUDE.md conventions...]
[Detects 3 changed files from git diff...]
[Runs detect-secrets.sh and analyze-complexity.sh...]
[Launches 4 parallel dimension agents...]

## Code Review Report

**Target:** 3 files changed (unstaged)
**Files analyzed:** 3 | **Lines:** 380

### Overall: 7.2/10 (Grade C) -- APPROVE WITH SUGGESTIONS

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Code Quality | 7.5 | 0.30 | 2.25 |
| Security | 8.0 | 0.25 | 2.00 |
| Efficiency | 6.5 | 0.25 | 1.63 |
| Maintainability | 6.5 | 0.20 | 1.30 |
| **Overall** | | | **7.18/10** |

### Issues Found

**High**
- [EFF-1] services/order.py:89 -- N+1 query: fetching customer inside order loop
- [CQ-1] handlers/auth.py:45 -- process_login() cyclomatic complexity 12

**Medium**
- [MT-1] handlers/auth.py:1-180 -- No type hints on 6/10 public functions
- [EFF-2] utils/format.py:23 -- String concatenation in loop (use join)

### Recommendations
1. [High] Batch customer queries with JOIN or prefetch_related
2. [High] Extract process_login() into validate_credentials() + create_session()
3. [Medium] Add type annotations to public functions in auth handler
```

### Example 2: Review with Auto-Fix

```
User: /platxa-code-review src/config.py --fix
Assistant: [Analyzes src/config.py...]

## Code Review Report

**Target:** src/config.py
**Files analyzed:** 1 | **Lines:** 85

### Overall: 7.8/10 (Grade C) -- APPROVE WITH SUGGESTIONS

### Issues Found

**Critical**
- [SEC-1] config.py:15 -- Hardcoded API key

**Medium**
- [CQ-1] config.py:42 -- Unused import: json

### Fixes Applied (2)
- [FIX-1] config.py:15 -- Replaced hardcoded key with os.environ.get("API_KEY")
- [FIX-2] config.py:42 -- Removed unused import

### Requires Manual Fix (0)
No issues requiring manual intervention.
```

### Example 3: Focused Security Review

```
User: /platxa-code-review --focus security src/api/
Assistant: [Focused security analysis of src/api/...]

## Code Review Report -- Security Focus

**Target:** src/api/ (8 files)

### Security: 6.0/10 (Grade D) -- REQUEST CHANGES

**Critical**
- [SEC-1] api/auth.py:42 -- Hardcoded JWT secret in source
- [SEC-2] api/users.py:78 -- SQL concatenation with user input

**High**
- [SEC-3] api/upload.py:31 -- No path traversal check on filename
- [SEC-4] api/auth.py:95 -- Failed login exposes whether email exists

### Recommendations
1. [Critical] Move JWT secret to environment variable
2. [Critical] Use parameterized query for user lookup
3. [High] Sanitize upload filename with os.path.basename()
4. [High] Use generic "invalid credentials" message
```

### Example 4: Systematic Codebase Review

```
User: /platxa-code-review --codebase
Assistant: Starting systematic codebase review...

## Codebase Review Report

**Project:** my-api | **Modules:** 4 | **Files:** 32 | **Lines:** 4,800

### Overall: 7.4/10 (Grade C) -- APPROVE WITH SUGGESTIONS

| Module | Quality | Security | Efficiency | Maint. | Overall |
|--------|---------|----------|------------|--------|---------|
| auth/     | 7.0  | 5.5  | 8.0  | 7.0  | 6.8  |
| api/      | 8.0  | 8.5  | 7.0  | 8.0  | 7.9  |
| services/ | 7.5  | 9.0  | 6.5  | 7.5  | 7.6  |
| models/   | 8.0  | 8.0  | 8.5  | 7.0  | 7.9  |

### Hotspots
1. **auth/** (6.8) -- Hardcoded token, no rate limiting
2. **services/** (7.6) -- N+1 queries in 2 handlers

### Top 3 Fixes
1. [Critical] auth/config.py:15 -- Hardcoded JWT secret
2. [High] services/order.py:89 -- N+1 query in loop
3. [High] auth/login.py:45 -- Bare except with pass
```

## Output Checklist

After completing a review, verify:

- [ ] CLAUDE.md conventions were checked and applied
- [ ] All target files were read and analyzed
- [ ] Helper scripts were run (secrets, complexity)
- [ ] Each dimension has a numeric score with justification
- [ ] Overall score uses weighted formula
- [ ] Findings filtered (auto-skip, deduplicate, confidence, root-cause)
- [ ] All issues include file:line references
- [ ] Issues categorized by severity (Critical/High/Medium/Low)
- [ ] Recommendations are actionable (what to do, not just what's wrong)
- [ ] Hard-fail rules applied if triggered
- [ ] Report follows the structured format
- [ ] Auto-fix applied only if --fix was requested
