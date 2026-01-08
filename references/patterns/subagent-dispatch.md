# Task Tool Subagent Dispatch Pattern

How to dispatch Task tool subagents for each workflow phase.

## Subagent Mapping

| Phase | Subagent Type | Purpose |
|-------|---------------|---------|
| Discovery | `Explore` | Research domain, find patterns |
| Architecture | `general-purpose` | Design decisions, planning |
| Generation | `general-purpose` | Content creation |
| Validation | `general-purpose` | Quality assessment |

## Phase-Specific Dispatch

### Discovery Phase

```markdown
Use Task tool with:
  subagent_type: "Explore"
  description: "Research {domain} best practices"
  prompt: [Load from references/agents/discovery-agent.md]
```

**Why Explore**: Optimized for codebase exploration, web searches, pattern finding.

**Example Dispatch**:
```
Task(
  subagent_type="Explore",
  description="Research API documentation patterns",
  prompt="""
    Research best practices for {skill_description}.

    Search for:
    1. Official documentation and standards
    2. Common workflows and processes
    3. Tools and technologies used

    Output: JSON with domain, concepts, best_practices, tools
  """
)
```

---

### Architecture Phase

```markdown
Use Task tool with:
  subagent_type: "general-purpose"
  description: "Design {skill_name} architecture"
  prompt: [Load from references/agents/architecture-agent.md]
```

**Why general-purpose**: Needs reasoning about structure, trade-offs, design decisions.

**Example Dispatch**:
```
Task(
  subagent_type="general-purpose",
  description="Design skill architecture",
  prompt="""
    Based on discovery findings:
    {discovery_json}

    Design skill architecture:
    1. Classify skill type (Builder/Guide/Automation/Analyzer/Validator)
    2. Determine directories needed
    3. Plan SKILL.md sections
    4. Design scripts and references

    Output: Architecture blueprint JSON
  """
)
```

---

### Generation Phase

```markdown
Use Task tool with:
  subagent_type: "general-purpose"
  description: "Generate {skill_name} files"
  prompt: [Load from references/agents/generation-agent.md]
```

**Why general-purpose**: Needs to write files, use templates, create content.

**Example Dispatch**:
```
Task(
  subagent_type="general-purpose",
  description="Generate skill files",
  prompt="""
    Generate skill files based on architecture:
    {architecture_json}

    Using template: references/templates/{skill_type}-template.md

    Create:
    1. SKILL.md with valid YAML frontmatter
    2. Scripts as specified
    3. Reference files as specified

    Output: List of created files with paths
  """
)
```

---

### Validation Phase

```markdown
Use Task tool with:
  subagent_type: "general-purpose"
  description: "Validate {skill_name}"
  prompt: [Load from references/agents/validation-agent.md]
```

**Why general-purpose**: Needs to read files, run checks, calculate scores.

**Example Dispatch**:
```
Task(
  subagent_type="general-purpose",
  description="Validate generated skill",
  prompt="""
    Validate skill at: {output_directory}

    Check:
    1. SKILL.md structure and frontmatter
    2. Name and description constraints
    3. Required sections present
    4. No placeholder content
    5. Scripts executable

    Output: Validation report with score
  """
)
```

---

## Dispatch Pattern Template

```markdown
### Phase: {PHASE_NAME}

**Dispatch**:
Task(
  subagent_type="{subagent_type}",
  description="{3-5 word description}",
  prompt="""
    {Detailed instructions from agent prompt file}

    Input:
    - {input_1}
    - {input_2}

    Output:
    {Expected output format}
  """
)

**On Success**:
- Update state: {state_updates}
- Transition to: {next_phase}

**On Failure**:
- Log error: {error_handling}
- Recovery: {recovery_action}
```

---

## Subagent Communication

### Passing Context

Each subagent receives context via prompt:
1. **Previous phase output**: JSON from state file
2. **User input**: Description, clarifications
3. **Templates**: Loaded from references/

### Receiving Results

Subagent returns:
1. **Status**: success/failure
2. **Data**: Phase-specific output (JSON)
3. **Errors**: Any issues encountered

### State Updates

After each subagent completes:
```json
{
  "phase": "{next_phase}",
  "{current_phase}": {
    "status": "complete",
    "output": { /* subagent result */ }
  },
  "updated_at": "{timestamp}"
}
```

---

## Parallel Dispatch

Some phases can run subagents in parallel:

### Discovery Phase (Parallel)
```markdown
Launch simultaneously:
1. Task(Explore): Web search for standards
2. Task(Explore): Analyze existing skills
3. Task(Explore): Find example implementations

Merge results when all complete.
```

### Not Parallelizable
- Architecture (depends on Discovery)
- Generation (depends on Architecture)
- Validation (depends on Generation)

---

## Error Handling

### Subagent Timeout
```markdown
IF subagent takes > 60 seconds:
  - Cancel task
  - Log timeout
  - Retry with simpler prompt
  - Max 2 retries
```

### Subagent Failure
```markdown
IF subagent returns error:
  - Log error details
  - Check if recoverable
  - IF recoverable: retry
  - ELSE: ask user for guidance
```

### Invalid Output
```markdown
IF subagent output doesn't match expected format:
  - Log parsing error
  - Request clarification from subagent
  - Fallback to manual extraction
```
