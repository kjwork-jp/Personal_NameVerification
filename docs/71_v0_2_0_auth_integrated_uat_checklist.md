# 71_v0_2_0_auth_integrated_uat_checklist.md

## 1. 目的

NameVerification v3 `v0.2.0` 認証・ユーザー管理機能の統合UATチェックリストを定義する。

対象範囲は、main after PR #142 時点で実装済みの以下とする。

- auth schema migration
- password hashing
- first-run admin setup
- password login
- role derived from users table
- user management tab
- user audit log tab
- EXE runtime migration packaging
- EXE smoke auth table check

## 2. 前提

| 項目 | 内容 |
|---|---|
| 対象ブランチ | `main` |
| 実行環境 | Windows / PowerShell |
| DB | SQLite local file |
| 対象版 | v0.2.0 UAT candidate |
| release artifact | まだ未固定。UAT後に v0.2.0-rc1 として固定する |

## 3. 事前準備

```powershell
git checkout main
git pull origin main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

既存の検証DBを使わず、UAT用に新規DBを指定する。

```powershell
$env:NAMEVERIFICATION_DB_PATH = "$PWD\tmp\uat_v020\nameverification_uat.db"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "$PWD\tmp\uat_v020\change_logs.jsonl"
```

## 4. 品質ゲート

| ID | 確認項目 | コマンド | 期待結果 | 結果 |
|---|---|---|---|---|
| QG-001 | pytest | `pytest -q` | pass | 未実施 |
| QG-002 | ruff | `ruff check .` | pass | 未実施 |
| QG-003 | black | `black --check .` | pass | 未実施 |
| QG-004 | mypy | `mypy app` | pass | 未実施 |
| QG-005 | EXE build | `.\scripts\build_exe_windows.ps1` | `dist/NameVerification.exe` 作成 | 未実施 |
| QG-006 | EXE smoke | `.\scripts\smoke_test_exe_windows.ps1` | auth系table確認までpass | 未実施 |

## 5. 初回admin setup UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| ADM-001 | users 0件時の初回setup表示 | 新規DBで `python -m app.pyside6_main` を起動 | InitialAdminSetupDialog が表示される | 未実施 |
| ADM-002 | admin作成 | operator_id / display_name / password / confirmation を入力 | admin user が作成される | 未実施 |
| ADM-003 | password confirmation不一致 | confirmationを不一致にする | 作成不可、validation message表示 | 未実施 |
| ADM-004 | 空operator_id | operator_idを空にする | 作成不可 | 未実施 |
| ADM-005 | setup後のlogin遷移 | admin作成後にloginへ進む | LoginDialog が表示される | 未実施 |

## 6. login UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| LOG-001 | 正常login | 作成済みadminでlogin | MainWindowが表示される | 未実施 |
| LOG-002 | role combo廃止 | LoginDialogを確認 | role選択UIがない | 未実施 |
| LOG-003 | 誤password | 誤passwordでlogin | login拒否 | 未実施 |
| LOG-004 | 存在しないoperator_id | 未登録operator_idでlogin | login拒否 | 未実施 |
| LOG-005 | RoleContext反映 | admin login後に権限系tabを確認 | admin操作が可能 | 未実施 |

## 7. user management UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| USR-001 | tab表示 | adminでlogin | ユーザー管理tabが表示される | 未実施 |
| USR-002 | viewer作成 | ユーザー管理でviewerを作成 | viewer userが一覧表示される | 未実施 |
| USR-003 | editor作成 | ユーザー管理でeditorを作成 | editor userが一覧表示される | 未実施 |
| USR-004 | operator_id重複 | 既存operator_idで作成 | validation/重複エラー | 未実施 |
| USR-005 | role変更 | viewerをeditorへ変更 | roleが更新される | 未実施 |
| USR-006 | user無効化 | viewerを無効化 | disabled扱いになる | 未実施 |
| USR-007 | user有効化 | disabled userを有効化 | active扱いに戻る | 未実施 |
| USR-008 | 最後のadmin降格防止 | adminが1人だけの状態で降格 | 拒否される | 未実施 |
| USR-009 | 最後のadmin無効化防止 | adminが1人だけの状態で無効化 | 拒否される | 未実施 |

## 8. role別操作 UAT

| ID | role | 確認項目 | 期待結果 | 結果 |
|---|---|---|---|---|
| RBAC-001 | viewer | 参照系tab表示 | 参照可能 | 未実施 |
| RBAC-002 | viewer | 名前登録/更新 | 不可 | 未実施 |
| RBAC-003 | viewer | restore/import | 不可 | 未実施 |
| RBAC-004 | editor | 名前登録/更新 | 可能 | 未実施 |
| RBAC-005 | editor | restore/import | 不可 | 未実施 |
| RBAC-006 | admin | destructive操作 | 可能 | 未実施 |
| RBAC-007 | non-admin | user management tab | 操作不可または表示制限 | 未実施 |
| RBAC-008 | non-admin | user audit log tab | 操作不可または表示制限 | 未実施 |

## 9. user audit log UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| AUD-001 | login_success記録 | 正常login | user_audit_logsに記録 | 未実施 |
| AUD-002 | login_failure記録 | 誤password login | user_audit_logsに記録 | 未実施 |
| AUD-003 | user_create記録 | user作成 | user_audit_logsに記録 | 未実施 |
| AUD-004 | user_role_change記録 | role変更 | user_audit_logsに記録 | 未実施 |
| AUD-005 | user_disable記録 | user無効化 | user_audit_logsに記録 | 未実施 |
| AUD-006 | password非記録 | audit before/afterを確認 | password平文が出ない | 未実施 |

## 10. migration / 既存DB互換 UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| MIG-001 | 既存v0.1.0 DB open | users無しDBを指定して起動 | migration成功 | 未実施 |
| MIG-002 | schema_migrations記録 | DB内tableを確認 | migration versionが記録される | 未実施 |
| MIG-003 | 既存データ維持 | names/titles等を確認 | 既存データが残る | 未実施 |
| MIG-004 | users 0件時setup | migration後active users 0件 | 初回admin setup表示 | 未実施 |

SQLite確認例:

```powershell
python - <<'PY'
import sqlite3
from pathlib import Path
p = Path('tmp/uat_v020/nameverification_uat.db')
con = sqlite3.connect(p)
try:
    print(con.execute("select name from sqlite_master where type='table' order by name").fetchall())
    print(con.execute("select version from schema_migrations order by version").fetchall())
finally:
    con.close()
PY
```

## 11. EXE / portable UAT

| ID | 確認項目 | 手順 | 期待結果 | 結果 |
|---|---|---|---|---|
| EXE-001 | build | `.\scripts\build_exe_windows.ps1` | EXE作成 | 未実施 |
| EXE-002 | smoke | `.\scripts\smoke_test_exe_windows.ps1` | auth tables check pass | 未実施 |
| EXE-003 | package | `.\scripts\package_release_windows.ps1 -ReleaseName v0.2.0-rc1` | release folder作成 | 未実施 |
| EXE-004 | portable smoke | `.\scripts\smoke_test_portable_release_windows.ps1 -ReleaseName v0.2.0-rc1` | pass | 未実施 |

## 12. 判定

| 判定 | 条件 |
|---|---|
| Go | QG / admin setup / login / user management / audit / migration / EXE smoke がすべてOK |
| Conditional Go | 軽微なdocs/UI文言のみ未修正で、データ破壊・認証・role・migrationに問題なし |
| No-Go | login不能、migration失敗、最後のadmin保護失敗、password平文露出、role制御崩れ、EXE smoke失敗 |

## 13. 次工程

1. 本チェックリストに沿ってUATを実施する。
2. 結果を `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` に記録する。
3. Go/Conditional Go の場合、`v0.2.0-rc1` release evidence固定へ進む。
4. No-Goの場合、不具合を1件1PRで修正する。
