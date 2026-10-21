# Definition of Done and Quality Gates

A feature is done only when all applicable gates pass.

## Specification
- [ ] Approved feature specification exists.
- [ ] Scope and out-of-scope items are explicit.
- [ ] Acceptance criteria are measurable and testable.
- [ ] Errors, authorization, data changes, and failure scenarios are specified.
- [ ] Requirement-to-test mapping is complete.

## Implementation
- [ ] Code follows service ownership boundaries.
- [ ] Input and output schemas are explicit.
- [ ] Database changes use reviewed migrations.
- [ ] Configuration and secrets are handled safely.
- [ ] Logs avoid secrets and unnecessary sensitive data.
- [ ] API documentation is updated.

## Tests
- [ ] Unit tests pass.
- [ ] Integration/API tests pass where applicable.
- [ ] Authorization positive and negative tests pass.
- [ ] Database constraints and migrations are tested.
- [ ] Regression tests cover fixed defects.
- [ ] Billing invariants and idempotency are tested for financial changes.
- [ ] Synthetic data integrity and reproducibility are tested for generator changes.

## Operations
- [ ] Logs and metrics are sufficient to diagnose failures.
- [ ] Timeouts, retries, and correlation IDs are handled where relevant.
- [ ] Health/readiness behavior is updated if dependencies change.
- [ ] Recovery or reconciliation behavior is documented for partial failure.

## Review and release
- [ ] Linting, formatting, type checks (if configured), and CI pass.
- [ ] Security/privacy impact is reviewed.
- [ ] ADRs and docs are updated.
- [ ] No unresolved critical acceptance failures remain.
- [ ] Any accepted exception has an owner, mitigation, and review date.
