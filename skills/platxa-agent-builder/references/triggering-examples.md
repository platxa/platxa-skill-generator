# Triggering Examples Reference

Guide to writing effective `<example>` blocks that control when Claude launches your agent.

## Example Block Anatomy

```markdown
<example>
Context: The user has just finished implementing a new feature.
user: "Can you review my code changes?"
assistant: "I'll use the code-reviewer agent to analyze your changes."
<commentary>
Since the user wants code review, launch the code-reviewer agent.
</commentary>
</example>
```

**Components:**

| Part | Required | Purpose |
|------|----------|---------|
| `Context:` | Recommended | Sets the scene — what happened before |
| `user:` | One of user/assistant | What the user says to trigger |
| `assistant:` | One of user/assistant | How Claude responds |
| `<commentary>` | Recommended | Explains WHY to trigger (training signal) |

## Example Types

### 1. Explicit Request

User directly asks for the agent's capability:

```markdown
<example>
user: "Review this pull request for security issues"
assistant: "I'll launch the security-analyzer agent to scan for vulnerabilities."
</example>
```

**When to use:** Always include at least one explicit request example.

### 2. Proactive Trigger

Agent should launch without being asked:

```markdown
<example>
Context: The assistant just finished writing authentication code with password handling.
assistant: "I've implemented the auth flow. Let me proactively run the security-analyzer to check for vulnerabilities in the password handling."
<commentary>
Security-sensitive code (authentication, encryption, user input handling) should trigger proactive security review without waiting for the user to ask.
</commentary>
</example>
```

**When to use:** For agents that should auto-trigger in specific situations.

### 3. Implicit Request

User implies the need without naming the specific task:

```markdown
<example>
Context: User is preparing to create a pull request.
user: "I think this module is ready for production"
assistant: "Before deploying, let me run the quality-validator agent to ensure production readiness."
<commentary>
"Ready for production" implies the need for quality validation even though the user didn't explicitly request it.
</commentary>
</example>
```

**When to use:** When the agent covers common implied needs.

### 4. Context-Dependent Trigger

The trigger depends on what just happened:

```markdown
<example>
Context: The assistant just generated a new API endpoint with database queries.
assistant: "I've created the endpoint. Let me run the security-analyzer to check the database queries for injection vulnerabilities."
<commentary>
New database queries warrant automated security scanning.
</commentary>
</example>
```

**When to use:** When code context determines if the agent should run.

## Best Practices

### Include Variety

Always include 2-4 examples covering different scenarios:

```yaml
description: |
  Use this agent when...

  <example>           # 1. Explicit request
  user: "Review my code"
  ...
  </example>

  <example>           # 2. Proactive trigger
  Context: After writing code...
  assistant: "Let me review..."
  ...
  </example>

  <example>           # 3. Implicit request
  user: "Is this ready to merge?"
  ...
  </example>
```

### Use Specific Keywords

Include words that match real user requests:

**Good:** `"Check this code for security issues"` — matches "security", "check", "issues"
**Bad:** `"Please invoke this agent"` — no one says this

### Commentary Teaches Reasoning

Commentary tells Claude WHY to trigger, not just WHEN:

**Good commentary:**
```markdown
<commentary>
Authentication code handles sensitive credentials and should always
be security-reviewed before merging, even if the user doesn't ask.
</commentary>
```

**Bad commentary:**
```markdown
<commentary>
Use the security-analyzer agent here.
</commentary>
```

## Debugging Triggers

### Agent Not Triggering

**Symptoms:** Claude doesn't launch the agent when expected.

**Fixes:**
- Add more example blocks covering the missed scenario
- Make keywords in examples match user's actual language
- Add commentary explaining the reasoning
- Check that description's first sentence clearly states when to trigger

### Agent Triggering Too Often

**Symptoms:** Agent launches for unrelated requests.

**Fixes:**
- Make examples more specific (narrow the scope)
- Add "Does NOT" section to description
- Use commentary to explain when NOT to trigger
- Reduce overlap with other agents' descriptions

### Wrong Agent Triggered

**Symptoms:** A different agent launches instead.

**Fixes:**
- Differentiate descriptions between overlapping agents
- Use distinct keywords in examples
- Add negative examples ("This is NOT a security review, it's a code quality review")

## Template Library

### For Code Review Agents
```markdown
<example>
Context: User completed implementing a feature with multiple file changes.
user: "Can you review my changes before I create a PR?"
assistant: "I'll use the code-reviewer agent to thoroughly analyze your changes."
<commentary>
Pre-PR review is a clear trigger for code review agents.
</commentary>
</example>
```

### For Test Generation Agents
```markdown
<example>
Context: User just implemented a new utility function without tests.
user: "This function needs tests"
assistant: "I'll use the test-generator agent to create comprehensive tests."
<commentary>
Explicit request for test creation triggers the test generator.
</commentary>
</example>
```

### For Documentation Agents
```markdown
<example>
Context: User added several new API endpoints without documentation.
user: "We need to document these new endpoints"
assistant: "I'll use the docs-generator agent to create API documentation."
<commentary>
New undocumented APIs should trigger documentation generation.
</commentary>
</example>
```

### For Security Agents
```markdown
<example>
Context: The assistant just wrote code that handles user input from a web form.
assistant: "I've implemented the form handler. Let me proactively scan it for input validation and injection vulnerabilities."
<commentary>
User input handling is a high-risk area that warrants proactive security review.
</commentary>
</example>
```

### For Validation Agents
```markdown
<example>
Context: User is about to merge a feature branch.
user: "I think we're ready to merge this"
assistant: "Let me run the quality-validator first to ensure everything meets our standards."
<commentary>
Pre-merge is a natural checkpoint for quality validation.
</commentary>
</example>
```
