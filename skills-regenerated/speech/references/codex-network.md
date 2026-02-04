# Network and Sandbox Notes

Speech generation uses the OpenAI Audio API, so the CLI needs outbound network access. This reference covers environment-specific configuration.

## Why Am I Asked to Approve Every Call?

In sandboxed environments (such as Codex), network access may be disabled by default or require confirmation before networked commands run.

## Reducing Approval Prompts

If you trust the repo and want fewer prompts, enable network access and relax the approval policy.

Example `~/.codex/config.toml`:
```toml
approval_policy = "never"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

Single session override:
```bash
codex --sandbox workspace-write --ask-for-approval never
```

## Safety Note

Enabling network and disabling approvals reduces friction but increases risk with untrusted code or repositories. Use caution.
