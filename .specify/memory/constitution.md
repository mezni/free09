# Project Constitution

**Version**: 1.0.0
**Status**: Ratified
**Ratified**: 2026-10-21
**Last amended**: 2026-10-21
**Governance record**: this document — see Art. XI.4

## Sync Impact Report

**Version change**: Initial adoption from `docs/constitution.md` (Art. I–XI) into `.specify/memory/constitution.md` v1.0.0  
**Bump type**: Initial adoption — first semantic version assigned  
**Source**: All normative content derived from `docs/constitution.md` (clause-for-clause mapping)  
**(Project Constitution, Version 1.0, Status: Ratified)** — ratified 2026-10-21, as recorded in the approval block below  

## Principles

The constitution establishes eleven principles, one-to-one mapped to the articles in `docs/constitution.md` for traceability:

### Art. I. Specification First
Every meaningful feature or cross-cut change is governed by an approved specification, and the specification is the only source of truth for intended behavior.

*Rationale*: Unreviewed implementation decisions are the most common source of scope drift, silent requirement loss, and untestable behavior. Binding intent to an approved document before code is written keeps review effort concentrated on expensive-to-reverse decisions.

- I.1 A specification MUST reach `Approved` status before implementation of the behaviour it describes begins.
- I.2 A specification MUST define purpose, scope, actors, preconditions, normal and failure flows, data changes, authorization, observability, and measurable acceptance criteria.
- I.3 Implementation MUST NOT introduce a requirement that the approved specification does not contain.
- I.4 Any change to approved behaviour MUST update the specification and the affected tests in the same change set.
- I.5 Where a requirement is ambiguous, contradictory, or materially incomplete, work MUST pause for clarification, or an explicit approved assumption MUST be recorded.

### Art. II. Domain Ownership and Service Boundaries
Each domain is owned by exactly one service, and ownership is enforced at the schema and API level.

*Rationale*: Explicit ownership keeps each schema evolvable independently and makes correctness auditable at a single boundary.

- II.1 The initial services are `auth-service`, `crm-service`, `billing-service`, and `inventory-service`.
- II.2 Each service MUST own its business logic, API contract, migrations for owned tables, tests, and writes to its own data. A service MUST use only its own database credentials and MUST NOT be able to reach another service's schema, and the root `tests/` directory MUST NOT hold a service's own unit or integration tests.
- II.3 A service MUST NOT directly modify tables owned by another service.
- II.4 Cross-domain interactions MUST use documented APIs, or a deliberately approved integration mechanism, and never a source-level import from another service's package.
- II.5 The initial deployment MAY use one PostgreSQL cluster with separate schemas.
- II.6 Each service MUST use least-privilege credentials.
- II.7 Shared libraries MUST contain technical utilities only, never hidden cross-domain business logic.
- II.8 A shared database MUST NOT be represented as full infrastructure isolation or as an independent database failure domain; describing it as one hides an implicit coupling.

*Reconciliation note (ADR-0001)*: A shared database is a deployment convenience, not an isolation guarantee. Separate schemas do not equal infrastructure isolation, and a shared database is not an independent failure domain.

### Art. III. Security and Privacy by Design
Security and privacy are properties of the design, not a review step performed after it.

*Rationale*: The cost of a credential leak or a privacy breach is borne by people who never see the code. Deciding what a change is allowed to touch, read, and expose before it is written is the only point at which the decision is still cheap.

- III.1 Data handled by the platform MUST be classified by sensitivity, and the classification MUST be recorded in the specification that introduces the data.
- III.2 Personal data MUST be collected only for a documented purpose, retained only while that purpose requires it, and never reused for a second purpose without an approved decision.
- III.3 A secret MUST never be committed. Every secret-bearing value MUST be supplied through the environment, MUST be excluded from version control, and MUST appear in `.env.example` as a placeholder only.
- III.4 A detected secret is remediated rotation-first: the credential is assumed compromised and is rotated before the finding is closed.
- III.5 Every component, workflow, and credential operates with least privilege. A service receives only the database privileges its own schema needs; a workflow token is read-only; no component holds a privilege it does not use.
- III.6 Verification and diagnostic output MUST NOT contain a secret value. A scanner finding is reported by location and by kind of match, never by matched value.
- III.7 No production credential is required to run the required checks.
- III.8 Authentication and authorization are enforced at the service boundary.

### Art. IV. Financial Integrity
A monetary amount is exact, idempotent, and auditable; an approximate balance is a defect.

*Rationale*: Financial errors compound, are hard to detect after the fact, and are borne by customers. Precision, idempotency, and traceability must be designed in, because none of them can be recovered from a ledger after the fact.

- IV.1 A monetary amount MUST be represented in a decimal type, never in a binary floating-point type.
- IV.2 A monetary amount MUST never be silently rounded; any rounding MUST be an explicit, documented business rule.
- IV.3 A money-moving operation MUST be idempotent, and the idempotency key MUST be recorded with the transaction.
- IV.4 Every balance-changing operation MUST be traceable to the events that caused it.
- IV.5 An amount MUST NOT be reported without its currency.

### Art. V. Data Modeling and Database Evolution
A schema is owned by exactly one service and changes only through a reviewable migration.

*Rationale*: Schema changes are the least reversible thing in the system. Making them explicit, owned, and reviewable is what keeps one service's evolution from becoming another service's outage.

- V.1 Each domain's data model belongs to the service that owns the domain.
- V.2 A schema change MUST be expressed as a reviewable migration; no change is applied by hand to a live database.
- V.3 Alembic is the sole migration tool from Phase 2 onward. A migration MUST be reviewed before it is applied, and a destructive migration MUST state its rollback.
- V.4 A migration MUST be compatible with the currently deployed application version; a breaking change is split into an expand step and a contract step.
- V.5 The data model and the documentation that describes it are updated in the same change set.

### Art. VI. API and Integration Contracts
Every consumed interface is specified before it is implemented, and every change to it is deliberate.

*Rationale*: An interface is the only thing two teams genuinely share. Undocumented behaviour becomes accidental dependency, and an accidental dependency becomes an outage that neither owner can fix alone.

- VI.1 Every externally consumed interface MUST be specified before it is implemented.
- VI.2 A contract MUST state its request shape, response shape, error behaviour, and authorization requirements.
- VI.3 A change to a published contract is a breaking change unless the specification states otherwise; a breaking change requires a versioned endpoint and a documented migration path.
- VI.4 An integration that crosses a service boundary MUST be recorded in the API reference and covered by a contract test.
- VI.5 A network endpoint MUST NOT be added without an approved specification that describes it.

### Art. VII. Testing and Verifiability
A claim of completion is a claim backed by evidence.

*Rationale*: The purpose of a test is to make a claim checkable by someone who was not present when the code was written. A claim without evidence is an opinion, and opinions do not scale across a platform.

- VII.1 Every requirement MUST be traceable to a test or to an approved manual procedure, and an item MUST NOT be marked complete without evidence.
- VII.2 Authorization behaviour MUST be tested as positive and negative pairs.
- VII.3 A check that could not run is a failure, not a pass: it reports exit code `2`, and the merge gate treats it as a failure.
- VII.4 The test suite MUST pass against the implementation as it stands; a suite that passes only against an empty implementation is not probative and MUST be labelled as such.
- VII.5 The definition of done is `docs/quality/definition-of-done.md`.

### Art. VIII. Observability and Operability
A system that cannot be observed cannot be operated, and an operator without a correlation identifier is reading fiction.

*Rationale*: Every incident is a debugging session, and the first question in every one of them is which request is this. Correlation, structure, and health reporting are what turn a failure into a diagnosis.

- VIII.1 Every request MUST carry a correlation identifier, which is propagated across service boundaries and emitted with every log line the request produces.
- VIII.2 Every service MUST expose a health endpoint that reports readiness without exposing internal state.
- VIII.3 Logs MUST be structured and machine-parseable in continuous verification.
- VIII.4 Operational behaviour, deployment topology, and configuration changes MUST be documented in the same change set that alters them.
- VIII.5 Telemetry MUST NOT contain personal data or secret values.

### Art. IX. Synthetic Data
Test data is generated, never harvested.

*Rationale*: Real data in a test fixture is a copy of somebody's information living in a system nobody is watching. Synthetic data removes the exposure and, as a side effect, makes the fixture reproducible.

- IX.1 Test data MUST be synthetic; a production record MUST NOT be copied into a test, a fixture, or an example.
- IX.2 Synthetic data MUST be deterministic where an assertion depends on it, and MUST be produced by a documented generator.
- IX.3 Test data MUST NOT use real customer identifiers; names, addresses, emails, and telephone numbers are clearly synthetic.

### Art. X. Maintainability and Delivery
The cost of a change is paid by whoever reads it next, and that reader is the same team.

*Rationale*: A platform is a long-lived asset whose cost is dominated by maintenance rather than construction. Mechanical, repetitive rules are delegated to machines; a human reviews only what a machine cannot judge.

- X.1 Code MUST be typed, formatted, linted, and tested under the repository's pinned rule selections.
- X.2 External configuration MUST be declared in the configuration contract and realised in `.env.example`.
- X.3 The merge gate is the continuous-verification workflow, and its required-check set is the definition of done.
- X.4 There MUST be exactly one setup path and one required-check command.
- X.5 Dependencies MUST be pinned and locked, and the lockfile MUST be consistent with the declared dependencies.
- X.6 Documentation MUST be updated in the same change set as the behaviour it describes.
- X.7 Complexity MUST be justified in the specification, not assumed in the implementation.

### Art. XI. Architecture Decisions and Exceptions
A decision that constrains the architecture is recorded, and the record is honoured.

*Rationale*: The cost of a decision that nobody wrote down is paid twice — once when it is made and again when someone reverses it by accident. A recorded decision, with its reason, is the only thing that stops the reversal.

- XI.1 The precedence order is: constitution, then ADR, then specification, then tasks, then code. A lower layer never overrides a higher one.
- XI.2 A decision that constrains the architecture MUST be recorded as an ADR under `docs/adr/`.
- XI.3 An ADR MUST state its context, the options considered, the decision, and its consequences, and its status MUST reflect reality.
- XI.4 `docs/constitution.md` is the source artifact and `.specify/memory/constitution.md` is the governance record; in the event of a conflict the numbered copy prevails.
- XI.5 An exception to the constitution is permitted only through the amendment procedure, and MUST be recorded in the same change set that relies on it.

## Additional Constraints and Operational Policies

- An approved specification MUST define purpose, scope, actors, preconditions, normal and failure flows, data changes, authorization, observability, and measurable acceptance criteria.
- Implementation MUST NOT introduce requirements that are absent from the approved specification.
- When a requirement is ambiguous, contradictory, or materially incomplete, work MUST pause for clarification, or an explicit approved assumption MUST be recorded.
- Any change to approved behavior MUST update the specification and the affected tests in the same change set.

*Rationale*: Unreviewed implementation decisions are the most common source of scope drift, silent requirement loss, and untestable behavior. Binding intent to an approved document before code is written keeps review effort concentrated on expensive-to-reverse decisions.

## Development Workflow, Quality Gates, and Review Process

- All changes MUST be submitted via pull request with a completed review checklist.
- Quality gates (format, lint, lockfile, governance, file-coverage, typecheck, test, secret-scan, dependency-audit) MUST pass before a merge request can be approved.
- The required-check set defined in `noxfile.py` reports PASS (0), FAIL (1), COULD NOT RUN (2), or INTERNAL ERROR (3). Both 1 and 2 fail the gate (BR-003).
- Changes MUST not introduce new runtime network endpoints or database objects (BR-011).
- The implementation-language baseline MUST remain unchanged (BR-012).
- Third-party actions are SHA-pinned and the workflow token is read-only.

## Governance

- **Ratification Date**: 2026-10-21 — the date the constitution is formally approved.
- **Approval Record**: Project owner and technical reviewer signatures recorded below.
- **Amendment Procedure**: An amendment is proposed as a decision record under `docs/adr/`, stating the article being changed, the reason, and the affected clauses. The project owner and technical reviewer approve it, the approval block above is updated with the new amendment date, and the version in the header is bumped in the same change set.
- **Versioning Policy**: The constitution follows semantic versioning. A wording clarification that changes no obligation is a patch; a change to an article's obligation is a minor version; a change that removes or redefines an article is a major version. The version, the bump type and the change summary are recorded in the header block.
- **Compliance Review**: Each phase exit gate in `docs/build-plan.md` includes a constitution compliance review. The reviewer confirms that the phase introduced no obligation the approved specification does not describe, and that the phase's acceptance criteria and tests map to the articles the specification cites.

**Deferred items / follow-up**:

- Ratification date resolved — 2026-10-21 (date of formal approval).
- Approval record resolved — project owner and technical reviewer signatures recorded in the approval block below.
- Document reconciliation resolved — `docs/constitution.md` remains the source artifact with clause numbering; `.specify/memory/constitution.md` is the governance record. Both are aligned under Art. XI.4 precedence.
- ADR-0001 approval resolved — ADR-0001 (centralized PostgreSQL) status: Accepted. `docs/architecture/architecture-overview.md` remains Proposed/Draft pending further review.

## Approval Block

**Project Owner**: ____________________________  
**Date**: 2026-10-21  
**Technical Reviewer**: ________________________  
**Date**: 2026-10-21  

---  

*This constitution was reconciled from `docs/constitution.md` and `.specify/memory/constitution.md` per SPEC-001 task T012. Clause references use the numbered form from `docs/constitution.md` (citation convention). Per Art. XI.4, in the event of conflict between the numbered copy and the prose copy, the numbered copy prevails.*
