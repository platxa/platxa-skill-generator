# Best Practices Reference Generator

Generate best-practices.md files with actionable practices and rationale.

## Purpose

Create reference files containing domain best practices:
- Actionable recommendations
- Clear rationale for each
- Anti-patterns to avoid
- Real examples

## Generation Algorithm

```markdown
FUNCTION generate_best_practices(discovery, blueprint):
    content = []

    # Header
    content.append(f"# {discovery.domain} Best Practices")
    content.append("")
    content.append(f"Guidelines for effective {discovery.domain} usage.")
    content.append("")

    # Quick Reference
    content.append("## Quick Reference")
    content.append("")
    content.append("| Do | Don't |")
    content.append("|----|----- |")
    FOR i in range(min(5, len(discovery.do_practices))):
        do = discovery.do_practices[i].short
        dont = discovery.dont_practices[i].short if i < len(discovery.dont_practices) else ""
        content.append(f"| {do} | {dont} |")
    content.append("")

    # Do section
    content.append("## Do")
    content.append("")
    FOR practice in discovery.do_practices:
        content.append(f"### ✓ {practice.name}")
        content.append("")
        content.append(practice.description)
        content.append("")
        content.append(f"**Why:** {practice.rationale}")
        content.append("")
        IF practice.example:
            content.append("**Example:**")
            content.append(f"```{practice.language}")
            content.append(practice.example)
            content.append("```")
            content.append("")

    # Don't section
    content.append("## Don't")
    content.append("")
    FOR anti in discovery.dont_practices:
        content.append(f"### ✗ {anti.name}")
        content.append("")
        content.append(anti.description)
        content.append("")
        content.append(f"**Why not:** {anti.rationale}")
        content.append("")
        IF anti.bad_example:
            content.append("**Bad:**")
            content.append(f"```{anti.language}")
            content.append(anti.bad_example)
            content.append("```")
            content.append("")
        IF anti.good_example:
            content.append("**Good:**")
            content.append(f"```{anti.language}")
            content.append(anti.good_example)
            content.append("```")
            content.append("")

    # Context-specific practices
    IF discovery.context_practices:
        content.append("## Context-Specific")
        content.append("")
        FOR ctx in discovery.context_practices:
            content.append(f"### When {ctx.condition}")
            content.append("")
            content.append(ctx.practice)
            content.append("")

    RETURN "\n".join(content)
```

## Practice Structure

```json
{
  "practice": {
    "name": "Use Components for Reuse",
    "short": "Use $ref for reuse",
    "description": "Define reusable schemas in components/schemas and reference them with $ref throughout your specification.",
    "rationale": "Reduces duplication, ensures consistency, makes maintenance easier.",
    "example": "components:\n  schemas:\n    User:\n      type: object\n      properties:\n        id: {type: string}",
    "language": "yaml",
    "category": "structure",
    "priority": "high"
  }
}
```

## Example Output

```markdown
# OpenAPI Best Practices

Guidelines for effective OpenAPI usage.

## Quick Reference

| Do | Don't |
|----|-------|
| Use $ref for reuse | Duplicate schemas |
| Include examples | Leave responses empty |
| Use operationId | Skip unique identifiers |
| Document errors | Only document success |
| Version your API | Use unversioned paths |

## Do

### ✓ Use Components for Reuse

Define reusable schemas in `components/schemas` and reference them with `$ref` throughout your specification.

**Why:** Reduces duplication, ensures consistency, makes maintenance easier.

**Example:**
```yaml
components:
  schemas:
    User:
      type: object
      required: [id, email]
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email

paths:
  /users/{id}:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

### ✓ Include Response Examples

Add `example` or `examples` to schemas and responses.

**Why:** Improves documentation, enables mock servers, helps consumers understand expected data.

**Example:**
```yaml
User:
  type: object
  properties:
    name:
      type: string
      example: "Jane Doe"
  example:
    id: "123"
    name: "Jane Doe"
```

## Don't

### ✗ Duplicate Schema Definitions

Copying the same schema definition across multiple operations.

**Why not:** Creates maintenance burden, leads to inconsistencies, increases file size.

**Bad:**
```yaml
paths:
  /users:
    get:
      responses:
        '200':
          schema:
            type: object
            properties:
              id: {type: string}
              name: {type: string}
  /users/{id}:
    get:
      responses:
        '200':
          schema:
            type: object
            properties:
              id: {type: string}
              name: {type: string}
```

**Good:**
```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id: {type: string}
        name: {type: string}
paths:
  /users:
    get:
      responses:
        '200':
          schema:
            type: array
            items:
              $ref: '#/components/schemas/User'
```

### ✗ Skip operationId

Operations without unique operationId identifiers.

**Why not:** Makes code generation inconsistent, harder to reference in documentation, breaks some tooling.

## Context-Specific

### When documenting internal APIs

- Include more implementation details
- Document internal error codes
- Reference internal services

### When documenting public APIs

- Focus on consumer perspective
- Hide implementation details
- Include rate limiting info
```

## Token Budget

- Target: 600-1000 tokens
- Maximum: 1500 tokens
- Prioritize: Quick Reference > Do > Don't > Context

## Integration

Reference from SKILL.md:
```markdown
For detailed guidelines, see [Best Practices](references/best-practices.md).
```
