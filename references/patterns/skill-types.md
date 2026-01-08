# Skill Types Reference

Classification system for Claude Code skills based on primary function.

## The Five Skill Types

### 1. Builder

**Purpose**: Create new artifacts (code, documents, configurations)

**Characteristics**:
- Produces tangible outputs
- Follows templates or patterns
- Requires output validation

**Key Sections**:
- Workflow (step-by-step creation process)
- Templates (starting points)
- Output Checklist (quality verification)

**Example Skills**:
- API endpoint generator
- React component scaffolder
- Database migration creator

**Typical Tools**: Write, Edit, Bash, Task

---

### 2. Guide

**Purpose**: Teach or explain concepts, processes, or best practices

**Characteristics**:
- Educational focus
- Progressive disclosure of information
- Interactive Q&A support

**Key Sections**:
- Overview (what you'll learn)
- Steps (learning progression)
- Best Practices (key takeaways)
- Examples (real-world applications)

**Example Skills**:
- Git workflow guide
- TypeScript migration guide
- Security best practices

**Typical Tools**: Read, WebSearch, WebFetch

---

### 3. Automation

**Purpose**: Automate repetitive tasks or workflows

**Characteristics**:
- Minimal user interaction
- Idempotent operations
- Clear success/failure states

**Key Sections**:
- Triggers (when to run)
- Process (what it does)
- Verification (how to confirm success)

**Example Skills**:
- Code formatter
- Dependency updater
- Log analyzer

**Typical Tools**: Bash, Read, Write, Glob, Grep

---

### 4. Analyzer

**Purpose**: Inspect, audit, or evaluate code/data

**Characteristics**:
- Read-only (doesn't modify)
- Produces reports or metrics
- Identifies issues or patterns

**Key Sections**:
- Checklist (what to check)
- Metrics (what to measure)
- Report Format (output structure)

**Example Skills**:
- Code complexity analyzer
- Dependency auditor
- Performance profiler

**Typical Tools**: Read, Grep, Glob, Bash

---

### 5. Validator

**Purpose**: Verify quality, compliance, or correctness

**Characteristics**:
- Pass/fail outcomes
- Rule-based evaluation
- Threshold enforcement

**Key Sections**:
- Rules (what must be true)
- Thresholds (acceptable limits)
- Pass/Fail Criteria (decision logic)

**Example Skills**:
- Schema validator
- Style guide enforcer
- Security compliance checker

**Typical Tools**: Read, Grep, Bash

---

## Type Selection Guide

| If the skill primarily... | Choose |
|---------------------------|--------|
| Creates new files/code | Builder |
| Teaches or explains | Guide |
| Runs tasks automatically | Automation |
| Inspects without changing | Analyzer |
| Checks pass/fail criteria | Validator |

## Hybrid Skills

Some skills combine multiple types. Choose the **primary** type for classification, but incorporate patterns from secondary types as needed.

Example: A "Code Review" skill might be:
- **Primary**: Analyzer (inspects code)
- **Secondary**: Validator (checks rules)
- **Tertiary**: Guide (explains issues)
