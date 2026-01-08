# Quality Iteration Loop

Pattern for improving generated skills until quality threshold is met.

## Quality Threshold

| Threshold | Score | Action |
|-----------|-------|--------|
| Pass | ≥ 7.0 | Proceed to installation |
| Iterate | 5.0 - 6.9 | Loop back with feedback |
| Reject | < 5.0 | Major rework or restart |

## Iteration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GENERATION PHASE                         │
│  ┌─────────┐   ┌────────────┐   ┌─────────────┐            │
│  │ SKILL.md│   │ references/│   │  scripts/   │            │
│  └────┬────┘   └─────┬──────┘   └──────┬──────┘            │
│       └──────────────┼─────────────────┘                    │
│                      ▼                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    VALIDATION PHASE                          │
│                                                              │
│  Structure ──▶ Frontmatter ──▶ Tokens ──▶ Quality           │
│                                              │                │
│                                              ▼                │
│                                    ┌─────────────────┐       │
│                                    │  Score: X.X/10  │       │
│                                    └────────┬────────┘       │
└─────────────────────────────────────────────┼────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────┐
                    │                         │                 │
                    ▼                         ▼                 ▼
              Score ≥ 7.0              5.0 ≤ Score < 7.0    Score < 5.0
                    │                         │                 │
                    ▼                         ▼                 ▼
              [INSTALLATION]          [ITERATION LOOP]     [REJECT/RESTART]
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ Generate        │
                                    │ Improvement     │
                                    │ Feedback        │
                                    └────────┬────────┘
                                              │
                                              │ (back to generation)
                                              ▼
                              ┌────────────────────────────────┐
                              │        REGENERATION            │
                              │  (with improvement context)    │
                              └────────────────────────────────┘
```

## Iteration Loop Logic

```python
MAX_ITERATIONS = 3
QUALITY_THRESHOLD = 7.0
MINIMUM_THRESHOLD = 5.0

def quality_iteration_loop(state: dict) -> IterationResult:
    """Run generation-validation loop until quality passes."""

    for iteration in range(MAX_ITERATIONS):
        # Generate (or regenerate)
        if iteration == 0:
            generation_result = generate_skill(state)
        else:
            generation_result = regenerate_with_feedback(
                state,
                feedback=state["improvement_feedback"]
            )

        # Validate
        validation_result = validate_skill(generation_result)
        quality_score = validation_result.quality_score

        # Check threshold
        if quality_score >= QUALITY_THRESHOLD:
            return IterationResult(
                status="passed",
                iterations=iteration + 1,
                final_score=quality_score,
                skill_path=generation_result.path
            )

        if quality_score < MINIMUM_THRESHOLD:
            return IterationResult(
                status="rejected",
                iterations=iteration + 1,
                final_score=quality_score,
                reason="Quality too low for iteration"
            )

        # Generate improvement feedback
        state["improvement_feedback"] = generate_feedback(
            validation_result,
            iteration=iteration
        )

        log(f"Iteration {iteration + 1}: Score {quality_score:.1f} < {QUALITY_THRESHOLD}")
        log(f"Feedback: {state['improvement_feedback']['summary']}")

    # Max iterations reached
    return IterationResult(
        status="max_iterations",
        iterations=MAX_ITERATIONS,
        final_score=quality_score,
        reason=f"Could not reach {QUALITY_THRESHOLD} in {MAX_ITERATIONS} iterations"
    )
```

## Improvement Feedback Generation

### Feedback Structure

```python
def generate_feedback(validation: ValidationResult, iteration: int) -> dict:
    """Generate actionable feedback for regeneration."""

    feedback = {
        "iteration": iteration + 1,
        "current_score": validation.quality_score,
        "target_score": QUALITY_THRESHOLD,
        "gap": QUALITY_THRESHOLD - validation.quality_score,
        "summary": "",
        "improvements": [],
        "priority_order": []
    }

    # Analyze each quality dimension
    for dimension, score in validation.dimension_scores.items():
        if score < dimension_thresholds[dimension]:
            improvement = analyze_dimension_gap(
                dimension,
                score,
                validation.details[dimension]
            )
            feedback["improvements"].append(improvement)

    # Prioritize by impact
    feedback["priority_order"] = prioritize_improvements(
        feedback["improvements"],
        remaining_iterations=MAX_ITERATIONS - iteration - 1
    )

    # Generate summary
    feedback["summary"] = summarize_feedback(feedback)

    return feedback
```

### Dimension-Specific Feedback

| Dimension | Low Score Feedback |
|-----------|-------------------|
| Spec Compliance | "Fix: {missing_field}. Add required section: {section}" |
| Content Quality | "Improve clarity in {section}. Current readability: {score}" |
| User Experience | "Add example for {use_case}. Workflow step {n} unclear" |
| Maintainability | "Reduce complexity in {file}. Split {section} into subsections" |
| Security | "Address: {vulnerability}. Add input validation for {param}" |

### Feedback Example

```json
{
  "iteration": 2,
  "current_score": 6.2,
  "target_score": 7.0,
  "gap": 0.8,
  "summary": "Focus on content clarity and add missing examples",
  "improvements": [
    {
      "dimension": "content_quality",
      "current": 5.8,
      "target": 7.0,
      "issues": [
        "Workflow Step 2 lacks detail",
        "Technical terms undefined"
      ],
      "suggestions": [
        "Expand Step 2 with substeps",
        "Add glossary in references/concepts.md"
      ]
    },
    {
      "dimension": "user_experience",
      "current": 6.0,
      "target": 7.0,
      "issues": [
        "Only 1 example provided",
        "No error handling example"
      ],
      "suggestions": [
        "Add 2 more diverse examples",
        "Include error scenario example"
      ]
    }
  ],
  "priority_order": ["content_quality", "user_experience"]
}
```

## Regeneration Strategy

### Targeted Regeneration

Don't regenerate everything - only what needs improvement:

```python
def regenerate_with_feedback(state: dict, feedback: dict) -> GenerationResult:
    """Regenerate only components that need improvement."""

    # Determine what to regenerate
    targets = identify_regeneration_targets(feedback)

    # Keep unchanged components
    preserved = state["generation_result"].files.copy()

    # Regenerate targeted components
    for target in targets:
        if target["type"] == "section":
            # Regenerate specific section in SKILL.md
            regenerate_section(
                state,
                section=target["name"],
                feedback=target["feedback"]
            )
        elif target["type"] == "file":
            # Regenerate entire file
            regenerate_file(
                state,
                file_path=target["path"],
                feedback=target["feedback"]
            )
            preserved.pop(target["path"], None)

    return GenerationResult(
        files=preserved,
        regenerated=targets
    )
```

### Iteration Context Prompt

Include previous feedback in regeneration prompt:

```
## Regeneration Context (Iteration 2/3)

Previous Score: 6.2/10.0
Target Score: 7.0/10.0

### Required Improvements

1. **Content Quality** (5.8 → 7.0)
   - Expand Workflow Step 2 with detailed substeps
   - Define technical terms (API, endpoint, schema)

2. **User Experience** (6.0 → 7.0)
   - Add 2 more examples showing different use cases
   - Include an error handling example

### Preserved Content
- SKILL.md frontmatter (valid)
- references/concepts.md (score: 7.5)
- scripts/validate.sh (shellcheck passed)

### Regenerate
- SKILL.md sections: workflow, examples
- references/workflow.md (expand detail)
```

## Iteration Limits

### Why 3 Iterations?

| Iteration | Purpose |
|-----------|---------|
| 1 | Initial generation (baseline) |
| 2 | Address major gaps identified |
| 3 | Fine-tune remaining issues |

Beyond 3 iterations:
- Diminishing returns
- Likely fundamental issue with requirements
- Better to involve user for clarification

### Escape Conditions

```python
def should_continue_iteration(
    iteration: int,
    current_score: float,
    previous_score: float
) -> tuple[bool, str]:
    """Determine if iteration should continue."""

    # Max iterations reached
    if iteration >= MAX_ITERATIONS:
        return False, "max_iterations_reached"

    # Quality threshold met
    if current_score >= QUALITY_THRESHOLD:
        return False, "quality_passed"

    # Below minimum (reject)
    if current_score < MINIMUM_THRESHOLD:
        return False, "below_minimum"

    # No improvement (stuck)
    if iteration > 0 and current_score <= previous_score:
        return False, "no_improvement"

    # Score decreased significantly
    if iteration > 0 and current_score < previous_score - 0.5:
        return False, "score_regression"

    return True, "continue"
```

## User Notification

### During Iteration

```
⟳ Quality Iteration (2/3)
  Previous: 6.2/10.0
  Target: 7.0/10.0

  Improving:
  • Content clarity in workflow section
  • Adding 2 more examples

  Please wait...
```

### After Max Iterations

```
⚠ Maximum iterations reached (3/3)
  Final Score: 6.8/10.0 (target: 7.0)

  Options:
  1. Accept current quality (proceed to installation)
  2. Provide additional guidance for improvement
  3. Restart with modified requirements

  Choose (1-3):
```

## Integration Points

```python
# In main orchestration flow
def orchestrate_skill_generation(request: SkillRequest) -> OrchestrationResult:
    # ... discovery and architecture phases ...

    # Generation with quality iteration
    iteration_result = quality_iteration_loop(state)

    if iteration_result.status == "passed":
        # Proceed to installation
        return proceed_to_installation(iteration_result)

    elif iteration_result.status == "max_iterations":
        # User decision required
        return request_user_decision(iteration_result)

    else:  # rejected
        # Cannot proceed
        return report_rejection(iteration_result)
```
