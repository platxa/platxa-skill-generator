# Universal Code Review Checklist

Language-agnostic checklist organized by review dimension.

## Code Quality

### Complexity

- [ ] No function exceeds cyclomatic complexity of 10
- [ ] No function exceeds 50 lines
- [ ] Maximum nesting depth is 3 (prefer early returns)
- [ ] No file exceeds 500 lines
- [ ] Each function has a single, clear responsibility

### Duplication

- [ ] No identical code blocks of 3+ lines appear more than once
- [ ] Similar logic extracted into shared functions
- [ ] Constants used instead of magic numbers/strings
- [ ] Configuration centralized (not scattered across files)

### Naming

- [ ] Variables describe their content (not `x`, `tmp`, `data`)
- [ ] Functions describe their action (verb-noun: `get_user`, `validate_input`)
- [ ] Booleans use `is_`, `has_`, `can_`, `should_` prefixes
- [ ] Abbreviations are avoided or universally understood
- [ ] Naming follows language conventions (snake_case, camelCase, PascalCase)

### SOLID Principles

- [ ] Single Responsibility: each class/module has one reason to change
- [ ] Open/Closed: can extend behavior without modifying existing code
- [ ] Liskov Substitution: subtypes don't violate base type contracts
- [ ] Interface Segregation: no client depends on methods it doesn't use
- [ ] Dependency Inversion: depends on abstractions, not concrete implementations

### Structure

- [ ] No dead code (unused functions, unreachable branches)
- [ ] No unused imports
- [ ] No commented-out code blocks
- [ ] Consistent file organization (imports, constants, classes, functions)

## Security

### Secrets

- [ ] No API keys, passwords, or tokens in source code
- [ ] No hardcoded database connection strings with credentials
- [ ] No private keys or certificates in repository
- [ ] Secrets loaded from environment or secrets manager

### Injection

- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] Shell commands use safe APIs (no unescaped user input)
- [ ] No eval/exec with dynamic input
- [ ] HTML output properly escaped (no raw user input in templates)
- [ ] File paths validated (no path traversal: `../`)

### Authentication and Authorization

- [ ] All endpoints require authentication (unless intentionally public)
- [ ] Authorization checked per resource (not just per endpoint)
- [ ] No client-side-only auth checks
- [ ] Session/token expiry configured
- [ ] Failed auth attempts don't leak information

### Data Protection

- [ ] Sensitive data not logged (passwords, tokens, PII)
- [ ] Error messages don't expose internals (stack traces, SQL, paths)
- [ ] Encryption used for sensitive data at rest
- [ ] HTTPS enforced for data in transit

## Efficiency

### Algorithmic

- [ ] Algorithm complexity matches data size expectations
- [ ] No quadratic (O(n^2)) where linear (O(n)) is possible
- [ ] Sorting uses built-in implementations (not hand-rolled)
- [ ] Binary search used for sorted data lookups
- [ ] Hash maps used for frequent lookups (not linear search)

### Database

- [ ] No N+1 queries (use JOINs, prefetch, or batch)
- [ ] Queries filter server-side (not fetch-all-then-filter)
- [ ] Indexes exist for frequently queried columns
- [ ] Pagination used for large result sets
- [ ] Transactions scoped minimally

### Memory and I/O

- [ ] No object creation inside tight loops
- [ ] Strings built with join/builder (not concatenation in loops)
- [ ] Large datasets use streaming/generators (not load all in memory)
- [ ] Files and connections closed after use (context managers, try-finally)
- [ ] Collections have bounded growth (max size or eviction)

### Async

- [ ] No blocking I/O in async event loops
- [ ] Async operations properly awaited
- [ ] Concurrent work uses parallel execution (not sequential awaits)
- [ ] Timeouts set on external calls

## Maintainability

### Type Safety

- [ ] Public function parameters and return types annotated
- [ ] No `any` types (TypeScript) or missing type hints (Python)
- [ ] Generic types used where applicable
- [ ] Type narrowing used instead of casting

### Error Handling

- [ ] Specific exception types caught (not bare catch-all)
- [ ] No empty catch/except blocks
- [ ] Errors include context (what failed, why, what to do)
- [ ] Resources cleaned up in finally/defer/context manager
- [ ] Error states don't leave system in inconsistent state

### Documentation

- [ ] Public APIs have docstrings/JSDoc with params and returns
- [ ] Non-obvious logic has inline comments explaining WHY
- [ ] No placeholder documentation (TODO, TBD, FIXME without context)
- [ ] README updated if public API changed

### Testability

- [ ] Dependencies are injectable (not hard-coded)
- [ ] Side effects isolated to boundaries
- [ ] Pure functions preferred for business logic
- [ ] No global mutable state
- [ ] Functions return values (not just mutate state)

## Quick Reference: Red Flags

Patterns that should always be flagged:

| Pattern | Severity | Why |
|---------|----------|-----|
| Hardcoded secret | Critical | Security breach risk |
| eval() with user input | Critical | Code injection |
| SQL concatenation | Critical | SQL injection |
| Empty catch block | High | Silent failures |
| CC > 15 | High | Untestable, bug-prone |
| N+1 queries | High | Performance degradation |
| No type hints on public API | Medium | Maintenance burden |
| Magic numbers | Medium | Unclear intent |
| Dead code | Low | Clutter |
| Missing docstring | Low | Onboarding friction |
