# API Reference — build-phase3: API Contract Layer

## Overview
The Telco Platform API Contract Layer provides specification-first designed RESTful endpoints for person management, authentication, and service communication.

## Base Information
- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **Specification**: [OpenAPI 3.1 YAML](/specs/004-build-phase3/openapi/person-management.yaml)
- **Authentication**: OAuth2.1 Bearer tokens

## Authentication
All API endpoints (except `/healthz`) require valid OAuth2.1 bearer tokens.

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
**Request Body**: APIKeyCreate (person_id, scopes*)  
**Security**: bearerAuth (admin scope required)  
**Responses**:
- `201`: API key created - APIKeyResponse object
- `400`: Bad request - invalid input
- `403`: Forbidden - insufficient scopes

### Get API Key
```
GET /api/v1/api-keys/{key_id}
```
**Summary**: Retrieve an API key by ID  
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
PATCH /api/v1/api-keys/{key_id}
```
**Summary**: Update an API key (activate/deactivate, change scopes)  
**Request Body**: partial APIKeyResponse  
**Security**: bearerAuth (or key's own prefix)  
**Responses**:
- `200`: API key updated - APIKeyResponse object
- `404`: API key not found

### Delete API Key
```
DELETE /api/v1/api-keys/{key_id}
```
**Summary**: Delete/soft-delete an API key  
**Security**: bearerAuth (or key's own prefix)  
**Responses**:
- `204`: API key deleted (no content)
- `404`: API key not found

## Rate Limiting
- **Default limit**: 100 requests per 1 second
- **Burst allowance**: 10 requests
- **Per-API-key limits**: Configurable via Traefik middleware
- **Health endpoint**: `/healthz` - no rate limiting, no authentication

## Error Responses
All error responses follow a standardized format:

```json
{
  "detail": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: 400 - Input validation failed
- `AUTHENTICATION_ERROR`: 401 - Missing or invalid token
- `AUTHORIZATION_ERROR`: 403 - Insufficient scopes
- `NOT_FOUND`: 404 - Resource not found
- `RATE_LIMIT_EXCEEDED`: 429 - Too many requests

## SDKs
- **Python SDK**: `person_api.PersonApiClient` - type-safe client with async support
- **TypeScript SDK**: `PersonApiClient` class with axios-based client and interceptors

## Versioning
- API version is embedded in the URL path: `/api/v1/`
- Backward compatibility maintained for minor version updates
- Major version changes require deprecation period

## Webhooks
- `person.created`: Fired when a new person is created
- `person.updated`: Fired when a person is updated
- `person.deleted`: Fired when a person is deleted

## Version History
- **v1.0.0** (current): Initial release with person management, auth, and API key features
