# Workflow State Machine

Logic for managing skill creation workflow phases.

## State Diagram

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    ▼                                         │
┌──────┐     ┌───────────┐     ┌──────────────┐     ┌────────┴────────┐
│ IDLE │────▶│   INIT    │────▶│  DISCOVERY   │────▶│  ARCHITECTURE   │
└──────┘     └───────────┘     └──────────────┘     └─────────────────┘
                                      │                      │
                                      │ (gaps found)         │
                                      ▼                      ▼
                              ┌──────────────┐     ┌─────────────────┐
                              │  CLARIFY     │     │   GENERATION    │
                              └──────────────┘     └─────────────────┘
                                      │                      │
                                      │ (answered)           │
                                      └──────────┬───────────┘
                                                 │
                                                 ▼
                                      ┌─────────────────┐
                                      │   VALIDATION    │
                                      └─────────────────┘
                                           │       │
                              (score < 7)  │       │  (score ≥ 7)
                                           ▼       ▼
                              ┌────────────┐     ┌─────────────────┐
                              │  REWORK    │     │  INSTALLATION   │
                              └────────────┘     └─────────────────┘
                                    │                    │
                                    │                    ▼
                                    │            ┌─────────────────┐
                                    └───────────▶│    COMPLETE     │
                                                 └─────────────────┘
```

## Phase Transitions

### IDLE → INIT

**Trigger**: User invokes `/skill-generator`

**Actions**:
1. Generate session ID: `skill_{timestamp}_{random}`
2. Create state file: `.claude/skill_creation_state.json`
3. Set phase: "init"

**State Update**:
```json
{
  "session_id": "skill_20260107_143022_a1b2c3",
  "phase": "init",
  "created_at": "2026-01-07T14:30:22Z"
}
```

---

### INIT → DISCOVERY

**Trigger**: User provides description and target users

**Actions**:
1. Store user input in state
2. Launch discovery subagent via Task tool
3. Set phase: "discovery"

**State Update**:
```json
{
  "phase": "discovery",
  "input": {
    "description": "...",
    "target_users": "..."
  },
  "discovery": {
    "status": "in_progress"
  }
}
```

---

### DISCOVERY → ARCHITECTURE (or CLARIFY)

**Trigger**: Discovery subagent completes

**Decision Logic**:
```
IF sufficiency_score >= 0.8:
    → ARCHITECTURE
ELSE IF gaps.length > 0:
    → CLARIFY
ELSE:
    → ARCHITECTURE (with warnings)
```

**Actions**:
1. Store discovery findings
2. Evaluate sufficiency score
3. If gaps exist, prepare clarification questions
4. Set phase accordingly

---

### CLARIFY → DISCOVERY

**Trigger**: User answers clarification questions

**Actions**:
1. Store answers in state
2. Re-run discovery with new context
3. Set phase: "discovery"

---

### ARCHITECTURE → GENERATION

**Trigger**: Architecture blueprint generated

**Actions**:
1. Store architecture decisions
2. Create output directory
3. Set phase: "generation"

**State Update**:
```json
{
  "phase": "generation",
  "architecture": {
    "status": "complete",
    "skill_type": "Builder",
    "skill_name": "my-skill"
  }
}
```

---

### GENERATION → VALIDATION

**Trigger**: All files generated

**Actions**:
1. Record generated artifacts
2. Launch validation checks
3. Set phase: "validation"

---

### VALIDATION → INSTALLATION (or REWORK)

**Trigger**: Validation complete

**Decision Logic**:
```
IF quality_score >= 7.0 AND errors.length == 0:
    → INSTALLATION
ELSE:
    → REWORK
```

---

### REWORK → GENERATION

**Trigger**: User approves regeneration

**Actions**:
1. Clear previous artifacts
2. Apply fixes based on validation feedback
3. Set phase: "generation"

---

### INSTALLATION → COMPLETE

**Trigger**: User selects location and confirms

**Actions**:
1. Copy files to target location
2. Verify installation
3. Clean up temporary files
4. Set phase: "complete"

---

## State File Management

### Reading State

```markdown
At start of each interaction:
1. Check if `.claude/skill_creation_state.json` exists
2. If exists, read and parse
3. Resume from stored phase
4. If not exists, start fresh (IDLE)
```

### Writing State

```markdown
After each phase transition:
1. Update phase field
2. Update relevant section (discovery, architecture, etc.)
3. Update timestamps
4. Write to `.claude/skill_creation_state.json`
```

### State Cleanup

```markdown
On COMPLETE or user cancellation:
1. Optionally archive state file
2. Remove `.claude/skill_creation_state.json`
3. Log completion/cancellation
```

## Error Handling

### Recoverable Errors

| Error | Recovery |
|-------|----------|
| Discovery timeout | Retry with simpler queries |
| Generation partial | Resume from last artifact |
| Validation failed | Go to REWORK |

### Unrecoverable Errors

| Error | Action |
|-------|--------|
| State file corrupted | Start fresh, warn user |
| Missing required input | Return to INIT |
| User cancellation | Clean up, exit gracefully |

## Concurrency

**Rule**: Only one skill creation session per project at a time.

Check at start:
```markdown
IF state file exists AND phase != "complete":
    Ask user: "Resume existing session or start new?"
```
