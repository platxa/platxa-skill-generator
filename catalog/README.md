# Claude Code Skills Catalog

> A curated collection of production-ready skills for Claude Code CLI.
>
> **Maintained by**: [Platxa](https://platxa.com) | **License**: MIT

---

## Quick Install

```bash
# Clone the repository
git clone https://github.com/platxa/platxa-skill-generator.git
cd platxa-skill-generator

# Install a single skill
./scripts/install-from-catalog.sh code-documenter

# Install to project instead of user directory
./scripts/install-from-catalog.sh code-documenter --project

# List all available skills
./scripts/install-from-catalog.sh --list

# Install all skills
./scripts/install-from-catalog.sh --all
```

---

## Skills Index

| Skill | Description | Type | Status |
|-------|-------------|------|--------|
| [code-documenter](#code-documenter) | Generate documentation across Python, JS/TS, Java, Go, Rust | Automation | Ready |
| [commit-message](#commit-message) | Generate conventional commit messages from staged changes | Automation | Ready |
| [test-generator](#test-generator) | Generate unit tests with comprehensive coverage | Builder | Ready |
| [pr-description](#pr-description) | Generate PR descriptions from git history | Builder | Ready |
| [platxa-frontend-builder](#platxa-frontend-builder) | Generate React/Next.js components with TypeScript and Tailwind | Builder | Ready |

---

## Available Skills

### code-documenter

**Type**: Automation | **Category**: Code Quality

Automatically generates and improves code documentation across multiple languages:
- Python (Google, NumPy, Sphinx styles)
- JavaScript/TypeScript (JSDoc, TSDoc)
- Java (Javadoc)
- Go (godoc)
- Rust (rustdoc)

```bash
./scripts/install-from-catalog.sh code-documenter
```

**Usage**:
```
User: Document the functions in src/utils/
Assistant: [Analyzes files, generates docstrings following detected style]
```

---

### commit-message

**Type**: Automation | **Category**: Git Workflow

Generates conventional commit messages by analyzing staged changes:
- Detects change type (feat, fix, refactor, docs, etc.)
- Suggests scope from file paths
- Follows Conventional Commits specification
- Supports breaking change notation

```bash
./scripts/install-from-catalog.sh commit-message
```

**Usage**:
```
User: Generate a commit message for my staged changes
Assistant: [Analyzes diff, generates: feat(components): add Button component]
```

---

### test-generator

**Type**: Builder | **Category**: Testing

Generates comprehensive unit tests for existing code:
- Detects testing framework (pytest, Jest, JUnit, etc.)
- Creates tests following AAA pattern
- Covers happy paths, boundaries, edge cases, errors
- Supports parameterized tests

```bash
./scripts/install-from-catalog.sh test-generator
```

**Usage**:
```
User: Generate tests for src/utils/calculator.py
Assistant: [Creates tests/test_calculator.py with comprehensive test cases]
```

---

### pr-description

**Type**: Builder | **Category**: Git Workflow

Generates pull request descriptions from commits and diff:
- Categorizes changes by file type
- Extracts related issue references
- Detects breaking changes
- Follows PR template if present

```bash
./scripts/install-from-catalog.sh pr-description
```

**Usage**:
```
User: Generate a PR description for this branch
Assistant: [Analyzes commits, generates structured PR description]
```

---

### platxa-frontend-builder

**Type**: Builder | **Category**: Frontend Development

Generates production-ready React/Next.js components for the Platxa platform:
- Server Components (data fetching, layouts)
- Client Components (interactive UI, forms)
- Form components with React Hook Form + Zod validation
- Data tables with TypeScript generics
- Accessible UI primitives with ARIA attributes

```bash
./scripts/install-from-catalog.sh platxa-frontend-builder
```

**Usage**:
```
User: Create a user profile card with avatar, name, and email
Assistant: [Generates TypeScript component with proper types, Tailwind styling, accessibility]
```

**Related Skills**: Uses `platxa-monaco-config` for editor integration.

---

## Installation Methods

### Method 1: Install Script (Recommended)

```bash
./scripts/install-from-catalog.sh <skill-name> [--user|--project]
```

| Flag | Description |
|------|-------------|
| `--user` | Install to `~/.claude/skills/` (default) |
| `--project` | Install to `.claude/skills/` |
| `--list` | List all available skills |
| `--all` | Install all skills |
| `--force` | Overwrite existing without prompting |

### Method 2: Manual Copy

```bash
# Copy skill to user directory
cp -r catalog/<skill-name> ~/.claude/skills/

# Or copy to project directory
cp -r catalog/<skill-name> .claude/skills/
```

### Method 3: Symbolic Link (Development)

```bash
# Link for development (changes reflect immediately)
ln -s $(pwd)/catalog/<skill-name> ~/.claude/skills/<skill-name>
```

---

## Skill Quality Standards

All skills in this catalog meet these requirements:

| Requirement | Threshold |
|-------------|-----------|
| SKILL.md exists | Required |
| Valid YAML frontmatter | Required |
| Name (hyphen-case) | <= 64 chars |
| Description | <= 1024 chars |
| Token budget | < 5000 tokens |
| All validations pass | Required |

### Validation

```bash
# Validate a skill before use
./scripts/validate-all.sh catalog/<skill-name>

# Check token count
python3 scripts/count-tokens.py catalog/<skill-name>
```

---

## Contributing Skills

We welcome community contributions!

### Quick Contribution Steps

1. **Create your skill** using the skill generator:
   ```
   User: /platxa-skill-generator
   ```

2. **Test thoroughly** in your own projects

3. **Validate quality**:
   ```bash
   ./scripts/validate-all.sh /path/to/your-skill
   ```

4. **Submit PR** with:
   - Skill directory in `catalog/`
   - Updated catalog README (add to index table)
   - Brief description of use case

### Skill Submission Checklist

- [ ] SKILL.md has valid frontmatter
- [ ] All validations pass
- [ ] No placeholder content
- [ ] Scripts are executable and tested
- [ ] References contain real domain expertise
- [ ] Examples show realistic usage
- [ ] Tested on real projects

---

## Roadmap

### Planned Skills

| Skill | Type | Category | Priority |
|-------|------|----------|----------|
| code-reviewer | Analyzer | Code Quality | High |
| changelog-generator | Builder | Git Workflow | Medium |
| readme-generator | Builder | Documentation | Medium |
| dependency-auditor | Analyzer | Security | High |
| dockerfile-generator | Builder | DevOps | Medium |
| api-documenter | Builder | Documentation | Medium |

### Suggest a Skill

Open an issue with:
- Skill name and description
- Use case and target users
- Example workflow

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Catalog Version**: 1.0.0 | **Skills Count**: 5
