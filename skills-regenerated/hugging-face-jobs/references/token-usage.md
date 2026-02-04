# Token Usage Guide

## When Tokens Are Required

**Required:** Pushing models/datasets, accessing private repos, creating repos, any Hub API write operation.

**Not required:** Downloading public models/datasets, jobs that don't interact with Hub.

## Providing Tokens Securely

**Always use `secrets` (encrypted server-side):**

```python
hf_jobs("uv", {
    "script": "...",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}  # Auto-replaced with your login token
})
```

**Never use:**
- `env` parameter — values are visible in job logs
- Hardcoded tokens — `"hf_abc123..."` in script content
- Token strings in prompts or chat messages

## Using Tokens in Scripts

```python
import os
from huggingface_hub import HfApi

# Always verify token exists
assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"

# Auto-detection (recommended) — HfApi reads HF_TOKEN from environment
api = HfApi()

# Explicit passing (when needed)
api = HfApi(token=os.environ.get("HF_TOKEN"))
```

## Token Permission Types

| Type | Permissions | Use When |
|------|------------|----------|
| Read | Download, read content | Jobs that only consume data |
| Write | Push, create repos, modify | Jobs that produce results (most common) |
| Fine-grained | Scoped to specific repos | Production jobs with least-privilege |

Manage tokens at: https://huggingface.co/settings/tokens

## Common Authentication Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token missing or invalid | Add `secrets: {"HF_TOKEN": "$HF_TOKEN"}`, verify with `hf_whoami()` |
| 403 Forbidden | Insufficient permissions | Use a write token, check repo access rights |
| Token not found in env | `secrets` not passed to job | Use `secrets` (not `env`), verify key is exactly `HF_TOKEN` |
| Repo access denied | No access to private repo | Use token from an account with repo access |

## Security Best Practices

1. **Never commit tokens** — Use `$HF_TOKEN` placeholder, resolved at runtime
2. **Use `secrets` not `env`** — Encrypted server-side, not visible in logs
3. **Minimal permissions** — Read-only when write is not needed
4. **Rotate tokens regularly** — Especially after team member departures
5. **One token per user** — Don't share tokens across team members
