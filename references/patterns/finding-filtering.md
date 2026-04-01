# Finding Filtering Pattern

Analyzer skills must filter noise before reporting. This pattern prevents generated
skills from reporting every possible issue, which overwhelms users and reduces trust.

## Confidence Threshold

Only report findings with HIGH confidence. When uncertain whether something is an
issue, omit it rather than generating noise.

```
IF confidence < HIGH:
    skip finding (do not include in report)
```

## Auto-Skip Rules

Skip findings in these categories without reporting:

| Category | Examples | Why Skip |
|----------|----------|----------|
| Auto-generated files | `*.pb.go`, `*.generated.ts`, `*_pb2.py`, migrations/ | Not human-authored, will be regenerated |
| Vendor/third-party | `node_modules/`, `vendor/`, `third_party/` | Not the project's responsibility |
| Test fixtures | Files in `fixtures/`, `testdata/`, `__mocks__/` | Intentionally bad patterns for testing |
| Build output | `dist/`, `build/`, `.next/`, `target/` | Generated artifacts |
| Lock files | `package-lock.json`, `poetry.lock`, `go.sum` | Machine-generated, not reviewable |

## Pattern Match Filtering

Distinguish between actual issues and pattern matches in non-code contexts:

- String literals: `password = "use_env_variable"` — not a hardcoded secret
- Comments: `# TODO: remove this hardcoded key` — not an actual key
- Documentation: `"API_KEY=your-key-here"` in a README — example, not real
- Test assertions: `assert password == "test123"` — test data, not production

## Deduplication Rules

### Same Location, Multiple Dimensions
When parallel agents report the same `file:line` from different dimensions:
- Keep the finding with the **highest severity**
- Cross-reference the other dimensions in the detail text
- Example: Security agent reports injection at line 42, Quality agent reports
  complexity at line 42 — keep the injection finding (CRITICAL > MEDIUM)

### Same Pattern, Multiple Files
When the same issue appears in multiple files:
- Group into a single finding with a file count
- List the first 3 files, then "and N more"
- Example: "Missing type hints on public functions (12 files: auth.py, api.py, db.py, and 9 more)"

### Same Root Cause
When multiple findings trace back to one root cause:
- Report the root cause as one finding
- List the symptoms as sub-items
- Example: "Missing error handling base class" causes "bare except in auth.py",
  "bare except in api.py", "bare except in db.py" — report the base class issue once

## Actionability Filter

Before including a finding, check:

1. **Can the developer act on this?**
   - No → skip (e.g., "language design limitation")
2. **Is the fix worth the effort?**
   - Trivial issue with complex fix → downgrade to LOW or skip
3. **Is this a style preference or actual defect?**
   - Style preference → only report if CLAUDE.md convention says so
   - Actual defect → always report

## Integration with Analyzer Template

Add this to the aggregation step (Step 3 in parallel analysis, or after single-pass
analysis):

```markdown
### Filtering

Before generating the report:
1. Remove findings in auto-generated, vendor, and build output files
2. Remove pattern matches in comments, strings, and documentation
3. Deduplicate: same file:line → keep highest severity
4. Deduplicate: same pattern across files → group with count
5. Deduplicate: same root cause → report once with symptoms
6. Remove findings below confidence threshold
7. Remove non-actionable findings
```
