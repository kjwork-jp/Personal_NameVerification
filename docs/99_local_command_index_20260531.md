# 99_local_command_index_20260531.md

## 1. Purpose

This document is the GitHub source of truth for local commands and script procedures used to verify, operate, package, and review Personal_NameVerification.

External ledgers should only point to this document or keep a small local DOCX copy for offline use.

## 2. Base assumptions

Run commands from the repository root:

```powershell
C:\Users\nkaji\Documents\GitHub\Personal_NameVerification
```

The user requested that repeated `cd` and venv activation steps may be skipped in future instructions.

If needed, activate the venv once:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Sync commands

### 3.1 Pull latest main

```powershell
git pull --ff-only
```

Expected result:

- Fast-forward or `Already up to date`.
- No merge commit is created.

### 3.2 Check local Git state

```powershell
git status
```

Expected result:

- `working tree clean` when no local change remains.

## 4. App launch commands

### 4.1 UAT demo reset and launch

```powershell
.\scripts\reset_uat_demo_windows.ps1 -Launch
```

Use this for repeatable UAT screenshots. It resets the UAT/demo state and launches the app.

### 4.2 Normal launch with current DB

```powershell
python -m app.pyside6_main
```

Use this when you do not want to reset the current local database.

### 4.3 Direct fallback launch

```powershell
python app\pyside6_main.py
```

Use only when module launch is inconvenient.

## 5. Focused test commands

### 5.1 Subtitle cross-parent search test

```powershell
python -m pytest tests/test_subtitle_management_tab_ui.py -q
```

Latest local evidence:

```text
.. [100%]
```

### 5.2 Title/subtitle UI related tests

```powershell
python -m pytest tests/test_subtitle_management_tab_ui.py tests/test_title_subtitle_management_tab_ui.py -q
```

### 5.3 Data I/O and operations UI tests

```powershell
python -m pytest tests/test_operations_guidance.py tests/test_operations_guidance_widgets.py tests/test_operations_tab_navigation.py -q
```

### 5.4 Audit UI tests

```powershell
python -m pytest tests/test_audit_log_tab_ui.py -q
```

### 5.5 Broad UI regression set

```powershell
python -m pytest tests/test_subtitle_management_tab_ui.py tests/test_title_subtitle_management_tab_ui.py tests/test_operations_tab_navigation.py tests/test_audit_log_tab_ui.py -q
```

### 5.6 Full pytest

```powershell
python -m pytest -q
```

## 6. Quality Gates local approximation

Run this when you want to approximate CI locally:

```powershell
python -m pytest -q
python -m ruff check .
python -m black --check .
python -m mypy
```

If any command fails, do not treat the local state as release-clean.

## 7. Manual UAT screenshot checklist

### 7.1 Data I/O

1. Launch the app.
2. Login as admin.
3. Open Data I/O.
4. Confirm Guide, Export, Backup, Restore, Import, Operations Log tabs.
5. Run Export or Backup once.
6. Confirm the result area shows `[OK]`.

### 7.2 Subtitle management

1. Open Subtitle Management.
2. Open List.
3. Confirm cross-parent search box exists.
4. Search by parent title, subtitle name, code, status, or note.
5. Open Add and confirm parent title candidates.
6. Open Edit and confirm selected-title summary and selected-subtitle summary.
7. Open Delete and confirm target subtitle summary.

### 7.3 Login

1. Launch the app.
2. Confirm Windows and local login sections are visible.
3. Login.
4. Confirm role context appears in the main window.

### 7.4 Audit

1. Open Audit Log.
2. Select one audit row.
3. Confirm readable diff/before/after sections.
4. Audit export evidence is optional unless required by release policy.

## 8. DB count audit commands

Use this only when verifying whether parent-title candidates and subtitle counts match DB records.

### 8.1 Count active and deleted titles

```powershell
python - <<'PY'
import sqlite3
from pathlib import Path

candidates = [
    Path('data/uat_demo.db'),
    Path('data/app.db'),
    Path('app.db'),
]
for path in candidates:
    if path.exists():
        db = path
        break
else:
    raise SystemExit('DB file not found. Check the local DB path.')

con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
print(f'DB: {db}')
for row in con.execute('''
    SELECT
      COUNT(*) AS total_titles,
      SUM(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS active_titles,
      SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS deleted_titles
    FROM titles
'''):
    print(dict(row))
PY
```

Interpretation:

- Add-subtitle parent combo should match active titles plus `未選択`.
- Edit title combo should match all titles plus `未選択`.
- Delete target title combo should match all titles plus `未選択`.

### 8.2 Count subtitles by parent title

```powershell
python - <<'PY'
import sqlite3
from pathlib import Path

candidates = [
    Path('data/uat_demo.db'),
    Path('data/app.db'),
    Path('app.db'),
]
for path in candidates:
    if path.exists():
        db = path
        break
else:
    raise SystemExit('DB file not found. Check the local DB path.')

con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
print(f'DB: {db}')
for row in con.execute('''
    SELECT
      t.title_name,
      COUNT(s.id) AS subtitle_total,
      SUM(CASE WHEN s.deleted_at IS NULL THEN 1 ELSE 0 END) AS subtitle_active,
      SUM(CASE WHEN s.deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS subtitle_deleted
    FROM titles t
    LEFT JOIN subtitles s ON s.title_id = t.id
    GROUP BY t.id, t.title_name
    ORDER BY t.title_name
'''):
    print(dict(row))
PY
```

Interpretation:

- Edit/delete subtitle candidates are scoped to the selected parent title.
- The cross-parent list tab is the place to search across all parent titles.

## 9. Screenshot and ZIP commands

### 9.1 Compress screenshot folder

Place screenshots under `screens_uat`, then run:

```powershell
Compress-Archive -Path .\screens_uat\* -DestinationPath .\screens_uat_$(Get-Date -Format yyyyMMdd_HHmmss).zip -Force
```

### 9.2 Check ZIP hash

```powershell
Get-FileHash .\screens_uat_YYYYMMDD_HHMMSS.zip -Algorithm SHA256
```

## 10. External ledger package checks

### 10.1 Verify minimal external-ledger package hash

```powershell
Get-FileHash .\52_名前解決アプリ_外部台帳_最小構成_20260531.zip -Algorithm SHA256
```

### 10.2 What to check manually

1. `00_README_外部台帳最小構成_20260531.md` exists.
2. `NameVerification_外部管理ミニ台帳_20260531.xlsx` opens.
3. `NameVerification_v3_手元確認スクリプト集_20260531.docx` opens.
4. `manifest_20260531.csv` exists.
5. `checksums_sha256_20260531.txt` exists.

## 11. Current remaining command-related work

| ID | Treatment |
|---|---|
| LOCAL-GIT-PULL-DOCS99 | Run `git pull --ff-only` when ready. |
| LOCAL-MIN-LEDGER-REVIEW | Download and inspect the minimal external-ledger ZIP. |
| PARENT-TITLE-COUNT-AUDIT | Optional DB count audit if the combo candidate count is still concerning. |
| AUDIT-EXPORT-EVIDENCE-OPTIONAL | Optional audit export screenshot/file evidence. |
