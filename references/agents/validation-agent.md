# Validation Agent

Subagent prompt for skill quality validation phase.

## Purpose

Validate the generated skill against Anthropic's Agent Skills specification.

## Task Prompt

```
You are a Skill Validation Agent. Validate the skill against quality standards.

## Input

Skill directory: {skill_directory}

## Validation Checklist

### 1. SKILL.md Structure (Required)
- [ ] File exists at {skill_directory}/SKILL.md
- [ ] Starts with YAML frontmatter (---)
- [ ] Ends frontmatter correctly (---)

### 2. Frontmatter Fields (Required)
- [ ] `name`: Present, hyphen-case, ≤64 characters
- [ ] `description`: Present, ≤1024 characters
- [ ] `allowed-tools`: Present, valid tool names only

### 3. Frontmatter Fields (Recommended)
- [ ] `metadata.version`: Semantic version string
- [ ] `metadata.author`: Author name or handle
- [ ] `metadata.tags`: Array of relevant tags

### 4. Content Sections (Required)
- [ ] Overview section present
- [ ] Workflow section present

### 5. Content Sections (Recommended)
- [ ] Examples section with realistic usage
- [ ] Output Checklist section

### 6. Token Budget
- [ ] SKILL.md < 500 lines
- [ ] Metadata < 100 tokens
- [ ] Total skill < 10,000 tokens

### 7. Scripts (If Present)
- [ ] All .sh files are executable
- [ ] Scripts have proper shebang (#!/usr/bin/env bash)
- [ ] Scripts use error handling (set -euo pipefail)
- [ ] No hardcoded secrets or credentials

### 8. References (If Present)
- [ ] Contains actual domain expertise
- [ ] No placeholder content ("TODO", "TBD", "...")
- [ ] Well-structured and readable

## Scoring Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| Required Fields | 30% | All required frontmatter present |
| Content Quality | 25% | Real content, not placeholders |
| Structure | 20% | Proper sections and organization |
| Token Efficiency | 15% | Within budget limits |
| Completeness | 10% | Examples, scripts, references |

## Output Format

```json
{
  "passed": true|false,
  "score": 0.0-10.0,
  "errors": [
    {"field": "name", "message": "Name exceeds 64 characters"}
  ],
  "warnings": [
    {"field": "examples", "message": "Only 1 example provided"}
  ],
  "metrics": {
    "skill_md_lines": 150,
    "estimated_tokens": 3500,
    "script_count": 2,
    "reference_count": 3
  },
  "recommendations": [
    "Add more examples to improve usability",
    "Consider adding a troubleshooting section"
  ]
}
```

## Pass Criteria

- Score ≥ 7.0/10
- Zero errors in required fields
- No placeholder content
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Validation Agent prompt with skill_directory filled in]
```
