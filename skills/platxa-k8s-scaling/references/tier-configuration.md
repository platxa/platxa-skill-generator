# Tier Configuration Reference

Per-plan resource and scaling settings for Platxa instances.

## Plan Comparison

| Setting | FREE | PRO | TEAM | ENTERPRISE |
|---------|------|-----|------|------------|
| **Scaling** |
| Min Replicas | 0 | 0 | 0 | 1 |
| Max Replicas | 1 | 1 | 1 | 3 |
| Scaling Mode | auto | auto | auto | always-on |
| Idle Timeout | 10 min | 20 min | 30 min | N/A |
| **Memory** |
| Request | 256Mi | 512Mi | 1Gi | 2Gi |
| Limit | 1Gi | 2Gi | 4Gi | 8Gi |
| **CPU** |
| Request | 50m | 100m | 200m | 500m |
| Limit | 500m | 1000m | 2000m | 4000m |
| **Storage** |
| Addons | 256Mi | 512Mi | 1Gi | 2Gi |
| Filestore | 512Mi | 1Gi | 2Gi | 5Gi |
| Database | 1Gi | 2Gi | 5Gi | 20Gi |

## Instance Configuration Model

```python
class Instance(models.Model):
    # Scaling
    min_replicas = fields.Integer(default=0)
    max_replicas = fields.Integer(default=1)
    idle_timeout_minutes = fields.Integer(default=15)
    scaling_mode = fields.Selection([
        ('auto', 'Auto (Scale to Zero)'),
        ('always_on', 'Always On'),
    ], default='auto')

    # Resources
    memory_request = fields.Char(default='512Mi')
    memory_limit = fields.Char(default='1Gi')
    cpu_request = fields.Char(default='100m')
    cpu_limit = fields.Char(default='1000m')

    # Storage
    addons_storage = fields.Char(default='256Mi')
    filestore_storage = fields.Char(default='512Mi')
    database_storage = fields.Char(default='1Gi')
```

## Deployment Template

```yaml
spec:
  replicas: {{ min_replicas }}
  template:
    spec:
      containers:
        - name: odoo
          resources:
            requests:
              memory: "{{ memory_request }}"
              cpu: "{{ cpu_request }}"
            limits:
              memory: "{{ memory_limit }}"
              cpu: "{{ cpu_limit }}"
```

## QoS Classes

All tiers use **Burstable** QoS:
- Requests < Limits
- Allows burst capacity
- Lower priority than Guaranteed

For Guaranteed QoS (requests = limits):
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"   # Same as request
    cpu: "500m"     # Same as request
```

## Waking Service Configuration

```yaml
# ConfigMap settings per tier
IDLE_TIMEOUT_FREE: "600s"      # 10 min
IDLE_TIMEOUT_PRO: "1200s"      # 20 min
IDLE_TIMEOUT_TEAM: "1800s"     # 30 min
IDLE_TIMEOUT_ENTERPRISE: "0"   # Never (always-on)
```

## Upgrade Paths

| From | To | Changes |
|------|----|---------|
| FREE → PRO | Memory: 256→512Mi, CPU: 50→100m, Idle: 10→20min |
| PRO → TEAM | Memory: 512Mi→1Gi, CPU: 100→200m, Idle: 20→30min |
| TEAM → ENT | Memory: 1→2Gi, CPU: 200→500m, Mode: auto→always-on |

## Node Pool Assignment

| Plan | Node Pool | Node Size |
|------|-----------|-----------|
| FREE | instance-pool | s-2vcpu-4gb |
| PRO | instance-pool | s-2vcpu-4gb |
| TEAM | instance-pool | s-4vcpu-8gb |
| ENTERPRISE | dedicated-pool | s-8vcpu-16gb |
