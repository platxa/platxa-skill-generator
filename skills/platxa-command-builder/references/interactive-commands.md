# Interactive Command Patterns

Guide to creating commands that gather user input through the AskUserQuestion tool.

## When to Use AskUserQuestion

### Use AskUserQuestion When:
- Multiple choice decisions with trade-offs needing explanation
- Complex options requiring context to choose
- Multi-select scenarios (choosing multiple items)
- Preference gathering for configuration
- Interactive workflows that adapt based on answers

### Use Command Arguments ($1, $2) When:
- Simple values (file paths, numbers, names)
- Known inputs the user already has
- Scriptable workflows that should be automatable
- Fast invocations where prompting would slow down

## AskUserQuestion Tool Parameters

```typescript
{
  questions: [        // 1-4 questions per call
    {
      question: "Which database should we use?",
      header: "Database",     // Short label, max 12 chars
      multiSelect: false,     // true for multiple selection
      options: [              // 2-4 options per question
        {
          label: "PostgreSQL",
          description: "Relational, ACID compliant, best for complex queries"
        },
        {
          label: "MongoDB",
          description: "Document store, flexible schema, rapid iteration"
        }
      ]
    }
  ]
}
```

**Key constraints:**
- Users can always choose "Other" to provide custom input (automatic)
- `multiSelect: true` allows selecting multiple options
- 2-4 options per question
- 1-4 questions per tool call
- Header max 12 characters

## Command Pattern: Basic Interactive

```markdown
---
description: Interactive project setup wizard
allowed-tools: AskUserQuestion, Write, Read
---

Guide through project setup.

Use AskUserQuestion to gather configuration:

**Question 1 - Deployment target:**
- header: "Deploy to"
- question: "Which deployment platform will you use?"
- options:
  - AWS (Amazon Web Services with ECS/EKS)
  - GCP (Google Cloud with GKE)
  - Local (Docker on local machine)

**Question 2 - Features to enable:**
- header: "Features"
- question: "Which features do you want to enable?"
- multiSelect: true
- options:
  - Auto-scaling (Automatic resource scaling)
  - Monitoring (Health checks and metrics)
  - CI/CD (Automated deployment pipeline)
  - Backups (Automated database backups)

Based on answers, generate configuration files.
```

## Command Pattern: Conditional Flow

```markdown
---
description: Adaptive configuration wizard
allowed-tools: AskUserQuestion, Read, Write
---

## Question 1: Deployment Complexity

Use AskUserQuestion:
- header: "Complexity"
- question: "How complex is your deployment?"
- options:
  - Simple (Single server, straightforward)
  - Standard (Multiple servers, load balancing)
  - Complex (Microservices, orchestration)

## Conditional Questions Based on Answer

If "Simple": No additional questions, use minimal config.

If "Standard": Ask about:
- Load balancing strategy
- Scaling policy

If "Complex": Ask about:
- Orchestration platform (Kubernetes, Docker Swarm)
- Service mesh (Istio, Linkerd, None)
- Monitoring stack (Prometheus, Datadog)

Generate configuration appropriate for selected complexity.
```

## Command Pattern: Confirmation Gate

```markdown
---
description: Destructive operation with confirmation
allowed-tools: AskUserQuestion, Bash
---

This operation will delete all cached data.

Use AskUserQuestion:
- header: "Confirm"
- question: "Delete all cached data? This cannot be undone."
- options:
  - Yes, delete (Proceed with deletion)
  - Cancel (Abort operation)

If "Yes": Execute deletion, report completion.
If "Cancel": Abort without changes.
```

## Command Pattern: Validation Loop

```markdown
---
description: Setup with validation
allowed-tools: AskUserQuestion, Bash, Write
---

## Gather Configuration
Use AskUserQuestion to collect settings.

## Validate Configuration
Check settings are compatible and dependencies available.

If validation fails:
  Show errors.
  Use AskUserQuestion:
  - header: "Next step"
  - question: "Configuration has issues. What would you like to do?"
  - options:
    - Fix (Adjust settings to resolve issues)
    - Override (Proceed despite warnings)
    - Cancel (Abort setup)

  Based on answer: retry, proceed, or exit.
```

## Command Pattern: Progressive Disclosure

```markdown
---
description: Smart setup with complexity levels
allowed-tools: AskUserQuestion, Write
---

## Setup Type Selection

Use AskUserQuestion:
- header: "Setup type"
- question: "How would you like to set up?"
- options:
  - Quick (Use recommended defaults)
  - Custom (Configure all options)
  - Guided (Step-by-step with explanations)

If "Quick": Apply defaults, skip detailed questions.
If "Custom": Ask all configuration questions.
If "Guided": Ask questions with explanations and recommendations.
```

## Combining Arguments and Questions

Use arguments for known values, questions for complex choices:

```markdown
---
description: Configure project
argument-hint: [project-name]
allowed-tools: AskUserQuestion, Write
---

Project: $1

Use AskUserQuestion for complex choices:
- Architecture pattern (requires explanation of trade-offs)
- Technology stack (options need descriptions)
- Deployment strategy (impacts depend on context)

These require explanation, so questions work better than arguments.
```

## Question Design Best Practices

### Good Questions
```
Question: "Which database should we use for this project?"
Header: "Database"
Options:
  - PostgreSQL (Relational, ACID compliant, best for complex queries)
  - MongoDB (Document store, flexible schema, best for rapid iteration)
  - Redis (In-memory, fast, best for caching and sessions)
```

### Poor Questions
```
Question: "Database?"           // Too vague
Header: "DB"                    // Unclear abbreviation
Options:
  - Option 1                    // Not descriptive
  - Option 2
```

### Option Design Rules

1. **Clear labels**: 1-5 words, specific and descriptive
2. **Helpful descriptions**: Explain what option means, mention trade-offs
3. **2-4 options**: Don't overwhelm with choices
4. **"Other" is automatic**: Don't add it manually

### multiSelect Guidelines

**Use multiSelect for:**
- Feature flags (user wants any combination)
- Tool selection (multiple tools can coexist)
- Module enablement (independent choices)

**Don't use multiSelect for:**
- Database engine choice (only one at a time)
- Authentication method (mutually exclusive)
- Framework selection (pick one)

## Troubleshooting

**Questions not appearing:**
- Verify `AskUserQuestion` in `allowed-tools`
- Check question format has 2-4 options
- Ensure header is max 12 characters

**Flow feels confusing:**
- Reduce number of questions
- Group related questions together
- Add explanation between stages
- Show progress through workflow

**User can't decide:**
- Add "(Recommended)" to preferred option label
- Include trade-off descriptions
- Provide context before asking
