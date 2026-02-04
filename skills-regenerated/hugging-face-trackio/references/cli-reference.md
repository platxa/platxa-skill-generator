# Trackio CLI Reference

The `trackio` CLI provides terminal access to query experiment tracking data. All `list` and `get` commands support `--json` for structured output.

## Command Summary

| Task | Command |
|------|---------|
| List projects | `trackio list projects` |
| List runs | `trackio list runs --project <name>` |
| List metrics | `trackio list metrics --project <name> --run <name>` |
| List system metrics | `trackio list system-metrics --project <name> --run <name>` |
| Get project summary | `trackio get project --project <name>` |
| Get run summary | `trackio get run --project <name> --run <name>` |
| Get metric values | `trackio get metric --project <name> --run <name> --metric <name>` |
| Get system metrics | `trackio get system-metric --project <name> --run <name>` |
| Show dashboard | `trackio show [--project <name>]` |
| Sync to Space | `trackio sync --project <name> --space-id <id>` |

## List Commands

```bash
trackio list projects                                          # All projects
trackio list projects --json                                   # JSON output
trackio list runs --project my-project --json                  # Runs in project
trackio list metrics --project my-project --run run-1 --json   # Metrics for run
trackio list system-metrics --project my-project --run run-1 --json
```

## Get Commands

```bash
trackio get project --project my-project --json                # Project summary
trackio get run --project my-project --run run-1 --json        # Run summary
trackio get metric --project my-project --run run-1 --metric loss --json
trackio get system-metric --project my-project --run run-1 --json
trackio get system-metric --project my-project --run run-1 --metric gpu_utilization --json
```

## Dashboard Commands

```bash
trackio show                                  # Launch dashboard
trackio show --project my-project             # Specific project
trackio show --theme soft                     # Custom theme
trackio show --mcp-server                     # Enable MCP server
trackio show --color-palette "#FF0000,#00FF00"
```

## Sync Commands

```bash
trackio sync --project my-project --space-id user/trackio
trackio sync --project my-project --space-id user/trackio --private
trackio sync --project my-project --space-id user/trackio --force
```

## Global Options

| Flag | Purpose |
|------|---------|
| `--project` | Project name (required for most commands) |
| `--run` | Run name (required for run-specific commands) |
| `--metric` | Metric name (required for metric queries) |
| `--json` | Structured JSON output instead of human-readable |
| `--theme` | Dashboard theme (`show` only) |
| `--mcp-server` | Enable MCP server mode (`show` only) |
| `--private` | Create private Space (`sync` only) |
| `--force` | Overwrite existing remote data (`sync` only) |

## JSON Output Formats

### List Projects

```json
{"projects": ["project1", "project2"]}
```

### List Runs

```json
{"project": "my-project", "runs": ["run-1", "run-2"]}
```

### Project Summary

```json
{
  "project": "my-project",
  "num_runs": 3,
  "runs": ["run-1", "run-2", "run-3"],
  "last_activity": 100
}
```

### Run Summary

```json
{
  "project": "my-project",
  "run": "run-1",
  "num_logs": 50,
  "metrics": ["loss", "accuracy"],
  "config": {"learning_rate": 0.001},
  "last_step": 49
}
```

### Metric Values

```json
{
  "project": "my-project",
  "run": "run-1",
  "metric": "loss",
  "values": [
    {"step": 0, "timestamp": "2025-01-01T00:00:00", "value": 0.5},
    {"step": 1, "timestamp": "2025-01-01T00:01:00", "value": 0.4}
  ]
}
```

## Automation Patterns

### Extract Latest Metric Value

```bash
trackio get metric --project my-project --run run-1 --metric loss --json \
  | jq '.values[-1].value'
```

### Export Run Summary

```bash
trackio get run --project my-project --run run-1 --json > run_summary.json
```

### Filter Runs by Name

```bash
trackio list runs --project my-project --json \
  | jq '.runs[] | select(startswith("train"))'
```

### LLM Agent Discovery Workflow

```bash
trackio list projects --json           # 1. Discover projects
trackio get project --project X --json # 2. Inspect project
trackio get run --project X --run Y --json   # 3. Inspect run
trackio get metric --project X --run Y --metric loss --json  # 4. Query metric
```

## Error Handling

Commands validate inputs and return clear errors to stderr:

- `Error: Project '<name>' not found.`
- `Error: Run '<name>' not found in project '<project>'.`
- `Error: Metric '<name>' not found in run '<run>' of project '<project>'.`

All errors exit with non-zero status code.
