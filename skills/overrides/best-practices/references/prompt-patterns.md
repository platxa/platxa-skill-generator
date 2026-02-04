# Prompt Patterns & Anti-Patterns

Quick reference for writing effective Claude Code prompts. Condensed from 50+ examples.

## The Universal Template

```
[WHAT] - Clear action description
[WHERE] - Specific files/paths with @
[HOW] - Constraints, patterns to follow
[VERIFY] - Tests, commands, or visual check
```

## Anti-Pattern Quick Fixes

| Anti-Pattern | Fix |
|-------------|-----|
| `fix the bug` | Add symptom + location + verification |
| `make it better` | Specify exact changes (perf? types? style?) |
| `update validation` | Add file path with `@`, specify which validation |
| `add a component` | Reference existing pattern with `@similar.tsx` |
| `getting an error` | Paste full error + file:line + reproduction steps |
| `add tests` | Specify file, cases, edge cases, coverage target |
| `review my code` | Specify focus: security? perf? patterns? edge cases? |
| `make it accessible` | List: keyboard nav, ARIA, focus, contrast, screen reader |
| Fix + style + refactor | Split tasks, `/clear` between each |
| `do what we discussed` | Restate the decision explicitly |
| `that's not right` | Say what's wrong and what's expected |
| `add try/catch` | Fix root cause, add validation, test the case |

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

## Phasing Pattern (Complex Tasks)

```
PHASE 1 - EXPLORE: read @[files], understand patterns
PHASE 2 - PLAN: design approach, write plan for review
PHASE 3 - IMPLEMENT: follow plan, test after each step
PHASE 4 - VERIFY: full test suite, manual testing
```

## Key Principles

- **Delegate outcomes, not steps** - Don't micromanage file edits
- **One task per session** - `/clear` between unrelated work
- **Scope investigations** - "check src/auth/" not "figure out why it's slow"
- **Provide test cases with I/O** - `"abc" -> true, "" -> false`
- **Reference patterns** - `follow @src/components/UserCard.tsx`
- **State constraints** - "no new deps", "no mocks", "client-side only"
- **After 2 corrections** - `/clear` and write a better prompt
