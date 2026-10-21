#!/usr/bin/env bash
set -euo pipefail
# setup.sh — Phase 1 setup path.
# Verifies prerequisites, syncs dependencies, starts PostgreSQL, and creates .env
# idempotently without destroying locally-supplied values.

# -- Step 1: Verify prerequisites --
echo "=== Prerequisite verification ==="
bash ci/check_prerequisites.py || {
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
        docker run --name postgres-telco -e POSTPOSTGRES_DB=telco_db -e POSTGRES_USER=telco_user -e POSTGRES_PASSWORD=PASSWORD_PLACEHOLDER -p 5432:5432 -d postgres:16.15-alpine || {
            echo "Warning: Could not start PostgreSQL Docker container"
        }
    else
        echo "PostgreSQL already running."
    fi
fi

# -- Step 4: Create .env idempotently --
echo "=== .env creation ==="
if [ ! -f .env ] || [ "$FORCE_ENV_RECREATE" = "1" ]; then
    # Start from .env.example placeholders, then overlay any existing .env values
    if [ -f .env.example ]; then
        # Use envchain or simple overlay: start with .env.example, then preserve
        # any locally-supplied values (vars already in .env that we should keep)
        if [ -f .env ]; then
            # overlay existing .env values on top of .env.example placeholders
            grep -v '^DB_PASSWORD=' .env > /tmp/.env.overlay 2>/dev/null || true
            # Keep DB_PASSWORD from existing .env if present
            if grep -q 'DB_PASSWORD=' /tmp/.env.overlay 2>/dev/null; then
                echo "DB_PASSWORD_OVERLAY=$(grep '^DB_PASSWORD=' /tmp/.env.overlay | cut -d= -f2)" > .env
            else
                # Use placeholder from .env.example
                DB_PASSWORD=PLACEHOLDER_NO_REAL_CREDENTIAL
                echo "DB_PASSWORD=${DB_PASSWORD}" > .env
            fi
            # Copy all other vars from .env.example
            grep -v '^DB_PASSWORD=' .env.example > .env 2>/dev/null || true
            # Now overlay the preserved values
            if [ -f /tmp/.env.overlay ]; then
                cat /tmp/.env.overlay >> .env
            fi
        else
            # No existing .env — just copy .env.example
            cp .env.example .env
        fi
    else
        # No .env.example — create minimal .env
        cat > .env <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telco_db
DB_USER=telco_user
DB_PASSWORD=PLACEHOLDER_NO_REAL_CREDENTIAL
EOF
    fi
    echo ".env created/updated idempotently."
else
    echo ".env already exists — preserving local values. Use FORCE_ENV_RECREATE=1 to overwrite."
fi

echo "=== Setup complete ==="
echo "Verified prerequisites, synced dependencies, started PostgreSQL (if available),"
echo "and created .env idempotently without destroying locally-supplied values."
