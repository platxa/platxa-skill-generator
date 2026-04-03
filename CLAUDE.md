# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Platxa Skill Generator creates production-ready Claude Code skills by orchestrating specialized subagents through a multi-phase workflow: Discovery → Architecture → Generation → Validation → Eval Loop → Installation. It follows both the Agent Skills open standard (agentskills.io) and Claude Code extensions, with eval infrastructure inspired by Anthropic's skill-creator. Supports advanced patterns (parallel sub-agents, auto-fix, CLAUDE.md integration, description optimization) matching Anthropic's bundled skills like /simplify.

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

### Evaluation
```bash
./scripts/run-eval.sh <skill-directory>                    # Run evals against skill
./scripts/run-eval.sh <skill-directory> --baseline         # Run without skill (comparison)
./scripts/run-eval.sh <skill-directory> --iteration 2      # Second iteration
python3 scripts/aggregate-benchmark.py <iter-dir> --skill-name <name>  # Aggregate results
python3 scripts/optimize-description.py <skill-directory> --json       # Optimize triggers
```

### Packaging
```bash
python3 scripts/package-skill.py <skill-directory>         # Create .skill archive
python3 scripts/package-skill.py <skill-directory> --output out.skill  # Custom output path
```

### Testing
```bash
pytest tests/ -v                    # Run all tests
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

The skill generator progresses through phases: IDLE → INIT → DISCOVERY → ARCHITECTURE → GENERATION → VALIDATION → EVAL_LOOP → INSTALLATION → COMPLETE. State is persisted in `.claude/skill_creation_state.json`. The EVAL_LOOP phase is optional but recommended for production skills.

### Subagent Pattern

Each phase uses Task tool with specialized agents defined in `references/agents/`:
- **discovery-agent.md**: Researches domain via web search, analyzes existing skills
- **architecture-agent.md**: Determines skill type, structure, and execution sophistication (simple/intermediate/advanced)
- **generation-agent.md**: Creates SKILL.md and supporting files with dynamic context injection
- **validation-agent.md**: Runs quality checks (score ≥7.0 required), generates Anthropic-compatible evals
- **script-agent.md**: Generates executable helpers
- **reference-agent.md**: Creates domain documentation
- **quality-agent.md**: Scores content quality
- **grader-agent.md**: Evaluates eval expectations against skill outputs

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
references/             # 140 domain knowledge files
├── agents/             # 9 subagent prompt definitions (incl. grader, comparator)
├── patterns/           # 56 implementation patterns (parallel, auto-fix, CLAUDE.md, filtering)
├── templates/          # 9 skill type templates (with advanced workflow variants)
├── orchestration/      # 7 workflow patterns
├── discovery/          # 3 research patterns
├── generation/         # 13 content generation patterns
├── validation/         # 6 quality validation patterns (incl. eval-schema)
├── installation/       # 10 install/export patterns
├── interaction/        # 9 user interaction patterns
├── architecture/       # 2 architecture patterns
├── scripts/            # 11 script generation patterns
├── spec/               # 2 specification references
└── examples/           # 2 example skills
scripts/                # 19 Bash/Python scripts (validation, eval, installation, packaging)
catalog/                # 17 production-ready skills
tests/                  # 155 tests across 9 files (uses real file operations, no mocks)
```

## SKILL.md Frontmatter Requirements

```yaml
---
name: hyphen-case-name  # Required, ≤64 chars, no consecutive hyphens
description: ...        # Required, ≤1024 chars, no placeholders
allowed-tools:          # Optional, supports constraint patterns like Bash(git:*)
  - Read
  - Write
  - Bash(git:*)
# Optional fields:
model: sonnet                     # opus, sonnet, or haiku
effort: medium                    # low, medium, high, max, or integer
context: fork                     # fork (sub-agent) or inline (default)
agent: Explore                    # Agent type when context: fork
paths: "**/*.ts"                  # Glob patterns for conditional activation
argument-hint: "[target]"         # Help text for /skill arguments
user-invocable: true              # true/false/yes/no
disable-model-invocation: false   # true/false/yes/no
shell: bash                       # bash or powershell
hooks: {}                         # Lifecycle hooks (PreToolUse, PostToolUse, TaskCreated, etc.)
metadata:                         # Arbitrary key-value pairs
  version: "1.0.0"                # Semantic versioning goes under metadata
# DEPRECATED (not in official spec — fold into description):
# when_to_use: "..."              # Use description field instead
# NON-STANDARD (open proposals only):
# depends-on:                     # Not yet in Agent Skills spec
# suggests:                       # Not yet in Agent Skills spec
---
```

Valid tools (30): Read, Write, Edit, MultiEdit, Glob, Grep, LS, Bash, Task, Agent, Skill, WebFetch, WebSearch, AskUserQuestion, TodoWrite, KillShell, BashOutput, NotebookEdit, Brief, ToolSearch, EnterPlanMode, ExitPlanMode, EnterWorktree, ExitWorktree, LSP, RemoteTrigger, CronCreate, CronDelete, CronList, SendMessage

Tool constraint patterns: `Bash(git:*)`, `Write(src/*)`, `Bash(${CLAUDE_SKILL_DIR}/scripts/*)`

Hook event types: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStop`, `TaskCreated`, `CwdChanged`, `FileChanged`, `PermissionDenied`
