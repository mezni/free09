# ADR-0001: Centralized PostgreSQL with Schema Ownership

- Status: Accepted
- Date: 2026-10-21
- Decision owners: Architecture and database owners

## Context

The initial platform contains four domain-specific FastAPI services. The project
needs manageable local development and strong relational data integrity, while
retaining explicit service boundaries.

The services are `auth-service`, `crm-service`, `billing-service`, and
`inventory-service` (Constitution Article II.1), and each owns exactly one
domain (Article II.2).

## Decision drivers

- Manageable local development and a single operational story at the start.
- Strong relational integrity for the data the platform owns.
- Explicit, enforceable service boundaries rather than an implicit coupling.
- The ability to move a service to its own database later without a rewrite of
  its domain logic.

## Options considered

1. **One database with schema ownership (selected)** — benefits: one
   deployment to operate, full relational integrity across the platform, and
   each domain's tables are isolated behind its own schema and role. Costs:
   a shared failure and capacity domain, and separate schemas do not equal
   infrastructure isolation. Risks: cross-domain workflows need explicit
   consistency and recovery design.
2. **A separate database per service** — benefits: true infrastructure
   isolation and independent scaling and availability. Costs: four deployments
   to run, no cross-domain relational integrity, and every cross-domain
   question becomes a distributed transaction. Risks: premature distribution
   of a system that has not yet proven its domain boundaries.
3. **One shared schema with unrestricted access** — benefits: the simplest
   possible arrangement. Costs: no enforced ownership at all, so any service
   can read and write any domain's data. Risks: exactly the silent coupling
   the constitution's ownership article exists to prevent.

## Decision

Use one PostgreSQL deployment and database initially, with separate schemas and
restricted credentials for `auth`, `crm`, `billing`, and `inventory`. Each
service owns writes to its schema. Cross-service data access uses documented
APIs by default. Any cross-schema constraints, views, or direct reads require
explicit review and documentation.

## Consequences

- Positive:
  - Lower initial operational complexity.
  - A straightforward local environment.
  - Clear logical ownership boundaries.
  - Strong database transactions within a schema.
- Negative:
  - A shared database failure and capacity domain.
  - Potential cross-service coupling.
  - Separate schemas do not equal infrastructure isolation.
- Risks and mitigations:
  - Cross-domain workflows still need explicit consistency and recovery
    design. Mitigation: every cross-schema access is reviewed and documented
    before it is introduced.

## Follow-up actions

- [x] Record the schema and role layout in `deploy/compose/compose.yaml`.
- [x] Give each service its own role and schema in the local topology.

## Revisit triggers

Revisit if service teams, availability requirements, scaling, regulatory
constraints, or deployment independence require separate database instances.
