# API Reference

## Overview
The Telco Platform exposes two API surfaces:

- The **API contract layer** (build-phase3), documented here and specified in
  `specs/004-build-phase3/`: person management, authentication, and API key
  management.
- The **cross-service application** (build-phase8), documented in
  [Analytics endpoints](#analytics-endpoints-build-phase8) below: the advanced
  analytics endpoints.

The contract layer is served by `src/main.py`, together with the phase-5
health probes, API key routes and webhook routes. The analytics endpoints are
also served by `src/main.py`.

## Base Information
- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Specification**: [build-phase3 API contract layer](../specs/004-build-phase3/spec.md)
- **Authentication**: OAuth2.1 Bearer tokens; health probes and webhook
  ingestion use their own mechanisms described below.

## Authentication
All endpoints under `/api/v1` require valid OAuth2.1 bearer tokens, except
the health probe (`/api/v1/health`) and webhook ingestion (HMAC signature).
The root health probes `/healthz`, `/readyz` and `/health` are unauthenticated.

### Token Format
```
Authorization: Bearer <jwt-token>
```

### Scopes
- `openid`: OpenID Connect core
- `profile`: User profile information
- `email`: Email address access
- `api_keys`: API key management

## Endpoints

### Person Management

#### List Persons
```
GET /api/v1/person
```
**Summary**: List all persons  
**Operation ID**: listPersons  
**Security**: bearerAuth  
**Responses**:
- `200`: Successful response - array of Person objects
- `400`: Bad request - validation error

#### Create Person
```
POST /api/v1/person
```
**Summary**: Create a new person  
**Operation ID**: createPerson  
**Request Body**: PersonCreate (name, email, phone*)  
**Security**: bearerAuth  
**Responses**:
- `201`: Person created - Person object
- `400`: Bad request - validation error (e.g., invalid email format, phone not in E.164)

#### Get Person
```
GET /api/v1/person/{person_id}
```
**Summary**: Get a person by UUID  
**Operation ID**: getPerson  
**Parameters**: 
- `person_id` (path, required, UUID format)
**Security**: bearerAuth  
**Responses**:
- `200`: Successful response - Person object
- `404`: Person not found

#### Update Person
```
PUT /api/v1/person/{person_id}
```
**Summary**: Update a person  
**Operation ID**: updatePerson  
**Request Body**: PersonUpdate (name*, email*)  
**Security**: bearerAuth  
**Responses**:
- `200`: Person updated - Person object
- `400`: Bad request - validation error

#### Delete Person
```
DELETE /api/v1/person/{person_id}
```
**Summary**: Delete a person  
**Operation ID**: deletePerson  
**Security**: bearerAuth  
**Responses**:
- `204`: Person deleted (no content)
- `404`: Person not found

## API Key Management

### Create API Key
```
POST /api/v1/api-keys
```
**Summary**: Create a new API key

**Request Body**: APIKeyCreate (`person_id`, `scopes`)

**Security**: bearerAuth (admin scope required)
**Responses**:
- `201`: API key created — includes the one-time plaintext `key`
- `400`: Bad request - invalid input or unknown scope
- `403`: Forbidden - insufficient scopes

The plaintext key is returned only in this response. Subsequent reads return
the key prefix and metadata, never the secret.

### Get API Key
```
GET /api/v1/api-keys/{prefix}
```
**Summary**: Retrieve an API key by prefix

**Security**: bearerAuth (or key's own prefix)
**Responses**:
- `200`: API key found - APIKeyResponse object
- `404`: API key not found

### List API Keys
```
GET /api/v1/api-keys
```
**Summary**: List all API keys for a person  
**Security**: bearerAuth  
**Responses**:
- `200`: Successful response - array of APIKeyResponse objects

### Update API Key
```
PATCH /api/v1/api-keys/{prefix}
```
**Summary**: Update an API key (activate/deactivate, change scopes)  
**Request Body**: partial APIKeyResponse  
**Security**: bearerAuth (or key's own prefix)  
**Responses**:
- `200`: API key updated - APIKeyResponse object
- `404`: API key not found

### Delete API Key
```
DELETE /api/v1/api-keys/{prefix}
```
**Summary**: Revoke an API key

**Security**: bearerAuth (or key's own prefix)
**Responses**:
- `204`: API key revoked (no content)
- `404`: API key not found

## Health Probes

| Endpoint | Purpose | Response |
|---|---|---|
| `GET /healthz` | Liveness | `200` with `status`, `service`, `version` |
| `GET /readyz` | Readiness | `200` when ready; `503` when dependencies are unavailable |
| `GET /health` | Readiness alias | Same body and status as `/readyz` |
| `GET /api/v1/health` | Versioned readiness | Delegates to `/readyz` |

The probes are unauthenticated and are not rate limited. A failing readiness
probe returns `503 Service Unavailable`.

## Rate Limiting
- **Default limit**: 100 requests per 1 second
- **Burst allowance**: 10 requests
- **Per-API-key limits**: Configurable via Traefik middleware
- **Health endpoint**: `/healthz` - no rate limiting, no authentication

## Error Responses
All error responses follow the canonical envelope:

```json
{
  "code": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "service": "crm-service",
  "request_id": "3f8c1d6e-...",
  "error_id": "err-20261022-4b83b511",
  "timestamp": "2026-10-22T20:05:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: 400 - Input validation failed
- `INVALID_SIGNATURE`: 401 - Webhook signature verification failed
- `AUTHENTICATION_ERROR`: 401 - Missing or invalid token
- `AUTHORIZATION_ERROR`: 403 - Insufficient scopes
- `NOT_FOUND`: 404 - Resource not found
- `RATE_LIMIT_EXCEEDED`: 429 - Too many requests
- `INTERNAL_SERVER_ERROR`: 500 - Unhandled server error
- `SERVICE_UNAVAILABLE`: 503 - Readiness check failed or webhook secret missing

## SDKs
- **Python SDK**: `person_api.PersonApiClient` - type-safe client with async support
- **TypeScript SDK**: `PersonApiClient` class with axios-based client and interceptors

## Versioning
- API version is embedded in the URL path: `/api/v1/`
- Backward compatibility maintained for minor version updates
- Major version changes require deprecation period

## Webhooks

Supported events: `person.created`, `person.updated`, `person.deleted`.

### Subscribe
`POST /api/v1/webhooks/subscribe`

**Request Body**: `{"event_types": ["person.created"]}`

**Responses**: `200` with the active subscription set; `400` for an unknown
event type.

### Unsubscribe
`POST /api/v1/webhooks/unsubscribe`

**Request Body**: `{"event_types": ["person.created"]}`

**Responses**: `200` with the remaining subscription set.

### Ingest an event
`POST /api/v1/webhooks/event`

**Headers**:
- `X-Webhook-Signature`: `sha256=<hex HMAC-SHA256 of the raw body>`
- `Idempotency-Key`: optional client-supplied deduplication key

**Request Body**: `{"event_type": "person.created", ...}`

**Responses**:
- `202`: Event accepted — `{"event": {...}, "duplicate": false}`
- `202` with `duplicate: true`: The idempotency key was already processed
- `400`: Unknown event type
- `401`: Invalid or missing signature
- `503`: `TELECO_WEBHOOK_SECRET` is not configured

Delivery is at-least-once with bounded retries. The signature covers the raw
request body exactly as sent, so clients must sign the serialized bytes rather
than a re-encoded object.

## Analytics endpoints (build-phase8)

Served by the application in `src/`, mounted under `/api/v1`. The interactive
schema is at `/docs` when the application is running.

### List analytics events
`GET /api/v1/analytics/events`

Query parameters: `limit` (default 100), `offset` (default 0), and an
optional `service` filter.

```json
[
  {
    "event_id": "8f14e45f-ceea-467a-9d0e-2f2b7a1c9d31",
    "event_type": "page_view",
    "user_id": "b7d2f0c4-...",
    "service": "web-frontend",
    "endpoint": "/dashboard",
    "timestamp": "2026-10-21T10:00:00Z",
    "metadata": {"page_id": "abc123"}
  }
]
```

Responses: `200` with the event list, `422` for an invalid query parameter.

### Get an analytics event
`GET /api/v1/analytics/events/{event_id}`

Responses: `200` with the event, `404` when the event does not exist.

### Create an analytics event
`POST /api/v1/analytics/events`

Request body: `event_type`, `user_id`, `service`, `endpoint`, `timestamp` and
`metadata`. `event_id` and `timestamp` are generated by the server.

Responses: `201` with the created event, `422` for a body that fails
validation.

### Planned endpoints

The remaining build-phase8 endpoints are specified but not implemented, and
return `404` until their tasks are complete:

| Endpoint | Requirement | State |
|---|---|---|
| `GET /api/v1/ai-model-metrics` | FR-071 | Not implemented |
| `GET /api/v1/admin/*` | FR-072 | Not implemented |
| `POST`/`PATCH /api/v1/partner-integrations` | FR-073 | Not implemented |
| `POST`/`GET /api/v1/compliance-reports` | FR-074 | Not implemented |
| `POST`/`PATCH /api/v1/feature-flags` | FR-075 | Not implemented |

### Platform endpoints

`GET /api/v1/health` returns `{"status": "healthy", "service": "telco-platform"}`.
`GET /api/v1/` returns the service name, version and the documentation path.
Both are unauthenticated.

## Observability Configuration

| Variable | Purpose | Default |
|---|---|---|
| `TELECO_OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP/HTTP collector endpoint | unset (tracing exports are disabled) |
| `TELECO_WEBHOOK_SECRET` | HMAC secret for webhook ingestion | unset (ingestion returns `503`) |

When the OTLP endpoint is unset, spans are still created and propagated but
not exported. The optional `deploy/compose/observability.yaml` overlay runs
Jaeger with OTLP/HTTP ingestion on port `4318` and its UI on port `16686`:

```bash
docker compose -f deploy/compose/compose.yaml \
  -f deploy/compose/observability.yaml up -d
```

## Version History
- **v1.2.0** (current): Documented the phase-5 health probes, webhook API,
  API key prefix behaviour, canonical error envelope and observability
  configuration; the contract layer is now served by the application
- **v1.1.0**: Added the build-phase8 analytics endpoints and the platform
  endpoints; recorded which build-phase8 endpoints are not yet implemented
- **v1.0.0**: Initial release with person management, auth, and API key features
