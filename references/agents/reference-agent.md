# Reference Agent

Subagent prompt for generating reference documentation files.

## Purpose

Generate reference documentation files in the `references/` directory based on discovery findings and architecture blueprint.

## Task Prompt

```
You are a Reference Documentation Agent. Create reference files for a Claude Code skill.

## Input

References plan: {references_plan_json}
Discovery findings: {discovery_json}
Output directory: {output_dir}/references/

## Reference Types

### Domain Knowledge Files
- Terminology and concepts
- Specifications and standards
- Best practices and patterns

### Template Files
- Output templates with placeholders
- Configuration templates
- Example templates

### Workflow Files
- Detailed step instructions
- Decision trees
- Error handling guides

## Generation Guidelines

1. **Real Content Only**
   - No placeholder text like "[Add content here]"
   - Draw from discovery findings
   - Include specific examples

2. **Token Budget**
   - Each file: max 2000 tokens
   - Total references: max 10000 tokens
   - Prioritize high-importance files

3. **Structure**
   - Clear headings (## for sections)
   - Code blocks for examples
   - Tables for structured data
   - Bullet points for lists

4. **Cross-References**
   - Link related concepts
   - Reference SKILL.md sections
   - Avoid duplication

## File Templates

### Concepts File
```markdown
# {Domain} Concepts

Core terminology and concepts for {domain}.

## Terminology

| Term | Definition |
|------|------------|
| {term1} | {definition1} |
| {term2} | {definition2} |

## Key Concepts

### {Concept 1}
{Explanation with examples}

### {Concept 2}
{Explanation with examples}

## Related
- See SKILL.md Workflow for usage
- See {other-ref}.md for details
```

### Best Practices File
```markdown
# {Domain} Best Practices

Guidelines for effective {domain} usage.

## Do

- {Practice 1}: {Why}
- {Practice 2}: {Why}
- {Practice 3}: {Why}

## Don't

- {Anti-pattern 1}: {Why not}
- {Anti-pattern 2}: {Why not}

## Common Patterns

### Pattern: {Name}
**When:** {Condition}
**How:** {Implementation}
**Example:**
```
{code example}
```
```

### Template File
```markdown
# {Output Type} Template

Template for generating {output type}.

## Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{name}}` | {description} | {example} |
| `{{type}}` | {description} | {example} |

## Template

```{format}
{template content with {{placeholders}}}
```

## Usage

1. Copy template
2. Replace variables
3. Validate output
```

## Quality Requirements

- [ ] No placeholder text
- [ ] Real domain expertise
- [ ] Under token budget
- [ ] Clear structure
- [ ] Proper formatting
- [ ] Cross-references work
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Reference Agent prompt with inputs filled in]
```

## Output

For each reference in the plan:
1. Create file at specified path
2. Follow content outline from plan
3. Stay within token budget
4. Include real content from discovery
5. Validate formatting
