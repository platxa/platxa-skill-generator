# gh CLI Checks Reference

Quick reference for `gh` commands used to inspect PR checks and Actions runs.

## PR Checks

```bash
# List all checks on a PR (JSON)
gh pr checks <pr> --json name,state,conclusion,detailsUrl,startedAt,completedAt

# Fallback fields (if primary fields are rejected by newer gh versions)
gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow
```

### Check JSON Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Check name (e.g., "test-suite") |
| `state` | string | Current state: queued, in_progress, completed |
| `conclusion` | string | Final result: success, failure, cancelled, timed_out, action_required |
| `detailsUrl` | string | URL to the check details (Actions run or external) |
| `startedAt` | string | ISO 8601 start time |
| `completedAt` | string | ISO 8601 completion time |
| `bucket` | string | Simplified status bucket: pass, fail, pending |
| `workflow` | object | Parent workflow info |

### Failure Detection

A check is considered failing if any of these conditions is true:
- `conclusion` in: failure, cancelled, timed_out, action_required
- `state` in: failure, error, cancelled, timed_out, action_required
- `bucket` = "fail"

## Run Inspection

```bash
# View run metadata
gh run view <run_id> --json conclusion,status,workflowName,name,event,headBranch,headSha,url

# View run log (full text output)
gh run view <run_id> --log

# View specific job log via API (fallback for in-progress runs)
gh api "/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"
```

### Run Metadata Fields

| Field | Description |
|-------|-------------|
| `conclusion` | success, failure, cancelled, skipped, timed_out, action_required |
| `status` | queued, in_progress, completed, waiting |
| `workflowName` | Name of the workflow file |
| `name` | Display name of the run |
| `event` | Trigger event: push, pull_request, workflow_dispatch |
| `headBranch` | Branch that triggered the run |
| `headSha` | Commit SHA that triggered the run |
| `url` | Web URL for the run |

## Extracting Run ID from URL

GitHub Actions URLs follow this pattern:
```
https://github.com/{owner}/{repo}/actions/runs/{run_id}
https://github.com/{owner}/{repo}/actions/runs/{run_id}/job/{job_id}
```

Regex patterns for extraction:
- Run ID: `/actions/runs/(\d+)` or `/runs/(\d+)`
- Job ID: `/actions/runs/\d+/job/(\d+)` or `/job/(\d+)`

## Authentication

```bash
# Check current auth status
gh auth status

# Login with required scopes
gh auth login
# Scopes needed: repo, workflow

# Verify repo access
gh repo view --json nameWithOwner
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "field not available" | gh CLI version drift | Use fallback field set |
| "not logged in" | Missing auth | Run `gh auth login` |
| "no pull requests found" | No PR for current branch | Specify PR number explicitly |
| "run is still in progress" | Logs not yet available | Fall back to job-level log API |
| Zip payload (PK header) | Job log returned as archive | Report as unavailable |
