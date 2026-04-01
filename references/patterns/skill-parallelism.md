# Skill Parallelism Pattern

When a generated skill has 3+ independent analysis dimensions, instruct it to spawn
parallel sub-agents via the Task tool instead of analyzing everything in a single pass.

## When to Apply

Use parallel sub-agents when the skill:
- Has 3+ independent analysis dimensions (e.g., quality + security + efficiency)
- Each dimension can operate on the same input independently
- Combined analysis of all dimensions would consume >50% of context window
- Each dimension benefits from a fresh, uncluttered context

Do NOT use parallel sub-agents when:
- Dimensions depend on each other (dimension B needs dimension A's output)
- The skill has only 1-2 dimensions
- The input is small enough for a single-pass analysis (<100 lines)

## Frontmatter Requirement

Skills using this pattern MUST include Task in allowed-tools:

```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Task    # Required for parallel sub-agents
```

## Workflow Structure

```
Step 1: Scope Detection (single agent — main conversation)
  Determine what to analyze: git diff, specific files, or full codebase.
  ↓
Step 2: Parallel Analysis (N agents via Task tool in SINGLE message)
  Agent 1: Dimension A → findings_a
  Agent 2: Dimension B → findings_b
  Agent 3: Dimension C → findings_c
  All launched in one message block for true concurrency.
  ↓
Step 3: Aggregation (single agent — main conversation)
  - Merge findings from all agents
  - Deduplicate: same file:line across dimensions → keep highest severity
  - Filter false positives (see finding-filtering.md)
  - Calculate weighted score
  ↓
Step 4: Report or Fix
  - Report: Structured output with per-dimension breakdown
  - Fix (optional): Apply unambiguous fixes via Edit tool
```

## Sub-Agent Prompt Template

Each sub-agent prompt MUST include:

1. **Full scope** — the file list or diff content (pass inline, don't make the agent re-read)
2. **Single dimension focus** — analyze ONLY this dimension
3. **Scoring rubric** — the specific criteria and weights for this dimension
4. **Output format** — structured findings the aggregation step can parse

```markdown
## SKILL.md Workflow Example

### Step 2: Parallel Analysis

Launch all dimension agents in a single message:

**Agent 1: Code Quality**
Use the Task tool:
  description: "Analyze code quality"
  prompt: |
    Analyze these files for CODE QUALITY only:

    {file_list_or_diff}

    Evaluate:
    - Cyclomatic complexity per function (target: <10)
    - Function length (target: <50 lines)
    - Naming clarity and consistency
    - SOLID principle adherence

    Output findings as:
    - file:line — severity (CRITICAL/HIGH/MEDIUM/LOW) — description

**Agent 2: Security**
Use the Task tool:
  description: "Analyze security"
  prompt: |
    Analyze these files for SECURITY only:

    {file_list_or_diff}

    Evaluate:
    - Hardcoded secrets (auto-fail if found)
    - SQL/command injection patterns
    - Input validation at boundaries

    Output findings as:
    - file:line — severity — description

**Agent 3: Efficiency**
Use the Task tool:
  description: "Analyze efficiency"
  prompt: |
    Analyze these files for EFFICIENCY only:

    {file_list_or_diff}

    Evaluate:
    - N+1 query patterns
    - Unnecessary allocations in loops
    - Blocking I/O in async contexts

    Output findings as:
    - file:line — severity — description
```

## Aggregation Rules

After all agents complete, the main conversation aggregates:

### Deduplication
- Same file:line in multiple agents → keep the highest-severity instance
- Same pattern across multiple files → group and report once with file count
- Same root cause producing multiple symptoms → report the root cause only

### False Positive Filtering
- Skip findings in auto-generated files (*.pb.go, *.generated.ts, migrations/)
- Skip findings in vendor/third-party code (node_modules/, vendor/)
- Skip findings in test fixtures with intentional bad patterns
- Skip pattern matches in comments or strings (not actual code)

### Weighted Scoring
```
overall = sum(dimension_score * dimension_weight)
```
Each dimension score: start at 10.0, deduct per finding by severity.

## Architecture Agent Integration

The architecture agent should recommend this pattern when:
- Skill type is Analyzer
- Blueprint has 3+ analysis categories/dimensions
- Each category is independently evaluable

Add to blueprint output:
```json
{
  "execution_sophistication": "advanced",
  "parallel_dimensions": ["quality", "security", "efficiency"],
  "requires_task_tool": true
}
```

## Token Budget Consideration

Parallel agents reduce main-conversation context pressure but increase total token usage.
Each sub-agent gets its own context window. The input (diff or file list) is duplicated
across agents. This is acceptable because:
- Each agent analyzes with fresh, focused context (better quality)
- Wall-clock time decreases (agents run concurrently)
- Main conversation stays clean for aggregation and reporting
