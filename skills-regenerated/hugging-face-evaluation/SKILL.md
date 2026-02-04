---
name: hugging-face-evaluation
description: Analyze and manage evaluation results in Hugging Face model cards. Extract benchmark tables from README content, import scores from Artificial Analysis API, run model evaluations with lighteval or inspect-ai on vLLM/GPU backends, and generate model-index YAML metadata compliant with the Papers with Code specification.
allowed-tools:
  - Bash
  - Read
  - Write
  - WebFetch
  - Task
metadata:
  version: "1.0.0"
  author: platxa
  tags:
    - ml
    - evaluation
    - hugging-face
    - model-cards
    - benchmarks
    - analyzer
  provenance:
    upstream_source: hugging-face-evaluation
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T15:55:18Z"
    generator_version: "1.0.0"
    intent_confidence: 0.61
---

# Hugging Face Evaluation Manager

Analyze, extract, and manage evaluation results in Hugging Face model cards.

## Overview

This skill manages evaluation metadata in HF model cards through four methods:

**What it analyzes:**
- README markdown tables containing benchmark scores
- Existing model-index YAML metadata in model cards
- Artificial Analysis API benchmark data
- Custom evaluation outputs from lighteval and inspect-ai

**What it reports:**
- Model-index YAML entries compliant with Papers with Code specification
- Extracted benchmark scores with source attribution
- Evaluation job results from HF Jobs infrastructure
- PR status checks to prevent duplicate contributions

Invoke this skill when users want to:
- Extract evaluation tables from a model's README into model-index metadata
- Import benchmark scores from Artificial Analysis for a model card
- Run evaluations on HF Jobs with lighteval (vLLM) or inspect-ai
- Validate or view existing model-index entries
- Create PRs to add evaluation metadata to models they do not own

## Analysis Checklist

### Before Any Operation

- [ ] HF_TOKEN set with write permissions (verify with `hf_whoami()`)
- [ ] For Artificial Analysis: AA_API_KEY set in environment or .env

### Before Creating a PR

- [ ] Run `get-prs` to check for existing open PRs on the target repo
- [ ] If PRs exist: warn the user, show URLs, do NOT proceed unless confirmed
- [ ] Preview YAML output before applying (default behavior prints YAML)
- [ ] Compare extracted values against the README table manually

### Before Running Evaluations

- [ ] Select hardware matching model size (see Hardware Selection)
- [ ] Verify GPU availability with `nvidia-smi` for local runs
- [ ] Confirm `uv` is installed for PEP 723 script execution

## Workflow

### Method 1: Extract Evaluation Tables from README

The primary workflow for adding model-index metadata from existing README tables.

```bash
# Step 1: Check for existing PRs (ALWAYS first)
uv run scripts/evaluation_manager.py get-prs --repo-id "owner/model"

# Step 2: Inspect tables to find structure and column indices
uv run scripts/evaluation_manager.py inspect-tables --repo-id "owner/model"

# Step 3: Extract from a specific table (prints YAML by default)
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "owner/model" \
  --table 1 \
  [--model-column-index N] \
  [--model-name-override "Exact Header Text"] \
  [--task-type "text-generation"]

# Step 4: Apply changes
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "owner/model" --table 1 --apply       # push directly
# OR
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "owner/model" --table 1 --create-pr   # open a PR
```

**Key rules:**
- Always start with `inspect-tables` to see table numbers and column hints
- Use `--table N` when multiple evaluation tables exist
- Prefer `--model-column-index` over `--model-name-override`
- For comparison tables with multiple models, use `--model-name-override` with the exact column header text from `inspect-tables` output
- One model per repo: only add the main model's results

### Method 2: Import from Artificial Analysis

Fetch benchmark scores from the Artificial Analysis API.

```bash
# Check for existing PRs first
uv run scripts/evaluation_manager.py get-prs --repo-id "owner/model"

# Import and create PR
AA_API_KEY=... uv run scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "owner/model" \
  --create-pr
```

### Method 3: Run Evaluations on HF Jobs (Inference Providers)

Submit evaluation jobs using inspect-ai against HF inference provider endpoints.

```bash
# Direct CLI
hf jobs uv run scripts/inspect_eval_uv.py \
  --flavor cpu-basic \
  --secret HF_TOKEN=$HF_TOKEN \
  -- --model "meta-llama/Llama-2-7b-hf" --task "mmlu"

# Python helper
uv run scripts/run_eval_job.py \
  --model "meta-llama/Llama-2-7b-hf" --task "mmlu" --hardware "cpu-basic"
```

### Method 4: Run Custom Evaluations with vLLM

Evaluate models directly on GPU using vLLM backend. Use when the model has no inference provider endpoint.

**lighteval (Open LLM Leaderboard tasks):**
```bash
# Local GPU
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B --tasks "leaderboard|mmlu|5"

# Via HF Jobs
hf jobs uv run scripts/lighteval_vllm_uv.py \
  --flavor a10g-small --secrets HF_TOKEN=$HF_TOKEN \
  -- --model meta-llama/Llama-3.2-1B --tasks "leaderboard|mmlu|5"
```

**inspect-ai with vLLM:**
```bash
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B --task mmlu

# Multi-GPU
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-70B --task mmlu --tensor-parallel-size 4
```

**Job submission helper (auto hardware selection):**
```bash
uv run scripts/run_vllm_eval_job.py \
  --model meta-llama/Llama-3.2-1B \
  --task "leaderboard|mmlu|5" --framework lighteval
```

## Metrics

### Hardware Selection

| Model Size | Hardware | Approx Cost/hr |
|-----------|----------|----------------|
| < 3B params | `t4-small` | ~$0.75 |
| 3-13B | `a10g-small` | ~$2.50 |
| 13-34B | `a10g-large` | ~$5.00 |
| 34B+ | `a100-large` | ~$10-20 |

### lighteval Task Format

Tasks use `suite|task|num_fewshot`:
- `leaderboard|mmlu|5` -- MMLU 5-shot
- `leaderboard|gsm8k|5` -- GSM8K 5-shot
- `leaderboard|arc_challenge|25` -- ARC-Challenge 25-shot
- `lighteval|hellaswag|0` -- HellaSwag zero-shot

Full task list: https://github.com/huggingface/lighteval/blob/main/examples/tasks/all_tasks.txt

### inspect-ai Tasks

`mmlu`, `gsm8k`, `hellaswag`, `arc_challenge`, `truthfulqa`, `winogrande`, `humaneval`

## Report Format

### Model-Index YAML Output

```yaml
model-index:
  - name: Model Name
    results:
      - task:
          type: text-generation
        dataset:
          name: Benchmark Dataset
          type: benchmark_type
        metrics:
          - name: MMLU
            type: mmlu
            value: 85.2
        source:
          name: Source Name
          url: https://source-url.com
```

**Rules:** Plain text model names only (no markdown). URLs only in `source.url`.

### Commands Reference

| Command | Purpose |
|---------|---------|
| `get-prs` | Check open PRs before creating new ones |
| `inspect-tables` | Show all tables with structure and columns |
| `extract-readme` | Extract table to model-index YAML |
| `import-aa` | Import from Artificial Analysis API |
| `show` | View existing model-index entries |
| `validate` | Validate model-index compliance |

## Examples

### Update Your Own Model

```bash
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/your-model" --task-type "text-generation"
```

### Update Someone Else's Model

```bash
# 1. Check for existing PRs
uv run scripts/evaluation_manager.py get-prs --repo-id "other-user/model"

# 2. If no open PRs, create one
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "other-user/model" --table 1 --create-pr
```

### Run lighteval Locally Then Apply

```bash
# Evaluate
uv run scripts/lighteval_vllm_uv.py \
  --model your-user/your-model \
  --tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5"

# Extract results and apply to model card
uv run scripts/evaluation_manager.py extract-readme \
  --repo-id "your-user/your-model" --apply
```

## Interpretation Guide

### Model Name Matching

The extraction uses exact normalized token matching:
- Strips markdown formatting (bold, links)
- Normalizes to lowercase, replaces `-`/`_` with spaces
- Compares token sets: `"OLMo-3-32B"` matches `"**Olmo 3 32B**"`
- Fails if no exact match (never guesses)

### Troubleshooting

| Issue | Fix |
|-------|-----|
| No evaluation tables found | Verify README contains markdown tables with numeric scores |
| Model not found in table | Use `--model-name-override` with exact text from `inspect-tables` |
| AA_API_KEY not set | Set in environment or .env file |
| Token lacks write access | Ensure HF_TOKEN has write permissions |
| vLLM OOM | Upgrade hardware, reduce `--gpu-memory-utilization`, use `--tensor-parallel-size` |
| Architecture not supported by vLLM | Use `--backend hf` (inspect-ai) or `--backend accelerate` (lighteval) |
| Chat template not found | Only use `--use-chat-template` for instruction-tuned models |
| Payment required | Add payment method to HF account for non-CPU hardware |

## Output Checklist

After any evaluation update, verify:

- [ ] YAML output matches README table values exactly
- [ ] Model name is plain text (no markdown formatting)
- [ ] `task.type` field is set correctly (e.g., `text-generation`)
- [ ] Source attribution includes name and URL
- [ ] No duplicate PRs created (checked with `get-prs`)
- [ ] Existing model-index entries preserved (merge, not overwrite)

## Resources

### References
- `references/model-index-format.md` -- Papers with Code model-index specification
- `references/evaluation-frameworks.md` -- lighteval vs inspect-ai comparison
- `references/hardware-guide.md` -- GPU selection and cost estimation

### Scripts
- `scripts/evaluation_manager.py` -- Core CLI for table extraction, AA import, PR management
- `scripts/inspect_eval_uv.py` -- inspect-ai runner for HF Jobs (inference providers)
- `scripts/run_eval_job.py` -- Job submission helper for inference provider evals

### External
- [Hugging Face Model Cards](https://huggingface.co/docs/hub/model-cards)
- [Papers with Code Model Index](https://github.com/paperswithcode/model-index)
- [lighteval Documentation](https://github.com/huggingface/lighteval)
- [inspect-ai Documentation](https://inspect.ai-safety-institute.org.uk/)
