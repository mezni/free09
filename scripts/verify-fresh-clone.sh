#!/bin/bash
# Fresh clone end-to-end verification — T032 [P] [US1]
# Runtime: ~30 minutes

set -e

echo "=== Fresh Clone Verification Start ==="

# Step 1: Clone the repository
echo "[1/6] Cloning repository..."
git clone https://github.com/telco-platform/telco-si.git /tmp/fresh-clone
cd /tmp/fresh-clone

# Step 2: Initialize dependencies
echo "[2/6] Installing dependencies..."
uv sync

# Step 3: Verify Python version
echo "[3/6] Verifying Python version..."
python3 --version | grep -q "3.13" || exit 1

# Step 4: Run setup
echo "[4/6] Running setup..."
make setup

# Step 5: Start services
echo "[5/6] Starting services..."
docker compose -f deploy/compose/compose.yaml up -d postgres
docker compose -f deploy/compose/compose.yaml up -d

# Step 6: Verify API accessibility
echo "[6/6] Verifying API accessibility..."
sleep 5
curl -s http://localhost:8000/healthz | grep -q "healthy" || exit 1

echo "=== Fresh Clone Verification Complete (under 30 min) ==="
