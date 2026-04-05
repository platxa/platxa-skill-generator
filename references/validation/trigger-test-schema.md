# Trigger Test Schema

Schema for `trigger-tests.json` used by `scripts/test-triggers.sh` to validate skill trigger accuracy.

## File Location

Place `trigger-tests.json` in either:
- `<skill-dir>/trigger-tests.json` (preferred)
- `<skill-dir>/evals/trigger-tests.json`

## Schema

```json
{
  "skill_name": "string (required) — matches SKILL.md name field",
  "should_trigger": [
    "string — prompts that SHOULD activate this skill"
  ],
  "should_not_trigger": [
    "string — prompts that should NOT activate this skill"
  ]
}
```

## Requirements

- `should_trigger`: minimum 5 prompts recommended
- `should_not_trigger`: minimum 3 prompts recommended
- At least one of the arrays must be non-empty

## Prompt Categories

### should_trigger

Include three types of prompts:

1. **Obvious triggers** — directly state the skill's purpose
   ```
   "Generate a commit message for my staged changes"
   ```

2. **Paraphrased triggers** — same intent, different wording
   ```
   "What should I name this commit?"
   "I need a good message for this git commit"
   ```

3. **Contextual triggers** — user's situation implies the skill
   ```
   "I just finished implementing the auth feature and I'm ready to commit"
   ```

### should_not_trigger

Include prompts that are:

1. **Completely unrelated** — different domain entirely
   ```
   "What's the weather in San Francisco?"
   ```

2. **Adjacent but distinct** — related domain, wrong skill
   ```
   "Review my pull request"
   "Show me the git log"
   ```

3. **Ambiguous** — could be confused but shouldn't trigger
   ```
   "Help me write a message to my team"
   ```

## Example: commit-message skill

```json
{
  "skill_name": "commit-message",
  "should_trigger": [
    "Generate a commit message for my staged changes",
    "Help me write a conventional commit message",
    "What should I name this commit?",
    "Create a commit message for the git diff",
    "I need a good commit message"
  ],
  "should_not_trigger": [
    "What's the weather in San Francisco?",
    "Help me write Python code",
    "Create a spreadsheet",
    "Review my pull request"
  ]
}
```

## Example: code-review skill

```json
{
  "skill_name": "code-review",
  "should_trigger": [
    "Review my code changes",
    "Check this code for bugs and security issues",
    "Can you audit this function?",
    "Look at my diff and tell me if anything is wrong",
    "Do a code review on the authentication module"
  ],
  "should_not_trigger": [
    "Write unit tests for the auth module",
    "Generate documentation for this function",
    "Help me commit these changes",
    "Deploy the application to production"
  ]
}
```

## Targets

| Metric | Target | Meaning |
|--------|--------|---------|
| Trigger rate | >= 90% | Skill activates for relevant prompts |
| False positive rate | <= 0% | Skill does NOT activate for irrelevant prompts |

## Usage

```bash
# Run trigger tests
./scripts/test-triggers.sh <skill-dir>

# JSON output for automation
./scripts/test-triggers.sh <skill-dir> --json

# Custom targets
./scripts/test-triggers.sh <skill-dir> --trigger-rate 80 --fp-rate 5

# Preview without running
./scripts/test-triggers.sh <skill-dir> --dry-run
```

## Improving Trigger Accuracy

If trigger rate is low:
- Add more trigger phrases to SKILL.md description (first 250 chars)
- Include specific tasks users would say: `Use when user says "X", "Y", or "Z"`

If false positive rate is high:
- Add negative triggers to description: `Do NOT use for general code questions`
- Be more specific about scope: `Use specifically for online payment workflows, not general financial queries`
