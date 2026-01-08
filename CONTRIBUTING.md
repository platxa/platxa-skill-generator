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

## How to Contribute

### Types of Contributions

We welcome contributions in these areas:

| Type | Description |
|------|-------------|
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

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent matters

---

**Thank you for contributing!**

*Created by DJ Patel — Founder & CEO, Platxa | https://platxa.com*
