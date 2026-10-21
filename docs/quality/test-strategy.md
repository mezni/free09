# Test Strategy

## Test layers

1. **Unit tests:** domain calculations, validation, state transitions, authorization decisions.
2. **Database integration tests:** constraints, transactions, migrations, repository behavior, and isolation.
3. **API tests:** request/response schemas, status codes, errors, pagination, and authorization.
4. **Contract tests:** service consumer/provider expectations and compatibility.
5. **Workflow tests:** multi-step customer, billing, and provisioning scenarios.
6. **Synthetic-data tests:** deterministic generation, valid references, uniqueness, scenario distributions, and safe reset behavior.
7. **Performance tests:** selected high-volume queries and endpoints using controlled synthetic datasets.
8. **Operational tests:** health checks, backup restoration, migration recovery, and dependency failure handling.

## Mandatory negative cases

- Missing, expired, malformed, or incorrectly scoped token.
- Agent attempts a supervisor-only action.
- Access to a resource outside the caller's permitted scope.
- Duplicate payment or financial-posting request.
- Invalid or conflicting asset identifiers.
- Invalid lifecycle transition.
- Missing referenced entity.
- Database or downstream service timeout.
- Provisioning failure after commercial activation has begun.
- Synthetic reset attempted against a non-test environment.

## Evidence

CI should publish test results and coverage summaries. Coverage percentage alone is not proof of correctness; critical acceptance criteria and financial invariants require explicit tests.
