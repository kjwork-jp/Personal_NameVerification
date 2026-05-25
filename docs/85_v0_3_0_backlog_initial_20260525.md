# 85_v0_3_0_backlog_initial_20260525.md

## Baseline

- Stable baseline: v0.2.0
- Stable release status: complete
- Required v0.2.0 P1 items: complete
- Next development target: v0.3.0

## Initial backlog

| ID | Priority | Area | Candidate |
|---|---:|---|---|
| V030-OPS-001 | P1 | Release | Automate stable release packaging flow |
| V030-OPS-002 | P1 | Release | Generate release verification checklist |
| V030-TEST-001 | P1 | Test | Add richer portable smoke coverage |
| V030-UX-001 | P1 | UI | Redesign CRUD screens as native list-first flows |
| V030-SEC-001 | P1 | Security/Ops | Add optional Windows file-permission diagnostics |
| V030-DOC-001 | P2 | Docs | Split user manual from release ledger |
| V030-DATA-001 | P2 | Data | Add sample database generation mode |
| V030-MAINT-001 | P2 | Maintenance | Review obsolete checkpoint docs |

## Suggested first iteration

1. V030-OPS-001
2. V030-TEST-001
3. V030-UX-001
4. V030-SEC-001

## Policy

- Keep v0.2.0 as the stable baseline.
- Use a separate branch or direct-main workflow only after deciding the next implementation item.
- Use hotfix scope only if v0.2.0 requires urgent correction.
