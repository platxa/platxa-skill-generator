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
| `FileNotFoundError` | Local path used in MCP | Use inline code or URL, not local file paths |
| Results not on Hub | No persistence code | Add push code + verify token has write access |
| No GPU detected | CPU flavor selected | Switch to GPU flavor: `"flavor": "a10g-large"` |
| Job stuck in queue | High demand on flavor | Try alternative flavor or wait |

## Debugging Steps

1. **Check logs:** `hf_jobs("logs", {"job_id": "..."})`
2. **Inspect status:** `hf_jobs("inspect", {"job_id": "..."})`
3. **View in browser:** `https://huggingface.co/jobs/username/job-id`

## Adding Debug Output to Scripts

```python
import os, sys
print(f"Python: {sys.version}")
print(f"HF_TOKEN present: {'HF_TOKEN' in os.environ}")
print(f"Working directory: {os.getcwd()}")
print(f"Available disk: {os.statvfs('/').f_bavail * os.statvfs('/').f_bsize / 1e9:.1f}GB")
try:
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name()}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f}GB")
except ImportError:
    print("torch not installed")
```

## Error Handling Pattern

```python
try:
    dataset.push_to_hub("username/dataset")
    print("Push successful!")
except Exception as e:
    print(f"Push failed: {e}")
    import traceback
    traceback.print_exc()
    # Re-raise so job exits with non-zero status
    raise
```

## Pre-Submission Checklist

- [ ] `secrets: {"HF_TOKEN": "$HF_TOKEN"}` in job config
- [ ] Script asserts token: `assert "HF_TOKEN" in os.environ`
- [ ] Timeout set with 20-30% buffer over expected duration
- [ ] Hardware flavor matches workload (model size, compute type)
- [ ] All dependencies listed in PEP 723 header or `dependencies` field
- [ ] Persistence code included (push to Hub or external storage)
- [ ] Error handling wraps critical operations
- [ ] Script tested locally first: `uv run script.py`
