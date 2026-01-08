# References Directory Planner

Plan references/ structure based on discovery findings and skill type.

## When to Include References

| Skill Type | References Needed | Reason |
|------------|-------------------|--------|
| Builder | Often | Domain specs, templates |
| Guide | Always | Learning materials, examples |
| Automation | Sometimes | Process documentation |
| Analyzer | Often | Criteria, standards |
| Validator | Always | Rules, specifications |

## Reference File Categories

### Domain Knowledge Files

```json
{
  "category": "domain",
  "files": [
    {
      "pattern": "{domain}-concepts.md",
      "purpose": "Core terminology and concepts",
      "when_needed": "Domain has significant vocabulary",
      "estimated_lines": 100
    },
    {
      "pattern": "{domain}-specification.md",
      "purpose": "Official spec summary",
      "when_needed": "Based on standard/spec",
      "estimated_lines": 150
    },
    {
      "pattern": "{domain}-examples.md",
      "purpose": "Real-world examples",
      "when_needed": "Complex or abstract domain",
      "estimated_lines": 80
    }
  ]
}
```

### Workflow Reference Files

```json
{
  "category": "workflow",
  "files": [
    {
      "pattern": "workflow-steps.md",
      "purpose": "Detailed step instructions",
      "when_needed": "Multi-step process",
      "estimated_lines": 120
    },
    {
      "pattern": "decision-points.md",
      "purpose": "Branching logic documentation",
      "when_needed": "Conditional workflows",
      "estimated_lines": 80
    },
    {
      "pattern": "error-handling.md",
      "purpose": "Error scenarios and recovery",
      "when_needed": "Complex failure modes",
      "estimated_lines": 60
    }
  ]
}
```

### Template Files

```json
{
  "category": "templates",
  "files": [
    {
      "pattern": "templates/{output-type}.md",
      "purpose": "Output templates",
      "when_needed": "Builder skills",
      "estimated_lines": 50
    },
    {
      "pattern": "templates/config.md",
      "purpose": "Configuration templates",
      "when_needed": "Configurable output",
      "estimated_lines": 40
    }
  ]
}
```

### Validation Reference Files

```json
{
  "category": "validation",
  "files": [
    {
      "pattern": "rules.md",
      "purpose": "Validation rules and criteria",
      "when_needed": "Validator skills",
      "estimated_lines": 100
    },
    {
      "pattern": "thresholds.md",
      "purpose": "Pass/fail thresholds",
      "when_needed": "Quantitative validation",
      "estimated_lines": 40
    }
  ]
}
```

## Planning Algorithm

```markdown
FUNCTION plan_references(skill_type, discovery):
    references = []

    # Analyze domain knowledge needs
    IF discovery.domain_knowledge.count > 5:
        references.append({
            name: "{domain}-concepts.md",
            content_outline: summarize(discovery.domain_knowledge)
        })

    # Check for specification basis
    IF discovery.has_official_spec:
        references.append({
            name: "{domain}-specification.md",
            content_outline: extract_spec_summary(discovery)
        })

    # Type-specific references
    SWITCH skill_type:
        CASE "Builder":
            references.extend(plan_builder_refs(discovery))
        CASE "Guide":
            references.extend(plan_guide_refs(discovery))
        CASE "Validator":
            references.extend(plan_validator_refs(discovery))

    # Complexity-based additions
    IF discovery.workflow_complexity > 0.7:
        references.append({
            name: "workflow-steps.md",
            content_outline: expand_workflow(discovery)
        })

    RETURN references
```

## Type-Specific Reference Plans

### Builder References

```json
{
  "skill_type": "Builder",
  "recommended_refs": [
    {"name": "output-format.md", "purpose": "Output structure spec"},
    {"name": "templates/", "purpose": "Output templates"},
    {"name": "customization.md", "purpose": "Configuration options"}
  ],
  "optional_refs": [
    {"name": "examples/", "purpose": "Example outputs"},
    {"name": "validation-rules.md", "purpose": "Output validation"}
  ]
}
```

### Guide References

```json
{
  "skill_type": "Guide",
  "recommended_refs": [
    {"name": "concepts.md", "purpose": "Core concepts explained"},
    {"name": "best-practices.md", "purpose": "Do's and don'ts"},
    {"name": "examples/", "purpose": "Learning examples"},
    {"name": "faq.md", "purpose": "Common questions"}
  ],
  "optional_refs": [
    {"name": "advanced.md", "purpose": "Advanced topics"},
    {"name": "troubleshooting.md", "purpose": "Common issues"}
  ]
}
```

### Automation References

```json
{
  "skill_type": "Automation",
  "recommended_refs": [
    {"name": "triggers.md", "purpose": "Trigger conditions"},
    {"name": "actions.md", "purpose": "Action specifications"}
  ],
  "optional_refs": [
    {"name": "rollback.md", "purpose": "Undo procedures"},
    {"name": "monitoring.md", "purpose": "Status checking"}
  ]
}
```

### Analyzer References

```json
{
  "skill_type": "Analyzer",
  "recommended_refs": [
    {"name": "metrics.md", "purpose": "What to measure"},
    {"name": "thresholds.md", "purpose": "Good/bad criteria"},
    {"name": "report-format.md", "purpose": "Output structure"}
  ],
  "optional_refs": [
    {"name": "benchmarks.md", "purpose": "Comparison baselines"}
  ]
}
```

### Validator References

```json
{
  "skill_type": "Validator",
  "recommended_refs": [
    {"name": "rules.md", "purpose": "Validation rules"},
    {"name": "severity-levels.md", "purpose": "Error vs warning"},
    {"name": "pass-criteria.md", "purpose": "Pass/fail definition"}
  ],
  "optional_refs": [
    {"name": "auto-fix.md", "purpose": "Automatic fixes"},
    {"name": "exceptions.md", "purpose": "Rule exceptions"}
  ]
}
```

## Content Outline Generation

### For Each Reference File

```json
{
  "reference_plan": {
    "name": "openapi-specification.md",
    "purpose": "OpenAPI 3.x specification summary",
    "content_outline": {
      "sections": [
        {"name": "Overview", "lines": 10, "notes": "What OpenAPI is"},
        {"name": "Structure", "lines": 30, "notes": "Top-level objects"},
        {"name": "Paths", "lines": 40, "notes": "Endpoint definitions"},
        {"name": "Components", "lines": 30, "notes": "Reusable schemas"},
        {"name": "Security", "lines": 20, "notes": "Auth schemes"}
      ],
      "total_lines": 130,
      "sources": ["swagger.io/specification", "openapi.tools"]
    }
  }
}
```

## Output Format

### References Plan

```json
{
  "references_plan": {
    "include_references_dir": true,
    "total_files": 5,
    "estimated_total_lines": 450,
    "files": [
      {
        "name": "openapi-concepts.md",
        "category": "domain",
        "purpose": "Core OpenAPI terminology",
        "estimated_lines": 100,
        "content_outline": {
          "sections": [
            {"name": "Terminology", "notes": "Key terms"},
            {"name": "Data Types", "notes": "Schema types"},
            {"name": "Operations", "notes": "HTTP operations"}
          ]
        },
        "sources": ["discovery.domain_knowledge"]
      },
      {
        "name": "templates/endpoint.md",
        "category": "template",
        "purpose": "Endpoint documentation template",
        "estimated_lines": 50,
        "content_outline": {
          "template_vars": ["method", "path", "description"],
          "format": "Markdown with placeholders"
        }
      }
    ],
    "subdirectories": [
      {"name": "templates/", "file_count": 2},
      {"name": "examples/", "file_count": 3}
    ]
  }
}
```

## Integration

### Discovery → Architecture

```markdown
Discovery provides:
- domain_knowledge[] → concepts.md content
- procedural_knowledge[] → workflow-steps.md content
- tools[] → dependencies.md content
- practices[] → best-practices.md content

Architecture plans:
- Which files to create
- Content outline for each
- Line budget per file
```

### Architecture → Generation

```markdown
Generation receives:
1. List of reference files to create
2. Content outline for each
3. Sources to draw from
4. Line budget constraints

Generation produces:
- Actual reference file content
- Proper formatting
- Cross-references between files
```
