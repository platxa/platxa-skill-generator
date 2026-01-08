# Parallel Subagent Execution

Pattern for executing independent Task tool calls concurrently.

## When to Use Parallel Execution

Use parallel execution when:
- Multiple operations have **no dependencies** between them
- Results from one operation don't affect another
- Operations target different files or resources
- You want to minimize total execution time

## Parallel vs Sequential

### Sequential (Dependencies)

```
Discovery → Architecture → Generation
     ↓           ↓             ↓
  (depends)  (depends)    (depends)
```

When results from one phase inform the next, execute sequentially.

### Parallel (Independent)

```
┌─────────────────────────────────────┐
│         Generation Phase            │
├──────────────┬──────────────────────┤
│ SKILL.md     │ scripts/generate.sh  │
│ generation   │ generation           │
│     ↓        │        ↓             │
│   (file)     │     (file)           │
└──────────────┴──────────────────────┘
         (merge results)
```

When operations don't depend on each other, run in parallel.

## Parallel Execution Pattern

### Single Message, Multiple Tool Calls

To run operations in parallel, issue multiple Task tool calls in a **single message**.

**Key Principle**: All independent tool calls must be in the SAME response block.

```python
# Conceptual pattern (not actual code)
parallel_tasks = [
    Task(
        description="Generate SKILL.md",
        prompt="Create the SKILL.md file for {skill_name}...",
        subagent_type="general-purpose"
    ),
    Task(
        description="Generate scripts",
        prompt="Create validation scripts for {skill_name}...",
        subagent_type="general-purpose"
    ),
    Task(
        description="Generate references",
        prompt="Create reference documentation for {skill_name}...",
        subagent_type="general-purpose"
    )
]
# All three execute concurrently
results = execute_parallel(parallel_tasks)
```

## Skill Generation Parallelization

### Phase Dependencies

| Phase | Depends On | Can Parallelize |
|-------|------------|-----------------|
| Discovery | User input | No (single phase) |
| Architecture | Discovery | No (single phase) |
| Generation | Architecture | **Yes (within phase)** |
| Validation | Generation | **Yes (within phase)** |
| Installation | Validation | No (single phase) |

### Generation Phase Parallelism

These can run in parallel (no inter-dependencies):

```
┌────────────────────────────────────────────────────────┐
│                  GENERATION PHASE                       │
├────────────────┬─────────────────┬─────────────────────┤
│   SKILL.md     │    references/  │     scripts/        │
│   Generator    │    Generator    │     Generator       │
│       │        │        │        │         │           │
│       ▼        │        ▼        │         ▼           │
│  SKILL.md      │  concepts.md    │  generate.sh        │
│                │  workflow.md    │  validate.sh        │
│                │  templates.md   │                     │
└────────────────┴─────────────────┴─────────────────────┘
```

**Implementation**:

```
# Single message with 3 Task tool invocations:
1. Task: "Generate SKILL.md" → writes SKILL.md
2. Task: "Generate references" → writes references/*.md
3. Task: "Generate scripts" → writes scripts/*.sh

# All three run concurrently, results merged after completion
```

### Validation Phase Parallelism

These validators can run in parallel:

```
┌────────────────────────────────────────────────────────┐
│                 VALIDATION PHASE                        │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  Structure  │ Frontmatter │   Tokens    │   Scripts    │
│  Validator  │  Validator  │  Counter    │   Tester     │
│      │      │      │      │      │      │      │       │
│      ▼      │      ▼      │      ▼      │      ▼       │
│   result    │   result    │   result    │   result     │
└─────────────┴─────────────┴─────────────┴──────────────┘
                        │
                        ▼
                  Aggregator
```

## Background Execution

For long-running operations, use `run_in_background`:

```python
Task(
    description="Run comprehensive validation",
    prompt="Execute all validators...",
    subagent_type="general-purpose",
    run_in_background=True  # Non-blocking
)
# Continue with other work
# Later: TaskOutput(task_id="...") to get results
```

### When to Use Background

| Scenario | Use Background | Reason |
|----------|---------------|--------|
| Quick generation | No | Wait for result |
| Long validation suite | Yes | Continue other work |
| User-facing output | No | Need immediate result |
| Batch processing | Yes | Process multiple items |

## Error Handling in Parallel

### Partial Failure Strategy

When parallel tasks partially fail:

```python
results = {
    "skill_md": {"status": "success", "file": "SKILL.md"},
    "references": {"status": "success", "files": ["concepts.md"]},
    "scripts": {"status": "error", "error": "Shellcheck failed"}
}

# Strategy: Report all results, let user decide
if any(r["status"] == "error" for r in results.values()):
    report_partial_success(results)
    # Don't auto-retry - let user review errors
```

### Dependency Violation Detection

Before parallelizing, verify no hidden dependencies:

```python
def can_parallelize(task_a, task_b):
    """Check if two tasks can run in parallel."""
    # Output of A is input to B?
    if task_a.outputs & task_b.inputs:
        return False
    # Same file modified by both?
    if task_a.files & task_b.files:
        return False
    # Shared state mutation?
    if task_a.state_keys & task_b.state_keys:
        return False
    return True
```

## Best Practices

### Do

- Group independent operations in single message
- Use background for operations >30 seconds
- Merge results before proceeding to next phase
- Handle partial failures gracefully

### Don't

- Parallelize dependent operations
- Assume execution order in parallel blocks
- Ignore partial failures
- Mix parallel and sequential in confusing ways

## Example: Full Generation Phase

```
# Phase 3: Generation (parallel execution)

## Message 1: Launch parallel generators

I'll generate all skill components in parallel since they're independent:

[Task 1: Generate SKILL.md]
- subagent_type: general-purpose
- Creates: SKILL.md with frontmatter and content

[Task 2: Generate references]
- subagent_type: general-purpose
- Creates: references/concepts.md, references/workflow.md

[Task 3: Generate scripts]
- subagent_type: general-purpose
- Creates: scripts/generate.sh, scripts/validate.sh

## Results: All three complete

Merging results:
- SKILL.md: Created (487 lines, 4,230 tokens)
- references/: 2 files created (1,890 tokens total)
- scripts/: 2 files created (shellcheck passed)

Proceeding to validation phase...
```
