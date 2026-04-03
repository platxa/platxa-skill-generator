# Eval Schema

JSON schemas for skill evaluation infrastructure. Compatible with Anthropic's skill-creator format.

## evals.json

Located at `evals/evals.json` within the skill directory. Defines test prompts and expectations for measuring skill quality.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "descriptive-eval-name",
      "prompt": "User's example prompt — realistic, detailed, like a real user would type",
      "expected_output": "Human-readable description of what success looks like",
      "files": [],
      "expectations": [
        "The output includes X",
        "The skill used script Y",
        "No errors were encountered"
      ]
    }
  ]
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `skill_name` | Yes | Must match the skill's frontmatter `name` |
| `evals[].id` | Yes | Unique integer identifier |
| `evals[].name` | No | Descriptive name (used as directory name in results) |
| `evals[].prompt` | Yes | The task prompt — realistic, specific, detailed |
| `evals[].expected_output` | Yes | Human-readable success description |
| `evals[].files` | No | Input file paths relative to skill root |
| `evals[].expectations` | No | Verifiable assertions for automated grading |

### Writing Good Eval Prompts

Prompts must be realistic — the kind of thing a real user would actually type:

**Bad** (too abstract):
```
"Format this data"
"Create a chart"
"Review my code"
```

**Good** (specific, detailed, natural):
```
"I've got a Python FastAPI project in src/api/ with about 12 endpoints. Can you review the auth middleware for security issues? I'm especially worried about the JWT validation."
```

### Writing Good Expectations

Expectations should be objectively verifiable and discriminating (they pass when the skill works, fail when it doesn't):

**Weak** (always passes):
```
"A response was generated"
"The output is not empty"
```

**Strong** (tests actual behavior):
```
"The review includes file:line references for each finding"
"Security score is calculated using the weighted formula"
"Hardcoded secrets trigger a hard-fail cap at 4.0"
```

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The review includes file:line references",
      "passed": true,
      "evidence": "Found in output: 'handler.py:42 — Hardcoded JWT secret'"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `expectations[].text` | The original expectation string |
| `expectations[].passed` | Boolean verdict |
| `expectations[].evidence` | Specific quote or description supporting the verdict |
| `summary.pass_rate` | Fraction passed (0.0 to 1.0) |

## timing.json

Wall clock timing for a run. Captured from task notification metadata.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

## benchmark.json

Aggregated results across multiple runs. Located at `<workspace>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "platxa-code-review",
    "timestamp": "2026-04-03T16:00:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05},
      "time_seconds": {"mean": 45.0, "stddev": 12.0},
      "tokens": {"mean": 3800, "stddev": 400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08},
      "time_seconds": {"mean": 32.0, "stddev": 8.0},
      "tokens": {"mean": 2100, "stddev": 300}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  }
}
```
