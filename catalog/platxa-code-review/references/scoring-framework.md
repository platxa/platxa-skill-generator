# Scoring Framework

Weighted scoring system for code review across four dimensions.

## Formula

```text
Overall = (Quality x 0.30) + (Security x 0.25) + (Efficiency x 0.25) + (Maintainability x 0.20)
```

Each dimension scores 0-10. Overall maps to letter grades.

## Dimension Scoring

### Code Quality (0.30)

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| Complexity | 0.35 | 10 if avg CC<5, 8 if <8, 6 if <10, 4 if <15, 2 if >15 |
| Duplication | 0.25 | 10 if <3%, 8 if <5%, 6 if <8%, 4 if <10%, 2 if >10% |
| Naming | 0.20 | 10 if all clear, -1 per vague name (floor 2) |
| SOLID | 0.20 | 10 if followed, -2 per major violation (floor 2) |

### Security (0.25)

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| Secrets | 0.40 | 10 if none, 0 if any hardcoded secret found |
| Injection | 0.30 | 10 if safe, -3 per injection vector |
| Auth/Access | 0.15 | 10 if proper checks, -2 per missing check |
| Input Validation | 0.15 | 10 if validated at boundaries, -1 per gap |

**Hard fail**: Any hardcoded secret caps overall at 4.0.

### Efficiency (0.25)

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| Algorithm | 0.40 | 10 if optimal, -2 per unnecessary O(n) bump |
| Anti-patterns | 0.30 | 10 if none, -2 per N+1, -1.5 per loop alloc |
| Memory | 0.15 | 10 if clean, -2 per leak/unbounded growth |
| I/O | 0.15 | 10 if async-correct, -2 per blocking call |

### Maintainability (0.20)

| Sub-metric | Weight | Scoring |
|-----------|--------|---------|
| Type Safety | 0.30 | 10 if full coverage, scale by % |
| Error Handling | 0.30 | 10 if comprehensive, -2 per silent failure |
| Documentation | 0.20 | 10 if public APIs documented, scale by % |
| Testability | 0.20 | 10 if injectable deps, -2 per hard-coded dep |

## Grade Mapping

| Score | Grade | Verdict |
|-------|-------|---------|
| 9.0-10.0 | A | APPROVE - Excellent code |
| 8.0-8.9 | B | APPROVE - Good code, minor suggestions |
| 7.0-7.9 | C | APPROVE WITH SUGGESTIONS - Acceptable |
| 5.0-6.9 | D | REQUEST CHANGES - Needs improvement |
| <5.0 | F | REJECT - Major issues |

## Hard-Fail Rules

These override the calculated score:

| Condition | Max Score |
|-----------|-----------|
| Hardcoded secrets | 4.0 |
| Critical security vulnerability | 5.0 |
| Syntax errors | 3.0 |
| Failing tests (if test suite exists) | 5.0 |

## Language Adjustments

### Python
- +0.5 for full type hint coverage with strict mypy/pyright
- -0.5 for no type hints on public functions
- Check: f-strings with user input (injection risk)

### TypeScript
- +0.5 for `strict: true` with zero `any` types
- -0.5 for pervasive `any` usage
- Check: `as` type assertions hiding real issues

### Go
- +0.5 for all errors explicitly handled
- -0.5 for `_ = err` patterns
- Check: goroutine leaks, unclosed channels

### Java
- +0.5 for no raw types, proper generics
- -0.5 for catch(Exception) with no rethrow
- Check: resource leaks (missing try-with-resources)

### Rust
- +0.5 for minimal `unsafe` with documented invariants
- -0.5 for excessive `.unwrap()` in library code
- Check: panic in library functions

## Issue Severity Classification

| Severity | Definition | Score Impact |
|----------|-----------|--------------|
| Critical | Security vulnerability, data loss risk | -3.0 to auto-fail |
| High | Bug, significant quality issue | -1.5 to -2.0 |
| Medium | Style, minor pattern issue | -0.5 to -1.0 |
| Low | Suggestion, nice-to-have | -0.0 to -0.25 |

## Scoring Example

```text
File: api/handler.py (150 lines, 8 functions)

Code Quality:
  Complexity: avg CC=6.2 -> 8/10
  Duplication: 2% -> 10/10
  Naming: 1 vague name -> 9/10
  SOLID: no violations -> 10/10
  Dimension: (8*0.35)+(10*0.25)+(9*0.20)+(10*0.20) = 9.1

Security:
  Secrets: none -> 10/10
  Injection: 1 SQL concat -> 7/10
  Auth: proper -> 10/10
  Input: 1 gap -> 9/10
  Dimension: (10*0.40)+(7*0.30)+(10*0.15)+(9*0.15) = 8.95

Efficiency:
  Algorithm: optimal -> 10/10
  Anti-patterns: 1 N+1 -> 8/10
  Memory: clean -> 10/10
  I/O: correct -> 10/10
  Dimension: (10*0.40)+(8*0.30)+(10*0.15)+(10*0.15) = 9.4

Maintainability:
  Types: 80% -> 8/10
  Errors: 1 bare except -> 8/10
  Docs: 60% public -> 6/10
  Testability: good -> 9/10
  Dimension: (8*0.30)+(8*0.30)+(6*0.20)+(9*0.20) = 7.8

Overall = (9.1*0.30)+(8.95*0.25)+(9.4*0.25)+(7.8*0.20)
        = 2.73 + 2.24 + 2.35 + 1.56
        = 8.88 -> Grade B -> APPROVE
```
