---
name: verification-before-completion
description: >-
  Use when about to claim work is complete, fixed, or passing, before committing
  or creating PRs. Requires running verification commands and confirming output
  before making any success claims. Evidence before assertions, always.
allowed-tools:
  - Bash
  - Read
  - Task
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - validator
    - verification
    - quality
    - testing
  provenance:
    upstream_source: "verification-before-completion"
    upstream_sha: "2f2d0c426d23c3adf37ebe2b29e72df39bc5ea07"
    regenerated_at: "2026-02-04T13:39:19Z"
    generator_version: "1.0.0"
    intent_confidence: 0.46
---

# Verification Before Completion

Claiming work is complete without verification is dishonesty, not efficiency.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If the verification command has not run **in this session**, the claim cannot be made. Confidence is not evidence. Previous runs are not current evidence. Partial checks prove nothing.

**Violating the letter of this rule is violating the spirit of this rule.**

## When This Skill Activates

This skill applies **immediately before**:

- Any success or completion claim ("done", "fixed", "passes", "works", "clean")
- Any expression of satisfaction ("Great!", "Perfect!", "All good!")
- Committing, pushing, or creating a PR
- Marking a task or TODO as complete
- Moving to the next task or phase
- Reporting agent-delegated work as successful
- Any paraphrase, synonym, or implication of the above

## The Verification Gate

Every claim must pass through this gate:

```
1. IDENTIFY  →  What command proves this claim?
2. RUN       →  Execute it FRESH and COMPLETE (not from memory)
3. READ      →  Full output. Check exit code. Count results.
4. VERIFY    →  Does the output actually confirm the claim?
               YES → State claim WITH evidence
               NO  → State actual status with evidence
5. ONLY THEN →  Make the claim
```

Skipping any step is a verification failure.

## Rules

### Rule 1: Test Suites

**Claim**: "Tests pass" / "All tests pass"

**Requires**: Run the full test command. Read output. Count pass/fail. Exit code 0.

**Passes when**: Command output shows 0 failures and exit code is 0.

**Fails when**: Tests not run in this session, partial suite run, or exit code non-zero.

**Severity**: Critical

### Rule 2: Type Checking

**Claim**: "No type errors" / "Types are clean"

**Requires**: Run the type checker. Read output. Confirm 0 errors.

**Passes when**: Type checker reports 0 errors with exit code 0.

**Fails when**: Only linter was run (linter ≠ type checker), or output not read.

**Severity**: Critical

### Rule 3: Build Verification

**Claim**: "Build succeeds" / "Build passes"

**Requires**: Run the build command. Confirm exit code 0.

**Passes when**: Build command completes with exit code 0.

**Fails when**: Only linter or type checker passed (neither proves build success).

**Severity**: Critical

### Rule 4: Linting

**Claim**: "No lint errors" / "Linter clean"

**Requires**: Run the linter. Read output. Confirm 0 errors/warnings at the required severity.

**Passes when**: Linter output shows 0 issues at or above threshold.

**Fails when**: Extrapolated from build success or type check pass.

**Severity**: High

### Rule 5: TDD Red-Green Cycle

**Claim**: "Regression test works" / "Test covers the bug"

**Requires**: Full red-green cycle: Write test → Run (FAIL expected) → Apply fix → Run (PASS expected).

**Passes when**: Test fails before fix and passes after fix, both verified with output.

**Fails when**: Test only run once (green), or red phase not verified.

**Severity**: Critical

### Rule 6: Agent-Delegated Work

**Claim**: "Agent completed the task" / "Changes applied"

**Requires**: Check VCS diff (`git diff`, `git status`). Verify actual file changes match expectations.

**Passes when**: Independent verification of VCS shows expected changes.

**Fails when**: Agent self-report trusted without independent file/diff verification.

**Severity**: Critical

### Rule 7: Requirements Checklist

**Claim**: "All requirements met" / "Phase complete"

**Requires**: Re-read the spec/plan. Create checklist. Verify each item individually.

**Passes when**: Every requirement has independent verification evidence.

**Fails when**: "Tests pass" used as proxy for "requirements met" — tests don't cover specs.

**Severity**: High

## Pass/Fail Criteria

### PASS — All must be true

- [ ] The verification command ran in this session (not from memory)
- [ ] Full command was run (not partial, not sampled)
- [ ] Output was read completely (not skimmed)
- [ ] Exit code was checked
- [ ] Output confirms the specific claim being made
- [ ] No rationalization was used to skip any step

### FAIL — Any triggers failure

- Claim made without running the verification command
- Partial verification used as proof of full compliance
- Agent self-report accepted without independent check
- Words like "should", "probably", "seems to" used instead of evidence
- Satisfaction expressed before verification ("Great!", "Done!")
- Previous session's results cited as current evidence

## Rationalization Prevention

These are lies, not shortcuts:

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ type checker ≠ build ≠ tests |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Worked last time" | Last time ≠ this time |
| "Code looks right" | Appearance ≠ correctness |
| "Different words, rule doesn't apply" | Spirit over letter |

### Cognitive Biases to Guard Against

- **Completion bias**: Wanting to be done creates false confidence
- **Confirmation bias**: Seeing what you want in output instead of what's there
- **Overconfidence**: Underestimating likelihood of failure
- **Sunk cost**: Investment of effort makes you want to declare victory
- **Satisficing**: "Good enough" instead of verified complete

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, "logs look good" |
| Bug fixed | Reproduce original → passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once (no red phase) |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| Types clean | Type checker: 0 errors | Linter clean |

## Examples

### Example 1: Correct Verification

```
[Runs: pytest tests/ -v]
[Output: 34 passed, 0 failed, 0 errors]
[Exit code: 0]

"All 34 tests pass."
```

### Example 2: Verification Failure Caught

```
[Runs: pnpm typecheck]
[Output: Found 3 errors in 2 files]
[Exit code: 1]

"Type checking found 3 errors in 2 files. Fixing before claiming completion."
```

### Example 3: Incorrect — Claim Without Evidence

```
❌ "Tests should pass now since I fixed the function."

This violates the Iron Law. No test command was run.
Correct: Run pytest, read output, THEN report the result.
```

### Example 4: TDD Red-Green Verification

```
[Writes regression test for bug #42]
[Runs: pytest tests/test_bug42.py -v]
[Output: 1 failed — EXPECTED (red phase confirmed)]

[Applies fix]
[Runs: pytest tests/test_bug42.py -v]
[Output: 1 passed — (green phase confirmed)]

"Regression test verified: fails without fix, passes with fix."
```

### Example 5: Agent Delegation Verification

```
[Agent reports: "Refactoring complete, all tests pass"]

[Runs: git diff --stat]
[Output: 3 files changed, 42 insertions, 18 deletions]
[Runs: pytest tests/ -v]
[Output: 34 passed, 0 failed]

"Agent changes verified: 3 files modified, all 34 tests pass."
```

## The Bottom Line

Run the command. Read the output. THEN claim the result.

No shortcuts. No exceptions. Non-negotiable.
