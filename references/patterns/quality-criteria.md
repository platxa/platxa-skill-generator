# Quality Criteria Reference

Standards for evaluating Claude Code skills.

## Scoring System

Total score: 0-10 points
Passing threshold: ≥7.0

### Category Weights

| Category | Weight | Max Points |
|----------|--------|------------|
| Required Fields | 30% | 3.0 |
| Content Quality | 25% | 2.5 |
| Structure | 20% | 2.0 |
| Token Efficiency | 15% | 1.5 |
| Completeness | 10% | 1.0 |

---

## Required Fields (30%)

### SKILL.md Existence
- **3.0 pts**: File exists with valid YAML frontmatter
- **0 pts**: File missing or malformed

### Name Field
| Criteria | Points |
|----------|--------|
| Present | +0.5 |
| Hyphen-case format | +0.5 |
| ≤64 characters | +0.5 |
| Descriptive | +0.5 |

### Description Field
| Criteria | Points |
|----------|--------|
| Present | +0.5 |
| ≤1024 characters | +0.5 |
| Clear purpose | +0.5 |

### Allowed-Tools Field
| Criteria | Points |
|----------|--------|
| Present | +0.5 |
| Valid tool names | +0.5 |
| Minimal necessary tools | +0.5 |

---

## Content Quality (25%)

### Real Content vs Placeholders
- **2.5 pts**: All content is substantive
- **1.5 pts**: Minor placeholders (1-2 TODOs)
- **0.5 pts**: Many placeholders
- **0 pts**: Mostly placeholder content

### Placeholder Detection
Check for these patterns:
```
TODO, TBD, FIXME, XXX
"...", "[...]", "<...>"
"Lorem ipsum"
"Example here"
"Add content"
```

### Helpful Examples
- **+0.5**: Examples show realistic usage
- **+0.5**: Examples cover common scenarios
- **-0.5**: Examples are trivial or unhelpful

---

## Structure (20%)

### Required Sections
| Section | Points |
|---------|--------|
| Overview | +0.5 |
| Workflow | +0.5 |

### Recommended Sections
| Section | Points |
|---------|--------|
| Examples | +0.25 |
| Output Checklist | +0.25 |
| Type-specific sections | +0.5 |

### Organization
- **+0.5**: Logical section ordering
- **+0.5**: Consistent formatting
- **-0.5**: Confusing structure

---

## Token Efficiency (15%)

### SKILL.md Size
| Lines | Points |
|-------|--------|
| <200 | 1.5 |
| 200-350 | 1.0 |
| 350-500 | 0.5 |
| >500 | 0 |

### Metadata Size
| Tokens | Points |
|--------|--------|
| <80 | +0.5 |
| 80-100 | +0.25 |
| >100 | 0 |

### Reference Loading
- **+0.5**: References loaded on-demand
- **-0.5**: All content in SKILL.md

---

## Completeness (10%)

### Scripts (if applicable)
| Criteria | Points |
|----------|--------|
| Executable | +0.25 |
| Error handling | +0.25 |
| Documentation | +0.25 |
| Tested | +0.25 |

### References (if applicable)
| Criteria | Points |
|----------|--------|
| Real expertise | +0.5 |
| Well-organized | +0.25 |
| Up-to-date | +0.25 |

---

## Automatic Deductions

| Issue | Deduction |
|-------|-----------|
| Hardcoded secrets | -3.0 |
| Invalid tool names | -1.0 |
| Name >64 chars | -1.0 |
| Description >1024 chars | -0.5 |
| Missing required section | -0.5 each |
| Non-executable scripts | -0.5 each |
| Placeholder content | -0.25 each |

---

## Quality Levels

| Score | Level | Recommendation |
|-------|-------|----------------|
| 9.0-10.0 | Excellent | Ready to publish |
| 8.0-8.9 | Good | Minor improvements suggested |
| 7.0-7.9 | Acceptable | Meets minimum standards |
| 5.0-6.9 | Needs Work | Significant improvements required |
| <5.0 | Failing | Major revision needed |

---

## Quick Validation Checklist

```
□ SKILL.md exists
□ YAML frontmatter is valid
□ Name: hyphen-case, ≤64 chars
□ Description: ≤1024 chars
□ allowed-tools: valid names only
□ Overview section present
□ Workflow section present
□ No placeholder content
□ Examples are realistic
□ SKILL.md < 500 lines
□ Scripts are executable
□ References have real content
```
