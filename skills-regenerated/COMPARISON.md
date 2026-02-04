# Pilot Skill Regeneration Comparison Report

Compares 5 regenerated pilot skills against upstream originals to verify domain intent preservation and Platxa standard compliance.

## Intent Preservation Matrix

| Skill | Purpose | Workflows | Tools | Domain | Overall |
|-------|:-------:|:---------:|:-----:|:------:|:-------:|
| imagegen (builder) | Yes | Yes | Partial (-2) | Yes | Strong |
| hugging-face-model-trainer (guide) | Yes | Yes | Partial (close) | Yes | Strong |
| hugging-face-jobs (automation) | Yes | Yes | Yes (exact) | Yes | Full |
| security-ownership-map (analyzer) | Yes | Yes | Partial (+2) | Yes | Strong |
| verification-before-completion (validator) | Yes | Yes | Yes (exact) | Yes | Full |

**Tool differences explained:**
- imagegen: Dropped WebFetch/WebSearch (image generation rarely needs web search)
- security-ownership-map: Added Glob/Grep (standard for analyzer-type codebase scanning)

## Platxa Standard Compliance

| Check | imagegen | hf-trainer | hf-jobs | sec-ownership | verification |
|-------|:--------:|:----------:|:-------:|:-------------:|:------------:|
| Valid frontmatter | PASS | PASS | PASS | PASS | PASS |
| `allowed-tools` | PASS | PASS | PASS | PASS | PASS |
| Provenance metadata | PASS | PASS | PASS | PASS | PASS |
| Type template structure | PASS | Partial | PASS | PASS | PASS |
| Token budget | PASS | PASS | PASS | PASS | PASS |
| Quality score >= 7.0 | 9.35 | 9.65 | 8.66 | 9.30 | 7.90 |

## Token Budget Comparison

| Skill | Upstream | Regenerated | Change | Notes |
|-------|:--------:|:-----------:|:------:|-------|
| imagegen | 8,933 | 6,725 | -25% | Upstream had 1 per-file limit warning |
| hugging-face-model-trainer | **23,224** | 8,906 | **-62%** | Upstream exceeded ALL limits |
| hugging-face-jobs | 3,680 | 5,086 | +38% | Added template-required sections |
| security-ownership-map | 2,748 | 4,285 | +56% | Added analyzer template sections |
| verification-before-completion | 987 | 2,778 | +182% | Added validator rules/criteria |

## Per-Skill Notes

### imagegen (builder)
- Added Output Checklist and Troubleshooting (builder template requirements)
- Trimmed sample-prompts.md from 3,392 to 1,226 tokens (was over per-file limit)
- Dropped codex-network.md reference (sandbox-specific, not broadly applicable)

### hugging-face-model-trainer (guide)
- **Biggest win**: Upstream was 23,224 tokens (limit: 15,000), compressed 62%
- Upstream SKILL.md was 707 lines (limit: 500) and 6,845 tokens (limit: 5,000)
- Uses "Workflow"/"Checklist" instead of "Learning Path"/"Best Practices" — reasonable for procedural guide
- All 5 per-file overages in references resolved

### hugging-face-jobs (automation)
- Strongest template compliance — Triggers, Process, Verification, Safety all present
- Tool dependencies exact match with upstream intent
- Added Safety section (idempotency, reversibility, cost awareness)

### security-ownership-map (analyzer)
- Added all 4 analyzer template sections: Checklist, Metrics, Report Format, Interpretation Guide
- New sensitivity-patterns.md reference (800 tokens) expanding tag documentation
- Added CODEOWNERS validation as formal checklist category

### verification-before-completion (validator)
- Lowest intent confidence (0.46) — behavioral skill without technical artifacts
- Core message preserved verbatim ("Evidence before assertions, always")
- Restructured patterns into 7 formal rules with severity levels
- New reference: verification-commands.md with language-specific patterns

## Key Findings

1. **All 5 pass Platxa validation** — frontmatter, tokens, provenance all correct
2. **hugging-face-model-trainer was the biggest fix** — upstream exceeded every token limit
3. **Type template compliance is strong** — 4/5 fully match, 1 partial (reasonable adaptation)
4. **All add provenance metadata** — enables upstream tracking in expansion pipeline
5. **Intent confidence correlates with upstream richness** — 0.46-0.91 range reflects content density
