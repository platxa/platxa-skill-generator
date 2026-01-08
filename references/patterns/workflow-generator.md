# Workflow Reference Generator

Generate detailed workflow.md files with step-by-step instructions and decision points.

## Purpose

Create workflow reference files that expand on SKILL.md's Workflow section with:
- Detailed step instructions
- Decision points and branching
- Error handling guidance
- Examples for each step

## Generation Algorithm

```markdown
FUNCTION generate_workflow_reference(discovery, blueprint):
    content = []

    # Header
    content.append(f"# {blueprint.skill_name} Workflow")
    content.append("")
    content.append("Detailed step-by-step instructions for skill execution.")
    content.append("")

    # Overview diagram
    content.append("## Workflow Overview")
    content.append("")
    content.append("```")
    content.append(generate_ascii_flow(discovery.workflow_steps))
    content.append("```")
    content.append("")

    # Prerequisites
    IF discovery.prerequisites:
        content.append("## Prerequisites")
        content.append("")
        FOR prereq in discovery.prerequisites:
            content.append(f"- {prereq}")
        content.append("")

    # Steps
    step_num = 1
    FOR step in discovery.workflow_steps:
        content.append(f"## Step {step_num}: {step.name}")
        content.append("")

        # Purpose
        content.append(f"**Purpose:** {step.purpose}")
        content.append("")

        # Input/Output
        IF step.inputs:
            content.append("**Input:**")
            FOR input in step.inputs:
                content.append(f"- {input}")
            content.append("")

        IF step.outputs:
            content.append("**Output:**")
            FOR output in step.outputs:
                content.append(f"- {output}")
            content.append("")

        # Instructions
        content.append("### Instructions")
        content.append("")
        content.append(step.detailed_instructions)
        content.append("")

        # Code example
        IF step.code_example:
            content.append("### Example")
            content.append("")
            content.append(f"```{step.code_language}")
            content.append(step.code_example)
            content.append("```")
            content.append("")

        # Decision point
        IF step.has_decision:
            content.append(generate_decision_point(step.decision))

        # Error handling
        IF step.error_scenarios:
            content.append("### Error Handling")
            content.append("")
            FOR error in step.error_scenarios:
                content.append(f"**{error.name}:**")
                content.append(f"- Symptom: {error.symptom}")
                content.append(f"- Action: {error.action}")
                content.append("")

        step_num += 1

    # Troubleshooting
    IF discovery.common_issues:
        content.append("## Troubleshooting")
        content.append("")
        FOR issue in discovery.common_issues:
            content.append(f"### {issue.name}")
            content.append(f"**Problem:** {issue.description}")
            content.append(f"**Solution:** {issue.solution}")
            content.append("")

    RETURN "\n".join(content)
```

## Decision Point Format

```markdown
FUNCTION generate_decision_point(decision):
    content = []

    content.append("### Decision Point")
    content.append("")
    content.append(f"**Question:** {decision.question}")
    content.append("")

    FOR option in decision.options:
        content.append(f"#### If {option.condition}:")
        content.append("")
        content.append(option.action)
        IF option.next_step:
            content.append(f"→ Continue to Step {option.next_step}")
        content.append("")

    RETURN "\n".join(content)
```

## ASCII Flow Diagram

```markdown
FUNCTION generate_ascii_flow(steps):
    flow = []
    flow.append("┌─────────┐")
    flow.append("│  Start  │")
    flow.append("└────┬────┘")
    flow.append("     │")

    FOR i, step in enumerate(steps):
        flow.append("     ▼")
        flow.append(f"┌─────────────────┐")
        flow.append(f"│ {i+1}. {step.name[:13]}│")
        flow.append(f"└────────┬────────┘")

        IF step.has_decision:
            flow.append("     │")
            flow.append("     ◇ Decision")
            flow.append("    / \\")
            flow.append("   Y   N")

    flow.append("     │")
    flow.append("     ▼")
    flow.append("┌─────────┐")
    flow.append("│   End   │")
    flow.append("└─────────┘")

    RETURN "\n".join(flow)
```

## Example Output

```markdown
# API Doc Generator Workflow

Detailed step-by-step instructions for skill execution.

## Workflow Overview

```
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
┌─────────────────┐
│ 1. Locate Spec  │
└────────┬────────┘
     │
     ▼
┌─────────────────┐
│ 2. Parse Spec   │
└────────┬────────┘
     │
     ◇ Valid?
    / \
   Y   N
     │
     ▼
┌─────────────────┐
│ 3. Generate     │
└────────┬────────┘
     │
     ▼
┌─────────┐
│   End   │
└─────────┘
```

## Prerequisites

- OpenAPI spec file (3.0+ or 3.1)
- Output directory with write permission
- User preference for output format

## Step 1: Locate Specification

**Purpose:** Find the OpenAPI specification file in the project.

**Input:**
- Project directory
- Optional: explicit spec path

**Output:**
- Path to spec file
- Detected spec version

### Instructions

1. Check if user provided explicit path
2. If not, search common locations:
   - `api/openapi.yaml`
   - `api/openapi.json`
   - `openapi.yaml`
   - `swagger.yaml`
3. Validate file exists and is readable
4. Detect format (YAML/JSON) from extension

### Example

```bash
# Search pattern
find . -name "openapi.*" -o -name "swagger.*" | head -1
```

### Decision Point

**Question:** Was a valid spec file found?

#### If spec found:
Proceed with parsing.
→ Continue to Step 2

#### If no spec found:
Ask user for spec file path using AskUserQuestion.
→ Wait for user response, then continue

### Error Handling

**File not found:**
- Symptom: No matching files in search paths
- Action: Prompt user for explicit path

**Permission denied:**
- Symptom: File exists but cannot read
- Action: Report permission error with path
```

## Token Budget

- Target: 800-1200 tokens
- Maximum: 1500 tokens
- Prioritize: Steps > Decision Points > Error Handling

## Integration

Reference from SKILL.md Workflow section:
```markdown
For detailed step instructions, see [Workflow Reference](references/workflow.md).
```
