# Architecture Validation

Validate architecture blueprint against Agent Skills Specification v1.0.

## Validation Scope

The architecture phase must produce a valid blueprint before generation:
- Required files present
- Structure follows spec
- Token budgets within limits
- All dependencies resolvable

## Validation Rules

### Required Files

```json
{
  "required_files": [
    {
      "file": "SKILL.md",
      "type": "entry_point",
      "required": true,
      "constraints": {
        "max_lines": 500,
        "must_have_frontmatter": true,
        "must_have_sections": ["Overview", "Workflow"]
      }
    }
  ],
  "conditional_files": [
    {
      "file": "scripts/",
      "type": "directory",
      "required_when": "skill_type in ['Builder', 'Automation', 'Validator']",
      "constraints": {
        "scripts_executable": true
      }
    },
    {
      "file": "references/",
      "type": "directory",
      "required_when": "has_domain_knowledge or skill_type == 'Guide'",
      "constraints": {
        "max_total_tokens": 10000
      }
    }
  ]
}
```

### SKILL.md Structure Validation

```markdown
FUNCTION validate_skill_md(blueprint):
    errors = []
    warnings = []

    skill_md = blueprint.skill_md

    # Rule 1: Line count
    IF skill_md.total_lines > 500:
        errors.append({
            rule: "SKILL_MD_LINE_LIMIT",
            message: f"SKILL.md has {skill_md.total_lines} lines, max 500",
            severity: "error"
        })
    ELIF skill_md.total_lines > 450:
        warnings.append({
            rule: "SKILL_MD_LINE_LIMIT",
            message: f"SKILL.md at {skill_md.total_lines} lines, approaching limit",
            severity: "warning"
        })

    # Rule 2: Required sections
    required_sections = ["YAML Frontmatter", "Overview", "Workflow"]
    section_names = [s.name for s in skill_md.sections]

    FOR required in required_sections:
        IF required NOT IN section_names:
            errors.append({
                rule: "REQUIRED_SECTION",
                message: f"Missing required section: {required}",
                severity: "error"
            })

    # Rule 3: Section order
    IF NOT is_valid_order(skill_md.sections):
        warnings.append({
            rule: "SECTION_ORDER",
            message: "Sections not in recommended order",
            severity: "warning"
        })

    # Rule 4: Frontmatter validation
    frontmatter = get_section(skill_md, "YAML Frontmatter")
    IF frontmatter:
        frontmatter_errors = validate_frontmatter(frontmatter)
        errors.extend(frontmatter_errors)

    RETURN errors, warnings
```

### Frontmatter Validation

```markdown
FUNCTION validate_frontmatter(frontmatter):
    errors = []
    notes = frontmatter.content_notes

    # Name validation
    name = notes.name
    IF len(name) > 64:
        errors.append({
            rule: "NAME_LENGTH",
            message: f"Name '{name}' exceeds 64 characters",
            severity: "error"
        })

    IF NOT matches_pattern(name, r'^[a-z][a-z0-9-]*[a-z0-9]$'):
        errors.append({
            rule: "NAME_FORMAT",
            message: "Name must be hyphen-case (lowercase letters, numbers, hyphens)",
            severity: "error"
        })

    # Description validation
    description = notes.description
    IF len(description) > 1024:
        errors.append({
            rule: "DESCRIPTION_LENGTH",
            message: f"Description exceeds 1024 characters",
            severity: "error"
        })

    IF len(description) < 20:
        errors.append({
            rule: "DESCRIPTION_LENGTH",
            message: "Description too short (min 20 characters)",
            severity: "warning"
        })

    # Tools validation
    tools = notes.tools or []
    valid_tools = [
        "Read", "Write", "Edit", "Bash", "Glob", "Grep",
        "WebFetch", "WebSearch", "Task", "AskUserQuestion",
        "TodoWrite", "LSP", "NotebookEdit"
    ]

    FOR tool in tools:
        IF tool NOT IN valid_tools:
            errors.append({
                rule: "INVALID_TOOL",
                message: f"Unknown tool: {tool}",
                severity: "error"
            })

    RETURN errors
```

### Token Budget Validation

```markdown
FUNCTION validate_token_budgets(blueprint):
    errors = []
    warnings = []

    # SKILL.md token estimate
    skill_tokens = estimate_tokens(blueprint.skill_md)
    IF skill_tokens > 5000:
        errors.append({
            rule: "SKILL_MD_TOKENS",
            message: f"SKILL.md estimated at {skill_tokens} tokens, max 5000",
            severity: "error"
        })

    # References total
    IF blueprint.references.include:
        ref_tokens = sum(r.token_budget for r in blueprint.references.files)
        IF ref_tokens > 10000:
            errors.append({
                rule: "REFERENCES_TOKENS",
                message: f"References total {ref_tokens} tokens, max 10000",
                severity: "error"
            })

        # Individual reference limits
        FOR ref in blueprint.references.files:
            IF ref.token_budget > 2000:
                warnings.append({
                    rule: "SINGLE_REF_TOKENS",
                    message: f"{ref.name} at {ref.token_budget} tokens, consider splitting",
                    severity: "warning"
                })

    RETURN errors, warnings
```

### Structure Validation

```markdown
FUNCTION validate_structure(blueprint):
    errors = []

    # Check directories are valid
    valid_dirs = ["scripts/", "references/", "examples/"]
    FOR dir in blueprint.structure.directories:
        base_dir = dir.split("/")[0] + "/"
        IF base_dir NOT IN valid_dirs AND NOT dir.startswith("references/"):
            errors.append({
                rule: "INVALID_DIRECTORY",
                message: f"Non-standard directory: {dir}",
                severity: "warning"
            })

    # Check generation order completeness
    all_files = []
    all_files.append(blueprint.skill_md.path)
    all_files.extend([s.path for s in blueprint.scripts.files])
    all_files.extend([r.path for r in blueprint.references.files])

    ordered_files = [o.file for o in blueprint.generation_order]

    missing = set(all_files) - set(ordered_files)
    IF missing:
        errors.append({
            rule: "GENERATION_ORDER_INCOMPLETE",
            message: f"Files missing from generation order: {missing}",
            severity: "error"
        })

    # Check dependencies are valid
    FOR order_item in blueprint.generation_order:
        FOR dep in order_item.depends_on:
            IF dep NOT IN ordered_files:
                errors.append({
                    rule: "INVALID_DEPENDENCY",
                    message: f"{order_item.file} depends on unknown file: {dep}",
                    severity: "error"
                })

    RETURN errors
```

### Type-Specific Validation

```markdown
FUNCTION validate_type_requirements(blueprint):
    errors = []
    skill_type = blueprint.skill_type
    sections = [s.name for s in blueprint.skill_md.sections]

    # Builder requirements
    IF skill_type == "Builder":
        IF "Templates" NOT IN sections AND "Configuration" NOT IN sections:
            errors.append({
                rule: "BUILDER_SECTIONS",
                message: "Builder skills should have Templates or Configuration section",
                severity: "warning"
            })

    # Guide requirements
    IF skill_type == "Guide":
        IF "Best Practices" NOT IN sections:
            errors.append({
                rule: "GUIDE_SECTIONS",
                message: "Guide skills should have Best Practices section",
                severity: "warning"
            })
        IF NOT blueprint.references.include:
            errors.append({
                rule: "GUIDE_REFERENCES",
                message: "Guide skills should have references/ directory",
                severity: "warning"
            })

    # Automation requirements
    IF skill_type == "Automation":
        IF "Triggers" NOT IN sections:
            errors.append({
                rule: "AUTOMATION_SECTIONS",
                message: "Automation skills should have Triggers section",
                severity: "warning"
            })
        IF "Verification" NOT IN sections:
            errors.append({
                rule: "AUTOMATION_SECTIONS",
                message: "Automation skills should have Verification section",
                severity: "warning"
            })

    # Validator requirements
    IF skill_type == "Validator":
        IF NOT blueprint.scripts.include:
            errors.append({
                rule: "VALIDATOR_SCRIPTS",
                message: "Validator skills must have scripts/ directory",
                severity: "error"
            })

    RETURN errors
```

## Full Validation Pipeline

```markdown
FUNCTION validate_architecture(blueprint):
    all_errors = []
    all_warnings = []

    # Run all validators
    e1, w1 = validate_skill_md(blueprint)
    all_errors.extend(e1)
    all_warnings.extend(w1)

    e2, w2 = validate_token_budgets(blueprint)
    all_errors.extend(e2)
    all_warnings.extend(w2)

    e3 = validate_structure(blueprint)
    all_errors.extend(e3)

    e4 = validate_type_requirements(blueprint)
    all_errors.extend(e4)

    # Calculate result
    is_valid = len([e for e in all_errors if e.severity == "error"]) == 0

    RETURN {
        valid: is_valid,
        errors: all_errors,
        warnings: all_warnings,
        summary: {
            error_count: len([e for e in all_errors if e.severity == "error"]),
            warning_count: len(all_warnings)
        }
    }
```

## Validation Output

```json
{
  "validation_result": {
    "valid": true,
    "errors": [],
    "warnings": [
      {
        "rule": "SKILL_MD_LINE_LIMIT",
        "message": "SKILL.md at 460 lines, approaching limit",
        "severity": "warning",
        "location": "blueprint.skill_md"
      }
    ],
    "summary": {
      "error_count": 0,
      "warning_count": 1,
      "rules_checked": 12,
      "rules_passed": 12
    }
  }
}
```

## Integration

### When Validation Fails

```markdown
IF NOT validation_result.valid:
    1. Log errors to state
    2. Identify fixable vs blocking errors
    3. For fixable: auto-correct and re-validate
    4. For blocking: return to discovery with gaps
```

### Auto-Corrections

| Error | Auto-Fix |
|-------|----------|
| Line budget exceeded | Compress sections proportionally |
| Missing recommended section | Add with minimal content |
| Token budget exceeded | Move content to references |
| Invalid tool name | Remove from list |
