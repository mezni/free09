# Implementation Plan: <Feature Name>

- Spec ID:
- Spec version/hash:
- Status: Draft / Approved / In Progress / Complete

## Prerequisites
- Approved specification:
- Required ADRs:
- Dependencies:
- Migration prerequisites:

## Tasks
| Task ID | Task | Files/components | Tests/evidence | Depends on | Status |
|---|---|---|---|---|---|
| T-001 | Add/modify schema via migration | | Migration test | | Planned |
| T-002 | Implement domain logic | | Unit tests | T-001 | Planned |
| T-003 | Implement repository/API | | API/integration tests | T-002 | Planned |
| T-004 | Add authorization and audit | | Negative authorization tests | T-003 | Planned |
| T-005 | Update docs and traceability | | Review | T-001–T-004 | Planned |

## Implementation constraints
- Do not expand scope beyond the approved specification.
- Do not bypass service ownership.
- Do not weaken tests to make implementation pass.
- Record unexpected requirements as questions or proposed spec changes.
- Update this plan when dependencies change.

## Verification commands
List exact project commands for formatting, linting, type checks, unit tests, integration tests, and migration tests.

## Completion evidence
- Tests:
- Acceptance criteria:
- Migration status:
- Security review:
- Documentation:
- Commit/PR:
