# Context-Aware Tool Selection Pattern

Use when the same outcome requires different tools depending on context (file type, size,
environment, user preferences). The skill embeds a decision tree that Claude follows to
choose the right approach transparently.

## Pattern Structure

```markdown
## Decision Tree

### Step 1: Determine Context
1. Check file type and size
2. Determine best storage/processing approach:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Step 2: Execute
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link

### Step 3: Explain Choice
Tell the user why that approach was chosen.
```

## Key Techniques

- **Clear decision criteria**: File size, type, purpose — not vague heuristics
- **Fallback options**: If primary tool fails, have a backup approach
- **Transparency**: Explain the choice to the user so they can override if needed
- **No silent failures**: If a tool isn't available, say so and suggest alternatives

## When to Use

- File storage skills (different backends for different file types)
- Deployment skills (different targets based on environment)
- Communication skills (different channels based on urgency)
- Data processing skills (different tools based on data size/format)
