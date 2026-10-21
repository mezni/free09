# build-phase5: API Contract

## Overview
This feature extends the telco platform API contract layer with advanced features for scalability and enterprise readiness.

## API Contract Extensions

### Error Response Contract
- **Endpoint**: All API endpoints (`/api/v1/*`)
- **Error Format**: Standardized error JSON response
  ```json
  {
    "error_id": "<uuid>",
    "code": "<ERROR_CODE>",
    "message": "<human-readable message>",
    "timestamp": "<ISO-8601 timestamp>",
    "request_id": "<request correlator>",
    "service": "<service name>"
  }
  ```
- **Error Codes**: 
  - `VALIDATION_ERROR` (400)
  - `AUTHENTICATION_ERROR` (401)
  - `AUTHORIZATION_ERROR` (403)
  - `NOT_FOUND` (404)
  - `RATE_LIMIT_EXCEEDED` (429)

### Health Check Contract
- **Liveness Endpoint**: `GET /healthz`
  - **Response**: `{"status": "healthy"}`
  - **No authentication required**
  - **Must respond in under 100ms (NFR-022)**
  
- **Readiness Endpoint**: `GET /health`
  - **Response**: 
    ```json
    {
      "status": "healthy|unhealthy",
      "services": {
        "postgres": "healthy|unhealthy",
        "redis": "healthy|unhealthy"
      }
    }
    ```
  - **No authentication required**
  - **Must respond in under 100ms (NFR-022)**

### API Key Contract
- **Create API Key**: `POST /api/v1/api-keys`
  - **Request**: `{"person_id": "<uuid>", "scopes": ["<scope>"]}`
  - **Response**: API key object with prefix, scopes, status
  
- **Get API Key**: `GET /api/v1/api-keys/{key_prefix}`
  - **Response**: API key object with full details
  
- **List API Keys**: `GET /api/v1/api-keys`
  - **Response**: List of API key summaries
  
- **Update API Key**: `PATCH /api/v1/api-keys/{key_prefix}`
  - **Request**: `{"is_active": boolean, "scopes": ["<scope>"]}`
  - **Response**: Updated API key object
  
- **Delete API Key**: `DELETE /api/v1/api-keys/{key_prefix}`
  - **Response**: 204 No Content

### Webhook Contract
- **Subscribe to Events**: `POST /api/v1/webhooks/subscribe`
  - **Request**: `{"event_types": ["person.created", "person.updated"]}`
  - **Response**: Subscription confirmation
  
- **Unsubscribe from Events**: `POST /api/v1/webhooks/unsubscribe`
  - **Request**: `{"event_types": ["person.created"]}`
  - **Response**: Confirmation
  
- **Webhook Event**: `POST /api/v1/webhooks/event`
  - **Request**: Event payload with idempotency key
  - **Response**: Delivery confirmation

### Tracing Contract
- **Trace Context Header**: `X-Request-Id` (correlates across services)
- **Span Attributes**: `service.name`, `endpoint`, `error.type`, `error.object`
- **Propagation**: W3C Trace Context (traceparent header)

## Versioning
- API version: `/api/v1/` (current)
- API reference documentation is versioned (v1.0.0)
- Backward compatibility maintained for minor version updates
- Major version changes require deprecation period
