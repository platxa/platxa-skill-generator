# Automatic Domain Research (Phase 1)

Autonomous research process that gathers domain knowledge without user intervention.

## Research Pipeline

```
User Input → Query Generation → Parallel Research → Result Aggregation → Sufficiency Check
     │              │                  │                    │                   │
     │              │                  ├── WebSearch        │                   │
     │              │                  ├── WebFetch         │                   │
     │              │                  └── Skill Analysis   │                   │
     ▼              ▼                  ▼                    ▼                   ▼
description   search queries     raw findings       structured         ready or
target_users                                        knowledge          need more
```

## Step 1: Query Generation

### From User Input

```markdown
Input: "A skill that generates API documentation from OpenAPI specs"

Generated Queries:
1. "OpenAPI documentation best practices"
2. "OpenAPI 3.0 specification guide"
3. "API documentation tools comparison"
4. "swagger documentation generator"
5. "OpenAPI examples templates"
```

### Query Categories

| Category | Query Template | Purpose |
|----------|----------------|---------|
| Standards | "{domain} specification official" | Get authoritative source |
| Practices | "{domain} best practices guide" | Learn conventions |
| Tools | "{domain} tools libraries" | Identify technologies |
| Examples | "{domain} examples github" | Find implementations |
| Pitfalls | "{domain} common mistakes" | Learn what to avoid |

## Step 2: Parallel Research

### Launch Concurrent Searches

```markdown
# Execute in parallel (single message, multiple tool calls)

Task 1: WebSearch
  query: "{domain} specification documentation"

Task 2: WebSearch
  query: "{domain} best practices"

Task 3: Skill Analysis
  Glob("~/.claude/skills/*/SKILL.md")
  Find similar skills

Task 4: WebSearch
  query: "{domain} tools automation"
```

### Fetch Official Documentation

```markdown
# Based on search results, fetch official docs

WebFetch(url: "https://official-docs.example.com",
         prompt: "Extract key concepts and workflows")

WebFetch(url: "https://standards.org/spec",
         prompt: "Extract specification requirements")
```

## Step 3: Knowledge Extraction

### From Search Results

```markdown
For each search result:
  1. Identify source authority (official/community/blog)
  2. Extract key points
  3. Note terminology used
  4. Identify linked resources

Output:
  - concepts: [{term, definition}]
  - practices: [{practice, rationale}]
  - sources: [{url, authority, relevance}]
```

### From Documentation

```markdown
For each fetched document:
  1. Extract section structure
  2. Identify core concepts
  3. Note code examples
  4. Find configuration options

Output:
  - structure: [section_names]
  - concepts: [definitions]
  - examples: [code_snippets]
  - config: [options]
```

### From Existing Skills

```markdown
For each similar skill:
  1. Note directory structure
  2. Extract section patterns
  3. Identify tool usage
  4. Learn from examples

Output:
  - patterns: [structural_patterns]
  - tools_used: [tool_list]
  - effective_sections: [section_list]
```

## Step 4: Result Aggregation

### Merge Findings

```json
{
  "domain": {
    "name": "OpenAPI Documentation",
    "aliases": ["Swagger", "OAS"],
    "version": "3.1.0"
  },
  "concepts": [
    {"term": "Path", "definition": "URL endpoint definition"},
    {"term": "Schema", "definition": "Data structure definition"},
    {"term": "Component", "definition": "Reusable definition"}
  ],
  "best_practices": [
    {"practice": "Include examples for all endpoints", "source": "official"},
    {"practice": "Document error responses", "source": "community"},
    {"practice": "Use semantic versioning", "source": "official"}
  ],
  "workflows": [
    {
      "name": "Generate docs from spec",
      "steps": ["Parse spec", "Extract endpoints", "Format output"]
    }
  ],
  "tools": {
    "required": ["Read", "Write"],
    "recommended": ["WebFetch", "Bash"],
    "external": ["swagger-cli", "redoc"]
  },
  "sources": [
    {"url": "https://spec.openapis.org", "authority": "official"},
    {"url": "https://swagger.io/docs", "authority": "official"}
  ]
}
```

### Deduplicate and Rank

```markdown
1. Remove duplicate concepts (same meaning, different wording)
2. Rank by source authority
3. Prioritize official over community
4. Keep top N items per category
```

## Step 5: Sufficiency Check

### Scoring Criteria

| Criterion | Weight | Score If Met |
|-----------|--------|--------------|
| Has official source | 20% | 1.0 |
| ≥5 concepts defined | 15% | 1.0 |
| ≥3 best practices | 15% | 1.0 |
| Primary workflow clear | 20% | 1.0 |
| Tools identified | 10% | 1.0 |
| Examples found | 10% | 1.0 |
| No critical gaps | 10% | 1.0 |

### Calculate Score

```markdown
sufficiency_score = weighted_sum(criteria_met)

IF score >= 0.8:
    status = "sufficient"
    proceed_to = "architecture"
ELIF score >= 0.6:
    status = "partial"
    action = "proceed with warnings"
ELSE:
    status = "insufficient"
    action = "identify gaps, ask user"
```

### Gap Analysis

```markdown
IF score < 0.8:
    gaps = []

    IF no official source:
        gaps.append("Could not find official documentation")

    IF concepts < 5:
        gaps.append("Need more domain concepts")

    IF workflow unclear:
        gaps.append("Primary workflow not understood")

    return gaps for user clarification
```

## Output Format

```json
{
  "phase": "discovery",
  "status": "complete",
  "research": {
    "searches_performed": 5,
    "pages_fetched": 3,
    "skills_analyzed": 2
  },
  "findings": {
    "domain": "...",
    "concepts": [...],
    "best_practices": [...],
    "workflows": [...],
    "tools": {...}
  },
  "sufficiency": {
    "score": 0.85,
    "status": "sufficient",
    "gaps": []
  },
  "next_phase": "architecture"
}
```

## Autonomy Principles

1. **No unnecessary questions**: Research first, ask only if stuck
2. **Parallel execution**: Maximize concurrent searches
3. **Smart prioritization**: Official sources before blogs
4. **Progressive refinement**: Broad search → specific fetch
5. **Clear handoff**: Structured output for next phase
