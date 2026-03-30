# Codebase Review Guide

Systematic workflow for reviewing an entire codebase module-by-module.

## Phase 1: Discovery

Map the codebase structure:

```bash
# Count files by language
find . -type f -name "*.py" ! -path "*/node_modules/*" | wc -l
find . -type f -name "*.ts" ! -path "*/node_modules/*" | wc -l
```

Identify logical modules (top-level directories or packages). Group files into review batches by module. Prioritize: entry points, API boundaries, auth/security code, data access layers.

## Phase 2: Automated Sweep

Run scripts across the entire codebase first to get a baseline:

```bash
bash scripts/detect-secrets.sh .
bash scripts/analyze-complexity.sh .
```

This surfaces critical issues immediately before deep analysis.

## Phase 3: Module-by-Module Deep Review

Process each module independently to avoid context overflow:

1. Read all files in the module
2. Score the module across all 4 dimensions
3. Record per-module scores and issues
4. Move to next module

**Review order** (highest risk first):
1. Authentication / authorization
2. API endpoints / controllers
3. Data access / database queries
4. Business logic / domain
5. Utilities / helpers
6. Configuration / setup
7. Tests (for coverage and quality)

## Phase 4: Cross-Cutting Analysis

After individual modules, check cross-cutting concerns:
- Consistent error handling patterns across modules
- Shared security practices (auth middleware applied everywhere)
- Duplication between modules (copy-pasted logic)
- Dependency flow (no circular dependencies)
- Configuration consistency

## Phase 5: Consolidated Report

Aggregate into a codebase-level report:

```
## Codebase Review Report

**Project:** {name}
**Date:** {timestamp}
**Modules reviewed:** {count}
**Total files:** {count}
**Total lines:** {count}

### Overall: {score}/10 (Grade {letter})

### Module Scores

| Module | Files | Lines | Quality | Security | Efficiency | Maint. | Overall |
|--------|-------|-------|---------|----------|------------|--------|---------|
| auth/  | 8     | 1200  | 7.5     | 6.0      | 8.0        | 7.0    | 7.1     |
| api/   | 12    | 2400  | 8.0     | 8.5      | 7.0        | 8.0    | 7.9     |

### Hotspots (Worst Modules)

1. **auth/** (7.1/10) - Hardcoded token expiry, missing rate limiting
2. **db/** (7.3/10) - N+1 queries in 3 handlers, no connection pooling

### Cross-Cutting Issues
- {pattern found across multiple modules}

### Top 10 Priority Fixes
1. [Critical] {file}:{line} - {issue}
2. [Critical] {file}:{line} - {issue}

### Codebase Health Summary
- Strongest dimension: {name} ({avg score})
- Weakest dimension: {name} ({avg score})
- Technical debt estimate: {low/medium/high}
```

## Checklist

- [ ] All modules discovered and listed
- [ ] Each module scored independently
- [ ] Module scores table included
- [ ] Hotspots (worst modules) identified
- [ ] Cross-cutting issues analyzed
- [ ] Top priority fixes ranked across entire codebase
- [ ] Codebase health summary with strongest/weakest dimensions
