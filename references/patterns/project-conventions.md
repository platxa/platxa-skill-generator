# Project Conventions Integration

Generated skills should adapt to project-specific conventions defined in CLAUDE.md.
This pattern applies to any skill that evaluates code quality, generates code,
or makes recommendations.

## When to Apply

- Any Analyzer or Validator skill (must respect project standards)
- Any Builder skill that generates code (must follow project patterns)
- Any Automation skill that modifies files (must maintain consistency)
- NOT for Guide skills (they teach general concepts, not project-specific ones)

## CLAUDE.md Hierarchy

Claude Code loads CLAUDE.md files from multiple locations. Generated skills should
reference them in this priority order (highest to lowest):

1. `./CLAUDE.md` — Project root (checked into git, team-shared)
2. `../CLAUDE.md` — Parent directory (monorepo root)
3. `~/.claude/CLAUDE.md` — User global (personal preferences)
4. Child directory CLAUDE.md files — Loaded on demand when working in subdirectories

Skills don't need to read these files manually — Claude Code loads them automatically.
The skill should reference their conventions in its analysis/generation workflow.

## Workflow Addition

Add this as the FIRST step in the skill's workflow (before any analysis or generation):

```markdown
### Step 0: Read Project Conventions

Check the project's CLAUDE.md files (loaded automatically by Claude Code):

Extract and note:
- **Coding standards**: Style preferences, naming conventions, patterns
- **Prohibited patterns**: Things the project explicitly bans
- **Required patterns**: Mandatory conventions (test frameworks, linters, etc.)
- **Tech stack**: Frameworks, languages, libraries in use
- **Testing requirements**: What must be tested and how

These conventions override the skill's default rules:
- If CLAUDE.md says "use tabs", don't flag tab indentation
- If CLAUDE.md says "no mocks in tests", don't suggest mocking
- If CLAUDE.md says "always use TypeScript strict mode", elevate any usage
```

## Finding Adjustment Rules

### Suppress Findings That Contradict CLAUDE.md

When the skill finds something that the project's CLAUDE.md explicitly permits or
requires, suppress the finding:

```
CLAUDE.md says: "Use snake_case for Python, camelCase for TypeScript"
Finding: "Inconsistent naming: snake_case in Python files"
Action: SUPPRESS — project convention explicitly allows this
```

### Elevate Findings That Violate CLAUDE.md

When the skill finds something that violates the project's CLAUDE.md rules,
elevate severity:

```
CLAUDE.md says: "Never use any types in TypeScript"
Finding: "Medium: 3 uses of 'any' type in handler.ts"
Action: ELEVATE to HIGH — violates explicit project rule
```

### Default When No CLAUDE.md Exists

When no CLAUDE.md is found, use the skill's built-in defaults without adjustment.
Do not warn about missing CLAUDE.md — many projects don't have one.

## Code Generation Integration

For Builder skills that generate code:

```markdown
Before generating code, check CLAUDE.md for:
- Import style (ES modules vs CommonJS, absolute vs relative)
- Formatting preferences (semicolons, quotes, indentation)
- Framework choices (React vs Vue, pytest vs unittest)
- Naming patterns (file naming, component naming)
- Required boilerplate (license headers, type annotations)

Generated code MUST follow these conventions. If CLAUDE.md specifies
a pattern, use it. If silent on a topic, use language defaults.
```

## Architecture Agent Integration

When `execution_sophistication` is intermediate or advanced, the architecture
blueprint should include:

```json
{
  "execution_sophistication": {
    "claude_md_integration": true,
    "rationale": "Skill evaluates/generates code and should respect project conventions"
  }
}
```

The generation agent includes the Step 0 convention-reading workflow when this flag
is true. For simple skills or Guide-type skills, this is typically false.
