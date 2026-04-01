---
name: platxa-code-review
description: >-
  Analyzes code for quality, security, and efficiency across any language.
  Reviews files or git diffs, produces structured reports with weighted scores,
  metrics, and actionable recommendations. Use when reviewing code changes,
  pull requests, or auditing codebases for technical debt.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
metadata:
  version: "2.0.0"
  author: "Platxa"
  tags:
    - analyzer
    - code-review
    - quality
    - security
    - efficiency
---

# Platxa Code Review

Language-agnostic code review with structured reports, weighted scores, and actionable recommendations.

## Overview

This skill analyzes code across four dimensions: quality, security, efficiency, and maintainability. It works on individual files, git diffs, or entire codebases.

**What it analyzes:**
- Code quality (complexity, duplication, naming, SOLID principles)
- Security (hardcoded secrets, injection patterns, OWASP Top 10)
- Efficiency (algorithmic complexity, performance anti-patterns, memory)
- Maintainability (type safety, error handling, documentation, testability)

**What it produces:**
- Overall score (0-10) with letter grade (A-F)
- Per-dimension breakdown with specific findings
- Prioritized issues by severity level
- Actionable fix recommendations

**Supported languages:** Python, TypeScript/JavaScript, Go, Java, Rust, C/C++, and any readable source.

## Workflow

### Step 1: Determine Scope

Ask the user or detect from context. Three modes are supported.

**File review** -- analyze specific files or directories:
```bash
glob "src/**/*.{py,ts,js,go,rs,java}"
```

**Diff review** -- analyze git changes:
```bash
git diff --name-only HEAD~1
git diff main...HEAD --name-only
```

**Codebase review** -- systematic full-project scan (see Codebase Review Mode below):
```bash
glob "**/*.{py,ts,js,go}" --exclude "node_modules,dist,.git"
```

Optionally accept a dimension focus: quality, security, efficiency, or maintainability.

### Step 2: Run Automated Checks

Execute helper scripts on target files:

Detect hardcoded secrets:
```bash
bash scripts/detect-secrets.sh <file-or-directory>
```

Analyze complexity metrics:
```bash
bash scripts/analyze-complexity.sh <file-or-directory>
```

### Step 3: Deep Analysis

Read each file and evaluate against four weighted dimensions.

**Code Quality (weight: 0.30)**
- Cyclomatic complexity per function (target: <10)
- Function length (target: <50 lines)
- Nesting depth (target: <4 levels)
- Code duplication (target: <5%)
- Naming clarity and consistency
- SOLID principle adherence

**Security (weight: 0.25)**
- Hardcoded secrets (auto-fail if found)
- SQL/command injection patterns
- Input validation at boundaries
- Authentication/authorization checks
- Sensitive data handling

**Efficiency (weight: 0.25)**
- Algorithm complexity (Big-O)
- N+1 query patterns
- Unnecessary allocations in loops
- String concatenation in loops
- Unbounded collection growth
- Blocking I/O in async contexts

**Maintainability (weight: 0.20)**
- Type coverage (hints, strict mode, generics)
- Error handling completeness
- Function documentation for public APIs
- Testability (dependency injection, pure functions)
- Consistent coding style

### Step 4: Score and Report

Calculate weighted score. Generate structured report (see Report Format below).

Apply hard-fail rules:
- Hardcoded secrets detected: cap at 4.0
- Critical security vulnerability: cap at 5.0
- Syntax errors present: cap at 3.0

### Step 5: Recommendations

Provide prioritized, actionable fixes:
- **Critical**: Must fix before merge
- **High**: Should fix before merge
- **Medium**: Plan to address
- **Low**: Consider improving

## Codebase Review Mode

For full-codebase reviews, follow the 5-phase approach in `references/codebase-review-guide.md`.

**Phases:**
1. **Discovery** -- Map modules, count files by language, identify review order
2. **Automated Sweep** -- Run `detect-secrets.sh` and `analyze-complexity.sh` on the entire codebase
3. **Module-by-Module** -- Score each module independently across all 4 dimensions
4. **Cross-Cutting** -- Check consistency, duplication, and dependency flow across modules
5. **Consolidated Report** -- Module scores table, hotspots, top priority fixes, health summary

**Review order** (highest risk first): auth > API > data access > business logic > utilities > config > tests

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
- [ ] No shell command injection (no unescaped user input in commands)
- [ ] User input validated at system boundaries
- [ ] No eval() with dynamic input
- [ ] Sensitive data not logged or exposed in errors
- [ ] Dependencies are up to date

### Efficiency

- [ ] No N+1 query patterns
- [ ] No unnecessary object creation in loops
- [ ] No string concatenation in loops (use builder/join)
- [ ] Collections have bounded growth
- [ ] Async operations not blocking event loop
- [ ] Expensive computations cached when reused
- [ ] Early returns prevent unnecessary work

### Maintainability

- [ ] Type annotations on public APIs
- [ ] Errors handled with specific types (no bare catch-all)
- [ ] No silent failures (no empty catch blocks)
- [ ] Public functions have documentation
- [ ] Dependencies are injectable (testable)
- [ ] Consistent formatting throughout

## Metrics

### Complexity Thresholds

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Cyclomatic complexity | 1-5 | 6-10 | >10 |
| Cognitive complexity | 1-9 | 10-19 | >19 |
| Function length (lines) | 1-25 | 26-50 | >50 |
| Nesting depth | 1-2 | 3 | >3 |
| File length (lines) | 1-300 | 301-500 | >500 |

### Quality Thresholds

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Duplication ratio | <5% | 5-10% | >10% |
| Type coverage | >90% | 70-90% | <70% |
| Test coverage | >80% | 60-80% | <60% |
| Doc coverage (public) | >80% | 50-80% | <50% |

### Scoring Scale

| Score | Grade | Verdict | Action |
|-------|-------|---------|--------|
| 9.0-10.0 | A | Excellent | APPROVE |
| 8.0-8.9 | B | Good | APPROVE |
| 7.0-7.9 | C | Acceptable | APPROVE with suggestions |
| 5.0-6.9 | D | Needs work | REQUEST CHANGES |
| <5.0 | F | Failing | REJECT |

## Report Format

Generate this structured report:

```markdown
## Code Review Report

**Target:** {files or diff description}
**Date:** {timestamp}
**Files analyzed:** {count}
**Lines of code:** {total}

### Overall: {score}/10 (Grade {letter}) - {verdict}

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Code Quality | {x}/10 | 0.30 | {w} |
| Security | {x}/10 | 0.25 | {w} |
| Efficiency | {x}/10 | 0.25 | {w} |
| Maintainability | {x}/10 | 0.20 | {w} |
| **Overall** | | | **{total}/10** |

### Issues Found

**Critical**
- [{id}] {file}:{line} - {description}

**High**
- [{id}] {file}:{line} - {description}

**Medium**
- [{id}] {file}:{line} - {description}

### Dimension Details

**Code Quality ({score}/10)**
{specific findings with file:line references}

**Security ({score}/10)**
{specific findings with file:line references}

**Efficiency ({score}/10)**
{specific findings with file:line references}

**Maintainability ({score}/10)**
{specific findings with file:line references}

### Recommendations
1. [Critical] {actionable fix}
2. [High] {actionable fix}
3. [Medium] {actionable fix}
```

## Examples

### Example 1: Review a Python Module

```text
User: Review src/auth/handler.py for code quality
Assistant: Analyzing src/auth/handler.py...

## Code Review Report

**Target:** src/auth/handler.py
**Date:** 2026-03-31
**Files analyzed:** 1
**Lines of code:** 245

### Overall: 6.8/10 (Grade D) - REQUEST CHANGES

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Code Quality | 6.0 | 0.30 | 1.80 |
| Security | 7.5 | 0.25 | 1.88 |
| Efficiency | 7.0 | 0.25 | 1.75 |
| Maintainability | 6.5 | 0.20 | 1.30 |
| **Overall** | | | **6.73/10** |

### Issues Found

**Critical**
- [SEC-1] handler.py:42 - Hardcoded JWT secret `SECRET_KEY = "mysecret123"`

**High**
- [CQ-1] handler.py:67 - `process_login()` has cyclomatic complexity 14
- [CQ-2] handler.py:120 - Duplicated validation block (also at line 180)

**Medium**
- [EFF-1] handler.py:95 - N+1: Querying user roles inside loop
- [MT-1] handler.py:1-245 - No type hints on 8/12 public functions

### Recommendations
1. [Critical] Move JWT secret to environment variable
2. [High] Extract `process_login()` into smaller functions
3. [High] Consolidate duplicated validation into shared function
4. [Medium] Batch role queries with JOIN or prefetch
5. [Medium] Add type hints to all public functions
```

### Example 2: Review a Git Diff

```text
User: Review the changes in my current branch
Assistant: Analyzing diff against main...

## Code Review Report

**Target:** 3 files changed (git diff main...HEAD)
**Date:** 2026-03-31
**Files analyzed:** 3 (+142 lines, -38 lines)

### Overall: 8.2/10 (Grade B) - APPROVE

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Code Quality | 8.5 | 0.30 | 2.55 |
| Security | 8.0 | 0.25 | 2.00 |
| Efficiency | 8.0 | 0.25 | 2.00 |
| Maintainability | 8.0 | 0.20 | 1.60 |
| **Overall** | | | **8.15/10** |

### Issues Found

**Medium**
- [CQ-1] api/routes.ts:45 - Function `handleRequest` has 4 nesting levels
- [MT-1] api/routes.ts:30 - Missing return type annotation

### Recommendations
1. [Medium] Extract inner conditions in `handleRequest` to helper
2. [Medium] Add explicit return type to `handleRequest`
```

### Example 3: Focused Security Review

```text
User: Security review on src/payments/
Assistant: Running security-focused analysis on src/payments/...

## Code Review Report (Security Focus)

**Target:** src/payments/ (8 files)
**Security Score: 5.5/10 (Grade D) - REQUEST CHANGES**

### Critical Issues
- [SEC-1] stripe.py:12 - API key in source: `sk_live_...`
- [SEC-2] webhook.py:34 - No signature verification on webhook payload
- [SEC-3] checkout.py:89 - User-supplied `amount` not validated server-side

### High Issues
- [SEC-4] refund.py:56 - No authorization check on refund endpoint
- [SEC-5] models.py:23 - Credit card last4 logged at DEBUG level

### Recommendations
1. [Critical] Remove API key, use STRIPE_SECRET_KEY env var
2. [Critical] Verify Stripe webhook signatures before processing
3. [Critical] Validate and sanitize amount server-side
4. [High] Add permission check: only order owner can request refund
5. [High] Remove PII from log statements
```

### Example 4: Systematic Codebase Review

```text
User: Review the entire codebase
Assistant: Starting systematic codebase review...

## Codebase Review Report

**Project:** my-api | **Modules:** 4 | **Files:** 32 | **Lines:** 4,800

### Overall: 7.4/10 (Grade C) - APPROVE WITH SUGGESTIONS

| Module | Quality | Security | Efficiency | Maint. | Overall |
|--------|---------|----------|------------|--------|---------|
| auth/     | 7.0  | 5.5  | 8.0  | 7.0  | 6.8  |
| api/      | 8.0  | 8.5  | 7.0  | 8.0  | 7.9  |
| services/ | 7.5  | 9.0  | 6.5  | 7.5  | 7.6  |
| models/   | 8.0  | 8.0  | 8.5  | 7.0  | 7.9  |

### Hotspots
1. **auth/** (6.8) - Hardcoded token, no rate limiting
2. **services/** (7.6) - N+1 queries in 2 handlers

### Top 3 Fixes
1. [Critical] auth/config.py:15 - Hardcoded JWT secret
2. [High] services/order.py:89 - N+1 query in loop
3. [High] auth/login.py:45 - Bare except with pass
```

## Output Checklist

After completing a review, verify:

- [ ] All target files were read and analyzed
- [ ] Helper scripts were run (secrets, complexity)
- [ ] Each dimension has a numeric score with justification
- [ ] Overall score uses weighted formula
- [ ] All issues include file:line references
- [ ] Issues are categorized by severity (Critical/High/Medium/Low)
- [ ] Recommendations are actionable (what to do, not just what's wrong)
- [ ] Hard-fail rules applied if triggered
- [ ] Report follows the structured format above

For codebase reviews, also verify per `references/codebase-review-guide.md`:
- [ ] All modules discovered, scored independently, and ranked in table
- [ ] Hotspots and cross-cutting issues identified
- [ ] Top priority fixes ranked across entire codebase
