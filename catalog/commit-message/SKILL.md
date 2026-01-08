---
name: commit-message
description: Generate conventional commit messages by analyzing staged git changes. Detects change type, suggests scope, and formats messages following the Conventional Commits specification.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
metadata:
  version: "1.0.0"
  tags:
    - automation
    - git
    - workflow
---

# Commit Message Generator

Generate conventional commit messages from staged git changes.

## Overview

This skill automates commit message generation for development teams. It analyzes staged changes, detects the appropriate commit type (feat, fix, refactor, etc.), suggests a scope based on modified files, and generates a properly formatted message following the Conventional Commits specification.

**What it automates:**
- Analysis of staged git changes
- Commit type detection based on change patterns
- Scope suggestion from file paths
- Message formatting with subject/body/footer

**Time saved:** ~2-5 minutes per commit

## Triggers

Run this skill when:
- You have staged changes ready to commit
- You want a well-formatted conventional commit
- You need to reference issues or breaking changes

## Workflow

### Step 1: Analyze Staged Changes

First, I'll examine what's staged:

```bash
git diff --cached --stat
git diff --cached --name-status
```

This shows:
- Files added (A), modified (M), deleted (D), renamed (R)
- Lines changed per file
- Overall change scope

### Step 2: Detect Commit Type

Based on the changes, I'll determine the appropriate type:

| Pattern | Type | Description |
|---------|------|-------------|
| New feature files | `feat` | New functionality |
| Bug fix in existing code | `fix` | Bug repair |
| Code restructuring | `refactor` | No behavior change |
| Performance improvements | `perf` | Faster/leaner code |
| Test additions/changes | `test` | Test updates |
| Documentation only | `docs` | Documentation |
| Formatting/style | `style` | No code change |
| Build/CI config | `build`/`ci` | Infrastructure |
| Maintenance | `chore` | Other changes |

### Step 3: Suggest Scope

Extract scope from the primary changed directory:

- `src/api/*` → scope: `api`
- `src/components/*` → scope: `components`
- `lib/utils/*` → scope: `utils`
- Multiple areas → omit scope or use parent

### Step 4: Generate Message

Format following Conventional Commits:

```
<type>(<scope>): <description>

<body - explains why, not how>

<footer - issues, breaking changes>
```

**Subject line rules:**
- Maximum 50 characters
- Imperative mood ("Add" not "Added")
- No period at end
- Capitalize first letter

### Step 5: Review and Commit

Present the generated message for your approval, then execute:

```bash
git commit -m "<message>"
```

## Verification

### Success Indicators

- Commit type matches the nature of changes
- Subject line is under 50 characters
- Message uses imperative mood
- Breaking changes are properly noted
- Issue references are included when applicable

### Message Validation

Before committing, I verify:
- [ ] Type is valid (feat, fix, docs, etc.)
- [ ] Subject line <= 50 characters
- [ ] Imperative mood used
- [ ] No trailing period
- [ ] Body wrapped at 72 characters (if present)
- [ ] Footer format correct (if present)

## Examples

### Example 1: Simple Feature

```
User: Generate a commit message for my staged changes
Assistant: Analyzing staged changes...

git diff --cached --name-status:
A  src/components/Button.tsx
M  src/components/index.ts

Detected: New component file added
Type: feat
Scope: components

Generated message:
feat(components): add Button component

Proceed with this commit? (y/n)
```

### Example 2: Bug Fix with Issue Reference

```
User: /commit - this fixes issue #42
Assistant: Analyzing staged changes...

git diff --cached --name-status:
M  src/utils/parser.ts

Detected: Modified existing utility code
Type: fix
Scope: utils

Generated message:
fix(utils): resolve array parsing edge case

Handle empty arrays correctly in parser to prevent
undefined errors when processing user input.

Closes #42

Proceed with this commit? (y/n)
```

### Example 3: Breaking Change

```
User: Generate commit - this changes the API signature
Assistant: Analyzing staged changes...

git diff --cached --name-status:
M  src/api/auth.ts
M  src/types/auth.ts

Detected: API modification with signature change
Type: feat (with breaking change)
Scope: api

Generated message:
feat(api)!: update authentication flow

Migrate from session-based to JWT authentication.
This changes the login endpoint response format.

BREAKING CHANGE: login() now returns {token, refreshToken}
instead of {sessionId}. All clients must update their
authentication handling.

Proceed with this commit? (y/n)
```

## Configuration

### Commit Types Reference

| Type | When to Use | SemVer Impact |
|------|-------------|---------------|
| `feat` | New feature | Minor bump |
| `fix` | Bug fix | Patch bump |
| `docs` | Documentation only | None |
| `style` | Formatting, no code change | None |
| `refactor` | Code restructure, no behavior change | None |
| `perf` | Performance improvement | None |
| `test` | Adding/updating tests | None |
| `build` | Build system changes | None |
| `ci` | CI configuration | None |
| `chore` | Maintenance tasks | None |

### Breaking Changes

Add `!` after type/scope or include footer:
- `feat!: change API`
- `feat(api)!: update endpoint`
- Footer: `BREAKING CHANGE: description`

## Output Checklist

Before finalizing a commit message:

- [ ] Type accurately reflects the change
- [ ] Scope matches the affected area
- [ ] Subject is imperative mood
- [ ] Subject <= 50 characters
- [ ] Body explains why (if included)
- [ ] Body wrapped at 72 characters
- [ ] Breaking changes documented
- [ ] Issue references included