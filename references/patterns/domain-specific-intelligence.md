# Domain-Specific Intelligence Pattern

Use when the skill adds specialized knowledge beyond tool access — compliance rules,
industry regulations, safety checks, or domain expertise that must be applied before
taking action.

## Pattern Structure

```markdown
## Workflow

### Before Processing (Compliance Check)
1. Fetch transaction/request details
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
- Call appropriate processing tool
- Apply domain-specific checks
- Process transaction
ELSE:
- Flag for review
- Create compliance case
- Do NOT proceed

### Audit Trail
- Log all compliance checks
- Record processing decisions
- Generate audit report
```

## Key Techniques

- **Compliance before action**: Never process first and check later
- **Domain expertise embedded in logic**: Rules encoded in workflow, not just referenced
- **Comprehensive documentation**: Every decision has a paper trail
- **Clear governance**: IF/ELSE branches make compliance deterministic

## When to Use

- Financial processing (payment compliance, KYC/AML)
- Healthcare workflows (HIPAA, patient data handling)
- Legal document processing (jurisdictional rules)
- Infrastructure changes (change management, approval gates)
- Data handling (GDPR, privacy regulations)

## Anti-Patterns

- Checking compliance after the action is taken
- Relying on prose instructions instead of encoded rules
- Missing audit trails for compliance-critical decisions
- Proceeding on ambiguous compliance status
