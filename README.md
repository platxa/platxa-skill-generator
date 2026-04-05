# Platxa Skill Generator

> Autonomous skill creator for Claude Code CLI using multi-phase orchestrated workflows with Task tool subagents.
>
> **Created by**: DJ Patel -- Founder & CEO, Platxa | https://platxa.com
>
> **Based on**: Anthropic's [Agent Skills](https://agentskills.io) Open Standard + [Claude Code Extensions](https://code.claude.com/docs/en/skills)

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
- [Frontmatter Reference](#frontmatter-reference)
- [Eval Infrastructure](#eval-infrastructure)
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
5. **Eval Loop** (optional) -- Test with real prompts, grade, iterate, optimize description
6. **Installation** -- Deploy to user or project skills directory

### Two-Layer Spec Compliance

The generator supports both specification layers:

| Layer | Fields | Compatibility |
|-------|--------|--------------|
| **Agent Skills Open Standard** ([agentskills.io](https://agentskills.io)) | name, description, license, compatibility, metadata, allowed-tools | claude.ai, Cursor, Gemini CLI, Codex CLI, VS Code Copilot |
| **Claude Code Extensions** ([code.claude.com](https://code.claude.com/docs/en/skills)) | model, effort, context, agent, paths, hooks, argument-hint, user-invocable, disable-model-invocation, shell | Claude Code CLI only |

Use `--claude-ai` flag on validation scripts to check open-standard-only compliance.

---

## Features

| Feature | Description |
|---------|-------------|
| **Autonomous Creation** | Minimal user input, maximum automation |
| **Multi-Phase Workflow** | 9 specialized subagents for each phase |
| **Five Skill Types** | Builder, Guide, Automation, Analyzer, Validator |
| **Advanced Patterns** | Parallel sub-agents, auto-fix, CLAUDE.md integration, smart scoping |
| **Eval Infrastructure** | Test prompts, grading, benchmarking, description optimization, A/B comparison |
| **Quality Scoring** | 5-dimension scorer with advanced pattern bonuses and spec compliance checks |
| **Full Frontmatter Validation** | 30 valid tools, constraint patterns, claude.ai compatibility mode |
| **Dependency System** | `depends-on` and `suggests` fields (experimental) with cycle detection |
| **Token Budget Management** | SKILL.md optimized for context efficiency |
| **Script Security** | ShellCheck + security pattern scanning |
| **Skill Packaging** | .skill archive creation for distribution |
| **Web Research** | Automatic domain knowledge discovery |
| **Trigger Testing** | Keyword-based trigger accuracy testing with should/should-not-trigger prompts |
| **Anthropic Guide Alignment** | 3-part description structure, XML security, reserved names, negative triggers |
| **145 Reference Files** | Domain knowledge across 60 patterns, 9 templates, 9 agents |
| **20 Scripts** | Validation, installation, scoring, eval, trigger testing, dependency, packaging |
| **164 Tests** | Comprehensive test suite across 7 test files with catalog regression |

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Claude Code CLI** | Latest | Required runtime environment |
| **Bash** | 4.0+ | Run validation and installation scripts |
| **Python** | 3.10+ | Token counting, quality scoring, eval infrastructure |
| **Git** | 2.0+ | Clone the repository |

Optional: `tiktoken` (pip install) for precise token counting, `shellcheck` for script linting, `jq` for eval runner and trigger testing, `yq` for YAML syntax validation.

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
| `validate-frontmatter.sh [--claude-ai] <dir>` | Validate YAML frontmatter (30 tools, constraint patterns, open-standard mode) |
| `validate-skill.sh <dir>` | Field validation with 0-10 scoring |
| `validate-catalog-entry.sh <dir>` | Validate a catalog entry for PR submission |
| `count-tokens.py <dir>` | Token counting with budget enforcement |
| `score-skill.py <dir>` | 5-dimension quality scorer (--json, --verbose) |
| `security-check.sh <dir>` | Scan scripts for dangerous patterns |

### Evaluation & Trigger Testing

| Script | Purpose |
|--------|---------|
| `run-eval.sh <dir> [--baseline] [--iteration N]` | Run eval prompts against a skill via `claude -p` |
| `test-triggers.sh <dir> [--json] [--dry-run]` | Test trigger accuracy (should-trigger vs should-NOT-trigger prompts) |
| `aggregate-benchmark.py <iter-dir> --skill-name <name>` | Aggregate grading/timing into benchmark.json (mean/stddev) |
| `optimize-description.py <dir> [--json] [--verbose]` | Optimize description trigger accuracy with negative trigger generation |

### Installation & Distribution

| Script | Purpose |
|--------|---------|
| `install-skill.sh <dir> [--user\|--project]` | Install a skill with validation and dependency check |
| `install-from-catalog.sh <name>` | Install from catalog with auto-dependency resolution |
| `package-skill.py <dir> [--output <path>]` | Package skill into .skill archive for distribution |

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
| `test-triggers.sh <dir>` | Trigger accuracy testing (90% trigger rate, 0% false positive target) |

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

## Frontmatter Reference

### Required Fields

```yaml
---
name: hyphen-case-name  # ≤64 chars, no consecutive hyphens
description: >-         # ≤1024 chars, trigger context in first 250 chars
  Analyzes X for Y. Use when the user asks to "do X", "check Y",
  or "review Z". Produces structured reports with actionable findings.
---
```

The description field is the **primary trigger mechanism**. Front-load the first 250 chars with what the skill does AND when to use it. Include quoted trigger phrases. Write in third person.

### Agent Skills Open Standard Fields

These fields work on claude.ai, Cursor, Gemini CLI, and all Agent Skills-compatible tools:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Skill identifier (required) |
| `description` | string | What it does + when to use (required) |
| `license` | string | License name |
| `compatibility` | string | Environment requirements |
| `metadata` | object | Arbitrary key-value pairs (e.g., `version: "1.0.0"`) |
| `allowed-tools` | list | Pre-approved tool permissions |

### Claude Code Extension Fields

These fields work in Claude Code CLI only:

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `model` | string | opus, sonnet, haiku | Override conversation model |
| `effort` | string/int | low, medium, high, max, or integer | Token budget control |
| `context` | string | fork | Run as isolated sub-agent |
| `agent` | string | Explore, Plan, general-purpose | Agent type (with context: fork) |
| `paths` | string/list | Glob patterns | Conditional activation by file type |
| `argument-hint` | string | Argument format | Help text for /skill arguments |
| `user-invocable` | bool | true/false | Allow user slash-command |
| `disable-model-invocation` | bool | true/false | Prevent auto-invocation |
| `shell` | string | bash, powershell | Shell for inline code blocks |
| `hooks` | object | Hook configuration | Lifecycle hooks (PreToolUse, PostToolUse, TaskCreated, etc.) |

### Deprecated / Experimental Fields

| Field | Status | Migration |
|-------|--------|-----------|
| `when_to_use` | Deprecated | Fold trigger phrases into `description` (first 250 chars) |
| `version` (top-level) | Deprecated | Move to `metadata.version` |
| `depends-on` | Experimental | Open proposal only, not yet in spec |
| `suggests` | Experimental | Open proposal only, not yet in spec |

### Tool Constraint Patterns

```yaml
allowed-tools:
  - Read
  - Bash(git:*)                              # Only git commands
  - Write(src/*)                             # Only writes in src/
  - Bash(${CLAUDE_SKILL_DIR}/scripts/run.sh:*)  # Only specific script
```

### Variable Substitution

| Variable | Purpose |
|----------|---------|
| `$ARGUMENTS` | All arguments passed to the skill |
| `$ARGUMENTS[0]`, `$0` | First argument by index |
| `${CLAUDE_SKILL_DIR}` | Skill's installation directory (portable) |
| `${CLAUDE_SESSION_ID}` | Current session ID |

---

## Eval Infrastructure

Inspired by Anthropic's [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator), the eval system enables iterative skill improvement:

### Workflow

```
Draft skill → Write eval prompts → Run evals → Grade → Review → Improve → Repeat
```

### evals.json

Create `evals/evals.json` in your skill directory:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "name": "realistic-test-case",
      "prompt": "Detailed, realistic user prompt...",
      "expected_output": "What success looks like",
      "expectations": [
        "Output includes file:line references",
        "Score uses weighted formula"
      ]
    }
  ]
}
```

### Running Evals

```bash
# Run all evals against skill
./scripts/run-eval.sh my-skill/

# Run baseline (without skill) for comparison
./scripts/run-eval.sh my-skill/ --baseline

# Grade results with grader agent (via Task tool)
# See references/agents/grader-agent.md

# Aggregate into benchmark
python3 scripts/aggregate-benchmark.py my-skill/eval-workspace/iteration-1 --skill-name my-skill
```

### Trigger Testing

Test that your skill's description activates it for relevant queries and NOT for irrelevant ones:

```bash
# Create trigger-tests.json in your skill directory
cat > my-skill/trigger-tests.json << 'EOF'
{
  "skill_name": "my-skill",
  "should_trigger": ["Help me format JSON", "Format this JSON file"],
  "should_not_trigger": ["What's the weather?", "Write Python code"]
}
EOF

# Run trigger tests (goal: >=90% trigger rate, 0% false positives)
./scripts/test-triggers.sh my-skill/
./scripts/test-triggers.sh my-skill/ --json    # Machine-readable output
```

See `references/validation/trigger-test-schema.md` for the full schema.

### Description Optimization

```bash
# Optimize description for trigger accuracy (with negative trigger generation)
python3 scripts/optimize-description.py my-skill/ --json --verbose
```

### Agents

| Agent | Purpose |
|-------|---------|
| `grader-agent.md` | Evaluate expectations against outputs with evidence |
| `comparator-agent.md` | Blind A/B comparison between skill versions |

See `references/validation/eval-schema.md` for full JSON schemas.

---

## Project Structure

```
platxa-skill-generator/
├── SKILL.md                    # Main skill definition (entry point)
├── README.md                   # This file
├── CLAUDE.md                   # Claude Code guidance
├── pyproject.toml              # Python project config
├── LICENSE                     # MIT License
│
├── scripts/                    # 20 executable scripts
│   ├── validate-all.sh         # Master validation orchestrator
│   ├── validate-structure.sh   # Directory structure checks
│   ├── validate-frontmatter.sh # YAML frontmatter validation (--claude-ai mode)
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
│   ├── test-scripts.sh         # Script test runner
│   ├── test-triggers.sh        # Trigger accuracy testing
│   ├── run-eval.sh             # Eval prompt runner (claude -p)
│   ├── aggregate-benchmark.py  # Benchmark aggregation (mean/stddev)
│   ├── optimize-description.py # Description trigger optimizer
│   └── package-skill.py        # .skill archive packager
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
├── references/                 # 145 domain knowledge files
│   ├── agents/                 # 9 subagent definitions (incl. grader, comparator)
│   ├── patterns/               # 60 implementation patterns
│   ├── templates/              # 9 skill type templates
│   ├── orchestration/          # 7 workflow patterns
│   ├── discovery/              # 3 research patterns
│   ├── generation/             # 13 content generation patterns
│   ├── validation/             # 7 quality validation patterns (incl. eval-schema, trigger-test-schema)
│   ├── installation/           # 10 install/export patterns
│   ├── interaction/            # 9 user interaction patterns
│   ├── architecture/           # 2 architecture patterns
│   ├── scripts/                # 11 script generation patterns
│   ├── spec/                   # 2 specification references
│   └── examples/               # 2 example skills
│
├── tests/                      # 164 tests across 7 test files
│   ├── test_validate_frontmatter.py  # 56 frontmatter tests (XML, reserved names, claude-ai mode)
│   ├── test_validate_structure.py    # 18 structure tests (README.md presence check)
│   ├── test_count_tokens.py          # 10 token tests
│   ├── test_score_skill.py           # 50 quality scorer tests (3-part structure, actionability)
│   ├── test_check_dependencies.py    # 8 dependency tests
│   ├── test_circular_deps.py         # 9 cycle detection tests
│   ├── test_integration.py           # 13 integration tests (incl. catalog regression)
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
| **Spec Compliance** | 25% | Frontmatter validity, name format, Anthropic 3-part description structure [What]+[When]+[Capabilities], XML tag security, reserved name check, trigger context in first 250 chars, deprecated field penalties |
| **Content Depth** | 25% | Placeholders, generic filler, vocabulary diversity, instruction actionability, advanced pattern bonuses |
| **Example Quality** | 20% | Code blocks, language labels, substance, YAML/JSON validity |
| **Structure** | 15% | Required sections, heading count, hierarchy, progressive disclosure |
| **Token Efficiency** | 15% | Line count, word count (5,000-word Anthropic limit), sentence length, references |

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

### Advanced Pattern Bonuses

| Pattern | Bonus | Detection |
|---------|-------|-----------|
| Parallel sub-agents | +0.5 | Task/Agent tool + parallel/concurrent language |
| Auto-fix capability | +0.5 | Edit tool + fix/apply workflow language |
| CLAUDE.md integration | +0.3 | References project conventions |
| `${CLAUDE_SKILL_DIR}` usage | +0.3 | Portable script references |
| argument-hint declared | +0.3 | Better discoverability |
| Smart scope detection | +0.2 | git diff or dynamic context |
| Finding filtering | +0.2 | Deduplication and false-positive filtering |

### Consistency Checks

- `argument-hint` without `$ARGUMENTS` in body triggers a warning
- `$ARGUMENTS` without `argument-hint` suggests adding it
- SKILL.md > 3000 tokens without `references/` triggers progressive disclosure penalty
- Quoted trigger phrases in description beyond first 250 chars get penalized
- Non-string metadata values warned for claude.ai compatibility
- XML angle brackets (`<`, `>`) in frontmatter field values are rejected (security)
- Reserved names containing `claude` or `anthropic` segments are rejected
- README.md inside skill folder generates a warning (all docs go in SKILL.md or references/)
- Vague instructions ("validate the data before proceeding") get penalized vs specific actionable ones
- Descriptions missing Anthropic 3-part structure [What]+[When]+[Capabilities] lose points
- SKILL.md exceeding 5,000 words triggers large context warning (Anthropic limit)

### Execution Tiers

| Tier | Criteria | Capabilities |
|------|----------|-------------|
| **Simple** | 1-2 dimensions, no code modification | Read, Grep, Glob, Bash |
| **Intermediate** | 2-3 dimensions, optional mechanical fixes | + Task, Edit |
| **Advanced** | 3+ dimensions, parallel agents, auto-fix | + Task, Edit, Write + CLAUDE.md + filtering |

---

## Testing

```bash
# Run all 164 tests
pytest tests/ -v

# Run specific test file
pytest tests/test_score_skill.py -v

# Run by marker
pytest tests/ -m frontmatter
pytest tests/ -m integration

# Run catalog regression only
pytest tests/test_integration.py -k catalog -v

# Run claude-ai compatibility tests
pytest tests/test_validate_frontmatter.py -k claude_ai -v
```

All tests use **real file system operations** -- no mocks or simulations.

---

## Troubleshooting

### Skill not recognized after installation

```bash
ls ~/.claude/skills/platxa-skill-generator/SKILL.md   # Verify location
head -5 ~/.claude/skills/platxa-skill-generator/SKILL.md  # Check frontmatter
```

### Quality score too low

Run `score-skill.py --verbose` for actionable suggestions. Common fixes:
- Add trigger phrases to description (first 250 chars)
- Move `version` to `metadata.version`
- Remove `when_to_use` field (fold into description)
- Add code block language labels

### validate-frontmatter.sh shows deprecation warnings

Fields not in the Agent Skills open standard trigger warnings:
- `when_to_use` -- fold trigger phrases into description
- `version` (top-level) -- move to `metadata.version`
- `depends-on` / `suggests` -- experimental, open proposal only

Use `--claude-ai` flag for strict open-standard-only validation.

### Scripts not executable

```bash
chmod +x scripts/*.sh
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run before submitting:

```bash
./scripts/validate-all.sh .    # All validators pass
pytest tests/ -v               # All 164 tests pass
shellcheck scripts/*.sh        # No warnings
ruff check scripts/            # Python linting
```

---

## License

MIT License -- See [LICENSE](LICENSE) for details.

---

**Version**: 3.1.0
**Created by**: DJ Patel -- Founder & CEO, Platxa | https://platxa.com
**Based on**: Anthropic's [Agent Skills](https://agentskills.io) Open Standard + [The Complete Guide to Building Skills for Claude](https://docs.anthropic.com) + [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
