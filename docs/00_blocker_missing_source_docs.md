# Blocker: Missing source specification documents

Date: 2026-04-16 (UTC)

The repository is currently empty except for `.gitkeep`.

The implementation prompt requires reading the following files before any coding:

- `docs/02_document_priority_order.md`
- `docs/00_repository_master_spec.md`
- `docs/01_role_responsibility_matrix.md`
- `docs/10_requirements_definition.md`
- `docs/11_acceptance_criteria.md`
- `docs/12_basic_design.md`
- `docs/13_detailed_technical_design.md`
- `docs/14_ui_ux_design.md`
- `docs/15_data_design.md`
- `docs/16_error_handling_policy.md`
- `docs/18_search_behavior_spec.md`
- `docs/19_permissions_rbac_spec.md`
- `docs/20_icon_file_handling_spec.md`
- `docs/30_development_process_map.md`
- `docs/31_branch_and_pr_policy.md`
- `docs/32_coding_rules.md`
- `docs/33_directory_structure_policy.md`
- `docs/34_definition_of_done.md`
- `docs/35_definition_of_ready.md`
- `docs/39_dependency_policy.md`
- `docs/40_test_strategy.md`
- `docs/41_test_level_matrix.md`
- `docs/43_review_checklist.md`
- `docs/44_final_review_checklist.md`
- `docs/50_operations_design.md`
- `docs/51_backup_restore_policy.md`
- `docs/52_logging_audit_policy.md`
- `docs/53_release_and_deployment_policy.md`
- `docs/54_go_live_checklist.md`
- `prompts/01_codex_work_rules.md`
- `prompts/02_codex_pr_template.md`
- `prompts/03_codex_task_split_examples.md`
- `prompts/04_codex_no_assumption_rules.md`
- `prompts/00_codex_bootstrap_prompt.md`

None of these files exist in the current branch.

## Impact

- Specification-driven implementation cannot start safely.
- Any implementation at this point would violate the "no assumption" constraint.

## Requested next action

Add the required `docs/` and `prompts/` files to the repository, then proceed with the first scoped PR (recommended: `chore/bootstrap-python-project`).
