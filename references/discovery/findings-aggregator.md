# Discovery Findings Aggregator

Aggregate and structure discovery phase outputs for architecture planning.

## DiscoveryFindings Schema

```python
from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime

@dataclass
class DiscoveryFindings:
    """Structured output from discovery phase."""

    # Core identification
    skill_name: str
    skill_type: Literal["builder", "guide", "automation", "analyzer", "validator"]
    description: str

    # Domain analysis
    domain: DomainAnalysis
    requirements: list[Requirement]
    constraints: list[Constraint]

    # Technical specifications
    tools_needed: list[str]
    model_recommendation: Literal["opus", "sonnet", "haiku"]
    complexity_estimate: Literal["simple", "moderate", "complex"]

    # Content planning
    reference_topics: list[str]
    script_needs: list[str]

    # Metadata
    discovered_at: datetime
    confidence_score: float  # 0.0 - 1.0
    clarifications_needed: list[Clarification]

@dataclass
class DomainAnalysis:
    """Analysis of the skill's domain."""
    primary_domain: str
    subdomains: list[str]
    expertise_level: Literal["beginner", "intermediate", "advanced", "expert"]
    related_skills: list[str]

@dataclass
class Requirement:
    """A functional requirement for the skill."""
    id: str
    description: str
    priority: Literal["must", "should", "could"]
    source: Literal["explicit", "inferred"]

@dataclass
class Constraint:
    """A constraint on the skill's implementation."""
    type: Literal["token", "tool", "security", "performance", "compatibility"]
    description: str
    hard: bool  # True = must satisfy, False = preference

@dataclass
class Clarification:
    """A question needing user clarification."""
    id: str
    question: str
    options: list[str] | None
    default: str | None
    blocking: bool  # True = cannot proceed without answer
```

## JSON Output Format

```json
{
  "skill_name": "api-doc-generator",
  "skill_type": "builder",
  "description": "Generate comprehensive API documentation from OpenAPI specifications",

  "domain": {
    "primary_domain": "API Documentation",
    "subdomains": ["OpenAPI", "Markdown", "Technical Writing"],
    "expertise_level": "intermediate",
    "related_skills": ["openapi-validator", "markdown-formatter"]
  },

  "requirements": [
    {
      "id": "REQ-001",
      "description": "Parse OpenAPI 3.x specification files",
      "priority": "must",
      "source": "explicit"
    },
    {
      "id": "REQ-002",
      "description": "Generate Markdown documentation for each endpoint",
      "priority": "must",
      "source": "explicit"
    },
    {
      "id": "REQ-003",
      "description": "Include request/response examples",
      "priority": "should",
      "source": "inferred"
    },
    {
      "id": "REQ-004",
      "description": "Support custom templates",
      "priority": "could",
      "source": "inferred"
    }
  ],

  "constraints": [
    {
      "type": "token",
      "description": "SKILL.md under 5000 tokens",
      "hard": true
    },
    {
      "type": "tool",
      "description": "Requires Read, Write, Glob tools",
      "hard": true
    },
    {
      "type": "compatibility",
      "description": "Should work with OpenAPI 2.x (Swagger)",
      "hard": false
    }
  ],

  "tools_needed": ["Read", "Write", "Glob", "Grep"],
  "model_recommendation": "sonnet",
  "complexity_estimate": "moderate",

  "reference_topics": [
    "OpenAPI specification structure",
    "Markdown documentation best practices",
    "Endpoint documentation templates"
  ],

  "script_needs": [
    "validate-openapi.sh - Validate input spec",
    "generate-docs.sh - Main generation script"
  ],

  "discovered_at": "2024-01-15T10:30:00Z",
  "confidence_score": 0.85,

  "clarifications_needed": [
    {
      "id": "CLR-001",
      "question": "Should the generated docs include authentication details?",
      "options": ["Yes, include auth sections", "No, skip auth", "Only if present in spec"],
      "default": "Only if present in spec",
      "blocking": false
    }
  ]
}
```

## Aggregation Process

### Input Sources

```python
def aggregate_discovery_findings(
    user_description: str,
    clarification_responses: dict[str, str],
    context: DiscoveryContext
) -> DiscoveryFindings:
    """Aggregate all discovery inputs into structured findings."""

    # 1. Parse user description
    parsed = parse_skill_description(user_description)

    # 2. Classify skill type
    skill_type = classify_skill_type(parsed)

    # 3. Analyze domain
    domain = analyze_domain(parsed, skill_type)

    # 4. Extract requirements
    requirements = extract_requirements(parsed, clarification_responses)

    # 5. Identify constraints
    constraints = identify_constraints(parsed, skill_type)

    # 6. Determine tool needs
    tools = determine_tools_needed(requirements, skill_type)

    # 7. Recommend model
    model = recommend_model(domain.expertise_level, len(requirements))

    # 8. Estimate complexity
    complexity = estimate_complexity(requirements, constraints)

    # 9. Plan references
    reference_topics = plan_reference_topics(domain, requirements)

    # 10. Plan scripts
    script_needs = plan_scripts(skill_type, requirements)

    # 11. Calculate confidence
    confidence = calculate_confidence(
        parsed,
        clarification_responses,
        requirements
    )

    # 12. Identify remaining clarifications
    clarifications = identify_clarifications(parsed, requirements)

    return DiscoveryFindings(
        skill_name=parsed.skill_name,
        skill_type=skill_type,
        description=parsed.description,
        domain=domain,
        requirements=requirements,
        constraints=constraints,
        tools_needed=tools,
        model_recommendation=model,
        complexity_estimate=complexity,
        reference_topics=reference_topics,
        script_needs=script_needs,
        discovered_at=datetime.now(),
        confidence_score=confidence,
        clarifications_needed=clarifications
    )
```

### Skill Type Classification

```python
SKILL_TYPE_INDICATORS = {
    "builder": [
        "generate", "create", "build", "scaffold",
        "produce", "construct", "make", "output"
    ],
    "guide": [
        "guide", "tutorial", "how-to", "explain",
        "teach", "document", "reference", "learn"
    ],
    "automation": [
        "automate", "workflow", "pipeline", "batch",
        "schedule", "trigger", "process", "run"
    ],
    "analyzer": [
        "analyze", "inspect", "review", "check",
        "audit", "scan", "examine", "evaluate"
    ],
    "validator": [
        "validate", "verify", "lint", "test",
        "assert", "confirm", "ensure", "comply"
    ]
}

def classify_skill_type(parsed: ParsedDescription) -> str:
    """Classify skill type from description keywords."""
    scores = {t: 0 for t in SKILL_TYPE_INDICATORS}

    description_lower = parsed.description.lower()

    for skill_type, keywords in SKILL_TYPE_INDICATORS.items():
        for keyword in keywords:
            if keyword in description_lower:
                scores[skill_type] += 1

    # Return highest scoring type, default to "guide"
    best_type = max(scores, key=scores.get)
    return best_type if scores[best_type] > 0 else "guide"
```

### Requirements Extraction

```python
def extract_requirements(
    parsed: ParsedDescription,
    responses: dict[str, str]
) -> list[Requirement]:
    """Extract functional requirements from description and responses."""
    requirements = []
    req_id = 1

    # Explicit requirements from description
    for statement in parsed.requirement_statements:
        requirements.append(Requirement(
            id=f"REQ-{req_id:03d}",
            description=statement,
            priority="must",
            source="explicit"
        ))
        req_id += 1

    # Requirements from clarification responses
    for question_id, response in responses.items():
        if infers_requirement(response):
            requirements.append(Requirement(
                id=f"REQ-{req_id:03d}",
                description=requirement_from_response(response),
                priority="should",
                source="explicit"
            ))
            req_id += 1

    # Inferred requirements based on skill type
    inferred = infer_requirements(parsed.skill_type)
    for desc in inferred:
        requirements.append(Requirement(
            id=f"REQ-{req_id:03d}",
            description=desc,
            priority="should",
            source="inferred"
        ))
        req_id += 1

    return requirements
```

### Tool Determination

```python
SKILL_TYPE_TOOLS = {
    "builder": ["Read", "Write", "Glob"],
    "guide": ["Read", "Glob", "Grep"],
    "automation": ["Read", "Write", "Bash", "Glob"],
    "analyzer": ["Read", "Glob", "Grep", "Bash"],
    "validator": ["Read", "Glob", "Grep", "Bash"]
}

REQUIREMENT_TOOL_MAPPING = {
    "file": ["Read", "Write"],
    "search": ["Grep", "Glob"],
    "execute": ["Bash"],
    "web": ["WebFetch", "WebSearch"],
    "user": ["AskUserQuestion"],
    "task": ["Task", "TodoWrite"]
}

def determine_tools_needed(
    requirements: list[Requirement],
    skill_type: str
) -> list[str]:
    """Determine required tools from requirements."""
    tools = set(SKILL_TYPE_TOOLS.get(skill_type, []))

    for req in requirements:
        req_lower = req.description.lower()
        for keyword, tool_list in REQUIREMENT_TOOL_MAPPING.items():
            if keyword in req_lower:
                tools.update(tool_list)

    return sorted(tools)
```

## Confidence Scoring

```python
def calculate_confidence(
    parsed: ParsedDescription,
    responses: dict[str, str],
    requirements: list[Requirement]
) -> float:
    """Calculate confidence score for discovery findings."""
    score = 1.0

    # Reduce for ambiguous description
    if len(parsed.description) < 50:
        score -= 0.2  # Too short
    if "?" in parsed.description:
        score -= 0.1  # Contains questions

    # Reduce for unresolved clarifications
    blocking_unresolved = sum(
        1 for q in parsed.pending_questions
        if q.blocking and q.id not in responses
    )
    score -= blocking_unresolved * 0.15

    # Reduce for many inferred requirements
    inferred_ratio = sum(1 for r in requirements if r.source == "inferred") / max(len(requirements), 1)
    if inferred_ratio > 0.5:
        score -= 0.15

    # Reduce for complex requirements
    if len(requirements) > 10:
        score -= 0.1

    return max(0.0, min(1.0, score))
```

## Validation

```python
def validate_findings(findings: DiscoveryFindings) -> list[str]:
    """Validate discovery findings before proceeding."""
    errors = []

    # Required fields
    if not findings.skill_name:
        errors.append("skill_name is required")
    if not findings.description:
        errors.append("description is required")
    if not findings.requirements:
        errors.append("At least one requirement needed")

    # Confidence threshold
    if findings.confidence_score < 0.5:
        errors.append(f"Confidence too low: {findings.confidence_score:.2f} < 0.5")

    # Blocking clarifications
    blocking = [c for c in findings.clarifications_needed if c.blocking]
    if blocking:
        errors.append(f"{len(blocking)} blocking clarification(s) unresolved")

    # Tool validation
    invalid_tools = [t for t in findings.tools_needed if t not in VALID_TOOLS]
    if invalid_tools:
        errors.append(f"Invalid tools: {invalid_tools}")

    return errors
```
