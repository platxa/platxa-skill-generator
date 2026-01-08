# Domain Expertise File Generator

Generate domain-expertise.md reference files with deep knowledge.

## Purpose

Create reference files containing real domain expertise, not generic content. These files provide on-demand context for Claude when executing skills.

## Generation Algorithm

```markdown
FUNCTION generate_domain_expertise(discovery, blueprint):
    content = []

    # Header
    content.append(f"# {discovery.domain} Domain Expertise")
    content.append("")
    content.append(f"Deep knowledge for {blueprint.skill_name}.")
    content.append("")

    # Terminology section
    IF discovery.terminology.count > 0:
        content.append("## Terminology")
        content.append("")
        content.append("| Term | Definition |")
        content.append("|------|------------|")
        FOR term in discovery.terminology:
            content.append(f"| {term.name} | {term.definition} |")
        content.append("")

    # Key Concepts section
    IF discovery.concepts.count > 0:
        content.append("## Key Concepts")
        content.append("")
        FOR concept in discovery.concepts:
            content.append(f"### {concept.name}")
            content.append("")
            content.append(concept.explanation)
            IF concept.example:
                content.append("")
                content.append("**Example:**")
                content.append(f"```\n{concept.example}\n```")
            content.append("")

    # Specifications section
    IF discovery.has_spec:
        content.append("## Specification Reference")
        content.append("")
        content.append(f"Based on: {discovery.spec_name} {discovery.spec_version}")
        content.append("")
        FOR rule in discovery.spec_rules:
            content.append(f"- **{rule.name}**: {rule.description}")
        content.append("")

    # Best Practices section
    IF discovery.best_practices.count > 0:
        content.append("## Best Practices")
        content.append("")
        FOR practice in discovery.best_practices:
            content.append(f"### {practice.name}")
            content.append(practice.description)
            IF practice.rationale:
                content.append(f"**Why:** {practice.rationale}")
            content.append("")

    # Anti-Patterns section
    IF discovery.anti_patterns.count > 0:
        content.append("## Anti-Patterns to Avoid")
        content.append("")
        FOR anti in discovery.anti_patterns:
            content.append(f"### ❌ {anti.name}")
            content.append(anti.description)
            content.append(f"**Instead:** {anti.alternative}")
            content.append("")

    # Common Patterns section
    IF discovery.patterns.count > 0:
        content.append("## Common Patterns")
        content.append("")
        FOR pattern in discovery.patterns:
            content.append(f"### {pattern.name}")
            content.append(f"**When:** {pattern.when_to_use}")
            content.append(f"**How:**")
            content.append(f"```\n{pattern.implementation}\n```")
            content.append("")

    RETURN "\n".join(content)
```

## Content Sources

### From Discovery Phase

| Discovery Output | Expertise Section |
|------------------|-------------------|
| `domain_knowledge.terms` | Terminology table |
| `domain_knowledge.concepts` | Key Concepts |
| `authoritative_sources` | Specification Reference |
| `best_practices` | Best Practices |
| `anti_patterns` | Anti-Patterns |
| `workflow_patterns` | Common Patterns |

### Quality Indicators

```markdown
# Good domain expertise file contains:
✓ Specific terminology with precise definitions
✓ Concepts explained with concrete examples
✓ Reference to actual specifications/standards
✓ Best practices with rationale
✓ Anti-patterns with alternatives
✓ Code examples that compile/run

# Bad domain expertise file contains:
✗ Generic descriptions ("data", "process", "handle")
✗ Vague definitions ("used for various purposes")
✗ Missing examples
✗ No specification references
✗ Placeholder text
```

## Example Output

```markdown
# OpenAPI Domain Expertise

Deep knowledge for api-doc-generator.

## Terminology

| Term | Definition |
|------|------------|
| operationId | Unique identifier for an API operation, used for code generation |
| $ref | JSON Reference pointer to reusable component in components section |
| discriminator | Property that determines which schema applies in polymorphism |
| securityScheme | Defines authentication method (apiKey, http, oauth2, openIdConnect) |

## Key Concepts

### Schema Composition

OpenAPI supports three composition keywords for complex types:

- **allOf**: Combines multiple schemas (all must validate)
- **oneOf**: Exactly one schema must validate
- **anyOf**: At least one schema must validate

**Example:**
```yaml
Pet:
  oneOf:
    - $ref: '#/components/schemas/Cat'
    - $ref: '#/components/schemas/Dog'
  discriminator:
    propertyName: petType
```

### Path Parameters

Path parameters are required and appear in the URL path:

**Example:**
```yaml
paths:
  /users/{userId}:
    get:
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
```

## Specification Reference

Based on: OpenAPI Specification 3.1.0

- **info.title**: Required, string, API title
- **info.version**: Required, string, API version (not OpenAPI version)
- **paths**: Required, object, available endpoints
- **components**: Optional, reusable schemas, responses, parameters

## Best Practices

### Use Components for Reuse

Define reusable schemas in `components/schemas` and reference with `$ref`.

**Why:** Reduces duplication, easier maintenance, consistent types.

### Include Examples

Add `example` or `examples` to schemas and responses.

**Why:** Improves documentation, enables mock servers, aids testing.

## Anti-Patterns to Avoid

### ❌ Inline Schemas Everywhere

Defining schemas inline in every operation instead of using components.

**Instead:** Extract to components and use $ref for schemas used more than once.

### ❌ Missing operationId

Operations without operationId make code generation inconsistent.

**Instead:** Always provide unique, descriptive operationId for each operation.
```

## Token Budget

- Target: 1000-1500 tokens
- Maximum: 2000 tokens
- Prioritize: Terminology > Concepts > Best Practices > Patterns

## Integration

### Generation Phase

1. Receive discovery findings
2. Filter to domain knowledge items
3. Generate sections based on available data
4. Validate content is specific (not generic)
5. Check token budget
6. Write to `references/domain-expertise.md`
