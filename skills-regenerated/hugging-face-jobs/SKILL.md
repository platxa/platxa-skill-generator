---
name: hugging-face-jobs
description: >-
  Run workloads on Hugging Face Jobs infrastructure. Automates UV script submission,
  Docker jobs, hardware selection, authentication, secrets management, timeout
  configuration, result persistence, scheduled jobs, and webhooks via the hf_jobs()
  MCP tool. For model training workflows, see the model-trainer skill.
allowed-tools:
  - Bash
  - Read
  - WebFetch
  - WebSearch
  - Write
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - automation
    - ml-ops
    - hugging-face
    - gpu-compute
    - batch-inference
  provenance:
    upstream_source: "hugging-face-jobs"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T12:21:57Z"
    generator_version: "1.0.0"
    intent_confidence: 0.91
---

# Running Workloads on Hugging Face Jobs

Run any workload on fully managed HF infrastructure with no local setup required.

## Overview

This skill automates submitting and managing compute jobs on Hugging Face Jobs. It handles UV script jobs, Docker container jobs, scheduled recurring jobs, and webhook-triggered jobs. Target audience: ML/AI engineers and data scientists who need cloud GPU/TPU compute for batch inference, data processing, synthetic data generation, and experiments.

**For model training:** Use the `model-trainer` skill for TRL-based fine-tuning workflows.

## Triggers

Run this automation when:
- User needs to execute Python scripts on cloud GPU/TPU hardware
- Batch inference, data processing, or synthetic data generation is required
- A recurring job needs scheduling (daily, weekly, cron)
- A webhook should trigger a job on Hub repository changes
- User asks about HF Jobs hardware, pricing, or configuration

## Key Directives

These rules must always be followed:

1. **Use `hf_jobs()` MCP tool** — Pass script content as an inline string. Never save to local files (the remote container cannot access the local filesystem).
2. **Always handle auth** — Hub operations require `secrets: {"HF_TOKEN": "$HF_TOKEN"}`. Never use `env` (visible in logs) or hardcode tokens.
3. **Provide job details after submission** — Return the job ID, monitoring URL (`https://huggingface.co/jobs/username/job-id`), and estimated completion time.
4. **Set appropriate timeouts** — Default is 30 minutes. Add 20-30% buffer. On timeout the job is killed and unsaved progress is lost.
5. **Always persist results** — The job environment is ephemeral. All files are deleted when the job ends. Push results to Hub or external storage.

## Prerequisites

- HF account with Pro, Team, or Enterprise plan
- Authenticated session: verify with `hf_whoami()`
- HF_TOKEN with appropriate permissions (read for downloads, write for pushing results)

## Process: UV Script Jobs

UV scripts are the recommended approach for Python workloads.

### Step 1: Prepare the Script

Write the script as an inline string with PEP 723 dependency metadata:

```python
script = """
# /// script
# dependencies = ["transformers", "torch", "datasets"]
# ///
import os
assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"

from transformers import pipeline
result = pipeline("sentiment-analysis")("I love HF!")
print(result)
"""
```

If the script exists as a file, read it first: `Path("script.py").read_text()`.

### Step 2: Configure and Submit

```python
hf_jobs("uv", {
    "script": script,
    "flavor": "cpu-basic",
    "timeout": "30m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

**Options:**
- `"image"`: Custom Docker image (e.g., `"vllm/vllm-openai:latest"`)
- `"dependencies"`: Extra deps beyond PEP 723 header
- `"python"`: Python version (default: 3.12)

### Step 3: Monitor and Verify

```python
hf_jobs("ps")                              # List all jobs
hf_jobs("logs", {"job_id": "..."})         # Stream logs
hf_jobs("inspect", {"job_id": "..."})      # Job details/status
hf_jobs("cancel", {"job_id": "..."})       # Cancel running job
```

## Process: Docker Jobs

Use Docker jobs for custom images, non-Python workloads, or complex environments:

```python
hf_jobs("run", {
    "image": "pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
    "command": ["python", "-c", "import torch; print(torch.cuda.get_device_name())"],
    "flavor": "a10g-small",
    "timeout": "1h"
})
```

**When to use Docker over UV:** Custom base images, system-level dependencies, non-Python languages, or HF Spaces as images (`"image": "hf.co/spaces/lhoestq/duckdb"`).

## Process: Scheduled Jobs and Webhooks

### Scheduled Jobs

```python
hf_jobs("scheduled uv", {
    "script": "...",
    "schedule": "@daily",        # or cron: "0 9 * * 1"
    "flavor": "cpu-basic",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

Schedules: `@hourly`, `@daily`, `@weekly`, `@monthly`, or cron syntax.
Manage: `hf_jobs("scheduled ps/inspect/suspend/resume/delete", {...})`

### Webhooks

Trigger jobs on Hub repository changes via `create_webhook()`. The webhook payload is available as `WEBHOOK_PAYLOAD` environment variable in the job.

## Hardware Selection

| Workload | Flavor | VRAM | Notes |
|----------|--------|------|-------|
| Testing | `cpu-basic` | — | Cheapest option |
| Data processing | `cpu-upgrade` | — | More CPU/RAM |
| <1B models | `t4-small` | 16GB | Demos, small inference |
| 1-7B models | `l4x1` / `a10g-small` | 24GB | Production inference |
| 7-13B models | `a10g-large` | 24GB | Larger batch sizes |
| 13B+ models | `a100-large` | 40GB | Large model inference |
| Multi-GPU | `l4x4` / `a10g-largex4` | 96GB | Distributed workloads |
| TPU (JAX/Flax) | `v5e-1x1` to `v5e-2x4` | — | JAX workloads |

Start small for testing, scale up as needed. See `references/hardware-guide.md` for detailed specs and cost estimates.

## Result Persistence

**The job environment is ephemeral. Without persistence, ALL work is lost.**

```python
# Push model to Hub
model.push_to_hub("user/model", token=os.environ["HF_TOKEN"])

# Push dataset to Hub
dataset.push_to_hub("user/dataset", token=os.environ["HF_TOKEN"])

# Upload arbitrary files
from huggingface_hub import HfApi
api = HfApi(token=os.environ.get("HF_TOKEN"))
api.upload_file("results.json", "results.json", "user/results", repo_type="dataset")
```

Always include `secrets: {"HF_TOKEN": "$HF_TOKEN"}` in job config and assert token existence in script. See `references/hub-saving.md` for complete patterns.

## Authentication and Secrets

Use `secrets` (encrypted server-side), never `env` (visible in logs):

```python
"secrets": {"HF_TOKEN": "$HF_TOKEN"}   # Auto-replaced with your token
```

**Token types:** Read (download/access), Write (push/create repos), Organization (act on behalf of org).
Manage tokens at: `https://huggingface.co/settings/tokens`

See `references/token-usage.md` for detailed auth patterns and common errors.

## Verification

After submitting a job:

1. **Confirm submission** — Check returned job ID is valid
2. **Monitor progress** — `hf_jobs("logs", {"job_id": "..."})` for real-time output
3. **Check completion** — `hf_jobs("inspect", {"job_id": "..."})` for final status
4. **Verify persistence** — Confirm results appear on Hub or external storage
5. **Report to user** — Job ID, status, monitoring URL, and output location

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token missing | Add `secrets: {"HF_TOKEN": "$HF_TOKEN"}` |
| CUDA out of memory | Hardware too small | Reduce batch size or upgrade flavor |
| Job timeout | Default 30min exceeded | Set `"timeout": "2h"` with buffer |
| ModuleNotFoundError | Missing dependency | Add to PEP 723: `# dependencies = [...]` |
| Results not on Hub | No persistence code | Add push code + verify token |
| FileNotFoundError | Local path in MCP | Use inline code or URL, not local paths |

See `references/troubleshooting.md` for full debugging guide.

## Example Patterns

### Synthetic Data Generation

Use Chain-of-Thought self-instruct: generate diverse prompts, produce reasoned responses, filter for quality, push curated dataset to Hub. Requires GPU flavor for inference.

### Batch Inference with vLLM

Load a dataset from Hub, run vLLM inference on GPU, collect responses, push results dataset to Hub. Use `a10g-large` or `a100-large` depending on model size.

### Large-Scale Data Analysis

Stream parquet files from Hub with Polars, compute aggregate statistics, push results. CPU flavors are typically sufficient.

## Safety

- **Never hardcode tokens** — Always use `secrets` parameter with `$HF_TOKEN` placeholder
- **Validate hardware** — Confirm the flavor matches workload requirements before submission
- **Cost awareness** — GPU flavors incur hourly costs; set timeouts to prevent runaway billing
- **Idempotency** — Jobs are not idempotent; resubmission creates a new job
- **Reversibility** — Pushed results can be deleted from Hub; compute costs cannot be reversed

## API Quick Reference

| Operation | MCP Tool | CLI Equivalent |
|-----------|----------|----------------|
| UV script | `hf_jobs("uv", {...})` | `hf jobs uv run script.py` |
| Docker job | `hf_jobs("run", {...})` | `hf jobs run image cmd` |
| List jobs | `hf_jobs("ps")` | `hf jobs ps` |
| View logs | `hf_jobs("logs", {...})` | `hf jobs logs <id>` |
| Cancel | `hf_jobs("cancel", {...})` | `hf jobs cancel <id>` |
| Inspect | `hf_jobs("inspect", {...})` | `hf jobs inspect <id>` |
| Scheduled | `hf_jobs("scheduled uv", {...})` | `hf jobs scheduled uv ...` |
