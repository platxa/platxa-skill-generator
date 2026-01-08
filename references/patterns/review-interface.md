# Review Interface

Interface for reviewing generated skill content before installation.

## Purpose

Allow users to review, approve, or request changes to generated content at key checkpoints in the workflow.

## Review Checkpoints

| Checkpoint | When | What's Shown |
|------------|------|--------------|
| Discovery | After discovery phase | Key findings summary |
| Architecture | After blueprint | Skill structure plan |
| SKILL.md | After generation | Full SKILL.md content |
| References | After generation | Reference file list |
| Final | Before installation | Complete skill summary |

## Content Display Format

### Discovery Review

```markdown
## Discovery Findings Review

**Domain:** OpenAPI / API Documentation
**Skill Type:** Builder

### Key Terminology Found
- operationId: Unique operation identifier
- $ref: JSON Reference pointer
- discriminator: Polymorphism marker

### Best Practices Identified
1. Use components for reuse
2. Include response examples
3. Always set operationId

### Workflow Steps
1. Locate specification file
2. Parse and validate
3. Generate documentation

**Sufficiency Score:** 0.85 (Good)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Architecture Review

```markdown
## Architecture Blueprint Review

**Skill Name:** api-doc-generator
**Type:** Builder

### Files to Generate
```
api-doc-generator/
├── SKILL.md (main skill file)
├── scripts/
│   └── generate.sh
└── references/
    ├── openapi-concepts.md
    └── best-practices.md
```

### SKILL.md Sections
1. Frontmatter (name, description, tools)
2. Overview
3. Workflow (4 steps)
4. Examples (2)
5. Output Checklist

**Estimated Tokens:** ~3,500

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### SKILL.md Preview

```markdown
## SKILL.md Preview

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---
name: api-doc-generator
description: |
  Generate comprehensive API documentation from OpenAPI 3.x specifications.
  Creates markdown docs with endpoints, schemas, and examples.
tools:
  - Read
  - Write
  - Glob
---

# API Documentation Generator

Generate beautiful API documentation from OpenAPI specifications.

## Overview
[Content preview...]

## Workflow
[Content preview...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Lines:** 287 | **Est. Tokens:** 3,420 | **Quality:** 8.2/10
```

## Review Questions

### After Each Checkpoint

```python
def ask_review_approval(
    checkpoint: str,
    summary: str,
    quality_score: float
) -> dict:
    """
    Ask user to approve content at checkpoint.

    Args:
        checkpoint: Which review checkpoint
        summary: Brief summary of what was generated
        quality_score: Quality assessment score

    Returns:
        AskUserQuestion payload
    """
    return {
        "questions": [{
            "question": f"Review {checkpoint}: {summary}. Quality: {quality_score}/10. How to proceed?",
            "header": "Review",
            "options": [
                {
                    "label": "Approve",
                    "description": "Content looks good, continue to next phase"
                },
                {
                    "label": "Request changes",
                    "description": "Specify what needs to be different"
                },
                {
                    "label": "Regenerate",
                    "description": "Start this phase over with different approach"
                },
                {
                    "label": "Cancel",
                    "description": "Stop skill generation entirely"
                }
            ],
            "multiSelect": False
        }]
    }
```

### Change Request

```python
def ask_what_to_change(content_type: str) -> dict:
    """
    Ask user what changes they want.

    Args:
        content_type: What content is being changed

    Returns:
        AskUserQuestion payload
    """
    return {
        "questions": [{
            "question": f"What changes would you like to the {content_type}?",
            "header": "Changes",
            "options": [
                {
                    "label": "Add more detail",
                    "description": "Expand explanations and examples"
                },
                {
                    "label": "Simplify",
                    "description": "Reduce complexity and length"
                },
                {
                    "label": "Different approach",
                    "description": "Try a different methodology"
                },
                {
                    "label": "Specific fix",
                    "description": "I'll describe what to change"
                }
            ],
            "multiSelect": False
        }]
    }
```

## Response Handling

```python
def handle_review_response(response: dict, checkpoint: str) -> dict:
    """
    Handle user's review decision.

    Args:
        response: User's answer
        checkpoint: Current checkpoint

    Returns:
        Action to take
    """
    answer = response.get('answers', {}).get('q0', 'Cancel')

    if answer == 'Approve':
        return {
            'action': 'continue',
            'next_phase': get_next_phase(checkpoint)
        }

    elif answer == 'Request changes':
        return {
            'action': 'modify',
            'request_details': True
        }

    elif answer == 'Regenerate':
        return {
            'action': 'regenerate',
            'phase': checkpoint
        }

    else:  # Cancel
        return {
            'action': 'cancel',
            'cleanup': True
        }


def get_next_phase(current: str) -> str:
    """Get next phase after approval."""
    phases = ['discovery', 'architecture', 'generation', 'validation', 'installation']
    idx = phases.index(current)
    return phases[idx + 1] if idx < len(phases) - 1 else 'complete'
```

## Final Review Summary

```python
def show_final_review(skill_summary: dict) -> str:
    """
    Generate final review summary before installation.

    Args:
        skill_summary: Complete skill information

    Returns:
        Formatted summary string
    """
    return f"""
## Final Review: {skill_summary['name']}

### Quality Assessment
- Overall Score: {skill_summary['quality_score']}/10
- Recommendation: {skill_summary['recommendation']}

### Files Generated
{format_file_tree(skill_summary['files'])}

### Token Usage
- SKILL.md: {skill_summary['skill_md_tokens']} tokens
- References: {skill_summary['ref_tokens']} tokens
- Total: {skill_summary['total_tokens']} tokens

### Warnings
{format_warnings(skill_summary.get('warnings', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to install to: ~/.claude/commands/{skill_summary['name']}/
"""
```

## Integration

```python
# Review at each checkpoint
for phase in ['discovery', 'architecture', 'generation', 'validation']:
    result = run_phase(phase)
    display_review(phase, result)

    response = ask_review_approval(
        checkpoint=phase,
        summary=result.summary,
        quality_score=result.quality
    )

    action = handle_review_response(response, phase)

    if action['action'] == 'cancel':
        cleanup_and_exit()
    elif action['action'] == 'regenerate':
        result = run_phase(phase)  # Retry
    elif action['action'] == 'modify':
        changes = get_change_details()
        result = run_phase_with_changes(phase, changes)
```
