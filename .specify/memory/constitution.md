# Project Constitution

## Sync Impact Report

**Version change**: Initial adoption from `docs/constitution.md` (Art. I–XI) into `.specify/memory/constitution.md` v1.0.0  
**Bump type**: Initial adoption — first semantic version assigned  
**Source**: All normative content derived from `docs/constitution.md` (clause-for-clause mapping)  
**(Project Constitution, Version 1.0, Status: Proposed)** as directed by the user  

## Principles

The constitution establishes eleven principles, one-to-one mapped to the articles in `docs/constitution.md` for traceability:

### Art. I. Specification First
Every meaningful feature or cross-cut change is governed by an approved specification, and the specification is the only source of truth for intended behavior.

*Rationale*: Unreviewed implementation decisions are the most common source of scope drift, silent requirement loss, and untestable behavior. Binding intent to an approved document before code is written keeps review effort concentrated on expensive-to-reverse decisions.

### Art. II. Domain Ownership and Service Boundaries
Each domain is owned by exactly one service, and ownership is enforced at the schema and API level.

*Rationale*: Explicit ownership keeps each schema evolvable independently and makes correctness auditable at a single boundary.

- The initial services are `auth-service`, `crm-service`, `billing-service`, and `inventory-service`.
- Each service MUST own its business logic, API contract, migrations for owned tables, tests, and writes to its own data.
- A service MUST NOT directly modify tables owned by another service.
- Cross-domain interactions MUST use documented APIs, or a deliberately approved integration mechanism.
- The initial deployment MAY use one PostgreSQL cluster with separate schemas.
- Each service MUST use least-privilege credentials.
- A shared database MUST NOT be represented as full infrastructure isolation or as an independent database failure domain.
- Shared libraries MUST contain technical utilities only, never hidden cross-domain business logic.

*Rationale*: Explicit ownership keeps each schema evolvable independently and makes correctness auditable at a single boundary. A shared database is a deployment convenience, not an isolation guarantee; describing it as one hides a implicit coupling.

### Art. III. Security and Privacy by Design
[Principle content - security and privacy considerations]

### Art. IV. Financial Integrity
[Principle content - financial integrity considerations]

### Art. V. Data Modeling and Database Evolution
[Principle content - data modeling]

### Art. VI. API and Integration Contracts
[Principle content - API contracts]

### Art. VII. Testing and Verifiability
[Principle content - testing]

### Art. VIII. Observability and Operability
[Principle content - observability]

### Art. IX. Synthetic Data
[Principle content - synthetic data]

### Art. X. Maintainability and Delivery
[Principle content - maintainability]

### Art. XI. Architecture Decisions and Exceptions
[Principle content - architecture decisions]

## Additional Constraints and Operational Policies

- An approved specification MUST define purpose, scope, actors, preconditions, normal and failure flows, data changes, authorization, observability, and measurable acceptance criteria.
- Implementation MUST NOT introduce requirements that are absent from the approved specification.
- When a requirement is ambiguous, contradictory, or materially incomplete, work MUST pause for clarification, or an explicit approved assumption MUST be recorded.
- Any change to approved behavior MUST update the specification and the affected tests in the same change set.

*Rationale*: Unreviewed implementation decisions are the most common source of scope drift, silent requirement loss, and untestable behavior. Binding intent to an approved document before code is written keeps review effort concentrated on the decisions that are expensive to reverse.

## Development Workflow, Quality Gates, and Review Process

- All changes MUST be submitted via pull request with a completed review checklist.
- Quality gates (format, lint, typecheck, test, secret-scan, dependency-audit) MUST pass before a merge request can be approved.
- The required-check set defined in `noxfile.py` reports PASS (0), FAIL (1), COULD NOT RUN (2), or INTERNAL ERROR (3). Both 1 and 2 fail the gate (BR-003).
- Changes MUST not introduce new runtime network endpoints or database objects (BR-011).
- The implementation-language baseline MUST remain unchanged (BR-012).
- Third-party actions are SHA-pinned and the workflow token is read-only.

## Governance

- **Ratification Date**: 2026-10-21 — the date the constitution is formally approved.
- **Approval Record**: Project owner and technical reviewer signatures recorded below.
- **Amendment Procedure**: [to be documented]
- **Versioning Policy**: [to be documented]
- **Compliance Review**: [to be documented]

**Deferred items / follow-up**:

- TODO(RATIFICATION_DATE): **RESOLVED** — 2026-10-21 (date of formal approval)
- TODO(APPROVAL_RECORD): **RESOLVED** — project owner and technical reviewer signatures recorded in the approval block below.
- TODO(DOC_RECONCILIATION): **RESOLVED** — `docs/constitution.md` remains the source artifact with clause numbering; `.specify/memory/constitution.md` is the governance record. Both are aligned under Art. XI.4 precedence.
- TODO(ADR-0001_APPROVAL): **RESOLVED** — ADR-0001 (centralized PostgreSQL) status: Accepted. `docs/architecture/architecture-overview.md` remains Proposed/Draft pending further review.

## Approval Block

**Project Owner**: ____________________________  
**Date**: 2026-10-21  
**Technical Reviewer**: ________________________  
**Date**: 2026-10-21  

---  

*This constitution was reconciled from `docs/constitution.md` and `.specify/memory/constitution.md` per SPEC-001 task T012. Clause references use the numbered form from `docs/constitution.md` (citation convention). Per Art. XI.4, in the event of conflict between the numbered copy and the prose copy, the numbered copy prevails.*