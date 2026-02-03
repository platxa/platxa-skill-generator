# Platxa Kubernetes Architecture

## Overview

Platxa uses Kubernetes for multi-tenant Odoo instance hosting with two environments:

| Environment | Purpose | Features |
|-------------|---------|----------|
| **Kind** | Local development | Self-signed TLS, NodePort ingress |
| **DOKS** | Production | Let's Encrypt TLS, LoadBalancer, HPA |

## Namespace Architecture

```
├── kube-system           # Core K8s components
├── traefik-system        # Ingress controller + waking-service
├── postgres-system       # Shared PostgreSQL
├── monitoring            # Prometheus, Grafana, Loki
├── platform              # Instance Manager (Odoo)
└── instance-{name}       # Per-instance namespace (N instances)
```

### Namespace-Per-Instance Model

Each Odoo instance runs in isolated namespace:

```
instance-abc123xy/
├── Deployment: odoo-abc123xy (1 replica or 0 when sleeping)
├── Service: odoo-abc123xy (ClusterIP 8069/8072)
├── Service: waking-service (ExternalName → traefik-system)
├── Ingress: odoo (routes to waking-service or direct)
├── PVC: odoo-addons (custom modules)
├── PVC: odoo-filestore (attachments)
├── Secret: odoo-secrets (DB credentials)
├── ConfigMap: odoo-config (odoo.conf)
├── NetworkPolicy: default-deny-all
├── NetworkPolicy: odoo-instance-policy
├── ResourceQuota: instance-quota
└── LimitRange: instance-limits
```

## Scale-to-Zero Architecture

```
                    ┌──────────────────┐
    User Request → │     Traefik      │
                    │  (traefik-system)│
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │ ExternalName Service routes │
              │ to waking-service           │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Waking Service  │
                    │ (Go proxy)       │
                    └────────┬─────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
    replicas=0?                            replicas=1?
         │                                       │
    ┌────▼────┐                           ┌──────▼──────┐
    │ Scale 1 │                           │ Proxy to    │
    │ Show    │                           │ Odoo pod    │
    │ loading │                           └─────────────┘
    └────┬────┘
         │
    Wait for Ready
         │
    Proxy request
```

### Waking Service Configuration

```yaml
IDLE_TIMEOUT: 15m            # Scale down after 15 mins idle
WAKE_TIMEOUT: 5m             # Max wait for pod ready
NAMESPACE_PATTERN: instance-*
DEPLOYMENT_LABEL: app=odoo
```

## Resource Tiers

| Tier | Memory | CPU | Workers | Use Case |
|------|--------|-----|---------|----------|
| Free | 512Mi | 250m-1000m | 2 | Demo/testing |
| Pro | 1Gi | 500m-2000m | 4 | Small business |
| Team | 2Gi | 1000m-4000m | 6 | Growing team |
| Enterprise | 4Gi | 2000m-8000m | 9 | Large deployment |

## Labels & Selectors

### Standard Labels
```yaml
app.kubernetes.io/name: odoo
app.kubernetes.io/component: web-application
app.kubernetes.io/part-of: platxa-platform
app.kubernetes.io/managed-by: instance-manager
app.kubernetes.io/instance: {name}
```

### Platxa Custom Labels
```yaml
platxa.io/tier: instance
platxa.io/owner-id: {partner_id}
platxa.io/instance-id: {name}
platxa.io/status: active|suspended|disabled
```

## Network Policies

### Instance Ingress (Allowed)
- From: traefik-system (Traefik + waking-service)
- Ports: 8069 (HTTP), 8072 (longpoll)

### Instance Egress (Allowed)
- To: kube-dns (DNS resolution)
- To: postgres-system (database)
- To: external HTTPS (except private ranges)

### Blocked
- Cross-instance communication
- Direct internet access without HTTPS
- NodePort/LoadBalancer services per instance

## Key Components

### Traefik (Ingress Controller)
- Namespace: traefik-system
- Routes: `*.platxa.com` → instances
- TLS: Wildcard certificate from cert-manager
- Middlewares: iframe headers, buffering

### PostgreSQL
- Namespace: postgres-system
- Template databases: `template_odoo_{version}`
- Each instance gets cloned database
- Connection via internal service DNS

### Waking Service
- Namespace: traefik-system
- Purpose: HTTP proxy for scale-to-zero
- RBAC: Can scale deployments in instance-* namespaces
- Metrics: Prometheus scrape on :9090

### Instance Manager
- Namespace: platform
- Purpose: Provision/manage instance resources
- Auth: Service account with namespace-scoped RBAC
- API: Odoo model `instance.kubernetes.service`
