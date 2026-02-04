# Transformation Examples

Extended before/after examples for all common task types.

## Bug Fix

```
BEFORE: fix the login bug

AFTER: users report login fails after session timeout.
check the auth flow in src/auth/, especially token refresh
in refresh_token.ts. write a failing test that reproduces
the issue, then fix it. verify by running the auth test suite.

ADDED: symptom, location, verification (failing test), success criteria
```

## Feature Implementation

```
BEFORE: add a search feature

AFTER: implement search for the products page. look at how
filtering works in ProductList.tsx for the pattern. search
should filter by name and category. add tests for: empty
query returns all, partial match works, no results shows
message. no external search libraries.

ADDED: location, reference pattern, specific behavior, test cases, constraint
```

## Refactoring

```
BEFORE: make the code better

AFTER: refactor utils.js to use ES2024 features while
maintaining the same behavior. specifically: convert
callbacks to async/await, use optional chaining, add
TypeScript types. run the existing test suite after each
change to ensure nothing breaks.

ADDED: specific changes, constraint (same behavior), verification per step
```

## Testing

```
BEFORE: add tests for foo.py

AFTER: write tests for foo.py covering the edge case where
the user is logged out. avoid mocks. use the existing test
patterns in tests/. test cases: logged_out_user returns 401,
expired_session redirects to login, invalid_token raises
AuthError. run and confirm all pass.

ADDED: specific edge case, constraint (no mocks), pattern reference, cases
```

## Debugging / Performance

```
BEFORE: the API is slow

AFTER: the /api/orders endpoint takes 3+ seconds for large
orders (1000+ items). profile the database queries in
OrderService.ts. look for N+1 queries or missing indexes.
fix the performance issue and verify response time is
under 500ms with a 1000-item test payload.

ADDED: specific endpoint, threshold, location, measurable success
```

## UI Changes

```
BEFORE: fix the button styling

AFTER: [paste screenshot of design] update the primary button
in Button.tsx to match this design. check the theme config
in tailwind.config.js. take a screenshot after changes and
compare to the design. list any differences.

ADDED: design reference, file locations, visual verification
```

## Exploration / Understanding

```
BEFORE: how does auth work?

AFTER: read src/auth/ and explain how authentication works
in this codebase. cover: how sessions are created, how
tokens are refreshed, where secrets are stored. summarize
in a markdown doc with file:line references.

ADDED: specific files, specific questions to answer, output format
```

## Migration

```
BEFORE: upgrade to React 18

AFTER: migrate from React 17 to React 18. first, read the
migration guide at https://react.dev/blog/2022/03/08/react-18-upgrade-guide.
identify all components using deprecated APIs (findDOMNode,
legacy context, string refs). update one component at a
time, running tests after each. do not change unrelated code.

ADDED: phased approach, reference docs, incremental verification, constraint
```

## With Verification Report

```
BEFORE: fix the API error

AFTER: the /api/orders endpoint returns 500 for large orders.
check OrderService.ts for the error. address the root cause,
do not suppress the error. after fixing, run the test suite
and summarize what passed and what you verified.

ADDED: symptom, location, root cause enforcement, verification report
```

## Complex Multi-Phase Task

```
BEFORE: add OAuth

AFTER:
Phase 1 - EXPLORE: read src/auth/ and understand current
  session handling. note how tokens are stored and refreshed.

Phase 2 - PLAN: create a plan for adding Google OAuth.
  list files to change, new files to create, and env vars
  needed. write the plan to docs/oauth-plan.md for review.

Phase 3 - IMPLEMENT: implement OAuth following the plan.
  write tests for the callback handler and token exchange.
  run tests after each file change. no new auth libraries
  beyond passport-google-oauth20.

Phase 4 - VERIFY: run the full test suite. verify login
  flow works end-to-end. commit with descriptive message.

ADDED: phased structure, exploration first, specific tests, constraint, verification
```

## Prompt Quality Scoring

Each transformed prompt should pass these checks:

| Principle | Pass | Fail |
|-----------|------|------|
| Verification | "run tests", "screenshot matches", "response < 500ms" | Nothing, "make it faster" |
| Specificity | `src/auth/login.ts`, `processPayment()` | "the auth code", "that function" |
| Constraints | "no mocks", "only auth module", "root cause" | Open-ended, unlimited scope |
| Structure | Single task, phased if complex | Multiple goals, jump to code |
| Rich Content | Pasted error, @file, screenshot | "it is broken", "that file" |

**Target**: Every transformed prompt should pass at least 4 of 5 principles.
