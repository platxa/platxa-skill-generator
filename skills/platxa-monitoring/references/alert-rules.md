# Alert Rules Reference

Prometheus and Loki alert configurations for Platxa.

## Infrastructure Alerts

### PostgreSQL Down

```yaml
alert: PostgreSQLDown
expr: |
  up{job="postgres-exporter"} == 0
  or
  absent(up{job="postgres-exporter"})
for: 1m
labels:
  severity: critical
  type: infrastructure
annotations:
  summary: "PostgreSQL exporter is down"
  description: "Database monitoring unavailable"
```

### Traefik Down

```yaml
alert: TraefikDown
expr: up{job="traefik"} == 0 or absent(up{job="traefik"})
for: 1m
labels:
  severity: critical
  type: infrastructure
```

### Waking Service Down

```yaml
alert: WakingServiceDown
expr: up{job="waking-service"} == 0 or absent(up{job="waking-service"})
for: 1m
labels:
  severity: critical
  type: infrastructure
```

### Certificate Expiry

```yaml
alert: CertificateExpiringSoon
expr: certmanager_certificate_expiration_timestamp_seconds - time() < 86400 * 14
for: 1h
labels:
  severity: warning
  type: infrastructure

alert: CertificateExpiringCritical
expr: certmanager_certificate_expiration_timestamp_seconds - time() < 86400 * 3
for: 10m
labels:
  severity: critical
  type: infrastructure
```

## Instance Alerts

### Storage Alerts

```yaml
alert: OdooStorageHigh
expr: instance:storage_usage:ratio > 0.90
for: 5m
labels:
  severity: warning
  type: storage

alert: OdooStorageCritical
expr: instance:storage_usage:ratio > 0.95
for: 2m
labels:
  severity: critical
  type: storage
```

### Memory Alerts

```yaml
alert: OdooHighMemory
expr: instance:memory_usage:ratio > 0.85
for: 5m
labels:
  severity: warning
  type: resource
```

### OOM Kill Alert

```yaml
alert: OdooOOMKilled
expr: |
  increase(kube_pod_container_status_restarts_total{
    namespace=~"instance-.*",
    container="odoo"
  }[5m]) > 0
  and on(namespace, pod, container)
  kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
for: 0m
labels:
  severity: critical
  type: resource
annotations:
  summary: "Odoo container killed by OOM"
  runbook: "Increase memory limit or reduce workers"
```

### Restart Loop Alert

```yaml
alert: OdooPodRestartLoop
expr: |
  increase(kube_pod_container_status_restarts_total{
    namespace=~"instance-.*",
    container="odoo"
  }[1h]) > 3
for: 5m
labels:
  severity: warning
  type: availability
```

### Wake Failed Alert

```yaml
alert: OdooWakeFailed
expr: |
  kube_deployment_status_replicas_ready{
    namespace=~"instance-.*",
    deployment=~"odoo-.*"
  } == 0
  and
  kube_deployment_spec_replicas{
    namespace=~"instance-.*",
    deployment=~"odoo-.*"
  } > 0
for: 5m
labels:
  severity: critical
  type: availability
```

## Database Alerts

### High Connections

```yaml
alert: PostgreSQLHighConnections
expr: sum by (datname) (pg_stat_activity_count{state="active"}) > 20
for: 5m
labels:
  severity: warning
  type: database

alert: PostgreSQLTotalConnectionsCritical
expr: sum(pg_stat_activity_count) > 150
for: 2m
labels:
  severity: critical
  type: database
```

### Slow Queries

```yaml
alert: PostgreSQLSlowQueries
expr: pg_slow_queries_count > 3
for: 5m
labels:
  severity: warning
  type: database
```

## Log-Based Alerts (Loki)

### Database Connection Error

```yaml
alert: OdooDBConnectionError
expr: |
  count_over_time(
    {namespace=~"instance-.*"}
    |~ "could not connect to server|connection refused|FATAL.*database"
    [5m]
  ) > 0
for: 1m
labels:
  severity: critical
  type: database
```

### High Error Rate

```yaml
alert: OdooHighErrorRate
expr: |
  sum by (namespace) (
    count_over_time({namespace=~"instance-.*"} |~ "ERROR|Error" [5m])
  ) > 50
for: 2m
labels:
  severity: warning
  type: application
```

## Alertmanager Routing

### Route Configuration

```yaml
route:
  receiver: 'platform-odoo'
  group_by: ['namespace', 'alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers:
        - severity = critical
      receiver: 'platform-odoo'
      group_wait: 10s
      repeat_interval: 1h
    - matchers:
        - alertname = Watchdog
      receiver: 'null'
```

### Webhook Receiver

```yaml
receivers:
  - name: 'platform-odoo'
    webhook_configs:
      - url_file: /etc/alertmanager/secrets/webhook-url
        bearer_token_file: /etc/alertmanager/secrets/webhook-token
        max_alerts: 100
        send_resolved: true
  - name: 'null'
```

## Severity Levels

| Severity | Response Time | Examples |
|----------|--------------|----------|
| critical | Immediate | Service down, OOM kill, cert expiring <3d |
| warning | Within hours | High resource usage, restart loop |
| info | Daily review | Watchdog, informational |

## Creating Custom Alerts

### PrometheusRule Template

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: custom-alerts
  namespace: monitoring
  labels:
    release: prometheus  # Required for discovery
spec:
  groups:
    - name: custom.rules
      rules:
        - alert: MyCustomAlert
          expr: <promql_expression>
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Alert description"
```

### Required Labels

| Label | Purpose |
|-------|---------|
| `severity` | Routing (critical, warning, info) |
| `type` | Category (infrastructure, resource, database) |
| `namespace` | From expr, for grouping |

## Silencing Alerts

```bash
# Via Alertmanager API
curl -X POST http://alertmanager:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "namespace", "value": "instance-demo"}],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T02:00:00Z",
    "comment": "Maintenance window"
  }'
```
