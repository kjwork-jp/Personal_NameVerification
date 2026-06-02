# 100_uat_script_chain_20260602.md

## 前提

通常の手元UAT指示では、以下は実施済みとして扱う。

```powershell
cd C:\Users\nkaji\Documents\GitHub\Personal_NameVerification
.\.venv\Scripts\Activate.ps1
```

## 通常UAT: ソース起動

```powershell
git status
python -m ruff check .
python -m black --check .
python -m mypy app
python -m pytest -q
.\scripts\reset_uat_demo_windows.ps1 -Launch
git status
```

## 高速UAT: CSV生成なし

```powershell
git status
python -m pytest -q
.\scripts\reset_uat_demo_windows.ps1 -SkipCsv -Launch
git status
```

## Rich Admin UI focused UAT

```powershell
python -m pytest tests/test_rich_search_tab_ui.py tests/test_table_microcopy_ui.py tests/test_navigation_polish_ui.py -q
.\scripts\reset_uat_demo_windows.ps1 -SkipCsv -Launch
```

## UAT DBだけ作ってから起動

```powershell
.\scripts\reset_uat_demo_windows.ps1
$env:NAMEVERIFICATION_DB_PATH = "tmp\uat_demo.db"
python -m app.pyside6_main
Remove-Item Env:NAMEVERIFICATION_DB_PATH -ErrorAction SilentlyContinue
```

## EXE/portable release UAT

```powershell
$ReleaseName = "v0.3.0-ui-polish-uat"
.\scripts\build_exe_windows.ps1
.\scripts\smoke_test_exe_windows.ps1
.\scripts\package_release_windows.ps1 -ReleaseName $ReleaseName
.\scripts\smoke_test_portable_windows.ps1 -ReleaseName $ReleaseName -StartupSeconds 5
```

## 一括release workflow

```powershell
.\scripts\run_release_windows.ps1 -ReleaseName "v0.3.0-ui-polish-uat" -StartupSeconds 5
```

## UAT後のclean確認

```powershell
git status
git restore -- logs/change_logs.jsonl nameverification.db
Remove-Item .\50_backups -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\60_exports -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\tmp -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\audit_logs_review.json -Force -ErrorAction SilentlyContinue
git status
```
