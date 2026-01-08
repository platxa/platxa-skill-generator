# Type-Specific Architecture Patterns

Architecture templates optimized for each skill type.

## Architecture by Skill Type

| Type | Primary Focus | Secondary Focus | Required Components |
|------|--------------|-----------------|---------------------|
| Builder | scripts/ | templates/ | generate.sh, SKILL.md |
| Guide | references/ | examples | concepts.md, workflow.md |
| Automation | scripts/ | workflow | run.sh, config handling |
| Analyzer | scripts/ | references/ | analyze.sh, report format |
| Validator | scripts/ | rules | validate.sh, rule definitions |

## Builder Architecture

### Focus: Generation Scripts

Builders create files, code, or content. They need robust generation scripts.

```
builder-skill/
├── SKILL.md                 # Generation instructions
├── references/
│   ├── output-format.md     # What gets generated
│   └── templates.md         # Template documentation
├── scripts/
│   ├── generate.sh          # Main generation script (REQUIRED)
│   ├── validate-output.sh   # Output validation
│   └── clean.sh             # Cleanup generated files
└── templates/
    ├── component.template   # Component templates
    └── config.template      # Config templates
```

### Architecture Pattern

```python
BUILDER_ARCHITECTURE = {
    "skill_md": {
        "sections": [
            "overview",           # What it builds
            "inputs",             # Required inputs
            "workflow",           # Generation steps
            "output",             # What gets created
            "examples",           # Usage examples
            "customization"       # How to customize
        ],
        "emphasis": ["workflow", "output", "customization"]
    },
    "references": {
        "required": [],
        "recommended": ["output-format.md", "templates.md"],
        "focus": "template documentation"
    },
    "scripts": {
        "required": ["generate.sh"],
        "recommended": ["validate-output.sh"],
        "focus": "generation logic"
    },
    "templates": {
        "required": True,  # Builders typically need templates
        "types": ["component", "config", "scaffold"]
    },
    "tools": ["Read", "Write", "Glob", "Bash"],
    "model": "sonnet"  # Good balance for generation
}
```

## Guide Architecture

### Focus: Reference Documentation

Guides teach concepts and procedures. They need comprehensive documentation.

```
guide-skill/
├── SKILL.md                 # Learning path overview
├── references/
│   ├── concepts.md          # Core concepts (REQUIRED)
│   ├── workflow.md          # Step-by-step procedures (REQUIRED)
│   ├── best-practices.md    # Do's and don'ts
│   ├── troubleshooting.md   # Common issues
│   └── glossary.md          # Term definitions
└── scripts/                 # Usually minimal or empty
```

### Architecture Pattern

```python
GUIDE_ARCHITECTURE = {
    "skill_md": {
        "sections": [
            "overview",           # What you'll learn
            "prerequisites",      # Required knowledge
            "learning_path",      # Structured progression
            "key_concepts",       # Main ideas summary
            "examples",           # Practical examples
            "next_steps"          # Further learning
        ],
        "emphasis": ["learning_path", "examples", "key_concepts"]
    },
    "references": {
        "required": ["concepts.md", "workflow.md"],
        "recommended": ["best-practices.md", "troubleshooting.md", "glossary.md"],
        "focus": "comprehensive documentation"
    },
    "scripts": {
        "required": [],
        "recommended": [],
        "focus": None  # Guides rarely need scripts
    },
    "templates": {
        "required": False,
        "types": []
    },
    "tools": ["Read", "Glob", "Grep"],  # Read-focused
    "model": "sonnet"  # Good for explanations
}
```

## Automation Architecture

### Focus: Workflow Execution

Automations run multi-step processes. They need robust execution scripts.

```
automation-skill/
├── SKILL.md                 # Workflow overview
├── references/
│   ├── workflow-steps.md    # Detailed step documentation
│   ├── config-options.md    # Configuration reference
│   └── error-handling.md    # Error recovery guide
├── scripts/
│   ├── run.sh               # Main execution script (REQUIRED)
│   ├── setup.sh             # Environment setup
│   ├── validate-env.sh      # Pre-flight checks
│   └── rollback.sh          # Rollback on failure
└── config/
    └── defaults.yaml        # Default configuration
```

### Architecture Pattern

```python
AUTOMATION_ARCHITECTURE = {
    "skill_md": {
        "sections": [
            "overview",           # What it automates
            "prerequisites",      # Environment requirements
            "configuration",      # Config options
            "workflow",           # Execution steps
            "monitoring",         # Progress tracking
            "error_handling",     # Failure recovery
            "examples"            # Usage examples
        ],
        "emphasis": ["workflow", "configuration", "error_handling"]
    },
    "references": {
        "required": ["workflow-steps.md"],
        "recommended": ["config-options.md", "error-handling.md"],
        "focus": "operational documentation"
    },
    "scripts": {
        "required": ["run.sh"],
        "recommended": ["setup.sh", "validate-env.sh", "rollback.sh"],
        "focus": "robust execution"
    },
    "templates": {
        "required": False,
        "types": ["config"]
    },
    "tools": ["Read", "Write", "Bash", "Glob", "TodoWrite"],
    "model": "sonnet"  # Reliable execution
}
```

## Analyzer Architecture

### Focus: Analysis Scripts

Analyzers examine code/data and report findings. They need analysis logic.

```
analyzer-skill/
├── SKILL.md                 # Analysis overview
├── references/
│   ├── analysis-rules.md    # What gets analyzed
│   ├── report-format.md     # Output format
│   └── severity-levels.md   # Issue classification
├── scripts/
│   ├── analyze.sh           # Main analysis script (REQUIRED)
│   ├── format-report.sh     # Report formatting
│   └── summarize.sh         # Summary generation
└── rules/                   # Optional: Rule definitions
    └── default-rules.yaml
```

### Architecture Pattern

```python
ANALYZER_ARCHITECTURE = {
    "skill_md": {
        "sections": [
            "overview",           # What it analyzes
            "scope",              # Analysis boundaries
            "methodology",        # How analysis works
            "output",             # Report format
            "interpretation",     # Understanding results
            "examples"            # Sample analyses
        ],
        "emphasis": ["methodology", "output", "interpretation"]
    },
    "references": {
        "required": ["analysis-rules.md"],
        "recommended": ["report-format.md", "severity-levels.md"],
        "focus": "analysis methodology"
    },
    "scripts": {
        "required": ["analyze.sh"],
        "recommended": ["format-report.sh", "summarize.sh"],
        "focus": "analysis logic"
    },
    "templates": {
        "required": False,
        "types": ["report"]
    },
    "tools": ["Read", "Glob", "Grep", "Bash"],
    "model": "sonnet"  # Good for analysis
}
```

## Validator Architecture

### Focus: Validation Scripts

Validators check compliance with rules. They need clear rules and checks.

```
validator-skill/
├── SKILL.md                 # Validation overview
├── references/
│   ├── rules.md             # Validation rules (REQUIRED)
│   ├── error-codes.md       # Error code reference
│   └── remediation.md       # How to fix issues
├── scripts/
│   ├── validate.sh          # Main validation script (REQUIRED)
│   ├── check-syntax.sh      # Syntax validation
│   ├── check-style.sh       # Style validation
│   └── generate-report.sh   # Validation report
└── rules/
    ├── required.yaml        # Required rules
    └── optional.yaml        # Optional rules
```

### Architecture Pattern

```python
VALIDATOR_ARCHITECTURE = {
    "skill_md": {
        "sections": [
            "overview",           # What it validates
            "rules",              # Rule summary
            "workflow",           # Validation process
            "output",             # Result format
            "integration",        # CI/CD integration
            "examples"            # Validation examples
        ],
        "emphasis": ["rules", "output", "integration"]
    },
    "references": {
        "required": ["rules.md"],
        "recommended": ["error-codes.md", "remediation.md"],
        "focus": "rule documentation"
    },
    "scripts": {
        "required": ["validate.sh"],
        "recommended": ["check-syntax.sh", "check-style.sh"],
        "focus": "validation logic"
    },
    "templates": {
        "required": False,
        "types": ["report"]
    },
    "tools": ["Read", "Glob", "Grep", "Bash"],
    "model": "haiku"  # Fast for validation
}
```

## Pattern Selection

```python
ARCHITECTURE_PATTERNS = {
    "builder": BUILDER_ARCHITECTURE,
    "guide": GUIDE_ARCHITECTURE,
    "automation": AUTOMATION_ARCHITECTURE,
    "analyzer": ANALYZER_ARCHITECTURE,
    "validator": VALIDATOR_ARCHITECTURE
}

def get_architecture_pattern(skill_type: str) -> dict:
    """Get architecture pattern for skill type."""
    if skill_type not in ARCHITECTURE_PATTERNS:
        raise ValueError(f"Unknown skill type: {skill_type}")
    return ARCHITECTURE_PATTERNS[skill_type]

def plan_components(
    skill_type: str,
    requirements: list[Requirement]
) -> list[Component]:
    """Plan components based on skill type and requirements."""
    pattern = get_architecture_pattern(skill_type)
    components = []

    # Always include SKILL.md
    components.append(Component(
        id="skill_md",
        path="SKILL.md",
        type="skill_md",
        description="Main skill documentation"
    ))

    # Add required references
    for ref in pattern["references"]["required"]:
        components.append(Component(
            id=ref.replace(".md", "_md").replace("-", "_"),
            path=f"references/{ref}",
            type="reference",
            description=f"Required reference: {ref}"
        ))

    # Add required scripts
    for script in pattern["scripts"]["required"]:
        components.append(Component(
            id=script.replace(".sh", "_sh").replace("-", "_"),
            path=f"scripts/{script}",
            type="script",
            description=f"Required script: {script}"
        ))

    # Add recommended based on requirements
    components.extend(
        plan_optional_components(pattern, requirements)
    )

    return components
```

## Token Budget Allocation

```python
def allocate_token_budget(skill_type: str, total_budget: int = 10000) -> dict:
    """Allocate token budget based on skill type focus."""

    allocations = {
        "builder": {
            "skill_md": 0.40,      # 4000 tokens
            "references": 0.25,    # 2500 tokens
            "scripts": 0.25,       # 2500 tokens
            "templates": 0.10      # 1000 tokens
        },
        "guide": {
            "skill_md": 0.35,      # 3500 tokens
            "references": 0.55,    # 5500 tokens (focus)
            "scripts": 0.05,       # 500 tokens
            "templates": 0.05      # 500 tokens
        },
        "automation": {
            "skill_md": 0.35,      # 3500 tokens
            "references": 0.25,    # 2500 tokens
            "scripts": 0.35,       # 3500 tokens (focus)
            "templates": 0.05      # 500 tokens
        },
        "analyzer": {
            "skill_md": 0.35,      # 3500 tokens
            "references": 0.30,    # 3000 tokens
            "scripts": 0.30,       # 3000 tokens (focus)
            "templates": 0.05      # 500 tokens
        },
        "validator": {
            "skill_md": 0.30,      # 3000 tokens
            "references": 0.30,    # 3000 tokens
            "scripts": 0.35,       # 3500 tokens (focus)
            "templates": 0.05      # 500 tokens
        }
    }

    alloc = allocations.get(skill_type, allocations["guide"])
    return {k: int(v * total_budget) for k, v in alloc.items()}
```
