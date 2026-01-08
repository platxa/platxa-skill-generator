# Existing Skill Analyzer

Pattern for analyzing existing skills to learn patterns and structures.

## Skill Discovery

### Finding Installed Skills

```markdown
# User skills
Glob("~/.claude/skills/*/SKILL.md")

# Project skills
Glob(".claude/skills/*/SKILL.md")

# System skills (if accessible)
Glob("/usr/share/claude/skills/*/SKILL.md")
```

### Listing All Skills

```markdown
1. Run Glob to find SKILL.md files
2. Extract skill names from paths
3. Categorize by location (user/project)
4. Return list with metadata
```

## Skill Analysis Process

### Step 1: Read SKILL.md

```markdown
For each skill found:
  Read("{skill_path}/SKILL.md")

Extract:
  - YAML frontmatter (name, description, allowed-tools)
  - Section headers
  - Content structure
  - Examples
```

### Step 2: Analyze Structure

```markdown
Glob("{skill_path}/*")
Glob("{skill_path}/**/*")

Map directory structure:
  - scripts/ present?
  - references/ present?
  - assets/ present?
  - Other directories?
```

### Step 3: Examine Scripts

```markdown
IF scripts/ exists:
  Glob("{skill_path}/scripts/*.sh")

  For each script:
    Read(script_path)

    Analyze:
      - Purpose (from comments)
      - Input/output patterns
      - Error handling approach
      - Dependencies
```

### Step 4: Examine References

```markdown
IF references/ exists:
  Glob("{skill_path}/references/**/*.md")

  For each reference:
    Read(reference_path)

    Analyze:
      - Topic covered
      - Depth of content
      - Structure used
```

## Pattern Extraction

### SKILL.md Patterns

```json
{
  "frontmatter_patterns": {
    "common_tools": ["Read", "Write", "Edit", "Bash"],
    "avg_description_length": 150,
    "common_tags": ["automation", "builder", "cli"]
  },
  "section_patterns": {
    "always_present": ["Overview", "Workflow"],
    "often_present": ["Examples", "Configuration"],
    "sometimes_present": ["Troubleshooting", "FAQ"]
  },
  "content_patterns": {
    "uses_code_blocks": true,
    "uses_tables": true,
    "uses_checklists": true,
    "avg_example_count": 2
  }
}
```

### Script Patterns

```json
{
  "naming": {
    "verbs": ["validate", "generate", "install", "check"],
    "format": "verb-noun.sh"
  },
  "structure": {
    "has_shebang": true,
    "has_set_flags": true,
    "has_usage_function": true,
    "has_error_handling": true
  },
  "common_patterns": [
    "argument parsing with getopts",
    "color output functions",
    "cleanup traps"
  ]
}
```

### Reference Patterns

```json
{
  "organization": {
    "by_topic": ["concepts/", "guides/", "api/"],
    "by_type": ["templates/", "examples/", "checklists/"]
  },
  "content_depth": {
    "overview_docs": "1-2 pages",
    "detailed_guides": "3-5 pages",
    "reference_docs": "varies"
  }
}
```

## Example Skill Analysis

### Analyzing skill-creator-pro

```markdown
Glob("~/.claude/skills/skill-creator-pro/SKILL.md")
Read("~/.claude/skills/skill-creator-pro/SKILL.md")

Findings:
- Type: Builder
- Tools: Read, Write, Edit, Bash, Task, WebSearch
- Sections: Overview, Workflow (5 phases), Templates, Examples
- Has: scripts/, references/
- Scripts: validate.sh, install.sh, generate.sh
- References: templates/, patterns/, examples/
```

### Analyzing mcp-builder

```markdown
Glob("~/.claude/skills/mcp-builder/SKILL.md")
Read("~/.claude/skills/mcp-builder/SKILL.md")

Findings:
- Type: Builder
- Tools: Read, Write, Edit, Bash, Glob, Grep
- Sections: Overview, MCP Concepts, Workflow, Server Types
- Has: scripts/, references/, assets/
- Scripts: scaffold.sh, test-server.sh
- References: mcp-spec.md, server-templates/
- Assets: boilerplate code
```

## Aggregated Insights

### Common Patterns Across Skills

```markdown
1. **Structure**
   - All have SKILL.md with valid frontmatter
   - Most have scripts/ for automation
   - Many have references/ for expertise

2. **Sections**
   - Overview always present
   - Workflow usually present
   - Examples highly recommended

3. **Tools**
   - Read/Write/Edit: universal
   - Bash: for automation
   - Task: for subagents
   - WebSearch: for research

4. **Quality**
   - Clear, actionable workflows
   - Real examples (not placeholders)
   - Scripts are tested and documented
```

## Integration with Discovery

### In Discovery Prompt

```markdown
Analyze existing skills to learn patterns:

1. Find skills in ~/.claude/skills/
2. For each relevant skill:
   - Read SKILL.md
   - Note structure and sections
   - Identify patterns used
3. Aggregate common patterns
4. Apply learnings to new skill design

Focus on skills similar to: {skill_description}
```

### Output Format

```json
{
  "skills_analyzed": 5,
  "relevant_skills": [
    {
      "name": "skill-creator-pro",
      "relevance": "high",
      "patterns_learned": ["multi-phase workflow", "validation scripts"]
    }
  ],
  "aggregated_patterns": {
    "structure": ["scripts/", "references/"],
    "sections": ["Overview", "Workflow", "Examples"],
    "tools": ["Read", "Write", "Task"]
  },
  "recommendations": [
    "Use 5-phase workflow like skill-creator-pro",
    "Include validation script"
  ]
}
```
