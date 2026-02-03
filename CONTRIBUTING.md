# Contributing to Platxa Skill Generator

Thank you for your interest in contributing to Platxa Skill Generator! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/platxa-skill-generator.git
   cd platxa-skill-generator
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Submitting a New Skill (PR-Based)

The skills registry uses GitHub PRs as the submission pipeline.
Every skill goes through automated validation before merging.

### Step 1: Fork and Clone

```bash
# Fork via GitHub UI, then:
git clone https://github.com/YOUR-USERNAME/platxa-skill-generator.git
cd platxa-skill-generator
git checkout -b add/my-skill-name
```

### Step 2: Create Your Skill

Create a directory under `skills/` with a `SKILL.md`:

```bash
mkdir -p skills/my-skill-name
```

Write `skills/my-skill-name/SKILL.md` with valid frontmatter:

```yaml
---
name: my-skill-name
description: One sentence describing what this skill does and when to use it.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - relevant-tag
---

# My Skill Name

Instructions for the AI agent go here...
```

Optionally add supporting files:

```
skills/my-skill-name/
├── SKILL.md              # Required
├── references/           # Optional domain expertise
│   └── patterns.md
├── scripts/              # Optional helper scripts
│   └── helper.sh
└── templates/            # Optional output templates
    └── template.md
```

### Step 3: Register in Manifest

Add your skill to `skills/manifest.yaml`:

```yaml
skills:
  # ... existing skills ...
  my-skill-name:
    local: true
    tier: 2              # 1=essential, 2=useful, 3=experimental
    category: devtools   # devtools, frontend, backend, testing, security, etc.
```

### Step 4: Validate Locally

```bash
# Run all validations (structure, frontmatter, tokens, duplicates, security)
./scripts/validate-all.sh skills/my-skill-name

# Check token budget
python3 scripts/count-tokens.py skills/my-skill-name

# Check for duplicates against existing skills
python3 scripts/check-duplicates.py skills/my-skill-name
```

All checks must pass. Token budgets:
- SKILL.md: ≤ 5,000 tokens (recommended), ≤ 10,000 (hard limit)
- References total: ≤ 10,000 tokens (recommended)
- Total skill: ≤ 15,000 tokens (recommended)

### Step 5: Open a Pull Request

```bash
git add skills/my-skill-name/ skills/manifest.yaml
git commit -m "feat: add my-skill-name skill"
git push origin add/my-skill-name
```

Open a PR against `main`. The CI pipeline will automatically:
1. Run `validate-all.sh` with profile-aware validation
2. Check token budgets
3. Run duplicate detection
4. Post a validation report as a PR comment

### What Happens After Submission

| Step | Action | Automated? |
|------|--------|------------|
| Validation | CI runs all quality checks | Yes |
| PR Comment | Bot posts validation report with scores | Yes |
| Review | Maintainers review content quality | No |
| Merge | PR merged to main | No |
| Publish | `index.json` and Pages site regenerated | Yes |
| Discovery | Skill appears in `.well-known/skills/` | Yes |

### Skill Quality Checklist

- [ ] SKILL.md has valid YAML frontmatter (name, description)
- [ ] Name is hyphen-case, ≤ 64 characters, no consecutive hyphens
- [ ] Description is ≤ 1,024 characters, no placeholders
- [ ] Only uses valid `allowed-tools` (Read, Write, Edit, Glob, Grep, Bash, Task, etc.)
- [ ] Token budget within limits
- [ ] No duplicate or near-duplicate of existing skills
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] Contains real domain expertise, not generic instructions
- [ ] Scripts are executable and pass security checks
- [ ] Tested on real projects

---

## How to Contribute

### Types of Contributions

We welcome contributions in these areas:

| Type | Description |
|------|-------------|
| **New Skills** | Submit a skill via the PR workflow above |
| **Bug Fixes** | Fix issues in existing functionality |
| **New Skill Types** | Add new skill type templates |
| **Pattern Improvements** | Enhance implementation patterns |
| **Documentation** | Improve README, examples, or inline docs |
| **Script Enhancements** | Better validation or utility scripts |

### Contribution Workflow

1. Check existing [issues](../../issues) and [pull requests](../../pulls)
2. For major changes, open an issue first to discuss
3. Fork and create a feature branch
4. Make your changes following style guidelines
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Claude Code CLI installed
- Bash shell (for scripts)
- Python 3.10+ (for token counting)

### Testing Your Changes

```bash
# Validate skill structure
./scripts/validate-structure.sh

# Validate frontmatter
./scripts/validate-frontmatter.sh

# Run all validations
./scripts/validate-all.sh

# Security check on scripts
./scripts/security-check.sh
```

### Testing Skill Generation

Install as a local skill and test:

```bash
# Copy to local skills
cp -r . ~/.claude/skills/platxa-skill-generator-dev/

# Test in Claude Code
# Use: /skill-generator-dev
```

## Pull Request Process

### Before Submitting

1. **Validate all changes**:
   ```bash
   ./scripts/validate-all.sh
   ```

2. **Update documentation** if needed

3. **Follow commit message format**:
   ```
   type(scope): description

   [optional body]
   ```

   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Requirements

- [ ] All validation scripts pass
- [ ] Documentation updated (if applicable)
- [ ] Follows style guidelines
- [ ] Descriptive PR title and body
- [ ] Links related issues

### Review Process

1. Maintainers will review within 1-2 weeks
2. Address any requested changes
3. Once approved, maintainers will merge

## Style Guidelines

### Markdown Files

- Use ATX-style headers (`#`, `##`, `###`)
- One sentence per line for easier diffs
- Use fenced code blocks with language specifiers
- Tables should be properly aligned

### SKILL.md Files

Follow Anthropic's Agent Skills specification:

```yaml
---
name: skill-name          # hyphen-case, <= 64 chars
description: ...          # <= 1024 chars
allowed-tools:
  - Read
  - Write
  # Only tools the skill actually needs
metadata:
  version: "1.0.0"
  author: "Your Name"
  tags:
    - relevant
    - tags
---
```

### Shell Scripts

- Include shebang: `#!/usr/bin/env bash`
- Use `set -euo pipefail` for safety
- Quote variables: `"$variable"`
- Add usage comments at the top
- Make scripts executable: `chmod +x script.sh`

### Python Scripts

- Python 3.10+ compatible
- Type hints where applicable
- Follow PEP 8 style
- Include docstrings

## Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Claude Code version)
- Relevant logs or screenshots

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Potential implementation approach
- Any alternatives considered

## Adding New Skill Types

To add a new skill type:

1. Create template in `references/templates/{type}-template.md`
2. Update `references/patterns/skill-types.md`
3. Add type to SKILL.md type reference table
4. Create examples in README.md
5. Update validation scripts if needed

## Adding External Skills via Manifest

To add a new upstream skill source to the catalog:

1. **Add the source** to `skills/manifest.yaml` under `sources:` (if new repo):
   ```yaml
   sources:
     my-source:
       repo: https://github.com/org/repo
       path: skills
   ```

2. **Add the skill entry** under `skills:`:
   ```yaml
   skills:
     my-new-skill:
       source: my-source
       ref: main
       tier: 2          # 1=essential, 2=useful, 3=experimental
       category: devtools
   ```

3. **Sync and validate**:
   ```bash
   ./scripts/sync-catalog.sh sync
   ./scripts/validate-all.sh skills/my-new-skill
   ```

4. **Add overrides** (optional): Place files in `skills/overrides/my-new-skill/` to customize the upstream skill.

5. **Submit PR** with the manifest change and any overrides.

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent matters

---

**Thank you for contributing!**

*Created by DJ Patel — Founder & CEO, Platxa | https://platxa.com*
