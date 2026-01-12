# Platxa K8s Troubleshooting Guide

## Quick Diagnosis Flow

```
Instance not working?
         │
    ┌────▼────┐
    │ Pod     │──No──► Check deployment, events
    │ exists? │
    └────┬────┘
         │Yes
    ┌────▼────┐
    │ Pod     │──Pending──► Check resources, PVC, scheduler
    │ status? │──CrashLoop──► Check logs, OOM, config
    └────┬────┘
         │Running
    ┌────▼────┐
    │ Service │──No──► Check service, endpoints
    │ reachable?│
    └────┬────┘
         │Yes
    ┌────▼────┐
    │ Ingress │──No──► Check ingress, TLS, waking-service
    │ routing?│
    └─────────┘
```

## Common Issues

### Instance Won't Start

**Symptom**: Pod stuck in Pending state

**Diagnosis**:
```bash
kubectl describe pod -n instance-{name} -l app=odoo
# Check Events section
```

**Causes & Fixes**:

| Cause | Event Message | Fix |
|-------|--------------|-----|
| No resources | `Insufficient cpu/memory` | Scale down other instances or upgrade tier |
| PVC pending | `waiting for volume` | Check storage class: `kubectl get sc` |
| Image pull | `ImagePullBackOff` | Check image exists, registry credentials |
| Node selector | `no nodes match` | Check node labels: `kubectl get nodes --show-labels` |

### Instance Keeps Crashing

**Symptom**: CrashLoopBackOff status

**Diagnosis**:
```bash
kubectl logs -n instance-{name} -l app=odoo --previous
kubectl get events -n instance-{name} --sort-by='.lastTimestamp'
```

**Causes & Fixes**:

| Cause | Log/Event | Fix |
|-------|-----------|-----|
| OOMKilled | `OOMKilled` in events | Increase memory limit or reduce workers |
| DB connection | `could not connect to server` | Check postgres-system pods, network policy |
| Config error | `Invalid configuration` | Check configmap: `kubectl get cm -n instance-{name} -o yaml` |
| Missing secret | `secret not found` | Create/check secret: `kubectl get secrets -n instance-{name}` |

### Instance Not Accessible

**Symptom**: 502/503 errors or timeout

**Diagnosis**:
```bash
# Check pod is running
kubectl get pods -n instance-{name}

# Check service endpoints
kubectl get endpoints -n instance-{name}

# Check ingress
kubectl get ingress -n instance-{name} -o yaml

# Check waking-service logs
kubectl logs -n traefik-system -l app.kubernetes.io/name=waking-service --tail=100
```

**Causes & Fixes**:

| Cause | Symptom | Fix |
|-------|---------|-----|
| Scaled to 0 | Replicas: 0 | Wake: `kubectl scale deploy odoo-{name} -n instance-{name} --replicas=1` |
| Waking-service down | 503 from proxy | Restart: `kubectl rollout restart deploy/waking-service -n traefik-system` |
| Network policy | Connection refused | Check: `kubectl get networkpolicies -n instance-{name}` |
| TLS issue | Certificate error | Check: `kubectl get certificate -n traefik-system` |

### Instance Won't Wake Automatically

**Symptom**: Request hangs, instance stays at 0 replicas

**Diagnosis**:
```bash
# Check waking-service health
kubectl get pods -n traefik-system -l app.kubernetes.io/name=waking-service

# Check waking-service logs for errors
kubectl logs -n traefik-system -l app.kubernetes.io/name=waking-service --tail=200 | grep -E "(error|failed|instance-)"

# Check RBAC
kubectl auth can-i update deployments/scale -n instance-{name} --as=system:serviceaccount:traefik-system:waking-service
```

**Causes & Fixes**:

| Cause | Fix |
|-------|-----|
| RBAC missing | Apply waking-service RBAC from infrastructure/manifests |
| Service routing | Check ExternalName service in instance namespace |
| Ingress annotation | Verify ingress routes to waking-service |

### Storage Issues

**Symptom**: Pod pending, PVC not bound, disk full

**Diagnosis**:
```bash
# Check PVC status
kubectl get pvc -n instance-{name}

# Check storage usage
kubectl exec -n instance-{name} -it deploy/odoo-{name} -- df -h /mnt/extra-addons /var/lib/odoo/filestore

# Check storage class
kubectl get sc
```

**Causes & Fixes**:

| Cause | Fix |
|-------|-----|
| PVC pending | Check storage class exists and has capacity |
| Disk full (addons) | Clean up unused modules |
| Disk full (filestore) | Archive old attachments, upgrade storage tier |

### Helm Release Issues

**Symptom**: `helmfile sync` fails

**Diagnosis**:
```bash
# Check release status
helm list -A

# Check specific release
helm history <release> -n <namespace>

# Check values
helmfile -e kind -l name=<release> template
```

**Causes & Fixes**:

| Cause | Error | Fix |
|-------|-------|-----|
| Chart version | `chart not found` | Update versions.yaml, run `helm repo update` |
| Values conflict | `cannot patch` | Check for immutable fields, delete and recreate |
| CRD missing | `no matches for kind` | Apply CRDs first: `helmfile -e kind -l name=cert-manager sync` |

## Health Check Commands

### Full Cluster Health
```bash
# All pods status
kubectl get pods -A | grep -v Running | grep -v Completed

# Node resources
kubectl top nodes

# PVC status
kubectl get pvc -A | grep -v Bound
```

### Instance Health
```bash
# Quick check
kubectl get all -n instance-{name}

# Detailed
kubectl describe deploy odoo-{name} -n instance-{name}
kubectl get events -n instance-{name} --sort-by='.lastTimestamp'
```

### Infrastructure Health
```bash
# Core services
kubectl get pods -n traefik-system
kubectl get pods -n postgres-system
kubectl get pods -n monitoring

# Certificates
kubectl get certificates -A
```

## Recovery Procedures

### Force Restart Instance
```bash
kubectl rollout restart deploy/odoo-{name} -n instance-{name}
kubectl rollout status deploy/odoo-{name} -n instance-{name}
```

### Rebuild Instance Resources
```bash
# Delete and let Instance Manager recreate
# (Only if managed by Instance Manager)
kubectl delete deploy odoo-{name} -n instance-{name}
# Trigger recreation via Odoo platform
```

### Reset Waking Service
```bash
kubectl rollout restart deploy/waking-service -n traefik-system
kubectl logs -n traefik-system -l app.kubernetes.io/name=waking-service -f
```

### Emergency: Delete Stuck Namespace
```bash
# Check for finalizers
kubectl get ns instance-{name} -o yaml | grep finalizers

# Remove finalizers if stuck (CAUTION)
kubectl patch ns instance-{name} -p '{"metadata":{"finalizers":null}}'
```
