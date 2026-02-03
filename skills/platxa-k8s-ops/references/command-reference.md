# Platxa K8s Command Reference

## Cluster Commands

### Setup
```bash
# Local development (Kind)
./infrastructure/scripts/install.sh kind

# Production (DOKS)
./infrastructure/scripts/install.sh doks

# Single component
./infrastructure/scripts/install.sh kind traefik
```

### Status
```bash
# Cluster info
kubectl cluster-info

# Node status
kubectl get nodes -o wide

# All namespaces
kubectl get ns

# All pods (check for issues)
kubectl get pods -A | grep -v Running | grep -v Completed
```

## Instance Commands

Replace `{name}` with instance name (e.g., `abc123xy`).

### Query
```bash
# List all instances
kubectl get ns -l platxa.io/tier=instance

# Instance status
kubectl get all -n instance-{name}

# Pod details
kubectl describe pod -n instance-{name} -l app=odoo

# Logs (current)
kubectl logs -n instance-{name} -l app=odoo --tail=100

# Logs (previous crash)
kubectl logs -n instance-{name} -l app=odoo --previous --tail=100

# Events
kubectl get events -n instance-{name} --sort-by='.lastTimestamp'
```

### Scaling
```bash
# Check current replicas
kubectl get deploy odoo-{name} -n instance-{name} -o jsonpath='{.spec.replicas}'

# Wake (scale to 1)
kubectl scale deploy odoo-{name} -n instance-{name} --replicas=1

# Sleep (scale to 0)
kubectl scale deploy odoo-{name} -n instance-{name} --replicas=0

# Wait for ready
kubectl wait --for=condition=available deploy/odoo-{name} -n instance-{name} --timeout=120s
```

### Access
```bash
# Shell into pod
kubectl exec -n instance-{name} -it deploy/odoo-{name} -- /bin/bash

# Port forward (local access)
kubectl port-forward -n instance-{name} svc/odoo-{name} 8069:8069

# Copy file from pod
kubectl cp instance-{name}/$(kubectl get pod -n instance-{name} -l app=odoo -o jsonpath='{.items[0].metadata.name}'):/path/to/file ./local-file
```

## Helm Commands

### Helmfile Operations
```bash
# Preview changes (Kind)
helmfile -e kind diff

# Preview changes (DOKS)
helmfile -e doks diff

# Apply all releases
helmfile -e kind sync

# Apply specific release
helmfile -e kind -l name=traefik sync

# Destroy release
helmfile -e kind -l name=traefik destroy
```

### Direct Helm
```bash
# List releases
helm list -A

# Release history
helm history <release> -n <namespace>

# Rollback
helm rollback <release> <revision> -n <namespace>

# Uninstall
helm uninstall <release> -n <namespace>
```

## Debug Commands

### Pod Debugging
```bash
# Describe pod
kubectl describe pod -n {namespace} {pod-name}

# Resource usage
kubectl top pod -n {namespace}

# Container logs
kubectl logs -n {namespace} {pod-name} -c {container-name}

# Previous container
kubectl logs -n {namespace} {pod-name} --previous
```

### Network Debugging
```bash
# Network policies
kubectl get networkpolicies -n {namespace}

# Describe policy
kubectl describe networkpolicy -n {namespace} {policy-name}

# Service endpoints
kubectl get endpoints -n {namespace}

# Ingress details
kubectl describe ingress -n {namespace}
```

### Storage Debugging
```bash
# PVC status
kubectl get pvc -n {namespace}

# PV details
kubectl describe pv {pv-name}

# Storage classes
kubectl get sc

# Disk usage (inside pod)
kubectl exec -n {namespace} deploy/{name} -- df -h
```

## Monitoring Commands

### Waking Service
```bash
# Status
kubectl get deploy waking-service -n traefik-system

# Logs
kubectl logs -n traefik-system -l app.kubernetes.io/name=waking-service --tail=100

# Restart
kubectl rollout restart deploy/waking-service -n traefik-system
```

### Traefik
```bash
# Status
kubectl get pods -n traefik-system -l app.kubernetes.io/name=traefik

# Logs
kubectl logs -n traefik-system -l app.kubernetes.io/name=traefik --tail=100

# IngressRoutes
kubectl get ingressroute -A
```

### PostgreSQL
```bash
# Status
kubectl get pods -n postgres-system

# Connect (port forward)
kubectl port-forward -n postgres-system svc/postgres 5432:5432
```

### Prometheus/Grafana
```bash
# Status
kubectl get pods -n monitoring

# Grafana access
kubectl port-forward -n monitoring svc/grafana 3000:80

# Prometheus access
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
```

## Quick Checks

### Cluster Health
```bash
# One-liner health check
kubectl get nodes && kubectl get pods -A | grep -v Running | grep -v Completed
```

### Instance Health
```bash
# Quick status for instance
kubectl get deploy,svc,ingress,pvc -n instance-{name}
```

### Before Deployment
```bash
# Pre-flight check
kubectl get nodes && \
kubectl get pods -n traefik-system && \
kubectl get pods -n postgres-system && \
helmfile -e kind diff
```
