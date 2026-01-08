# Skill Templates

Complete templates for each of the 5 skill types.

## Builder Skill Template

Builder skills generate code, files, or projects from inputs.

```yaml
---
name: {{skill-name}}
description: |
  {{One sentence describing what this skill builds/generates}}.
  {{Second sentence about inputs and outputs}}.
tools:
  - Read
  - Write
  - Glob
  - Bash
---

# {{Skill Title}}

{{Brief tagline about what this builds}}.

## Overview

This skill generates {{output type}} from {{input type}}. Use it when you need to:

- {{Primary use case}}
- {{Secondary use case}}
- {{Tertiary use case}}

## Input Requirements

- **Required:** {{Primary input description}}
- **Optional:** {{Optional inputs}}
- **Format:** {{Expected format}}

## Workflow

### Step 1: Locate Input

{{Instructions for finding/validating input}}

### Step 2: Parse Input

{{Instructions for parsing/understanding input}}

### Step 3: Generate Output

{{Instructions for generating output}}

### Step 4: Validate Output

{{Instructions for validating generated content}}

## Templates

### {{Output Type}} Template

```{{language}}
{{Template with placeholders}}
```

## Examples

<example>
user: "{{Example user request}}"
assistant: "{{Example assistant response showing skill in action}}"
</example>

## Output Checklist

- [ ] {{Output file}} generated
- [ ] {{Validation step}} passed
- [ ] {{Quality check}} completed
```

## Guide Skill Template

Guide skills provide expertise and step-by-step guidance.

```yaml
---
name: {{skill-name}}
description: |
  {{One sentence describing what guidance this provides}}.
  {{Second sentence about the domain/expertise}}.
tools:
  - Read
  - Glob
  - WebSearch
---

# {{Skill Title}}

{{Brief tagline about expertise provided}}.

## Overview

This skill guides you through {{domain/process}}. Use it when you need:

- {{Guidance scenario 1}}
- {{Guidance scenario 2}}
- {{Guidance scenario 3}}

## Key Concepts

### {{Concept 1}}

{{Explanation of key concept}}

### {{Concept 2}}

{{Explanation of key concept}}

## Best Practices

### Do

- {{Best practice 1}}
- {{Best practice 2}}
- {{Best practice 3}}

### Don't

- {{Anti-pattern 1}}
- {{Anti-pattern 2}}

## Workflow

### Phase 1: {{Phase Name}}

**Goal:** {{What this phase accomplishes}}

1. {{Step 1}}
2. {{Step 2}}
3. {{Step 3}}

### Phase 2: {{Phase Name}}

**Goal:** {{What this phase accomplishes}}

1. {{Step 1}}
2. {{Step 2}}

## Examples

<example>
user: "{{Example question about domain}}"
assistant: "{{Detailed expert guidance response}}"
</example>

## Checklist

- [ ] {{Understanding verified}}
- [ ] {{Approach selected}}
- [ ] {{Implementation guidance provided}}
```

## Automation Skill Template

Automation skills execute tasks automatically via scripts.

```yaml
---
name: {{skill-name}}
description: |
  {{One sentence describing what this automates}}.
  {{Second sentence about automation benefits}}.
tools:
  - Bash
  - Read
  - Write
---

# {{Skill Title}}

{{Brief tagline about automation}}.

## Overview

This skill automates {{task description}}. Use it to:

- {{Automation benefit 1}}
- {{Automation benefit 2}}
- {{Automation benefit 3}}

## Prerequisites

- {{Prerequisite 1}}
- {{Prerequisite 2}}
- {{Required tool/permission}}

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| {{param1}} | {{default}} | {{description}} |
| {{param2}} | {{default}} | {{description}} |

## Workflow

### Step 1: Validate Environment

```bash
# Check prerequisites
{{validation commands}}
```

### Step 2: Execute Task

```bash
# Main automation
{{execution commands}}
```

### Step 3: Verify Results

```bash
# Verification
{{verification commands}}
```

## Error Handling

### {{Error Type 1}}

**Symptom:** {{What user sees}}
**Cause:** {{Why it happens}}
**Fix:** {{How to resolve}}

### {{Error Type 2}}

**Symptom:** {{What user sees}}
**Fix:** {{How to resolve}}

## Examples

<example>
user: "{{Example automation request}}"
assistant: "{{Example showing automation execution and results}}"
</example>

## Safety

- {{Safety consideration 1}}
- {{Safety consideration 2}}
- Always runs with {{permission level}}
```

## Analyzer Skill Template

Analyzer skills review code/data and provide insights.

```yaml
---
name: {{skill-name}}
description: |
  {{One sentence describing what this analyzes}}.
  {{Second sentence about insights provided}}.
tools:
  - Read
  - Glob
  - Grep
---

# {{Skill Title}}

{{Brief tagline about analysis capabilities}}.

## Overview

This skill analyzes {{target}} to identify:

- {{Analysis focus 1}}
- {{Analysis focus 2}}
- {{Analysis focus 3}}

## Analysis Dimensions

### {{Dimension 1}}

**What:** {{What is analyzed}}
**Why:** {{Why it matters}}
**Output:** {{What insights are provided}}

### {{Dimension 2}}

**What:** {{What is analyzed}}
**Why:** {{Why it matters}}

## Workflow

### Step 1: Gather Data

{{Instructions for collecting analysis targets}}

### Step 2: Analyze

{{Instructions for performing analysis}}

### Step 3: Report Findings

{{Instructions for presenting results}}

## Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| {{metric1}} | {{good}} | {{warning}} | {{critical}} |
| {{metric2}} | {{good}} | {{warning}} | {{critical}} |

## Examples

<example>
user: "{{Example analysis request}}"
assistant: "{{Example showing analysis and insights}}"
</example>

## Output Format

```
Analysis Report: {{Target}}
═══════════════════════════════════════

{{Dimension 1}}: {{Score/Status}}
{{Dimension 2}}: {{Score/Status}}

Findings:
- {{Finding 1}}
- {{Finding 2}}

Recommendations:
- {{Recommendation 1}}
- {{Recommendation 2}}
```
```

## Validator Skill Template

Validator skills check compliance with rules/standards.

```yaml
---
name: {{skill-name}}
description: |
  {{One sentence describing what this validates}}.
  {{Second sentence about compliance standards}}.
tools:
  - Read
  - Glob
  - Bash
---

# {{Skill Title}}

{{Brief tagline about validation}}.

## Overview

This skill validates {{target}} against {{standard/rules}}. Use it to:

- {{Validation use case 1}}
- {{Validation use case 2}}
- {{Validation use case 3}}

## Validation Rules

### {{Rule Category 1}}

| Rule | Severity | Description |
|------|----------|-------------|
| {{rule1}} | Error | {{description}} |
| {{rule2}} | Warning | {{description}} |

### {{Rule Category 2}}

| Rule | Severity | Description |
|------|----------|-------------|
| {{rule1}} | Error | {{description}} |

## Workflow

### Step 1: Collect Targets

{{Instructions for identifying what to validate}}

### Step 2: Run Validation

{{Instructions for executing validation checks}}

### Step 3: Report Results

{{Instructions for presenting validation results}}

## Examples

<example>
user: "{{Example validation request}}"
assistant: "{{Example showing validation execution and results}}"
</example>

## Output Format

```
Validation Results
═══════════════════════════════════════

Target: {{target}}
Status: {{PASS/FAIL}}

Errors ({{count}}):
  ✗ {{error description}}

Warnings ({{count}}):
  ⚠ {{warning description}}

Summary: {{X}} errors, {{Y}} warnings
```

## Pass Criteria

- Zero errors required for PASS
- Warnings acceptable but should be reviewed
- Exit code 0 for PASS, 1 for FAIL
```

## Template Selection

```python
SKILL_TEMPLATES = {
    'builder': 'templates/builder.md',
    'guide': 'templates/guide.md',
    'automation': 'templates/automation.md',
    'analyzer': 'templates/analyzer.md',
    'validator': 'templates/validator.md',
}

def get_template(skill_type: str) -> str:
    """Get template content for skill type."""
    template_path = SKILL_TEMPLATES.get(skill_type)
    if not template_path:
        raise ValueError(f"Unknown skill type: {skill_type}")
    return read_template(template_path)
```
