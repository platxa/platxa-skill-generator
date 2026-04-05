# Iterative Refinement Pattern

Use when output quality improves with iteration. Applies to Builder and Automation skills
that generate content, reports, or code where a validate-then-fix cycle produces better results.

## Pattern Structure

```markdown
## Workflow

### Initial Draft
1. Fetch data via MCP or tool
2. Generate first draft report/output
3. Save to temporary file

### Quality Check
1. Run validation script: `scripts/check_quality.py`
2. Identify issues:
   - Missing sections
   - Inconsistent formatting
   - Data validation errors

### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met (max 3 iterations)

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

## Key Techniques

- **Explicit quality criteria**: Define what "good enough" means before starting
- **Validation scripts**: Use code for checks, not prose instructions — code is deterministic
- **Iteration cap**: Always set a maximum (3 iterations recommended) to prevent infinite loops
- **Know when to stop**: Define clear pass/fail thresholds

## When to Use

- Report generation (data quality varies)
- Code generation (compile/lint/test cycles)
- Document creation (format and completeness checks)
- Configuration generation (validation against schemas)

## When NOT to Use

- Simple lookups or reads (no iteration needed)
- One-shot transformations with deterministic output
- Skills where the first output is typically correct
