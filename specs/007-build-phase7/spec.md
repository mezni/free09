# build-phase7: Polish & Completion

**Feature**: Final polishing, completion, and hand-off for the telco platform  
**Priority**: P2 (should-have for release readiness)  
**Status**: Proposed  
**Estimated effort**: 8 story points  

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
- [ ] All spec.md files across build-phases set to Implemented status (FR-060, T224 outstanding)
- [x] Constitution reconciliation between docs/ and .specify/ complete with dates and signatures (FR-061, T225 complete)
- [x] ADR-0001 carries its final decision status and the governance artefacts cite it (FR-062, T226 complete)
- [ ] Traceability matrix TM001–TM220 complete with all test mappings mapped (FR-063, T227 outstanding)
- [x] Fresh clone verification passes all check sets within 45 minutes (FR-064, T228 complete)
- [ ] Hand-off documentation complete and distributed (FR-065, no implementing task yet)

## Dependencies
- **Depends on**: the specifications of the earlier build phases, in the state
  `docs/build-plan.md` records — build-phase1 `Approved`, build-phase2 `Draft`,
  build-phase3 `Implemented`, build-phase5 and build-phase6 `Implemented`, and
  build-phase4 not specified. The finalisation of the remaining statuses
  (FR-060) and the closure of the unallocated TM ranges (FR-063) therefore
  remain open.
- **Enables**: None (final phase in the sequence)

## Traceability
| Requirement | User Story | Implementing task | Test Mapping | Priority | State |
|---|---|---|---|---|---|
| FR-060 Finalize spec.md statuses | US1 | T224 | TM221–TM223 | P1 | Partial |
| FR-061 Reconcile constitution documents | US2 | T225 | TM224–TM226 | P1 | Complete |
| FR-062 Record final ADR-0001 status | US3 | T226 | TM227–TM229 | P1 | Complete |
| FR-063 Update traceability matrix | US4 | T227 | TM230–TM232 | P1 | Not started |
| FR-064 Fresh clone verification | US5 | T228 | TM233–TM235 | P1 | Complete |
| FR-065 Hand-off documentation | US6 | *no implementing task* | *unallocated* | P2 | Not started |

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
