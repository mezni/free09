#!/usr/bin/env bash
set -euo pipefail

# run-checks.sh — Single entry point for all required checks.
#
# Sessions: fast_checks, slow_checks, trace, key, webhook, benchmark, log,
# metric, alert, mesh, runbook, and any
# other nox session defined in noxfile.py.
# Forwards the nox session exit code unchanged, so CI pipelines can rely on
# exit code 0/1/2/3 semantics without wrapping.

if [[ ${#} -lt 1 ]]; then
    echo "Usage: run-checks.sh <nox-session> [session-flags...]" >&2
    exit 1
fi

SESSION="${1}"
shift

# Resolve the nox command. Prefer an explicit `nox` on PATH; fall back to the
# project's uv environment so the script works from a plain checkout.
if command -v nox >/dev/null 2>&1; then
    NOX=(nox)
elif command -v uv >/dev/null 2>&1; then
    NOX=(uv run --no-sync nox)
else
    echo "run-checks.sh: neither 'nox' nor 'uv' is available on PATH" >&2
    exit 2
fi

# Run the requested nox session and pass its exit code through.
exec "${NOX[@]}" -s "${SESSION}" "$@"
