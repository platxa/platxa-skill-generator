# Token Usage Guide

## When Tokens Are Required

**Required:** Pushing models/datasets, accessing private repos, creating repos, Hub API operations.
**Not required:** Downloading public models/datasets, jobs without Hub interaction.

## Providing Tokens

**Recommended: Automatic token via secrets (encrypted server-side)**
```python
hf_jobs("uv", {
    "script": "...",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}  # Auto-replaced with your login token
})
```

**Avoid:** Hardcoded tokens (`"hf_abc123..."`) or `env` instead of `secrets` (visible in logs).

## Using in Scripts

```python
import os
from huggingface_hub import HfApi

# Verify token exists
assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"

# Auto-detection (recommended)
api = HfApi()  # Uses HF_TOKEN from environment automatically

# Explicit (when needed)
api = HfApi(token=os.environ.get("HF_TOKEN"))
```

## Token Types

- **Read:** Download/read content
- **Write:** Push models/datasets, create repos (most common for jobs)
- **Organization:** Act on behalf of org

Manage at: https://huggingface.co/settings/tokens

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token missing/invalid | Add `secrets: {"HF_TOKEN": "$HF_TOKEN"}`, check `hf_whoami()` |
| 403 Forbidden | Insufficient permissions | Ensure write token, check repo access |
| Token not found | `secrets` not passed | Use `secrets` (not `env`), verify key is `HF_TOKEN` |
| Repo access denied | No access to private repo | Use token from account with access |

## Security Best Practices

1. Never commit tokens - use `$HF_TOKEN` placeholder
2. Use `secrets` not `env` - encrypted server-side
3. Use minimal permissions - read-only when write not needed
4. Rotate tokens regularly
5. Each user uses own token
