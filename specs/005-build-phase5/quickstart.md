# build-phase5: Quickstart

## Prerequisites
- Docker and Docker Compose installed
- Python 3.13+ (via `.python-version`)
- `uv` package manager
- OpenTelemetry Collector (or Jaeger) available
- Existing build-phase1 through build-phase4 environment running

## Setup

### 1. Ensure Prior Phases Are Complete
```bash
# Verify all prior phases are implemented
make verify

# Or verify individually
make docker-up  # Start all services
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure OpenTelemetry
```bash
# Ensure OpenTelemetry collector is running
# Or Jaeger is available for trace visualization
cp .env.example .env  # Configure OTel collector endpoint if needed
```

### 4. Apply Migrations and Extensions
```bash
# Apply phase 5 database extensions
cd services/auth-service
alembic upgrade head

# Or run the phase 5 migration script
make migrate-phase5
```

### 5. Start Services
```bash
docker compose -f deploy/compose/compose.yaml up -d
# Wait for services to be ready
sleep 10
```

### 6. Verify Endpoints
```bash
# Health checks
curl -s http://localhost:8000/healthz
# Expected: "healthy"

curl -s http://localhost:8000/health
# Expected: detailed health status

# Person API (phase 3 functionality)
curl -H "Authorization: Bearer <jwt-token>" http://localhost:8000/api/v1/person

# OpenTelemetry verification
# Check Jaeger UI at http://localhost:14268
# Or Prometheus metrics at http://localhost:9090
```

## SDK Usage (Phase 5 Extensions)

### Python - Error Tracking
```python
import requests
import json

# Report error to tracking system
def report_error(service, endpoint, error_type, message, request_id=None):
    payload = {
        "service": service,
        "endpoint": endpoint,
        "error_type": error_type,
        "message": message,
        "request_id": request_id,
        "timestamp": __import__('datetime').utcnow().isoformat()
    }
    requests.post("http://localhost:8000/track-error", json=payload)
```

### Python - API Key Management
```python
from auth_service.sdk.person_api import PersonApiClient

client = PersonApiClient(
    base_url="http://localhost:8000",
    auth_header={"Authorization": "Bearer <jwt>"}
)

# Create API key
key = client.create_api_key(
    person_id="<person-uuid>",
    scopes=["read", "write"]
)

# List API keys
keys = client.list_api_keys()

# Update API key status
updated = client.update_api_key(key_prefix=key["prefix"], is_active=False)

# Delete API key
deleted = client.delete_api_key(key_prefix=key["prefix"])
```

### TypeScript - Webhook Subscription
```typescript
import { PersonApiClient } from "./sdk/person-api";

// Subscribe to webhook events
const client = new PersonApiClient(
  "http://localhost:8000",
  { authHeader: "Bearer <jwt>" }
);

await client.subscribeWebhooks(["person.created", "person.updated"]);

// Unsubscribe from events
await client.unsubscribeWebhooks(["person.created"]);
```

### Verification Checklist
- [ ] Health check endpoints respond under 100ms
- [ ] OpenTelemetry traces visible in collector/Jaeger
- [ ] Error tracking receives errors with request ID correlation
- [ ] API key CRUD operations functional
- [ ] Webhook subscription and event processing
- [ ] Performance benchmarks run (compare to phase 3 baseline)
