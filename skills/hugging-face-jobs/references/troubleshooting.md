# Troubleshooting Guide

## Quick Diagnosis

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 401 Unauthorized | Token missing | `secrets: {"HF_TOKEN": "$HF_TOKEN"}` |
| 403 Forbidden | Wrong permissions | Use write token, check repo access |
| `KeyError: 'HF_TOKEN'` | Secrets not passed | Use `secrets` not `env` |
| CUDA out of memory | Hardware too small | Reduce batch size or upgrade flavor |
| Job timeout | Default 30min exceeded | Set `"timeout": "2h"` with 20-30% buffer |
| `ModuleNotFoundError` | Missing dependency | Add to PEP 723: `# dependencies = [...]` |
| `FileNotFoundError` | Local path in MCP | Use inline code or URL, not local paths |
| Results not on Hub | No persistence code | Add push code + verify token |
| No GPU found | CPU flavor used | Use GPU flavor: `"flavor": "a10g-large"` |

## Debugging Steps

1. **Check logs:** `hf_jobs("logs", {"job_id": "..."})`
2. **Inspect status:** `hf_jobs("inspect", {"job_id": "..."})`
3. **Job URL:** `https://huggingface.co/jobs/username/job-id`

## Add Debugging to Scripts

```python
import os, sys
print(f"Python: {sys.version}")
print(f"HF_TOKEN present: {'HF_TOKEN' in os.environ}")
try:
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
except ImportError:
    print("torch not installed")
```

## Error Handling Pattern

```python
try:
    dataset.push_to_hub("username/dataset")
    print("Push successful")
except Exception as e:
    print(f"Push failed: {e}")
    import traceback
    traceback.print_exc()
    raise
```

## Pre-Submission Checklist

- [ ] Token: `secrets={"HF_TOKEN": "$HF_TOKEN"}`
- [ ] Script verifies token: `assert "HF_TOKEN" in os.environ`
- [ ] Timeout set with buffer
- [ ] Hardware matches workload
- [ ] Dependencies in PEP 723 header
- [ ] Persistence code included
- [ ] Error handling added
- [ ] Tested locally first (`uv run script.py`)
