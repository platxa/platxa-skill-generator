# Context Handoff Protocol

How artifacts flow between workflow phases.

## Handoff Chain

```
Init ──────────▶ Discovery ──────────▶ Architecture
  │                  │                      │
  │ user_input       │ findings             │ blueprint
  ▼                  ▼                      ▼
┌─────────────┐  ┌─────────────┐      ┌─────────────┐
│ description │  │ domain      │      │ skill_type  │
│ target_users│  │ concepts    │      │ skill_name  │
│ clarif.     │  │ practices   │      │ directories │
└─────────────┘  │ tools       │      │ sections    │
                 │ sufficiency │      │ scripts     │
                 └─────────────┘      │ references  │
                                      └─────────────┘
                                            │
      ┌─────────────────────────────────────┘
      │
      ▼
Generation ──────────▶ Validation ──────────▶ Installation
     │                      │                      │
     │ artifacts            │ report               │ result
     ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ files[]     │      │ score       │      │ location    │
│ - path      │      │ errors[]    │      │ path        │
│ - type      │      │ warnings[]  │      │ installed_at│
│ - size      │      │ checks{}    │      └─────────────┘
└─────────────┘      └─────────────┘
```

## Phase Artifacts

### Init → Discovery

**Passed Forward**:
```json
{
  "input": {
    "description": "A skill that generates API docs from OpenAPI specs",
    "target_users": "Backend developers",
    "clarifications": []
  }
}
```

**Used By Discovery**:
- `description` → Search queries
- `target_users` → Context for best practices
- `clarifications` → Additional constraints

---

### Discovery → Architecture

**Passed Forward**:
```json
{
  "discovery": {
    "domain": "API Documentation",
    "key_concepts": ["OpenAPI 3.0", "Swagger", "REST"],
    "best_practices": ["Include examples", "Document errors"],
    "tools": ["Read", "Write", "WebFetch"],
    "sufficiency_score": 0.85
  }
}
```

**Used By Architecture**:
- `domain` → Skill naming
- `key_concepts` → Section planning
- `best_practices` → Reference content
- `tools` → `allowed-tools` selection

---

### Architecture → Generation

**Passed Forward**:
```json
{
  "architecture": {
    "skill_type": "Builder",
    "skill_name": "api-doc-generator",
    "directories": ["scripts", "references"],
    "sections": ["Overview", "Workflow", "Examples", "Output Checklist"],
    "scripts": [
      {"name": "generate.sh", "purpose": "Generate docs from spec"}
    ],
    "references": [
      {"name": "openapi-guide.md", "purpose": "OpenAPI best practices"}
    ]
  }
}
```

**Used By Generation**:
- `skill_type` → Template selection
- `skill_name` → SKILL.md name field
- `directories` → Folder creation
- `sections` → Content structure
- `scripts` → Script generation
- `references` → Reference file creation

---

### Generation → Validation

**Passed Forward**:
```json
{
  "generation": {
    "output_directory": "/tmp/skill-gen/api-doc-generator",
    "artifacts": [
      {"path": "SKILL.md", "type": "skill_md", "size_bytes": 4200},
      {"path": "scripts/generate.sh", "type": "script", "size_bytes": 1500},
      {"path": "references/openapi-guide.md", "type": "reference", "size_bytes": 3000}
    ]
  }
}
```

**Used By Validation**:
- `output_directory` → Where to validate
- `artifacts` → What to check
- `artifacts[].path` → File locations
- `artifacts[].type` → Validation rules per type

---

### Validation → Installation

**Passed Forward**:
```json
{
  "validation": {
    "status": "passed",
    "quality_score": 8.5,
    "errors": [],
    "warnings": [
      {"field": "examples", "message": "Consider adding more examples"}
    ]
  }
}
```

**Used By Installation**:
- `status` → Gate for installation
- `quality_score` → Display to user
- `warnings` → Show recommendations

---

## Handoff Mechanics

### Reading Previous Phase

```markdown
At phase start:
1. Read `.claude/skill_creation_state.json`
2. Extract previous phase's output section
3. Parse into working variables
4. Validate required fields present
```

### Writing Current Phase

```markdown
At phase end:
1. Collect phase outputs
2. Update state file with new section
3. Update phase field
4. Update timestamps
5. Write to disk
```

### Example State Read/Write

```markdown
# Reading (Architecture phase reading Discovery)
state = Read(".claude/skill_creation_state.json")
discovery = state.discovery
domain = discovery.domain
concepts = discovery.key_concepts

# Writing (Architecture phase saving results)
state.architecture = {
  skill_type: "Builder",
  skill_name: "api-doc-generator",
  ...
}
state.phase = "generation"
state.updated_at = now()
Write(".claude/skill_creation_state.json", state)
```

## Artifact Persistence

### Short-Term (State File)
- JSON data structures
- Small enough for context
- Updated every phase

### Medium-Term (Output Directory)
- Generated files
- Scripts, references
- Persists until installation

### Long-Term (Installed Skill)
- Final skill files
- User or project location
- Permanent until deleted

## Context Compression

### What to Keep
- Essential decisions (skill_type, skill_name)
- Structural choices (directories, sections)
- Quality metrics (score, errors)

### What to Summarize
- Discovery findings → Key concepts only
- Validation checks → Pass/fail summary
- Artifact details → Path and type only

### What to Discard
- Raw search results
- Intermediate drafts
- Verbose explanations

## Error Recovery with Context

```markdown
IF phase fails:
  1. Keep all previous phase artifacts
  2. Store error context in current phase
  3. Allow retry from current phase
  4. Don't lose accumulated context

State after failure:
{
  "phase": "generation",  // Still in failed phase
  "generation": {
    "status": "failed",
    "error": "Write permission denied",
    "retry_count": 1
  },
  "architecture": { ... }  // Previous phases intact
}
```
