# Domain Expertise Embedding

Embed domain-specific knowledge into generated skills.

## Purpose

Skills must contain real domain expertise, not generic content:
- Specific terminology and concepts
- Authoritative best practices
- Real-world patterns and anti-patterns
- Domain-specific validation rules

## Generic vs Domain-Specific

### Generic (Avoid)

```markdown
## Workflow

### Step 1: Read Input
Read the input file.

### Step 2: Process
Process the content.

### Step 3: Output
Write the output.
```

### Domain-Specific (Target)

```markdown
## Workflow

### Step 1: Parse OpenAPI Specification
Read and validate the OpenAPI 3.x specification file. Check for:
- Valid JSON/YAML syntax
- Required `openapi` version field (3.0.0+)
- `info` object with title and version
- At least one path in `paths`

### Step 2: Extract API Endpoints
For each path in the specification:
- Parse HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Extract operationId for unique identification
- Collect parameters (path, query, header, cookie)
- Identify request body schemas via $ref or inline

### Step 3: Generate Documentation
Transform extracted data into documentation:
- Group endpoints by tags or path prefixes
- Include request/response examples from spec
- Document authentication requirements from securitySchemes
```

## Expertise Sources

### From Discovery Phase

| Source | Expertise Type |
|--------|---------------|
| Official docs | Authoritative specifications |
| WebSearch | Current best practices |
| Existing skills | Proven patterns |
| Domain analysis | Terminology and concepts |

### Expertise Categories

```json
{
  "domain_expertise": {
    "terminology": [
      {"term": "operationId", "definition": "Unique identifier for an API operation"},
      {"term": "$ref", "definition": "JSON Reference pointer to reusable component"}
    ],
    "concepts": [
      {"name": "Schema composition", "explanation": "Using allOf, oneOf, anyOf for complex types"},
      {"name": "Security schemes", "explanation": "API authentication methods: apiKey, http, oauth2, openIdConnect"}
    ],
    "best_practices": [
      "Always validate spec before processing",
      "Use operationId for consistent naming",
      "Preserve parameter order from spec"
    ],
    "anti_patterns": [
      "Don't assume all endpoints have operationId",
      "Don't hardcode API versions",
      "Don't ignore deprecated endpoints without warning"
    ]
  }
}
```

## Embedding Algorithm

```markdown
FUNCTION embed_domain_expertise(section, discovery):
    # Get domain knowledge relevant to this section
    relevant = filter_by_section(discovery.domain_knowledge, section)

    # Embed terminology
    FOR term in relevant.terminology:
        IF term.appears_in(section.content):
            section.add_context(term.definition)

    # Add specific guidance
    IF section.type == "workflow":
        embed_workflow_expertise(section, relevant)
    ELIF section.type == "examples":
        embed_example_expertise(section, relevant)
    ELIF section.type == "validation":
        embed_validation_expertise(section, relevant)

    RETURN section
```

## Section-Specific Embedding

### Workflow Sections

```markdown
FUNCTION embed_workflow_expertise(workflow, expertise):
    FOR step in workflow.steps:
        # Add specific checks
        step.add_validation_items(expertise.checks_for(step.action))

        # Add domain-specific notes
        IF expertise.has_gotchas(step.action):
            step.add_note(expertise.gotchas)

        # Reference specific tools/formats
        step.use_specific_terminology(expertise.terminology)

    RETURN workflow
```

### Example Sections

```markdown
FUNCTION embed_example_expertise(examples, expertise):
    FOR example in examples:
        # Use realistic domain values
        example.user_input = make_domain_specific(
            example.user_input,
            expertise.realistic_values
        )

        # Show domain-specific behavior
        example.assistant_response = include_domain_details(
            example.assistant_response,
            expertise.expected_behaviors
        )

    RETURN examples
```

## Quality Indicators

### Domain-Specific Markers

| Indicator | Weight | Example |
|-----------|--------|---------|
| Domain terminology | High | "operationId", "schema", "$ref" |
| Specific formats | High | "OpenAPI 3.1", "JSON Schema draft-07" |
| Concrete values | Medium | "paths", "components", "securitySchemes" |
| Domain tools | Medium | "swagger-cli", "openapi-generator" |
| Best practices | High | "Validate before processing" |

### Generic Markers (Red Flags)

| Indicator | Example |
|-----------|---------|
| Vague verbs | "process", "handle", "do" |
| Generic nouns | "input", "output", "data" |
| No specifics | "as needed", "if applicable" |
| Placeholder text | "Add your content here" |

## Validation

```markdown
FUNCTION validate_expertise(skill_content, discovery):
    score = 0
    max_score = 10

    # Check terminology usage
    terms_used = count_terminology_usage(skill_content, discovery.terminology)
    IF terms_used >= 5:
        score += 3
    ELIF terms_used >= 2:
        score += 1

    # Check specific formats/versions
    IF has_specific_versions(skill_content):
        score += 2

    # Check best practices mentioned
    practices = count_best_practices(skill_content, discovery.best_practices)
    IF practices >= 3:
        score += 2
    ELIF practices >= 1:
        score += 1

    # Check for generic markers (penalty)
    generic_count = count_generic_markers(skill_content)
    score -= min(generic_count, 3)

    # Check examples are domain-specific
    IF examples_are_realistic(skill_content):
        score += 3

    RETURN score / max_score
```

## Integration

### Discovery → Generation

```markdown
Discovery provides:
- domain_knowledge.terminology[]
- domain_knowledge.concepts[]
- domain_knowledge.best_practices[]
- domain_knowledge.anti_patterns[]

Generation uses:
- Embed terms in workflow descriptions
- Add specific checks based on concepts
- Include best practices in guidance
- Warn about anti-patterns in notes
```

### Output Quality Check

Before completing generation:
1. Run expertise validation
2. Score must be ≥ 0.7 (70%)
3. If below threshold, enhance with more specifics
4. Log areas needing improvement
