# Saving Training Results to Hugging Face Hub

Training environments are ephemeral. ALL results are lost when a job completes unless pushed to the Hub.

## Required Configuration

**Training config:**
```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/model-name",
)
```

**Job submission:**
```python
hf_jobs("uv", {
    "script": "...",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

## Checkpoint Saving

```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/my-model",
    save_strategy="steps",
    save_steps=100,
    save_total_limit=3,
    hub_strategy="every_save",
)
```

## Verification Checklist

- [ ] `push_to_hub=True` in training config
- [ ] `hub_model_id` specified with username
- [ ] `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config
- [ ] Repository name doesn't conflict
- [ ] User has write access

## Troubleshooting

| Error | Fix |
|-------|-----|
| 401 Unauthorized | Verify `secrets` includes HF_TOKEN. Re-login: `huggingface-cli login` |
| 403 Forbidden | Check write access. Verify org membership if using org namespace. |
| Repo not found | Create repo first or check name format |
| Push failed | Network issue. Checkpoints may be saved. Re-run push manually. |
| Model not visible | Check if private. Verify `hub_model_id` namespace. Wait a few minutes. |

## Best Practices

1. Always enable `push_to_hub=True`
2. Use checkpoint saving for long runs
3. Verify Hub push in logs before job completes
4. Use descriptive repo names
5. Call `trainer.push_to_hub()` at end of script
