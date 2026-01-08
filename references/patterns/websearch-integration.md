# WebSearch Integration for Domain Research

Patterns for using WebSearch tool during discovery phase.

## Query Strategy

### Query Types

| Type | Purpose | Example |
|------|---------|---------|
| Standards | Official specifications | "{domain} specification standard" |
| Best Practices | Industry guidelines | "{domain} best practices 2026" |
| Tutorials | How-to guides | "{domain} tutorial guide" |
| Tools | Relevant tooling | "{domain} tools libraries" |
| Examples | Real implementations | "{domain} examples github" |

### Query Templates

```markdown
# For API/Protocol domains
"{protocol_name} specification"
"{protocol_name} best practices"
"{protocol_name} implementation guide"

# For Framework domains
"{framework} documentation"
"{framework} patterns conventions"
"{framework} project structure"

# For Process domains
"{process} workflow steps"
"{process} automation tools"
"{process} checklist template"
```

## Search Execution

### Parallel Searches

Launch multiple searches simultaneously:

```markdown
Search 1: "{domain} official documentation"
Search 2: "{domain} best practices guide"
Search 3: "{domain} common mistakes avoid"
```

### Sequential Refinement

Based on initial results, refine:

```markdown
Round 1: Broad search → "{domain} overview"
Round 2: Specific search → "{specific_concept} from Round 1"
Round 3: Deep dive → "{edge_case} handling"
```

## Domain-Specific Queries

### API Documentation Domain
```
"OpenAPI specification 3.1"
"API documentation best practices"
"swagger vs openapi differences"
"API documentation tools comparison"
```

### Code Generation Domain
```
"code generation patterns"
"template engine best practices"
"AST manipulation techniques"
"code scaffolding tools"
```

### Testing Domain
```
"test automation best practices"
"testing pyramid strategy"
"unit test naming conventions"
"test coverage metrics meaningful"
```

### Security Domain
```
"OWASP top 10 2025"
"security code review checklist"
"vulnerability scanning tools"
"secure coding guidelines {language}"
```

## Result Processing

### Filtering Results

```markdown
KEEP results that:
- Come from official documentation
- Are from recognized authorities
- Are recent (< 2 years old)
- Have technical depth

SKIP results that:
- Are marketing content
- Lack technical detail
- Are outdated (> 3 years)
- Are AI-generated summaries
```

### Extracting Information

From each result, extract:
1. **Key concepts** - Core terminology
2. **Best practices** - Recommended approaches
3. **Anti-patterns** - What to avoid
4. **Tools** - Relevant technologies
5. **Examples** - Code snippets or workflows

### Source Quality Rating

| Source Type | Quality | Trust Level |
|-------------|---------|-------------|
| Official docs | High | 100% |
| Standards body | High | 100% |
| Major tech blog | Medium | 80% |
| Tutorial site | Medium | 70% |
| Stack Overflow | Variable | 60% |
| Random blog | Low | 40% |

## Integration with Discovery Agent

### In Discovery Prompt

```markdown
Use WebSearch to find:
1. Official documentation for {domain}
2. Best practices from authoritative sources
3. Common patterns and anti-patterns
4. Tools and libraries used in {domain}

For each search:
- Use specific, targeted queries
- Prefer official sources
- Note the source URL and authority level
- Extract actionable information
```

### Result Aggregation

```json
{
  "searches_performed": [
    {
      "query": "OpenAPI best practices",
      "results_found": 10,
      "results_used": 3
    }
  ],
  "sources": [
    {
      "url": "https://swagger.io/docs/",
      "authority": "high",
      "concepts_extracted": ["paths", "schemas", "components"]
    }
  ],
  "coverage": {
    "concepts": true,
    "best_practices": true,
    "tools": true,
    "examples": false
  }
}
```

## Error Handling

### No Results
```markdown
IF search returns no results:
  1. Simplify query (fewer terms)
  2. Try alternative terminology
  3. Broaden scope
  4. Flag as gap for user clarification
```

### Rate Limiting
```markdown
IF rate limited:
  1. Wait and retry
  2. Reduce query count
  3. Prioritize most important queries
```

### Irrelevant Results
```markdown
IF results are off-topic:
  1. Add qualifier terms
  2. Use domain filter if available
  3. Try exact phrase matching
```

## Allowed Domains

Prefer searches on trusted domains:

```
- Official: docs.*, *.io/docs, developer.*
- Standards: w3.org, ietf.org, iso.org
- Tech: github.com, stackoverflow.com
- Frameworks: react.dev, python.org, nodejs.org
```
