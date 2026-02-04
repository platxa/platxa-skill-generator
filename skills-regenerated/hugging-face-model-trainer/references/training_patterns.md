# Common Training Patterns

## Multi-GPU Training

TRL/Accelerate handles distribution automatically. No code changes needed.

```python
hf_jobs("uv", {
    "script": "# Same script as single GPU",
    "flavor": "a10g-largex2",  # 2x A10G GPUs
    "timeout": "4h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

Effective batch = `per_device_train_batch_size` x `num_gpus` x `gradient_accumulation_steps`.

## DPO Training

```python
config = DPOConfig(
    output_dir="dpo-model",
    push_to_hub=True, hub_model_id="username/dpo-model",
    beta=0.1,  # KL penalty
    num_train_epochs=1,  # DPO needs fewer epochs
    learning_rate=5e-7,  # Much lower LR than SFT
    eval_strategy="steps", eval_steps=50,
    report_to="trackio",
)
trainer = DPOTrainer(
    model="Qwen/Qwen2.5-0.5B-Instruct",  # Use instruct model
    train_dataset=train_split, eval_dataset=eval_split,
    args=config,
)
```

## GRPO Training

Use TRL maintained script:
```python
hf_jobs("uv", {
    "script": "https://raw.githubusercontent.com/huggingface/trl/main/examples/scripts/grpo.py",
    "script_args": ["--model_name_or_path", "Qwen/Qwen2.5-0.5B-Instruct",
                    "--dataset_name", "trl-lib/math_shepherd",
                    "--output_dir", "grpo-model", "--push_to_hub"],
    "flavor": "a10g-large", "timeout": "4h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

## Eval Dataset Requirements

If `eval_strategy="steps"` or `"epoch"`, you MUST provide `eval_dataset` or training will hang.

```python
dataset_split = dataset.train_test_split(test_size=0.1, seed=42)
trainer = SFTTrainer(
    train_dataset=dataset_split["train"],
    eval_dataset=dataset_split["test"],  # Required when eval enabled
    args=SFTConfig(eval_strategy="steps", eval_steps=100),
)
```

To skip eval: set `eval_strategy="no"` and omit `eval_dataset`.

## Pattern Selection

| Use Case | Hardware | Time |
|----------|----------|------|
| SFT training | a10g-large | 2-6h |
| Large dataset >10K | a10g-largex2 | 4-12h |
| DPO preference | a10g-large | 2-4h |
| GRPO online RL | a10g-large | 3-6h |
