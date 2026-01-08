# Procedural vs Domain Knowledge Classifier

Categorize research findings into actionable knowledge types.

## Knowledge Types

### Domain Knowledge (WHAT)

**Definition**: Facts, concepts, terminology, and structures of the domain.

**Characteristics**:
- Declarative (states facts)
- Static (doesn't change often)
- Referenceable (can be looked up)
- Universal (same across projects)

**Examples**:
- "OpenAPI uses JSON Schema for data types"
- "REST APIs use HTTP methods: GET, POST, PUT, DELETE"
- "Components are reusable schema definitions"

**Skill Usage**: Goes in `references/` for on-demand loading

---

### Procedural Knowledge (HOW)

**Definition**: Processes, workflows, steps, and sequences for accomplishing tasks.

**Characteristics**:
- Imperative (describes actions)
- Sequential (has order)
- Conditional (may have branches)
- Practical (applied during execution)

**Examples**:
- "First parse the spec, then extract endpoints, then format output"
- "If validation fails, show errors and prompt for fixes"
- "Always validate input before processing"

**Skill Usage**: Goes in `SKILL.md Workflow` section

## Classification Rules

### Indicators for Domain Knowledge

| Indicator | Example |
|-----------|---------|
| Defines a term | "A schema is a data structure definition" |
| States a fact | "OpenAPI 3.0 supports callbacks" |
| Describes structure | "Paths contain operations" |
| Lists options | "Supported formats: JSON, YAML" |
| Explains concept | "Polymorphism in OpenAPI uses discriminator" |

### Indicators for Procedural Knowledge

| Indicator | Example |
|-----------|---------|
| Uses action verbs | "Parse the specification file" |
| Has sequence words | "First... then... finally..." |
| Contains conditions | "If X, then Y" |
| Describes workflow | "The process involves three steps" |
| Gives instructions | "Run the validator to check" |

## Classification Algorithm

```markdown
FOR each finding:
    signals = {domain: 0, procedural: 0}

    # Check for domain indicators
    IF contains_definition(finding):
        signals.domain += 2
    IF states_fact(finding):
        signals.domain += 1
    IF describes_structure(finding):
        signals.domain += 1
    IF is_terminology(finding):
        signals.domain += 2

    # Check for procedural indicators
    IF contains_action_verb(finding):
        signals.procedural += 2
    IF has_sequence(finding):
        signals.procedural += 2
    IF has_condition(finding):
        signals.procedural += 1
    IF is_instruction(finding):
        signals.procedural += 2

    # Classify
    IF signals.domain > signals.procedural:
        category = "domain"
    ELIF signals.procedural > signals.domain:
        category = "procedural"
    ELSE:
        category = "mixed"

    RETURN category
```

## Pattern Recognition

### Domain Knowledge Patterns

```regex
# Definitions
"X is (a|an|the) ..."
"X refers to ..."
"X means ..."

# Facts
"X supports ..."
"X uses ..."
"X contains ..."

# Structure
"X consists of ..."
"X has (the following|these) ..."
"Types of X include ..."
```

### Procedural Knowledge Patterns

```regex
# Sequences
"(First|Then|Next|Finally) ..."
"Step N: ..."
"... followed by ..."

# Actions
"(Create|Generate|Parse|Validate|Check) ..."
"To X, you need to ..."
"Run ... to ..."

# Conditions
"If X, (then) ..."
"When X, ..."
"... otherwise ..."
```

## Output Structure

### Classified Findings

```json
{
  "knowledge": {
    "domain": [
      {
        "content": "OpenAPI uses JSON Schema for type definitions",
        "category": "domain",
        "confidence": 0.9,
        "tags": ["concept", "schema"]
      },
      {
        "content": "Paths define available endpoints",
        "category": "domain",
        "confidence": 0.85,
        "tags": ["structure", "paths"]
      }
    ],
    "procedural": [
      {
        "content": "First validate the spec, then extract endpoints",
        "category": "procedural",
        "confidence": 0.95,
        "tags": ["workflow", "validation"]
      }
    ],
    "mixed": [
      {
        "content": "Components should be reused across operations",
        "category": "mixed",
        "confidence": 0.6,
        "tags": ["best-practice", "components"]
      }
    ]
  }
}
```

## Skill Mapping

### Where Knowledge Goes

| Type | Skill Location | Format |
|------|----------------|--------|
| Domain | `references/*.md` | Reference documentation |
| Procedural | `SKILL.md Workflow` | Step-by-step sections |
| Mixed | Both locations | Split appropriately |

### Example Mapping

```markdown
Finding: "OpenAPI specs must be validated before processing"

Classification: Mixed
- Domain part: "OpenAPI specs have validation requirements"
  → references/openapi-concepts.md

- Procedural part: "Validate spec before processing"
  → SKILL.md Workflow Step 1
```

## Integration with Discovery

### In Discovery Output

```json
{
  "discovery": {
    "findings": {
      "total": 25,
      "domain": 12,
      "procedural": 10,
      "mixed": 3
    },
    "domain_knowledge": [...],
    "procedural_knowledge": [...],
    "mixed_knowledge": [...]
  }
}
```

### Used By Architecture Phase

- Domain count → Determines need for `references/`
- Procedural count → Determines workflow complexity
- Mixed items → Reviewed for proper placement
