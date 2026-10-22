# Tasks: <Feature Name>

**Input**: Design documents from `<path-to-feature-directory>/`
**Spec**: `<path-to-feature-directory>/spec.md`
**Plan**: `<path-to-feature-directory>/plan.md`
**Research**: `<path-to-feature-directory>/research.md`
**Data model**: `<path-to-feature-directory>/data-model.md`
**Contracts**: `<path-to-feature-directory>/contracts/`
**Quickstart**: `<path-to-feature-directory>/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test or a documented manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the skeleton this feature needs. No check, story, or behaviour exists yet.

- [ ] T001 <task description with an exact file path>

**Checkpoint**: At this point, the skeleton is complete and the toolchain is declared.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Satisfy the constitution's approval precondition and the shared infrastructure this feature depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T002 <task description with an exact file path>

**Checkpoint**: At this point, the preconditions are met. User story implementation can begin.

---

## Phase 3: User Story 1 - <User Story Title> (Priority: P1) 🎯 MVP

**Goal**: <What the user wants to be able to do>

**Independent Test**: <How to verify this story on its own>

**Tests for User Story 1 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T003 [P] [US1] <test file path> asserting <observable behaviour> (test ID: `<test_function_name>`)

### Implementation for User Story 1

- [ ] T004 [US1] <implementation task with an exact file path>

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - <User Story Title> (Priority: P2)

**Goal**: <What the user wants to be able to do>

**Independent Test**: <How to verify this story on its own>

**Tests for User Story 2 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T005 [P] [US2] <test file path> asserting <observable behaviour> (test ID: `<test_function_name>`)

### Implementation for User Story 2

- [ ] T006 [US2] <implementation task with an exact file path>

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories**: All depend on Foundational phase completion

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Configuration and helpers before the checks that consume them
- Governance records before the evidence that cites them
- Story complete before moving to the next priority

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
