# Scripts Directory Planner

Plan scripts based on skill type and required automation.

## When to Include Scripts

| Skill Type | Scripts Needed | Reason |
|------------|----------------|--------|
| Builder | Often | Validation, generation helpers |
| Guide | Rarely | Usually no automation |
| Automation | Always | Core functionality |
| Analyzer | Often | Analysis execution |
| Validator | Always | Validation execution |

## Common Script Types

### Validation Scripts

```json
{
  "name": "validate.sh",
  "purpose": "Validate skill output or input",
  "interface": {
    "args": ["<target-path>"],
    "options": ["--strict", "--quiet"],
    "exit_codes": {"0": "pass", "1": "fail", "2": "warning"}
  },
  "when_needed": "Builder, Validator skills"
}
```

### Installation Scripts

```json
{
  "name": "install.sh",
  "purpose": "Install skill to user/project location",
  "interface": {
    "args": ["<skill-dir>"],
    "options": ["--user", "--project", "--force"],
    "exit_codes": {"0": "success", "1": "failure"}
  },
  "when_needed": "All skills (standard)"
}
```

### Generation Scripts

```json
{
  "name": "generate.sh",
  "purpose": "Generate output artifacts",
  "interface": {
    "args": ["<input>", "<output-dir>"],
    "options": ["--dry-run", "--force", "--format <fmt>"],
    "exit_codes": {"0": "success", "1": "failure"}
  },
  "when_needed": "Builder skills"
}
```

### Analysis Scripts

```json
{
  "name": "analyze.sh",
  "purpose": "Run analysis and produce report",
  "interface": {
    "args": ["<target>"],
    "options": ["--output <file>", "--format <json|text>"],
    "exit_codes": {"0": "clean", "1": "issues found"}
  },
  "when_needed": "Analyzer skills"
}
```

## Planning Algorithm

```markdown
FUNCTION plan_scripts(skill_type, discovery):
    scripts = []

    # Standard scripts for all skills
    scripts.append(plan_validate_script(discovery))
    scripts.append(plan_install_script())

    # Type-specific scripts
    SWITCH skill_type:
        CASE "Builder":
            scripts.append(plan_generate_script(discovery))
            IF has_templates(discovery):
                scripts.append(plan_template_script(discovery))

        CASE "Automation":
            scripts.append(plan_run_script(discovery))
            scripts.append(plan_verify_script(discovery))

        CASE "Analyzer":
            scripts.append(plan_analyze_script(discovery))
            scripts.append(plan_report_script(discovery))

        CASE "Validator":
            scripts.append(plan_check_script(discovery))

        CASE "Guide":
            # Guides typically don't need scripts
            pass

    RETURN scripts
```

## Script Plan Output

```json
{
  "scripts_plan": {
    "include_scripts_dir": true,
    "scripts": [
      {
        "name": "validate-skill.sh",
        "purpose": "Validate generated skill against spec",
        "interface": {
          "usage": "validate-skill.sh <skill-directory>",
          "args": [
            {"name": "skill-directory", "required": true, "description": "Path to skill"}
          ],
          "options": [
            {"flag": "--strict", "description": "Fail on warnings"},
            {"flag": "--quiet", "description": "Suppress output"}
          ],
          "exit_codes": [
            {"code": 0, "meaning": "Validation passed"},
            {"code": 1, "meaning": "Validation failed"},
            {"code": 2, "meaning": "Passed with warnings"}
          ]
        },
        "dependencies": ["bash 4+"],
        "estimated_lines": 80
      },
      {
        "name": "install-skill.sh",
        "purpose": "Install skill to target location",
        "interface": {
          "usage": "install-skill.sh <skill-dir> [--user|--project]",
          "args": [
            {"name": "skill-dir", "required": true, "description": "Source directory"}
          ],
          "options": [
            {"flag": "--user", "description": "Install to ~/.claude/skills/"},
            {"flag": "--project", "description": "Install to .claude/skills/"}
          ],
          "exit_codes": [
            {"code": 0, "meaning": "Installed successfully"},
            {"code": 1, "meaning": "Installation failed"}
          ]
        },
        "dependencies": ["bash 4+"],
        "estimated_lines": 60
      }
    ]
  }
}
```

## Type-Specific Script Plans

### Builder Scripts

```json
{
  "skill_type": "Builder",
  "recommended_scripts": [
    {"name": "generate.sh", "purpose": "Generate output from input"},
    {"name": "validate.sh", "purpose": "Validate generated output"},
    {"name": "install.sh", "purpose": "Install to location"}
  ]
}
```

### Automation Scripts

```json
{
  "skill_type": "Automation",
  "recommended_scripts": [
    {"name": "run.sh", "purpose": "Execute automation"},
    {"name": "verify.sh", "purpose": "Verify execution succeeded"},
    {"name": "rollback.sh", "purpose": "Undo changes if needed"}
  ]
}
```

### Analyzer Scripts

```json
{
  "skill_type": "Analyzer",
  "recommended_scripts": [
    {"name": "analyze.sh", "purpose": "Run analysis"},
    {"name": "report.sh", "purpose": "Generate report from analysis"}
  ]
}
```

### Validator Scripts

```json
{
  "skill_type": "Validator",
  "recommended_scripts": [
    {"name": "check.sh", "purpose": "Run validation checks"},
    {"name": "fix.sh", "purpose": "Auto-fix fixable issues (optional)"}
  ]
}
```

## Script Interface Standards

### Argument Conventions

```markdown
- First arg: Target path or input
- Flags: --flag for boolean, --option <value> for values
- Help: --help shows usage
- Verbose: --verbose or -v for debug output
- Quiet: --quiet or -q for minimal output
```

### Exit Code Standards

```markdown
0 = Success / Pass
1 = Failure / Error
2 = Warning / Partial success
```

### Output Standards

```markdown
✓ = Success indicator
✗ = Failure indicator
⚠ = Warning indicator
Use colors only if terminal supports it
```

## Integration

### Used By Generation Phase

```markdown
Generation reads scripts plan:
1. Create scripts/ directory
2. For each script in plan:
   - Generate script following interface spec
   - Add proper error handling
   - Make executable
3. Test scripts work correctly
```
