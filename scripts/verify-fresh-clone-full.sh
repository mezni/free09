#!/bin/bash
# Final fresh clone end-to-end verification — T051 [P] [Shared]
# Runtime: ~45 minutes (full environment including advanced features)

set -e

echo "=== Final Fresh Clone Verification Start ==="

# Step 1: Clone the repository
echo "[1/8] Cloning repository..."
git clone https://github.com/telco-platform/telco-si.git /tmp/final-clone
cd /tmp/final-clone

# Step 2: Initialize dependencies
echo "[2/8] Installing dependencies..."
uv sync --frozen

# Step 3: Verify Python version
echo "[3/8] Verifying Python version..."
python3 --version | grep -q "3.13" || exit 1

# Step 4: Run full setup
echo "[4/8] Running full setup..."
make setup

# Step 5: Start all services
echo "[5/8] Starting services..."
docker compose -f deploy/compose/compose.yaml up -d

# Step 6: Apply all migrations
echo "[6/8] Applying migrations..."
cd services/auth-service && alembic upgrade head
cd ../crm-service && alembic upgrade head
cd ../billing-service && alembic upgrade head
cd ../inventory-service && alembic upgrade head

# Step 7: Verify API accessibility
echo "[7/8] Verifying API accessibility..."
sleep 5
curl -s http://localhost:8000/healthz | grep -q "healthy" || exit 1

# Step 8: Run full test suite
echo "[8/8] Running test suite..."
uv run pytest tests/ -x --tb=short

echo "=== Final Fresh Clone Verification Complete (under 45 min) ==="
