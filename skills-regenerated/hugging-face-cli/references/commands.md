# HF CLI Command Reference

## Authentication

```bash
hf auth login                              # Interactive login
hf auth login --token $HF_TOKEN            # Non-interactive
hf auth login --token $HF_TOKEN --add-to-git-credential  # Add to git credentials
hf auth whoami                             # Check current user and orgs
hf auth list                               # List stored tokens
hf auth switch                             # Switch between tokens
hf auth logout                             # Log out (delete stored tokens)
```

## Download

```bash
hf download <repo_id> [files...] [options]
```

| Option | Description |
|--------|-------------|
| `--repo-type` | `model` (default), `dataset`, `space` |
| `--revision` | Commit, branch, or tag |
| `--include/--exclude` | Glob patterns (e.g., `"*.safetensors"`) |
| `--local-dir` | Download to directory instead of cache |
| `--cache-dir` | Override default cache location |
| `--force-download` | Re-download even if cached |
| `--dry-run` | List files without downloading |
| `--quiet` | Output only final path |
| `--token` | Override authentication token |

## Upload

```bash
hf upload <repo_id> [local_path] [path_in_repo] [options]
```

| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, `space` |
| `--include/--exclude` | Glob patterns |
| `--delete` | Patterns of remote files to delete |
| `--commit-message` | Custom commit message |
| `--commit-description` | Extended commit description |
| `--create-pr` | Create PR instead of direct push |
| `--revision` | Target branch or ref |
| `--every` | Auto-upload interval in minutes |
| `--quiet` | Output only final URL |

**Large folders:** `hf upload-large-folder <repo_id> <folder> [path]` (resumable, chunked)

## Repository Management

```bash
hf repo create <name> [--repo-type TYPE] [--private] [--space-sdk gradio|streamlit|docker|static] [--exist-ok]
hf repo delete <repo_id> [--repo-type TYPE]
hf repo move <from_id> <to_id>
hf repo settings <repo_id> [--private true|false] [--gated auto|manual|false]
hf repo list [--repo-type TYPE] [--search Q] [--author A] [--sort FIELD] [--limit N]
```

**Branches:**
```bash
hf repo branch create <repo_id> <branch> [--revision REF]
hf repo branch delete <repo_id> <branch>
```

**Tags:**
```bash
hf repo tag create <repo_id> <tag> [--revision REF] [-m "message"]
hf repo tag list <repo_id>
hf repo tag delete <repo_id> <tag> [-y]
```

**Sort fields:** `created_at`, `downloads`, `last_modified`, `likes`, `trending_score`

## Delete Files from Repo

```bash
hf repo-files delete <repo_id> <paths...> [--repo-type TYPE] [--create-pr]
```

Supports folders (`folder/`), wildcards (`"*.txt"`), and multiple paths. Wildcard matching uses `fnmatch` which matches `*` across path boundaries.

## Cache Management

```bash
hf cache ls [--revisions] [--format table|json|csv] [--sort size:desc] [--filter "size>1GB"] [--quiet] [--limit N]
hf cache rm <repo_or_hash...> [--dry-run] [-y] [--cache-dir PATH]
hf cache prune [--dry-run] [-y]
hf cache verify <repo_id> [--local-dir PATH] [--revision REF] [--fail-on-missing-files] [--fail-on-extra-files]
```

Pipe quiet output for batch operations: `hf cache rm $(hf cache ls --filter "accessed>1y" -q) -y`

## Browse Hub

All three resources share the same pattern:
```bash
hf {models|datasets|spaces} ls [--search Q] [--author A] [--filter TAG] [--sort FIELD] [--limit N] [--expand FIELDS]
hf {models|datasets|spaces} info <id> [--revision REF] [--expand FIELDS]
```

**Papers:**
```bash
hf papers ls [--sort trending|recent] [--date YYYY-MM-DD|today] [--limit N]
```

## Jobs (Cloud Compute)

```bash
hf jobs run [--flavor FLAVOR] [--timeout DURATION] [--detach] [--namespace ORG] <image> <command>
hf jobs uv run [--flavor FLAVOR] [--with PKG] <script.py|url> [args...]
hf jobs ps [-a] [--filter label=KEY=VALUE]
hf jobs inspect <job_id>
hf jobs logs <job_id>
hf jobs stats <job_id>
hf jobs cancel <job_id>
```

**Environment/Secrets:** `-e KEY=val`, `-s KEY=val`, `--env-file FILE`, `--secrets-file FILE`, `--secrets HF_TOKEN`

**Labels:** `-l KEY=VALUE` for metadata, `--filter label=KEY=VALUE` for filtering

**Scheduled:**
```bash
hf jobs scheduled run @daily|@hourly|"CRON" [options] <image> <command>
hf jobs scheduled uv run @daily|@hourly|"CRON" [options] <script.py>
hf jobs scheduled ps|inspect|suspend|resume|delete <id>
```

**Timeout units:** `s` (seconds), `m` (minutes), `h` (hours), `d` (days). Default: 30min.

**Flavors:** `cpu-basic`, `cpu-upgrade`, `t4-small`, `t4-medium`, `l4x1`, `l4x4`, `l40sx1`, `l40sx4`, `l40sx8`, `a10g-small`, `a10g-large`, `a10g-largex2`, `a10g-largex4`, `a100-large`, `h100`, `h100x8`, `v5e-1x1`, `v5e-2x2`, `v5e-2x4`

## Inference Endpoints

```bash
hf endpoints ls [--namespace ORG]
hf endpoints catalog ls
hf endpoints catalog deploy --repo MODEL [--name NAME]
hf endpoints deploy <name> --repo MODEL --framework FRAMEWORK --accelerator TYPE --instance-size SIZE --instance-type TYPE --region REGION --vendor VENDOR
hf endpoints describe|update|pause|resume|scale-to-zero|delete <name> [--namespace ORG]
```

**Update options:** `--repo`, `--min-replica`, `--max-replica`, `--scale-to-zero-timeout`, `--instance-size`, `--instance-type`

## Global Options

All commands accept: `--help`, `--token TOKEN`

Most resource commands accept: `--repo-type model|dataset|space`

## Environment

```bash
hf env      # Print environment info (hub version, platform, token status, cache paths)
hf version  # Print CLI version
```

## Installation

```bash
# Standalone (recommended)
curl -LsSf https://hf.co/cli/install.sh -o install.sh && bash install.sh

# Via uv (no install, always latest)
uvx hf <command>

# Via pip
pip install -U huggingface_hub

# Via Homebrew
brew install huggingface-cli
```
