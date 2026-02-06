# Advanced Command Patterns

Multi-step workflows, state management, plugin integration, and validation patterns.

## Multi-Step Workflow Commands

### Sequential Workflow

Commands that guide through multi-step processes:

```markdown
---
description: Complete PR review workflow
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read, Grep
---

# PR Review Workflow for #$1

## Step 1: Fetch PR Details
!`gh pr view $1 --json title,body,author,files`

## Step 2: Review Files
Files changed: !`gh pr diff $1 --name-only`

For each file:
- Check code quality
- Verify tests exist
- Review documentation

## Step 3: Run Checks
Test status: !`gh pr checks $1`

## Step 4: Provide Feedback
Summarize findings and recommend: approve, request changes, or comment.
```

### State-Carrying Workflow

Commands that persist state between invocations:

```markdown
---
description: Initialize deployment workflow
allowed-tools: Write, Bash(git:*)
---

Creating deployment tracking state...

Branch: !`git branch --show-current`
Commit: !`git log -1 --format=%H`

Write state to `.claude/deployment-state.local.md`:
- workflow: deployment
- stage: initialized
- branch and commit info
- timestamp

Next: Run /deploy-test to continue.
```

**Follow-up command** reads the state file:

```markdown
---
description: Run deployment tests
allowed-tools: Read, Bash(npm:*)
---

Reading state: @.claude/deployment-state.local.md

Running tests: !`npm test`

Update state to 'tested'. Next: /deploy-execute
```

**Key benefits:**
- Persistent state across commands
- Clear workflow progression
- Safety checkpoints between steps
- Resume capability after interruption

## Plugin Integration Patterns

### Plugin Script Execution

```markdown
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`
```

### Plugin Configuration Loading

```markdown
@${CLAUDE_PLUGIN_ROOT}/config/settings.json
@${CLAUDE_PLUGIN_ROOT}/config/$1-deploy.json  <!-- Environment-specific -->
```

### Plugin Template Usage

```markdown
Template: @${CLAUDE_PLUGIN_ROOT}/templates/report.md
Generate output following the template structure above.
```

### Multi-Component Plugin Workflow

```markdown
---
description: Comprehensive review using all plugin components
argument-hint: [file-path]
allowed-tools: Bash(node:*), Read
---

Target: @$1

Phase 1 - Static Analysis:
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`

Phase 2 - Deep Review:
Launch the code-reviewer agent for detailed analysis.

Phase 3 - Standards Check:
Use the coding-standards skill for validation.

Phase 4 - Report:
Template: @${CLAUDE_PLUGIN_ROOT}/templates/review-report.md
Compile findings following template.
```

### Plugin Resource Validation

Always validate plugin resources before using them:

```markdown
---
description: Run plugin analyzer
allowed-tools: Bash(test:*)
---

Validate plugin setup:
- Script: !`test -x ${CLAUDE_PLUGIN_ROOT}/bin/analyze && echo "OK" || echo "MISSING"`
- Config: !`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "OK" || echo "MISSING"`

If all checks pass, proceed. Otherwise report missing components.
```

## Validation Patterns

### Argument Validation

```markdown
Validate environment: !`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"`

If valid: Deploy to $1
If invalid: Explain valid options (dev, staging, prod) and usage.
```

### File Existence Checks

```markdown
Check file: !`test -f $1 && echo "EXISTS" || echo "MISSING"`

If exists: Process @$1
If missing: Explain expected location and how to create it.
```

### Required Arguments

```markdown
Validate: !`test -n "$1" -a -n "$2" && echo "OK" || echo "MISSING"`

If both present: Deploy version $2 to $1
If missing: ERROR - both environment and version required.
  Usage: /deploy [environment] [version]
```

## Command Composition

### Command Chaining

Design commands that work together:

```markdown
---
description: Prepare for code review
---

Running preparation sequence:
1. Format code: /format-code
2. Run linter: /lint-code
3. Run tests: /test-all
4. Create summary: /review-summary

Compile results and prepare review materials.
```

### Conditional Branching

```markdown
---
description: Smart deployment
argument-hint: [environment]
allowed-tools: Bash(git:*), Bash(npm:*)
---

Branch: !`git branch --show-current`
Tests: !`npm test`

Conditions:
- If $1 = 'production': Extra validation, require main branch
- If $1 = 'staging': Standard process
- If $1 = 'dev': Minimal checks

Proceed based on environment requirements.
```

## Error Handling

### Graceful Failure

```markdown
Execute build: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh 2>&1 || echo "BUILD_FAILED"`

If succeeded: Report results and output location
If failed:
  - Analyze error output
  - Suggest likely causes
  - Provide troubleshooting steps
```

### Rollback on Failure

```markdown
Save current state for rollback:
Previous version: !`cat version.txt`

Deploy new version...

If deployment failed:
  - Initiate automatic rollback
  - Report failure details
  - Suggest next steps
```

## Workflow State Management

### Using .local.md Files

Store state in project-specific files:

```markdown
.claude/workflow-state.local.md:

---
workflow: deployment
stage: testing
started: 2025-01-15T10:30:00Z
environment: staging
---

Completed: Validation, Branch check
In progress: Testing
Pending: Build, Deploy, Smoke tests
```

**Reading state:**
```markdown
Current state: @.claude/workflow-state.local.md
Parse YAML frontmatter to determine next step.
```

### Workflow Locking

Prevent concurrent execution:

```markdown
Check lock: !`test -f .claude/deployment.lock && echo "LOCKED" || echo "FREE"`

If locked: ERROR - deployment in progress. Wait or run /deploy-abort
If free: Create lock, proceed with deployment.
```

**Clean up after completion:**
```markdown
Remove lock: rm .claude/deployment.lock
Ready for next deployment.
```

## Cross-Platform Considerations

### Platform Detection

```markdown
Platform: !`uname`

Adapt behavior:
- macOS (Darwin): Use pbcopy for clipboard
- Linux: Use xclip or xsel
- Windows (MINGW/MSYS): Use clip.exe
```

### Dependency Checking

```markdown
Check required tools:
- git: !`command -v git && echo "OK" || echo "MISSING"`
- jq: !`command -v jq && echo "OK" || echo "MISSING"`
- node: !`command -v node && echo "OK" || echo "MISSING"`

If any missing: Provide installation links and instructions.
```

## Best Practices Summary

1. **Clear progression**: Number steps, show current position
2. **Explicit state**: Don't rely on implicit state
3. **User control**: Provide decision points
4. **Error recovery**: Handle failures gracefully
5. **Single responsibility**: Each command does one thing well
6. **Composable design**: Commands work together easily
7. **Atomic updates**: Write complete state files
8. **Cleanup**: Remove stale state and lock files
