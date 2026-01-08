# Getting Started with Platxa Skill Generator

This guide walks you through creating your first Claude Code skill using the Platxa Skill Generator.

**Time Required**: 10-15 minutes

---

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Understanding Skills](#understanding-skills)
3. [Your First Skill](#your-first-skill)
4. [Understanding the Output](#understanding-the-output)
5. [Next Steps](#next-steps)

---

## Before You Begin

### What You'll Need

- Claude Code CLI installed and configured
- Basic familiarity with command-line interfaces
- An idea for a skill you want to create

### Verify Your Setup

```bash
# Verify Claude Code is installed
claude --version

# Verify the skill generator is installed
ls ~/.claude/skills/platxa-skill-generator/SKILL.md
```

If the second command fails, see the [Installation Guide](./installation.md).

---

## Understanding Skills

### What is a Claude Code Skill?

A skill is a packaged set of instructions that teaches Claude how to perform specialized tasks. Skills contain:

- **SKILL.md** - The main instruction file with YAML frontmatter
- **scripts/** - Helper scripts for automation
- **references/** - Domain knowledge and best practices

### Skill Types

| Type | Use When You Want To... |
|------|------------------------|
| **Builder** | Create or generate something new |
| **Guide** | Teach or explain a concept |
| **Automation** | Automate a repetitive task |
| **Analyzer** | Inspect or audit code/data |
| **Validator** | Verify quality or compliance |

---

## Your First Skill

Let's create a simple skill that formats Markdown files.

### Step 1: Start the Generator

In Claude Code, type:

```
/skill-generator
```

### Step 2: Describe Your Skill

When prompted, provide a clear description:

```
User: A skill that formats and lints Markdown files,
      fixing common issues like inconsistent headers,
      trailing whitespace, and missing blank lines.
```

### Step 3: Watch the Workflow

The generator progresses through four phases:

#### Discovery Phase (30-60 seconds)

```
[Discovery] Researching Markdown formatting...
  - Found: CommonMark specification
  - Found: markdownlint rules
  - Analyzing: Prettier Markdown plugin patterns
```

The generator searches the web for best practices and existing solutions.

#### Architecture Phase (10-20 seconds)

```
[Architecture] Designing skill structure...
  - Type: Automation
  - Rationale: Transforms files automatically
  - Scripts: format.sh, lint.sh
  - References: formatting-rules.md
```

The generator selects the appropriate skill type and plans the structure.

#### Generation Phase (20-40 seconds)

```
[Generation] Creating skill files...
  - markdown-formatter/SKILL.md (156 lines)
  - markdown-formatter/scripts/format.sh
  - markdown-formatter/references/formatting-rules.md
```

The generator creates all skill files with domain-specific content.

#### Validation Phase (5-10 seconds)

```
[Validation] Quality check...
  - Frontmatter: OK
  - Structure: OK
  - Token budget: OK (3,142 tokens)
  - Quality score: 8.1/10

Install to ~/.claude/skills/markdown-formatter? (y/n)
```

The generator validates the skill against Anthropic's specification.

### Step 4: Install the Skill

Type `y` to install, or `n` to review/modify first.

### Step 5: Use Your New Skill

```
User: /markdown-formatter
```

Your skill is now ready to use!

---

## Understanding the Output

### Generated File Structure

```
markdown-formatter/
├── SKILL.md                    # Main skill file
├── scripts/
│   ├── format.sh               # Formatting script
│   └── lint.sh                 # Linting script
└── references/
    └── formatting-rules.md     # Markdown best practices
```

### SKILL.md Contents

```yaml
---
name: markdown-formatter
description: Formats and lints Markdown files, fixing common issues...
allowed-tools:
  - Read
  - Write
  - Bash
metadata:
  version: "1.0.0"
  author: "DJ Patel — Founder & CEO, Platxa | https://platxa.com"
  tags:
    - markdown
    - formatting
    - linting
---

# Markdown Formatter

[Instructions for Claude on how to format Markdown files...]
```

### Quality Score Breakdown

| Component | Your Score | What It Measures |
|-----------|------------|-----------------|
| Structure | 9.0 | Valid frontmatter, correct directories |
| Content | 8.5 | Clear instructions, useful examples |
| Expertise | 7.5 | Real domain knowledge in references |
| Security | 8.0 | Safe scripts, no vulnerabilities |
| Efficiency | 8.0 | Token budget, concise content |
| **Total** | **8.1** | Weighted average |

---

## Next Steps

### Improve Your Skill

1. **Add more examples** to the SKILL.md
2. **Expand references** with additional best practices
3. **Test edge cases** and update instructions

### Create More Skills

Try creating skills for:

- Code formatting for a specific language
- Documentation generation
- Test case creation
- Security scanning
- API design validation

### Share Your Skills

1. Push to a GitHub repository
2. Share the repository URL with your team
3. Others can install with:
   ```bash
   git clone <your-repo-url> ~/.claude/skills/<skill-name>
   ```

---

## Troubleshooting

### Skill not appearing after installation

```bash
# Check the skill exists
ls ~/.claude/skills/<skill-name>/SKILL.md

# Restart Claude Code to reload skills
```

### Quality score too low

- Provide a more detailed description
- Be specific about what the skill should do
- Include target users and use cases

### Generator seems stuck

- Check internet connectivity (needed for research)
- Try with a simpler or more common topic
- The generator will timeout after 60 seconds per phase

---

## Additional Resources

- [Installation Guide](./installation.md)
- [Skill Types Reference](./skill-types.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Anthropic Agent Skills Spec](https://github.com/anthropics/skills)

---

**Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
