# ADR-0001: Centralized PostgreSQL with Schema Ownership

- Status: Implemented
- Date: YYYY-MM-DD
- Decision owners: Architecture and database owners

## Context

The initial platform contains four domain-specific FastAPI services. The project needs manageable local development and strong relational data integrity, while retaining explicit service boundaries.

## Decision

Use one PostgreSQL deployment/database initially, with separate schemas and restricted credentials for `auth`, `crm`, `billing`, and `inventory`. Each service owns writes to its schema. Cross-service data access uses documented APIs by default. Any cross-schema constraints, views, or direct reads require explicit review and documentation.

## Alternatives considered

1. Separate database per service.
2. One shared schema with unrestricted access.
3. One database with schema ownership.

## Consequences

**Benefits**
- Lower initial operational complexity.
- Straightforward local environment.
- Clear logical ownership boundaries.
- Strong database transactions within a schema.

**Costs and risks**
- Shared database failure and capacity domain.
- Potential cross-service coupling.
- Separate schemas do not equal infrastructure isolation.
- Cross-domain workflows still need explicit consistency and recovery design.

## Revisit when

Revisit if service teams, availability requirements, scaling, regulatory constraints, or deployment independence require separate database instances.
