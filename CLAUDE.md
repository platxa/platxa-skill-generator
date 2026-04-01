# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Platxa Skill Generator creates production-ready Claude Code skills by orchestrating specialized subagents through a multi-phase workflow: Discovery → Architecture → Generation → Validation → Installation. It follows Anthropic's Agent Skills specification and supports advanced patterns (parallel sub-agents, auto-fix, CLAUDE.md integration) matching Anthropic's bundled skills like /simplify.

## Commands

### Validation
```bash
./scripts/validate-all.sh <skill-directory>      # Run all validators
./scripts/validate-structure.sh <skill-directory> # Check directory structure
./scripts/validate-frontmatter.sh <skill-directory> # Check SKILL.md frontmatter
./scripts/validate-skill.sh <skill-directory>    # Field validation with scoring
./scripts/validate-catalog-entry.sh <skill-directory> # Validate catalog entry for PR
python3 scripts/count-tokens.py <skill-directory>  # Check token budget
python3 scripts/score-skill.py <skill-directory>   # 5-dimension quality scorer (--json, --verbose)
./scripts/security-check.sh <skill-directory>     # Security validation
```

### Testing
```bash
pytest tests/ -v                    # Run all 130 tests
pytest tests/test_validate_frontmatter.py -v  # Run specific test file
pytest -k "test_valid_name"         # Run tests matching pattern
```

### Installation
```bash
./scripts/install-skill.sh <skill-directory> --user    # Install to ~/.claude/skills/
./scripts/install-skill.sh <skill-directory> --project # Install to .claude/skills/
./scripts/install-from-catalog.sh --list               # Browse catalog with quality scores
./scripts/install-from-catalog.sh <name>               # Install from catalog
./scripts/install-from-catalog.sh --all                # Install all (topological order)
```

### Dependency Management
```bash
./scripts/check-dependencies.sh <skill-directory>  # Check depends-on requirements
./scripts/detect-circular-deps.sh [--dir <path>]   # Find cycles in dependency graph
./scripts/skill-graph.sh [--dir <path>]            # Output dependency graph (DOT format)
./scripts/list-installed.sh [--user|--project]     # List installed skills
```

## Architecture

### Workflow State Machine

The skill generator progresses through phases: IDLE → INIT → DISCOVERY → ARCHITECTURE → GENERATION → VALIDATION → INSTALLATION → COMPLETE. State is persisted in `.claude/skill_creation_state.json`.

### Subagent Pattern

Each phase uses Task tool with specialized agents defined in `references/agents/`:
- **discovery-agent.md**: Researches domain via web search, analyzes existing skills
- **architecture-agent.md**: Determines skill type, structure, and execution sophistication (simple/intermediate/advanced)
- **generation-agent.md**: Creates SKILL.md and supporting files with dynamic context injection
- **validation-agent.md**: Runs quality checks (score ≥7.0 required), generates Anthropic-compatible evals
- **script-agent.md**: Generates executable helpers
- **reference-agent.md**: Creates domain documentation
- **quality-agent.md**: Scores content quality

### Skill Types

Five types with distinct templates in `references/templates/`:
| Type | Purpose | Key Sections |
|------|---------|--------------|
| Builder | Create artifacts | Workflow, Templates, Output Checklist |
| Guide | Teach/explain | Steps, Examples, Best Practices |
| Automation | Automate tasks | Triggers, Scripts, Verification |
| Analyzer | Inspect/audit | Checklist, Metrics, Reports |
| Validator | Verify quality | Rules, Thresholds, Pass/Fail |

### Token Budget Limits

Defined in `scripts/count-tokens.py`:
- SKILL.md: ≤5000 tokens, ≤500 lines
- Single reference file: ≤2000 tokens
- Total references: ≤10000 tokens
- Total skill: ≤15000 tokens

## Key Directories

```
references/             # 137 domain knowledge files
├── agents/             # 7 subagent prompt definitions
├── patterns/           # 56 implementation patterns (includes parallel, auto-fix, CLAUDE.md, filtering)
├── templates/          # 9 skill type templates (with advanced workflow variants)
├── orchestration/      # 7 workflow patterns
├── discovery/          # 3 research patterns
├── generation/         # 13 content generation patterns
├── validation/         # 5 quality validation patterns
├── installation/       # 10 install/export patterns
├── interaction/        # 9 user interaction patterns
├── architecture/       # 2 architecture patterns
├── scripts/            # 11 script generation patterns
├── spec/               # 2 specification references
└── examples/           # 2 example skills
scripts/                # 15 Bash/Python scripts
catalog/                # 17 production-ready skills
tests/                  # 130 tests across 7 files (uses real file operations, no mocks)
```

## SKILL.md Frontmatter Requirements

```yaml
---
name: hyphen-case-name  # Required, ≤64 chars, no consecutive hyphens
description: ...        # Required, ≤1024 chars, no placeholders
allowed-tools:          # Optional, only valid Claude Code tools
  - Read
  - Write
  - Task
---
```

Valid tools: Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash, Task, Agent, Skill, WebFetch, WebSearch, AskUserQuestion, TodoWrite, KillShell, BashOutput, NotebookEdit
