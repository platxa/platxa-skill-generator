# Varies vs Constant Analyzer

Identify what changes between projects vs what remains constant.

## Why This Matters

**Constants**: Can be hardcoded or assumed by the skill
**Variables**: Must be asked, detected, or configured

This analysis determines:
- What the skill can do automatically
- What needs user input
- What should be configurable

## Categories

### Constants (Universal)

Things that are the same regardless of project:

| Category | Examples |
|----------|----------|
| Standards | JSON syntax, HTTP methods, file formats |
| Specifications | OpenAPI schema, GraphQL spec, RFC standards |
| Best practices | Security rules, code quality principles |
| Language rules | Python syntax, JavaScript semantics |
| Tool behavior | How git works, how npm installs |

### Variables (Project-Specific)

Things that differ between projects:

| Category | Examples |
|----------|----------|
| Structure | Directory layout, file naming conventions |
| Preferences | Tabs vs spaces, quote style, line length |
| Technology | Framework choice, library versions |
| Configuration | Ports, paths, environment variables |
| Business logic | Domain-specific rules, workflows |

## Classification Signals

### Constant Indicators

```markdown
Signal → Classification
─────────────────────────
"must", "shall", "always"     → Constant (specification)
"standard", "specification"    → Constant (standard)
"by definition"                → Constant (definition)
"universally", "everywhere"    → Constant (universal)
"RFC", "ISO", "W3C"           → Constant (standard body)
```

### Variable Indicators

```markdown
Signal → Classification
─────────────────────────
"typically", "usually"         → Variable (common but not universal)
"can be", "may be"            → Variable (optional)
"depends on", "varies"         → Variable (project-specific)
"configured", "customized"     → Variable (configuration)
"team preference"              → Variable (preference)
"project-specific"             → Variable (explicit)
```

## Analysis Algorithm

```markdown
FOR each finding:
    variability = analyze_variability(finding)

    IF contains_specification_language(finding):
        variability = "constant"
        confidence = 0.9

    ELIF contains_preference_language(finding):
        variability = "variable"
        confidence = 0.9

    ELIF is_from_official_spec(finding.source):
        variability = "constant"
        confidence = 0.8

    ELIF is_from_project_config(finding.source):
        variability = "variable"
        confidence = 0.8

    ELIF mentions_multiple_options(finding):
        variability = "variable"
        confidence = 0.7

    ELSE:
        variability = "unknown"
        confidence = 0.5

    RETURN {variability, confidence}
```

## Common Patterns

### Always Constant

| Domain | Constant Elements |
|--------|-------------------|
| OpenAPI | Schema structure, required fields, data types |
| Git | Command syntax, object model, ref format |
| HTTP | Status codes, method semantics, headers |
| JSON | Syntax rules, data types, escaping |
| Testing | Assert semantics, test lifecycle |

### Always Variable

| Domain | Variable Elements |
|--------|-------------------|
| Any | Project directory structure |
| Any | File naming conventions |
| Any | Framework/library choice |
| Any | Code style preferences |
| Any | Environment configuration |

### Context-Dependent

| Element | When Constant | When Variable |
|---------|---------------|---------------|
| Port numbers | Standard ports (80, 443) | Custom ports |
| File extensions | Language-mandated (.py) | Preference (.yml/.yaml) |
| Naming patterns | Language conventions | Team conventions |

## Output Structure

```json
{
  "variability_analysis": {
    "constants": [
      {
        "item": "OpenAPI uses JSON Schema for types",
        "reason": "specification requirement",
        "confidence": 0.95,
        "implications": ["Can hardcode schema validation logic"]
      },
      {
        "item": "HTTP GET is idempotent",
        "reason": "RFC 7231 specification",
        "confidence": 0.99,
        "implications": ["Can assume GET doesn't modify state"]
      }
    ],
    "variables": [
      {
        "item": "Output directory path",
        "reason": "project-specific",
        "confidence": 0.9,
        "implications": ["Must ask user or detect from config"],
        "detection_method": "Check for .claude/config or ask"
      },
      {
        "item": "Documentation format preference",
        "reason": "team preference",
        "confidence": 0.85,
        "implications": ["Should offer options"],
        "options": ["Markdown", "HTML", "Both"]
      }
    ],
    "uncertain": [
      {
        "item": "Whether to include examples",
        "reason": "could be preference or requirement",
        "confidence": 0.5,
        "resolution": "default to yes, allow disable"
      }
    ]
  }
}
```

## Skill Design Implications

### For Constants

```markdown
Action: Hardcode or assume
Example: "Always validate OpenAPI spec structure"
In SKILL.md: State as fact, don't ask
```

### For Variables

```markdown
Action: Ask, detect, or make configurable

Options:
1. Ask user (AskUserQuestion)
2. Detect from project (Read config files)
3. Make configurable (with defaults)

In SKILL.md: Document as option or ask in workflow
```

### For Uncertain

```markdown
Action: Use sensible default, allow override

Example:
  default: include_examples = true
  config: can be disabled via flag

In SKILL.md: Document default and override option
```

## Integration

### Discovery → Architecture

```markdown
variability_analysis feeds into:
- What sections need configuration
- What to hardcode in templates
- What questions to ask users
- What defaults to set
```

### Example Application

```markdown
Domain: API Documentation Generator

Constants (hardcode):
- OpenAPI spec structure validation
- HTTP method documentation order
- Standard response code meanings

Variables (ask/detect):
- Output directory
- Framework (Express/FastAPI/etc)
- Include examples? Default: yes

Result:
- Workflow asks: "Where to output docs?"
- Auto-detects framework from package.json/requirements.txt
- Defaults to including examples
```
