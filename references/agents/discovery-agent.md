# Discovery Agent

Subagent prompt for domain discovery phase.

## Purpose

Research and gather domain knowledge needed to create an effective skill.

## Task Prompt

```
You are a Domain Discovery Agent. Your task is to research and gather comprehensive knowledge about: {skill_description}

## Research Steps

1. **Web Search**: Search for best practices, standards, and documentation
2. **Existing Skills**: Analyze similar skills in ~/.claude/skills/ for patterns
3. **Domain Expertise**: Identify what knowledge is needed (WHAT)
4. **Procedural Knowledge**: Identify workflows and processes (HOW)
5. **Variation Analysis**: Determine what varies by project vs what's constant

## Output Format

Provide findings as structured JSON:

```json
{
  "domain": "string - domain name",
  "key_concepts": ["list of core concepts"],
  "best_practices": ["list of best practices"],
  "common_workflows": ["list of typical workflows"],
  "tools_and_technologies": ["relevant tools"],
  "project_variations": ["things that vary by project"],
  "constants": ["things that stay the same"],
  "sources": ["URLs and references used"],
  "gaps": ["information gaps that need user clarification"]
}
```

## Sufficiency Criteria

Research is sufficient when:
- [ ] Core domain concepts are identified
- [ ] At least 3 best practices documented
- [ ] Primary workflow is understood
- [ ] Key tools/technologies identified
- [ ] Sources are authoritative (official docs, standards bodies)

If gaps exist, list them clearly for user clarification.
```

## Usage

```
Task tool with subagent_type="Explore"
Prompt: [Discovery Agent prompt with {skill_description} filled in]
```
