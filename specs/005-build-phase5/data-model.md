# build-phase5: Data Model

## API Contract Entities (extends phase 3 model)

### ErrorInfo
- `error_id`: UUID (primary key)
- `service`: string (service name generating the error)
- `endpoint`: string (API endpoint path)
- `error_type`: string (classification: validation, authentication, not_found, server_error, rate_limit)
- `message`: string (human-readable error message)
- `request_id`: UUID (correlates with request tracing)
- `timestamp`: datetime (auto-now)
- `details`: JSONB (optional structured error details)

### WebhookEvent
- `event_id`: UUID (primary key)
- `event_type`: string (e.g., "person.created", "person.updated", "person.deleted", "api_key.created")
- `endpoint`: string (webhook endpoint URL)
- `payload`: JSONB (original event data)
- `status`: string (delivered, failed, retrying)
- `delivery_attempts`: integer (default 0)
- `max_delivery_attempts`: integer (default 3)
- `idempotency_key`: UUID (optional, for deduplication)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now-on-update)

### WebhookDelivery
- `delivery_id`: UUID (primary key)
- `webhook_event_id`: UUID (foreign key → WebhookEvent.id)
- `attempt_number`: integer (1, 2, 3...)
- `status`: string (success, failed, retrying)
- `response_code`: integer (HTTP status code if available)
- `response_body`: JSONB (optional, truncated)
- `attempted_at`: datetime (auto-now)

## Relationships
- **ErrorInfo → WebhookEvent**: Many-to-Many (multiple errors can relate to multiple events via WebhookDelivery; an event can have multiple error associations)
- **WebhookEvent → WebhookDelivery**: One-to-Many (one event can have multiple delivery attempts)
- **Person → APIKey**: One-to-Many (inherited from phase 3, one person can have multiple API keys)
- **APIKey → WebhookEvent**: Many-to-Many (multiple API keys can subscribe to multiple event types, via subscription model - not modeled explicitly here but noted)

## Indexes
- `UNIQUE` on `ErrorInfo.error_id`
- `UNIQUE` on `WebhookEvent.event_id`
- Index on `ErrorInfo.service`
- Index on `ErrorInfo.endpoint`
- Index on `WebhookEvent.endpoint`
- Index on `WebhookEvent.status`
- Index on `WebhookEvent.created_at`
- Index on `WebhookDelivery.webhook_event_id`
- Index on `WebhookDelivery.status`

## JSON Schemas (for OpenAPI generation)

```json
{
  "ErrorInfo": {
    "type": "object",
    "required": ["service", "endpoint", "error_type", "message", "request_id"],
    "properties": {
      "error_id": {"type": "string", "format": "uuid"},
      "service": {"type": "string"},
      "endpoint": {"type": "string"},
      "error_type": {"type": "string"},
      "message": {"type": "string"},
      "request_id": {"type": "string", "format": "uuid"},
      "timestamp": {"type": "string", "format": "date-time"},
      "details": {"type": "object"}
    }
  },
  "WebhookEvent": {
    "type": "object",
    "required": ["event_type", "endpoint", "payload", "status"],
    "properties": {
      "event_id": {"type": "string", "format": "uuid"},
      "event_type": {"type": "string"},
      "endpoint": {"type": "string"},
      "payload": {"type": "object"},
      "status": {"type": "string"},
      "delivery_attempts": {"type": "integer"},
      "max_delivery_attempts": {"type": "integer"},
      "idempotency_key": {"type": "string", "format": "uuid"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "WebhookDelivery": {
    "type": "object",
    "required": ["webhook_event_id", "attempt_number", "status"],
    "properties": {
      "delivery_id": {"type": "string", "format": "uuid"},
      "webhook_event_id": {"type": "string", "format": "uuid"},
      "attempt_number": {"type": "integer"},
      "status": {"type": "string"},
      "response_code": {"type": "integer"},
      "response_body": {"type": "object"},
      "attempted_at": {"type": "string", "format": "date-time"}
    }
  }
}
```
