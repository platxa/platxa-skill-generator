# SKILL.md Section Writers

Generate content for each SKILL.md section based on blueprint and discovery.

## Overview Section Writer

### Purpose
Explain what the skill does, who it's for, and key capabilities.

### Structure

```markdown
## Overview

{One-line summary of what the skill does}

**What it does:**
- {Capability 1}
- {Capability 2}
- {Capability 3}

**Who it's for:** {Target users}

**Key features:**
- {Feature 1}
- {Feature 2}
- {Feature 3}
```

### Generation Algorithm

```markdown
FUNCTION write_overview(blueprint, discovery):
    content = []

    # Opening line
    summary = generate_summary(discovery)
    content.append(f"## Overview\n\n{summary}\n")

    # What it does
    content.append("**What it does:**")
    capabilities = discovery.capabilities[:5]
    FOR cap in capabilities:
        content.append(f"- {cap}")
    content.append("")

    # Who it's for
    target = discovery.target_users or "Developers"
    content.append(f"**Who it's for:** {target}\n")

    # Key features (if different from capabilities)
    IF discovery.key_features:
        content.append("**Key features:**")
        FOR feature in discovery.key_features[:3]:
            content.append(f"- {feature}")

    RETURN "\n".join(content)
```

### Line Budget: 15-30 lines

---

## Workflow Section Writer

### Purpose
Guide users through the step-by-step process of using the skill.

### Structure

```markdown
## Workflow

### Step 1: {Action Verb} {Object}

{Description of what happens}

{Code block or example if needed}

### Step 2: {Action Verb} {Object}

{Description}

**Decision Point:** {If applicable}
- Option A: {path}
- Option B: {path}
```

### Generation Algorithm

```markdown
FUNCTION write_workflow(blueprint, discovery):
    content = ["## Workflow\n"]
    step_num = 1

    FOR step in discovery.workflow_steps:
        # Step header
        header = f"### Step {step_num}: {step.action}"
        content.append(header)
        content.append("")

        # Step description
        content.append(step.description)
        content.append("")

        # Code example if relevant
        IF step.has_example:
            content.append("```")
            content.append(step.example)
            content.append("```")
            content.append("")

        # Decision point
        IF step.has_decision:
            content.append(f"**Decision Point:** {step.decision_prompt}")
            FOR option in step.options:
                content.append(f"- {option.label}: {option.description}")
            content.append("")

        step_num += 1

    RETURN "\n".join(content)
```

### Line Budget: 50-100 lines

---

## Examples Section Writer

### Purpose
Show realistic usage scenarios with user/assistant dialog format.

### Structure

```markdown
## Examples

### Example 1: {Basic Use Case}

User: {Typical request}
Assistant: {How skill handles it with specific steps}

### Example 2: {Edge Case}

User: {Unusual or complex request}
Assistant: {How skill handles edge cases}
```

### Generation Algorithm

```markdown
FUNCTION write_examples(blueprint, discovery):
    content = ["## Examples\n"]

    # Example 1: Basic usage
    basic = discovery.examples.basic or generate_basic_example(discovery)
    content.append("### Example 1: Basic Usage\n")
    content.append("```")
    content.append(f"User: {basic.user_input}")
    content.append(f"Assistant: {basic.assistant_response}")
    content.append("```\n")

    # Example 2: Edge case or advanced
    IF discovery.examples.advanced:
        content.append("### Example 2: Advanced Usage\n")
        content.append("```")
        content.append(f"User: {discovery.examples.advanced.user_input}")
        content.append(f"Assistant: {discovery.examples.advanced.assistant_response}")
        content.append("```")

    RETURN "\n".join(content)
```

### Line Budget: 40-80 lines

---

## Output Checklist Writer

### Purpose
Provide verification items to confirm skill completed successfully.

### Structure

```markdown
## Output Checklist

### Files Created
- [ ] {file1} exists and is valid
- [ ] {file2} has correct content

### Quality Checks
- [ ] {quality check 1}
- [ ] {quality check 2}

### Verification Commands
- [ ] Run: `{command}` - expect: {expected output}
```

### Generation Algorithm

```markdown
FUNCTION write_output_checklist(blueprint, discovery):
    content = ["## Output Checklist\n"]

    # Files section
    IF blueprint.outputs_files:
        content.append("### Files Created")
        FOR file in blueprint.output_files:
            content.append(f"- [ ] `{file}` exists and is valid")
        content.append("")

    # Quality checks
    content.append("### Quality Checks")
    checks = get_quality_checks(blueprint.skill_type)
    FOR check in checks:
        content.append(f"- [ ] {check}")
    content.append("")

    # Verification commands (if applicable)
    IF blueprint.has_validation_script:
        content.append("### Verification Commands")
        content.append(f"- [ ] Run: `./scripts/validate.sh` - expect: exit code 0")

    RETURN "\n".join(content)
```

### Line Budget: 15-30 lines

---

## Type-Specific Sections

### Builder: Templates Section

```markdown
FUNCTION write_templates_section(blueprint, discovery):
    content = ["## Templates\n"]

    FOR template in blueprint.templates:
        content.append(f"### {template.name}\n")
        content.append(template.description)
        content.append("\n```")
        content.append(template.content_preview)
        content.append("```\n")

    RETURN "\n".join(content)
```

### Guide: Best Practices Section

```markdown
FUNCTION write_best_practices(blueprint, discovery):
    content = ["## Best Practices\n"]

    content.append("### Do")
    FOR practice in discovery.do_practices[:5]:
        content.append(f"- {practice}")
    content.append("")

    content.append("### Don't")
    FOR anti in discovery.dont_practices[:5]:
        content.append(f"- {anti}")

    RETURN "\n".join(content)
```

### Automation: Triggers Section

```markdown
FUNCTION write_triggers_section(blueprint, discovery):
    content = ["## Triggers\n"]

    content.append("### When to Run")
    FOR trigger in discovery.triggers:
        content.append(f"- {trigger}")
    content.append("")

    content.append("### Manual Invocation")
    content.append(f"```\n/{blueprint.skill_name}\n```")

    RETURN "\n".join(content)
```

### Validator: Rules Section

```markdown
FUNCTION write_rules_section(blueprint, discovery):
    content = ["## Validation Rules\n"]

    FOR rule in discovery.validation_rules:
        content.append(f"### {rule.name}")
        content.append(f"- **Check:** {rule.check}")
        content.append(f"- **Severity:** {rule.severity}")
        content.append(f"- **Message:** {rule.message}")
        content.append("")

    RETURN "\n".join(content)
```

---

## Integration

### Section Assembly Order

1. YAML Frontmatter (always first)
2. Overview (required)
3. Workflow (required)
4. Type-specific sections
5. Examples (required)
6. Output Checklist (required)

### Line Budget Enforcement

```markdown
FUNCTION assemble_skill_md(sections, budget=500):
    total_lines = 0
    assembled = []

    FOR section in sections:
        IF total_lines + section.lines <= budget:
            assembled.append(section.content)
            total_lines += section.lines
        ELSE:
            # Compress or truncate
            remaining = budget - total_lines
            compressed = compress_section(section, remaining)
            assembled.append(compressed)
            break

    RETURN "\n\n".join(assembled)
```