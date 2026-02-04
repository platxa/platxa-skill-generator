# Dataset Templates Guide

The `dataset_manager.py` script validates uploaded rows against predefined templates. Each template defines required fields, recommended fields, field types, and format-specific validation rules.

## Available Templates

### chat

Multi-turn conversational data for training chat models.

```json
{
  "messages": [
    {"role": "user", "content": "How do I sort a list in Python?"},
    {"role": "assistant", "content": "Use sorted() for a new list or .sort() for in-place."},
    {"role": "tool", "content": "...", "tool_call_id": "call_123"}
  ],
  "scenario": "programming-help",
  "complexity": "simple"
}
```

Required: `messages` (array of objects with `role` and `content`).
Valid roles: `user`, `assistant`, `tool`, `system`.

### classification

Labeled text for sentiment, intent, or topic classification.

```json
{
  "text": "This product exceeded my expectations",
  "label": "positive",
  "confidence": 0.95,
  "metadata": {"domain": "reviews", "language": "en"}
}
```

Required: `text`, `label`.

### qa

Question-answer pairs for reading comprehension and factual QA.

```json
{
  "question": "What database does sql_manager.py use?",
  "answer": "DuckDB, an in-process SQL OLAP database engine.",
  "context": "The sql_manager module uses DuckDB's hf:// protocol...",
  "answer_type": "factual",
  "difficulty": "easy"
}
```

Required: `question`, `answer`.

### completion

Prompt-completion pairs for language modeling and code generation.

```json
{
  "prompt": "def fibonacci(n):",
  "completion": "\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "domain": "code",
  "style": "recursive"
}
```

Required: `prompt`, `completion`.

### tabular

Structured data with explicit column definitions.

```json
{
  "columns": [
    {"name": "age", "type": "numeric", "description": "Patient age"},
    {"name": "diagnosis", "type": "categorical", "description": "Primary diagnosis"}
  ],
  "data": [
    {"age": 45, "diagnosis": "type2_diabetes"},
    {"age": 32, "diagnosis": "hypertension"}
  ]
}
```

Required: `columns`, `data`.

### custom

Flexible schema for specialized datasets. No required fields beyond valid JSON objects.

## Validation Behavior

- **Required fields** -- Upload fails if any row is missing a required field
- **Recommended fields** -- Warning printed but upload proceeds
- **Type checking** -- Fields are validated against expected types (string, number, array, object, enum)
- **Format-specific** -- Chat messages validated for role/content structure; tabular validated for columns/data arrays

## Listing Templates

```bash
uv run scripts/dataset_manager.py list_templates
```

Prints all available templates with descriptions and required fields.
