# PromQL Query Reference

Common Prometheus queries for Platxa monitoring.

## Instance Metrics

### Memory Usage

```promql
# Current memory (bytes)
container_memory_working_set_bytes{
  namespace="instance-{name}",
  pod=~"odoo-{name}.*",
  container="odoo"
}

# Memory usage ratio (using recording rule)
instance:memory_usage:ratio{namespace="instance-{name}"}

# Memory over time (range query)
avg_over_time(
  container_memory_working_set_bytes{namespace="instance-{name}"}[1h]
)
```

### CPU Usage

```promql
# CPU rate (cores)
sum(rate(container_cpu_usage_seconds_total{
  namespace="instance-{name}",
  container="odoo"
}[5m]))

# CPU in millicores (using recording rule)
instance:cpu_usage:millicores{namespace="instance-{name}"}

# CPU throttling
rate(container_cpu_cfs_throttled_seconds_total{
  namespace="instance-{name}"
}[5m])
```

### Storage Usage

```promql
# PVC used bytes
kubelet_volume_stats_used_bytes{
  namespace="instance-{name}",
  persistentvolumeclaim=~"odoo-{name}-.*"
}

# Storage ratio (using recording rule)
instance:storage_usage:ratio{namespace="instance-{name}"}

# Storage by type
kubelet_volume_stats_used_bytes{
  namespace="instance-{name}",
  persistentvolumeclaim="odoo-{name}-filestore"
}
```

### Network Traffic

```promql
# Request rate (from ingress)
sum(rate(nginx_ingress_controller_requests{
  namespace="instance-{name}"
}[5m]))

# Bytes received
sum(rate(container_network_receive_bytes_total{
  namespace="instance-{name}"
}[5m]))
```

### Pod Restarts

```promql
# Restart count (1 hour, using recording rule)
instance:restarts:1h{namespace="instance-{name}"}

# OOM kills
increase(kube_pod_container_status_restarts_total{
  namespace="instance-{name}",
  reason="OOMKilled"
}[24h])
```

## PostgreSQL Metrics

### Database Size

```promql
# Size per database
pg_database_size{datname=~"instance_.*"}

# Total instance databases size
sum(pg_database_size{datname=~"instance_.*"})
```

### Connections

```promql
# Active connections by database
sum by (datname) (pg_stat_activity_count{state="active"})

# Idle connections
sum by (datname) (pg_stat_activity_count{state="idle"})

# Total connections
sum(pg_stat_activity_count)

# Using recording rule
postgresql:connections:by_database
```

### Slow Queries

```promql
# Queries running >30 seconds
pg_slow_queries_count

# Per database
pg_slow_queries_count{datname="instance_{name}"}
```

## Waking Service Metrics

```promql
# Instance states
waking_instances_by_state{state="running"}
waking_instances_by_state{state="sleeping"}
waking_instances_by_state{state="waking"}
waking_instances_by_state{state="error"}

# Total instances
waking_instances_total

# Total hosts
waking_hosts_total
```

## Infrastructure Metrics

### Traefik

```promql
# Request rate
sum(rate(traefik_entrypoint_requests_total[5m]))

# Error rate (4xx, 5xx)
sum(rate(traefik_entrypoint_requests_total{code=~"4..|5.."}[5m]))

# Request duration (95th percentile)
histogram_quantile(0.95,
  sum(rate(traefik_entrypoint_request_duration_seconds_bucket[5m])) by (le)
)
```

### cert-manager

```promql
# Certificates expiring soon
certmanager_certificate_expiration_timestamp_seconds - time()

# Ready certificates
certmanager_certificate_ready_status{condition="True"}
```

## Aggregation Patterns

### Sum by Label

```promql
# Memory by namespace
sum by (namespace) (container_memory_working_set_bytes{namespace=~"instance-.*"})
```

### Rate and Increase

```promql
# Rate (per second average)
rate(metric[5m])

# Increase (total change)
increase(metric[1h])
```

### Top K

```promql
# Top 10 memory consumers
topk(10, container_memory_working_set_bytes{namespace=~"instance-.*"})
```

### Histogram Quantiles

```promql
# 95th percentile
histogram_quantile(0.95, sum(rate(metric_bucket[5m])) by (le))
```

## Query Tips

| Tip | Example |
|-----|---------|
| Use recording rules | `instance:memory_usage:ratio` instead of raw query |
| Narrow scope first | Add namespace filter before other labels |
| Use appropriate rate | `[5m]` for graphs, `[1m]` for alerts |
| Avoid regex when possible | Exact match is faster |
