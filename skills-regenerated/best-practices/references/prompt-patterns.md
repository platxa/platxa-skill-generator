# Prompt Patterns and Anti-Patterns

Quick reference for writing effective Claude Code prompts.

## The Universal Template

```
[WHAT] - Clear action description
[WHERE] - Specific files/paths with @
[HOW] - Constraints, patterns to follow
[VERIFY] - Tests, commands, or visual check
```

## Task-Type Templates

### Bug Fix

```
[symptom with error message]. check [location].
write failing test -> fix root cause -> verify test passes.
run full suite, confirm no regressions.
```

### Feature

```
implement [feature] following patterns in @[similar code].
requirements: [bullet list].
constraints: [no new deps / specific approach].
add tests for: [cases]. verify: [how].
```

### Refactor

```
refactor @[file]: [specific changes].
preserve: same API, all tests pass.
make one change at a time, test after each.
```

### Investigation

```
[symptom]. investigate:
1. profile/check [specific area]
2. identify [bottleneck/root cause]
3. report top 3 findings with file:line refs
```

### Testing

```
write tests for @[file] covering [edge cases].
avoid mocks. use existing test patterns in tests/.
test cases: [case1] -> [expected], [case2] -> [expected].
run and verify all pass.
```

### UI Change

```
[paste screenshot of design] update [component] to match.
check @[component file] and theme in @[config].
take screenshot after changes. compare to design.
list any differences and fix them.
```

### Migration

```
migrate from [old] to [new]. read migration guide at [URL].
identify all [deprecated API] usage. update one file at a
time, running tests after each. do not change unrelated code.
```

### Exploration

```
read @[directory] and explain how [system] works.
cover: [question 1], [question 2], [question 3].
summarize in a markdown doc with file:line references.
```

## Phasing Pattern (Complex Tasks)

```
PHASE 1 - EXPLORE: read @[files], understand patterns
PHASE 2 - PLAN: design approach, write plan for review
PHASE 3 - IMPLEMENT: follow plan, test after each step
PHASE 4 - VERIFY: full test suite, manual testing
```

## Anti-Pattern Quick Fixes

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `fix the bug` | No symptom or location | Add what users report + where to look |
| `make it better` | No criteria for "better" | Specify exact changes (perf? types?) |
| `update validation` | No file path | Add `@path`, specify which validation |
| `add a component` | No reference pattern | Point to existing similar component |
| `getting an error` | No error text | Paste full error + file:line + repro |
| `add tests` | No scope or cases | Specify file, cases, edge cases |
| `review my code` | No focus area | State: security? perf? edge cases? |
| Fix + style + refactor | Compound task | Split tasks, `/clear` between each |
| `do what we discussed` | Ambiguous reference | Restate the decision explicitly |
| `that is not right` | No expected behavior | Say what is wrong and what is expected |
| `add try/catch` | Suppresses errors | Fix root cause, add validation, test |

## Key Principles

- **Delegate outcomes, not steps** -- Do not micromanage file edits
- **One task per session** -- `/clear` between unrelated work
- **Scope investigations** -- "check src/auth/" not "figure out why it is slow"
- **Provide test cases with I/O** -- `"abc" -> true, "" -> false`
- **Reference patterns** -- `follow @src/components/UserCard.tsx`
- **State constraints** -- "no new deps", "no mocks", "client-side only"
- **After 2 corrections** -- `/clear` and write a better prompt

## Environment Setup Tips

| Tool | Purpose |
|------|---------|
| **CLAUDE.md** | Persistent project rules (commands, style, conventions) |
| **Skills** | Domain knowledge loaded on demand via `/skill-name` |
| **Subagents** | Isolated investigation in separate context via Task |
| **Hooks** | Deterministic actions (lint on edit, block writes) |
| **`/permissions`** | Allowlist safe commands to reduce interruptions |

### CLAUDE.md Best Practices

Keep concise. For each line ask: "Would removing this cause mistakes?" If not, cut it.

**Include**: Commands Claude cannot guess, style rules differing from defaults, test runners, project conventions, known gotchas.

**Exclude**: Anything inferrable from code, standard conventions, long tutorials, file-by-file descriptions.
