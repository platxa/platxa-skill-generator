# LogQL Query Reference

Common Loki queries for Platxa log analysis.

## Label Filtering

### Basic Selectors

```logql
# Single namespace
{namespace="instance-abc123xy"}

# Specific container
{namespace="instance-abc123xy", container="odoo"}

# Multiple values (OR)
{namespace=~"instance-abc123xy|instance-demo"}

# Regex pattern
{namespace=~"instance-.*"}

# Exclude pattern
{namespace!~"monitoring|kube-system"}
```

### Common Label Combinations

```logql
# Odoo application logs
{namespace=~"instance-.*", container="odoo", app="odoo"}

# Waking service logs
{namespace="traefik-system", container="waking-service"}

# Infrastructure logs
{namespace="monitoring", app=~"prometheus|loki|grafana"}

# PostgreSQL logs
{namespace="postgres-system"}
```

## Line Filters

### Contains (Case Sensitive)

```logql
# Exact substring
{namespace="instance-demo"} |= "ERROR"

# Multiple patterns (AND)
{namespace="instance-demo"} |= "ERROR" |= "database"
```

### Contains (Case Insensitive)

```logql
{namespace="instance-demo"} |~ "(?i)error"
```

### Regex Match

```logql
# Match pattern
{namespace="instance-demo"} |~ "connection refused|timeout"

# Exclude pattern
{namespace="instance-demo"} != "healthcheck"
{namespace="instance-demo"} !~ "DEBUG|TRACE"
```

## Parsers

### JSON Parser

```logql
# Parse JSON log
{namespace="traefik-system"} | json

# Extract specific fields
{namespace="traefik-system"} | json | status >= 500

# Line format after parsing
{namespace="traefik-system"} | json | line_format "{{.method}} {{.path}} {{.status}}"
```

### Logfmt Parser

```logql
{app="waking-service"} | logfmt | level="error"
```

### Pattern Parser

```logql
# Extract from unstructured logs
{namespace="instance-demo"} | pattern "<timestamp> <level> <message>"
```

## Aggregations

### Count Over Time

```logql
# Error count in time window
count_over_time({namespace="instance-demo"} |~ "ERROR" [5m])

# Per namespace
sum by (namespace) (count_over_time({namespace=~"instance-.*"} |~ "ERROR" [5m]))
```

### Rate

```logql
# Errors per second
rate({namespace="instance-demo"} |~ "ERROR" [1m])

# Log volume per namespace
sum by (namespace) (rate({namespace=~"instance-.*"} [5m]))
```

### Top K

```logql
# Top 10 namespaces by error count
topk(10, sum by (namespace) (count_over_time({namespace=~"instance-.*"} |~ "ERROR" [1h])))
```

### Bytes Over Time

```logql
# Log volume in bytes
bytes_over_time({namespace="instance-demo"} [1h])
```

## Common Search Patterns

### Error Detection

```logql
# Python errors
{namespace=~"instance-.*"} |~ "ERROR|Exception|Traceback"

# Database errors
{namespace=~"instance-.*"} |~ "could not connect|connection refused|FATAL.*database"

# OOM errors
{namespace=~"instance-.*"} |~ "OOM|killed|Cannot allocate memory"
```

### Performance Issues

```logql
# Slow queries (Odoo)
{namespace=~"instance-.*"} |~ "query.*took.*seconds"

# Timeout errors
{namespace=~"instance-.*"} |~ "timeout|timed out"
```

### Authentication Issues

```logql
# Login failures
{namespace=~"instance-.*"} |~ "authentication failed|invalid password|access denied"

# Token errors
{namespace=~"instance-.*"} |~ "token.*expired|invalid token"
```

### Startup/Shutdown

```logql
# Startup messages
{namespace=~"instance-.*"} |~ "starting|started|initialized"

# Shutdown messages
{namespace=~"instance-.*"} |~ "shutdown|stopping|terminated"
```

## Time Range Examples

```logql
# Last 5 minutes
{namespace="instance-demo"} |~ "ERROR"

# Specific time range (in Grafana Explore)
# Set time picker to custom range

# With offset (useful in alerts)
count_over_time({namespace="instance-demo"} |~ "ERROR" [5m] offset 5m)
```

## Query Tips

| Tip | Description |
|-----|-------------|
| Labels first | Always filter by labels before line filters |
| Narrow time | Smaller time ranges are faster |
| Avoid `.*` | Use specific patterns when possible |
| Use index | Namespace and app labels are indexed |
| Limit results | Add `| limit 1000` for large queries |

## Performance Guidelines

```logql
# Good: Specific labels, exact match
{namespace="instance-demo", container="odoo"} |= "ERROR"

# Bad: Broad regex, complex pattern
{namespace=~".*"} |~ ".*error.*"

# Good: Label aggregation
sum by (namespace) (rate({namespace=~"instance-.*"} [5m]))

# Bad: High cardinality extraction
{namespace=~"instance-.*"} | json | by (request_id)
```
