# Platxa Skill Generator

> Autonomous skill creator for Claude Code CLI using multi-phase orchestrated workflows with Task tool subagents.
>
> **Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
>
> **Based on**: Anthropic's [Agent Skills](https://github.com/anthropics/skills) specification

---

## Table of Contents

- [Skills Catalog](#skills-catalog)
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Installation](#installation)
- [Usage](#usage)
- [Skill Types](#skill-types)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Quality Standards](#quality-standards)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Skills Catalog

**Ready-to-use skills for the community!** Browse and install production-ready skills from our curated catalog.

| Skill | Description | Install |
|-------|-------------|---------|
| **[code-documenter](catalog/code-documenter/)** | Generate docs for Python, JS/TS, Java, Go, Rust | `./scripts/install-from-catalog.sh code-documenter` |
| **[commit-message](catalog/commit-message/)** | Generate conventional commit messages | `./scripts/install-from-catalog.sh commit-message` |
| **[test-generator](catalog/test-generator/)** | Generate comprehensive unit tests | `./scripts/install-from-catalog.sh test-generator` |
| **[pr-description](catalog/pr-description/)** | Generate PR descriptions from git history | `./scripts/install-from-catalog.sh pr-description` |

```bash
# Quick install
./scripts/install-from-catalog.sh --list        # See all skills
./scripts/install-from-catalog.sh code-documenter  # Install one
./scripts/install-from-catalog.sh --all         # Install all
```

See the full **[Skills Catalog](catalog/README.md)** for details and contribution guidelines.

---

## Overview

Platxa Skill Generator creates production-ready Claude Code skills by orchestrating specialized subagents through a multi-phase workflow:

1. **Discovery** - Research domain knowledge via web search and existing skill analysis
2. **Architecture** - Design skill structure based on type (Builder/Guide/Automation/Analyzer/Validator)
3. **Generation** - Create SKILL.md, scripts, and reference documentation
4. **Validation** - Verify against Anthropic's spec with quality scoring

### Who Is This For?

- **Developers** who want to extend Claude Code with custom capabilities
- **Teams** building specialized AI workflows for their domains
- **Organizations** creating reusable skill libraries

---

## Features

| Feature | Description |
|---------|-------------|
| **Autonomous Creation** | Minimal user input, maximum automation |
| **Multi-Phase Workflow** | Specialized subagents for each phase |
| **Five Skill Types** | Builder, Guide, Automation, Analyzer, Validator |
| **Quality Gates** | Validation against Anthropic's Agent Skills specification |
| **Token Budget Management** | SKILL.md optimized for context efficiency |
| **Script Security** | Executable helpers with security checks |
| **Web Research** | Automatic domain knowledge discovery |
| **Template System** | Pre-built templates for each skill type |

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Claude Code CLI** | Latest | Required runtime environment |
| **Git** | 2.0+ | Clone the repository |
| **Bash** | 4.0+ | Run validation scripts |
| **Python** | 3.10+ | Token counting utility (optional) |

### Verify Prerequisites

```bash
# Check Claude Code is installed
claude --version

# Check Git
git --version

# Check Bash
bash --version

# Check Python (optional)
python3 --version
```

---

## Quick Start (5 Minutes)

Get your first skill generated in 5 minutes:

### Step 1: Install the Skill (1 minute)

```bash
# Clone and install as user skill
git clone https://github.com/platxa/platxa-skill-generator.git
cp -r platxa-skill-generator ~/.claude/skills/
```

### Step 2: Verify Installation (30 seconds)

```bash
# Check the skill is installed
ls ~/.claude/skills/platxa-skill-generator/SKILL.md
```

Expected output:
```
/home/user/.claude/skills/platxa-skill-generator/SKILL.md
```

### Step 3: Generate Your First Skill (3 minutes)

In Claude Code, run:

```
User: /skill-generator
Assistant: What skill would you like to create?
User: A skill that formats JSON files
```

The generator will:
1. Research JSON formatting best practices
2. Design a "Builder" type skill
3. Generate the skill files
4. Validate quality (>= 7.0/10)
5. Offer to install the new skill

### Step 4: Use Your New Skill

```
User: /json-formatter
```

**Congratulations!** You've created your first Claude Code skill.

---

## Installation

### Option 1: User Skill (Recommended)

Available across all your projects:

```bash
# Clone the repository
git clone https://github.com/platxa/platxa-skill-generator.git

# Install to user skills directory
cp -r platxa-skill-generator ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/platxa-skill-generator/
```

### Option 2: Project Skill

Available only in a specific project:

```bash
# Navigate to your project
cd /path/to/your/project

# Create skills directory if needed
mkdir -p .claude/skills

# Clone and install
git clone https://github.com/platxa/platxa-skill-generator.git .claude/skills/platxa-skill-generator
```

### Option 3: Direct Download

```bash
# Download latest release
curl -L https://github.com/platxa/platxa-skill-generator/archive/main.zip -o skill-generator.zip
unzip skill-generator.zip
mv platxa-skill-generator-main ~/.claude/skills/platxa-skill-generator
```

### Verify Installation

Run the validation script:

```bash
cd ~/.claude/skills/platxa-skill-generator
./scripts/validate-all.sh
```

Expected output:
```
[OK] SKILL.md exists
[OK] Frontmatter valid
[OK] Structure valid
[OK] All validations passed
```

---

## Usage

### Basic Usage

```
User: /skill-generator
Assistant: What skill would you like to create?
User: [Describe the skill you want]
```

### With Specific Requirements

```
User: /skill-generator
User: Create a skill that:
- Analyzes Python code for security issues
- Uses OWASP Top 10 as reference
- Outputs a detailed report
```

### Workflow Phases

The generator progresses through these phases automatically:

| Phase | Duration | What Happens |
|-------|----------|--------------|
| **Discovery** | 30-60s | Web research, existing skill analysis |
| **Architecture** | 10-20s | Skill type selection, structure design |
| **Generation** | 20-40s | SKILL.md, scripts, references creation |
| **Validation** | 5-10s | Quality scoring, spec compliance check |
| **Installation** | 5s | Copy to skills directory |

### Command Options

| Command | Description |
|---------|-------------|
| `/skill-generator` | Interactive skill creation |
| `/skill-generator "description"` | Start with initial description |

---

## Skill Types

Choose the right type for your use case:

| Type | Purpose | Best For | Key Sections |
|------|---------|----------|--------------|
| **Builder** | Create new things | Code generators, scaffolders | Workflow, Templates, Output Checklist |
| **Guide** | Teach/explain | Tutorials, how-tos | Steps, Examples, Best Practices |
| **Automation** | Automate tasks | CI/CD, batch processing | Triggers, Scripts, Verification |
| **Analyzer** | Inspect/audit | Code review, security | Checklist, Metrics, Reports |
| **Validator** | Verify quality | Testing, compliance | Rules, Thresholds, Pass/Fail Criteria |

### Choosing a Skill Type

```
Is the primary goal to CREATE something new?
  └─ Yes → Builder

Is the primary goal to TEACH or EXPLAIN?
  └─ Yes → Guide

Is the primary goal to AUTOMATE a process?
  └─ Yes → Automation

Is the primary goal to INSPECT or AUDIT?
  └─ Yes → Analyzer

Is the primary goal to VERIFY or VALIDATE?
  └─ Yes → Validator
```

---

## Examples

### Example 1: Code Documenter (Automation)

```
User: /skill-generator
Assistant: What skill would you like to create?
User: A skill that generates documentation for Python code

[Discovery] Researching Python docstring standards...
  - Found: NumPy style, Google style, Sphinx format
  - Analyzing existing documentation tools

[Architecture] Designing skill structure...
  - Type: Automation
  - Scripts: generate-docs.sh, validate-docs.sh
  - References: docstring-styles.md, examples.md

[Generation] Creating skill files...
  - py-documenter/SKILL.md (142 lines)
  - py-documenter/scripts/generate-docs.sh
  - py-documenter/references/docstring-styles.md

[Validation] Quality check...
  - Frontmatter: OK
  - Structure: OK
  - Token budget: OK (2,847 tokens)
  - Quality score: 8.2/10

Install to ~/.claude/skills/py-documenter? (y/n)
```

### Example 2: Security Analyzer (Analyzer)

```
User: /skill-generator
Assistant: What skill would you like to create?
User: A skill that scans code for security vulnerabilities

[Discovery] Researching security analysis...
  - Found: OWASP Top 10, CWE database, SAST patterns
  - Analyzing: semgrep rules, bandit patterns

[Architecture] Designing skill structure...
  - Type: Analyzer
  - References: owasp-checklist.md, vulnerability-patterns.md
  - Scripts: scan.sh, report.sh

[Generation] Creating skill files...
  - security-analyzer/SKILL.md (198 lines)
  - security-analyzer/references/owasp-checklist.md
  - security-analyzer/scripts/scan.sh

[Validation] Quality score: 7.8/10

Install to ~/.claude/skills/security-analyzer? (y/n)
```

### Example 3: API Generator (Builder)

```
User: /skill-generator
Assistant: What skill would you like to create?
User: A skill that generates REST API endpoints from OpenAPI specs

[Discovery] Researching OpenAPI and API generation...
  - Found: OpenAPI 3.0 spec, code generation patterns
  - Analyzing: FastAPI, Express.js patterns

[Architecture] Designing skill structure...
  - Type: Builder
  - Templates: endpoint-template.py, router-template.py
  - Scripts: generate.sh, validate-openapi.sh

[Validation] Quality score: 8.5/10

Install to ~/.claude/skills/api-generator? (y/n)
```

---

## Project Structure

```
platxa-skill-generator/
├── SKILL.md                 # Main skill definition (entry point)
├── README.md                # This file
├── LICENSE                  # MIT License
├── CONTRIBUTING.md          # Contribution guidelines
│
├── scripts/                 # Executable helpers
│   ├── validate-all.sh      # Run all validations
│   ├── validate-structure.sh
│   ├── validate-frontmatter.sh
│   ├── install-skill.sh     # Installation helper
│   ├── security-check.sh    # Security validation
│   └── count-tokens.py      # Token counting utility
│
├── references/              # Domain knowledge and patterns
│   ├── agents/              # Subagent definitions (7 agents)
│   │   ├── discovery-agent.md
│   │   ├── architecture-agent.md
│   │   ├── generation-agent.md
│   │   ├── validation-agent.md
│   │   ├── script-agent.md
│   │   ├── reference-agent.md
│   │   └── quality-agent.md
│   │
│   ├── patterns/            # Implementation patterns (40+ files)
│   │   ├── skill-types.md
│   │   ├── domain-discovery.md
│   │   ├── quality-criteria.md
│   │   ├── state-machine.md
│   │   └── ...
│   │
│   ├── templates/           # Skill templates by type
│   │   ├── builder-template.md
│   │   ├── guide-template.md
│   │   ├── automation-template.md
│   │   ├── analyzer-template.md
│   │   └── validator-template.md
│   │
│   └── state-schema.md      # State management schema
│
└── assets/                  # Static resources
    └── skill-template/      # Empty skill template
        ├── SKILL.md
        ├── scripts/.gitkeep
        └── references/.gitkeep
```

---

## Quality Standards

Generated skills must meet these criteria to pass validation:

### Required Checks

| Check | Requirement | Validation |
|-------|-------------|------------|
| **SKILL.md** | Exists with valid YAML frontmatter | `validate-frontmatter.sh` |
| **Name** | Hyphen-case, <= 64 characters | Automated |
| **Description** | <= 1024 characters | Automated |
| **Token Budget** | < 500 lines in SKILL.md | `count-tokens.py` |
| **Tools** | Only required tools listed | Manual review |
| **Scripts** | Executable and secure | `security-check.sh` |
| **References** | Real domain expertise | Quality scoring |
| **Quality Score** | >= 7.0/10 | Quality agent |

### Quality Score Breakdown

| Component | Weight | Criteria |
|-----------|--------|----------|
| **Structure** | 20% | Valid frontmatter, correct directories |
| **Content** | 30% | Clear instructions, useful examples |
| **Expertise** | 25% | Real domain knowledge in references |
| **Security** | 15% | Safe scripts, no vulnerabilities |
| **Efficiency** | 10% | Token budget, concise content |

---

## Troubleshooting

### Common Issues

#### Skill not recognized after installation

**Symptom**: `/skill-generator` doesn't work

**Solution**:
```bash
# Verify the skill is in the correct location
ls ~/.claude/skills/platxa-skill-generator/SKILL.md

# Check frontmatter is valid
head -20 ~/.claude/skills/platxa-skill-generator/SKILL.md

# Restart Claude Code to reload skills
```

#### Quality score too low

**Symptom**: Generated skill fails validation with score < 7.0

**Solution**:
- Provide more specific description of what the skill should do
- Include target users and use cases
- Let the generator complete all phases before interrupting

#### Scripts not executable

**Symptom**: `Permission denied` when running scripts

**Solution**:
```bash
# Make all scripts executable
chmod +x ~/.claude/skills/platxa-skill-generator/scripts/*.sh
```

#### Web research fails

**Symptom**: Discovery phase times out or returns empty

**Solution**:
- Check internet connectivity
- Try with a more specific or different topic
- The generator will proceed with reduced quality if research fails

### Getting Help

1. **Check existing issues**: [GitHub Issues](https://github.com/platxa/platxa-skill-generator/issues)
2. **Read the patterns**: `references/patterns/` contains detailed documentation
3. **Run diagnostics**: `./scripts/validate-all.sh`

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Reporting issues
- Submitting pull requests
- Adding new skill types
- Improving patterns and templates
- Writing documentation

### Quick Contribution Guide

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR-USERNAME/platxa-skill-generator.git

# Create a feature branch
git checkout -b feature/your-feature

# Make changes and test
./scripts/validate-all.sh

# Commit and push
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature

# Open a Pull Request
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **[Anthropic](https://anthropic.com)** - For Claude Code and the Agent Skills specification

---

## Additional Resources

- [Claude Code](https://claude.com/product/claude-code)
- [Agent Skills Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

---

**Version**: 1.0.0
**Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
**Based on**: Anthropic's Agent Skills Specification
