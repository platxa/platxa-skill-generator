#!/usr/bin/env bash
# Platxa Helmfile Operations
# Usage: helm-ops.sh <command> [release] [--env kind|doks]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Find infrastructure directory
find_infra_dir() {
    local search_paths=(
        "./infrastructure"
        "../platxa-platform/infrastructure"
        "../../platxa/platxa-platform/infrastructure"
        "$HOME/workspace/platxa/platxa-platform/infrastructure"
    )

    for path in "${search_paths[@]}"; do
        if [[ -f "$path/helmfile.yaml.gotmpl" ]]; then
            echo "$path"
            return 0
        fi
    done

    echo ""
    return 1
}

usage() {
    cat <<EOF
Usage: $(basename "$0") <command> [release] [options]

Commands:
  diff      Preview changes (default: all releases)
  sync      Apply releases
  status    Show release status
  list      List all releases

Options:
  --env ENV     Environment: kind or doks (auto-detected from context)
  --release R   Target specific release

Examples:
  $(basename "$0") diff
  $(basename "$0") diff --release traefik
  $(basename "$0") sync --env kind
  $(basename "$0") status
EOF
    exit 1
}

[[ $# -lt 1 ]] && usage

COMMAND="$1"
shift

# Parse options
ENV=""
RELEASE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env) ENV="$2"; shift 2 ;;
        --release|-l) RELEASE="$2"; shift 2 ;;
        *)
            # Positional argument could be release name
            if [[ -z "$RELEASE" ]]; then
                RELEASE="$1"
            fi
            shift
            ;;
    esac
done

# Auto-detect environment from context
detect_env() {
    local context
    context=$(kubectl config current-context 2>/dev/null || echo "unknown")

    if [[ "$context" == *"kind"* ]]; then
        echo "kind"
    elif [[ "$context" == *"do-"* ]] || [[ "$context" == *"doks"* ]]; then
        echo "doks"
    else
        echo ""
    fi
}

# Set environment
if [[ -z "$ENV" ]]; then
    ENV=$(detect_env)
    if [[ -z "$ENV" ]]; then
        echo -e "${YELLOW}Warning:${NC} Could not auto-detect environment"
        echo "Specify with --env kind or --env doks"
        echo ""
        echo "Current context: $(kubectl config current-context 2>/dev/null || echo 'none')"
        exit 1
    fi
    echo -e "${BLUE}Auto-detected environment:${NC} $ENV"
fi

# Find infrastructure directory
INFRA_DIR=$(find_infra_dir)
if [[ -z "$INFRA_DIR" ]]; then
    echo -e "${RED}Error:${NC} Could not find infrastructure directory"
    echo "Expected helmfile.yaml.gotmpl in one of:"
    echo "  ./infrastructure"
    echo "  ../platxa-platform/infrastructure"
    echo "  ~/workspace/platxa/platxa-platform/infrastructure"
    exit 1
fi

echo -e "${BLUE}Infrastructure dir:${NC} $INFRA_DIR"
echo ""

# Build helmfile command
HELMFILE_CMD="helmfile -e $ENV"
if [[ -n "$RELEASE" ]]; then
    HELMFILE_CMD="$HELMFILE_CMD -l name=$RELEASE"
fi

case "$COMMAND" in
    diff)
        echo -e "${BLUE}=== Helmfile Diff ($ENV) ===${NC}"
        [[ -n "$RELEASE" ]] && echo "Release: $RELEASE"
        echo ""

        cd "$INFRA_DIR"
        $HELMFILE_CMD diff || {
            EXIT_CODE=$?
            if [[ $EXIT_CODE -eq 2 ]]; then
                echo -e "${GREEN}No changes detected${NC}"
            else
                echo -e "${RED}Diff failed with exit code: $EXIT_CODE${NC}"
                exit $EXIT_CODE
            fi
        }
        ;;

    sync)
        echo -e "${BLUE}=== Helmfile Sync ($ENV) ===${NC}"
        [[ -n "$RELEASE" ]] && echo "Release: $RELEASE"
        echo ""

        echo -e "${YELLOW}This will apply changes to the cluster.${NC}"
        read -rp "Continue? [y/N] " confirm
        if [[ ! "$confirm" =~ ^[Yy] ]]; then
            echo "Aborted."
            exit 0
        fi

        cd "$INFRA_DIR"
        $HELMFILE_CMD sync

        echo ""
        echo -e "${GREEN}Sync complete${NC}"
        ;;

    status)
        echo -e "${BLUE}=== Helm Release Status ===${NC}"
        echo ""

        if [[ -n "$RELEASE" ]]; then
            helm status "$RELEASE" -A 2>/dev/null || echo "Release '$RELEASE' not found"
        else
            helm list -A
        fi
        ;;

    list)
        echo -e "${BLUE}=== Helm Releases ===${NC}"
        echo ""
        helm list -A
        ;;

    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
