# Token Budget Constraints

Guidelines for keeping skills efficient and fast-loading.

## Budget Overview

| Component | Limit | Rationale |
|-----------|-------|-----------|
| YAML Metadata | ~100 tokens | Loaded on every skill invocation |
| SKILL.md body | <500 lines | Primary context injection |
| Total SKILL.md | <5,000 tokens | Keep context window lean |
| Single reference | <2,000 tokens | Loaded on demand |
| All references | <10,000 tokens | Total skill footprint |

## Why Token Budgets Matter

1. **Context Window Limits**: Claude has finite context; wasteful skills crowd out user content
2. **Loading Speed**: Smaller skills load faster and feel more responsive
3. **Cost Efficiency**: Larger context = higher API costs per interaction
4. **Focus**: Concise skills stay focused on their purpose

## YAML Metadata (~100 tokens)

### Target

```yaml
---
name: example-skill        # ~3 tokens
description: Brief desc... # ~20 tokens
allowed-tools:             # ~15 tokens (5 tools)
  - Read
  - Write
  - Edit
  - Bash
  - Task
metadata:                  # ~30 tokens
  version: "1.0.0"
  author: "Name"
  tags: [tag1, tag2]
---
# Total: ~68 tokens (under budget)
```

### Over Budget (Avoid)

```yaml
---
name: my-extremely-verbose-skill-name-that-is-way-too-long
description: This is an extremely detailed and verbose description
  that goes on and on explaining every single detail about what
  this skill does, who it's for, why it was created, and many
  other unnecessary details that should really be in the Overview
  section instead of the metadata...
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - Task
  - AskUserQuestion
  - TodoWrite
  - LSP
metadata:
  version: "1.0.0"
  author: "A Very Long Author Name With Unnecessary Detail"
  tags: [tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8]
  created: "2026-01-01"
  updated: "2026-01-07"
  license: "MIT"
  repository: "https://github.com/example/skill"
---
# Total: ~200+ tokens (OVER BUDGET)
```

## SKILL.md Body (<500 lines)

### Line Budget Allocation

| Section | Lines | Purpose |
|---------|-------|---------|
| Overview | 20-40 | What and why |
| Workflow | 50-100 | Step-by-step process |
| Examples | 50-100 | Usage demonstrations |
| Output Checklist | 20-30 | Verification items |
| Other sections | 50-100 | Type-specific content |
| **Total** | **~200-370** | Room for growth |

### Efficiency Tips

1. **Use bullet points** over paragraphs
2. **Tables** for structured data
3. **Code blocks** only for essential examples
4. **Link to references** instead of inline content
5. **Remove fluff** - no "In this section we will..."

### Good Example (Efficient)

```markdown
## Overview

Generates API documentation from OpenAPI specs.

**Creates:**
- Markdown docs
- HTML pages
- PDF exports

**For:** Backend developers with OpenAPI 3.0+ specs.
```

### Bad Example (Wasteful)

```markdown
## Overview

Welcome to this skill! In this comprehensive overview section, we
will discuss in great detail what this skill does, why it was
created, and how you might want to use it. The purpose of this
skill is to help you generate documentation for your APIs...

[Continues for 20 more lines saying the same thing]
```

## References (On-Demand Loading)

### Progressive Loading Strategy

```
1. Skill invoked
   └─ Load: SKILL.md (~3K tokens)

2. Discovery phase
   └─ Load: references/patterns/domain-discovery.md (~1K tokens)

3. Architecture phase
   └─ Load: references/patterns/skill-types.md (~1K tokens)

4. Generation phase
   └─ Load: references/templates/{type}-template.md (~1K tokens)

5. Validation phase
   └─ Load: references/patterns/quality-criteria.md (~1K tokens)
```

**Key**: Only load what's needed for current phase.

### Reference Size Guidelines

| Type | Max Size | Example |
|------|----------|---------|
| Agent prompt | 500 tokens | discovery-agent.md |
| Pattern doc | 1,000 tokens | domain-discovery.md |
| Template | 800 tokens | builder-template.md |
| Checklist | 300 tokens | quality-checklist.md |

## Measuring Token Usage

### Quick Estimates

```
1 token ≈ 4 characters (English)
1 token ≈ 0.75 words
100 words ≈ 130 tokens
1 line of code ≈ 10-15 tokens
```

### Validation Script Check

The `validate-skill.sh` script checks:
- SKILL.md line count (<500)
- Estimated total tokens
- Warns if approaching limits

## Red Flags (Token Waste)

- [ ] Description > 200 characters
- [ ] More than 8 allowed-tools
- [ ] More than 5 metadata tags
- [ ] Examples longer than 30 lines each
- [ ] Inline content that should be in references
- [ ] Duplicate information across sections
- [ ] Verbose explanations of obvious things

## Token Budget Allocator

### Budget Pool

```json
{
  "total_budget": {
    "skill_md": 500,
    "references": 10000,
    "scripts": 5000
  },
  "units": "lines for skill_md, tokens for others"
}
```

### Allocation Algorithm

```markdown
FUNCTION allocate_budget(discovery, architecture):
    budget = {
        skill_md: {total: 500, allocated: {}},
        references: {total: 10000, allocated: {}}
    }

    # Step 1: Allocate SKILL.md sections (< 500 lines)
    base_sections = {
        "frontmatter": 15,
        "overview": 25,
        "workflow": 80,
        "examples": 60,
        "output_checklist": 20
    }

    # Adjust based on skill type
    type_additions = get_type_sections(architecture.skill_type)
    FOR section in type_additions:
        base_sections[section.name] = section.default_lines

    # Verify total < 500
    total = sum(base_sections.values())
    IF total > 450:
        # Scale down proportionally, keeping minimums
        scale_factor = 450 / total
        FOR section in base_sections:
            base_sections[section] = max(
                MIN_LINES[section],
                floor(base_sections[section] * scale_factor)
            )

    budget.skill_md.allocated = base_sections

    # Step 2: Allocate reference budgets by importance
    references = architecture.references_plan.files

    # Score each reference by importance
    FOR ref in references:
        ref.importance = calculate_importance(ref, discovery)

    # Sort by importance (descending)
    references = sort_by(references, "importance", descending=true)

    # Allocate tokens proportionally
    remaining = budget.references.total
    FOR ref in references:
        allocation = min(
            ref.estimated_tokens,
            remaining * (ref.importance / sum_importance),
            MAX_SINGLE_REF  # 2000 tokens max per file
        )
        budget.references.allocated[ref.name] = allocation
        remaining -= allocation

    RETURN budget
```

### Importance Scoring

```markdown
FUNCTION calculate_importance(ref, discovery):
    score = 0

    # Category weights
    category_weights = {
        "domain": 3,      # Core concepts - high importance
        "workflow": 3,    # How-to - high importance
        "template": 2,    # Output patterns - medium
        "validation": 2,  # Quality rules - medium
        "examples": 1     # Nice-to-have - lower
    }
    score += category_weights.get(ref.category, 1)

    # Usage frequency boost
    IF ref.used_in_phases > 1:
        score += 1  # Used in multiple phases

    # Discovery support
    IF ref.addresses_gap:
        score += 2  # Fills a discovery gap

    # Complexity adjustment
    IF discovery.complexity > 0.7 AND ref.category == "workflow":
        score += 1  # Complex skills need detailed workflows

    RETURN score
```

### Budget Allocation Output

```json
{
  "budget_allocation": {
    "skill_md": {
      "total_lines": 500,
      "allocated_lines": 420,
      "remaining": 80,
      "sections": {
        "frontmatter": 15,
        "overview": 25,
        "workflow": 100,
        "templates": 80,
        "configuration": 40,
        "examples": 80,
        "output_checklist": 30,
        "troubleshooting": 50
      }
    },
    "references": {
      "total_tokens": 10000,
      "allocated_tokens": 8500,
      "remaining": 1500,
      "files": [
        {"name": "openapi-concepts.md", "tokens": 1500, "importance": 5},
        {"name": "workflow-steps.md", "tokens": 1200, "importance": 5},
        {"name": "templates/endpoint.md", "tokens": 800, "importance": 4},
        {"name": "validation-rules.md", "tokens": 1000, "importance": 4},
        {"name": "examples/basic.md", "tokens": 600, "importance": 2}
      ]
    }
  }
}
```

### Minimum Allocations

| Component | Minimum | Purpose |
|-----------|---------|---------|
| Overview | 15 lines | Must explain what/why |
| Workflow | 40 lines | Core instructions |
| Examples | 30 lines | At least one example |
| Checklist | 10 lines | Verification items |
| Domain ref | 500 tokens | Core concepts |
| Template ref | 300 tokens | Basic template |

### Overflow Handling

```markdown
IF allocated > budget:
    1. Identify lowest-importance items
    2. Move content to references (if in SKILL.md)
    3. Compress verbose sections
    4. Remove redundant information
    5. Split large refs into on-demand parts
```
