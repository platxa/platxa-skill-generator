---
name: hugging-face-model-trainer
description: Guide for training and fine-tuning language models using TRL on Hugging Face Jobs infrastructure. Covers SFT, DPO, GRPO training methods via hf_jobs() MCP tool with UV scripts (PEP 723), dataset validation, hardware selection, cost estimation, Trackio monitoring, Hub persistence, and GGUF conversion for local deployment.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - WebFetch
  - AskUserQuestion
metadata:
  version: "1.0.0"
  author: platxa
  tags:
    - ml
    - training
    - hugging-face
    - trl
    - fine-tuning
    - guide
  provenance:
    upstream_source: hugging-face-model-trainer
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T12:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.91
---

# TRL Training on Hugging Face Jobs

## Overview

Train language models using TRL on managed Hugging Face infrastructure. No local GPU required -- models train on cloud GPUs with results saved to the Hub.

Invoke this skill when users want to:
- Fine-tune language models on cloud GPUs (SFT, DPO, GRPO)
- Run training jobs on Hugging Face Jobs infrastructure
- Convert trained models to GGUF for local deployment (Ollama, LM Studio)
- Validate dataset format before training
- Estimate training cost and select hardware

## Workflow

### 1. Verify Prerequisites

Before any training job, verify:

- **Account**: HF Pro, Team, or Enterprise plan (Jobs requires paid plan)
- **Auth**: Check with `hf_whoami()`. Token needs write permissions.
- **HF_TOKEN**: MUST pass `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config
- **Dataset**: Must exist on Hub. Validate unknown datasets first (see Dataset Validation).
- **Timeout**: Default 30min is too short. Minimum 1-2 hours recommended.
- **Hub push**: `push_to_hub=True` + `hub_model_id="username/model"` -- environment is ephemeral, all results lost without push.

### 2. Choose Training Method

| Method | Purpose | Dataset Format |
|--------|---------|---------------|
| **SFT** | Instruction tuning on demonstration data | `messages`, `text`, or `prompt`/`completion` |
| **DPO** | Alignment from preference pairs | `prompt`, `chosen`, `rejected` |
| **GRPO** | Online RL with verifiable rewards | Prompt-only (responses generated online) |
| **Reward** | Train reward models for RLHF | Preference pairs |

**Recommended pipeline**: SFT first, then DPO for alignment, optionally GGUF for local use.

See `references/training_methods.md` for method details and selection guidance.

### 3. Select Hardware

| Model Size | Hardware | Cost/hr | Notes |
|-----------|----------|---------|-------|
| <1B | `t4-small` | ~$0.75 | Demos only, skip eval for memory |
| 1-3B | `t4-medium`, `l4x1` | ~$1.50-2.50 | Development |
| 3-7B | `a10g-small/large` | ~$3.50-5.00 | Production |
| 7-13B | `a10g-large`, `a100-large` | ~$5-10 | Use LoRA |
| 13B+ | `a100-large` | ~$10-20 | LoRA required |

Use `scripts/estimate_cost.py` to estimate time and cost. See `references/hardware_guide.md` for full specs.

### 4. Submit Training Job

Use `hf_jobs()` MCP tool -- submit via `hf_jobs("uv", {...})` with inline Python scripts. Do NOT save to local files unless requested. If user asks to train or fine-tune, create the script AND submit immediately.

**Key directives:**
- Always include Trackio for monitoring. Use `scripts/train_sft_example.py` as template.
- Report job details after submission: job ID, monitoring URL, estimated time.
- Jobs are asynchronous -- don't poll. Let users request status checks.

### 5. Monitor and Verify

```python
hf_jobs("ps")                                    # List all jobs
hf_jobs("inspect", {"job_id": "your-job-id"})    # Job details
hf_jobs("logs", {"job_id": "your-job-id"})       # View logs
```

## Examples

### SFT Training (Quick Start)

UV scripts use PEP 723 inline dependencies. This is the primary approach for Claude Code.

```python
hf_jobs("uv", {
    "script": """
# /// script
# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio"]
# ///

from datasets import load_dataset
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

dataset = load_dataset("trl-lib/Capybara", split="train")
dataset_split = dataset.train_test_split(test_size=0.1, seed=42)

trainer = SFTTrainer(
    model="Qwen/Qwen2.5-0.5B",
    train_dataset=dataset_split["train"],
    eval_dataset=dataset_split["test"],
    peft_config=LoraConfig(r=16, lora_alpha=32),
    args=SFTConfig(
        output_dir="my-model",
        push_to_hub=True,
        hub_model_id="username/my-model",
        num_train_epochs=3,
        eval_strategy="steps",
        eval_steps=50,
        report_to="trackio",
        project="my-training",
        run_name="baseline-run",
    )
)
trainer.train()
trainer.push_to_hub()
""",
    "flavor": "a10g-large",
    "timeout": "2h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

**Script parameter**: Accepts inline code or URLs. Local file paths do NOT work (Jobs run in isolated containers). For URLs, use Hub, GitHub, or Gist links.

**Sequence length**: TRL uses `max_length` (not `max_seq_length`). Default is 1024. Only override for longer context or memory constraints.

### Alternative Approaches

- **TRL maintained scripts**: `hf_jobs("uv", {"script": "https://github.com/huggingface/trl/blob/main/trl/scripts/sft.py", ...})`
- **HF Jobs CLI**: `hf jobs uv run --flavor a10g-large --timeout 2h --secrets HF_TOKEN "https://..."` (flags BEFORE script URL)
- **trl-jobs package**: `pip install trl-jobs && trl-jobs sft --model_name ... --dataset_name ...`

See `references/training_patterns.md` for DPO, GRPO, and multi-GPU examples.

### Dataset Validation

Validate format BEFORE GPU training to prevent the top cause of failures.

```python
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

Output markers: `READY` (use directly), `NEEDS MAPPING` (apply provided code), `INCOMPATIBLE`.

**Always validate**: Unknown datasets, DPO training (90% need mapping), any non-TRL dataset.
**Skip for**: Known TRL datasets (`trl-lib/Capybara`, `trl-lib/ultrachat_200k`).

### GGUF Conversion

Convert trained models to GGUF for llama.cpp, Ollama, and LM Studio.

```python
hf_jobs("uv", {
    "script": "<see references/gguf_conversion.md for complete script>",
    "flavor": "a10g-large",
    "timeout": "45m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"},
    "env": {
        "ADAPTER_MODEL": "username/my-finetuned-model",
        "BASE_MODEL": "Qwen/Qwen2.5-0.5B",
        "OUTPUT_REPO": "username/my-model-gguf"
    }
})
```

See `references/gguf_conversion.md` for the full guide and `scripts/convert_to_gguf.py` for the production script.

## Saving Results to Hub

**Environment is ephemeral. Without Hub push, ALL training is lost.**

Required config:
```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/model-name",
    hub_strategy="every_save",  # Push checkpoints
)
# In job submission:
{"secrets": {"HF_TOKEN": "$HF_TOKEN"}}
```

See `references/hub_saving.md` for troubleshooting.

## Monitoring with Trackio

Add `trackio` to dependencies and set `report_to="trackio"` in config. Trackio syncs metrics to an HF Space for real-time monitoring.

```python
import trackio
trackio.init(
    project="my-training",
    space_id="username/trackio",
    config={"model": "Qwen/Qwen2.5-0.5B", "dataset": "trl-lib/Capybara"}
)
# ... training code ...
trackio.finish()
```

See `references/trackio_guide.md` for complete setup.

## Common Failures

| Issue | Fix |
|-------|-----|
| OOM | Reduce `per_device_train_batch_size=1`, increase `gradient_accumulation_steps=8`, enable `gradient_checkpointing=True`, upgrade GPU |
| Dataset mismatch | Run dataset inspector first. Apply mapping code if needed. |
| Job timeout | Increase timeout (add 30% buffer), reduce epochs, save checkpoints with `hub_strategy="every_save"` |
| Hub push fails | Verify `secrets={"HF_TOKEN": "$HF_TOKEN"}`, check `push_to_hub=True`, confirm write permissions via `hf_whoami()` |
| Training hangs | Caused by `eval_strategy="steps"` without `eval_dataset`. Provide eval split or set `eval_strategy="no"`. |
| Missing deps | Add all packages to PEP 723 header. Include `sentencepiece`, `protobuf` for tokenizers. |

See `references/troubleshooting.md` and `references/reliability_principles.md` for detailed solutions.

## Checklist

Before submitting any training job, verify:

- [ ] Account has HF Pro/Team/Enterprise plan
- [ ] `hf_whoami()` confirms authentication with write permissions
- [ ] Dataset exists on Hub and format validated (for unknown datasets)
- [ ] `push_to_hub=True` and `hub_model_id` set in training config
- [ ] `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job submission
- [ ] Timeout includes 20-30% buffer over estimated training time
- [ ] Hardware matches model size (see Hardware Selection table)
- [ ] Trackio configured for monitoring (`report_to="trackio"`)
- [ ] All dependencies listed in PEP 723 header
- [ ] `trainer.push_to_hub()` called at end of script

## Resources

### References
- `references/training_methods.md` -- SFT, DPO, GRPO, Reward Modeling overview
- `references/training_patterns.md` -- Common patterns and examples
- `references/hardware_guide.md` -- Hardware specs and selection
- `references/trackio_guide.md` -- Trackio monitoring setup
- `references/hub_saving.md` -- Hub persistence and troubleshooting
- `references/gguf_conversion.md` -- GGUF conversion guide
- `references/troubleshooting.md` -- Common issues and solutions
- `references/reliability_principles.md` -- Production reliability patterns

### Scripts
- `scripts/train_sft_example.py` -- Production SFT template
- `scripts/train_dpo_example.py` -- Production DPO template
- `scripts/train_grpo_example.py` -- Production GRPO template
- `scripts/estimate_cost.py` -- Time and cost estimator
- `scripts/convert_to_gguf.py` -- GGUF conversion script
- `scripts/dataset_inspector.py` -- Dataset format validator

### External
- [TRL Documentation](https://huggingface.co/docs/trl)
- [HF Jobs Documentation](https://huggingface.co/docs/huggingface_hub/guides/jobs)
- [TRL Example Scripts](https://github.com/huggingface/trl/tree/main/examples/scripts)
- [Dataset Inspector](https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py)
