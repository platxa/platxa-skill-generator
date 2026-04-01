# Skill Composition Pattern

Skills can invoke other skills during execution, creating pipeline workflows.
This pattern documents when and how to use the Skill tool for composition.

## When to Compose

Use skill composition when:
- A workflow naturally chains two distinct capabilities (e.g., generate then review)
- The called skill already exists and is well-tested
- The calling skill benefits from the called skill's conventions/standards

Do NOT compose when:
- The logic is simple enough to inline (don't add a dependency for 5 lines of work)
- The called skill doesn't exist yet (use `suggests` instead for future companions)
- The composition creates a circular dependency

## Frontmatter Requirements

```yaml
allowed-tools:
  - Skill    # Required for invoking other skills
depends-on:  # If the skill BREAKS without the companion
  - required-skill
suggests:    # If the skill BENEFITS from the companion
  - optional-skill
```

## Composition Patterns

### Sequential Pipeline

One skill completes, then another runs on the output:

```markdown
## Workflow

### Step 1: Generate code
Create the implementation following the specification.

### Step 2: Simplify
Invoke the `/simplify` skill to clean up the generated code.

### Step 3: Review
Invoke the `/code-review` skill to audit the result.
```

Real-world example: `/batch` workers auto-invoke `/simplify` before committing.

### Conditional Composition

Invoke companion skills only when specific conditions are met:

```markdown
### Step 4: Post-Processing

If the generated code includes API endpoints:
  Invoke `/security-review` to check for vulnerabilities.

If the generated code includes database queries:
  Invoke `/code-review focus on efficiency` to check for N+1 patterns.
```

### Delegation

Hand off a subtask entirely to a specialized skill:

```markdown
### Step 3: Generate Tests

Invoke `/test-generator` with the implementation files as context.
The test generator will create appropriate test cases.
```

## Architecture Agent Integration

When the architecture agent detects composition opportunities:

```json
{
  "suggests": ["simplify", "code-review"],
  "allowed_tools": ["Read", "Write", "Edit", "Skill"],
  "composition_notes": "Invoke /simplify after code generation for cleanup"
}
```

## Relationship to depends-on and suggests

| Relationship | Meaning | Install behavior |
|-------------|---------|-----------------|
| `depends-on` | Breaks without it | Auto-installed, blocks if missing |
| `suggests` | Benefits from it | Shown as recommendation |
| Skill tool call | Invokes at runtime | Fails gracefully if not installed |

A skill can `suggests` a companion and also invoke it via Skill tool — the invocation
should handle the case where the companion isn't installed (skip gracefully, don't crash).
