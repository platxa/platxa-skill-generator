# Skill Type Decision Tree

Algorithm for classifying skills into one of 5 types.

## Decision Tree

```
                    ┌─────────────────────────────┐
                    │ Does the skill CREATE new   │
                    │ files, code, or artifacts?  │
                    └─────────────────────────────┘
                           │              │
                          YES             NO
                           │              │
                           ▼              ▼
                    ┌──────────┐   ┌─────────────────────────────┐
                    │ BUILDER  │   │ Does the skill CHECK or     │
                    └──────────┘   │ VERIFY against rules?       │
                                   └─────────────────────────────┘
                                          │              │
                                         YES             NO
                                          │              │
                                          ▼              ▼
                              ┌─────────────────────────────────────┐
                              │ Does it return PASS/FAIL result?    │
                              └─────────────────────────────────────┘
                                     │              │
                                    YES             NO
                                     │              │
                                     ▼              ▼
                              ┌───────────┐  ┌───────────┐
                              │ VALIDATOR │  │ ANALYZER  │
                              └───────────┘  └───────────┘
                                                  │
                                                  │ (if NO to checking)
                                                  ▼
                                   ┌─────────────────────────────┐
                                   │ Does the skill TEACH or     │
                                   │ EXPLAIN concepts?           │
                                   └─────────────────────────────┘
                                          │              │
                                         YES             NO
                                          │              │
                                          ▼              ▼
                                   ┌──────────┐  ┌────────────┐
                                   │  GUIDE   │  │ AUTOMATION │
                                   └──────────┘  └────────────┘
```

## Classification Questions

Answer these questions in order to determine skill type:

### Question 1: Output Type
**"What does the skill produce?"**

| Answer | Likely Type |
|--------|-------------|
| New files, code, documents | Builder |
| Reports, metrics, analysis | Analyzer |
| Pass/fail verdicts | Validator |
| Knowledge, explanations | Guide |
| Changed state, completed tasks | Automation |

### Question 2: Primary Action
**"What verb best describes the skill?"**

| Verb | Type |
|------|------|
| Create, Generate, Build, Scaffold | **Builder** |
| Teach, Explain, Guide, Help | **Guide** |
| Run, Execute, Process, Automate | **Automation** |
| Inspect, Audit, Measure, Analyze | **Analyzer** |
| Validate, Check, Verify, Enforce | **Validator** |

### Question 3: User Interaction
**"How does the user interact?"**

| Interaction | Type |
|-------------|------|
| Requests something to be made | Builder |
| Asks questions, learns | Guide |
| Triggers a task to run | Automation |
| Wants to understand something | Analyzer |
| Wants to know if something is correct | Validator |

## Scoring Matrix

Score each type (0-3) based on fit. Highest score wins.

| Signal | B | G | Au | An | V |
|--------|---|---|----|----|---|
| Creates new files | 3 | 0 | 1 | 0 | 0 |
| Modifies existing files | 2 | 0 | 2 | 0 | 0 |
| Read-only operation | 0 | 2 | 1 | 3 | 3 |
| Has pass/fail outcome | 0 | 0 | 1 | 1 | 3 |
| Produces metrics/scores | 0 | 0 | 0 | 3 | 2 |
| Interactive Q&A | 1 | 3 | 0 | 1 | 0 |
| Runs automatically | 0 | 0 | 3 | 1 | 2 |
| Uses templates | 3 | 1 | 1 | 0 | 0 |
| Enforces rules | 0 | 0 | 0 | 1 | 3 |
| Educational purpose | 0 | 3 | 0 | 1 | 0 |

**B**=Builder, **G**=Guide, **Au**=Automation, **An**=Analyzer, **V**=Validator

## Examples by Type

### Builder
- "Generate API documentation"
- "Create React component"
- "Scaffold new project"
- "Build database migrations"

### Guide
- "Teach Git workflow"
- "Explain authentication patterns"
- "Help with TypeScript migration"
- "Guide through deployment"

### Automation
- "Format code on save"
- "Update dependencies weekly"
- "Sync configuration files"
- "Run linting pipeline"

### Analyzer
- "Analyze code complexity"
- "Profile performance bottlenecks"
- "Audit security vulnerabilities"
- "Measure test coverage"

### Validator
- "Validate API schema"
- "Check style guide compliance"
- "Verify security requirements"
- "Enforce naming conventions"

## Hybrid Classification

Some skills span multiple types. Choose **primary** type:

### Builder + Validator
"Generate component with validation"
→ Primary: **Builder** (main output is created artifact)
→ Secondary: Validation happens on output

### Analyzer + Guide
"Analyze code and explain issues"
→ Primary: **Analyzer** (main action is inspection)
→ Secondary: Explanations are educational

### Automation + Validator
"Auto-fix linting errors"
→ Primary: **Automation** (runs automatically)
→ Secondary: Uses validation rules

## Decision Algorithm

```
function classifySkillType(description, discovery):
    scores = {Builder: 0, Guide: 0, Automation: 0, Analyzer: 0, Validator: 0}

    # Check for creation verbs
    if matches(description, ["create", "generate", "build", "scaffold"]):
        scores.Builder += 3

    # Check for teaching verbs
    if matches(description, ["teach", "explain", "guide", "help", "learn"]):
        scores.Guide += 3

    # Check for automation verbs
    if matches(description, ["run", "execute", "automate", "process"]):
        scores.Automation += 3

    # Check for analysis verbs
    if matches(description, ["analyze", "inspect", "audit", "measure"]):
        scores.Analyzer += 3

    # Check for validation verbs
    if matches(description, ["validate", "check", "verify", "enforce"]):
        scores.Validator += 3

    # Check discovery findings
    if discovery.outputs_files:
        scores.Builder += 2
    if discovery.has_pass_fail:
        scores.Validator += 2
    if discovery.produces_metrics:
        scores.Analyzer += 2

    return max(scores, key=scores.get)
```

## Confidence Levels

| Score Difference | Confidence |
|------------------|------------|
| Winner > 2nd by 3+ | High |
| Winner > 2nd by 1-2 | Medium |
| Tie or < 1 difference | Low (ask user) |

If confidence is **Low**, ask user:
> "This skill could be a {Type1} or {Type2}. Which fits better?"
