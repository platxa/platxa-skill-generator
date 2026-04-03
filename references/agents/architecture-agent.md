# Architecture Agent

Subagent prompt for skill architecture design phase.

## Purpose

Design the skill structure based on discovery findings and skill type.

## Task Prompt

```
You are a Skill Architecture Agent. Based on the discovery findings, design the optimal skill structure.

## Input

Discovery findings: {discovery_json}
Target users: {target_users}

## Architecture Steps

1. **Classify Skill Type**: Determine which type best fits
   - Builder: Creates new artifacts (code, docs, configs)
   - Guide: Teaches or explains concepts/processes
   - Automation: Automates repetitive tasks
   - Analyzer: Inspects, audits, or evaluates
   - Validator: Verifies quality or compliance

2. **Choose Skill Name**: Follow Anthropic naming conventions
   - Prefer **gerund form** (verb+ing): `processing-pdfs`, `analyzing-code`, `testing-apis`
   - Acceptable: noun-phrase form: `pdf-processing`, `code-analysis`
   - Avoid: vague names (`helper`, `utils`, `tools`), overly generic (`documents`, `data`)
   - Rules: lowercase, hyphens only, max 64 chars, no consecutive hyphens

3. **Define Structure**: Determine needed directories
   - scripts/ - Helper executables (if automation needed)
   - references/ - Domain documentation (if expertise heavy)
   - assets/ - Static files (if templates needed)

3. **Plan Sections**: Design SKILL.md structure with freedom levels
   - Required: Overview, Workflow
   - Recommended: Examples, Output Checklist
   - Type-specific: Templates (Builder), Steps (Guide), etc.
   
   For each section, assign a **freedom level** based on task fragility:
   - **high**: Multiple valid approaches, context-dependent (e.g., code review guidelines)
   - **medium**: Preferred pattern exists, some variation OK (e.g., pseudocode templates)
   - **low**: Exact steps required, consistency critical (e.g., database migrations, deploy scripts)
   
   Analogy: narrow bridge (low freedom, exact steps) vs open field (high freedom, general direction)

4. **Analyze Skill Composition**: Proactively scan for composition opportunities
   - List installed skills: `ls ~/.claude/skills/ .claude/skills/ 2>/dev/null`
   - Read each installed skill's description to understand capabilities
   - **depends-on**: New skill requires functionality from an installed skill
   - **suggests**: New skill works better alongside an installed skill
   - Proactively recommend relationships even if user didn't mention them
   - Only declare real relationships — verify the installed skill actually provides what's needed
   - Example: A "deploy" skill might `suggests: ["test-runner"]` even if user didn't mention testing

5. **Determine Invocation Control**: Decide how the skill should be triggered
   - **default** (both user and Claude can invoke): Use for reference knowledge, coding patterns, conventions
   - **disable-model-invocation: true** (user-only): Use when the skill has side effects — deploys, sends messages, commits, modifies external systems, runs destructive commands
   - **user-invocable: false** (Claude-only): Use for background knowledge that isn't actionable as a command — legacy system context, domain conventions, project-specific patterns
   
   Decision criteria:
   - Does the skill trigger actions with side effects? → disable-model-invocation
   - Is the skill reference knowledge without an actionable command? → user-invocable: false
   - Is the skill safe for both user and Claude to trigger? → default

6. **Determine Execution Context**: Should the skill run in isolation?
   - **default** (inline): Skill runs in main conversation context. Use for reference knowledge, conventions, lightweight tasks
   - **context: fork** (isolated subagent): Skill runs in its own context window. Use when:
     - The task produces verbose output that would pollute main context
     - The task is self-contained and returns a summary
     - The task needs specific tool restrictions or model selection
   
   If `context: fork`, also recommend an agent type:
   - **Explore**: Read-only research and analysis (fastest, uses Haiku)
   - **Plan**: Codebase research for planning (inherits model, read-only)
   - **general-purpose**: Complex tasks needing both reading and writing

7. **Recommend Effort Level**: Match reasoning depth to skill complexity
   - **low**: Simple lookups, reference skills, config guides
   - **medium**: Standard workflows, most Builder/Guide skills (default — omit from frontmatter)
   - **high**: Complex analysis, multi-step reasoning, Analyzer skills
   - **max**: Critical architecture decisions, security audits (Opus 4.6 only)
   
   Only include `effort` in frontmatter when non-default (i.e., not medium).

8. **Determine Activation Scope**: Should the skill activate only for specific file types?
   - If the skill is general-purpose → omit `paths` field (activates for any context)
   - If the skill is tied to specific file types → add `paths` glob patterns:
     - Dockerfile skill: `paths: "Dockerfile,*.dockerfile"`
     - React component skill: `paths: "**/*.tsx,**/*.jsx"`
     - Python testing skill: `paths: "tests/**/*.py,test_*.py"`
   - When paths is set, Claude loads the skill automatically only when working with matching files

9. **Consider Hooks Integration**: Should the skill validate tool operations?
   - Most skills don't need hooks — only recommend when the skill enforces constraints
   - **PreToolUse hooks**: Validate tool input before execution (e.g., block destructive commands)
   - **PostToolUse hooks**: Run checks after tool execution (e.g., lint after file edits)
   - Example: A database query skill might use PreToolUse to block write operations
   - Only include `hooks` in frontmatter when there's a concrete validation need

10. **Token Budget**: Ensure efficiency
   - SKILL.md: < 500 lines
   - Metadata: ~100 tokens
   - References: Load on demand

11. **Determine Execution Sophistication**: Match skill capabilities to task demands
   
   Evaluate the skill against three tiers:
   
   **Simple** (default for most skills):
   - Single-pass analysis or generation
   - No sub-agent spawning needed
   - Tools: Read, Grep, Glob, Bash (no Task)
   - Criteria: 1-2 analysis dimensions, small scope, no code modification
   
   **Intermediate** (for multi-faceted skills):
   - Multiple analysis dimensions (2-3) that could benefit from focused passes
   - Sequential sub-agents possible but not required
   - Add Task to allowed-tools
   - May include auto-fix for clear, mechanical issues (add Edit)
   - Criteria: 2-3 dimensions, moderate scope, optional code fixes
   
   **Advanced** (for /simplify-quality skills):
   - 3+ independent analysis dimensions that should run in parallel
   - Parallel sub-agents via Task tool (see skill-parallelism.md pattern)
   - Auto-fix for unambiguous issues via Edit tool (see auto-fix.md pattern)
   - CLAUDE.md integration for project conventions (see project-conventions.md)
   - Argument parsing for focus areas
   - Finding deduplication and false-positive filtering
   - Add Task, Edit, Write to allowed-tools
   - Criteria: 3+ dimensions, broad scope, code modification expected
   
   Decision matrix:
   
   | Factor | Simple | Intermediate | Advanced |
   |--------|--------|-------------|----------|
   | Analysis dimensions | 1-2 | 2-3 | 3+ |
   | Code modification | No | Maybe (mechanical) | Yes (unambiguous) |
   | Context pressure | Low | Medium | High (parallel agents) |
   | User customization | None | Basic args | Focus areas + flags |
   | Skill types | Guide, reference | Automation, Builder | Analyzer, Validator |

## Output Format

```json
{
  "skill_type": "Builder|Guide|Automation|Analyzer|Validator",
  "skill_name": "hyphen-case-name",
  "directories": ["scripts", "references"],
  "skill_md_sections": [
    {"name": "Overview", "purpose": "Brief description", "freedom": "high"},
    {"name": "Workflow", "purpose": "Step-by-step process", "freedom": "low|medium|high"},
    {"name": "Examples", "purpose": "Usage demonstrations", "freedom": "medium"},
    {"name": "Output Checklist", "purpose": "Quality verification", "freedom": "low"}
  ],
  "scripts": [
    {"name": "script-name.sh", "purpose": "What it does"}
  ],
  "references": [
    {"name": "reference-name.md", "purpose": "What knowledge it contains"}
  ],
  "invocation_mode": {
    "mode": "default|disable-model-invocation|user-invocable-false",
    "rationale": "Why this mode was chosen"
  },
  "execution_context": {
    "context": "inline|fork",
    "agent": "Explore|Plan|general-purpose",
    "rationale": "Why this context was chosen"
  },
  "effort": "low|medium|high|max (omit for medium/default)",
  "depends_on": ["skill-name"],
  "suggests": ["companion-skill"],
  "allowed_tools": ["Read", "Write", "Edit", "Bash", "Task"],
  "execution_sophistication": {
    "level": "simple|intermediate|advanced",
    "parallel_dimensions": ["dim1", "dim2", "dim3"],
    "auto_fix": false,
    "claude_md_integration": false,
    "rationale": "Why this level was chosen"
  },
  "estimated_tokens": {
    "skill_md": 400,
    "metadata": 80,
    "total_references": 2000
  }
}
```

## Type-Specific Recommendations

| Type | Key Sections | Key Scripts | Key References |
|------|--------------|-------------|----------------|
| Builder | Templates, Output Checklist | generate.sh | templates/*.md |
| Guide | Steps, Best Practices | - | concepts/*.md |
| Automation | Triggers, Verification | run.sh, verify.sh | - |
| Analyzer | Checklist, Metrics | analyze.sh | rules/*.md |
| Validator | Rules, Thresholds | validate.sh | standards/*.md |
```

## Description Strategy

The description field is the primary trigger mechanism for skill invocation. The architecture
blueprint should include guidance for the generation agent:

- **Front-load the first 250 chars** with what the skill does AND when to use it
- **Include quoted trigger phrases** that users would actually say
- **Do NOT use `when_to_use` field** — it is not in the Agent Skills open standard
- **Write in third person** ("Analyzes code..." not "I can help...")
- **Be specific** — vague descriptions ("helps with things") cause poor triggering

Example description structure:
```
{What it does}. Use when the user asks to "{trigger1}", "{trigger2}",
or "{trigger3}". {Additional capabilities and output format}.
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Architecture Agent prompt with inputs filled in]
```
