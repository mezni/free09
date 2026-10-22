#!/usr/bin/env bash
set -euo pipefail
# setup.sh — Phase 1 setup path.
# Verifies prerequisites, syncs dependencies, starts PostgreSQL, and creates .env
# idempotently without destroying locally-supplied values.

# -- Step 1: Verify prerequisites --
echo "=== Prerequisite verification ==="
python3 ci/check_prerequisites.py || {
    echo "Prerequisite check failed. Aborting setup."
    exit 1
}
echo "Prerequisites OK."

# -- Step 2: Sync dependencies --
echo "=== Dependency sync ==="
uv sync --frozen --all-packages || {
    echo "Dependency sync failed. Aborting setup."
    exit 1
}
echo "Dependencies synced."

# -- Step 3: Start PostgreSQL (local dev only) --
if command -v docker &>/dev/null; then
    echo "=== PostgreSQL startup (Docker) ==="
    if ! docker ps --filter "name=postgres-telco" --format '{{.Names}}' | grep -q postgres-telco; then
        docker run --name postgres-telco -e POSTGRES_DB=telco_db -e POSTGRES_USER=telco_user -e POSTGRES_PASSWORD=PASSWORD_PLACEHOLDER -p 5432:5432 -d postgres:16.15-alpine || {
            echo "Warning: Could not start PostgreSQL Docker container"
        }
    else
        echo "PostgreSQL already running."
    fi
fi

# -- Step 4: Create .env idempotently --
echo "=== .env creation ==="
FORCE_ENV_RECREATE="${FORCE_ENV_RECREATE:-0}"

if [ ! -f .env ] || [ "$FORCE_ENV_RECREATE" = "1" ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        # No .env.example — create a minimal .env
        cat > .env <<EOF
# TELECO_ENV: required — environment selector (dev, test, ci, prod)
TELECO_ENV=dev
# TELECO_SERVICE_NAME: required — name of the running service
TELECO_SERVICE_NAME=telco-platform
# TELECO_DB_URL: optional — service connection URL
TELECO_DB_URL=sqlite:///./telco_platform.db
# TELECO_DB_PASSWORD: optional — PostgreSQL application role credential placeholder
TELECO_DB_PASSWORD=PLACEHOLDER_NO_REAL_CREDENTIAL
EOF
    fi
    echo ".env created from .env.example."
else
    echo ".env already exists — preserving local values. Use FORCE_ENV_RECREATE=1 to overwrite."
fi

echo "=== Setup complete ==="
echo "Verified prerequisites, synced dependencies, started PostgreSQL (if available),"
echo "and created .env idempotently without destroying locally-supplied values."
