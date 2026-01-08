# Troubleshooting Guide

Solutions for common issues with Platxa Skill Generator.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Generation Issues](#generation-issues)
3. [Quality Issues](#quality-issues)
4. [Script Issues](#script-issues)
5. [Performance Issues](#performance-issues)
6. [Getting Help](#getting-help)

---

## Installation Issues

### Skill not recognized after installation

**Symptoms**:
- `/skill-generator` doesn't work
- Claude says "I don't know that skill"

**Diagnosis**:
```bash
# Check skill location
ls -la ~/.claude/skills/platxa-skill-generator/SKILL.md

# Check frontmatter is valid
head -30 ~/.claude/skills/platxa-skill-generator/SKILL.md
```

**Solutions**:

1. **Verify location**: Skill must be in `~/.claude/skills/` or `.claude/skills/`
   ```bash
   cp -r platxa-skill-generator ~/.claude/skills/
   ```

2. **Check SKILL.md exists**: The file must exist at the root
   ```bash
   ls ~/.claude/skills/platxa-skill-generator/SKILL.md
   ```

3. **Restart Claude Code**: Skills are loaded at startup
   ```bash
   # Exit and restart Claude Code
   ```

4. **Check frontmatter syntax**: Must be valid YAML
   ```yaml
   ---
   name: platxa-skill-generator
   description: ...
   ---
   ```

---

### Permission denied on scripts

**Symptoms**:
- `bash: ./scripts/validate-all.sh: Permission denied`

**Solution**:
```bash
# Make all scripts executable
chmod +x ~/.claude/skills/platxa-skill-generator/scripts/*.sh

# Verify
ls -la ~/.claude/skills/platxa-skill-generator/scripts/
```

---

### Git clone fails

**Symptoms**:
- `fatal: repository not found`
- `Permission denied (publickey)`

**Solutions**:

1. **Use HTTPS instead of SSH**:
   ```bash
   git clone https://github.com/platxa/platxa-skill-generator.git
   ```

2. **Use direct download**:
   ```bash
   curl -L https://github.com/platxa/platxa-skill-generator/archive/main.zip -o skill.zip
   unzip skill.zip
   mv platxa-skill-generator-main ~/.claude/skills/platxa-skill-generator
   ```

---

## Generation Issues

### Discovery phase fails or times out

**Symptoms**:
- `[Discovery] Timeout waiting for research...`
- `[Discovery] No results found`

**Causes**:
- No internet connection
- Topic too obscure or specific
- Web search rate limiting

**Solutions**:

1. **Check internet connection**:
   ```bash
   curl -I https://google.com
   ```

2. **Use a more common topic**: Try well-documented domains first

3. **Retry**: Transient network issues resolve on retry

4. **Proceed without research**: The generator can still create a skill with reduced quality

---

### Architecture phase selects wrong type

**Symptoms**:
- Generator chooses "Builder" when you wanted "Analyzer"
- Skill type doesn't match your intent

**Solutions**:

1. **Be explicit in description**:
   ```
   User: Create an ANALYZER skill that inspects code for...
   ```

2. **Use type keywords**:
   - Builder: "create", "generate", "scaffold"
   - Guide: "teach", "explain", "how to"
   - Automation: "automate", "batch", "process"
   - Analyzer: "analyze", "inspect", "audit"
   - Validator: "validate", "verify", "check"

---

### Generation produces empty or minimal content

**Symptoms**:
- SKILL.md has very few instructions
- References folder is empty
- Scripts are placeholder only

**Causes**:
- Insufficient description
- Discovery returned poor results
- Interrupted workflow

**Solutions**:

1. **Provide detailed description**:
   ```
   User: A skill that generates Python API documentation
         following NumPy docstring format, including
         parameter types, return values, examples,
         and cross-references between functions.
   ```

2. **Specify target users**:
   ```
   User: ... for Python developers maintaining large codebases
   ```

3. **Include success criteria**:
   ```
   User: ... that outputs HTML documentation with search
   ```

---

## Quality Issues

### Quality score too low (< 7.0)

**Symptoms**:
- `[Validation] Quality score: 5.2/10`
- Skill fails validation

**Score Components**:

| Component | Weight | How to Improve |
|-----------|--------|----------------|
| Structure | 20% | Valid frontmatter, correct directories |
| Content | 30% | More examples, clearer instructions |
| Expertise | 25% | Better references, real domain knowledge |
| Security | 15% | Safe scripts, no dangerous commands |
| Efficiency | 10% | Concise content, within token budget |

**Solutions by Component**:

**Low Structure Score**:
```bash
# Validate frontmatter
./scripts/validate-frontmatter.sh

# Validate structure
./scripts/validate-structure.sh
```

**Low Content Score**:
- Add more examples to SKILL.md
- Include step-by-step workflows
- Add expected outputs

**Low Expertise Score**:
- Provide better initial description
- Specify authoritative sources
- Let discovery phase complete fully

**Low Security Score**:
- Review generated scripts for dangerous commands
- Remove any `rm -rf`, `sudo`, or network operations
- Use safe defaults

**Low Efficiency Score**:
- Reduce SKILL.md length (< 500 lines)
- Remove redundant content
- Consolidate similar instructions

---

### Frontmatter validation fails

**Symptoms**:
- `[ERROR] Invalid YAML frontmatter`
- `[ERROR] Missing required field: name`

**Common Issues**:

1. **Missing dashes**:
   ```yaml
   # Wrong
   name: my-skill
   description: Does things

   # Correct
   ---
   name: my-skill
   description: Does things
   ---
   ```

2. **Invalid characters in name**:
   ```yaml
   # Wrong - spaces and uppercase
   name: My Skill Name

   # Correct - lowercase with hyphens
   name: my-skill-name
   ```

3. **Description too long**:
   ```yaml
   # Must be <= 1024 characters
   description: A concise description...
   ```

---

## Script Issues

### Scripts fail with syntax errors

**Symptoms**:
- `syntax error near unexpected token`
- `bad interpreter: No such file or directory`

**Solutions**:

1. **Check shebang**:
   ```bash
   # First line should be
   #!/usr/bin/env bash
   ```

2. **Convert line endings (Windows)**:
   ```bash
   # Install dos2unix
   sudo apt-get install dos2unix  # Linux
   brew install dos2unix          # macOS

   # Convert
   dos2unix scripts/*.sh
   ```

3. **Check bash version**:
   ```bash
   bash --version
   # Requires 4.0+
   ```

---

### Python script fails

**Symptoms**:
- `ModuleNotFoundError: No module named 'tiktoken'`
- `python3: command not found`

**Solutions**:

1. **Install Python 3.10+**:
   ```bash
   python3 --version
   # Should be 3.10 or higher
   ```

2. **Install dependencies** (if needed):
   ```bash
   pip3 install tiktoken
   ```

3. **Skip token counting**: The utility is optional
   ```bash
   # Remove the script call from validation
   ```

---

## Performance Issues

### Generation takes too long

**Symptoms**:
- Each phase takes > 60 seconds
- Process seems stuck

**Causes**:
- Slow network connection
- Complex topic requiring extensive research
- Resource constraints

**Solutions**:

1. **Simplify topic**: Start with well-documented domains

2. **Reduce scope**: Generate smaller, focused skills

3. **Check network**:
   ```bash
   ping -c 3 google.com
   ```

4. **Interrupt and retry**: Use Ctrl+C and try again

---

### Out of memory errors

**Symptoms**:
- Claude Code becomes unresponsive
- Browser tab crashes

**Solutions**:

1. **Close other tabs/applications**
2. **Restart Claude Code**
3. **Generate smaller skills**
4. **Use project skills** instead of user skills (smaller scope)

---

## Getting Help

### Self-Diagnosis

Run the full diagnostic:

```bash
cd ~/.claude/skills/platxa-skill-generator
./scripts/validate-all.sh

# Check specific components
./scripts/validate-frontmatter.sh
./scripts/validate-structure.sh
./scripts/security-check.sh
```

### Check Patterns Documentation

```bash
ls references/patterns/
# Review relevant pattern files
cat references/patterns/troubleshooting.md
```

### Report Issues

1. **Search existing issues**: [GitHub Issues](https://github.com/platxa/platxa-skill-generator/issues)

2. **Create new issue** with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Output from `./scripts/validate-all.sh`
   - Your environment (OS, Claude Code version)

### Community Support

- [GitHub Discussions](https://github.com/platxa/platxa-skill-generator/discussions)
- [Anthropic Discord](https://discord.gg/anthropic)

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Skill not found | `cp -r skill ~/.claude/skills/` |
| Permission denied | `chmod +x scripts/*.sh` |
| Quality < 7.0 | More detailed description |
| Discovery fails | Check internet, retry |
| Wrong skill type | Use type keywords |
| Frontmatter error | Check YAML syntax |
| Script error | Check shebang, line endings |

---

**Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
