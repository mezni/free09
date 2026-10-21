# Requirements Traceability Matrix

Maintain one row per requirement or acceptance criterion. Replace sample IDs with approved identifiers as specifications are created.

## SPEC-001 — Project Setup and Governance

Spec: `specs/001-project-setup/spec.md`

| Requirement ID | Requirement summary | Spec | Acceptance criterion | Test ID | Status |
|---|---|---|---|---|---|
| FR-001 | Documented top-level layout | SPEC-001 | AC-017 | `test_repository_layout_matches_documented_structure` | Planned |
| FR-002 | Single entry-point document | SPEC-001 | AC-017 | `test_repository_layout_matches_documented_structure` | Planned |
| FR-003 | Contributor document | SPEC-001 | AC-018 | `test_contributor_docs_cover_setup_checks_and_obligations` | Planned |
| FR-004 | Contribution rules | SPEC-001 | AC-018 | `test_contributor_docs_cover_setup_checks_and_obligations` | Planned |
| FR-005 | Single documented setup path | SPEC-001 | AC-001 | `test_fresh_clone_setup_reaches_verified_state` | Planned |
| FR-006 | Setup states and verifies prerequisites | SPEC-001 | AC-002 | `test_setup_names_missing_prerequisite` | Planned |
| FR-007 | Automated formatting, lint, and test checks | SPEC-001 | AC-019 | `test_local_verification_command_runs_all_required_checks` | Planned |
| FR-008 | Minimal test suite passes | SPEC-001 | AC-019 | `test_minimal_test_suite_passes_on_empty_implementation` | Planned |
| FR-009 | Automated continuous verification on every change | SPEC-001 | AC-004 | `test_continuous_verification_accepts_and_rejects_changes` | Planned |
| FR-010 | Continuous verification rejects a failing change | SPEC-001 | AC-005 | `test_continuous_verification_accepts_and_rejects_changes` | Planned |
| FR-011 | Checks run unattended and without external network | SPEC-001 | AC-007 | `test_checks_complete_without_network_access` | Planned |
| FR-012 | Runtime and OS baselines documented | SPEC-001 | AC-002 | `test_setup_names_missing_prerequisite` | Planned |
| FR-013 | Version-controlled example configuration | SPEC-001 | AC-009 | `test_example_config_lists_all_variables_without_secrets` | Planned |
| FR-014 | Example configuration holds placeholders only | SPEC-001 | AC-009 | `test_example_config_lists_all_variables_without_secrets` | Planned |
| FR-015 | All configuration externalized and declared | SPEC-001 | AC-020 | `test_checks_derive_config_from_example` | Planned |
| FR-016 | Local overrides and generated artifacts excluded | SPEC-001 | AC-010 | `test_local_overrides_and_artifacts_are_untracked` | Planned |
| FR-017 | Automated secret detection | SPEC-001 | AC-006 | `test_secret_detection_blocks_and_redacts` | Planned |
| FR-018 | Detected secrets are never printed | SPEC-001 | AC-006 | `test_secret_detection_blocks_and_redacts` | Planned |
| FR-019 | Documented secret remediation procedure | SPEC-001 | AC-021 | `test_secret_remediation_procedure_exists` | Planned |
| FR-020 | Exactly one constitution document | SPEC-001 | AC-012 | `test_single_constitution_with_version_and_ratification` | Planned |
| FR-021 | Build plan stating phases and exit gates | SPEC-001 | AC-022 | `test_build_plan_states_phases_and_exit_gates` | Planned |
| FR-022 | Templates for the required document types | SPEC-001 | AC-011 | `test_templates_contain_only_placeholders` | Planned |
| FR-023 | Templates hold unfilled placeholders only | SPEC-001 | AC-011 | `test_templates_contain_only_placeholders` | Planned |
| FR-024 | At least one completed architecture decision record | SPEC-001 | AC-023 | `test_completed_decision_record_matches_template` | Planned |
| FR-025 | Numbered feature directories | SPEC-001 | AC-013 | `test_feature_directories_are_numbered_and_complete` | Planned |
| FR-026 | Documented feature numbering convention | SPEC-001 | AC-013 | `test_feature_directories_are_numbered_and_complete` | Planned |
| FR-027 | Open questions carry an owner and a due phase | SPEC-001 | AC-014 | `test_open_questions_have_owner_and_due_phase` | Planned |
| FR-028 | Documented precedence order | SPEC-001 | AC-015 | `test_precedence_order_resolves_documented_conflict` | Planned |
| FR-029 | Requirement-to-verification linkage | SPEC-001 | AC-024 | `test_requirement_to_test_mapping_exists` | Planned |
| FR-030 | Feature quality checklist alongside the specification | SPEC-001 | AC-024 | `test_requirement_to_test_mapping_exists` | Planned |
| FR-031 | Recorded exit-gate evidence | SPEC-001 | AC-014 | `test_exit_gate_evidence_recorded_for_every_condition` | Planned |
| FR-032 | Every phase artefact covered by a gate condition or exemption | SPEC-001 | AC-025 | `test_every_phase_artifact_covered_by_gate_or_exemption` | Planned |
| BR-001 | No secret material in version-controlled history | SPEC-001 | — | `test_no_secret_material_in_full_history` | Planned |
| BR-002 | Setup path is deterministic | SPEC-001 | AC-003 | `test_two_independent_setups_reach_equivalent_state` | Planned |
| BR-003 | A failed or inconclusive check blocks a merge | SPEC-001 | AC-008 | `test_failed_or_inconclusive_check_blocks_merge` | Planned |
| BR-004 | Checks reproducible locally with the same result | SPEC-001 | AC-016 | `test_local_result_matches_automated_result` | Planned |
| BR-005 | Minimal suite passes on an empty implementation | SPEC-001 | AC-019 | `test_minimal_test_suite_passes_on_empty_implementation` | Planned |
| BR-006 | Templates carry no approved content | SPEC-001 | — | `test_templates_do_not_carry_approved_content` | Planned |
| BR-007 | Configuration externalized; no real secret tracked | SPEC-001 | — | `test_no_real_secret_in_tracked_files` | Planned |
| BR-008 | Setup requires no production access | SPEC-001 | — | `test_setup_requires_no_production_access` | Planned |
| BR-009 | Precedence order resolves to one governing statement | SPEC-001 | AC-015 | `test_conflict_resolves_to_single_governing_statement` | Planned |
| BR-010 | A gate is not satisfied without full evidence | SPEC-001 | AC-014 | `test_exit_gate_evidence_recorded_for_every_condition` | Planned |
| BR-011 | No runtime endpoint or database object in this phase | SPEC-001 | — | `test_no_network_endpoint_or_database_object_introduced` | Planned |
| BR-012 | Implementation-language baseline unchanged | SPEC-001 | — | `test_implementation_language_baseline_unchanged` | Planned |
| Security controls | Third-party dependency review recorded | SPEC-001 | — | `test_dependency_review_recorded` | Planned |

## Placeholder rows — retained from the starter template

These rows predate SPEC-001 and reference feature specifications that do not yet
exist. They are **not** approved identifiers and are not yet traceable to a
real test. Each must be replaced when its feature is created, or removed.

| Requirement ID | Requirement summary | Spec | Acceptance criterion | Test ID | Status |
|---|---|---|---|---|---|
| SEC-001 | Protected endpoints require authentication | `specs/authentication/spec.md` *(not created)* | AC-SEC-001 | `test_protected_endpoint_requires_token` | Placeholder — no spec |
| SEC-002 | Agents cannot approve restricted credit memos | `specs/credit-memos/spec.md` *(not created)* | AC-CM-004 | `test_agent_cannot_approve_credit_memo` | Placeholder — no spec |
| DB-001 | Phone number is not subscriber primary key | `specs/crm-subscribers/spec.md` *(not created)* | AC-CRM-002 | `test_subscriber_uses_stable_id` | Placeholder — no spec |
| BILL-001 | Duplicate payment request has no duplicate effect | `specs/payments/spec.md` *(not created)* | AC-PAY-005 | `test_payment_idempotency` | Placeholder — no spec |
| BILL-002 | Posted ledger entries cannot be edited silently | `specs/ledger/spec.md` *(not created)* | AC-LED-003 | `test_posted_entry_immutable` | Placeholder — no spec |
| INV-001 | Provisioning failure remains distinguishable from activation | `specs/provisioning/spec.md` *(not created)* | AC-PROV-006 | `test_failed_provisioning_state` | Placeholder — no spec |
| SYN-001 | Generated relationships are valid | `specs/synthetic-data/spec.md` *(not created)* | AC-SYN-003 | `test_generated_foreign_keys_valid` | Placeholder — no spec |
| SYN-002 | Generator reset refuses production target | `specs/synthetic-data/spec.md` *(not created)* | AC-SYN-007 | `test_reset_rejects_production` | Placeholder — no spec |

## Rules

- Every MUST requirement needs an acceptance criterion.
- Every acceptance criterion needs a test or an approved manual verification.
- Mark an item complete only when evidence exists.
- Update this matrix when requirements, test names, or specifications change.
- A row in the placeholder section is not a traceability claim. Replace it when
  the feature is created; do not leave a placeholder row in the approved
  section.
