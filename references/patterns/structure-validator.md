# Structure Completeness Validator

Validate skill directory structure and file completeness.

## Purpose

Ensure generated skills have all required and expected files in the correct locations before installation.

## Expected Structure by Skill Type

### Minimal Structure (All Types)

```
skill-name/
├── SKILL.md              # Required - main skill file
└── references/           # Optional - supporting docs
    └── *.md
```

### Builder Skill Structure

```
builder-skill/
├── SKILL.md
├── scripts/
│   └── generate.sh       # Or generate.py
└── references/
    ├── templates/
    │   └── *.template
    └── patterns/
        └── *.md
```

### Automation Skill Structure

```
automation-skill/
├── SKILL.md
├── scripts/
│   ├── main.sh           # Primary script
│   └── helpers/          # Optional helpers
└── references/
    └── workflow.md
```

### Guide/Analyzer/Validator Structures

```
guide-or-analyzer/
├── SKILL.md
└── references/
    ├── concepts.md       # Domain knowledge
    └── best-practices.md # Guidelines
```

## Validation Algorithm

```python
def validate_structure(skill_dir: Path, skill_type: str) -> StructureResult:
    """
    Validate skill directory structure completeness.

    Args:
        skill_dir: Path to skill directory
        skill_type: One of: builder, guide, automation, analyzer, validator

    Returns:
        StructureResult with passed, missing, extra, warnings
    """
    errors = []
    warnings = []
    found_files = []
    missing_files = []

    # 1. Required files (all types)
    required = ['SKILL.md']

    for req in required:
        path = skill_dir / req
        if path.exists():
            found_files.append(req)
        else:
            missing_files.append(req)
            errors.append(f"Missing required file: {req}")

    # 2. Type-specific requirements
    type_requirements = get_type_requirements(skill_type)

    for req in type_requirements.required:
        path = skill_dir / req
        if not path.exists():
            missing_files.append(req)
            errors.append(f"Missing required file for {skill_type}: {req}")
        else:
            found_files.append(req)

    for rec in type_requirements.recommended:
        path = skill_dir / rec
        if not path.exists():
            warnings.append(f"Missing recommended file: {rec}")

    # 3. Check references directory
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        ref_result = validate_references_structure(refs_dir, skill_type)
        errors.extend(ref_result.errors)
        warnings.extend(ref_result.warnings)
        found_files.extend(ref_result.found)

    # 4. Check scripts directory (if applicable)
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        script_result = validate_scripts_structure(scripts_dir)
        errors.extend(script_result.errors)
        warnings.extend(script_result.warnings)
        found_files.extend(script_result.found)

    # 5. Check for unexpected files
    all_files = list(skill_dir.rglob("*"))
    expected_patterns = get_expected_patterns(skill_type)
    for f in all_files:
        if f.is_file() and not matches_expected(f, expected_patterns):
            warnings.append(f"Unexpected file: {f.relative_to(skill_dir)}")

    return StructureResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        found_files=found_files,
        missing_files=missing_files,
        completeness_score=calculate_completeness(found_files, missing_files)
    )
```

## Type Requirements

```python
TYPE_REQUIREMENTS = {
    "builder": {
        "required": [],
        "recommended": ["scripts/", "references/templates/"],
        "expected_patterns": ["*.md", "scripts/*.sh", "scripts/*.py", "references/**/*.md"]
    },
    "guide": {
        "required": [],
        "recommended": ["references/"],
        "expected_patterns": ["*.md", "references/**/*.md"]
    },
    "automation": {
        "required": ["scripts/"],
        "recommended": ["references/workflow.md"],
        "expected_patterns": ["*.md", "scripts/*.sh", "scripts/*.py", "references/**/*.md"]
    },
    "analyzer": {
        "required": [],
        "recommended": ["references/"],
        "expected_patterns": ["*.md", "scripts/*.sh", "scripts/*.py", "references/**/*.md"]
    },
    "validator": {
        "required": ["scripts/"],
        "recommended": ["references/"],
        "expected_patterns": ["*.md", "scripts/*.sh", "scripts/*.py", "references/**/*.md"]
    }
}
```

## File Validation Checks

### SKILL.md Validation

```python
def validate_skill_md(skill_md: Path) -> FileValidation:
    """Validate SKILL.md file completeness."""
    errors = []
    warnings = []

    if not skill_md.exists():
        return FileValidation(valid=False, errors=["SKILL.md not found"])

    content = skill_md.read_text()

    # Check file is not empty
    if len(content.strip()) < 100:
        errors.append("SKILL.md appears incomplete (< 100 chars)")

    # Check has frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md missing frontmatter (must start with ---)")

    # Check frontmatter is closed
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("SKILL.md frontmatter not properly closed")

    # Check has content after frontmatter
    if len(parts) >= 3 and len(parts[2].strip()) < 50:
        warnings.append("SKILL.md has minimal content after frontmatter")

    # Check encoding
    try:
        content.encode('utf-8')
    except UnicodeEncodeError:
        errors.append("SKILL.md contains invalid UTF-8 characters")

    return FileValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

### Reference Files Validation

```python
def validate_references_structure(refs_dir: Path, skill_type: str) -> RefValidation:
    """Validate references directory structure."""
    errors = []
    warnings = []
    found = []

    # Check for at least one reference file
    md_files = list(refs_dir.glob("**/*.md"))
    if not md_files:
        warnings.append("references/ directory is empty")
    else:
        found.extend([f.name for f in md_files])

    # Check file sizes
    for md_file in md_files:
        size = md_file.stat().st_size
        if size < 100:
            warnings.append(f"{md_file.name}: File appears empty or minimal")
        if size > 50000:  # ~50KB
            warnings.append(f"{md_file.name}: File unusually large ({size} bytes)")

    # Check for broken internal links
    for md_file in md_files:
        broken = check_internal_links(md_file, refs_dir)
        for link in broken:
            warnings.append(f"{md_file.name}: Broken link to {link}")

    return RefValidation(
        errors=errors,
        warnings=warnings,
        found=found
    )
```

### Scripts Validation

```python
def validate_scripts_structure(scripts_dir: Path) -> ScriptValidation:
    """Validate scripts directory structure."""
    errors = []
    warnings = []
    found = []

    # Find script files
    scripts = list(scripts_dir.glob("*.sh")) + list(scripts_dir.glob("*.py"))

    if not scripts:
        errors.append("scripts/ directory contains no .sh or .py files")
        return ScriptValidation(errors=errors, warnings=warnings, found=[])

    found.extend([s.name for s in scripts])

    for script in scripts:
        # Check executable bit for shell scripts
        if script.suffix == '.sh':
            if not os.access(script, os.X_OK):
                warnings.append(f"{script.name}: Not executable (missing chmod +x)")

        # Check shebang
        content = script.read_text()
        if not content.startswith('#!'):
            warnings.append(f"{script.name}: Missing shebang line")

        # Check not empty
        if len(content.strip()) < 50:
            errors.append(f"{script.name}: Script appears empty or minimal")

    return ScriptValidation(
        errors=errors,
        warnings=warnings,
        found=found
    )
```

## Completeness Score

```python
def calculate_completeness(found: list, missing: list) -> float:
    """
    Calculate structure completeness score.

    Returns:
        Score from 0.0 to 1.0
    """
    total = len(found) + len(missing)
    if total == 0:
        return 1.0

    return len(found) / total
```

## Output Format

```json
{
  "structure_validation": {
    "passed": true,
    "completeness_score": 0.92,
    "found_files": [
      "SKILL.md",
      "references/concepts.md",
      "references/best-practices.md",
      "scripts/validate.sh"
    ],
    "missing_files": [],
    "errors": [],
    "warnings": [
      "scripts/validate.sh: Not executable"
    ]
  }
}
```

## Integration

Called during validation phase:

```python
# In validation workflow
structure = validate_structure(skill_dir, skill_type)

if not structure.passed:
    return ValidationResult(
        passed=False,
        phase="structure",
        errors=structure.errors
    )

# Continue to spec compliance check...
```
