# Few-Shot Example Generator

Generate concrete examples that demonstrate key skill behaviors.

## Purpose

Few-shot examples in SKILL.md help Claude understand:
- What inputs to expect
- How to process them
- What outputs to produce
- Edge cases to handle

## Example Categories

### By Complexity

| Category | Purpose | When to Use |
|----------|---------|-------------|
| Basic | Happy path demonstration | Always include |
| Edge case | Error handling, unusual input | Recommended |
| Advanced | Complex multi-step scenario | For complex skills |

### By Skill Type

| Type | Example Focus |
|------|---------------|
| Builder | Input → Output transformation |
| Guide | Question → Explanation flow |
| Automation | Trigger → Action → Verification |
| Analyzer | Target → Analysis → Report |
| Validator | Input → Validation → Result |

## Generation Algorithm

```markdown
FUNCTION generate_examples(discovery, blueprint):
    examples = []

    # Example 1: Basic usage (always)
    basic = generate_basic_example(discovery)
    examples.append(basic)

    # Example 2: Edge case (recommended)
    IF discovery.has_edge_cases:
        edge = generate_edge_example(discovery)
        examples.append(edge)

    # Example 3: Advanced (if complex skill)
    IF blueprint.complexity > 0.7:
        advanced = generate_advanced_example(discovery)
        examples.append(advanced)

    RETURN examples
```

## Basic Example Generation

```markdown
FUNCTION generate_basic_example(discovery):
    # Determine typical user request
    user_input = template_user_request(
        action: discovery.primary_action,
        target: discovery.typical_target,
        context: discovery.common_context
    )

    # Generate expected assistant behavior
    assistant_response = template_assistant_response(
        acknowledgment: brief_confirmation(discovery),
        steps: discovery.workflow_steps[:3],
        outcome: discovery.primary_output
    )

    RETURN {
        title: "Basic Usage",
        user: user_input,
        assistant: assistant_response
    }
```

### User Request Templates

```markdown
# Builder skills
"Create a {output_type} for {input_description}"
"Generate {output} from {source}"

# Guide skills
"How do I {action}?"
"Explain {concept} in {context}"

# Automation skills
"Run {process} on {target}"
"Execute {workflow}"

# Analyzer skills
"Analyze {target} for {criteria}"
"Review {subject} and report on {aspects}"

# Validator skills
"Validate {target} against {rules}"
"Check if {subject} meets {criteria}"
```

### Assistant Response Templates

```markdown
# Opening acknowledgment
"I'll {action} for you. Let me {first_step}."

# Progress indication
"First, I'll {step_1}. Then {step_2}."

# Completion
"Done! I've {completed_action}. Here's what was created: {summary}"
```

## Edge Case Generation

```markdown
FUNCTION generate_edge_example(discovery):
    # Identify common edge cases
    edge_cases = [
        "missing_input",
        "invalid_format",
        "empty_result",
        "permission_error",
        "partial_success"
    ]

    # Select relevant edge case
    relevant = select_relevant_edge(discovery, edge_cases)

    user_input = template_edge_request(relevant, discovery)
    assistant_response = template_edge_response(relevant, discovery)

    RETURN {
        title: f"Handling {relevant.title}",
        user: user_input,
        assistant: assistant_response
    }
```

### Edge Case Patterns

| Edge Case | User Request Pattern | Assistant Response Pattern |
|-----------|---------------------|---------------------------|
| Missing input | Request without required info | Ask for missing info politely |
| Invalid format | Provide wrong format | Explain expected format |
| Empty result | Request with no matches | Explain why empty, suggest alternatives |
| Permission error | Request blocked action | Explain limitation, offer workaround |

## Example Format

### Standard Format

```markdown
### Example 1: Creating API Documentation

User: Generate documentation for my OpenAPI spec at api/openapi.yaml