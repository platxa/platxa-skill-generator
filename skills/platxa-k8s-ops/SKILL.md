---
name: platxa-k8s-ops
description: Kubernetes operations automation for Platxa platform. Debug instances, manage clusters, scale deployments, and perform infrastructure operations with guided workflows.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - automation
    - kubernetes
    - devops
    - infrastructure
---

# Platxa K8s Operations

Automated Kubernetes operations for the Platxa platform with guided debugging workflows.

## Overview

This skill provides operational commands for managing Platxa's Kubernetes infrastructure:

| Category | Operations |
|----------|------------|
| **Cluster** | Setup, health check, node status |
| **Instance** | Status, logs, events, scale, wake, shell |
| **Helm** | Diff, sync, release status |
| **Debug** | Pod, network, storage, ingress diagnostics |
| **Monitor** | Service health, resource usage, alerts |

## Prerequisites

Required tools (verify with `which <tool>`):
- `kubectl` - Kubernetes CLI (configured with cluster access)
- `helm` - Helm package manager
- `helmfile` - Declarative Helm releases

Verify cluster connectivity:
```bash
kubectl cluster-info
kubectl get nodes
```

## Operations Reference

### Cluster Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| Setup Kind | `./install.sh kind` | Install local Kind cluster |
| Setup DOKS | `./install.sh doks` | Install DOKS production cluster |
| Health Check | `kubectl get pods -A` | Check all pod statuses |
| Node Status | `kubectl get nodes -o wide` | List nodes with resources |

### Instance Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| List All | `kubectl get ns -l platxa.io/tier=instance` | List instance namespaces |
| Status | `kubectl get all -n instance-{name}` | Instance resources |
| Logs | `kubectl logs -n instance-{name} -l app=odoo --tail=100` | View logs |
| Events | `kubectl get events -n instance-{name} --sort-by='.lastTimestamp'` | Recent events |
| Scale Up | `kubectl scale deploy odoo-{name} -n instance-{name} --replicas=1` | Wake instance |
| Scale Down | `kubectl scale deploy odoo-{name} -n instance-{name} --replicas=0` | Sleep instance |
| Shell | `kubectl exec -n instance-{name} -it deploy/odoo-{name} -- /bin/bash` | Access pod |

### Infrastructure Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| Helm Diff | `helmfile -e kind diff` | Preview changes |
| Helm Sync | `helmfile -e kind sync` | Apply releases |
| Release Status | `helm list -A` | All Helm releases |

## Workflow

When a user requests K8s operations, follow this workflow:

### Step 1: Identify Operation Type

Detect intent from user message:
- "debug", "not working", "help" → Instance debugging
- "health", "status", "check" → Cluster health check
- "deploy", "update", "sync" → Infrastructure update
- "wake", "scale", "start" → Instance scaling
- "logs", "events" → Instance investigation

### Step 2: Gather Context

Before executing commands:
1. Identify target (instance name, namespace, release)
2. Verify current cluster context: `kubectl config current-context`
3. Check if target exists: `kubectl get ns <namespace>`

### Step 3: Execute Operation

Run appropriate commands from Operations Reference above.
Always show the command before executing for transparency.

### Step 4: Analyze Results

Interpret output and identify:
- Status indicators (Running, Pending, Error, CrashLoopBackOff)
- Resource issues (OOMKilled, insufficient CPU/memory)
- Configuration problems (missing secrets, wrong image)
- Network issues (service unreachable, policy blocking)

### Step 5: Recommend Actions

Based on findings:
- Provide specific fix commands
- Suggest follow-up checks
- Link to relevant troubleshooting guide sections

## Examples

### Example 1: Debug Non-Responsive Instance

**User**: "The abc123xy instance isn't loading"

**Response**:
```
Checking instance status...

kubectl get all -n instance-abc123xy
# Output: deployment replicas=0

The instance is scaled to zero (sleeping). Waking it up:

kubectl scale deploy odoo-abc123xy -n instance-abc123xy --replicas=1
kubectl wait --for=condition=available deploy/odoo-abc123xy -n instance-abc123xy --timeout=120s

Instance is now running. Access at: https://abc123xy.platxa.com
```

### Example 2: Pre-Deployment Health Check

**User**: "Is the cluster healthy before I deploy?"

**Response**:
```
Running cluster health check...

Nodes:
kubectl get nodes
# All nodes Ready ✓

Core Services:
kubectl get pods -n traefik-system
kubectl get pods -n postgres-system
kubectl get pods -n monitoring
# All pods Running ✓

Resource Availability:
kubectl top nodes
# CPU/Memory within limits ✓

Cluster is healthy. Safe to proceed with deployment.
Preview changes with: helmfile -e kind diff
```

### Example 3: Investigate Pod CrashLoop

**User**: "Instance demo keeps restarting"

**Response**:
```
Investigating crash loop...

Pod Status:
kubectl get pods -n instance-demo -l app=odoo
# STATUS: CrashLoopBackOff, Restarts: 5

Recent Events:
kubectl get events -n instance-demo --sort-by='.lastTimestamp' | head -20
# Event: OOMKilled

Container Logs (last crash):
kubectl logs -n instance-demo -l app=odoo --previous --tail=50
# Error: Cannot allocate memory

Root Cause: Out of Memory (OOMKilled)

Fix Options:
1. Increase memory limit in instance tier
2. Reduce Odoo workers: kubectl edit configmap odoo-config -n instance-demo
3. Check for memory leaks in custom addons
```

### Example 4: Helm Release Update

**User**: "Update the Traefik ingress controller"

**Response**:
```
Previewing Traefik update...

helmfile -e kind -l name=traefik diff

Changes:
- image: traefik:v2.10.5 -> traefik:v2.11.0
- Added new middleware configuration

Ready to apply? Running sync:

helmfile -e kind -l name=traefik sync

Verifying deployment:
kubectl rollout status deploy/traefik -n traefik-system

Traefik updated successfully. All ingress routes operational.
```

## Error Handling

### Connection Errors

**Symptom**: `Unable to connect to the server`

**Causes**:
- Kubeconfig not set or expired
- Cluster not running (Kind)
- Network issues (DOKS)

**Fix**:
```bash
# Kind: Restart cluster
kind get clusters
kind export kubeconfig --name platxa

# DOKS: Refresh credentials
doctl kubernetes cluster kubeconfig save <cluster-id>
```

### Permission Denied

**Symptom**: `forbidden: User cannot <action>`

**Causes**:
- RBAC role not bound
- Service account missing permissions

**Fix**: Check and apply RBAC:
```bash
kubectl auth can-i <verb> <resource> -n <namespace>
# If denied, apply appropriate RoleBinding
```

### Resource Not Found

**Symptom**: `NotFound: <resource> not found`

**Causes**:
- Wrong namespace
- Resource deleted
- Typo in name

**Fix**: Verify resource exists:
```bash
kubectl get <resource-type> -A | grep <name>
kubectl get ns | grep instance
```

### Pod Stuck Pending

**Symptom**: Pod in Pending state

**Causes**:
- Insufficient resources
- PVC not bound
- Node selector mismatch

**Fix**:
```bash
kubectl describe pod <pod> -n <namespace>
# Check Events section for scheduling failure reason
```

## Safety

### Read-Only Operations (Safe)
- `get`, `describe`, `logs`, `events` - No cluster changes
- `diff` - Preview only, no apply

### Write Operations (Caution)
- `scale` - Changes replica count
- `sync` - Applies Helm releases
- `delete` - Removes resources

### Dangerous Operations (Require Confirmation)
- `kubectl delete ns` - Deletes entire namespace
- `helmfile destroy` - Removes all releases
- `kubectl drain` - Evicts all pods from node

Always preview changes with `diff` before `sync`.
Never run destructive commands without explicit user confirmation.

## Output Checklist

After completing an operation, verify:

- [ ] Command executed successfully (exit code 0)
- [ ] Output analyzed and interpreted
- [ ] Issues identified (if any)
- [ ] Fix recommendations provided
- [ ] Follow-up actions suggested
- [ ] User can proceed with confidence
