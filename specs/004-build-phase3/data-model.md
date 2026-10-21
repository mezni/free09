# build-phase3: Data Model

## API Contract Entities

### Person
- `id`: UUID (primary key)
- `name`: string (required, max 255)
- `email`: string (required, valid email format, unique)
- `phone`: string (optional, E.164 format)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now-on-update)

### APIKey
- `id`: UUID (primary key)
- `person_id`: UUID (foreign key → Person.id)
- `key_hash`: string (required, bcrypt-derived)
- `prefix`: string (required, 8 chars, displayed once)
- `scopes`: JSONB (optional, list of allowed endpoints)
- `is_active`: boolean (default true)
- `created_at`: datetime (auto-now)

### RateLimit
- `id`: UUID (primary key)
- `endpoint`: string (required, OpenAPI path match)
- `limit`: integer (required, requests per window)
- `window_seconds`: integer (required, default 60)
- `burst`: integer (optional, default 0)

## Relationships
- **Person → APIKey**: One-to-Many (one person can have multiple API keys)
- **APIKey → RateLimit**: Many-to-One (multiple keys can share rate limit config)
- **Person → RateLimit**: Indirect via APIKey lookup

## Indexes
- `UNIQUE` on `Person.email`
- `UNIQUE` on `APIKey.prefix`
- Index on `APIKey.person_id`
- Index on `RateLimit.endpoint`

## JSON Schemas (for OpenAPI generation)
```json
{
  "Person": {
    "type": "object",
    "required": ["name", "email"],
    "properties": {
      "id": {"type": "string", "format": "uuid"},
      "name": {"type": "string", "maxLength": 255},
      "email": {"type": "string", "format": "email"},
      "phone": {"type": "string", "pattern": "^\\+[1-9]\d{1,14}$"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "APIKey": {
    "type": "object",
    "required": ["key_hash", "prefix"],
    "properties": {
      "id": {"type": "string", "format": "uuid"},
      "person_id": {"type": "string", "format": "uuid"},
      "key_hash": {"type": "string"},
      "prefix": {"type": "string", "maxLength": 8},
      "scopes": {"type": "array", "items": {"type": "string"}},
      "is_active": {"type": "boolean"},
      "created_at": {"type": "string", "format": "date-time"}
    }
  }
}
```
