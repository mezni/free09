# build-phase3: Research

## Decisions

### Decision R-030: OpenAPI 3.1 over 2.0
- **Rationale**: Better tooling, improved type generation, enhanced security schems
- **Alternatives considered**: OpenAPI 2.0, AsyncAPI (for event-driven only)
- **Decision**: OpenAPI 3.1 for all new APIs; backward compatibility layer for legacy 2.0 specs

### Decision R-031: Python SDK via OpenAPI Generator
- **Rationale**: Mature, actively maintained, supports Pydantic v2 model generation
- **Alternatives considered**: FastAPI auto-docs only, manual SDK, drf-spectacular
- **Decision**: Use `openapi-generator` with `pydantic` generator for Python SDK

### Decision R-032: TypeScript SDK via OpenAPI Generator
- **Rationale**: Consistent with Python approach, good TypeScript support
- **Alternatives considered**: tsoa, manual types, zod-only validation
- **Decision**: Use `openapi-generator` with `typescript-axios` generator

### Decision R-033: Pydantic v2 for Request Validation
- **Rationale**: Native OpenAPI schema generation, type safety, validation composition
- **Alternatives considered**: Marshmallow, Cerberus, manual validation
- **Decision**: Pydantic v2 as validation layer, auto-generates from OpenAPI specs

### Decision R-034: API Gateway via Traefik
- **Rationale**: Lightweight, dynamic config, good rate limiting, Docker-native
- **Alternatives considered**: NGINX, Envoy, Kong (too heavy for MVP)
- **Decision**: Traefik with rate limit middleware for API gateway

### Decision R-035: OAuth2.1 Authentication
- **Rationale**: Modern auth standard, revocation support, JWT best practices
- **Alternatives considered**: OAuth2.0, JWT-only, simple API keys
- **Decision**: OAuth2.1 with PKCE for first-party clients, auth codes for browser flows
