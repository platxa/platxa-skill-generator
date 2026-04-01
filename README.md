# Platxa Skill Generator

> Autonomous skill creator for Claude Code CLI using multi-phase orchestrated workflows with Task tool subagents.
>
> **Created by**: DJ Patel -- Founder & CEO, Platxa | https://platxa.com
>
> **Based on**: Anthropic's [Agent Skills](https://github.com/anthropics/skills) specification

---

## Table of Contents

- [Skills Catalog](#skills-catalog)
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts Reference](#scripts-reference)
- [Skill Types](#skill-types)
- [Project Structure](#project-structure)
- [Quality Standards](#quality-standards)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Skills Catalog

**17 ready-to-use skills** for the community. Browse and install production-ready skills:

| Skill | Type | Description |
|-------|------|-------------|
| **[code-documenter](catalog/code-documenter/)** | Automation | Generate docs for Python, JS/TS, Java, Go, Rust |
| **[commit-message](catalog/commit-message/)** | Automation | Generate conventional commit messages |
| **[test-generator](catalog/test-generator/)** | Builder | Generate comprehensive unit tests |
| **[pr-description](catalog/pr-description/)** | Automation | Generate PR descriptions from git history |
| **[platxa-code-review](catalog/platxa-code-review/)** | Analyzer | Code quality, security, and efficiency analysis |
| **[platxa-frontend-builder](catalog/platxa-frontend-builder/)** | Builder | React/Next.js component generation |
| **[platxa-sidecar-builder](catalog/platxa-sidecar-builder/)** | Builder | Node.js sidecar service builder |
| **[platxa-error-handling](catalog/platxa-error-handling/)** | Guide | Error handling patterns across Platxa stack |
| **[platxa-jwt-auth](catalog/platxa-jwt-auth/)** | Builder | RS256 JWT authentication with JWKS |
| **[platxa-k8s-ops](catalog/platxa-k8s-ops/)** | Automation | Kubernetes operations automation |
| **[platxa-k8s-scaling](catalog/platxa-k8s-scaling/)** | Guide | Kubernetes scaling patterns (HPA, scale-to-zero) |
| **[platxa-logging](catalog/platxa-logging/)** | Guide | Structured logging and correlation IDs |
| **[platxa-monaco-config](catalog/platxa-monaco-config/)** | Guide | Monaco editor configuration |
| **[platxa-monitoring](catalog/platxa-monitoring/)** | Guide | Prometheus/Loki observability |
| **[platxa-secrets-management](catalog/platxa-secrets-management/)** | Guide | Fernet encryption and K8s secrets |
| **[platxa-testing](catalog/platxa-testing/)** | Guide | pytest/Vitest testing patterns |
| **[platxa-yjs-server](catalog/platxa-yjs-server/)** | Guide | Yjs CRDT WebSocket servers |

```bash
./scripts/install-from-catalog.sh --list           # Browse with quality scores
./scripts/install-from-catalog.sh code-documenter   # Install one skill
./scripts/install-from-catalog.sh --all             # Install all (topologically ordered)
```

See the full **[Skills Catalog](catalog/README.md)** for details.

---

## Overview

Platxa Skill Generator creates production-ready Claude Code skills by orchestrating specialized subagents through a multi-phase workflow:

1. **Discovery** -- Research domain knowledge via web search and existing skill analysis
2. **Architecture** -- Design skill structure based on type (Builder/Guide/Automation/Analyzer/Validator)
3. **Generation** -- Create SKILL.md, scripts, and reference documentation
4. **Validation** -- Verify against Anthropic's spec with 5-dimension quality scoring
5. **Installation** -- Deploy to user or project skills directory

---

## Features

| Feature | Description |
|---------|-------------|
| **Autonomous Creation** | Minimal user input, maximum automation |
| **Multi-Phase Workflow** | 7 specialized subagents for each phase |
| **Five Skill Types** | Builder, Guide, Automation, Analyzer, Validator |
| **Advanced Patterns** | Parallel sub-agents, auto-fix, CLAUDE.md integration, smart scoping |
| **Quality Scoring** | 5-dimension scorer with advanced pattern bonuses |
| **Dependency System** | `depends-on` and `suggests` fields with cycle detection |
| **Token Budget Management** | SKILL.md optimized for context efficiency |
| **Script Security** | ShellCheck + security pattern scanning |
| **Web Research** | Automatic domain knowledge discovery |
| **137 Reference Files** | Domain knowledge across 56 patterns, 9 templates, 7 agents |
| **15 Scripts** | Validation, installation, scoring, dependency checking, graph visualization |
| **130 Tests** | Comprehensive test suite across 7 test files |

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Claude Code CLI** | Latest | Required runtime environment |
| **Bash** | 4.0+ | Run validation and installation scripts |
| **Python** | 3.10+ | Token counting, quality scoring |
| **Git** | 2.0+ | Clone the repository |

Optional: `tiktoken` (pip install) for precise token counting, `shellcheck` for script linting.

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/platxa/platxa-skill-generator.git
cd platxa-skill-generator
./scripts/install-skill.sh . --user
```

### 2. Verify

```bash
./scripts/validate-all.sh .
```

### 3. Generate a skill

In Claude Code:
```
/platxa-skill-generator
> A skill that formats JSON files
```

The generator researches, designs, generates, validates (score >= 7.0/10), and installs.

---

## Installation

### Option 1: Using install script (recommended)

```bash
git clone https://github.com/platxa/platxa-skill-generator.git
cd platxa-skill-generator
./scripts/install-skill.sh . --user    # User-wide (~/.claude/skills/)
./scripts/install-skill.sh . --project # Project-only (.claude/skills/)
```

### Option 2: Manual copy

```bash
git clone https://github.com/platxa/platxa-skill-generator.git
cp -r platxa-skill-generator ~/.claude/skills/platxa-skill-generator
```

### Install catalog skills

```bash
cd platxa-skill-generator
./scripts/install-from-catalog.sh --list    # Browse available skills
./scripts/install-from-catalog.sh --all     # Install all (respects dependency order)
```

---

## Scripts Reference

### Validation

| Script | Purpose |
|--------|---------|
| `validate-all.sh <dir>` | Run all validators (structure, frontmatter, tokens, shellcheck, quality) |
| `validate-structure.sh <dir>` | Check directory structure and file presence |
| `validate-frontmatter.sh <dir>` | Validate YAML frontmatter fields and formats |
| `validate-skill.sh <dir>` | Field validation with 0-10 scoring |
| `validate-catalog-entry.sh <dir>` | Validate a catalog entry for PR submission |
| `count-tokens.py <dir>` | Token counting with budget enforcement |
| `score-skill.py <dir>` | 5-dimension quality scorer (--json, --verbose) |
| `security-check.sh <dir>` | Scan scripts for dangerous patterns |

### Installation

| Script | Purpose |
|--------|---------|
| `install-skill.sh <dir> [--user\|--project]` | Install a skill with validation and dependency check |
| `install-from-catalog.sh <name>` | Install from catalog with auto-dependency resolution |

### Dependency Management

| Script | Purpose |
|--------|---------|
| `check-dependencies.sh <dir>` | Check if depends-on requirements are installed |
| `detect-circular-deps.sh [--dir <path>]` | Find cycles in dependency graph (DFS) |
| `skill-graph.sh [--dir <path>]` | Output dependency graph in DOT format |
| `list-installed.sh [--user\|--project]` | List installed skills with dependency info |

### Testing

| Script | Purpose |
|--------|---------|
| `test-scripts.sh` | Test runner for script validation |

---

## Skill Types

| Type | Purpose | Key Sections |
|------|---------|--------------|
| **Builder** | Create new things | Workflow, Templates, Output Checklist |
| **Guide** | Teach/explain | Steps, Examples, Best Practices |
| **Automation** | Automate tasks | Triggers, Scripts, Verification |
| **Analyzer** | Inspect/audit | Checklist, Metrics, Reports |
| **Validator** | Verify quality | Rules, Thresholds, Pass/Fail Criteria |

---

## Project Structure

```
platxa-skill-generator/
├── SKILL.md                    # Main skill definition (entry point)
├── README.md                   # This file
├── pyproject.toml              # Python project config
├── LICENSE                     # MIT License
│
├── scripts/                    # 15 executable scripts
│   ├── validate-all.sh         # Master validation orchestrator
│   ├── validate-structure.sh   # Directory structure checks
│   ├── validate-frontmatter.sh # YAML frontmatter validation
│   ├── validate-skill.sh       # Field validation with scoring
│   ├── validate-catalog-entry.sh # Catalog entry validator
│   ├── count-tokens.py         # Token counting (tiktoken)
│   ├── score-skill.py          # 5-dimension quality scorer
│   ├── security-check.sh       # Script security scanning
│   ├── install-skill.sh        # Skill installer
│   ├── install-from-catalog.sh # Catalog installer (batch, deps)
│   ├── check-dependencies.sh   # Dependency checker
│   ├── detect-circular-deps.sh # Cycle detection (DFS)
│   ├── skill-graph.sh          # DOT graph output
│   ├── list-installed.sh       # Installed skills lister
│   └── test-scripts.sh         # Script test runner
│
├── catalog/                    # 17 production-ready skills
│   ├── code-documenter/
│   ├── commit-message/
│   ├── test-generator/
│   ├── pr-description/
│   ├── platxa-code-review/
│   ├── platxa-frontend-builder/
│   ├── platxa-sidecar-builder/
│   ├── platxa-error-handling/
│   ├── platxa-jwt-auth/
│   ├── platxa-k8s-ops/
│   ├── platxa-k8s-scaling/
│   ├── platxa-logging/
│   ├── platxa-monaco-config/
│   ├── platxa-monitoring/
│   ├── platxa-secrets-management/
│   ├── platxa-testing/
│   └── platxa-yjs-server/
│
├── references/                 # 137 domain knowledge files
│   ├── agents/                 # 7 subagent definitions
│   ├── patterns/               # 56 implementation patterns
│   ├── templates/              # 9 skill type templates
│   ├── orchestration/          # 7 workflow patterns
│   ├── discovery/              # 3 research patterns
│   ├── generation/             # 13 content generation patterns
│   ├── validation/             # 5 quality validation patterns
│   ├── installation/           # 10 install/export patterns
│   ├── interaction/            # 9 user interaction patterns
│   ├── architecture/           # 2 architecture patterns
│   ├── scripts/                # 11 script generation patterns
│   ├── spec/                   # 2 specification references
│   └── examples/               # 2 example skills
│
├── tests/                      # 130 tests across 7 files
│   ├── test_validate_frontmatter.py  # 33 frontmatter tests
│   ├── test_validate_structure.py    # 16 structure tests
│   ├── test_count_tokens.py          # 10 token tests
│   ├── test_score_skill.py           # 43 quality scorer tests (incl. advanced pattern bonuses)
│   ├── test_check_dependencies.py    # 8 dependency tests
│   ├── test_circular_deps.py         # 9 cycle detection tests
│   ├── test_integration.py           # 11 integration tests
│   ├── conftest.py                   # Fixtures
│   └── helpers.py                    # Test utilities
│
└── .github/workflows/          # CI/CD
    ├── ci.yml                  # Tests, validation, shellcheck
    └── validate-catalog.yml    # Catalog PR validation
```

---

## Quality Standards

### Quality Scorer (score-skill.py)

Every generated skill is scored across 5 dimensions:

| Dimension | Weight | What It Checks |
|-----------|--------|----------------|
| **Spec Compliance** | 25% | Frontmatter validity, name format, description, tools |
| **Content Depth** | 25% | Placeholders, generic filler, LLM-favorite words, vocabulary diversity, advanced pattern bonuses |
| **Example Quality** | 20% | Code blocks, language labels, substance, YAML/JSON validity |
| **Structure** | 15% | Required sections, heading count, hierarchy |
| **Token Efficiency** | 15% | Line count, word count, sentence length, references |

| Score | Level | Decision |
|-------|-------|----------|
| 9.0-10.0 | Excellent | APPROVE |
| 8.0-8.9 | Good | APPROVE |
| 7.0-7.9 | Acceptable | APPROVE with suggestions |
| 5.0-6.9 | Needs Work | REVISE |
| < 5.0 | Poor | REJECT |

```bash
python3 scripts/score-skill.py catalog/code-documenter --json     # JSON output
python3 scripts/score-skill.py catalog/code-documenter --verbose   # Detailed signals
```

### Skill Composition

Skills can declare relationships via frontmatter:

```yaml
depends-on:          # Required skills (checked at install time)
  - platxa-logging
suggests:            # Recommended companions (shown after install)
  - platxa-testing
```

### Advanced Patterns (v2.2.0)

The generator now supports advanced skill patterns matching Anthropic's bundled skills like `/simplify`:

| Pattern | File | What It Enables |
|---------|------|-----------------|
| **Parallel Sub-Agents** | `references/patterns/skill-parallelism.md` | 3+ dimension analysis via concurrent Task agents |
| **Auto-Fix** | `references/patterns/auto-fix.md` | Analyzer skills apply fixes directly via Edit tool |
| **CLAUDE.md Integration** | `references/patterns/project-conventions.md` | Skills adapt to project conventions |
| **Smart Scoping** | `references/patterns/smart-scope.md` | Git-diff-first scope detection, zero config |
| **Finding Filtering** | `references/patterns/finding-filtering.md` | False positive filtering and deduplication |
| **Skill Composition** | `references/patterns/skill-composition.md` | Skills invoking other skills (like /batch + /simplify) |
| **Worktree Isolation** | `references/patterns/worktree-isolation.md` | Parallel file modifications in isolated worktrees |
| **Persistent Memory** | `references/patterns/skill-memory.md` | Cross-session learning for repeated analysis |

The architecture agent classifies skills into three execution sophistication tiers:

| Tier | Criteria | Capabilities |
|------|----------|-------------|
| **Simple** | 1-2 dimensions, no code modification | Read, Grep, Glob, Bash |
| **Intermediate** | 2-3 dimensions, optional mechanical fixes | + Task, Edit |
| **Advanced** | 3+ dimensions, parallel agents, auto-fix | + Task, Edit, Write + CLAUDE.md + filtering |

---

## Testing

```bash
# Run all 130 tests
pytest tests/ -v

# Run specific test file
pytest tests/test_score_skill.py -v

# Run by marker
pytest tests/ -m frontmatter
pytest tests/ -m integration
```

---

## Troubleshooting

### Skill not recognized after installation

```bash
ls ~/.claude/skills/platxa-skill-generator/SKILL.md   # Verify location
head -5 ~/.claude/skills/platxa-skill-generator/SKILL.md  # Check frontmatter
```

### Quality score too low

Provide more specific descriptions. Check `score-skill.py --verbose` for actionable suggestions.

### Scripts not executable

```bash
chmod +x scripts/*.sh
```

### ShellCheck fails in CI

Avoid comments starting with `# shellcheck` (parsed as directives). Remove unused color variables.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run before submitting:

```bash
./scripts/validate-all.sh .    # All validators pass
pytest tests/ -v               # All 130 tests pass
shellcheck scripts/*.sh        # No warnings
```

---

## License

MIT License -- See [LICENSE](LICENSE) for details.

---

**Version**: 2.2.0
**Created by**: DJ Patel -- Founder & CEO, Platxa | https://platxa.com
**Based on**: Anthropic's [Agent Skills](https://agentskills.io) Open Standard
