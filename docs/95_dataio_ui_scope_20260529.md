# 95_dataio_ui_scope_20260529.md

## 1. Purpose

This document defines the implementation scope for `UI-DATAIO-001`.

The goal is to improve the Data I/O screen presentation without changing service calls, permission guards, path history behavior, log behavior, or confirmation behavior.

## 2. Current target

Target file:

- `app/ui/operations_tab.py`

Related tests:

- `tests/test_operations_tab_ui.py`
- `tests/test_operations_tab_compact_layout_ui.py`
- `tests/test_rbac_ui_guards.py`
- `tests/test_invalid_io_evidence.py`

## 3. Current behavior to preserve

| Area | Preserve |
|---|---|
| Export | editor/admin can run CSV, JSON, and SQL dump export |
| Backup | editor/admin can create backup |
| Restore | admin only |
| Import | admin only |
| Viewer | no export, backup, restore, or import execution |
| Recent paths | max 5, de-duplication, tuple/blank normalization |
| Operation logs | pagination, filtering, source switching, export |
| Busy state | blocks other operations and enables cancel |
| Confirmation | restore/import confirmation behavior remains unchanged |

## 4. UI problems

| ID | Problem |
|---|---|
| DATAIO-UX-001 | Screen starts directly with a dense 2-column operation grid and lacks a clear page-level explanation |
| DATAIO-UX-002 | Export/Backup/Restore/Import groups are compact but still read like implementation blocks |
| DATAIO-UX-003 | Restore and Import are visually marked as destructive, but the safe flow is not obvious enough |
| DATAIO-UX-004 | Result message area is small and looks like a raw log buffer |
| DATAIO-UX-005 | Operations log controls are dense and should be treated as a secondary section |

## 5. Approved implementation slices

Apply in small commits, with Quality Gates after each commit.

### Slice 1: Page-level guide only

Add a top-level explanatory label or `PageHeader` above the operation grid.

Allowed changes:

- Add a page title/description.
- Keep `operations_grid` as `root.itemAt(0)` only if tests are updated intentionally, or add the header in a way that updates the compact-layout test.
- Do not change buttons, service calls, role guards, or confirmation dialogs.

### Slice 2: Group descriptions

Add one short description per group:

| Group | Description |
|---|---|
| Export | Output current data for review or migration. |
| Backup | Copy the current DB before risky work. |
| Restore | Replace a target DB from a backup. Admin only. |
| Import | Load CSV/JSON into an initial or prepared DB. Admin only. |

Allowed changes:

- Add labels inside each group.
- Keep all field labels and button object references unchanged.

### Slice 3: Result section polish

Improve the result area without changing `_set_message` semantics.

Allowed changes:

- Add a label such as `実行結果` above `result_view`.
- Keep `[OK]` and `[ERROR]` message prefixes unchanged.
- Keep `result_view.maximumHeight() == 72` unless tests are updated intentionally.

### Slice 4: Operations log section polish

Improve readability of the log section without changing filtering/pagination behavior.

Allowed changes:

- Add a short hint label under the group title.
- Keep current controls and signal connections unchanged.

## 6. Non-goals

Do not change these in `UI-DATAIO-001`:

- Service method names or call order
- Path conversion logic
- Recent path storage keys
- Permission guards
- Confirmation text semantics
- Log event schema
- Import/restore safety logic

## 7. Recommended next commit

Start with Slice 1 only.

Expected commit message:

```text
feat: add data io page guidance
```

Expected tests to update:

- `tests/test_operations_tab_compact_layout_ui.py`

Expected Quality Gates:

- pytest
- ruff
- black
- mypy

## 8. Exit criteria

`UI-DATAIO-001` can move to `FIX PARTIAL / UAT REQUIRED` when:

- Slice 1 and Slice 2 pass Quality Gates.
- UAT confirms the screen is easier to understand without changing permissions.

`UI-DATAIO-001` can move to `FIX APPLIED / UAT REQUIRED` when:

- Slices 1 through 4 pass Quality Gates.
- UAT confirms export, backup, restore, import, and log review are understandable.
