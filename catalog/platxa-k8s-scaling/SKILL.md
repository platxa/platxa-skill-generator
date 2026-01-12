---
name: platxa-k8s-scaling
description: Kubernetes scaling patterns for Platxa platform. Configure scale-to-zero with waking-service, HPA autoscaling, and per-instance resource management.
allowed-tools:
  - Read
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - kubernetes
    - scaling
    - hpa
    - scale-to-zero
---

# Platxa Kubernetes Scaling

Guide for implementing scale-to-zero and HPA autoscaling patterns in the Platxa platform.

## Overview

This skill covers Kubernetes scaling strategies for Platxa:

| Component | What You Can Configure |
|-----------|----------------------|
| **Scale-to-Zero** | Idle timeout, wake behavior, activity tracking |
| **HPA Autoscaling** | CPU/Memory targets, behavior policies, stabilization |
| **Instance Tiers** | Resource limits, scaling mode, plan-specific settings |
| **Waking Service** | Proxy configuration, rate limiting, error handling |

## Workflow

When configuring Kubernetes scaling, follow this workflow:

### Step 1: Understand Instance State

Check the current state of instances:
- **Sleeping**: replicas=0, no running pod
- **Waking**: replicas>0, pod starting
- **Running**: pod ready, receiving traffic
- **Error**: pod failed (CrashLoop, OOM, etc.)

### Step 2: Configure Scaling Mode

Choose scaling mode based on requirements:
- **Auto (scale-to-zero)**: `min_replicas=0`, idle timeout applies
- **Always-On**: `min_replicas=1+`, no scale-to-zero

### Step 3: Set HPA for Infrastructure

Configure HPA for waking-service (not per-instance):
- Define CPU/Memory targets
- Set min/max replicas
- Configure behavior policies

### Step 4: Monitor and Tune

Adjust based on observations:
- Tune idle timeouts per tier
- Adjust stabilization windows
- Monitor cold start times

## Scale-to-Zero Architecture

### Request Flow

```
User Request → Traefik Ingress → Waking-Service
                                       │
                               [Check State]
                                       │
         ┌──────────┬──────────┬───────┴───────┐
         ↓          ↓          ↓               ↓
      RUNNING    SLEEPING    WAKING         ERROR
      (proxy)   (scale up)  (hold/wait)  (error page)
```

### Instance States

| State | Replicas | Pod Status | Waking-Service Action |
|-------|----------|------------|----------------------|
| Sleeping | 0 | None | Scale up, serve waking page |
| Waking | >0 | Starting | Hold XHR, wait for ready |
| Running | >0 | Ready | Proxy directly to pod |
| Error | >0 | Failed | Show error page |
| Suspended | 0 | N/A | Return 503 |
| Disabled | 0 | N/A | Return 503 |

### Request Classification

| Request Type | Wakes Instance | Updates Activity |
|--------------|---------------|------------------|
| PageLoad | Yes | Yes |
| XHR (API calls) | Yes | Yes |
| Longpolling | No | No |
| WebSocket | No (503) | No |
| Static assets | No | No |

## HPA Configuration

### Basic HPA (autoscaling/v2)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: waking-service
  namespace: traefik-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: waking-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Asymmetric Scaling Behavior

```yaml
behavior:
  # Scale UP quickly (minimize latency)
  scaleUp:
    stabilizationWindowSeconds: 30
    policies:
      - type: Pods
        value: 2
        periodSeconds: 60
      - type: Percent
        value: 100
        periodSeconds: 60
    selectPolicy: Max

  # Scale DOWN slowly (avoid flapping)
  scaleDown:
    stabilizationWindowSeconds: 300
    policies:
      - type: Pods
        value: 1
        periodSeconds: 120
    selectPolicy: Min
```

### PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: waking-service
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: waking-service
```

## Configuration Presets

### Development (Kind)

HPA disabled for single-node local development:

```yaml
# Deployment
spec:
  replicas: 1

# HPA: Not applied
# PDB: Not applied
```

### Production Base

Standard multi-replica with HPA:

```yaml
# HPA
minReplicas: 2
maxReplicas: 10
metrics:
  - cpu: 70%
  - memory: 80%
behavior:
  scaleUp:
    stabilizationWindowSeconds: 30
  scaleDown:
    stabilizationWindowSeconds: 300
```

### Production DOKS

More conservative for DigitalOcean:

```yaml
# HPA
minReplicas: 2
maxReplicas: 5  # Lower ceiling
metrics:
  - cpu: 70%    # CPU only
behavior:
  scaleUp:
    stabilizationWindowSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 300
```

## Instance Tier Configuration

### Scaling by Plan

| Plan | Min Replicas | Max Replicas | Idle Timeout | Scaling Mode |
|------|-------------|-------------|--------------|--------------|
| FREE | 0 | 1 | 10 min | auto |
| PRO | 0 | 1 | 20 min | auto |
| TEAM | 0 | 1 | 30 min | auto |
| ENTERPRISE | 1 | 3 | N/A | always-on |

### Resources by Plan

| Plan | Memory Request | Memory Limit | CPU Request | CPU Limit |
|------|---------------|--------------|-------------|-----------|
| FREE | 256Mi | 1Gi | 50m | 500m |
| PRO | 512Mi | 2Gi | 100m | 1000m |
| TEAM | 1Gi | 4Gi | 200m | 2000m |
| ENTERPRISE | 2Gi | 8Gi | 500m | 4000m |

### Instance Configuration

```python
# Odoo model fields (instance_instance.py)
min_replicas = 0      # 0 for scale-to-zero
max_replicas = 1      # Plan-dependent
idle_timeout_minutes = 15
scaling_mode = 'auto'  # or 'always_on'

# Resources
memory_request = '512Mi'
memory_limit = '1Gi'
cpu_request = '100m'
cpu_limit = '1000m'
```

## Examples

### Example 1: Scale-to-Zero Instance

**User**: "Configure scale-to-zero for a FREE tier instance"

**Response**:

Instance configuration:
```python
# In Odoo instance model
instance.min_replicas = 0
instance.max_replicas = 1
instance.idle_timeout_minutes = 10
instance.scaling_mode = 'auto'
instance.memory_request = '256Mi'
instance.memory_limit = '1Gi'
```

Generated deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo-abc123xy
  namespace: instance-abc123xy
spec:
  replicas: 0  # Scale-to-zero: starts at 0
  template:
    spec:
      containers:
        - name: odoo
          resources:
            requests:
              memory: "256Mi"
              cpu: "50m"
            limits:
              memory: "1Gi"
              cpu: "500m"
```

### Example 2: HPA for Production Waking-Service

**User**: "Configure HPA for waking-service in production"

**Response**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: waking-service
  namespace: traefik-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: waking-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
      selectPolicy: Min
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: waking-service
  namespace: traefik-system
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: waking-service
```

### Example 3: Always-On Enterprise Instance

**User**: "Configure always-on for enterprise customer"

**Response**:

Instance configuration:
```python
instance.min_replicas = 1    # Always-on: never scale to zero
instance.max_replicas = 3    # Allow horizontal scaling
instance.scaling_mode = 'always_on'
instance.memory_request = '2Gi'
instance.memory_limit = '8Gi'
instance.cpu_request = '500m'
instance.cpu_limit = '4000m'
```

Generated deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo-enterprise01
  namespace: instance-enterprise01
spec:
  replicas: 1  # Always-on: starts at 1
  template:
    spec:
      containers:
        - name: odoo
          resources:
            requests:
              memory: "2Gi"
              cpu: "500m"
            limits:
              memory: "8Gi"
              cpu: "4000m"
```

## Best Practices

### Scaling Behavior

| Practice | Recommendation |
|----------|---------------|
| Scale-up stabilization | 30-60 seconds (minimize latency) |
| Scale-down stabilization | 300+ seconds (avoid flapping) |
| CPU target | 70% (headroom for spikes) |
| Memory target | 80% (avoid OOM) |
| Min replicas (infra) | 2+ for HA |

### Activity Tracking

| Practice | Recommendation |
|----------|---------------|
| Exclude longpolling | Prevents false activity |
| Exclude WebSocket | Return 503 with Retry-After |
| Track PageLoad/XHR | Real user activity |
| Idle check interval | 60 seconds |

### Rate Limiting

| Practice | Recommendation |
|----------|---------------|
| Per-instance | 10 wake attempts/hour |
| Per-IP | 100 requests/hour |
| Global | 1000 requests/minute |

## Troubleshooting

### Instance Not Waking

**Symptom**: 504 Gateway Timeout when accessing sleeping instance

**Causes & Fixes**:
- **Pod startup failure**: Check `kubectl describe pod` for events
- **Resource limits too low**: Increase memory/CPU limits
- **Image pull failure**: Verify image exists and credentials
- **Init container timeout**: Check filestore extraction

### Excessive Scale Events (Flapping)

**Symptom**: Constant scale up/down in HPA logs

**Causes & Fixes**:
- **Short stabilization window**: Increase to 300s+
- **Borderline utilization**: Adjust target percentage
- **Memory pressure**: Add memory metric or increase limits

### Cold Start Too Slow

**Symptom**: Users wait >2 minutes for instance wake

**Causes & Fixes**:
- **Large filestore**: Optimize compression, reduce size
- **Slow init container**: Profile init duration
- **Aggressive probes**: Increase initialDelaySeconds
- **Resource starvation**: Check node resources

### HPA Not Scaling

**Symptom**: High CPU but no scale-up

**Causes & Fixes**:
- **Missing metrics-server**: Install metrics-server
- **maxReplicas reached**: Increase limit
- **Insufficient resources**: Check node capacity
- **Check HPA status**: `kubectl describe hpa`

## Output Checklist

After configuring Kubernetes scaling, verify:

- [ ] Waking-service deployed with 2+ replicas
- [ ] HPA configured with appropriate min/max
- [ ] PodDisruptionBudget ensures >=1 available
- [ ] Metrics-server providing CPU/Memory data
- [ ] Instance idle timeout matches plan tier
- [ ] Scale-down stabilization >= 300 seconds
- [ ] Rate limiting configured for wake attempts
- [ ] Pod anti-affinity for HA distribution
- [ ] Monitoring alerts for scaling events

## Related Resources

- **K8s Operations**: Use `platxa-k8s-ops` skill for debugging
- **Scale-to-Zero Flow**: See `references/scale-to-zero-flow.md`
- **HPA Details**: See `references/hpa-configuration.md`
- **Tier Settings**: See `references/tier-configuration.md`
