# WebFetch Integration for Documentation Crawling

Patterns for using WebFetch tool to retrieve official documentation.

## WebFetch Basics

### Tool Signature
```
WebFetch(
  url: "https://example.com/docs",
  prompt: "Extract key concepts and best practices"
)
```

### Key Constraints
- **Max fetch size**: 10MB
- **Text limit**: 100KB after HTML→Markdown conversion
- **Cache TTL**: 15 minutes
- **Redirects**: Follow, but new host requires new request

## URL Patterns for Official Docs

### Framework Documentation
| Framework | Documentation URL Pattern |
|-----------|---------------------------|
| React | `https://react.dev/reference/*` |
| Python | `https://docs.python.org/3/*` |
| Node.js | `https://nodejs.org/docs/*` |
| TypeScript | `https://www.typescriptlang.org/docs/*` |

### API Specifications
| Spec | URL Pattern |
|------|-------------|
| OpenAPI | `https://spec.openapis.org/oas/v3.1.0` |
| JSON Schema | `https://json-schema.org/specification` |
| GraphQL | `https://spec.graphql.org/` |

### Standards Bodies
| Org | URL Pattern |
|-----|-------------|
| W3C | `https://www.w3.org/TR/*` |
| IETF | `https://www.rfc-editor.org/rfc/*` |
| OWASP | `https://owasp.org/www-project-*` |

## Extraction Prompts

### For Concept Extraction
```
Extract from this documentation:
1. Key concepts and definitions
2. Core terminology
3. Main components/modules
Return as a list of {term: definition} pairs.
```

### For Best Practices
```
Extract from this documentation:
1. Recommended patterns
2. Best practices
3. Guidelines
Return as a list of actionable recommendations.
```

### For Workflow Extraction
```
Extract from this documentation:
1. Step-by-step processes
2. Common workflows
3. Typical usage patterns
Return as numbered steps.
```

### For API Reference
```
Extract from this documentation:
1. Available endpoints/functions
2. Parameters and their types
3. Return values
4. Example usage
Return as structured API reference.
```

## Crawling Strategy

### Single Page Fetch
```markdown
For focused topics:
WebFetch(
  url: "https://docs.example.com/getting-started",
  prompt: "Extract the main concepts and setup steps"
)
```

### Multi-Page Strategy
```markdown
For comprehensive coverage:
1. Fetch index/overview page first
2. Identify key sub-pages from links
3. Fetch each sub-page with specific prompts
4. Aggregate results

Page 1: Overview → Get structure
Page 2: Concepts → Get definitions
Page 3: API Reference → Get signatures
Page 4: Best Practices → Get guidelines
```

### Depth-Limited Crawl
```markdown
Limit to:
- Max 5 pages per domain
- Max 2 levels deep
- Focus on most relevant pages
```

## Content Processing

### Extraction Flow
```
URL → WebFetch → Markdown → Prompt Processing → Structured Output
```

### Quality Checks
```markdown
After extraction, verify:
- [ ] Content is from official source
- [ ] Information is current (check dates)
- [ ] Concepts are clearly defined
- [ ] No placeholder or lorem ipsum
```

### Structured Output
```json
{
  "source": {
    "url": "https://docs.example.com/guide",
    "fetched_at": "2026-01-07T14:30:00Z",
    "authority": "official"
  },
  "extracted": {
    "concepts": [
      {"term": "Component", "definition": "..."}
    ],
    "best_practices": [
      "Always validate input before processing"
    ],
    "code_examples": [
      {"description": "Basic usage", "code": "..."}
    ]
  }
}
```

## Error Handling

### Redirect Handling
```markdown
IF WebFetch returns redirect message:
  1. Extract redirect URL from response
  2. Make new WebFetch request to redirect URL
  3. Continue processing
```

### Content Too Large
```markdown
IF content exceeds 100KB:
  1. Results will be truncated
  2. Focus prompt on most important sections
  3. Consider fetching specific sub-pages instead
```

### Page Not Found
```markdown
IF 404 error:
  1. Try alternative URL patterns
  2. Search for new documentation location
  3. Flag as unavailable, use cached info if available
```

### Rate Limiting
```markdown
IF rate limited:
  1. Rely on 15-min cache
  2. Space out requests
  3. Prioritize most important pages
```

## Integration with Discovery

### In Discovery Prompt
```markdown
After WebSearch identifies relevant URLs:

1. Filter for official documentation URLs
2. For each official URL:
   WebFetch(url, prompt="Extract {specific_info}")
3. Aggregate extracted information
4. Cross-reference with search results
```

### Priority Order
```markdown
1. Official specification (highest priority)
2. Official documentation
3. Official tutorials
4. Community guides (lower priority)
```

## Caching Benefits

```markdown
WebFetch has 15-minute cache:
- Repeated fetches are fast
- Useful for iterative exploration
- Reduces rate limiting risk
- Share results across prompts
```
