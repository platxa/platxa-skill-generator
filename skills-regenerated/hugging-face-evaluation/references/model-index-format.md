# Model-Index Format Specification

The model-index is a YAML metadata block in Hugging Face model cards that structures evaluation results for machine consumption. It follows the Papers with Code specification and enables automatic leaderboard integration.

## Structure

```yaml
model-index:
  - name: "Plain Text Model Name"
    results:
      - task:
          type: text-generation          # Papers with Code task type
          name: "Text Generation"        # Human-readable name (optional)
        dataset:
          name: "MMLU"                   # Benchmark display name
          type: cais/mmlu                # HF dataset ID or Papers with Code ID
          config: default                # Dataset config (optional)
          split: test                    # Dataset split (optional)
          revision: main                 # Dataset revision (optional)
        metrics:
          - name: accuracy               # Metric display name
            type: accuracy               # Metric identifier
            value: 85.2                  # Numeric score
            verified: false              # Hub verification status
        source:
          name: "Open LLM Leaderboard"   # Attribution (optional)
          url: "https://..."             # Source URL (optional)
```

## Field Rules

### Name Field
- MUST be plain text (no markdown bold, links, or formatting)
- Should match the model's display name on the Hub
- One name per model-index entry

### Task Types
Common `task.type` values from Papers with Code:
- `text-generation` -- Language modeling, chat, completion
- `question-answering` -- QA benchmarks (SQuAD, TriviaQA)
- `text-classification` -- Sentiment, NLI, topic classification
- `summarization` -- Text summarization
- `translation` -- Machine translation
- `image-classification` -- Vision models
- `object-detection` -- Detection models

### Dataset Identifiers
- Prefer HF dataset IDs when available: `cais/mmlu`, `gsm8k`, `openai/openai_humaneval`
- For custom benchmarks, use a descriptive type: `custom-benchmark`
- The `name` field is the human-readable display name

### Metric Values
- Must be numeric (float or int)
- Percentage scores: use the actual percentage (85.2), not decimal (0.852)
- Multiple metrics per dataset entry are supported

## Merge Behavior

When adding new results to an existing model-index:
1. Preserve all existing entries
2. Append new results to the `results` list
3. Do not duplicate entries for the same dataset/metric combination
4. The `evaluation_manager.py` script handles merging automatically

## Validation

A valid model-index entry requires:
- At least one result with `task.type`, `dataset.name`, and one metric with `name`, `type`, `value`
- No markdown syntax in text fields
- Numeric metric values (strings like "85.2%" are invalid)
