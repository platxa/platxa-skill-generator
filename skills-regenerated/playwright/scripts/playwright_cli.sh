#!/usr/bin/env bash
# playwright_cli.sh - Wrapper for playwright-cli via npx
#
# Uses npx to run @playwright/mcp playwright-cli without requiring
# a global install. Supports PLAYWRIGHT_CLI_SESSION environment variable
# for session isolation.
#
# Usage:
#   ./playwright_cli.sh open https://example.com
#   ./playwright_cli.sh snapshot
#   ./playwright_cli.sh --session myapp open https://example.com
#
# Environment:
#   PLAYWRIGHT_CLI_SESSION - default session name (overridden by --session flag)

set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but not found on PATH." >&2
  echo "Install Node.js >= 18 to get npx: https://nodejs.org/" >&2
  exit 1
fi

has_session_flag="false"
for arg in "$@"; do
  case "$arg" in
    --session|--session=*)
      has_session_flag="true"
      break
      ;;
  esac
done

cmd=(npx --yes --package @playwright/mcp playwright-cli)
if [[ "${has_session_flag}" != "true" && -n "${PLAYWRIGHT_CLI_SESSION:-}" ]]; then
  cmd+=(--session "${PLAYWRIGHT_CLI_SESSION}")
fi
cmd+=("$@")

exec "${cmd[@]}"
