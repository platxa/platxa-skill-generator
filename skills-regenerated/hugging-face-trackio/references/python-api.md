# Trackio Python API Reference

## Installation

```bash
pip install trackio
# or
uv pip install trackio
```

## Core Functions

### trackio.init()

Start a new tracking run. Call once at the beginning of a training script.

```python
trackio.init(
    project="my-project",           # Required: groups runs together
    name="run-name",                # Optional: identifies this run
    config={"lr": 1e-4, "epochs": 5},  # Optional: hyperparameters
    space_id="username/trackio",    # Optional: sync to HF Space
    group="experiment-group",       # Optional: sidebar grouping
)
```

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `project` | `str` | Required | Project name for grouping runs |
| `name` | `str` | Auto-generated | Display name for this run |
| `config` | `dict` | `None` | Hyperparameters saved with the run |
| `space_id` | `str` | `None` | HF Space ID for remote dashboard |
| `group` | `str` | `None` | Group label in dashboard sidebar |

### trackio.log()

Log one or more metrics at the current step. Call repeatedly during training.

```python
trackio.log({
    "train_loss": 0.45,
    "train_accuracy": 0.87,
    "val_loss": 0.39,
    "val_accuracy": 0.90,
    "epoch": 2,
})
```

Each call increments the step counter. All values must be numeric.

### trackio.finish()

Finalize the run. Flushes all pending metrics to storage and syncs to Space if configured.

```python
trackio.finish()
```

Always call this at the end of training. For cloud/remote environments, `finish()` ensures metrics persist before the instance terminates.

### trackio.show()

Launch the local Gradio dashboard.

```python
trackio.show()
```

### trackio.sync()

Sync a local project to a Hugging Face Space.

```python
trackio.sync(project="my-project", space_id="username/my-experiments")
```

## wandb Compatibility

Drop-in replacement for wandb:

```python
import trackio as wandb

wandb.init(project="my-project", config={"lr": 1e-4})
wandb.log({"loss": 0.5})
wandb.finish()
```

## TRL Integration

Set `report_to="trackio"` in TRL config for automatic metric logging:

```python
from trl import SFTConfig, SFTTrainer
import trackio

trackio.init(project="sft-run", space_id="user/trackio")

config = SFTConfig(
    output_dir="./output",
    report_to="trackio",
    num_train_epochs=3,
    push_to_hub=True,
    hub_model_id="user/my-model",
)

trainer = SFTTrainer(model=model, args=config, train_dataset=ds)
trainer.train()
trackio.finish()
```

TRL automatically logs: `train_loss`, `learning_rate`, eval metrics, and throughput.

## Grouping Runs

Organize experiments in the dashboard sidebar:

```python
trackio.init(project="sweep", name="lr-1e4", group="learning_rate")
trackio.init(project="sweep", name="lr-1e3", group="learning_rate")
trackio.init(project="sweep", name="bs-16", group="batch_size")
```

## Dashboard Embedding

Embed Space dashboards with URL query parameters:

```
https://user-trackio.hf.space/?project=my-project&metrics=loss,accuracy&sidebar=hidden&smoothing=5
```

Parameters: `project`, `metrics`, `sidebar` (`hidden`/`collapsed`), `smoothing` (0-20), `xmin`, `xmax`.

## Storage

- **Local**: SQLite database in `~/.trackio/` by default
- **Remote**: HF Dataset backing the Space (via `space_id`)
- **Sync**: `trackio.sync()` copies local data to a Space
