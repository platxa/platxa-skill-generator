# SKILL.md Structure Planner

Plan SKILL.md sections based on skill type and discovery findings.

## Section Categories

### Required Sections (All Skills)

| Section | Purpose | Est. Lines |
|---------|---------|------------|
| Overview | What and why | 10-20 |
| Workflow | How to use | 30-80 |

### Recommended Sections

| Section | Purpose | Est. Lines |
|---------|---------|------------|
| Examples | Usage demos | 30-60 |
| Output Checklist | Verify completion | 10-20 |

### Type-Specific Sections

| Skill Type | Additional Sections |
|------------|---------------------|
| Builder | Templates, Configuration |
| Guide | Learning Path, Best Practices, FAQ |
| Automation | Triggers, Verification, Safety |
| Analyzer | Checklist, Metrics, Report Format |
| Validator | Rules, Thresholds, Pass/Fail Criteria |

## Planning Algorithm

```markdown
FUNCTION plan_sections(skill_type, discovery):
    sections = []

    # Required sections
    sections.append({
        name: "Overview",
        required: true,
        content_notes: generate_overview_notes(discovery)
    })

    sections.append({
        name: "Workflow",
        required: true,
        content_notes: generate_workflow_notes(discovery)
    })

    # Recommended sections
    sections.append({
        name: "Examples",
        required: false,
        content_notes: generate_example_notes(discovery)
    })

    # Type-specific sections
    type_sections = get_type_sections(skill_type)
    FOR section in type_sections:
        sections.append({
            name: section.name,
            required: section.required,
            content_notes: generate_type_notes(section, discovery)
        })

    # Output checklist (if Builder or Validator)
    IF skill_type in ["Builder", "Validator"]:
        sections.append({
            name: "Output Checklist",
            required: true,
            content_notes: generate_checklist_notes(discovery)
        })

    RETURN sections
```

## Section Content Notes

### Overview Notes Generation

```json
{
  "section": "Overview",
  "content_notes": {
    "opening": "One-line description: {skill_name} {verb}s {output}",
    "what_it_does": "List 3-5 capabilities from discovery.concepts",
    "who_its_for": "Target users from input.target_users",
    "key_features": "Top 3 differentiators",
    "line_budget": 15
  }
}
```

### Workflow Notes Generation

```json
{
  "section": "Workflow",
  "content_notes": {
    "structure": "Sequential steps with ### headers",
    "steps": [
      {"step": 1, "action": "Gather input", "from": "discovery.workflow[0]"},
      {"step": 2, "action": "Process", "from": "discovery.workflow[1]"},
      {"step": 3, "action": "Output", "from": "discovery.workflow[2]"}
    ],
    "include_code_blocks": true,
    "include_decision_points": true,
    "line_budget": 50
  }
}
```

### Examples Notes Generation

```json
{
  "section": "Examples",
  "content_notes": {
    "count": 2,
    "example_1": {
      "type": "Basic usage",
      "show": "Typical workflow",
      "format": "User/Assistant dialog"
    },
    "example_2": {
      "type": "Edge case",
      "show": "Error handling or special case",
      "format": "User/Assistant dialog"
    },
    "line_budget": 40
  }
}
```

## Type-Specific Plans

### Builder Sections

```json
{
  "skill_type": "Builder",
  "additional_sections": [
    {
      "name": "Templates",
      "required": true,
      "content_notes": {
        "list": "Available templates with purpose",
        "format": "Code blocks with template content",
        "customization": "What can be customized"
      }
    },
    {
      "name": "Configuration",
      "required": false,
      "content_notes": {
        "options": "Available configuration options",
        "defaults": "Default values",
        "format": "Table of option/default/description"
      }
    }
  ]
}
```

### Guide Sections

```json
{
  "skill_type": "Guide",
  "additional_sections": [
    {
      "name": "Learning Path",
      "required": true,
      "content_notes": {
        "levels": "Beginner → Intermediate → Advanced",
        "progression": "Each level builds on previous",
        "format": "### Level N headers"
      }
    },
    {
      "name": "Best Practices",
      "required": true,
      "content_notes": {
        "dos": "3-5 things to do",
        "donts": "3-5 things to avoid",
        "format": "Bullet lists"
      }
    }
  ]
}
```

### Automation Sections

```json
{
  "skill_type": "Automation",
  "additional_sections": [
    {
      "name": "Triggers",
      "required": true,
      "content_notes": {
        "when": "When to run automatically",
        "manual": "How to invoke manually",
        "format": "Conditions list"
      }
    },
    {
      "name": "Verification",
      "required": true,
      "content_notes": {
        "success": "How to know it worked",
        "failure": "What failure looks like",
        "format": "Success/failure indicators"
      }
    }
  ]
}
```

## Output Format

### Section Plan

```json
{
  "skill_md_plan": {
    "total_sections": 6,
    "estimated_lines": 180,
    "sections": [
      {
        "name": "Overview",
        "order": 1,
        "required": true,
        "estimated_lines": 15,
        "content_notes": {
          "opening": "API Doc Generator creates...",
          "key_points": ["Parses OpenAPI specs", "Generates Markdown"]
        }
      },
      {
        "name": "Workflow",
        "order": 2,
        "required": true,
        "estimated_lines": 50,
        "subsections": [
          {"name": "Step 1: Input", "lines": 15},
          {"name": "Step 2: Parse", "lines": 15},
          {"name": "Step 3: Generate", "lines": 20}
        ]
      }
    ]
  }
}
```

## Integration

### Used By Generation Phase

```markdown
Generation reads section plan:
1. For each section in plan:
   - Use content_notes to guide writing
   - Stay within line_budget
   - Apply appropriate template
2. Assemble into complete SKILL.md
```
