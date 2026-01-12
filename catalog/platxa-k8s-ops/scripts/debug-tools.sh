#!/usr/bin/env bash
# Platxa K8s Debug Tools
# Usage: debug-tools.sh <category> <namespace> [selector]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $(basename "$0") <category> <namespace> [options]

Categories:
  pod        Debug pod issues
  network    Check network policies
  storage    Check storage/PVCs
  ingress    Debug ingress routing
  all        Run all diagnostics

Options:
  --selector S   Pod selector (default: app=odoo for instances)

Examples:
  $(basename "$0") pod instance-abc123xy
  $(basename "$0") network traefik-system
  $(basename "$0") storage instance-abc123xy
  $(basename "$0") all instance-abc123xy
EOF
    exit 1
}

[[ $# -lt 2 ]] && usage

CATEGORY="$1"
NAMESPACE="$2"
shift 2

# Parse options
SELECTOR=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --selector|-l) SELECTOR="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Auto-detect selector for instance namespaces
if [[ -z "$SELECTOR" ]] && [[ "$NAMESPACE" == instance-* ]]; then
    SELECTOR="app=odoo"
fi

# Verify namespace exists
if ! kubectl get ns "$NAMESPACE" &>/dev/null; then
    echo -e "${RED}Error:${NC} Namespace '$NAMESPACE' not found"
    exit 1
fi

debug_pod() {
    echo -e "${BLUE}=== Pod Diagnostics: $NAMESPACE ===${NC}"
    echo ""

    # List pods
    echo "Pods:"
    if [[ -n "$SELECTOR" ]]; then
        kubectl get pods -n "$NAMESPACE" -l "$SELECTOR" -o wide
    else
        kubectl get pods -n "$NAMESPACE" -o wide
    fi
    echo ""

    # Get first pod
    local POD
    if [[ -n "$SELECTOR" ]]; then
        POD=$(kubectl get pods -n "$NAMESPACE" -l "$SELECTOR" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    else
        POD=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    fi

    if [[ -z "$POD" ]]; then
        echo -e "${YELLOW}No pods found${NC}"
        return
    fi

    echo "Pod Details: $POD"
    echo ""

    # Pod status
    local STATUS
    STATUS=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
    echo "Status: $STATUS"

    # Container statuses
    echo ""
    echo "Container Statuses:"
    kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{range .status.containerStatuses[*]}{.name}: {.state}{"\n"}{end}' 2>/dev/null || echo "  Unable to get container status"

    # Restart count
    local RESTARTS
    RESTARTS=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || echo "0")
    echo ""
    echo "Restart Count: $RESTARTS"

    # Resource usage
    echo ""
    echo "Resource Usage:"
    kubectl top pod "$POD" -n "$NAMESPACE" 2>/dev/null || echo "  Metrics not available"

    # Recent events
    echo ""
    echo "Recent Events:"
    kubectl get events -n "$NAMESPACE" --field-selector "involvedObject.name=$POD" --sort-by='.lastTimestamp' 2>/dev/null | tail -10 || echo "  No events"

    # Check for OOM
    local REASON
    REASON=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}' 2>/dev/null || echo "")
    if [[ "$REASON" == "OOMKilled" ]]; then
        echo ""
        echo -e "${RED}WARNING: Pod was OOMKilled${NC}"
        echo "Recommendation: Increase memory limit or reduce workers"
    fi
}

debug_network() {
    echo -e "${BLUE}=== Network Diagnostics: $NAMESPACE ===${NC}"
    echo ""

    # Network policies
    echo "Network Policies:"
    kubectl get networkpolicies -n "$NAMESPACE" 2>/dev/null || echo "  None"
    echo ""

    # Describe policies
    local POLICIES
    POLICIES=$(kubectl get networkpolicies -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

    if [[ -n "$POLICIES" ]]; then
        for POLICY in $POLICIES; do
            echo "Policy: $POLICY"
            kubectl get networkpolicy "$POLICY" -n "$NAMESPACE" -o yaml 2>/dev/null | grep -A 50 "spec:" | head -30
            echo ""
        done
    fi

    # Services
    echo "Services:"
    kubectl get svc -n "$NAMESPACE" -o wide
    echo ""

    # Endpoints
    echo "Endpoints:"
    kubectl get endpoints -n "$NAMESPACE"
    echo ""

    # DNS test (if pod available)
    if [[ -n "$SELECTOR" ]]; then
        local POD
        POD=$(kubectl get pods -n "$NAMESPACE" -l "$SELECTOR" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        if [[ -n "$POD" ]]; then
            echo "DNS Resolution Test:"
            kubectl exec -n "$NAMESPACE" "$POD" -- nslookup kubernetes.default 2>/dev/null || echo "  DNS test failed (pod may not have nslookup)"
        fi
    fi
}

debug_storage() {
    echo -e "${BLUE}=== Storage Diagnostics: $NAMESPACE ===${NC}"
    echo ""

    # PVCs
    echo "Persistent Volume Claims:"
    kubectl get pvc -n "$NAMESPACE" -o wide 2>/dev/null || echo "  None"
    echo ""

    # PVC details
    local PVCS
    PVCS=$(kubectl get pvc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

    if [[ -n "$PVCS" ]]; then
        for PVC in $PVCS; do
            echo "PVC: $PVC"
            local STATUS
            STATUS=$(kubectl get pvc "$PVC" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
            local CAPACITY
            CAPACITY=$(kubectl get pvc "$PVC" -n "$NAMESPACE" -o jsonpath='{.status.capacity.storage}')
            echo "  Status: $STATUS"
            echo "  Capacity: $CAPACITY"

            if [[ "$STATUS" != "Bound" ]]; then
                echo -e "  ${YELLOW}WARNING: PVC not bound${NC}"
                kubectl describe pvc "$PVC" -n "$NAMESPACE" 2>/dev/null | grep -A 5 "Events:" || true
            fi
            echo ""
        done
    fi

    # Disk usage in pod
    if [[ -n "$SELECTOR" ]]; then
        local POD
        POD=$(kubectl get pods -n "$NAMESPACE" -l "$SELECTOR" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        if [[ -n "$POD" ]]; then
            echo "Disk Usage in Pod:"
            kubectl exec -n "$NAMESPACE" "$POD" -- df -h 2>/dev/null | grep -E "^Filesystem|/mnt|/var/lib/odoo" || echo "  Unable to get disk usage"
        fi
    fi

    # Storage classes
    echo ""
    echo "Available Storage Classes:"
    kubectl get sc
}

debug_ingress() {
    echo -e "${BLUE}=== Ingress Diagnostics: $NAMESPACE ===${NC}"
    echo ""

    # Ingress resources
    echo "Ingress Resources:"
    kubectl get ingress -n "$NAMESPACE" -o wide 2>/dev/null || echo "  None"
    echo ""

    # Ingress details
    local INGRESSES
    INGRESSES=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

    if [[ -n "$INGRESSES" ]]; then
        for ING in $INGRESSES; do
            echo "Ingress: $ING"

            # Hosts
            echo "  Hosts:"
            kubectl get ingress "$ING" -n "$NAMESPACE" -o jsonpath='{range .spec.rules[*]}  - {.host}{"\n"}{end}' 2>/dev/null

            # TLS
            local TLS
            TLS=$(kubectl get ingress "$ING" -n "$NAMESPACE" -o jsonpath='{.spec.tls[*].secretName}' 2>/dev/null || echo "")
            if [[ -n "$TLS" ]]; then
                echo "  TLS Secret: $TLS"
                # Check if secret exists
                if kubectl get secret "$TLS" -n "$NAMESPACE" &>/dev/null; then
                    echo -e "  ${GREEN}TLS secret exists${NC}"
                else
                    echo -e "  ${RED}TLS secret missing!${NC}"
                fi
            fi

            # Backend service
            local SVC
            SVC=$(kubectl get ingress "$ING" -n "$NAMESPACE" -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}' 2>/dev/null || echo "")
            echo "  Backend Service: $SVC"

            # Check if service exists
            if [[ -n "$SVC" ]] && kubectl get svc "$SVC" -n "$NAMESPACE" &>/dev/null; then
                echo -e "  ${GREEN}Backend service exists${NC}"
            elif [[ -n "$SVC" ]]; then
                echo -e "  ${RED}Backend service missing!${NC}"
            fi

            echo ""
        done
    fi

    # Traefik IngressRoutes (if applicable)
    echo "IngressRoutes (Traefik CRD):"
    kubectl get ingressroute -n "$NAMESPACE" 2>/dev/null || echo "  None"
}

case "$CATEGORY" in
    pod)     debug_pod ;;
    network) debug_network ;;
    storage) debug_storage ;;
    ingress) debug_ingress ;;
    all)
        debug_pod
        echo ""
        debug_network
        echo ""
        debug_storage
        echo ""
        debug_ingress
        ;;
    *)
        echo "Unknown category: $CATEGORY"
        usage
        ;;
esac
