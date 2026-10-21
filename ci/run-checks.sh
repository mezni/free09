#!/usr/bin/env bash
set -euo pipefail

# run-checks.sh — Single entry point for all required checks.
# Forwards the nox session exit code unchanged, so CI pipelines can rely on
# exit code 0/1/2/3 semantics without wrapping.

if [[ ${#} -lt 1 ]]; then
    echo "Usage: run-checks.sh <nox-session> [session-flags...]" >&2
    exit 1
fi

SESSION="${1}"
shift

# Run the requested nox session and pass its exit code through.
exec nox run "${SESSION}" "$@"
