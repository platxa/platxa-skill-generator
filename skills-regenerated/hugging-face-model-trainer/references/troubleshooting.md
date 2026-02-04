# Troubleshooting TRL Training Jobs

## Training Hangs

**Cause**: `eval_strategy="steps"` without providing `eval_dataset`.

**Fix A** (recommended): Provide eval_dataset:
```python
dataset_split = dataset.train_test_split(test_size=0.1, seed=42)
trainer = SFTTrainer(
    train_dataset=dataset_split["train"],
    eval_dataset=dataset_split["test"],
    args=SFTConfig(eval_strategy="steps", eval_steps=50),
)
```

**Fix B**: Disable evaluation: `eval_strategy="no"`

## Job Times Out

- Increase timeout (e.g., `"timeout": "4h"`)
- Reduce `num_train_epochs` or dataset size
- Use smaller model or enable LoRA
- Add 20-30% buffer to estimated time

## Model Not Saved to Hub

Check: `push_to_hub=True`, `hub_model_id` set, `secrets={"HF_TOKEN": "$HF_TOKEN"}`, write access, `trainer.push_to_hub()` called.

## Out of Memory (OOM)

Fix in order:
1. Reduce `per_device_train_batch_size` (try 4 -> 2 -> 1)
2. Increase `gradient_accumulation_steps`
3. Disable eval (saves ~40% memory)
4. Enable LoRA: `peft_config=LoraConfig(r=8, lora_alpha=16)`
5. Use larger GPU
6. Enable `gradient_checkpointing=True`

## Parameter Naming

`TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_seq_length'`
TRL uses `max_length`, not `max_seq_length`. Default 1024 works for most cases.

## Dataset Format Error

1. Check format docs: `hf_doc_fetch("https://huggingface.co/docs/trl/dataset_formats")`
2. Validate: run dataset inspector before training
3. SFT needs `messages`/`text`/`prompt+completion`; DPO needs `chosen`+`rejected`; GRPO needs prompt-only

## Import/Module Errors

Add all packages to PEP 723 header. Verify exact format with `# ///` delimiters.

## Authentication Errors

1. `mcp__huggingface__hf_whoami()` to check auth
2. Verify write permissions at https://huggingface.co/settings/tokens
3. Ensure `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config

## Job Stuck/Not Starting

- Check Jobs dashboard: https://huggingface.co/jobs
- Try different hardware flavor
- Typical GPU startup: 30-90 seconds. If >3 min: likely queued.

## Getting Help

- TRL docs: `hf_doc_search("your issue", product="trl")`
- Jobs docs: `hf_doc_fetch("https://huggingface.co/docs/huggingface_hub/guides/jobs")`
- HF forums: https://discuss.huggingface.co/
