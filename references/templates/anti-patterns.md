# Skill Anti-Patterns

Common mistakes to avoid when creating Claude Code skills.

## Anti-Pattern Categories

| Category | Impact |
|----------|--------|
| Structure | Skill fails to load or parse |
| Content | Confusing or ineffective instructions |
| Scope | Skill too broad or too narrow |
| Performance | Token waste or slow execution |

## Structure Anti-Patterns

### Missing Frontmatter

```markdown
<!-- ❌ BAD: No YAML frontmatter -->
# My Skill

This skill does something useful.
```

```markdown
<!-- ✓ GOOD: Proper frontmatter -->
---
name: my-skill
description: Does something useful
---

# My Skill

This skill does something useful.
```

**Why it matters:** Claude Code requires YAML frontmatter to identify and invoke skills.

---

### Invalid Frontmatter Format

```yaml
# ❌ BAD: Syntax errors
---
name: my skill        # Spaces not allowed
description  Missing colon
version: "1.0
---
```

```yaml
# ✓ GOOD: Valid YAML
---
name: my-skill
description: Does something useful
version: "1.0.0"
---
```

**Why it matters:** Invalid YAML prevents skill loading.

---

### Wrong File Name

```
❌ BAD:
my-skill/
├── skill.md          # Wrong name
└── Skill.md          # Wrong case
```

```
✓ GOOD:
my-skill/
└── SKILL.md          # Exact name required
```

**Why it matters:** Claude Code only recognizes `SKILL.md` (case-sensitive).

---

### Deeply Nested References

```
❌ BAD:
my-skill/
└── references/
    └── category/
        └── subcategory/
            └── topic/
                └── file.md    # Too deep
```

```
✓ GOOD:
my-skill/
└── references/
    ├── overview.md
    └── workflow.md            # Flat structure
```

**Why it matters:** Deep nesting increases cognitive load and path complexity.

---

## Content Anti-Patterns

### Vague Instructions

```markdown
<!-- ❌ BAD: Unclear direction -->
## Instructions

Do the thing with the code. Make sure it works well.
Handle errors appropriately.
```

```markdown
<!-- ✓ GOOD: Specific guidance -->
## Instructions

1. Read the target file using the Read tool
2. Parse the function signatures from the content
3. Generate JSDoc comments for each function
4. Write the updated file using the Write tool
5. Verify the changes compile without errors
```

**Why it matters:** Vague instructions lead to inconsistent behavior.

---

### Contradictory Rules

```markdown
<!-- ❌ BAD: Conflicting guidance -->
Always use async/await for all operations.
Never use promises, prefer callbacks instead.
Use synchronous file operations for speed.
```

```markdown
<!-- ✓ GOOD: Consistent rules -->
## Async Handling

Use async/await for all I/O operations:
- File reads/writes
- Network requests
- Database queries

Avoid callbacks except when required by legacy APIs.
```

**Why it matters:** Contradictions cause unpredictable behavior.

---

### Missing Context

```markdown
<!-- ❌ BAD: No context about when to use -->
## Usage

Run this skill on your code.
```

```markdown
<!-- ✓ GOOD: Clear applicability -->
## When to Use

Use this skill when:
- Adding documentation to undocumented functions
- Updating outdated JSDoc comments
- Standardizing comment format across a project

Do NOT use for:
- Generated code files
- Third-party library code
- Files with existing comprehensive docs
```

**Why it matters:** Without context, skills get misapplied.

---

### Hardcoded Values

```markdown
<!-- ❌ BAD: Hardcoded paths and values -->
Always write output to `/home/user/output/`.
Use the API key: `sk-abc123`.
Set timeout to 30 seconds.
```

```markdown
<!-- ✓ GOOD: Flexible configuration -->
## Output Location

Write output to the location specified by the user.
Default to the current working directory if not specified.

## Configuration

Ask the user for any required API keys.
Use reasonable defaults that can be overridden.
```

**Why it matters:** Hardcoded values break portability.

---

## Scope Anti-Patterns

### Kitchen Sink Skill

```markdown
<!-- ❌ BAD: Does everything -->
# Super Developer Skill

This skill:
- Generates code in any language
- Writes tests for everything
- Reviews and refactors code
- Deploys to production
- Monitors performance
- Handles customer support
```

```markdown
<!-- ✓ GOOD: Focused purpose -->
# Python Test Generator

This skill generates pytest test cases for Python functions.

## Scope
- Unit tests for pure functions
- Mock-based tests for I/O operations
- Parametrized tests for edge cases
```

**Why it matters:** Broad skills are hard to use effectively.

---

### Micro Skill

```markdown
<!-- ❌ BAD: Too narrow -->
# Add Semicolon Skill

This skill adds a semicolon to the end of line 42.
```

```markdown
<!-- ✓ GOOD: Useful scope -->
# JavaScript Linter Fixer

This skill automatically fixes common ESLint errors:
- Missing semicolons
- Unused variables
- Inconsistent quotes
```

**Why it matters:** Overly specific skills have limited utility.

---

### Overlapping Skills

```markdown
<!-- ❌ BAD: Duplicate functionality -->
# Code Reviewer
Reviews code for bugs.

# Bug Finder
Finds bugs in code.

# Quality Checker
Checks code quality and bugs.
```

```markdown
<!-- ✓ GOOD: Distinct purposes -->
# Code Reviewer
Reviews code for style and best practices.

# Security Auditor
Scans code for security vulnerabilities.

# Performance Analyzer
Identifies performance bottlenecks.
```

**Why it matters:** Overlap causes confusion about which skill to use.

---

## Performance Anti-Patterns

### Token Bloat

```markdown
<!-- ❌ BAD: Verbose repetition -->
## Important Note

This is very important. Please pay attention to this important
information. It is important that you understand how important
this is. The importance of this cannot be overstated. Importantly,
you should always remember this important point.
```

```markdown
<!-- ✓ GOOD: Concise -->
## Important

Always validate user input before processing.
```

**Why it matters:** Wasted tokens reduce available context.

---

### Unnecessary References

```markdown
<!-- ❌ BAD: References for simple skills -->
my-skill/
├── SKILL.md (200 tokens)
└── references/
    ├── overview.md         # Repeats SKILL.md
    ├── detailed-overview.md # More repetition
    ├── introduction.md      # Even more
    └── getting-started.md   # Still repeating
```

```markdown
<!-- ✓ GOOD: Self-contained when appropriate -->
my-skill/
└── SKILL.md (200 tokens)    # Complete on its own
```

**Why it matters:** Extra files add overhead without value.

---

### Large Embedded Examples

```markdown
<!-- ❌ BAD: Huge inline examples -->
## Example

Here's a complete 500-line application:
\`\`\`python
# ... 500 lines of code ...
\`\`\`
```

```markdown
<!-- ✓ GOOD: Minimal examples -->
## Example

\`\`\`python
def greet(name: str) -> str:
    """Generate greeting."""
    return f"Hello, {name}!"
\`\`\`

For complete examples, see references/examples.md
```

**Why it matters:** Large examples consume tokens needed for actual work.

---

## Interaction Anti-Patterns

### No User Feedback

```markdown
<!-- ❌ BAD: Silent operation -->
Process all files without confirmation.
Don't show progress or results.
```

```markdown
<!-- ✓ GOOD: Interactive feedback -->
1. Show the files that will be processed
2. Ask for confirmation before proceeding
3. Display progress during execution
4. Summarize results when complete
```

**Why it matters:** Users need visibility into skill actions.

---

### Excessive Prompting

```markdown
<!-- ❌ BAD: Prompt fatigue -->
Ask the user:
1. What language?
2. What framework?
3. What version?
4. What style?
5. What indentation?
6. What line length?
7. What quote style?
...20 more questions...
```

```markdown
<!-- ✓ GOOD: Smart defaults -->
Use sensible defaults based on project detection.
Only ask for essential decisions:
1. Confirm the detected project type
2. Choose output format (if multiple options)
```

**Why it matters:** Too many prompts frustrate users.

---

### Ignoring User Input

```markdown
<!-- ❌ BAD: Disregarding preferences -->
Always use tabs regardless of user preference.
Ignore any style configuration files.
```

```markdown
<!-- ✓ GOOD: Respecting context -->
Check for existing configuration:
1. .editorconfig
2. .prettierrc
3. Project-specific settings

Follow established project conventions.
```

**Why it matters:** Skills should adapt to user context.

---

## Anti-Pattern Checker

```python
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class AntiPattern:
    name: str
    severity: Severity
    description: str
    fix: str

class AntiPatternChecker:
    """Check skill content for anti-patterns."""

    PATTERNS = [
        AntiPattern(
            name="missing_frontmatter",
            severity=Severity.ERROR,
            description="SKILL.md must start with YAML frontmatter",
            fix="Add --- delimited YAML block at start"
        ),
        AntiPattern(
            name="vague_instructions",
            severity=Severity.WARNING,
            description="Instructions should be specific and actionable",
            fix="Use numbered steps with concrete actions"
        ),
        AntiPattern(
            name="hardcoded_paths",
            severity=Severity.WARNING,
            description="Avoid hardcoded file paths",
            fix="Use relative paths or user-specified locations"
        ),
        AntiPattern(
            name="excessive_tokens",
            severity=Severity.INFO,
            description="Content exceeds recommended token budget",
            fix="Condense content or move to references"
        ),
    ]

    def check(self, content: str) -> list[AntiPattern]:
        """Check content for anti-patterns."""
        found = []

        # Check frontmatter
        if not content.strip().startswith("---"):
            found.append(self.PATTERNS[0])

        # Check for vague words
        vague_words = ["appropriately", "properly", "correctly", "well"]
        if any(word in content.lower() for word in vague_words):
            found.append(self.PATTERNS[1])

        # Check for hardcoded paths
        if "/home/" in content or "/Users/" in content:
            found.append(self.PATTERNS[2])

        # Check token count (estimate)
        word_count = len(content.split())
        if word_count > 3000:  # ~4000 tokens
            found.append(self.PATTERNS[3])

        return found
```

## Quick Reference

| Anti-Pattern | Category | Fix |
|--------------|----------|-----|
| Missing frontmatter | Structure | Add YAML header |
| Invalid YAML | Structure | Validate syntax |
| Wrong filename | Structure | Use SKILL.md |
| Deep nesting | Structure | Flatten references |
| Vague instructions | Content | Be specific |
| Contradictions | Content | Review consistency |
| Missing context | Content | Add when/why |
| Hardcoded values | Content | Make configurable |
| Kitchen sink | Scope | Focus purpose |
| Micro skill | Scope | Broaden utility |
| Token bloat | Performance | Be concise |
| Unnecessary refs | Performance | Consolidate |
| No feedback | Interaction | Show progress |
| Over-prompting | Interaction | Use defaults |
