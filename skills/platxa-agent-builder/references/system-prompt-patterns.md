# System Prompt Design Patterns

Four agent patterns with templates for structuring system prompts.

## Pattern 1: Analysis Agent

For agents that examine, review, or audit existing code/content.

**Process:** Gather → Scan → Deep Analysis → Synthesize → Prioritize → Report

```markdown
You are a [specific analysis role]. Your role is to [primary objective].

## Responsibilities
- [Specific analysis task 1]
- [Specific analysis task 2]
- [Specific analysis task 3]
- [What the agent explicitly does NOT do]

## Process
1. **Gather context**: [What to read and understand first]
2. **Scan structure**: [High-level structural review]
3. **Deep analysis**: [Detailed examination of each component]
4. **Cross-reference**: [Check against related code/standards]
5. **Synthesize**: [Combine findings, identify patterns]
6. **Prioritize**: [Rank findings by severity/impact]

## Output Format
[Specify exact structure of the report]

For each finding:
- **Severity**: [Scale used]
- **Location**: file_path:line_number
- **Issue**: [Description]
- **Recommendation**: [How to fix]

## Quality Standards
- [Minimum confidence threshold for reporting]
- [False positive handling]
- [What constitutes a genuine finding vs noise]

## Edge Cases
- [What to do when code is minified/generated]
- [How to handle ambiguous patterns]
- [When to escalate to user judgment]
```

## Pattern 2: Generation Agent

For agents that create new code, tests, documentation, or artifacts.

**Process:** Understand → Gather Context → Design → Generate → Validate → Document

```markdown
You are a [specific generation role]. Your role is to [what you create].

## Responsibilities
- [What kind of artifacts to generate]
- [Standards to follow]
- [What NOT to generate]

## Process
1. **Understand**: [Read target code, understand requirements]
2. **Gather context**: [Find conventions, patterns, existing examples]
3. **Design**: [Plan structure before generating]
4. **Generate**: [Create the artifact following conventions]
5. **Validate**: [Verify the output works/compiles/passes]

## Conventions
- [Naming patterns to follow]
- [File structure conventions]
- [Style guidelines]

## Output
- [What files are created]
- [Where they are placed]
- [What format they follow]

## Quality Standards
- [Completeness criteria]
- [Coverage requirements]
- [Style compliance]
```

## Pattern 3: Validation Agent

For agents that check compliance, quality, or readiness.

**Process:** Load Criteria → Scan → Check Rules → Collect Violations → Assess → Determine

```markdown
You are a [specific validation role]. Your role is to [what you validate].

## Criteria
- [Rule category 1 with specific checks]
- [Rule category 2 with specific checks]
- [Rule category 3 with specific checks]

## Process
1. **Load criteria**: [Read project standards and requirements]
2. **Scan scope**: [Identify all files/components to check]
3. **Apply rules**: [Check each rule against each component]
4. **Collect violations**: [Record all failures with locations]
5. **Assess severity**: [Classify as blocking vs advisory]
6. **Determine verdict**: [Overall pass/fail decision]

## Verdicts
- **PASS**: All blocking rules pass, advisory issues are minor
- **CONDITIONAL PASS**: No blocking failures, significant advisories
- **FAIL**: One or more blocking rule failures

## Output Format
Overall verdict: PASS / CONDITIONAL PASS / FAIL
Score: X/10

Blocking issues:
- [Issue with location and fix]

Advisory issues:
- [Issue with location and suggestion]

## Edge Cases
- [How to handle partial compliance]
- [When to override strict rules]
```

## Pattern 4: Orchestration Agent

For agents that coordinate multi-phase workflows.

**Process:** Plan → Prepare → Execute Phases → Monitor → Verify → Report

```markdown
You are a [specific orchestration role]. Your role is to [what workflow you coordinate].

## Phases
1. [Phase name]: [What happens]
2. [Phase name]: [What happens]
3. [Phase name]: [What happens]

## Process
1. **Plan**: [Determine which phases apply based on input]
2. **Pre-flight**: [Validate all prerequisites before starting]
3. **Execute**: [Run each phase, checking results between steps]
4. **Monitor**: [Watch for failures or warnings during execution]
5. **Verify**: [Confirm final state matches expectations]
6. **Report**: [Summarize what happened and any issues]

## Error Handling
- Phase failure: [Stop and report, or continue with warnings]
- Prerequisite missing: [How to handle]
- Partial completion: [Resume or rollback strategy]

## Output
- Phase-by-phase status report
- Any errors or warnings encountered
- Final state summary
- Next steps or follow-up actions
```

## Writing Guidelines

### Do
- Write in second person ("You are...", "Your role is...")
- Be specific about each process step
- Define output format with concrete structure
- Include quality thresholds and edge cases
- Use imperative voice for instructions

### Don't
- Use vague language ("review the code" → "check each function for null pointer dereferences")
- Skip output format definition
- Forget edge cases
- Make the prompt too short (minimum ~500 words)
- Include instructions for tools the agent doesn't have access to

### Length Guidelines

| Agent Complexity | Target Words | Sections |
|-----------------|-------------|----------|
| Simple/focused | ~500 | Role, Process, Output |
| Standard | 1000-2000 | Role, Responsibilities, Process, Output, Standards |
| Comprehensive | 2000-5000 | All sections + detailed edge cases |
| Orchestration | Up to 10000 | All sections + per-phase instructions |

### Common Pitfalls

1. **Vague responsibilities**: "Analyze code" → "Check each function for proper error handling, null safety, and resource cleanup"
2. **Missing process**: Just stating the goal without HOW to achieve it
3. **Undefined output**: Agent doesn't know what format to return results in
4. **No quality threshold**: Agent reports everything including noise
5. **No edge cases**: Agent fails on unusual inputs
