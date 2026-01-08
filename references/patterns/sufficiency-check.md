# Sufficiency Check (Phase 2)

Evaluate research completeness and identify gaps before proceeding.

## Scoring Rubric

### Coverage Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Authority | 20% | Has official/authoritative sources |
| Concepts | 15% | Core domain terms defined |
| Practices | 15% | Best practices documented |
| Workflow | 20% | Primary process understood |
| Tools | 10% | Required tools identified |
| Examples | 10% | Real examples found |
| Completeness | 10% | No critical gaps |

### Scoring Each Dimension

#### Authority (0-1.0)
```
1.0: Official specification + official docs
0.8: Official docs only
0.6: Major vendor docs (e.g., AWS, Google)
0.4: Community docs only
0.2: Blog posts only
0.0: No authoritative sources
```

#### Concepts (0-1.0)
```
1.0: ≥10 concepts with clear definitions
0.8: 7-9 concepts defined
0.6: 5-6 concepts defined
0.4: 3-4 concepts defined
0.2: 1-2 concepts defined
0.0: No concepts identified
```

#### Practices (0-1.0)
```
1.0: ≥5 best practices with rationale
0.8: 4 practices documented
0.6: 3 practices documented
0.4: 2 practices documented
0.2: 1 practice documented
0.0: No practices found
```

#### Workflow (0-1.0)
```
1.0: Complete workflow with all steps clear
0.8: Main steps clear, minor gaps
0.6: Core process understood, details fuzzy
0.4: General idea, missing steps
0.2: Vague understanding only
0.0: Workflow not understood
```

#### Tools (0-1.0)
```
1.0: All required Claude tools + external tools identified
0.8: Required Claude tools identified
0.6: Some tools identified
0.4: Few tools known
0.2: Tools unclear
0.0: No tool information
```

#### Examples (0-1.0)
```
1.0: ≥3 real-world examples with code
0.8: 2 examples found
0.6: 1 good example
0.4: Partial examples only
0.2: Trivial examples
0.0: No examples found
```

#### Completeness (0-1.0)
```
1.0: All questions answerable
0.8: Minor unknowns (non-blocking)
0.6: Some gaps (workaround possible)
0.4: Significant gaps
0.2: Major gaps
0.0: Critical information missing
```

## Score Calculation

```
total_score = (
    authority * 0.20 +
    concepts * 0.15 +
    practices * 0.15 +
    workflow * 0.20 +
    tools * 0.10 +
    examples * 0.10 +
    completeness * 0.10
)
```

## Decision Thresholds

| Score Range | Status | Action |
|-------------|--------|--------|
| 0.80 - 1.00 | Sufficient | Proceed to Architecture |
| 0.60 - 0.79 | Partial | Proceed with warnings |
| 0.40 - 0.59 | Insufficient | Ask 1-2 clarifying questions |
| 0.00 - 0.39 | Critical | Ask user for guidance |

## Gap Identification

### Gap Detection Rules

```markdown
IF authority < 0.6:
    gap: "No official documentation found"
    question: "Do you know the official docs URL for {domain}?"

IF concepts < 0.6:
    gap: "Core concepts unclear"
    question: "What are the main terms/concepts in {domain}?"

IF practices < 0.6:
    gap: "Best practices unknown"
    question: "What are the key do's and don'ts for {domain}?"

IF workflow < 0.6:
    gap: "Process not understood"
    question: "What are the typical steps when {doing_task}?"

IF tools < 0.6:
    gap: "Required tools unknown"
    question: "What tools/libraries do you use for {domain}?"

IF examples < 0.4:
    gap: "No examples found"
    question: "Can you point to an example project using {domain}?"
```

### Gap Priority

| Priority | Criteria |
|----------|----------|
| Critical | workflow < 0.4 OR authority < 0.4 |
| High | concepts < 0.6 OR practices < 0.6 |
| Medium | tools < 0.6 OR examples < 0.4 |
| Low | completeness < 0.8 |

## Sufficiency Report

### Output Format

```json
{
  "sufficiency": {
    "total_score": 0.75,
    "status": "partial",
    "dimensions": {
      "authority": {"score": 0.8, "notes": "Official docs found"},
      "concepts": {"score": 0.6, "notes": "5 concepts defined"},
      "practices": {"score": 0.8, "notes": "4 practices documented"},
      "workflow": {"score": 0.6, "notes": "Main steps clear"},
      "tools": {"score": 1.0, "notes": "All tools identified"},
      "examples": {"score": 0.6, "notes": "1 good example"},
      "completeness": {"score": 0.7, "notes": "Minor unknowns"}
    },
    "gaps": [
      {
        "dimension": "concepts",
        "severity": "medium",
        "description": "Some advanced concepts unclear",
        "question": null
      }
    ],
    "blocking_gaps": [],
    "recommendation": "proceed_with_warnings"
  }
}
```

### Decision Logic

```markdown
FUNCTION make_decision(report):
    IF report.total_score >= 0.8:
        RETURN "proceed"

    IF report.blocking_gaps.length > 0:
        RETURN "ask_user", report.blocking_gaps[0].question

    IF report.total_score >= 0.6:
        RETURN "proceed_with_warnings", report.gaps

    IF report.gaps.length <= 2:
        questions = [gap.question for gap in report.gaps if gap.question]
        RETURN "ask_user", questions

    RETURN "ask_user_guidance"
```

## Iterative Improvement

### After User Clarification

```markdown
1. Receive user answers
2. Incorporate new information into findings
3. Re-run sufficiency check
4. IF score improved to >= 0.6:
       Proceed to Architecture
   ELSE:
       Ask for more guidance
```

### Maximum Iterations

```markdown
Max clarification rounds: 2

IF after 2 rounds score < 0.6:
    Warn user: "Limited research available"
    Offer: "Proceed anyway" or "Cancel"
```

## Integration

### In Workflow

```markdown
Discovery Phase:
    1. Automatic research
    2. → Sufficiency check ←
    3. IF sufficient: Architecture
       ELSE: Clarification → Loop back to check
```

### State Update

```json
{
  "discovery": {
    "status": "complete",
    "sufficiency_score": 0.75,
    "sufficiency_status": "partial",
    "gaps_identified": 1,
    "clarifications_needed": false
  }
}
```
