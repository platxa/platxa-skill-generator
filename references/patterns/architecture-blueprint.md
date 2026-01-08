# Architecture Blueprint Generator

Generate complete skill blueprint from discovery findings.

## Blueprint Purpose

The architecture blueprint is the complete plan for the skill:
- All files to create
- Content outline for each file
- Dependencies between files
- Token budgets allocated
- Generation order

## Blueprint Schema

```json
{
  "$schema": "architecture-blueprint-v1",
  "blueprint": {
    "skill_name": "string (hyphen-case, ≤64 chars)",
    "skill_type": "Builder|Guide|Automation|Analyzer|Validator",
    "version": "1.0.0",
    "generated_at": "ISO-8601 timestamp",

    "structure": {
      "root_files": ["SKILL.md"],
      "directories": ["scripts/", "references/"],
      "total_files": "number",
      "estimated_tokens": "number"
    },

    "skill_md": {
      "path": "SKILL.md",
      "sections": [
        {
          "name": "section name",
          "order": "number",
          "required": "boolean",
          "line_budget": "number",
          "content_notes": "guidance for generation"
        }
      ],
      "total_lines": "number (<500)"
    },

    "scripts": {
      "include": "boolean",
      "files": [
        {
          "name": "script.sh",
          "path": "scripts/script.sh",
          "purpose": "description",
          "interface": {
            "usage": "string",
            "args": [],
            "options": [],
            "exit_codes": []
          },
          "estimated_lines": "number"
        }
      ]
    },

    "references": {
      "include": "boolean",
      "files": [
        {
          "name": "file.md",
          "path": "references/file.md",
          "category": "domain|workflow|template|validation",
          "purpose": "description",
          "token_budget": "number",
          "content_outline": {
            "sections": [],
            "sources": []
          }
        }
      ],
      "subdirectories": []
    },

    "generation_order": [
      {"step": 1, "file": "SKILL.md", "depends_on": []},
      {"step": 2, "file": "scripts/validate.sh", "depends_on": ["SKILL.md"]},
      {"step": 3, "file": "references/concepts.md", "depends_on": []}
    ],

    "metadata": {
      "discovery_source": "discovery_id",
      "complexity_score": "0.0-1.0",
      "confidence_score": "0.0-1.0"
    }
  }
}
```

## Generation Algorithm

```markdown
FUNCTION generate_blueprint(discovery, skill_type):
    blueprint = initialize_blueprint()

    # Set basic info
    blueprint.skill_name = normalize_name(discovery.skill_name)
    blueprint.skill_type = skill_type
    blueprint.generated_at = now()

    # Step 1: Plan SKILL.md structure
    blueprint.skill_md = plan_skill_md(skill_type, discovery)

    # Step 2: Plan scripts
    blueprint.scripts = plan_scripts(skill_type, discovery)

    # Step 3: Plan references
    blueprint.references = plan_references(skill_type, discovery)

    # Step 4: Calculate structure
    blueprint.structure = calculate_structure(blueprint)

    # Step 5: Allocate token budgets
    blueprint = allocate_budgets(blueprint, discovery)

    # Step 6: Determine generation order
    blueprint.generation_order = plan_generation_order(blueprint)

    # Step 7: Add metadata
    blueprint.metadata = {
        discovery_source: discovery.id,
        complexity_score: discovery.complexity,
        confidence_score: calculate_confidence(blueprint)
    }

    RETURN blueprint
```

## SKILL.md Planning

```markdown
FUNCTION plan_skill_md(skill_type, discovery):
    sections = []

    # Required sections (all types)
    sections.append({
        name: "YAML Frontmatter",
        order: 0,
        required: true,
        line_budget: 15,
        content_notes: {
            name: discovery.skill_name,
            description: discovery.description,
            tools: determine_tools(skill_type)
        }
    })

    sections.append({
        name: "Overview",
        order: 1,
        required: true,
        line_budget: 25,
        content_notes: {
            what: discovery.purpose,
            who: discovery.target_users,
            features: discovery.key_features[:5]
        }
    })

    sections.append({
        name: "Workflow",
        order: 2,
        required: true,
        line_budget: calculate_workflow_budget(discovery),
        content_notes: {
            steps: discovery.workflow_steps,
            decisions: discovery.decision_points
        }
    })

    # Type-specific sections
    type_sections = get_type_sections(skill_type)
    FOR section in type_sections:
        sections.append({
            name: section.name,
            order: len(sections),
            required: section.required,
            line_budget: section.default_lines,
            content_notes: section.guidance
        })

    # Examples and checklist
    sections.append({
        name: "Examples",
        order: len(sections),
        required: true,
        line_budget: 60,
        content_notes: {
            count: 2,
            types: ["basic", "edge_case"]
        }
    })

    sections.append({
        name: "Output Checklist",
        order: len(sections),
        required: true,
        line_budget: 25,
        content_notes: {
            categories: get_checklist_categories(skill_type)
        }
    })

    # Verify total < 500
    total = sum(s.line_budget for s in sections)
    IF total > 450:
        sections = compress_sections(sections, 450)

    RETURN {
        path: "SKILL.md",
        sections: sections,
        total_lines: sum(s.line_budget for s in sections)
    }
```

## Generation Order Planning

```markdown
FUNCTION plan_generation_order(blueprint):
    order = []
    step = 1

    # SKILL.md always first (no dependencies)
    order.append({
        step: step++,
        file: "SKILL.md",
        depends_on: [],
        reason: "Entry point must exist first"
    })

    # References next (may be referenced by scripts)
    FOR ref in blueprint.references.files:
        order.append({
            step: step++,
            file: ref.path,
            depends_on: [],
            reason: "Reference content needed before validation"
        })

    # Scripts last (may reference SKILL.md or refs)
    FOR script in blueprint.scripts.files:
        deps = []
        IF script.validates_skill:
            deps.append("SKILL.md")
        order.append({
            step: step++,
            file: script.path,
            depends_on: deps,
            reason: "Scripts depend on skill structure"
        })

    RETURN order
```

## Example Blueprint Output

```json
{
  "$schema": "architecture-blueprint-v1",
  "blueprint": {
    "skill_name": "api-doc-generator",
    "skill_type": "Builder",
    "version": "1.0.0",
    "generated_at": "2026-01-07T12:00:00Z",

    "structure": {
      "root_files": ["SKILL.md"],
      "directories": ["scripts/", "references/", "references/templates/"],
      "total_files": 8,
      "estimated_tokens": 12500
    },

    "skill_md": {
      "path": "SKILL.md",
      "sections": [
        {
          "name": "YAML Frontmatter",
          "order": 0,
          "required": true,
          "line_budget": 15,
          "content_notes": {
            "name": "api-doc-generator",
            "description": "Generates API documentation from OpenAPI specs",
            "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
          }
        },
        {
          "name": "Overview",
          "order": 1,
          "required": true,
          "line_budget": 25,
          "content_notes": {
            "what": "Generates Markdown/HTML docs from OpenAPI",
            "who": "Backend developers",
            "features": ["Parse OpenAPI 3.x", "Multiple formats", "Customizable"]
          }
        },
        {
          "name": "Workflow",
          "order": 2,
          "required": true,
          "line_budget": 80,
          "content_notes": {
            "steps": ["Locate spec", "Parse", "Extract", "Format", "Output"],
            "decisions": ["Output format", "Include examples"]
          }
        },
        {
          "name": "Templates",
          "order": 3,
          "required": true,
          "line_budget": 60,
          "content_notes": {
            "list": ["endpoint.md", "schema.md", "auth.md"],
            "customization": "Variables for project-specific values"
          }
        },
        {
          "name": "Configuration",
          "order": 4,
          "required": false,
          "line_budget": 40,
          "content_notes": {
            "options": ["output_dir", "format", "include_examples"]
          }
        },
        {
          "name": "Examples",
          "order": 5,
          "required": true,
          "line_budget": 60,
          "content_notes": {
            "count": 2,
            "types": ["basic_api", "complex_with_auth"]
          }
        },
        {
          "name": "Output Checklist",
          "order": 6,
          "required": true,
          "line_budget": 25,
          "content_notes": {
            "categories": ["files_created", "content_verified", "formatting"]
          }
        }
      ],
      "total_lines": 305
    },

    "scripts": {
      "include": true,
      "files": [
        {
          "name": "validate-output.sh",
          "path": "scripts/validate-output.sh",
          "purpose": "Validate generated documentation",
          "interface": {
            "usage": "validate-output.sh <output-dir>",
            "args": [{"name": "output-dir", "required": true}],
            "options": [{"flag": "--strict"}],
            "exit_codes": [{"code": 0, "meaning": "valid"}]
          },
          "estimated_lines": 60
        },
        {
          "name": "install-skill.sh",
          "path": "scripts/install-skill.sh",
          "purpose": "Install skill to user/project location",
          "interface": {
            "usage": "install-skill.sh [--user|--project]",
            "args": [],
            "options": [{"flag": "--user"}, {"flag": "--project"}],
            "exit_codes": [{"code": 0, "meaning": "success"}]
          },
          "estimated_lines": 50
        }
      ]
    },

    "references": {
      "include": true,
      "files": [
        {
          "name": "openapi-concepts.md",
          "path": "references/openapi-concepts.md",
          "category": "domain",
          "purpose": "OpenAPI terminology and structure",
          "token_budget": 1500,
          "content_outline": {
            "sections": ["Terms", "Structure", "Data Types"],
            "sources": ["discovery.domain_knowledge"]
          }
        },
        {
          "name": "endpoint.md",
          "path": "references/templates/endpoint.md",
          "category": "template",
          "purpose": "Endpoint documentation template",
          "token_budget": 600,
          "content_outline": {
            "template_vars": ["method", "path", "description", "params"],
            "format": "Markdown with placeholders"
          }
        }
      ],
      "subdirectories": [
        {"name": "templates/", "purpose": "Output templates"}
      ]
    },

    "generation_order": [
      {"step": 1, "file": "SKILL.md", "depends_on": []},
      {"step": 2, "file": "references/openapi-concepts.md", "depends_on": []},
      {"step": 3, "file": "references/templates/endpoint.md", "depends_on": []},
      {"step": 4, "file": "scripts/validate-output.sh", "depends_on": ["SKILL.md"]},
      {"step": 5, "file": "scripts/install-skill.sh", "depends_on": []}
    ],

    "metadata": {
      "discovery_source": "discovery-abc123",
      "complexity_score": 0.65,
      "confidence_score": 0.85
    }
  }
}
```

## Validation

```markdown
FUNCTION validate_blueprint(blueprint):
    errors = []

    # Check skill_md constraints
    IF blueprint.skill_md.total_lines > 500:
        errors.append("SKILL.md exceeds 500 line limit")

    # Check required sections
    required = ["YAML Frontmatter", "Overview", "Workflow", "Examples", "Output Checklist"]
    FOR section in required:
        IF section NOT IN blueprint.skill_md.sections:
            errors.append(f"Missing required section: {section}")

    # Check token budgets
    total_tokens = sum(ref.token_budget for ref in blueprint.references.files)
    IF total_tokens > 10000:
        errors.append("References exceed 10,000 token limit")

    # Check generation order has all files
    all_files = get_all_files(blueprint)
    ordered_files = [o.file for o in blueprint.generation_order]
    IF set(all_files) != set(ordered_files):
        errors.append("Generation order missing files")

    RETURN len(errors) == 0, errors
```

## Integration

### Input (from Discovery)

- `discovery.skill_name` → Blueprint skill name
- `discovery.workflow_steps` → SKILL.md Workflow section
- `discovery.domain_knowledge` → References content
- `discovery.complexity` → Budget allocation

### Output (to Generation)

- Complete file list with paths
- Content outlines for each file
- Token budgets per file
- Generation order with dependencies
