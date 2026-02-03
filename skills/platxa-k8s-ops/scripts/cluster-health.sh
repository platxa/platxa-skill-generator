#!/usr/bin/env bash
# Platxa K8s Cluster Health Check
# Exit codes: 0=healthy, 1=degraded, 2=critical

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CRITICAL=0
DEGRADED=0

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        ok)     echo -e "${GREEN}✓${NC} $message" ;;
        warn)   echo -e "${YELLOW}⚠${NC} $message"; ((DEGRADED++)) ;;
        error)  echo -e "${RED}✗${NC} $message"; ((CRITICAL++)) ;;
    esac
}

echo "=== Platxa K8s Cluster Health Check ==="
echo ""

# Check cluster connectivity
echo "Cluster Connectivity:"
if kubectl cluster-info &>/dev/null; then
    CONTEXT=$(kubectl config current-context)
    print_status ok "Connected to cluster: $CONTEXT"
else
    print_status error "Cannot connect to cluster"
    exit 2
fi
echo ""

# Check nodes
echo "Node Status:"
NODES_READY=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready" || echo 0)
NODES_TOTAL=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo 0)
if [[ "$NODES_READY" -eq "$NODES_TOTAL" ]] && [[ "$NODES_TOTAL" -gt 0 ]]; then
    print_status ok "All nodes ready ($NODES_READY/$NODES_TOTAL)"
elif [[ "$NODES_READY" -gt 0 ]]; then
    print_status warn "Some nodes not ready ($NODES_READY/$NODES_TOTAL)"
else
    print_status error "No nodes ready"
fi
echo ""

# Check core namespaces
echo "Core Namespaces:"
for NS in traefik-system postgres-system monitoring; do
    if kubectl get ns "$NS" &>/dev/null; then
        PODS_RUNNING=$(kubectl get pods -n "$NS" --no-headers 2>/dev/null | grep -c "Running" || echo 0)
        PODS_TOTAL=$(kubectl get pods -n "$NS" --no-headers 2>/dev/null | wc -l || echo 0)
        if [[ "$PODS_TOTAL" -eq 0 ]]; then
            print_status warn "$NS: No pods"
        elif [[ "$PODS_RUNNING" -eq "$PODS_TOTAL" ]]; then
            print_status ok "$NS: All pods running ($PODS_RUNNING/$PODS_TOTAL)"
        else
            print_status warn "$NS: Some pods not running ($PODS_RUNNING/$PODS_TOTAL)"
        fi
    else
        print_status warn "$NS: Namespace not found"
    fi
done
echo ""

# Check key deployments
echo "Key Services:"
declare -A SERVICES=(
    ["traefik-system:traefik"]="Ingress Controller"
    ["traefik-system:waking-service"]="Scale-to-Zero Proxy"
)

for KEY in "${!SERVICES[@]}"; do
    NS="${KEY%%:*}"
    DEPLOY="${KEY##*:}"
    NAME="${SERVICES[$KEY]}"

    if kubectl get deploy "$DEPLOY" -n "$NS" &>/dev/null; then
        READY=$(kubectl get deploy "$DEPLOY" -n "$NS" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)
        DESIRED=$(kubectl get deploy "$DEPLOY" -n "$NS" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo 0)
        if [[ "${READY:-0}" -eq "${DESIRED:-0}" ]] && [[ "${DESIRED:-0}" -gt 0 ]]; then
            print_status ok "$NAME: Ready ($READY/$DESIRED)"
        else
            print_status warn "$NAME: Not ready ($READY/$DESIRED)"
        fi
    else
        print_status error "$NAME: Deployment not found"
    fi
done
echo ""

# Check storage classes
echo "Storage:"
SC_COUNT=$(kubectl get sc --no-headers 2>/dev/null | wc -l || echo 0)
if [[ "$SC_COUNT" -gt 0 ]]; then
    print_status ok "Storage classes available ($SC_COUNT)"
else
    print_status warn "No storage classes found"
fi
echo ""

# Check instance namespaces
echo "Instances:"
INSTANCE_COUNT=$(kubectl get ns -l platxa.io/tier=instance --no-headers 2>/dev/null | wc -l || echo 0)
if [[ "$INSTANCE_COUNT" -gt 0 ]]; then
    RUNNING=$(kubectl get pods -A -l app=odoo --no-headers 2>/dev/null | grep -c "Running" || echo 0)
    print_status ok "Instance namespaces: $INSTANCE_COUNT (pods running: $RUNNING)"
else
    print_status ok "No instances provisioned"
fi
echo ""

# Summary
echo "=== Summary ==="
if [[ "$CRITICAL" -gt 0 ]]; then
    echo -e "${RED}CRITICAL${NC}: $CRITICAL critical issues found"
    exit 2
elif [[ "$DEGRADED" -gt 0 ]]; then
    echo -e "${YELLOW}DEGRADED${NC}: $DEGRADED warnings found"
    exit 1
else
    echo -e "${GREEN}HEALTHY${NC}: All checks passed"
    exit 0
fi
