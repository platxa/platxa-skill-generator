---
name: code-documenter
description: Automatically generates and improves code documentation across Python, JavaScript/TypeScript, Java, Go, and Rust. Detects language conventions, applies appropriate docstring standards, and validates documentation quality.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  tags:
    - automation
    - documentation
    - developer-tools
---

# Code Documenter

Automatically generate and improve code documentation following language-specific standards.

## Overview

This skill automates documentation generation for development teams. It detects your codebase language, applies appropriate docstring standards (Google/NumPy for Python, JSDoc/TSDoc for TypeScript, Javadoc for Java, godoc for Go, rustdoc for Rust), and validates documentation quality.

**What it automates:**
- Detection of language and existing documentation style
- Generation of missing docstrings for public APIs
- Validation of documentation completeness and quality
- Suggestions for documentation improvements

## Language Support

| Language | Supported Styles | Generator Tool |
|----------|------------------|----------------|
| Python | Google, NumPy, Sphinx | Sphinx + Napoleon |
| JavaScript/TypeScript | JSDoc, TSDoc | TypeDoc |
| Java | Javadoc | javadoc |
| Go | godoc conventions | pkgsite |
| Rust | rustdoc (CommonMark) | cargo doc |

## Workflow

### Step 1: Detect Language and Style

First, I'll scan your codebase to identify:
- Primary programming language(s)
- Existing documentation conventions (if any)
- Public API surface that needs documentation

### Step 2: Analyze Coverage

I'll check current documentation status:
- Files with existing documentation
- Public functions/classes missing documentation
- Documentation quality issues (incomplete params, missing returns)

### Step 3: Generate Documentation

For undocumented code, I'll generate:
- One-line summary describing purpose
- Parameter documentation with types and descriptions
- Return value documentation
- Exception/error documentation where applicable
- Usage examples for complex functions

### Step 4: Validate Quality

I'll verify documentation meets quality standards:
- No placeholder content (TODO, TBD, ...)
- All parameters documented
- Return types specified
- Consistent style throughout

## Triggers

Run this skill when:
- Adding new functions or classes
- Preparing code for review
- Onboarding new team members
- Setting up documentation infrastructure

## Verification

### Success Indicators

- All public APIs have docstrings
- Documentation style is consistent
- No placeholder content remains
- Parameters and returns documented

### Coverage Report

After running, I'll provide:
- Documentation coverage percentage
- List of newly documented items
- Remaining items needing manual attention

## Examples

### Example 1: Document a Python Module

```
User: Document the functions in src/utils/helpers.py
Assistant: Analyzing src/utils/helpers.py...

Found 5 public functions, 2 already documented.

Generating documentation for 3 functions using Google style:

def calculate_discount(price: float, percentage: float) -> float:
    """Calculate discounted price.

    Args:
        price: Original price in dollars.
        percentage: Discount percentage (0-100).

    Returns:
        Final price after applying discount.

    Raises:
        ValueError: If percentage is not between 0 and 100.
    """

[Continues for remaining functions...]

Coverage: 100% (5/5 functions documented)
```

### Example 2: Audit TypeScript Documentation

```
User: Check documentation coverage in src/components/
Assistant: Scanning TypeScript files in src/components/...

Documentation Report:
- Total exports: 24
- Documented: 18 (75%)
- Missing: 6

Missing documentation:
1. src/components/Button.tsx: ButtonProps interface
2. src/components/Modal.tsx: useModal hook
3. src/components/Form.tsx: validateField, submitForm, resetForm

Would you like me to generate TSDoc comments for these?
```

### Example 3: Set Up Documentation Standards

```
User: Help us establish documentation standards for our Python project
Assistant: I'll analyze your current codebase and recommend a standard.

Current state:
- 3 files use Google-style docstrings
- 2 files use NumPy-style docstrings
- 5 files have no docstrings

Recommendation: Standardize on Google style (most common in your codebase).

I'll create:
1. Documentation style guide (CONTRIBUTING.md section)
2. Pre-commit hook to validate docstring format
3. Generate missing docs in Google style

Proceed? (y/n)
```

## Configuration

### Style Preferences

When multiple styles are valid, I'll ask which you prefer:

| Language | Options |
|----------|---------|
| Python | google, numpy, sphinx |
| TypeScript | jsdoc, tsdoc |

### Scope Control

| Option | Effect |
|--------|--------|
| Public only | Document exported functions/classes only |
| Include private | Document all functions including internal |
| Specific files | Target only specified files/directories |

## Safety

### Idempotency

Running multiple times is safe:
- Existing documentation is preserved
- Only missing documentation is added
- Style conflicts are flagged, not overwritten

### Reversibility

All changes are made through standard file edits:
- Use `git diff` to review changes
- Use `git checkout` to revert if needed

## Output Checklist

Before considering documentation complete:

- [ ] All public functions have docstrings
- [ ] Parameter types and descriptions present
- [ ] Return values documented with type
- [ ] Exceptions documented where thrown
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] Consistent style across codebase
- [ ] At least one example for complex functions
