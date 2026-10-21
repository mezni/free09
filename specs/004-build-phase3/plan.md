# build-phase3: Plan

## Constitution Check ✓
- Constitution v1.0.0 aligned with `.specify/memory/constitution.md`
- FR-030 through FR-036 mapped to testable acceptance criteria

## Project Structure
- `specs/004-build-phase3/spec.md` — feature specification
- `specs/004-build-phase3/plan.md` — this document
- `specs/004-build-phase3/research.md` — design decisions
- `specs/004-build-phase3/data-model.md` — entity definitions
- `specs/004-build-phase3/contracts/` — interface contracts
- `specs/004-build-phase3/quickstart.md` — setup guide
- `specs/004-build-phase3/tasks.md` — 102-task breakdown (Phase 1–7)

## Complexity Tracking
- **Phase 1 (Setup)**: T001–T011 — Repository skeleton, toolchain, basic infra — 11 tasks
- **Phase 2 (Foundational)**: T012–T021 — Constitution, config loader, CI/CD, governance — 10 tasks
- **Phase 3 (US1)**: T022–T035 — API contract layer (this phase) — 14 tasks
- **Phase 4 (US2)**: T036–T063 — SDK generation, validation, gateway — 28 tasks
- **Phase 5 (US3)**: T064–T085 — Advanced features, monitoring, scaling — 22 tasks
- **Phase 6 (US4)**: T086–T095 — Polish, documentation, compliance — 10 tasks
- **Phase 7 (Polish)**: T096–T102 — Finalization, cleanup, handbook — 9 tasks

**Total**: 102 tasks across 7 phases

## Traceability Matrix
| Task | FR/BR/AC | User Story | Test Mapping | Priority |
|------|----------|------------|--------------|----------|
| T022–T035 | FR-030 to FR-036 | US1 | TM031–TM044 | P1 |
| T036–T063 | FR-030 to FR-036 | US2 | TM045–TM072 | P2 |
| T064–T085 | FR-030 to FR-036 | US3 | TM073–TM094 | P3 |
| T086–T095 | FR-030 to FR-036 | US4 | TM095–TM102 | P4 |
| T096–T102 | — | Polish | TM103–TM110 | P5 |

## Phase 3: US1 — API Contract Layer
- Goal: Design and document API contracts using OpenAPI 3.1
- Independent test criteria: SDK generation, validation, gateway config
- Implementation: OpenAPI spec, SDK generators, middleware
- Parallel tasks: SDK generation (P), spec review (P)
- Dependencies: None (Phase 1–2 complete)
