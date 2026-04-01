# Smart Scope Pattern

Analyzer skills should detect their scope automatically instead of always asking
the user. This pattern provides a cascade of scope detection strategies.

## Scope Detection Cascade

Try each strategy in order, use the first that succeeds:

```
1. User provided explicit target → use it
   /skill-name src/auth/       → analyze src/auth/
   /skill-name handler.py      → analyze handler.py

2. Git diff has changes → analyze changed files
   git diff --name-only         → unstaged changes
   git diff --cached --name-only → staged changes
   git diff HEAD~1 --name-only  → last commit

3. Current directory has source files → analyze them
   Detect language, find source files

4. Nothing found → ask the user
   "What would you like me to analyze?"
```

## Implementation with Dynamic Context Injection

Use the `` !`command` `` syntax for zero-latency scope detection:

```markdown
## Workflow

### Step 1: Determine Scope

**Changed files in this repository:**
!`git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null`

If files are listed above, analyze those files.
If no files listed, analyze $ARGUMENTS or ask what to review.
```

The backtick commands run as preprocessing — Claude receives the actual file list
without spending a tool call to discover it.

## Argument Handling

When the skill accepts a focus area argument:

```markdown
Parse $ARGUMENTS for:
- **File path or directory**: `/skill src/auth/` → scope to that path
- **Focus keyword**: `/skill focus on security` → analyze all files but weight security
- **Flag**: `/skill --fix` → enable auto-fix mode

If $ARGUMENTS is empty, use the scope detection cascade above.
```

## Frontmatter for Scoped Skills

```yaml
---
name: code-review
description: Reviews code for quality, security, and efficiency. Use when reviewing
  changes before commit or analyzing specific files for issues.
argument-hint: "[path or focus area]"
---
```

## Integration with Analyzer Template

Replace the standard "Step 1: Determine Scope" with:

```markdown
### Step 1: Scope Detection

**Recent changes:**
!`git diff --name-only 2>/dev/null | head -20`
!`git diff --cached --name-only 2>/dev/null | head -20`

**Analysis target:**
- If $ARGUMENTS specifies files/directories → use those
- If git diff shows changed files → use those
- If neither → ask the user what to analyze

**Focus area** (optional):
- If $ARGUMENTS contains "focus on X" → weight X dimension higher
- Otherwise → equal weight across all dimensions
```
