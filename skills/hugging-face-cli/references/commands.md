# HF CLI Command Reference

## Authentication

```bash
hf auth login                    # Interactive login
hf auth login --token $HF_TOKEN  # Non-interactive
hf auth whoami                   # Check current user
hf auth list                     # List stored tokens
hf auth switch                   # Switch between tokens
hf auth logout                   # Log out
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
| `--force-download` | Re-download even if cached |
| `--quiet` | Output only final path |

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
| `--create-pr` | Create PR instead of direct push |
| `--every` | Upload at regular intervals (minutes) |
| `--quiet` | Output only final URL |

**Large folders:** `hf upload-large-folder <repo_id> <folder> [path] --num-workers N`

## Repository Management

```bash
hf repo create <name> [--repo-type TYPE] [--private] [--space_sdk gradio|streamlit|docker|static]
hf repo delete <repo_id> [--repo-type TYPE] [--missing-ok]
hf repo move <from_id> <to_id>
hf repo settings <repo_id> [--private true|false] [--gated auto|manual|false]
hf repo list [--repo-type TYPE] [--search Q] [--author A] [--sort FIELD] [--limit N]
```

**Branches & Tags:**
```bash
hf repo branch create|delete <repo_id> <branch> [--revision REF]
hf repo tag create <repo_id> <tag> [--revision REF] [-m "message"]
hf repo tag list|delete <repo_id> [<tag>] [-y]
```

**Sort fields:** `created_at`, `downloads`, `last_modified`, `likes`, `trending_score`

## Delete Files from Repo

```bash
hf repo-files delete <repo_id> <paths...> [--repo-type TYPE] [--create-pr]
```

Supports folders (`folder/`), wildcards (`"*.txt"`), and multiple paths.

## Cache Management

```bash
hf cache ls [--revisions] [--format table|json|csv] [--sort size:desc] [--filter "size>1GB"]
hf cache rm <repo_or_hash> [--dry-run] [-y]
hf cache prune [--dry-run] [-y]           # Remove detached revisions
hf cache verify <repo_id> [--local-dir PATH] [--revision REF]
```

## Browse Hub (Models, Datasets, Spaces)

All three share the same pattern:
```bash
hf {models|datasets|spaces} ls [--search Q] [--author A] [--filter TAG] [--sort FIELD] [--limit N] [--expand FIELDS]
hf {models|datasets|spaces} info <id> [--revision REF] [--expand FIELDS]
```

**Note:** `--sort downloads` not valid for spaces.

## Jobs (Cloud Compute)

```bash
hf jobs run [--flavor FLAVOR] <image> <command>     # Run Docker job
hf jobs uv run <script.py|url> [--with PKG] [--flavor FLAVOR]  # Run UV script
hf jobs ps | inspect <id> | logs <id> | cancel <id>  # Manage jobs
```

**Options:** `-e KEY=val` (env), `-s KEY=val` (secrets, encrypted), `--detach`, `--timeout SECS`, `--namespace ORG`

**Scheduled:** `hf jobs scheduled run @daily|@hourly|"CRON" ...` then `ps|inspect|suspend|resume|delete <id>`

**Flavors:** `cpu-basic`, `cpu-upgrade`, `cpu-xl`, `t4-small/medium`, `l4x1/x4`, `l40sx1/x4/x8`, `a10g-small/large/largex2/largex4`, `a100-large`, `h100`, `h100x8`

## Inference Endpoints

```bash
hf endpoints ls [--namespace ORG]
hf endpoints deploy <name> --repo MODEL --framework vllm --accelerator gpu --instance-size x4 --instance-type nvidia-a10g --region us-east-1 --vendor aws
hf endpoints catalog ls | catalog deploy --repo MODEL --name NAME
hf endpoints describe|update|pause|resume|scale-to-zero|delete <name>
```

**Update options:** `--repo`, `--min-replica`, `--max-replica`, `--scale-to-zero-timeout`, `--instance-size/type`

## Environment

```bash
hf env      # Print environment info (hub version, platform, token status, cache paths)
hf version  # Print CLI version
```

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | Auth token | - |
| `HF_HUB_CACHE` | Cache dir | `~/.cache/huggingface/hub` |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Timeout (sec) | 10 |

## Global Options

All commands: `--help`, `--token TOKEN`, `--repo-type model|dataset|space`
