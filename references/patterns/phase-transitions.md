# Phase Transition Rules

Entry and exit criteria for each workflow phase.

## Phase 1: Initialize

### Entry Criteria
- [ ] User invoked `/skill-generator`
- [ ] No active session (or user chose to start new)

### Required Actions
1. Create session state file
2. Ask user for skill description
3. Ask user for target users

### Exit Criteria
- [ ] `input.description` is non-empty
- [ ] `input.target_users` is non-empty
- [ ] State file created with `phase: "init"`

### Next Phase
→ **Discovery**

---

## Phase 2: Discovery

### Entry Criteria
- [ ] Phase 1 complete
- [ ] User input captured in state

### Required Actions
1. Launch Task tool with `subagent_type="Explore"`
2. Web search for domain best practices
3. Analyze existing skills in `~/.claude/skills/`
4. Identify domain concepts and workflows
5. Calculate sufficiency score

### Exit Criteria
- [ ] `discovery.status` = "complete"
- [ ] `discovery.findings` populated
- [ ] `discovery.sufficiency_score` calculated

### Decision Point
```
IF sufficiency_score >= 0.8:
    → Architecture
ELSE IF gaps exist:
    → Clarify (ask user)
    → Return to Discovery after answers
ELSE:
    → Architecture (with warnings)
```

### Next Phase
→ **Architecture** (or **Clarify** if gaps)

---

## Phase 3: Architecture

### Entry Criteria
- [ ] Discovery complete
- [ ] Sufficiency score acceptable (≥0.6)
- [ ] No blocking gaps remain

### Required Actions
1. Classify skill type (Builder/Guide/Automation/Analyzer/Validator)
2. Determine directory structure
3. Plan SKILL.md sections
4. Design scripts and references
5. Generate architecture blueprint JSON

### Exit Criteria
- [ ] `architecture.skill_type` set
- [ ] `architecture.skill_name` valid (hyphen-case, ≤64 chars)
- [ ] `architecture.directories` defined
- [ ] `architecture.sections` defined
- [ ] Blueprint JSON generated

### Validation
```
ASSERT skill_name matches ^[a-z][a-z0-9-]*$
ASSERT skill_name.length <= 64
ASSERT directories is non-empty array
ASSERT sections includes ["Overview", "Workflow"]
```

### Next Phase
→ **Generation**

---

## Phase 4: Generation

### Entry Criteria
- [ ] Architecture blueprint complete
- [ ] Output directory created
- [ ] Templates available in `references/templates/`

### Required Actions
1. Generate SKILL.md with YAML frontmatter
2. Generate scripts (if specified)
3. Generate reference files (if specified)
4. Make scripts executable
5. Record artifacts in state

### Exit Criteria
- [ ] SKILL.md exists in output directory
- [ ] All planned scripts created
- [ ] All planned references created
- [ ] `generation.artifacts` populated
- [ ] `generation.status` = "complete"

### Artifact Recording
```json
{
  "artifacts": [
    {"path": "SKILL.md", "type": "skill_md", "size_bytes": 4200},
    {"path": "scripts/validate.sh", "type": "script", "size_bytes": 1500}
  ]
}
```

### Next Phase
→ **Validation**

---

## Phase 5: Validation

### Entry Criteria
- [ ] Generation complete
- [ ] All artifacts exist on disk
- [ ] Validation script available

### Required Actions
1. Run `scripts/validate-skill.sh`
2. Check YAML frontmatter validity
3. Verify name constraints (hyphen-case, ≤64 chars)
4. Verify description length (≤1024 chars)
5. Check for placeholder content
6. Calculate quality score

### Exit Criteria
- [ ] `validation.quality_score` calculated
- [ ] `validation.errors` populated (may be empty)
- [ ] `validation.warnings` populated (may be empty)
- [ ] `validation.checks` all evaluated

### Decision Point
```
IF quality_score >= 7.0 AND errors.length == 0:
    validation.status = "passed"
    → Installation
ELSE:
    validation.status = "failed"
    → Rework (return to Generation with feedback)
```

### Next Phase
→ **Installation** (if passed) or **Generation** (if failed)

---

## Phase 6: Installation

### Entry Criteria
- [ ] Validation passed (score ≥7.0)
- [ ] Zero critical errors
- [ ] User confirmed proceed

### Required Actions
1. Ask user: "User skill or Project skill?"
2. Determine target path
3. Check for existing skill (offer overwrite)
4. Copy all files to target
5. Verify installation

### Exit Criteria
- [ ] `installation.location` set ("user" or "project")
- [ ] `installation.path` set to actual path
- [ ] All files copied successfully
- [ ] `installation.status` = "complete"

### Installation Paths
| Choice | Path |
|--------|------|
| User | `~/.claude/skills/{skill-name}/` |
| Project | `.claude/skills/{skill-name}/` |

### Next Phase
→ **Complete**

---

## Phase 7: Complete

### Entry Criteria
- [ ] Installation successful
- [ ] All files in place

### Required Actions
1. Display success message
2. Show skill usage instructions
3. Clean up temporary files
4. Archive or delete state file

### Exit Criteria
- [ ] User notified of completion
- [ ] Temporary directory cleaned
- [ ] State file removed (or archived)

### Final State
```json
{
  "phase": "complete",
  "progress": {
    "phases_complete": 6,
    "total_phases": 6,
    "percent": 100
  }
}
```

---

## Error Recovery Rules

| From Phase | Error Type | Recovery Action |
|------------|------------|-----------------|
| Discovery | Timeout | Retry with simpler queries |
| Discovery | No results | Ask user for more context |
| Architecture | Invalid name | Suggest valid alternatives |
| Generation | Write failed | Check permissions, retry |
| Validation | Score < 7 | Show issues, go to Rework |
| Installation | Path exists | Ask to overwrite or rename |

## Rollback Rules

| Current Phase | Rollback To | Condition |
|---------------|-------------|-----------|
| Discovery | Init | User requests restart |
| Architecture | Discovery | Need more research |
| Generation | Architecture | Wrong structure |
| Validation | Generation | Need to regenerate |
| Installation | Validation | User cancels |
