#!/usr/bin/env bash
# Platxa Instance Operations
# Usage: instance-ops.sh <command> <instance-name> [options]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $(basename "$0") <command> <instance-name> [options]

Commands:
  status    Show instance status
  logs      View instance logs
  events    Show recent events
  scale     Scale instance (0 or 1)
  wake      Wake sleeping instance
  sleep     Put instance to sleep
  shell     Access instance shell

Options:
  --tail N     Number of log lines (default: 100)
  --follow     Follow logs
  --previous   Show previous container logs

Examples:
  $(basename "$0") status abc123xy
  $(basename "$0") logs abc123xy --tail 200
  $(basename "$0") wake abc123xy
  $(basename "$0") scale abc123xy 0
EOF
    exit 1
}

[[ $# -lt 2 ]] && usage

COMMAND="$1"
INSTANCE="$2"
shift 2

# Parse options
TAIL=100
FOLLOW=""
PREVIOUS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tail) TAIL="$2"; shift 2 ;;
        --follow|-f) FOLLOW="-f"; shift ;;
        --previous|-p) PREVIOUS="--previous"; shift ;;
        *)
            if [[ "$COMMAND" == "scale" ]]; then
                REPLICAS="$1"
                shift
            else
                echo "Unknown option: $1"
                exit 1
            fi
            ;;
    esac
done

NAMESPACE="instance-$INSTANCE"
DEPLOYMENT="odoo-$INSTANCE"

# Verify namespace exists
check_namespace() {
    if ! kubectl get ns "$NAMESPACE" &>/dev/null; then
        echo -e "${RED}Error:${NC} Namespace '$NAMESPACE' not found"
        echo ""
        echo "Available instance namespaces:"
        kubectl get ns -l platxa.io/tier=instance --no-headers 2>/dev/null | awk '{print "  " $1}' || echo "  (none)"
        exit 1
    fi
}

case "$COMMAND" in
    status)
        check_namespace
        echo -e "${BLUE}=== Instance: $INSTANCE ===${NC}"
        echo ""
        echo "Namespace: $NAMESPACE"
        echo ""

        echo "Deployment:"
        kubectl get deploy "$DEPLOYMENT" -n "$NAMESPACE" -o wide 2>/dev/null || echo "  Not found"
        echo ""

        echo "Pods:"
        kubectl get pods -n "$NAMESPACE" -l app=odoo -o wide 2>/dev/null || echo "  No pods"
        echo ""

        echo "Services:"
        kubectl get svc -n "$NAMESPACE" 2>/dev/null || echo "  No services"
        echo ""

        echo "Ingress:"
        kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "  No ingress"
        echo ""

        echo "Storage:"
        kubectl get pvc -n "$NAMESPACE" 2>/dev/null || echo "  No PVCs"
        ;;

    logs)
        check_namespace
        echo -e "${BLUE}=== Logs: $INSTANCE ===${NC}"
        # shellcheck disable=SC2086
        kubectl logs -n "$NAMESPACE" -l app=odoo --tail="$TAIL" $FOLLOW $PREVIOUS 2>/dev/null || {
            echo -e "${YELLOW}No logs available. Pod may not be running.${NC}"
            echo "Current status:"
            kubectl get pods -n "$NAMESPACE" -l app=odoo
        }
        ;;

    events)
        check_namespace
        echo -e "${BLUE}=== Events: $INSTANCE ===${NC}"
        kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' 2>/dev/null | tail -30 || echo "No events"
        ;;

    scale)
        check_namespace
        [[ -z "${REPLICAS:-}" ]] && { echo "Usage: instance-ops.sh scale <instance> <0|1>"; exit 1; }

        CURRENT=$(kubectl get deploy "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "?")
        echo "Current replicas: $CURRENT"
        echo "Scaling to: $REPLICAS"

        kubectl scale deploy "$DEPLOYMENT" -n "$NAMESPACE" --replicas="$REPLICAS"

        if [[ "$REPLICAS" -gt 0 ]]; then
            echo "Waiting for pod to be ready..."
            kubectl wait --for=condition=available deploy/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=120s && \
                echo -e "${GREEN}Instance scaled successfully${NC}" || \
                echo -e "${YELLOW}Timeout waiting for pod. Check: kubectl get pods -n $NAMESPACE${NC}"
        else
            echo -e "${GREEN}Instance scaled to 0${NC}"
        fi
        ;;

    wake)
        check_namespace
        CURRENT=$(kubectl get deploy "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

        if [[ "$CURRENT" -gt 0 ]]; then
            echo -e "${GREEN}Instance already running (replicas: $CURRENT)${NC}"
        else
            echo "Waking instance $INSTANCE..."
            kubectl scale deploy "$DEPLOYMENT" -n "$NAMESPACE" --replicas=1

            echo "Waiting for pod to be ready..."
            if kubectl wait --for=condition=available deploy/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=120s; then
                echo -e "${GREEN}Instance is now running${NC}"
                HOST=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "$INSTANCE.platxa.com")
                echo "Access at: https://$HOST"
            else
                echo -e "${YELLOW}Timeout. Check status:${NC}"
                kubectl get pods -n "$NAMESPACE" -l app=odoo
            fi
        fi
        ;;

    sleep)
        check_namespace
        CURRENT=$(kubectl get deploy "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

        if [[ "$CURRENT" -eq 0 ]]; then
            echo -e "${GREEN}Instance already sleeping (replicas: 0)${NC}"
        else
            echo "Putting instance $INSTANCE to sleep..."
            kubectl scale deploy "$DEPLOYMENT" -n "$NAMESPACE" --replicas=0
            echo -e "${GREEN}Instance is now sleeping${NC}"
        fi
        ;;

    shell)
        check_namespace
        CURRENT=$(kubectl get deploy "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

        if [[ "$CURRENT" -eq 0 ]]; then
            echo -e "${YELLOW}Instance is sleeping. Wake it first:${NC}"
            echo "  $(basename "$0") wake $INSTANCE"
            exit 1
        fi

        echo "Connecting to instance $INSTANCE..."
        kubectl exec -n "$NAMESPACE" -it deploy/"$DEPLOYMENT" -- /bin/bash
        ;;

    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
