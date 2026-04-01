# Worktree Isolation Pattern

When a skill spawns parallel sub-agents that ALL modify files, use `isolation: "worktree"`
to give each agent its own git worktree. This prevents merge conflicts between agents.

## When to Use

- Skill spawns 2+ parallel agents via Task tool
- Each agent modifies files (not read-only analysis)
- Changes are independent and non-overlapping
- A git repository is available

Do NOT use when:
- Agents are read-only (analysis, review) — no conflict possible
- Only one agent modifies files at a time (sequential)
- Not in a git repository

## How It Works

```
Agent(
  description="Fix module A",
  prompt="...",
  isolation="worktree"
)
```

1. Claude Code creates a temporary git worktree (isolated branch + working copy)
2. The agent operates in this isolated copy
3. On completion:
   - If agent made changes → worktree path and branch returned in result
   - If no changes → worktree auto-cleaned

## Example: Batch Modification Skill

```markdown
## Workflow

### Step 1: Plan units
Decompose the task into independent units (one per file or module).

### Step 2: Execute in parallel
For each unit, launch an agent in an isolated worktree:

Use the Task tool for each unit (all in a single message):
  description: "Fix unit 1"
  isolation: "worktree"
  prompt: "Apply change X to file Y. Run tests. Commit if passing."

### Step 3: Merge results
Review each agent's changes. Create PRs or merge branches.
```

## Architecture Agent Integration

Recommend `isolation: "worktree"` when:
- `execution_sophistication: "advanced"`
- Parallel agents modify files (not just analyze)
- Blueprint shows 3+ independent modification units

This is the pattern `/batch` uses: 5-30 worktree agents, each implementing
one unit, running tests, and opening a PR.
