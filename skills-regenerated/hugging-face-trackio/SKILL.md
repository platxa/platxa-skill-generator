---
name: hugging-face-trackio
description: Guide for tracking ML training experiments with Trackio. Covers the Python API for logging metrics during training (trackio.init, trackio.log, trackio.finish) and the CLI for retrieving metrics after training (trackio list, trackio get). Includes HF Space syncing, TRL integration, wandb compatibility, and JSON output for automation.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Task
metadata:
  version: "1.0.0"
  author: platxa
  tags:
    - ml
    - experiment-tracking
    - hugging-face
    - metrics
    - observability
    - guide
  provenance:
    upstream_source: hugging-face-trackio
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T16:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.61
---

# Trackio Experiment Tracking

Track and visualize ML training experiments with Trackio, a lightweight experiment tracking library from Hugging Face. Invoke this skill when the user needs to log metrics during training or retrieve and analyze logged experiment data.

## Overview

Trackio provides two interfaces for ML experiment tracking:

| Task | Interface | When to Use |
|------|-----------|-------------|
| **Log metrics** during training | Python API (`trackio.init`, `trackio.log`) | Writing or modifying training scripts |
| **Retrieve metrics** after training | CLI (`trackio list`, `trackio get`) | Querying results, automation, analysis |

Trackio is API-compatible with wandb (`import trackio as wandb`), stores data locally in SQLite by default, and optionally syncs to Hugging Face Spaces for persistent dashboards.

See `references/python-api.md` for the full Python API and `references/cli-reference.md` for all CLI commands.

## Workflow

### Step 1: Install Trackio

```bash
pip install trackio
```

### Step 2: Initialize a Run

```python
import trackio

trackio.init(
    project="my-project",
    name="baseline-v1",
    config={"learning_rate": 1e-4, "epochs": 10, "batch_size": 16},
    space_id="username/trackio",  # omit for local-only
)
```

Key parameters for `trackio.init()`:

| Parameter | Purpose | Required |
|-----------|---------|----------|
| `project` | Groups runs together | Yes |
| `name` | Identifies this specific run | No |
| `config` | Hyperparameters dictionary | No |
| `space_id` | HF Space for remote dashboard | No |
| `group` | Organizes related runs in sidebar | No |

### Step 3: Log Metrics

```python
for epoch in range(10):
    loss, acc = train_epoch()
    trackio.log({"loss": loss, "accuracy": acc, "epoch": epoch})
```

For TRL trainers, set `report_to="trackio"` in `SFTConfig` or `DPOConfig` for automatic metric logging without manual `trackio.log()` calls.

### Step 4: Finalize

```python
trackio.finish()
```

Always call `trackio.finish()` to flush pending metrics. For cloud/remote training, this ensures all data syncs to the Space before the instance terminates.

### Step 5: Retrieve Results

```bash
trackio list projects --json
trackio get run --project my-project --run baseline-v1 --json
trackio get metric --project my-project --run baseline-v1 --metric loss --json
```

Append `--json` to any command for structured output suitable for automation and LLM agents.

## Local vs Remote Dashboards

### Local (Default)

Trackio stores metrics in a local SQLite database. Launch the dashboard with:

```bash
trackio show --project my-project
```

Or from Python: `trackio.show()`.

### Remote (HF Space)

Pass `space_id` to sync metrics to a Hugging Face Space. The Space auto-creates if it does not exist.

```python
trackio.init(project="my-project", space_id="username/trackio")
```

For remote training (cloud GPUs, HF Jobs): always use `space_id` since local storage is lost when the instance terminates.

### Sync Existing Data

Push a local project to a remote Space:

```python
trackio.sync(project="my-project", space_id="username/my-experiments")
```

Or via CLI:

```bash
trackio sync --project my-project --space-id username/my-experiments
```

## TRL Integration

When using TRL trainers (`SFTTrainer`, `DPOTrainer`, `GRPOTrainer`), configure automatic Trackio logging:

```python
from trl import SFTConfig, SFTTrainer
import trackio

trackio.init(
    project="sft-training",
    space_id="username/trackio",
    config={"model": "Qwen/Qwen2.5-0.5B", "dataset": "trl-lib/Capybara"},
)

config = SFTConfig(
    output_dir="./output",
    report_to="trackio",
    num_train_epochs=3,
    eval_strategy="steps",
    eval_steps=50,
)

trainer = SFTTrainer(model=model, args=config, train_dataset=dataset)
trainer.train()
trackio.finish()
```

TRL automatically logs: training loss, learning rate, eval metrics, and throughput.

## wandb Compatibility

Trackio is a drop-in replacement for wandb. Change only the import:

```python
import trackio as wandb

wandb.init(project="my-project")
wandb.log({"loss": 0.5, "accuracy": 0.85})
wandb.finish()
```

Existing wandb-based code works without further changes.

## Examples

### Quick Logging Setup

```python
import trackio

trackio.init(project="experiment-1", space_id="user/trackio")
for step in range(100):
    trackio.log({"loss": 1.0 / (step + 1), "step": step})
trackio.finish()
```

### Retrieve Latest Loss Value

```bash
trackio get metric --project experiment-1 --run my-run --metric loss --json \
  | jq '.values[-1].value'
```

### Compare Runs

```bash
trackio list runs --project experiment-1 --json
trackio get run --project experiment-1 --run run-1 --json
trackio get run --project experiment-1 --run run-2 --json
```

### Embed Dashboard in a Web Page

```html
<iframe
  src="https://user-trackio.hf.space/?project=my-project&metrics=loss,accuracy&sidebar=hidden"
  style="width:1600px; height:500px; border:0;">
</iframe>
```

Query parameters: `project`, `metrics` (comma-separated), `sidebar` (`hidden`/`collapsed`), `smoothing` (0-20), `xmin`, `xmax`.

## Best Practices

- **Always call `trackio.finish()`** to flush metrics, especially in remote environments.
- **Use `space_id` for cloud training** (HF Jobs, rented GPUs) so metrics survive instance termination.
- **Keep config minimal** -- only log hyperparameters useful for comparing runs.
- **Use `--json` flag** when scripting CLI commands or integrating with automation pipelines.
- **Group related runs** with `group` parameter for organized dashboard sidebar.
- **Use `report_to="trackio"`** with TRL instead of manual `trackio.log()` calls.

## Common Issues

| Problem | Solution |
|---------|----------|
| Metrics lost after cloud job ends | Add `space_id` parameter to `trackio.init()` |
| Dashboard not showing new metrics | Call `trackio.finish()` to flush pending data |
| Need wandb compatibility | Use `import trackio as wandb` -- API-compatible |
| Want JSON output from CLI | Append `--json` to any `trackio list` or `trackio get` command |
| Sync local data to Space | Use `trackio.sync(project="...", space_id="...")` |

## Checklist

Before finalizing a Trackio integration, verify:

- [ ] `trackio` is installed (`pip install trackio`)
- [ ] `trackio.init()` is called with `project` name before logging
- [ ] `trackio.log()` is called inside the training loop with numeric metrics
- [ ] `trackio.finish()` is called after training completes
- [ ] `space_id` is set for cloud/remote training environments
- [ ] TRL trainers use `report_to="trackio"` instead of manual logging
- [ ] CLI queries use `--json` flag when output feeds scripts or agents
- [ ] Dashboard is accessible via `trackio show` or the HF Space URL

## Resources

- `references/python-api.md` -- Complete Python API with all functions and parameters
- `references/cli-reference.md` -- Full CLI command reference with JSON output formats
- [Trackio Documentation](https://huggingface.co/docs/trackio/index)
- [Trackio GitHub](https://github.com/gradio-app/trackio)
