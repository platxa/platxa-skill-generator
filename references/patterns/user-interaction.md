# User Interaction Patterns

Patterns for gathering information from users via AskUserQuestion tool.

## Purpose

Guide users through skill description entry and decision points using structured questions that ensure all necessary information is collected.

## Initial Skill Description

### Question Flow

```
1. What skill do you want to create?
   → Free text description

2. What type of skill is this?
   → Builder / Guide / Automation / Analyzer / Validator

3. What domain does this skill operate in?
   → (Inferred or asked if unclear)

4. Who is the target user?
   → Developers / DevOps / Data Scientists / General users
```

### Implementation

```python
def gather_skill_description() -> dict:
    """
    Gather skill description through guided questions.

    Uses AskUserQuestion tool to collect:
    - Skill purpose
    - Skill type
    - Target domain
    - Target users
    """

    # Question 1: Purpose
    purpose_question = {
        "questions": [{
            "question": "What skill would you like to create? Describe what it should do.",
            "header": "Purpose",
            "options": [
                {
                    "label": "Generate code/files",
                    "description": "Create new files from templates or specifications"
                },
                {
                    "label": "Guide a process",
                    "description": "Walk through steps with best practices"
                },
                {
                    "label": "Automate a task",
                    "description": "Execute commands automatically"
                },
                {
                    "label": "Analyze code/data",
                    "description": "Review and provide insights"
                }
            ],
            "multiSelect": False
        }]
    }

    # Question 2: Skill Type
    type_question = {
        "questions": [{
            "question": "What type of skill best matches your needs?",
            "header": "Skill Type",
            "options": [
                {
                    "label": "Builder",
                    "description": "Generates code, files, or projects from inputs"
                },
                {
                    "label": "Guide",
                    "description": "Provides expertise and step-by-step guidance"
                },
                {
                    "label": "Automation",
                    "description": "Executes tasks automatically via scripts"
                },
                {
                    "label": "Analyzer",
                    "description": "Reviews code/data and provides insights"
                },
                {
                    "label": "Validator",
                    "description": "Checks compliance with rules/standards"
                }
            ],
            "multiSelect": False
        }]
    }

    # Question 3: Domain (if not clear from purpose)
    domain_question = {
        "questions": [{
            "question": "What domain or technology does this skill focus on?",
            "header": "Domain",
            "options": [
                {
                    "label": "API/OpenAPI",
                    "description": "REST APIs, OpenAPI specs, Swagger"
                },
                {
                    "label": "Frontend",
                    "description": "React, Vue, web components"
                },
                {
                    "label": "Backend",
                    "description": "Python, Node.js, databases"
                },
                {
                    "label": "DevOps",
                    "description": "Docker, CI/CD, infrastructure"
                }
            ],
            "multiSelect": False
        }]
    }

    return {
        "purpose": purpose_question,
        "type": type_question,
        "domain": domain_question
    }
```

## Clarification Questions

### When Discovery Needs More Info

```python
def ask_clarification(unclear_aspects: list[str]) -> dict:
    """
    Generate clarification questions for unclear aspects.

    Args:
        unclear_aspects: List of aspects needing clarification

    Returns:
        AskUserQuestion payload
    """
    questions = []

    for aspect in unclear_aspects[:4]:  # Max 4 questions
        if aspect == 'input_format':
            questions.append({
                "question": "What format is the input for this skill?",
                "header": "Input",
                "options": [
                    {"label": "File path", "description": "Path to a file on disk"},
                    {"label": "Text content", "description": "Direct text/code input"},
                    {"label": "URL", "description": "Web URL to fetch"},
                    {"label": "Directory", "description": "Path to a directory"}
                ],
                "multiSelect": True
            })

        elif aspect == 'output_format':
            questions.append({
                "question": "What output should this skill produce?",
                "header": "Output",
                "options": [
                    {"label": "Files", "description": "Create/modify files"},
                    {"label": "Report", "description": "Text/markdown report"},
                    {"label": "Console", "description": "Print to terminal"},
                    {"label": "JSON", "description": "Structured data output"}
                ],
                "multiSelect": True
            })

        elif aspect == 'scope':
            questions.append({
                "question": "What is the scope of this skill?",
                "header": "Scope",
                "options": [
                    {"label": "Single file", "description": "Operates on one file"},
                    {"label": "Directory", "description": "Operates on a folder"},
                    {"label": "Project", "description": "Whole project/repo"},
                    {"label": "External", "description": "Interacts with external services"}
                ],
                "multiSelect": False
            })

        elif aspect == 'complexity':
            questions.append({
                "question": "How complex should this skill be?",
                "header": "Complexity",
                "options": [
                    {"label": "Simple", "description": "Single task, quick execution"},
                    {"label": "Moderate", "description": "Multiple steps, some decisions"},
                    {"label": "Complex", "description": "Many steps, branching logic"}
                ],
                "multiSelect": False
            })

    return {"questions": questions}
```

## Architecture Decisions

### When Multiple Approaches Exist

```python
def ask_architecture_decision(
    decision_point: str,
    options: list[dict]
) -> dict:
    """
    Ask user to choose between architecture options.

    Args:
        decision_point: What decision needs to be made
        options: List of {label, description, tradeoffs}

    Returns:
        AskUserQuestion payload
    """
    formatted_options = []

    for opt in options[:4]:  # Max 4 options
        formatted_options.append({
            "label": opt['label'],
            "description": f"{opt['description']}. Trade-offs: {opt.get('tradeoffs', 'None')}"
        })

    return {
        "questions": [{
            "question": decision_point,
            "header": "Architecture",
            "options": formatted_options,
            "multiSelect": False
        }]
    }


# Example usage
def ask_reference_structure():
    return ask_architecture_decision(
        "How should reference documentation be organized?",
        [
            {
                "label": "Single file",
                "description": "All references in one file",
                "tradeoffs": "Simple but may be large"
            },
            {
                "label": "By topic",
                "description": "Separate files by topic area",
                "tradeoffs": "Organized but more files"
            },
            {
                "label": "By usage",
                "description": "Separate files by when they're needed",
                "tradeoffs": "Context-aware but complex"
            }
        ]
    )
```

## Validation Confirmations

### Before Final Installation

```python
def confirm_installation(skill_summary: dict) -> dict:
    """
    Ask user to confirm skill installation.

    Args:
        skill_summary: Summary of generated skill

    Returns:
        AskUserQuestion payload
    """
    skill_name = skill_summary.get('name', 'unknown')
    quality_score = skill_summary.get('quality_score', 0)

    return {
        "questions": [{
            "question": f"Install '{skill_name}' skill? (Quality: {quality_score}/10)",
            "header": "Install",
            "options": [
                {
                    "label": "Yes, install now",
                    "description": "Install to ~/.claude/commands/"
                },
                {
                    "label": "Review first",
                    "description": "Show generated files before installing"
                },
                {
                    "label": "Save only",
                    "description": "Save to output directory without installing"
                },
                {
                    "label": "Cancel",
                    "description": "Discard generated skill"
                }
            ],
            "multiSelect": False
        }]
    }
```

## Quality Warning Confirmation

```python
def confirm_with_warnings(warnings: list[str]) -> dict:
    """
    Ask user to confirm despite quality warnings.

    Args:
        warnings: List of quality warnings

    Returns:
        AskUserQuestion payload
    """
    warning_summary = "; ".join(warnings[:3])

    return {
        "questions": [{
            "question": f"Quality warnings found: {warning_summary}. Proceed anyway?",
            "header": "Warnings",
            "options": [
                {
                    "label": "Proceed anyway",
                    "description": "Install despite warnings (Recommended)"
                },
                {
                    "label": "Try to improve",
                    "description": "Attempt automatic improvements"
                },
                {
                    "label": "Cancel",
                    "description": "Stop and review issues"
                }
            ],
            "multiSelect": False
        }]
    }
```

## Response Handling

```python
def handle_user_response(response: dict, question_type: str) -> dict:
    """
    Process user's response to questions.

    Args:
        response: User's answers
        question_type: Which question flow this is from

    Returns:
        Processed data for next phase
    """
    answers = response.get('answers', {})

    if question_type == 'skill_description':
        return {
            'purpose': answers.get('q0', ''),
            'skill_type': answers.get('q1', 'guide'),
            'domain': answers.get('q2', ''),
            'user_provided': True
        }

    elif question_type == 'clarification':
        return {
            'clarifications': answers,
            'resolved': True
        }

    elif question_type == 'installation':
        action = answers.get('q0', 'Cancel')
        return {
            'install': action == 'Yes, install now',
            'review': action == 'Review first',
            'save_only': action == 'Save only',
            'cancel': action == 'Cancel'
        }

    return answers
```

## Best Practices

1. **Limit questions**: Max 4 questions per interaction
2. **Clear options**: 2-4 options per question
3. **Descriptions**: Always provide helpful descriptions
4. **Default first**: Put recommended option first
5. **Multi-select sparingly**: Only when choices aren't exclusive
6. **Short headers**: Max 12 characters for chip display
