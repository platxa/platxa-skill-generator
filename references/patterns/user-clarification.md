# User Clarification Requests (Phase 3)

Generate targeted questions only when automatic research has gaps.

## Core Principles

1. **Research First**: Never ask what can be searched
2. **Targeted Questions**: Ask only about identified gaps
3. **Minimal Questions**: Max 2 questions per round
4. **Actionable Answers**: Questions should have clear answer types

## When to Ask

### Ask When

- Sufficiency score < 0.6
- Critical gap identified (workflow/authority < 0.4)
- Research exhausted but gaps remain

### Don't Ask When

- Question can be answered by WebSearch
- Information exists in official docs
- Answer is a common convention
- Preference doesn't affect skill quality

## Question Generation

### Gap-to-Question Mapping

| Gap Type | Question Template |
|----------|-------------------|
| No official docs | "Do you have a URL for official {domain} documentation?" |
| Unclear workflow | "What are the typical steps when {doing_task}?" |
| Missing concepts | "What key terms should I know for {domain}?" |
| Unknown tools | "What tools/libraries do you use for {domain}?" |
| No examples | "Can you point to an existing project that does {task}?" |
| Ambiguous scope | "Should this skill handle {option_A} or {option_B}?" |

### Question Quality Checklist

Good questions are:
- [ ] Specific (not "tell me more about X")
- [ ] Actionable (user can answer concretely)
- [ ] Gap-filling (addresses identified gap)
- [ ] Non-obvious (couldn't find via research)

### Good vs Bad Questions

| ❌ Bad Question | ✅ Good Question |
|-----------------|------------------|
| "What should the skill do?" | (Already provided) |
| "What are best practices?" | (Should research) |
| "How does X work?" | (Should look up) |
| "Tell me about your project" | "Does your project use TypeScript or JavaScript?" |
| "What features do you want?" | "Should this handle {specific_case}?" |

## AskUserQuestion Integration

### Using the Tool

```markdown
AskUserQuestion(
  questions: [
    {
      question: "Which OpenAPI version does your project use?",
      header: "OpenAPI",
      options: [
        {label: "3.1 (Latest)", description: "OpenAPI 3.1.0 specification"},
        {label: "3.0", description: "OpenAPI 3.0.x specification"},
        {label: "2.0 (Swagger)", description: "Legacy Swagger 2.0"}
      ],
      multiSelect: false
    }
  ]
)
```

### Question Formats

#### Single Choice
```json
{
  "question": "Which framework should this skill target?",
  "header": "Framework",
  "options": [
    {"label": "React", "description": "React 18+"},
    {"label": "Vue", "description": "Vue 3+"},
    {"label": "Angular", "description": "Angular 15+"}
  ],
  "multiSelect": false
}
```

#### Multiple Choice
```json
{
  "question": "Which output formats should be supported?",
  "header": "Formats",
  "options": [
    {"label": "Markdown", "description": "For documentation sites"},
    {"label": "HTML", "description": "Standalone pages"},
    {"label": "PDF", "description": "Printable documents"}
  ],
  "multiSelect": true
}
```

#### Open-Ended (via "Other")
```markdown
Always include options - user can select "Other" for custom input.
Never use pure free-text questions.
```

## Question Prioritization

### Priority Order

1. **Blocking gaps** (must resolve to proceed)
   - Workflow completely unknown
   - Critical ambiguity in requirements

2. **High-impact gaps** (significantly affects quality)
   - Target framework/version
   - Key technology choices

3. **Nice-to-have** (improves but not required)
   - Preference between valid approaches
   - Edge case handling

### Limit Questions

```markdown
Per clarification round:
  - Max 2 questions
  - Prioritize by impact
  - Defer low-priority to later

Total clarification rounds:
  - Max 2 rounds
  - If still insufficient, warn and offer to proceed
```

## Processing Answers

### Incorporating Responses

```markdown
1. Receive user answer
2. Update discovery findings:
   - Add to concepts if terminology
   - Add to workflow if process info
   - Add to tools if technology choice
3. Recalculate sufficiency score
4. Proceed or ask follow-up
```

### Answer Validation

```markdown
IF answer == "Other" with custom text:
    Parse custom input
    Categorize appropriately

IF answer is unclear:
    Ask one follow-up clarification
    Don't loop indefinitely
```

## State Management

### Before Clarification

```json
{
  "discovery": {
    "status": "needs_clarification",
    "sufficiency_score": 0.55,
    "gaps": [
      {"dimension": "workflow", "severity": "high"}
    ]
  }
}
```

### Questions Sent

```json
{
  "discovery": {
    "status": "awaiting_clarification",
    "clarification_round": 1,
    "questions_asked": [
      {"question": "Which framework...", "timestamp": "..."}
    ]
  }
}
```

### After Answer

```json
{
  "discovery": {
    "status": "complete",
    "sufficiency_score": 0.82,
    "clarifications": [
      {"question": "Which framework...", "answer": "React"}
    ]
  }
}
```

## Example Flow

```markdown
1. Research complete, score = 0.55
   Gap: "Framework target unknown"

2. Generate question:
   "Which framework should this skill target?"
   Options: React, Vue, Angular

3. User selects: "React"

4. Update findings:
   tools.framework = "React"
   practices.append("Use React hooks pattern")

5. Recalculate score = 0.78

6. Score >= 0.6, proceed with warnings
```
