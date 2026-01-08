# Installation Guide

Complete installation instructions for Platxa Skill Generator.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Verification](#verification)
4. [Updating](#updating)
5. [Uninstalling](#uninstalling)
6. [Troubleshooting Installation](#troubleshooting-installation)

---

## Prerequisites

### Required

| Requirement | Minimum Version | Check Command |
|-------------|-----------------|---------------|
| Claude Code CLI | Latest | `claude --version` |
| Git | 2.0+ | `git --version` |
| Bash | 4.0+ | `bash --version` |

### Optional

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Token counting utility |
| curl | Any | Direct download method |

### Verify Prerequisites

Run this script to check all requirements:

```bash
#!/bin/bash
echo "Checking prerequisites..."

# Claude Code
if command -v claude &> /dev/null; then
    echo "[OK] Claude Code: $(claude --version 2>/dev/null | head -1)"
else
    echo "[MISSING] Claude Code CLI not found"
fi

# Git
if command -v git &> /dev/null; then
    echo "[OK] Git: $(git --version)"
else
    echo "[MISSING] Git not found"
fi

# Bash
echo "[OK] Bash: $BASH_VERSION"

# Python (optional)
if command -v python3 &> /dev/null; then
    echo "[OK] Python: $(python3 --version)"
else
    echo "[OPTIONAL] Python not found (token counting unavailable)"
fi

echo "Done."
```

---

## Installation Methods

### Method 1: Git Clone (Recommended)

Best for: Most users, easy updates

```bash
# Clone the repository
git clone https://github.com/platxa/platxa-skill-generator.git

# Install as user skill (available in all projects)
cp -r platxa-skill-generator ~/.claude/skills/

# Or install as project skill (only in current project)
cp -r platxa-skill-generator .claude/skills/
```

### Method 2: Direct Download

Best for: Users without Git, one-time installation

```bash
# Download latest release
curl -L https://github.com/platxa/platxa-skill-generator/archive/main.zip \
     -o platxa-skill-generator.zip

# Extract
unzip platxa-skill-generator.zip

# Install
mv platxa-skill-generator-main ~/.claude/skills/platxa-skill-generator

# Clean up
rm platxa-skill-generator.zip
```

### Method 3: GitHub CLI

Best for: GitHub CLI users

```bash
# Clone using GitHub CLI
gh repo clone platxa/platxa-skill-generator

# Install
cp -r platxa-skill-generator ~/.claude/skills/
```

### Method 4: Manual Download

Best for: Users who prefer browser downloads

1. Go to https://github.com/platxa/platxa-skill-generator
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Move to `~/.claude/skills/platxa-skill-generator`

---

## Installation Locations

### User Skills Directory

Location: `~/.claude/skills/`

Skills installed here are available in all projects.

```bash
# Create directory if it doesn't exist
mkdir -p ~/.claude/skills

# Install skill
cp -r platxa-skill-generator ~/.claude/skills/
```

### Project Skills Directory

Location: `.claude/skills/` (in project root)

Skills installed here are only available in that specific project.

```bash
# Navigate to project
cd /path/to/your/project

# Create directory if needed
mkdir -p .claude/skills

# Install skill
cp -r platxa-skill-generator .claude/skills/
```

### Priority Order

When a skill exists in both locations, the project skill takes precedence.

---

## Verification

### Quick Verification

```bash
# Check skill exists
ls ~/.claude/skills/platxa-skill-generator/SKILL.md
```

Expected output:
```
/home/user/.claude/skills/platxa-skill-generator/SKILL.md
```

### Full Verification

```bash
# Navigate to skill directory
cd ~/.claude/skills/platxa-skill-generator

# Run all validations
./scripts/validate-all.sh
```

Expected output:
```
[OK] SKILL.md exists
[OK] Frontmatter valid
[OK] Structure valid
[OK] Scripts executable
[OK] All validations passed
```

### Test in Claude Code

```
User: /skill-generator
Assistant: What skill would you like to create?
```

If you see this prompt, installation was successful.

---

## Updating

### Update via Git

```bash
# Navigate to skill directory
cd ~/.claude/skills/platxa-skill-generator

# Pull latest changes
git pull origin main
```

### Update via Reinstall

```bash
# Remove old version
rm -rf ~/.claude/skills/platxa-skill-generator

# Install new version
git clone https://github.com/platxa/platxa-skill-generator.git
cp -r platxa-skill-generator ~/.claude/skills/
```

### Check Current Version

```bash
grep "version:" ~/.claude/skills/platxa-skill-generator/SKILL.md
```

---

## Uninstalling

### Remove User Skill

```bash
rm -rf ~/.claude/skills/platxa-skill-generator
```

### Remove Project Skill

```bash
rm -rf .claude/skills/platxa-skill-generator
```

### Verify Removal

```bash
ls ~/.claude/skills/platxa-skill-generator 2>/dev/null || echo "Successfully removed"
```

---

## Troubleshooting Installation

### "Permission denied" when running scripts

**Cause**: Scripts not marked as executable

**Solution**:
```bash
chmod +x ~/.claude/skills/platxa-skill-generator/scripts/*.sh
```

### "SKILL.md not found" error

**Cause**: Skill not in correct location

**Solution**:
```bash
# Check where the skill is
find ~ -name "SKILL.md" -path "*platxa-skill-generator*" 2>/dev/null

# Move to correct location
mv /found/path/platxa-skill-generator ~/.claude/skills/
```

### Skill not appearing in Claude Code

**Cause**: Claude Code hasn't reloaded skills

**Solution**:
1. Restart Claude Code
2. Or reload the current session

### "git clone" fails

**Cause**: Network issues or repository access

**Solution**:
```bash
# Try with HTTPS instead of SSH
git clone https://github.com/platxa/platxa-skill-generator.git

# Or use direct download
curl -L https://github.com/platxa/platxa-skill-generator/archive/main.zip -o skill.zip
```

### Scripts fail with "bad interpreter"

**Cause**: Windows line endings in scripts

**Solution**:
```bash
# Install dos2unix if needed
sudo apt-get install dos2unix  # Debian/Ubuntu
brew install dos2unix          # macOS

# Convert scripts
dos2unix ~/.claude/skills/platxa-skill-generator/scripts/*.sh
```

---

## Environment-Specific Notes

### macOS

Default skills directory: `/Users/<username>/.claude/skills/`

```bash
# Create directory
mkdir -p ~/.claude/skills
```

### Linux

Default skills directory: `/home/<username>/.claude/skills/`

```bash
# Create directory
mkdir -p ~/.claude/skills
```

### Windows (WSL)

Use WSL for best compatibility:

```bash
# In WSL
mkdir -p ~/.claude/skills
git clone https://github.com/platxa/platxa-skill-generator.git
cp -r platxa-skill-generator ~/.claude/skills/
```

---

**Created by**: DJ Patel — Founder & CEO, Platxa | https://platxa.com
