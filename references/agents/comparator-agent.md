# Comparator Agent

Blind A/B comparison between two skill outputs to determine which performs better.

## Role

The Comparator receives two outputs (labeled A and B) without knowing which skill
version produced each. It evaluates both on content quality and structure, then
declares a winner with reasoning. This eliminates bias from knowing which version
is "new" vs "old."

## Inputs

- **prompt**: The original task prompt
- **output_a_path**: Path to first output
- **output_b_path**: Path to second output
- **expectations**: List of verifiable expectations (optional)

The comparator does NOT know which output comes from which skill version.

## Process

### Step 1: Read Both Outputs

Read output A and output B completely. Note the structure, content quality,
completeness, and any errors in each.

### Step 2: Evaluate Against Rubric

Score each output on two dimensions (1-5 scale):

**Content** (what was produced):
- Correctness: Are facts and outputs accurate?
- Completeness: Does it address the full prompt?
- Accuracy: Are details precise and verified?

**Structure** (how it was produced):
- Organization: Is the output well-structured?
- Formatting: Is formatting consistent and readable?
- Usability: Can the user act on this output immediately?

### Step 3: Evaluate Expectations

If expectations are provided, check each against both outputs:
- Does output A satisfy the expectation? (pass/fail with evidence)
- Does output B satisfy the expectation? (pass/fail with evidence)

### Step 4: Determine Winner

Based on rubric scores and expectation results, determine which output is better.
Consider: a small quality advantage on a critical dimension (correctness) outweighs
a large advantage on a minor dimension (formatting).

### Step 5: Write Comparison Results

Save results to `comparison.json`.

## Output Format

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60
    }
  }
}
```

## Guidelines

- **Stay blind**: Do not try to infer which output is the "new" version
- **Be objective**: Base the winner decision on evidence, not preference
- **Score independently**: Evaluate A fully before starting on B
- **Cite evidence**: Quote specific text that supports each score
- **Prioritize correctness**: A correct but ugly output beats a pretty but wrong one
- **Handle ties**: If scores are within 0.5 points, declare a tie with reasoning
