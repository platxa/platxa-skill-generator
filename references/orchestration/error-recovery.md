# Error Recovery Workflow

Pattern for recovering from failures without losing progress.

## State Persistence

### Checkpoint Structure

Each phase saves state to enable recovery:

```json
{
  "skill_name": "api-doc-generator",
  "current_phase": "generation",
  "completed_phases": ["init", "discovery", "architecture"],
  "phase_outputs": {
    "discovery": {
      "completed_at": "2024-01-15T10:30:00Z",
      "skill_type": "builder",
      "domain": "API documentation",
      "requirements": ["openapi parsing", "markdown output"]
    },
    "architecture": {
      "completed_at": "2024-01-15T10:32:00Z",
      "structure": {
        "skill_md_sections": ["overview", "workflow", "examples"],
        "references": ["openapi-spec.md", "markdown-templates.md"],
        "scripts": ["generate.sh", "validate.sh"]
      }
    }
  },
  "failed_phase": null,
  "error_log": []
}
```

### Checkpoint Location

```
.claude/skill-generator/
├── state.json              # Current generation state
├── checkpoints/
│   ├── discovery.json      # Discovery phase snapshot
│   ├── architecture.json   # Architecture phase snapshot
│   └── generation.json     # Generation phase snapshot (partial)
└── output/
    └── {skill-name}/       # Generated files (in progress)
```

## Error Categories

### Recoverable Errors

| Category | Example | Recovery Strategy |
|----------|---------|-------------------|
| Network | API timeout | Retry with backoff |
| Validation | Token limit exceeded | Adjust and regenerate |
| Tool failure | Write permission denied | Fix permissions, retry |
| User input | Ambiguous requirement | Request clarification |

### Non-Recoverable Errors

| Category | Example | Action |
|----------|---------|--------|
| Invalid spec | Skill name reserved | Restart with valid input |
| Conflicting requirements | Incompatible tools | Restart with clarification |
| System failure | Disk full | Fix system, restart |

## Recovery Workflow

### Phase Failure Detection

```python
class PhaseResult:
    status: Literal["success", "partial", "failed"]
    outputs: dict
    errors: list[str]
    recoverable: bool
    checkpoint: dict

def execute_phase(phase: str, state: dict) -> PhaseResult:
    """Execute phase with error handling."""
    try:
        # Save pre-execution checkpoint
        save_checkpoint(phase, state, status="started")

        # Execute phase logic
        result = PHASE_HANDLERS[phase](state)

        # Save success checkpoint
        save_checkpoint(phase, state, status="completed", outputs=result)

        return PhaseResult(
            status="success",
            outputs=result,
            errors=[],
            recoverable=True,
            checkpoint=state
        )
    except RecoverableError as e:
        save_checkpoint(phase, state, status="failed", error=str(e))
        return PhaseResult(
            status="failed",
            outputs={},
            errors=[str(e)],
            recoverable=True,
            checkpoint=state
        )
    except FatalError as e:
        return PhaseResult(
            status="failed",
            outputs={},
            errors=[str(e)],
            recoverable=False,
            checkpoint=None
        )
```

### Retry Logic

```python
def retry_phase(phase: str, max_retries: int = 3) -> PhaseResult:
    """Retry failed phase with exponential backoff."""
    state = load_checkpoint(phase)

    for attempt in range(max_retries):
        result = execute_phase(phase, state)

        if result.status == "success":
            return result

        if not result.recoverable:
            raise NonRecoverableError(result.errors)

        # Exponential backoff
        wait_time = 2 ** attempt
        log(f"Retry {attempt + 1}/{max_retries} in {wait_time}s")
        sleep(wait_time)

    raise MaxRetriesExceeded(phase, max_retries)
```

### Partial Progress Recovery

When generation phase partially completes:

```python
def recover_generation_phase(state: dict) -> dict:
    """Recover from partial generation failure."""
    checkpoint = load_checkpoint("generation")

    # What was successfully generated?
    completed = checkpoint.get("completed_files", [])
    pending = checkpoint.get("pending_files", [])
    failed = checkpoint.get("failed_files", [])

    # Keep completed, retry failed + pending
    for file_spec in failed + pending:
        try:
            generate_file(file_spec, state)
            completed.append(file_spec)
        except Exception as e:
            failed.append({"spec": file_spec, "error": str(e)})

    return {
        "completed": completed,
        "failed": failed,
        "success": len(failed) == 0
    }
```

## Recovery Commands

### Check Current State

```bash
# Show current generation state
skill-generator status

# Output:
# Skill: api-doc-generator
# Phase: generation (FAILED)
# Completed: init, discovery, architecture
# Error: Token limit exceeded in SKILL.md
# Recovery: Run 'skill-generator retry' to continue
```

### Retry Failed Phase

```bash
# Retry the failed phase
skill-generator retry

# Retry with modifications
skill-generator retry --reduce-tokens

# Retry specific file
skill-generator retry --file SKILL.md
```

### Rollback to Checkpoint

```bash
# Rollback to previous phase
skill-generator rollback --to architecture

# Rollback and modify inputs
skill-generator rollback --to discovery --modify
```

### Resume from Checkpoint

```bash
# Resume after system recovery
skill-generator resume

# Resume with fresh context
skill-generator resume --reload-context
```

## Error Recovery Matrix

| Phase | Error Type | Recovery Action |
|-------|------------|-----------------|
| Discovery | User unclear | AskUserQuestion for clarification |
| Discovery | Invalid type | Show valid types, retry |
| Architecture | Conflict | Present options, user chooses |
| Architecture | Missing info | Return to discovery |
| Generation | Token exceeded | Reduce content, regenerate |
| Generation | Write failed | Check permissions, retry |
| Generation | Partial fail | Keep successful, retry failed |
| Validation | Structure fail | Regenerate affected files |
| Validation | Quality fail | Present issues, user decides |
| Installation | Path conflict | Offer rename or overwrite |
| Installation | Permission denied | Request elevated permissions |

## State Transitions

```
     ┌─────────────────────────────────────────┐
     │                                         │
     ▼                                         │
  [Phase N] ──success──▶ [Phase N+1]          │
     │                                         │
     │ failure                                 │
     ▼                                         │
  [Error Handler]                              │
     │                                         │
     ├── recoverable ──▶ [Retry Phase N] ─────┘
     │
     ├── needs_input ──▶ [User Prompt] ──▶ [Retry Phase N]
     │
     └── fatal ──▶ [Rollback] ──▶ [Phase N-1 or Exit]
```

## Best Practices

### Checkpoint Frequency

- Save checkpoint at phase boundaries
- Save partial progress for long operations
- Include enough state to resume without re-prompting user

### Error Messages

Provide actionable error messages:

```python
# Bad
"Generation failed"

# Good
"Generation failed: SKILL.md exceeded 5000 token limit (actual: 5,847).
Suggestion: Reduce workflow steps or move detailed examples to references/.
Run 'skill-generator retry --reduce-tokens' to auto-optimize."
```

### Idempotent Operations

Design operations to be safely retried:

```python
def write_file_idempotent(path: str, content: str) -> None:
    """Write file only if content changed."""
    if path_exists(path):
        existing = read_file(path)
        if existing == content:
            log(f"Skipping {path} (unchanged)")
            return
    write_file(path, content)
    log(f"Wrote {path}")
```

### User Communication

Keep user informed during recovery:

```
⚠ Generation phase failed
  Error: Token limit exceeded in SKILL.md (5,847 > 5,000)

Automatic recovery options:
  1. [Recommended] Reduce content and regenerate
  2. Move examples to references/examples.md
  3. Split into multiple skills

Choose option (1-3) or 'manual' for custom fix:
```
