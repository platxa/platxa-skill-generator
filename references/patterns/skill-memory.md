# Persistent Memory Pattern

Skills can accumulate knowledge across sessions using persistent memory directories.
This is useful for analyzer skills that review the same codebase repeatedly.

## When to Use

- Skill reviews/audits the same codebase over time (learns patterns)
- Skill benefits from remembering past findings (avoids re-reporting known issues)
- Skill tracks project-specific conventions discovered during analysis

Do NOT use when:
- Skill is stateless by nature (one-shot generation, single-use validation)
- Memory would become stale quickly (rapidly changing contexts)
- Skill is a Guide type (reference knowledge, not accumulated knowledge)

## Memory Scopes

| Scope | Location | Use When |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Knowledge applies across all projects |
| `project` | `.claude/agent-memory/<name>/` | Knowledge is project-specific, shareable via git |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, NOT checked into git |

## How It Works

Memory is a subagent feature. Skills that use `context: fork` can declare memory
in their agent configuration. The subagent gets a persistent directory with a
`MEMORY.md` index file (first 200 lines auto-loaded into context).

## Integration with Generated Skills

For analyzer skills that review codebases repeatedly:

```markdown
## Workflow

### Step 0: Load Context
Read agent memory for known patterns and past findings in this codebase.

### Step N: Save Learnings
After analysis, update agent memory with:
- New patterns discovered in this codebase
- Project-specific conventions observed
- Recurring issues and their root causes
```

## Architecture Agent Integration

Recommend memory when:
- Skill type is Analyzer or Validator
- Skill will be used repeatedly on the same codebase
- Skill benefits from accumulated project knowledge

Add to blueprint:
```json
{
  "execution_context": {
    "context": "fork",
    "agent": "general-purpose"
  },
  "memory_scope": "project"
}
```
