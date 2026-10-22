# Build Plan
Version: 1.1  
Status: Baseline plan with the phase 10 and 11 build-plan extensions

## 1. Delivery strategy

Build in dependency order. Stabilize domain concepts and database ownership before implementing dependent APIs. Use vertical slices where practical: each feature should include its specification, migration, API, authorization, tests, observability, and documentation.

Do not attempt full TM Forum or 3GPP compliance by implication. Identify any specific standards and versions only when a concrete requirement needs them.

## 2. Phases and exit gates

### Phase 0 — Project setup and governance
**Outcomes**
- Approve the constitution and initial assumptions.
- Create repository layout, Python tooling, linting, tests, environment configuration, and CI.
- Establish ADR and specification templates.
- Add `README.md`, `.env.example`, `.gitignore`, and contribution rules.

**Exit gate**
- Clean environment setup is reproducible.
- Formatting, linting, and a minimal test run succeed in CI.
- No secrets are committed.

### Phase 1 — Domain discovery and architecture
**Outcomes**
- Define actors, use cases, non-functional requirements, and explicit out-of-scope items.
- Confirm service responsibilities and ownership.
- Draw system context, container/service, and key workflow diagrams.
- Document service dependencies and failure behavior.
- Decide API versioning, identifiers, time zones, currency policy, and audit policy.

**Exit gate**
- Architecture overview is approved.
- Service responsibility matrix and initial ADRs are accepted.
- Open questions are either resolved or recorded with owners and deadlines.

### Phase 2 — Data model and database foundation
**Outcomes**
- Define conceptual ER model and logical data model.
- Define PostgreSQL schemas, table ownership, keys, constraints, indexes, and lifecycle/status fields.
- Define migration policy and local database environment.
- Specify audit fields, effective dating, and historical-data strategy.

**Exit gate**
- ER diagram and data dictionary are reviewed.
- Critical relationships and financial invariants are documented.
- Initial migrations can create a clean database and pass migration tests.

### Phase 3 — Authentication and authorization
**Outcomes**
- Implement users, roles, permissions, password hashing, token lifecycle, and protected endpoints.
- Define agent, supervisor, and service-identity permissions.
- Add audit events for security-sensitive actions.

**Exit gate**
- Positive and negative authorization tests pass.
- Token validation and password handling are tested.
- Privilege escalation and unauthorized access tests pass.

### Phase 4 — CRM vertical slice
**Outcomes**
- Implement customers, subscribers, contact details, and indexed lookup.
- Implement support tickets, status history, assignment history, and agent assignment.
- Specify cross-domain references without violating service ownership.

**Exit gate**
- CRUD and workflow tests pass.
- Customer/subscriber relationships and ticket history are validated.
- RBAC, pagination, filtering, and error contracts are tested.

### Phase 5 — Inventory, catalog, subscriptions, and provisioning
**Outcomes**
- Implement products, product versions, rate plans, pricing versions, and add-ons.
- Implement subscriptions and lifecycle transitions.
- Implement devices, SIM/eSIM records, assignments, and provisioning profiles/jobs.
- Add a mock provisioning adapter.

**Exit gate**
- Historical pricing and effective-date rules are testable.
- Device/SIM identifiers and assignment constraints are validated.
- Failed provisioning cannot be mistaken for successful activation.

### Phase 6 — Monitoring and observability
**Outcomes**
- Implement structured log aggregation, search and Loki shipping.
- Expose Prometheus metrics for every service and provision dashboards.
- Route alert rules through Alertmanager with team and severity labels.
- Continue OpenTelemetry traces across service boundaries and expose mesh telemetry.
- Provide executable incident runbooks and rolling-window anomaly detection.

**Exit gate**
- Log search returns filtered results without blocking request handling.
- `/metrics` is scrapeable for all four services.
- Alert rules and routes include severity, team and runbook references.
- Trace IDs propagate across boundaries and Istio telemetry is provisioned.
- The three documented runbooks and their API representation execute successfully.

### Phase 7 — Synthetic data generation
**Outcomes**
- Implement configuration, deterministic random seed, generators, dependency ordering, validators, CLI, and database loader.
- Generate representative lifecycle and failure scenarios.
- Add dataset summaries and safe reset protections.

**Exit gate**
- Fixed seed/configuration produces repeatable output within the documented reproducibility boundary.
- All foreign keys and domain invariants pass.
- Generator refuses unsafe environment targets.
- Small, medium, and stress profiles are validated.

### Phase 8 — Cross-service integration
**Outcomes**
- Implement and test required service-to-service API calls.
- Document timeouts, retries, correlation IDs, and partial failure.
- Define reconciliation or repair workflows for cross-service inconsistencies.
- Add contract and integration tests.

**Exit gate**
- Dependency failures are handled predictably.
- Retries do not duplicate business effects.
- Integration tests run in CI using controlled dependencies.

### Phase 9 — Production readiness
**Outcomes**
- Structured logging, metrics, tracing, health/readiness, alerting, and dashboards.
- Security review, dependency review, and threat model.
- Performance tests, query review, and capacity assumptions.
- Backup/restore drills and recovery documentation.
- Deployment, migration, rollback/forward-recovery, and incident runbooks.

**Exit gate**
- All critical acceptance criteria pass.
- Restore procedure has been exercised.
- Security and operational risks have owners and accepted mitigations.
- Release readiness is explicitly approved.

### Phase 10 — Build plan extension
**Outcomes**
- Additional build pipeline optimization stages.
- Enhanced phase gate compliance validation.
- Improved phase traceability and reporting.
- Integration with external deployment systems.
- Compliance and audit reporting for build processes.
- Build performance metrics and profiling.

**Exit gate**
- FR-100 through FR-105 have passing acceptance criteria.
- Phase gate compliance validation completes within 20 seconds.
- Performance metrics add less than 5% build-time overhead.

Specification: `specs/010-build-phase10/spec.md` — status **Proposed**.

### Phase 11 — Build plan extension (reporting horizon)
**Outcomes**
- Additional build pipeline reporting stages.
- Enhanced phase gate statistical analysis.
- Improved phase dashboard and visualization.
- Integration with external monitoring systems.
- Compliance and statistical process control reporting.
- Build trend analysis and forecasting.

**Exit gate**
- FR-110 through FR-115 have passing acceptance criteria.
- Phase gate statistical analysis completes within 15 seconds.
- Trend analysis adds less than 3% build-time overhead.

Specification: `specs/011-build-phase11/spec.md` — status **Proposed**.

## 2.1 Phase-to-specification index

The phase numbers above describe the delivery strategy. The specifications that
carry the requirements use their own directory names, so the mapping is:

| Plan phase | Specification directory | Specification status | Implementation state |
|---|---|---|---|
| Phase 0 — Project setup and governance | `specs/001-project-setup/` | Approved | 100 of 102 tasks complete — T095 and T102 (status finalisation) stay open until the GitHub Actions run reference is recorded in `docs/quality/phase-0-exit-gate.md` |
| Phase 1 — Domain discovery and architecture | `specs/002-build-phase1/` | Approved | Implemented — all 26 tasks complete |
| Phase 2 — Data model and database foundation | `specs/003-build-phase2/` | Approved | Phase 2 complete — schemas/roles, models, four reversible Alembic revisions, migration/schema tests with role-grant enforcement, preflight wired into required checks (all nine checks pass). |
| Phase 3 — Authentication and authorization | `specs/004-build-phase3/` | Implemented | Implemented — all 54 tasks complete |
| Phase 4 — CRM vertical slice | *(no specification directory)* | — | Not specified |
| Phase 5 — Inventory, catalog, subscriptions, provisioning | `specs/005-build-phase5/` | Implemented | Implemented — all 59 tasks complete; observability, API keys, webhooks and benchmarks delivered |
| Phase 6 — Monitoring and observability | `specs/006-build-phase6/` | Implemented | Implemented — all 62 tasks complete; Loki, Prometheus, Alertmanager, Grafana, Istio, runbooks and anomaly detection delivered |
| Phase 7 — Synthetic data generation | `specs/007-build-phase7/` | Proposed | Partially implemented — 3 of 5 tasks complete |
| Phase 8 — Cross-service integration | `specs/008-build-phase8/` | Proposed | Partially implemented — 22 of 54 tasks complete; US1 only |
| Phase 9 — Production readiness | `specs/009-build-phase9/` | Proposed | Not started |
| Phase 10 — Build plan extension | `specs/010-build-phase10/` | Proposed | Not started |
| Phase 11 — Build plan extension (reporting horizon) | `specs/011-build-phase11/` | Proposed | Not started |

The specification status is the lifecycle field the specification itself
carries; the implementation state is the completion count from that phase's
`tasks.md`, verified against the repository. A phase keeps the status
**Proposed** until every acceptance criterion in its `spec.md` passes, so a
phase with a partially implemented task list is **Proposed** even when most of
its tasks are complete. The task counts are recorded in each phase's task list
header.

The phase names carried by the specification directories predate this plan and
describe the work each extension phase actually added, so the two vocabularies
do not align one-to-one. The table above is the authoritative mapping.

## 3. Prioritization

Priority order:
1. Data ownership, identity model, and financial invariants.
2. Authentication and authorization.
3. Core CRM and catalog/subscription workflows.
4. Billing correctness and auditability.
5. Synthetic data and integration automation.
6. Operational hardening and performance.

Synthetic generator scaffolding can begin early, but domain-specific generators and loaders should be finalized after the relevant schemas and invariants are approved.

## 4. Work-item workflow

For every feature:
1. Create a feature brief and define scope.
2. Write functional requirements and non-functional requirements.
3. Write scenarios and measurable acceptance criteria.
4. Specify data changes, API contracts, permissions, errors, and observability.
5. Review dependencies and update ADRs if needed.
6. Derive small implementation tasks.
7. Implement with tests.
8. Run quality gates.
9. Review requirement-to-test traceability.
10. Update documentation and mark the spec implemented only after acceptance.

## 5. Change control

A requirement change must identify:
- Reason and requester.
- Affected specs, APIs, schemas, tests, and downstream consumers.
- Data migration/backfill impact.
- Security, privacy, financial, and operational risks.
- Compatibility and rollout strategy.
- Approval and updated acceptance criteria.

Do not silently change an approved spec to match an implementation that already exists.
