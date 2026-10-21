# build-phase3: Quickstart

## Prerequisites
- Docker and Docker Compose installed
- Python 3.13+ (via `.python-version`)
- `uv` package manager (via `uv tool install openapi-generator`)
- Node.js 20+ (for TypeScript SDK generation)

## Setup

### 1. Clone and Initialize
```bash
git clone <repo-url>
cd telco-si
uv sync
```

### 2. Generate OpenAPI Spec
```bash
# Ensure .env is sourced
cp .env.example .env  # adjust AUTH_PREFIX, RATE_LIMIT_WINDOW

# Generate Python SDK
make sdk-python

# Generate TypeScript SDK  
make sdk-typescript
```

### 3. Start Services
```bash
docker compose up -d
# Services start: PostgreSQL, Traefik gateway
```

### 4. Apply Migrations
```bash
# Auth service
cd services/auth-service
alembic upgrade head

# CRM service
cd services/crm-service
alembic upgrade head
```

### 5. Verify
```bash
# Check Traefik dashboard at http://localhost:8080
# Test health endpoint
curl http://localhost:8000/healthz

# Test person API
curl -H "Authorization: Bearer <jwt-token>" http://localhost:8000/api/v1/person
```

## SDK Usage

### Python
```python
from person_api import PersonApiClient

client = PersonApiClient(
    base_url="http://localhost:8000",
    auth_header={"Authorization": "Bearer <jwt>"}
)

# Create person
person = client.create_person(name="John Doe", email="john@example.com")
```

### TypeScript
```typescript
import { PersonApiClient } from "./sdk/person-api";

const client = new PersonApiClient(
  "http://localhost:8000",
  { authHeader: "Bearer <jwt>" }
);

// Create person
const person = await client.createPerson({ name: "John Doe", email: "john@example.com" });
```
