# Tasks: Project Setup and Governance

**Input**: Design documents from `/home/dali/WORK/telco-si/specs/001-project-setup/`
**Spec**: `specs/001-project-setup/spec.md`
**Plan**: `specs/001-project-setup/plan.md`
**Research**: `specs/001-project-setup/research.md`
**Data model**: `specs/001-project-setup/data-model.md`
**Contracts**: `specs/001-project-setup/contracts/`
**Quickstart**: `specs/001-project-setup/quickstart.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included. The feature specification's Test Mapping names a planned test for every requirement, FR-008 requires a minimal test suite, and Constitution Article VII.1 requires every acceptance criterion to map to a verifiable test or a documented manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

⚠️ Blocking gate: Constitution Article I.1 permits implementation only against an **approved** specification. T012, T013, and T014 complete that precondition and MUST complete before any other task in this list begins.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo** of four independently-deployable services plus a shared technical library, governed by Spec Kit artefacts. Paths below follow `specs/001-project-setup/contracts/repository-layout-contract.md`:

- `services/<service-name>/src/<package_name>/` — application source
- `libs/telco-common/src/telco_common/` — shared technical utilities only
- `tests/contract/`, `tests/governance/` — cross-service and repository-governance tests
- `ci/` — machine-consumed verification configuration
- `deploy/compose/` — local runtime topology
- `docs/` — governance and design prose
- `specs/001-project-setup/` — this feature's artefacts

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the repository skeleton and declare the toolchain. No
check, story, or behaviour exists yet.

- [X] T001 Create the top-level directory skeleton in `services/`, `libs/telco-common/`, `ci/`, `deploy/compose/`, `tests/contract/`, and `tests/governance/` per `specs/001-project-setup/contracts/repository-layout-contract.md`
- [X] T002 Create the root `pyproject.toml` with `[tool.uv.workspace]` members covering `services/*` and `libs/*` plus the `[tool.ruff]`, `[tool.pytest.ini_options]`, and `[tool.coverage]` sections
- [X] T003 Create `.python-version` pinning the interpreter to `3.13`
- [X] T004 [P] Create `libs/telco-common/pyproject.toml` and `libs/telco-common/src/telco_common/__init__.py` for the shared technical library
- [X] T005 [P] Create `services/auth-service/pyproject.toml` and `services/auth-service/src/auth_service/__init__.py`
- [X] T006 [P] Create `services/crm-service/pyproject.toml` and `services/crm-service/src/crm_service/__init__.py`
- [X] T007 [P] Create `services/billing-service/pyproject.toml` and `services/billing-service/src/billing_service/__init__.py`
- [X] T008 [P] Create `services/inventory-service/pyproject.toml` and `services/inventory-service/src/inventory_service/__init__.py`
- [X] T009 Extend `.gitignore` with the Phase 0 exclusions (`.env`, `.venv/`, `.nox/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `htmlcov/`, `.coverage`, `dist/`, `build/`, `*.egg-info/`, `deploy/compose/.env`) and state each exclusion's rationale in a comment
- [X] T010 Create `Makefile` as a thin alias layer over nox and docker compose, containing no logic of its own
- [X] T011 Generate `uv.lock` with `uv lock` and verify `uv sync --frozen --all-packages` succeeds, then commit the lockfile

**Checkpoint**: At this point, the repository skeleton is complete and the toolchain is declared.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Satisfy the constitution's approval precondition and build the
shared technical library and nox framework. No user story work can begin
until this phase is complete.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X]  T012 Reconcile `docs/constitution.md` with `.specify/memory/constitution.md` into exactly one constitution document, resolve the Sync Impact Report placeholders `TODO(RATIFICATION_DATE)`, `TODO(APPROVAL_RECORD)`, `TODO(DOC_RECONCILIATION)`, and `TODO(ADR-0001_APPROVAL)`, and align the two copies so FR-020 holds
- [X]  T013 Ratify the constitution by recording the ratification date and the project owner and technical reviewer signatures in the approval block of `docs/constitution.md` and the Ratification Record of `.specify/memory/constitution.md`
- [X]  T014 Set the Status of `specs/001-project-setup/spec.md` to `Approved` with the approver and the approval date, satisfying Constitution Article I.1
- [X]  T015 Record the decision status of `docs/adr/ADR-0001-centralized-postgresql.md` as `Accepted`, or as a documented deferral with an owner and a due phase
- [X]  T016 Implement the configuration loader in `libs/telco-common/src/telco_common/config.py` per `specs/001-project-setup/contracts/configuration-contract.md`, honouring the required, optional, reserved, and secret-bearing markers and failing fast with exit code 2
- [X]  T017 Create `.env.example` realizing every variable declared in the configuration contract with placeholder values only and no usable credential, key, or connection string
- [X]  T018 Implement the session framework and the shared result reporter in `noxfile.py`, distinguishing PASS, FAIL, COULD NOT RUN, and INTERNAL ERROR with exit codes 0, 1, 2, and 3
- [X]  T019 Create `ci/run-checks.sh` as the single entry point invoked by every nox session, forwarding the session exit code unchanged
- [X]  T020 Create `tests/conftest.py` registering the `unit`, `integration`, `contract`, `governance`, and `slow` markers and the shared fixtures
- [X]  T021 Create the minimal test suite in `tests/governance/test_minimal_suite.py` that passes against the empty implementation so a failing check always indicates a real defect (test ID: `test_minimal_test_suite_passes_on_empty_implementation`)

**Checkpoint**: At this point, the constitution is ratified, the specification is approved, and the technical infrastructure is complete. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Reproducible Local Environment (Priority: P1) 🎯 MVP

**Goal**: A new engineer can clone the repository, follow the single documented
setup path, and reach a verified state with no undocumented manual steps.

**Independent Test**: On a fresh clone with only the documented prerequisites,
the setup command produces a verified environment: correct Python version,
dependencies installed, database running, and `.env` created idempotently
without destroying locally-supplied values.

**Tests for User Story 1 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X]  T022 [P] [US1] Create `tests/governance/test_fresh_clone_setup.py` asserting a person with no prior project context reaches a verified state from a fresh clone following only the repository documentation, with no undocumented manual step (test ID: `test_fresh_clone_setup_reaches_verified_state`)
- [X]  T023 [P] [US1] Create `tests/governance/test_language_baseline_unchanged.py` asserting the implementation-language and persistence baseline declared by the constitution is unchanged by this phase (test ID: `test_implementation_language_baseline_unchanged`)
- [X]  T024 [P] [US1] Create `tests/governance/test_setup_prerequisites.py` asserting the setup path names the missing prerequisite and how to obtain it, and does not fail with an unrelated or generic error (test ID: `test_setup_names_missing_prerequisite`)
- [X]  T025 [P] [US1] Create `tests/governance/test_setup_determinism.py` asserting two independent setup paths reach an equivalent verified state with no undocumented manual adjustment (test ID: `test_two_independent_setups_reach_equivalent_state`)
- [X]  T026 [P] [US1] Create `tests/governance/test_example_config.py` asserting the example configuration lists every variable the repository requires with its purpose and its required-or-optional status, and contains no usable credential, key, or connection string (test ID: `test_example_config_lists_all_variables_without_secrets`)
- [X]  T027 [P] [US1] Create `tests/governance/test_config_derivation.py` asserting the required checks derive every configuration value from `.env.example` alone in a clean environment (test ID: `test_checks_derive_config_from_example`)
- [X]  T028 [P] [US1] Create `tests/governance/test_gitignore_exclusions.py` asserting local overrides and generated artifacts are excluded from version tracking (test ID: `test_local_overrides_and_artifacts_are_untracked`)

### Implementation for User Story 1

- [X]  T029 [US1] Implement the prerequisite verifier in `ci/check_prerequisites.py` checking the Python, uv, Docker, git, and make versions against the documented baseline and naming each missing prerequisite
- [X]  T030 [US1] Implement the setup path in `ci/setup.sh` to verify prerequisites, run `uv sync --frozen --all-packages`, start the database, and create `.env` idempotently without destroying locally supplied values
- [X]  T031 [P] [US1] Create `deploy/compose/compose.yaml` with `postgres:16.15-alpine`, the `auth`, `crm`, `billing`, and `inventory` schemas, and least-privilege per-service roles
- [X]  T032 [US1] Add the `setup`, `db-up`, and `db-down` sessions to `noxfile.py` and the matching aliases to `Makefile`
- [X]  T033 [US1] Write `README.md` as the entry point stating the project purpose, the repository conventions, the documented setup path, the runtime and operating system baseline, and the verification command
- [X]  T034 [US1] Reconcile `specs/001-project-setup/quickstart.md` with the implemented setup path so every command, default, and expected output matches

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Automated Quality Gates on Every Change (Priority: P2)

**Goal**: Every change is automatically checked for formatting, lint quality,
test results, and secret/dependency compliance before it can be merged.

**Independent Test**: Introduce a deliberate defect — broken formatting, a lint
error, a test failure, or a secret finding — and confirm the documented local
command reports the per-check outcome with the expected exit code.

**Tests for User Story 2 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X]  T035 [P] [US2] Create `tests/governance/test_ci_accepts_and_rejects.py` asserting continuous verification accepts a conforming change and rejects a change that breaks formatting, lint, or a test, naming the failing check and the location of the problem (test ID: `test_continuous_verification_accepts_and_rejects_changes`)
- [X]  T036 [P] [US2] Create `tests/governance/test_dependency_review_recorded.py` asserting the dependency review is recorded as evidence produced by the required checks (test ID: `test_dependency_review_recorded`)
- [X]  T037 [P] [US2] Create `tests/governance/test_local_verification.py` asserting the documented local command runs every required check and reports a per-check outcome (test ID: `test_local_verification_command_runs_all_required_checks`)
- [X]  T038 [P] [US2] Create `tests/governance/test_gate_fails_closed.py` asserting a failing check always blocks merge (test ID: `test_failed_or_inconclusive_check_blocks_merge`)
- [X]  T039 [P] [US2] Create `tests/governance/test_checks_offline.py` asserting the documented local command runs every required check without network access and reports appropriate outcomes (test ID: `test_checks_complete_without_network_access`)
- [X]  T040 [P] [US2] Create `tests/governance/test_secret_scan_redaction.py` asserting a credential in a tracked file is rejected, the file and the violated rule are named, and the credential value never appears in the output (test ID: `test_secret_detection_blocks_and_redacts`)
- [X]  T041 [P] [US2] Create `tests/governance/test_secret_scan_history.py` asserting the full version-controlled history contains no secret material (test ID: `test_no_secret_material_in_full_history`)
- [X]  T042 [P] [US2] Create `tests/governance/test_no_runtime_surface.py` asserting this phase introduced no runtime network endpoint and no application database object (test ID: `test_no_network_endpoint_or_database_object_introduced`)
- [X]  T043 [P] [US2] Create `tests/governance/test_local_ci_parity.py` asserting the local outcome matches the automated outcome for the same change (test ID: `test_local_result_matches_automated_result`)
- [X]  T044 [P] [US2] Create `tests/governance/test_config_agreement.py` asserting the configuration contract, the example configuration, and the code that reads the settings agree in both directions, and that the reserved per-service database variables are declared (test IDs: `test_configuration_contract_and_code_agree`, `test_the_contract_declares_the_reserved_database_variables`, `test_the_example_declares_every_implemented_variable`, `test_the_example_is_the_single_source_of_the_variable_list`, `test_the_environment_settings_are_documented_where_they_are_read`)
- [X]  T045 [US2] Add the explicit `[tool.ruff]` rule selection, `[tool.pytest.ini_options]`, and `[tool.coverage]` sections to `pyproject.toml` and create `mypy.ini` with strict mode and the pydantic plugin
- [X]  T046 [US2] Implement the `format`, `lint`, `lockfile`, and `typecheck` sessions in `noxfile.py`
- [X]  T047 [US2] Implement the `test` session in `noxfile.py` with marker-based selection and coverage reporting
- [X]  T048 [P] [US2] Create `.gitleaks.toml` with the custom rule for the known weak placeholder literals and the allowlist for this repository's own placeholder values
- [X]  T049 [US2] Implement the `secret-scan` session in `noxfile.py` running gitleaks in git mode with `--redact` across the full history
- [X]  T050 [P] [US2] Create `ci/advisories/python-advisories.json` as the vendored advisory snapshot
- [X]  T051 [P] [US2] Create `ci/check_dependencies.py` checking the locked dependency set against the vendored snapshot and asserting the lockfile resolves offline
- [X]  T052 [US2] Implement the `dependency-audit` session in `noxfile.py`
- [X]  T053 [P] [US2] Create `ci/check_spec_artifacts.py` verifying templates hold unfilled placeholders only, exactly one constitution exists in the tracked tree, feature directories and numbering are valid, and the configuration contract and `.env.example` agree in both directions
- [X]  T054 [US2] Implement the `governance` session in `noxfile.py`
- [X]  T055 [P] [US2] Create `ci/check_file_coverage.py` enforcing the five conditions defined in `specs/001-project-setup/contracts/verification-contract.md`
- [X]  T056 [P] [US2] Create `ci/file-coverage.yml` mapping each tracked path glob to the required check that covers it, with the Phase 0 exclusions each carrying a reason, an owner, and a review date
- [X]  T057 [US2] Implement the `file-coverage` session in `noxfile.py`
- [X]  T058 [P] [US2] Create `.github/workflows/ci.yml` with the `fast-checks` and `slow-checks` lanes and the `required-checks` gate job, using SHA-pinned actions, `permissions: contents: read`, `persist-credentials: false`, the `if: always()` gate condition, and a concurrency group that never cancels a merge-queue run
- [X]  T059 [P] [US2] Create `.github/rulesets/main-required-checks.json` making the `required-checks` gate job a required status check on `main`
- [X]  T060 [P] [US2] Create `.github/dependabot.yml` for the `uv` and `github-actions` ecosystems
- [X]  T061 [P] [US2] Create `.pre-commit-config.yaml` with the ruff check, ruff format, `uv-lock`, gitleaks, and standard pre-commit hooks
- [X]  T062 [P] [US2] Create `.github/workflows/refresh-advisories.yml` as the scheduled, non-required advisory snapshot refresh that opens a pull request

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Governance Records and Reusable Document Templates (Priority: P3)

**Goal**: A maintainer can point to one place that states what the project
requires, how work is planned, and how decisions are recorded, and can create
new feature artefacts from templates that carry only unfilled placeholders.

**Independent Test**: Instantiate each template into a new, unused artefact and
confirm the result is structurally complete, contains no approved content
carried over from another feature, and leaves only the expected metadata
unresolved.

**Tests for User Story 3 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X]  T063 [P] [US3] Create `tests/governance/test_build_plan.py` asserting the build plan states every phase, that phase's outcomes, and that phase's exit gate conditions (test ID: `test_build_plan_states_phases_and_exit_gates`)
- [X]  T064 [P] [US3] Create `tests/governance/test_decision_record_format.py` asserting a completed decision record states context, options considered, the decision, consequences, a status, and the conditions under which it should be revisited (test ID: `test_completed_decision_record_matches_template`)
- [X]  T065 [P] [US3] Create `tests/governance/test_single_constitution.py` asserting exactly one constitution document exists in the tracked tree and states its version, its ratification state, and its amendment procedure (test ID: `test_single_constitution_with_version_and_ratification`)
- [X]  T066 [P] [US3] Create `tests/governance/test_templates_unfilled.py` asserting each required template instantiates into an artefact with every required section present and no unfilled template comment remaining (test ID: `test_templates_contain_only_placeholders`)
- [X]  T067 [P] [US3] Create `tests/governance/test_templates_no_approved_content.py` asserting no template carries approved content, decisions, or values belonging to a specific feature (test ID: `test_templates_do_not_carry_approved_content`)
- [X]  T068 [P] [US3] Create `tests/governance/test_feature_numbering.py` asserting feature directories are uniquely and sequentially numbered and each holds a specification, a task set, and a quality checklist (test ID: `test_feature_directories_are_numbered_and_complete`)
- [X]  T069 [P] [US3] Create `tests/governance/test_open_questions_owned.py` asserting every open question carries an owner and a due phase (test ID: `test_open_questions_have_owner_and_due_phase`)
- [X]  T070 [P] [US3] Create `tests/governance/test_precedence_order.py` asserting a conflict between two governance documents resolves to exactly one governing statement and the lower-precedence document is flagged for correction (test IDs: `test_precedence_order_resolves_documented_conflict`, `test_conflict_resolves_to_single_governing_statement`)
- [X]  T071 [P] [US3] Create `tests/governance/test_exit_gate_evidence.py` asserting every phase exit gate condition has recorded evidence before the gate is treated as satisfied (test ID: `test_exit_gate_evidence_recorded_for_every_condition`)
- [X]  T072 [P] [US3] Create `tests/governance/test_artefact_coverage.py` asserting every artefact introduced by this phase is covered by a gate condition or carries an explicitly recorded exemption (test ID: `test_every_phase_artifact_covered_by_gate_or_exemption`)
- [X]  T073 [P] [US3] Create `tests/governance/test_traceability_complete.py` asserting every requirement in the matrix points to a test or an approved manual verification, and that no placeholder row remains in the approved section (test ID: `test_requirement_to_test_mapping_exists`)

### Implementation for User Story 3

- [X]  T074 [US3] Create `templates/tasks-template.md` from the Spec Kit task template carrying only unfilled placeholders
- [X]  T075 [P] [US3] Complete `templates/feature-spec-template.md`, `templates/implementation-plan-template.md`, `templates/adr-template.md`, and `templates/decision-log-template.md` so each carries only unfilled placeholders and no approved content
- [X]  T076 [P] [US3] Create `docs/adr/ADR-0002-uv-workspace.md` recording the uv workspace decision, the rejected pip-tools, Poetry, and plain-pip alternatives, and its revisit conditions
- [X]  T077 [P] [US3] Create `docs/adr/ADR-0003-secret-scanning-and-remediation.md` recording gitleaks with `--redact` and the rotate-first remediation path, with the rejected trufflehog and detect-secrets alternatives and their licence and redaction reasons
- [X]  T078 [P] [US3] Create `docs/adr/ADR-0004-http-client-pinning.md` recording the httpx 0.28.1 pin, the ecosystem reason for the `httpx2` deferral, and the revisit trigger
- [X]  T079 [P] [US3] Create `docs/adr/ADR-0005-python-quality-toolchain.md` recording ruff plus mypy strict with the pydantic plugin, the pyright alternative, and its trade-offs
- [X]  T080 [US3] Create `docs/governance/precedence-and-conventions.md` stating the precedence order and the feature and decision-record numbering conventions, and add the `docs/governance/` row to the placement table in `specs/001-project-setup/contracts/repository-layout-contract.md`
- [X]  T081 [US3] Update `docs/build-plan.md` so every phase states its outcomes and its exit gate conditions explicitly
- [X]  T082 [US3] Record the exit-gate evidence for the conditions "formatting, linting, and a minimal test run succeed in CI" and "no secrets are committed" in `docs/quality/phase-0-exit-gate.md`
- [X]  T083 [US3] Update `docs/quality/traceability-matrix.md` with the implemented test names and their evidence, and replace or remove the eight placeholder rows inherited from the starter template
- [X]  T084 [US3] Update `specs/001-project-setup/checklists/requirements.md` to reflect the approved state of the specification

**Checkpoint**: At this point, all user stories should now be independently functional.

---

## Phase 6: User Story 4 - Contributor Orientation and Safe Secret Handling (Priority: P4)

**Goal**: A contributor who has never worked on this project understands what
the project requires, how to set up, how to run the checks, how to propose a
change, and what must accompany a change beyond working code. Safe secret
handling practices are documented and enforced.

**Independent Test**: A participant who has not seen the project completes a
setup task and verifies the outcome without external assistance.

**Tests for User Story 4 ⚠️**

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X]  T085 [P] [US4] Create `tests/governance/test_contributor_docs_match_checks.py` asserting the contributor guide covers all setup checks and obligations (test ID: `test_contributor_docs_cover_setup_checks_and_obligations`)
- [X]  T086 [P] [US4] Create `tests/governance/test_layout_matches_documentation.py` asserting the repository layout matches the documented structure (test ID: `test_repository_layout_matches_documented_structure`)
- [X]  T087 [P] [US4] Create `tests/governance/test_secret_remediation_procedure.py` asserting the secret remediation procedure exists and covers credential rotation, the `git-filter-repo` rewrite procedure, the collateral-damage count, the force-push, the GitHub Support notification, and the collaborator rebase (test ID: `test_secret_remediation_procedure_exists`)
- [X]  T088 [P] [US4] Create `tests/governance/test_no_production_access.py` asserting no production credentials, production data, or live external system is required (test ID: `test_setup_requires_no_production_access`)
- [X]  T089 [P] [US4] Create `tests/governance/test_no_real_secret_in_tracked_files.py` asserting no usable credential, key, or connection string is present in the full version-controlled history (test ID: `test_no_real_secret_in_tracked_files`)
- [X]  T090 [US4] Write `CONTRIBUTING.md` with the contributor guide: how to set up, how to run the checks, how to propose a change, and what must accompany a change beyond working code
- [X]  T091 [US4] Add the contribution rules to `CONTRIBUTING.md` covering the required checks, the documentation obligations, the approval expectations, and the conditions under which an exception is acceptable with rationale, risk, scope, owner, compensating controls, and review date
- [X]  T092 [US4] Add the rotate-first secret remediation runbook to `CONTRIBUTING.md` covering credential rotation, the `git-filter-repo` rewrite procedure, the collateral-damage count, the force-push, the GitHub Support notification, and the collaborator rebase
- [X]  T093 [US4] Document the `.gitignore` exclusions and their rationale in `CONTRIBUTING.md`
- [X]  T094 [US4] Add the link from `README.md` to `CONTRIBUTING.md` and document the accepted-exception route in both files

**Checkpoint**: All four user stories are independently functional and documented.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and close out the
Phase 0 exit gate with recorded evidence.

- [ ]  T095 [P] [Shared] Set the Status of `specs/001-project-setup/spec.md` to `Implemented` only after acceptance evidence exists — still open: the status stays `Approved` until the required checks have run on the GitHub Actions workflow and the run reference is recorded in `docs/quality/phase-0-exit-gate.md`
- [X]  T096 Run the complete required check set defined in `noxfile.py` and confirm every required check reports PASS
- [X]  T097 [P] [Shared] Reconcile `docs/constitution.md` with the ratified `.specify/memory/constitution.md` — ensure clause numbers from `docs/constitution.md` are reflected in the governance record and all SYNC Impact Report TODOs are resolved
- [X]  T098 [P] [Shared] Record the decision status of `docs/adr/ADR-0001-centralized-postgresql.md` as finally accepted or documented deferral with owner and due phase
- [X]  T099 [P] [Shared] Update `docs/quality/traceability-matrix.md` to replace any remaining placeholder rows with implemented test names and their evidence
- [X]  T100 [P] [Shared] Update `specs/001-project-setup/checklists/requirements.md` to reflect the implemented state of the specification
- [X]  T101 [P] [Shared] Run a fresh clone from scratch and verify it reaches the verified state described in the setup documentation (within 30 minutes)
- [ ]  T102 Set the Status of `specs/001-project-setup/spec.md` to `Implemented` only after acceptance evidence exists — still open for the same reason as T095

**Checkpoint**: All four user stories are independently functional and documented, and the Phase 0 exit gate is closed with recorded evidence.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — No dependencies on other stories. It consumes the configuration loader and the nox framework from Phase 2, not from another story.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) — T094 depends on T033 (User Story 1), because it adds a link from the `README.md` that US1 creates. Every other US4 task is independent of US1.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Configuration and helpers before the checks that consume them
- Check implementations before the CI workflow that invokes them
- Governance records before the evidence that cites them
- Story complete before moving to the next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T004–T008)
- All User Story 1 test tasks marked [P] can run in parallel (T022–T028), as can the local-topology task (T031)
- All User Story 2 test tasks marked [P] can run in parallel (T035–T043), as can the standalone configuration and script tasks (T047, T049–T050, T052, T054–T055, T058–T061)
- All User Story 3 test tasks marked [P] can run in parallel (T063–T073), as can the decision-record and template tasks (T075–T079)
- All User Story 4 test tasks marked [P] can run in parallel (T085–T089)
- All Polish evidence tasks marked [P] can run in parallel (T095–T098)
- Within a story, tasks touching the same file are deliberately **not** marked [P]

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create tests/governance/test_fresh_clone_setup.py asserting a person with no prior project context reaches a verified state from a fresh clone"
Task: "Create tests/governance/test_language_baseline_unchanged.py asserting the implementation-language and persistence baseline is unchanged by this phase"
Task: "Create tests/governance/test_setup_prerequisites.py asserting the setup path names the missing prerequisite"
Task: "Create tests/governance/test_setup_determinism.py asserting two independent setup paths reach an equivalent verified state"
Task: "Create tests/governance/test_example_config.py asserting the example configuration lists every required variable with its purpose"
Task: "Create tests/governance/test_config_derivation.py asserting the required checks derive every configuration value from .env.example alone"
Task: "Create tests/governance/test_gitignore_exclusions.py asserting local overrides and generated artifacts are excluded from version tracking"

# Launch the local topology alongside them (different files):
Task: "Create deploy/compose/compose.yaml with postgres:16.15-alpine"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Every task that creates a tracked file requires a matching entry in `ci/file-coverage.yml` (T056), or the `file-coverage` check fails
- Every new environment variable requires a matching entry in both `.env.example` (T017) and the configuration contract, or the `governance` check fails
