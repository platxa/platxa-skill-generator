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

2. **Define Structure**: Determine needed directories
   - scripts/ - Helper executables (if automation needed)
   - references/ - Domain documentation (if expertise heavy)
   - assets/ - Static files (if templates needed)

3. **Plan Sections**: Design SKILL.md structure
   - Required: Overview, Workflow
   - Recommended: Examples, Output Checklist
   - Type-specific: Templates (Builder), Steps (Guide), etc.

4. **Token Budget**: Ensure efficiency
   - SKILL.md: < 500 lines
   - Metadata: ~100 tokens
   - References: Load on demand

## Output Format

```json
{
  "skill_type": "Builder|Guide|Automation|Analyzer|Validator",
  "skill_name": "hyphen-case-name",
  "directories": ["scripts", "references"],
  "skill_md_sections": [
    {"name": "Overview", "purpose": "Brief description"},
    {"name": "Workflow", "purpose": "Step-by-step process"},
    {"name": "Examples", "purpose": "Usage demonstrations"},
    {"name": "Output Checklist", "purpose": "Quality verification"}
  ],
  "scripts": [
    {"name": "script-name.sh", "purpose": "What it does"}
  ],
  "references": [
    {"name": "reference-name.md", "purpose": "What knowledge it contains"}
  ],
  "allowed_tools": ["Read", "Write", "Edit", "Bash", "Task"],
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

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Architecture Agent prompt with inputs filled in]
```
