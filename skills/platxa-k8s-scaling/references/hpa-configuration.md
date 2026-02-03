# HPA Configuration Reference

Horizontal Pod Autoscaler patterns for Kubernetes autoscaling/v2.

## API Structure

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: <name>
  namespace: <namespace>
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: <deployment-name>
  minReplicas: <min>
  maxReplicas: <max>
  metrics: [...]
  behavior: {...}
```

## Metric Types

### Resource Metrics (CPU/Memory)

```yaml
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
```

### Custom Metrics

```yaml
metrics:
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: 1000
```

### External Metrics

```yaml
metrics:
  - type: External
    external:
      metric:
        name: queue_length
        selector:
          matchLabels:
            queue: orders
      target:
        type: Value
        value: 100
```

## Behavior Policies

### Scale-Up Behavior

```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 30  # Wait before scaling
    policies:
      - type: Pods
        value: 2              # Add 2 pods
        periodSeconds: 60     # Per minute
      - type: Percent
        value: 100            # Double pods
        periodSeconds: 60
    selectPolicy: Max         # Use most aggressive
```

### Scale-Down Behavior

```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300  # 5 min wait
    policies:
      - type: Pods
        value: 1              # Remove 1 pod
        periodSeconds: 120    # Per 2 minutes
      - type: Percent
        value: 50             # Halve pods
        periodSeconds: 60
    selectPolicy: Min         # Use most conservative
```

### Policy Selection

| selectPolicy | Behavior |
|--------------|----------|
| Max | Most aggressive (scale up: add most, scale down: remove most) |
| Min | Most conservative (scale up: add least, scale down: remove least) |
| Disabled | Prevent scaling in this direction |

## Stabilization Window

Prevents thrashing by waiting for metrics to stabilize:

| Direction | Recommended | Purpose |
|-----------|-------------|---------|
| Scale-up | 30-60s | Minimize latency |
| Scale-down | 300s+ | Avoid premature removal |

## Environment Configurations

### Development (Kind)

```yaml
# HPA disabled
spec:
  replicas: 1  # Fixed, no autoscaling
```

### Production Base

```yaml
minReplicas: 2
maxReplicas: 10
metrics:
  - cpu: 70%
  - memory: 80%
```

### Production DOKS

```yaml
minReplicas: 2
maxReplicas: 5
metrics:
  - cpu: 70%  # CPU only
```

## Monitoring HPA

```bash
# Check HPA status
kubectl get hpa -n traefik-system

# Detailed status
kubectl describe hpa waking-service -n traefik-system

# Watch scaling events
kubectl get events -n traefik-system --field-selector reason=SuccessfulRescale
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Unknown metrics | Missing metrics-server | Install metrics-server |
| No scale-up | maxReplicas reached | Increase limit |
| Constant flapping | Short stabilization | Increase window |
| Slow scale-up | Long stabilization | Decrease window |
