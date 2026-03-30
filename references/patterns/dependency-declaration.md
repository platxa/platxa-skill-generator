# Dependency Declaration

How to declare skill dependencies and suggestions in SKILL.md frontmatter.

## Fields

| Field | Purpose | Required | Effect |
|-------|---------|----------|--------|
| `depends-on` | Skills that must be installed | No | Warning at install time if missing |
| `suggests` | Skills that enhance but aren't required | No | Shown after install as recommendations |

## Syntax

```yaml
---
name: my-skill
description: A skill that needs logging and benefits from testing.
depends-on:
  - platxa-logging
  - platxa-error-handling
suggests:
  - platxa-testing
---
```

## Entry Format

Each entry must be a valid skill name:
- Hyphen-case only (`a-z`, `0-9`, `-`)
- 2-64 characters
- No consecutive hyphens (`--`)
- Must start with a letter, end with letter or number

## When to Use depends-on

Use when the skill **will not work correctly** without the dependency:

- Skill references another skill's output format
- Skill's scripts call another skill's scripts
- Skill's workflow assumes another skill's configuration exists

**Example**: A deployment skill that requires logging to be configured:
```yaml
depends-on:
  - platxa-logging  # Deployment scripts expect structured log format
```

## When to Use suggests

Use when the skill **works alone** but is **better with companions**:

- Skills that cover complementary concerns (logging + monitoring)
- Skills in the same domain (k8s-ops + k8s-scaling)
- Builder skills that produce code benefiting from other skills

**Example**: A sidecar builder that benefits from logging patterns:
```yaml
suggests:
  - platxa-logging         # Add structured logging to generated code
  - platxa-error-handling  # Add error patterns to generated code
  - platxa-testing         # Generate tests for the sidecar
```

## When NOT to Declare Dependencies

- Don't declare dependencies on skills that might not exist in the user's catalog
- Don't use `depends-on` for "nice to have" — use `suggests` instead
- Don't declare circular dependencies (A depends-on B, B depends-on A)
- Don't declare dependencies for unrelated skills

## Validation

Dependencies are validated at two levels:

1. **Frontmatter validation** (`validate-frontmatter.sh`): Checks entry format
2. **Install-time check** (`check-dependencies.sh`): Checks if deps are installed
3. **Cycle detection** (`detect-circular-deps.sh`): Checks for circular deps across all skills

## Tools

| Script | Purpose |
|--------|---------|
| `check-dependencies.sh <skill-dir>` | Check if a skill's deps are installed |
| `detect-circular-deps.sh [--dir <path>]` | Find cycles in dependency graph |
| `install-from-catalog.sh <name>` | Auto-installs catalog deps |
