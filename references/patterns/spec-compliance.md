# Agent Skills Spec Compliance Checker

Validate skills against Agent Skills Spec v1.0 requirements.

## Purpose

Ensure generated skills fully comply with the official Agent Skills specification before installation. This is a hard requirement - non-compliant skills will fail to load.

## Spec Requirements Checklist

### 1. SKILL.md File Structure

```markdown
REQUIRED structure:
---
name: skill-name
description: |
  Skill description text.
[optional fields...]
---

# Skill Title

[Content sections...]
```

### 2. Frontmatter Validation

| Field | Required | Format | Validation |
|-------|----------|--------|------------|
| name | Yes | hyphen-case | `^[a-z][a-z0-9-]*[a-z0-9]$`, ≤64 chars |
| description | Yes | string | ≤1024 chars, non-empty |
| tools | No | list | Valid tool names only |
| subagent_type | No | string | Valid subagent type |
| model | No | string | opus, sonnet, haiku |
| run_in_background | No | boolean | true/false |

### 3. Name Validation Rules

```python
def validate_name(name: str) -> list[str]:
    errors = []

    # Length check
    if len(name) > 64:
        errors.append(f"Name too long: {len(name)} chars (max 64)")

    # Format check
    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name):
        errors.append("Name must be hyphen-case: lowercase, hyphens, no leading/trailing hyphens")

    # No double hyphens
    if '--' in name:
        errors.append("Name cannot contain double hyphens")

    # Minimum length
    if len(name) < 2:
        errors.append("Name must be at least 2 characters")

    return errors
```

### 4. Description Validation Rules

```python
def validate_description(desc: str) -> list[str]:
    errors = []

    # Length check
    if len(desc) > 1024:
        errors.append(f"Description too long: {len(desc)} chars (max 1024)")

    # Non-empty
    if not desc.strip():
        errors.append("Description cannot be empty")

    # Quality checks
    if desc.strip().endswith('...'):
        errors.append("Description appears incomplete (ends with ...)")

    # Placeholder detection
    placeholders = ['TODO', 'TBD', 'FIXME', '[description]', 'Add description']
    for p in placeholders:
        if p.lower() in desc.lower():
            errors.append(f"Description contains placeholder: {p}")

    return errors
```

### 5. Tools Validation

```python
VALID_TOOLS = {
    # File operations
    'Read', 'Write', 'Edit', 'MultiEdit', 'NotebookEdit',
    # Search
    'Glob', 'Grep', 'LS',
    # Execution
    'Bash', 'Task',
    # Web
    'WebFetch', 'WebSearch',
    # User interaction
    'AskUserQuestion',
    # Planning
    'TodoWrite',
    # Management
    'KillShell', 'BashOutput',
}

def validate_tools(tools: list) -> list[str]:
    errors = []

    if not isinstance(tools, list):
        errors.append("tools must be a list")
        return errors

    for tool in tools:
        if tool not in VALID_TOOLS:
            errors.append(f"Invalid tool: {tool}")

    # Check for duplicates
    if len(tools) != len(set(tools)):
        errors.append("Duplicate tools in list")

    return errors
```

### 6. Required Sections

| Section | Required | Purpose |
|---------|----------|---------|
| Title (H1) | Yes | Skill name as heading |
| Overview or Purpose | Yes | What the skill does |
| Workflow | Recommended | How to use it |
| Examples | Recommended | Usage demonstrations |

```python
def validate_sections(content: str) -> list[str]:
    errors = []
    warnings = []

    # Must have H1 title
    if not re.search(r'^# .+', content, re.MULTILINE):
        errors.append("Missing H1 title")

    # Must have overview/purpose
    if not re.search(r'^##\s+(Overview|Purpose)', content, re.MULTILINE | re.IGNORECASE):
        errors.append("Missing Overview or Purpose section")

    # Should have workflow
    if not re.search(r'^##\s+Workflow', content, re.MULTILINE | re.IGNORECASE):
        warnings.append("Missing Workflow section (recommended)")

    # Should have examples
    if not re.search(r'^##\s+Examples?', content, re.MULTILINE | re.IGNORECASE):
        warnings.append("Missing Examples section (recommended)")

    return errors, warnings
```

## Compliance Checker Algorithm

```python
def check_spec_compliance(skill_dir: Path) -> ComplianceResult:
    """
    Full spec compliance check for a skill directory.

    Returns:
        ComplianceResult with passed, errors, warnings
    """
    errors = []
    warnings = []

    skill_md = skill_dir / "SKILL.md"

    # 1. File existence
    if not skill_md.exists():
        return ComplianceResult(
            passed=False,
            errors=["SKILL.md not found"],
            warnings=[]
        )

    content = skill_md.read_text()

    # 2. Parse frontmatter
    try:
        frontmatter, body = parse_frontmatter(content)
    except FrontmatterError as e:
        errors.append(f"Invalid frontmatter: {e}")
        return ComplianceResult(passed=False, errors=errors, warnings=[])

    # 3. Validate required fields
    if 'name' not in frontmatter:
        errors.append("Missing required field: name")
    else:
        errors.extend(validate_name(frontmatter['name']))

    if 'description' not in frontmatter:
        errors.append("Missing required field: description")
    else:
        errors.extend(validate_description(frontmatter['description']))

    # 4. Validate optional fields
    if 'tools' in frontmatter:
        errors.extend(validate_tools(frontmatter['tools']))

    if 'model' in frontmatter:
        if frontmatter['model'] not in ['opus', 'sonnet', 'haiku']:
            errors.append(f"Invalid model: {frontmatter['model']}")

    # 5. Validate sections
    section_errors, section_warnings = validate_sections(body)
    errors.extend(section_errors)
    warnings.extend(section_warnings)

    # 6. Token budget check
    line_count = len(content.split('\n'))
    if line_count > 500:
        errors.append(f"SKILL.md too long: {line_count} lines (max 500)")

    word_count = len(content.split())
    est_tokens = int(word_count * 1.3)
    if est_tokens > 5000:
        warnings.append(f"SKILL.md may exceed token budget: ~{est_tokens} tokens (target <5000)")

    # 7. References validation
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        ref_errors, ref_warnings = validate_references(refs_dir)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)

    return ComplianceResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        score=calculate_compliance_score(errors, warnings)
    )
```

## Compliance Score Calculation

```python
def calculate_compliance_score(errors: list, warnings: list) -> float:
    """
    Calculate compliance score from 0.0 to 1.0.

    - Each error: -0.1 (min 0.0)
    - Each warning: -0.02
    - Perfect: 1.0
    """
    score = 1.0
    score -= len(errors) * 0.1
    score -= len(warnings) * 0.02
    return max(0.0, score)
```

## Reference Validation

```python
def validate_references(refs_dir: Path) -> tuple[list, list]:
    """Validate references directory."""
    errors = []
    warnings = []

    total_tokens = 0

    for ref_file in refs_dir.glob("**/*.md"):
        content = ref_file.read_text()

        # Per-file token check
        words = len(content.split())
        tokens = int(words * 1.3)

        if tokens > 2000:
            warnings.append(f"{ref_file.name}: {tokens} tokens (target <2000)")

        total_tokens += tokens

    # Total references check
    if total_tokens > 10000:
        errors.append(f"Total references too large: {total_tokens} tokens (max 10000)")

    return errors, warnings
```

## Output Format

```json
{
  "compliance": {
    "passed": true,
    "score": 0.96,
    "spec_version": "1.0",
    "errors": [],
    "warnings": [
      "Missing Examples section (recommended)"
    ],
    "validated": {
      "name": "api-doc-generator",
      "description_length": 156,
      "tools_count": 5,
      "line_count": 287,
      "estimated_tokens": 2150
    }
  }
}
```

## Integration with Quality Agent

The spec compliance checker is called by the Quality Agent as the first validation step:

```python
# In quality-agent validation
compliance = check_spec_compliance(skill_dir)

if not compliance.passed:
    return QualityResult(
        passed=False,
        recommendation="REJECT",
        reason="Spec compliance failed",
        errors=compliance.errors
    )

# Continue with other quality dimensions...
```

## CLI Usage

```bash
# Validate a skill
./scripts/validate-skill.sh /path/to/skill

# The script calls spec compliance checks internally
# Returns exit code 0 for pass, 1 for fail
```
