# Auto-Fix Pattern

Skills that identify issues can optionally fix them directly instead of only reporting.
This pattern applies to Analyzer and Validator skill types.

## When to Auto-Fix

Apply fixes when ALL of these are true:
- Severity is CRITICAL or HIGH
- Fix is unambiguous (single correct solution)
- Fix doesn't change public API surface
- Fix doesn't require architectural decisions
- Fix is reversible (Edit tool, not destructive operations)

Skip fixes when ANY of these are true:
- Multiple valid approaches exist (needs human judgment)
- Fix requires refactoring across multiple modules
- Fix would change function signatures or public interfaces
- Fix involves security decisions (auth flows, encryption choices)
- User didn't request auto-fix (respect report-only mode)

## Frontmatter Requirements

Skills with auto-fix MUST include Edit (and optionally Write) in allowed-tools:

```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit      # Required for modifying existing files
  - Write     # Optional, for creating new files (rare)
```

## Workflow Addition

Add this phase AFTER analysis and BEFORE final report:

```markdown
### Fix Phase (opt-in)

If the user requests fixes (e.g., invoked with `--fix` or `fix` argument):

1. **Filter fixable issues**:
   - CRITICAL and HIGH severity only
   - Unambiguous single-solution fixes
   - Mechanical changes (formatting, imports, naming, simple refactors)

2. **Apply each fix**:
   - Use Edit tool to modify the specific lines
   - One fix per Edit call (atomic changes)
   - Preserve surrounding code exactly

3. **Verify fixes**:
   - Re-run automated checks (helper scripts) on modified files
   - Confirm fix didn't introduce new issues
   - If new issue detected: revert the fix, report as manual-fix-needed

4. **Record results**:
   - Track what was fixed vs what was skipped
   - Include reason for each skip
```

## Report Format with Fixes

```markdown
### Fixes Applied (N)
- [FIX-1] file.py:42 — Removed hardcoded API key, replaced with os.environ.get()
- [FIX-2] handler.ts:15 — Added missing null check before property access

### Requires Manual Fix (M)
- [MANUAL-1] auth.py:89 — Multiple valid refactoring approaches for complexity reduction
- [MANUAL-2] api.go:120 — Architectural decision needed: middleware vs decorator pattern

### No Fix Needed (K)
- Issues below MEDIUM severity are reported but not auto-fixed
```

## Safety Rules

1. **NEVER** auto-fix if skill lacks Edit in allowed-tools
2. **NEVER** delete files or remove functions without user confirmation
3. **NEVER** modify test files to make tests pass (fix the implementation instead)
4. **NEVER** suppress errors or warnings (fix the cause, not the symptom)
5. **ALWAYS** preserve existing behavior (fixes should be safe refactors)
6. **ALWAYS** report what was changed (no silent modifications)
7. **ALWAYS** verify after fixing (re-run checks on modified code)

## Fixable vs Non-Fixable Issue Guide

| Issue Type | Fixable? | Example |
|-----------|----------|---------|
| Unused import | Yes | Remove the import line |
| Hardcoded secret | Yes | Replace with env var lookup |
| Missing type hint | Yes | Add the type annotation |
| String concat in loop | Yes | Replace with join() |
| Missing null check | Yes | Add guard clause |
| N+1 query | No | Requires architectural decision (join, prefetch, batch) |
| SOLID violation | No | Multiple valid refactoring approaches |
| Complex function | No | Many ways to decompose |
| Auth flow issue | No | Security design decision |
| Dead code | Cautious | May be intentionally preserved for future use |

## Architecture Agent Integration

When the architecture blueprint has `execution_sophistication.auto_fix: true`:
- Generation agent adds Edit to allowed-tools
- Generation agent includes the fix phase in the workflow
- Generation agent adds `--fix` argument parsing

When `auto_fix: false` (default):
- Skill is report-only
- No Edit in allowed-tools
- No fix phase in workflow
