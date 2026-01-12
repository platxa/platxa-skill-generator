---
name: platxa-monitoring
description: Observability guide for Platxa platform using Prometheus metrics and Loki logs. Query metrics, analyze logs, configure alerts, and troubleshoot issues.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - monitoring
    - prometheus
    - loki
    - observability
---

# Platxa Monitoring

Guide for observability in the Platxa platform using Prometheus metrics and Loki logs.

## Overview

This skill covers the complete observability stack:

| Component | Purpose | Access |
|-----------|---------|--------|
| **Prometheus** | Metrics collection and alerting | Port 9090 |
| **Loki** | Log aggregation and querying | Port 3100 |
| **Grafana** | Visualization dashboards | Port 3000 |
| **Alertmanager** | Alert routing and notification | Port 9093 |
| **Fluent Bit** | Log collection from pods | DaemonSet |

## Prerequisites

Verify monitoring stack is running:

```bash
kubectl get pods -n monitoring
# prometheus-*, loki-*, grafana-*, fluent-bit-*

# Access Grafana locally
kubectl port-forward svc/grafana 3000:80 -n monitoring
```

## Prometheus Metrics

### Common PromQL Queries

#### Instance Resource Metrics

```promql
# Memory usage (bytes)
container_memory_working_set_bytes{
  namespace="instance-{name}",
  container="odoo"
}

# CPU usage (millicores)
sum(rate(container_cpu_usage_seconds_total{
  namespace="instance-{name}",
  container="odoo"
}[5m])) * 1000

# Storage usage (ratio)
kubelet_volume_stats_used_bytes{namespace="instance-{name}"}
/
kubelet_volume_stats_capacity_bytes{namespace="instance-{name}"}
```

#### Waking Service Metrics

```promql
# Instance state distribution
waking_instances_by_state{state="running"}
waking_instances_by_state{state="sleeping"}
waking_instances_by_state{state="waking"}
waking_instances_by_state{state="error"}

# Total tracked instances
waking_instances_total
```

#### PostgreSQL Metrics

```promql
# Database size
pg_database_size{datname=~"instance_.*"}

# Active connections per database
sum by (datname) (pg_stat_activity_count{state="active"})

# Slow queries (>30s)
pg_slow_queries_count
```

### Recording Rules

Pre-computed metrics for dashboard efficiency:

| Recording Rule | Description |
|----------------|-------------|
| `instance:memory_usage:ratio` | Memory usage percentage |
| `instance:cpu_usage:millicores` | CPU in millicores |
| `instance:storage_usage:ratio` | Storage percentage |
| `instance:restarts:1h` | Restart count (1 hour) |
| `postgresql:connections:by_database` | Connections per DB |

### ServiceMonitors

Automatic scrape targets via Prometheus Operator:

| Target | Namespace | Port | Interval |
|--------|-----------|------|----------|
| postgres-exporter | postgres-system | 9187 | 30s |
| traefik | traefik-system | 8082 | 30s |
| waking-service | traefik-system | 9100 | 30s |
| loki | monitoring | 3100 | 30s |
| cert-manager | cert-manager | 9402 | 60s |

## Loki Logs

### LogQL Query Patterns

#### Basic Label Filtering

```logql
# All logs from an instance
{namespace="instance-abc123xy"}

# Specific container
{namespace="instance-abc123xy", container="odoo"}

# Multiple namespaces (regex)
{namespace=~"instance-.*"}
```

#### Pattern Matching

```logql
# Contains error (case insensitive)
{namespace=~"instance-.*"} |~ "(?i)error"

# Exact match
{namespace=~"instance-.*"} |= "FATAL"

# Exclude pattern
{namespace=~"instance-.*"} != "healthcheck"

# Regex pattern
{namespace=~"instance-.*"} |~ "connection refused|timeout"
```

#### Aggregations

```logql
# Error count over time
count_over_time({namespace="instance-abc123xy"} |~ "ERROR" [5m])

# Error rate per minute
rate({namespace=~"instance-.*"} |~ "ERROR" [1m])

# Top namespaces by log volume
topk(10, sum by (namespace) (rate({namespace=~"instance-.*"}[5m])))
```

### Log Labels

Fluent Bit enriches logs with Kubernetes metadata:

| Label | Source | Example |
|-------|--------|---------|
| `namespace` | Pod namespace | `instance-abc123xy` |
| `container` | Container name | `odoo` |
| `pod` | Pod name | `odoo-abc123xy-7f8b9c` |
| `app` | Pod label | `odoo` |
| `job` | Static label | `fluentbit` |

### Multiline Log Handling

Python stack traces are automatically combined:

```
# Fluent Bit parser detects:
# - "Traceback (most recent call last):"
# - Indented continuation lines
# - "Error:", "Exception:", "Warning:"
```

## Alerting

### Alert Categories

#### Infrastructure Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| PostgreSQLDown | Target unreachable | critical |
| TraefikDown | Target unreachable | critical |
| WakingServiceDown | Target unreachable | critical |
| CertificateExpiringSoon | <14 days | warning |
| CertificateExpiringCritical | <3 days | critical |

#### Instance Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| OdooStorageHigh | >90% used | warning |
| OdooStorageCritical | >95% used | critical |
| OdooHighMemory | >85% used | warning |
| OdooOOMKilled | Container killed | critical |
| OdooPodRestartLoop | >3 restarts/hour | warning |
| OdooWakeFailed | Scale-up failed | critical |

#### Database Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| PostgreSQLHighConnections | >20 active per DB | warning |
| PostgreSQLTotalConnectionsCritical | >150 total | critical |
| PostgreSQLSlowQueries | >3 queries >30s | warning |

#### Log-Based Alerts (Loki)

| Alert | LogQL Pattern | Severity |
|-------|---------------|----------|
| OdooDBConnectionError | DB connection errors | critical |
| OdooHighErrorRate | >50 errors in 5m | warning |

### Alertmanager Routing

```yaml
Routes:
  critical → platform-odoo (webhook, 10s group wait)
  warning  → platform-odoo (30s group wait)
  null     → silence (Watchdog, informational)

Webhook: Bearer token auth to Odoo platform
Grouping: By namespace and alertname
```

## Workflow

### Investigating Issues

#### Step 1: Identify Issue Type

| Symptom | Primary Tool | Secondary |
|---------|--------------|-----------|
| Slow response | Prometheus | Loki |
| Crashes/restarts | Loki | Prometheus |
| Out of memory | Prometheus | Loki |
| Connection errors | Loki | Prometheus |
| High resource usage | Prometheus | - |

#### Step 2: Scope to Target

```bash
# Find instance namespace
kubectl get ns -l platxa.io/tier=instance | grep {name}

# Identify components
kubectl get pods -n instance-{name}
```

#### Step 3: Query Data

**Prometheus (via Grafana or API):**
```bash
# API query
curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=instance:memory_usage:ratio{namespace="instance-abc123xy"}'
```

**Loki (via Grafana or API):**
```bash
# API query
curl -G 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query={namespace="instance-abc123xy"} |~ "ERROR"'
```

#### Step 4: Correlate

- Match metric spikes with log timestamps
- Check alert history in Alertmanager
- Review recent events: `kubectl get events -n instance-{name}`

#### Step 5: Recommend Actions

- Use `platxa-k8s-ops` for operational commands
- Suggest resource adjustments
- Link to relevant troubleshooting guides

## Examples

### Example 1: Memory Investigation

**User**: "Instance abc123xy is running slow"

**Response**:

Check memory usage:
```promql
instance:memory_usage:ratio{namespace="instance-abc123xy"}
# Result: 0.92 (92% of limit)
```

Check for OOM events:
```logql
{namespace="instance-abc123xy"} |~ "OOM|killed|memory"
```

Recent restarts:
```promql
instance:restarts:1h{namespace="instance-abc123xy"}
# Result: 2 restarts
```

**Finding**: Memory pressure causing slowdown. Recommend increasing memory limit or reducing Odoo workers.

### Example 2: Error Log Analysis

**User**: "Users report 500 errors on demo instance"

**Response**:

Search recent errors:
```logql
{namespace="instance-demo", container="odoo"}
  |~ "ERROR|Exception|Traceback"
  | json
  | line_format "{{.message}}"
```

Count errors by type:
```logql
sum by (level) (
  count_over_time({namespace="instance-demo"} |~ "ERROR|WARNING" [1h])
)
```

Check database connectivity:
```logql
{namespace="instance-demo"} |~ "could not connect|connection refused"
```

**Finding**: Database connection errors detected. Check PostgreSQL status with `platxa-k8s-ops`.

### Example 3: Alert Investigation

**User**: "Got alert for OdooStorageCritical"

**Response**:

Check current storage usage:
```promql
instance:storage_usage:ratio{namespace=~"instance-.*"} > 0.90
```

Identify which PVC is full:
```promql
kubelet_volume_stats_used_bytes{namespace="instance-{name}"}
/
kubelet_volume_stats_capacity_bytes{namespace="instance-{name}"}
```

Results:
- `odoo-{name}-addons`: 45% used
- `odoo-{name}-filestore`: 97% used (CRITICAL)

**Finding**: Filestore PVC near capacity. Options:
1. Clean up old attachments
2. Expand PVC (if storage class supports)
3. Upgrade instance tier for larger storage

### Example 4: Cold Start Performance

**User**: "Instances taking too long to wake"

**Response**:

Check waking service metrics:
```promql
# Current instance states
waking_instances_by_state

# Cold start timing (if exposed)
histogram_quantile(0.95, waking_cold_start_duration_bucket)
```

Check waking service logs:
```logql
{namespace="traefik-system", container="waking-service"}
  |~ "cold start|wake|scale"
  | json
```

Common causes:
- Large filestore extraction time
- Resource scheduling delays
- Init container timeouts

## Grafana Dashboards

Pre-built dashboards available:

| Dashboard | Purpose |
|-----------|---------|
| Cluster Overview | Node and resource summary |
| Instances Overview | All instances at a glance |
| Instance Detail | Single instance deep dive |
| Postgres System | Database metrics |
| Edge Overview | Traefik and ingress |
| Scale-to-Zero | Wake/sleep patterns |
| Monitoring Health | Stack self-monitoring |
| Instance Status | Embeddable status widget |

Access: Grafana → Dashboards → Browse

## Troubleshooting

### No Metrics Data

| Symptom | Cause | Fix |
|---------|-------|-----|
| Target down | Pod not running | Check pod status |
| No ServiceMonitor | Missing CRD | Apply ServiceMonitor |
| Wrong labels | Selector mismatch | Check `release: prometheus` label |

### No Logs in Loki

| Symptom | Cause | Fix |
|---------|-------|-----|
| Empty results | Wrong namespace | Verify label values |
| Missing logs | Fluent Bit down | Check DaemonSet |
| Delayed logs | Ingestion backlog | Check Loki metrics |

### Alerts Not Firing

| Symptom | Cause | Fix |
|---------|-------|-----|
| No alerts | Rule not loaded | Check PrometheusRule CRD |
| Not routing | Wrong labels | Verify severity label |
| Not received | Webhook error | Check Alertmanager logs |

## Output Checklist

After monitoring investigation:

- [ ] Relevant PromQL/LogQL query constructed
- [ ] Time range appropriate for issue
- [ ] Results interpreted correctly
- [ ] Metrics and logs correlated
- [ ] Root cause identified or narrowed
- [ ] Actionable recommendations provided
- [ ] Follow-up monitoring suggested

## Related Resources

- **PromQL Queries**: See `references/promql-queries.md`
- **LogQL Queries**: See `references/logql-queries.md`
- **Alert Rules**: See `references/alert-rules.md`
- **K8s Operations**: Use `platxa-k8s-ops` skill
