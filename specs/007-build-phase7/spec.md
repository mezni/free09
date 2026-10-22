# build-phase7: Polish & Completion

**Feature**: Final polishing, completion, and hand-off for the telco platform  
**Priority**: P2 (should-have for release readiness)  
**Status**: Implemented  
**Estimated effort**: 8 story points  
**Implemented**: 2026-10-22  

## User Stories
- **US1**: Finalize all spec.md statuses to Implemented after acceptance evidence
- **US2**: Reconcile constitution documents (docs/ vs .specify/) across all phases
- **US3**: Record final ADR-0001 decision status and update governance artifacts
- **US4**: Update traceability matrix with all test mappings (TM001–TM220)
- **US5**: Fresh clone verification (full environment, 30-45 minutes)
- **US6**: Hand-off documentation and knowledge transfer

## Functional Requirements
- **FR-060**: Finalize all spec.md statuses to Implemented after acceptance evidence
- **FR-061**: Reconcile constitution documents (docs/ vs .specify/) across all phases
- **FR-062**: Record final ADR-0001 decision status and update governance artifacts
- **FR-063**: Update traceability matrix with all test mappings (TM001–TM220)
- **FR-064**: Fresh clone verification (full environment, 30-45 minutes)
- **FR-065**: Hand-off documentation and knowledge transfer

## Non-Functional Requirements
- **NFR-040**: All acceptance criteria [x] marked in respective requirements.md files
- **NFR-041**: Constitution documents reconciled between docs/ and .specify/memory/ across all phases
- **NFR-042**: Traceability matrix TM001–TM220 complete with all test mappings mapped
- **NFR-043**: Fresh clone verification passes all check sets within 45 minutes

## Boundaries
- **In-scope**: Status updates, constitution reconciliation, traceability matrix updates, fresh clone verification, hand-off documentation
- **Out-of-scope**: Any new feature development, infrastructure changes, database schema modifications, business logic implementation

## Acceptance Criteria
- [x] All spec.md files across completed build-phases set to Implemented status; incomplete phases remain Proposed (FR-060, T224)
- [x] Constitution reconciliation between docs/ and .specify/ complete with dates and signatures (FR-061, T225 complete)
- [x] ADR-0001 carries its final decision status and the governance artefacts cite it (FR-062, T226 complete)
- [x] Traceability matrix TM001–TM238 allocated with every test mapping mapped or explicitly unallocated (FR-063, T227)
- [x] Fresh clone verification passes all check sets within 45 minutes (FR-064, T228 complete)
- [x] Hand-off documentation complete and distributed in `docs/HANDOFF.md` (FR-065, T229)

## Dependencies
- **Depends on**: the specifications of the earlier build phases, in the state
  `docs/build-plan.md` records — phases 1–7 are `Implemented`, phase 0 is
  `Approved` pending its two status-finalisation tasks, and phase 4 is not
  specified. Phases 8–11 remain `Proposed` because their acceptance evidence
  does not exist yet; the unallocated TM ranges are recorded explicitly in
  `docs/traceability-matrix.md`.
- **Enables**: None (final phase in the sequence)

## Traceability
| Requirement | User Story | Implementing task | Test Mapping | Priority | State |
|---|---|---|---|---|---|
| FR-060 Finalize spec.md statuses | US1 | T224 | TM221–TM223 | P1 | Complete |
| FR-061 Reconcile constitution documents | US2 | T225 | TM224–TM226 | P1 | Complete |
| FR-062 Record final ADR-0001 status | US3 | T226 | TM227–TM229 | P1 | Complete |
| FR-063 Update traceability matrix | US4 | T227 | TM230–TM232 | P1 | Complete |
| FR-064 Fresh clone verification | US5 | T228 | TM233–TM235 | P1 | Complete |
| FR-065 Hand-off documentation | US6 | T229 | TM236–TM238 | P2 | Complete |

## Edge Cases
- **Acceptance evidence missing**: a phase whose acceptance criteria have not been verified keeps the status **Proposed**; the status is never set to Implemented on the strength of the task list alone
- **The two constitution copies disagree**: the numbered copy prevails under Art. XI.4 and the discrepancy is recorded rather than resolved silently
- **A test mapping in the earlier range cannot be found**: the gap is reported as unallocated rather than omitted from the matrix
- **Fresh clone verification fails**: the programme is not handed over, and the failing check is recorded with its exit code
- **Hand-off requested while a phase is still Proposed**: the hand-off document names the open phase and its outstanding tasks explicitly

## Assumptions
- The prior phases' specifications reach `Approved` with their acceptance
  criteria passed before their statuses are finalized; the phases that are
  still `Proposed` or `Draft` keep their status until that evidence exists
- The constitution ratification record in `docs/constitution.md` is the
  authoritative reconciliation result for US2
- A fresh clone verification can be run in a clean environment with the
  documented prerequisites only

## Success Criteria
- **SC-01**: All spec.md files across build-phases status set to Implemented
- **SC-02**: Constitution reconciliation complete with dates and signatures recorded
- **SC-03**: Traceability matrix TM001–TM220 complete with all test mappings mapped
- **SC-04**: Fresh clone verification passes all check sets within 45 minutes
- **SC-05**: Hand-off documentation complete and distributed
