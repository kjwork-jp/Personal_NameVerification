# 72_v0_2_0_auth_integrated_uat_execution_record.md

## 1. 目的

`docs/71_v0_2_0_auth_integrated_uat_checklist.md` に基づき、NameVerification v3 `v0.2.0` 認証・ユーザー管理統合UATの実行結果を記録する。

この文書は、UAT実施時に結果・証跡・不具合・Go/No-Go判定を残すための記録表である。最新の横断状況は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` も参照する。

---

## 2. 実行サマリ

| 項目 | 記録 |
|---|---|
| 実行日 | 2026-05-18 |
| 実行者 | NAOKI KAJIWARA |
| 対象branch | `main` |
| 対象commit | `4f4c1d9` 以降（login context表示、RBAC UI hardening、現況台帳更新反映済み） |
| Python | 3.13.1 |
| OS | Windows 11 |
| DB path | `tmp/exe_smoke/nameverification_smoke.db` / GUI UAT DB path: `tmp/exe_smoke/nameverification_smoke.db` |
| change log JSONL path | `tmp/uat_v020_gui/change_logs.jsonl` |
| EXE path | `dist/NameVerification.exe` |
| release candidate | v0.2.0 UAT candidate |
| 総合判定 | UAT継続（viewer主要RBACはOK。editor画面表示は一部OK。editor/admin実行UAT、品質ゲート再実行、portable未完） |

---

## 3. 事前確認ログ

```powershell
git checkout main
git pull origin main
git log --oneline -n 12
python --version
python -m pip --version
```

実行結果:

```text
git pull origin main: Fast-forward updates confirmed across UAT patches
4f4c1d9 feat: show current login context in main window
61137aa fix: satisfy ruff in RBAC UI guards
73cb7a6 fix: apply strict RBAC guards to operations tab
fb82a83 feat: add UI RBAC hardening helpers
5f73815 fix: disable title and subtitle edit inputs for viewer role
efb88be fix: disable name edit inputs for viewer role
f8cd14a fix: disable link edit controls for unauthorized roles
47c868d fix: disable user audit filters for non-admin roles
python --version: Python 3.13.1
python -m pip --version: 未記入
```

---

## 4. UAT用環境変数

```powershell
$env:NAMEVERIFICATION_DB_PATH = "$PWD\tmp\uat_v020\nameverification_uat.db"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "$PWD\tmp\uat_v020\change_logs.jsonl"
```

実行結果:

```text
EXE smokeは script 管理の isolated smoke database path を使用。
GUI UATでは tmp/exe_smoke/nameverification_smoke.db を使用したスクリーンショット確認あり。
```

---

## 5. 品質ゲート結果

| ID | 確認項目 | コマンド | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| QG-001 | pytest | `pytest -q` | pass | OK | `.................................................................................................................... [ 69%]` / `[100%]` |
| QG-002 | ruff | `ruff check .` | pass | 一度NG→修正済み | `rbac_ui_guards.py` の未使用変数2件、行長1件。`61137aa` で修正済み |
| QG-003 | black | `black --check .` | pass | OK | `All done!` / `26 files would be left unchanged.` |
| QG-004 | mypy | `mypy app` | pass | OK | `Success: no issues found in 54 source files` |
| QG-005 | EXE build | `.\scripts\build_exe_windows.ps1` | EXE作成 | OK | `Build complete: dist/NameVerification.exe` |
| QG-006 | EXE smoke | `.\scripts\smoke_test_exe_windows.ps1` | auth tables check pass | OK | `Smoke database tables OK: app_settings, schema_migrations, user_audit_logs, users` |
| QG-007 | 最新docs/UI更新後品質ゲート | `pytest -q` / `ruff check .` / `black --check .` / `mypy app` | pass | 要再実行 | `4f4c1d9`、`f926be4`、`6abc7e1`、`f0c4661` 以降で再実行が必要 |

---

## 6. 初回admin setup結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| ADM-001 | users 0件時の初回setup表示 | InitialAdminSetupDialog 表示 | OK | screenshot確認: 初回管理者作成dialog表示 |
| ADM-002 | admin作成 | admin user 作成 | OK | screenshot確認: admin / admin がユーザー一覧に表示 |
| ADM-003 | password confirmation不一致 | 作成不可 | 未実施 |  |
| ADM-004 | 空operator_id | 作成不可 | 未実施 |  |
| ADM-005 | setup後のlogin遷移 | LoginDialog 表示 | OK | screenshot確認: login dialog表示 |

---

## 7. login結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| LOG-001 | 正常login | MainWindow表示 | OK | screenshot確認: NameVerification v3 MainWindow表示 |
| LOG-002 | role combo廃止 | role選択UIなし | OK | LoginDialogは操作者ID/passwordのみ |
| LOG-003 | 誤password | login拒否 | 未実施 |  |
| LOG-004 | 未登録operator_id | login拒否 | 未実施 |  |
| LOG-005 | RoleContext反映 | admin/viewer/editor別UI反映 | OK | viewer/editor/admin別のUI状態を一部確認 |
| LOG-006 | ログイン中ユーザー表示 | title bar/status barにoperator_id/role表示 | OK | `NameVerification v3 - ログイン中: editor / 権限: editor` と下部status表示を確認 |

---

## 8. user management結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| USR-001 | tab表示 | ユーザー管理tab表示 | OK | screenshot確認 |
| USR-002 | viewer作成 | viewer user一覧表示 | OK | screenshot確認: admin / editor / viewer の3件表示 |
| USR-003 | editor作成 | editor user一覧表示 | OK | screenshot確認: admin / editor / viewer の3件表示 |
| USR-004 | operator_id重複 | 重複エラー | OK | screenshot確認: `operator_id already exists` |
| USR-005 | role変更 | role更新 | 未実施 |  |
| USR-006 | user無効化 | disabled扱い | 未実施 |  |
| USR-007 | user有効化 | active扱い | 未実施 |  |
| USR-008 | 最後のadmin降格防止 | 拒否 | 未実施 |  |
| USR-009 | 最後のadmin無効化防止 | 拒否 | 未実施 |  |
| USR-010 | ユーザー管理ガイド | 固定表示ではなくサブタブ表示 | OK | `ガイド` / `ユーザー作成` / `ユーザー一覧` / `選択ユーザー操作` を確認 |
| USR-011 | viewer/editorでユーザー管理 | 操作不可 | viewer OK / editor OK | 警告表示、作成/操作系disabledを確認 |

---

## 9. role別操作結果

| ID | role | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| RBAC-001 | viewer | 参照系tab表示 | 参照可能 | OK | 検索/操作履歴/ヘルプ/設定は参照可能 |
| RBAC-002 | viewer | 名前登録/更新/削除 | 不可 | OK | 名前/備考/操作者ID/新規作成/更新/ゴミ箱に入れるがdisabled |
| RBAC-003 | viewer | タイトル/サブタイトル登録/更新/削除 | 不可 | OK | タイトル名/備考/関連付ける名前/管理番号/サブタイトル名/表示順/備考/作成/更新/削除がdisabled |
| RBAC-004 | viewer | 関連付け登録/解除 | 不可 | OK | 登録/解除系入力欄とボタンがdisabled。警告表示あり |
| RBAC-005 | viewer | export/backup/import/restore/log export | 不可 | OK | データ入出力でパス入力/参照/履歴削除/出力/backup/restore/import/log exportがdisabled。Operationsログ参照は可 |
| RBAC-006 | viewer | user management tab | 操作不可 | OK | 警告表示、操作系disabled |
| RBAC-007 | viewer | user audit log tab | 操作不可/内容非表示 | OK | フィルタ/一覧更新/一覧がdisabled。警告表示 |
| RBAC-008 | editor | 名前登録/更新 | 可能 | UI表示OK / 実行未実施 | 新規作成/更新が有効表示、ゴミ箱に入れるは無効表示 |
| RBAC-009 | editor | タイトル/サブタイトル登録/更新 | 可能 | UI表示OK / 実行未実施 | 作成/更新系が有効表示、削除系は無効表示 |
| RBAC-010 | editor | 関連付け登録 | 可能 | UI表示OK / 実行未実施 | 登録ボタン有効、解除系は未確認/要実行確認 |
| RBAC-011 | editor | export/backup | 可能 | UI表示OK / 実行未実施 | CSV/JSON/SQL出力、バックアップ作成が有効表示 |
| RBAC-012 | editor | restore/import/destructive | 不可 | UI表示OK / 実行未実施 | 復元/CSV取込/JSON取込は無効表示 |
| RBAC-013 | editor | user management / user audit log | 不可 | OK | 警告表示、操作系disabled |
| RBAC-014 | admin | destructive操作 | 可能 | 一部OK | adminでユーザー管理tab操作可能。restore/import等は未実施 |

---

## 10. user audit log結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| AUD-001 | login_success記録 | user_audit_logsに記録 | OK | screenshot確認: `login_success` 表示 |
| AUD-002 | login_failure記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-003 | user_create記録 | user_audit_logsに記録 | OK | screenshot確認: `user_create` 表示 |
| AUD-004 | user_role_change記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-005 | user_disable記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-006 | password非記録 | password平文が出ない | 未判定 | screenshot範囲ではpassword平文は見えないが、全JSON確認は未実施 |
| AUD-007 | viewer/editorでユーザー監査ログ | 操作不可/内容非表示 | viewer OK / editor OK | viewer/editorではフィルタ/一覧更新/一覧がdisabled |

---

## 11. migration / 既存DB互換結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| MIG-001 | 既存v0.1.0 DB open | migration成功 | 未実施 |  |
| MIG-002 | schema_migrations記録 | migration version記録 | OK | EXE smokeで `schema_migrations` table存在を確認 |
| MIG-003 | 既存データ維持 | 既存データが残る | 未実施 |  |
| MIG-004 | users 0件時setup | 初回admin setup表示 | OK | screenshot確認 |

SQLite確認結果:

```text
Smoke database tables OK: app_settings, schema_migrations, user_audit_logs, users
```

---

## 12. EXE / portable結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| EXE-001 | build | EXE作成 | OK | `Build complete: dist/NameVerification.exe` |
| EXE-002 | smoke | auth tables check pass | OK | `Smoke database tables OK: app_settings, schema_migrations, user_audit_logs, users` |
| EXE-003 | package | release folder作成 | 未実施 |  |
| EXE-004 | portable smoke | pass | 未実施 |  |

---

## 13. 不具合・課題一覧

| ID | 区分 | 重大度 | 内容 | 再現手順 | 対応方針 | 状態 |
|---|---|---|---|---|---|---|
| BUG-001 | UI | 高 | ユーザー作成用operator入力欄が非表示になる | ユーザー管理 > ユーザー作成 | `operator_input` を `create_operator_input` へ改名 | closed |
| BUG-002 | UI/RBAC | 高 | viewerで一部更新系入力欄・参照・履歴削除が操作可能に見える | viewer login後、名前/タイトル/サブタイトル/関連付け/データ入出力を確認 | UI-level RBAC hardeningを実施 | closed |
| BUG-003 | UI | 中 | ログイン中ユーザー/権限が分かりにくい | editor/viewer/adminで複数タブを確認 | title bar/status barにoperator_id/roleを常時表示 | closed |
| UAT-REMAIN-001 | UAT残 | 中 | validation系、editor実行、role変更、無効化/有効化、最後のadmin保護、既存DB migration、portable package smoke が未実施 | docs/71に従う | 次工程で実施 | open |
| UAT-REMAIN-002 | 品質ゲート残 | 中 | 最新docs/UI更新後の品質ゲート再実行が必要 | `4f4c1d9` 以降で再実行 | pytest/ruff/black/mypy | open |
| UI-IMPROVE-001 | UI改善 | 中 | データ入出力/削除データ/通常CRUD系のサブタブ化が未完 | 画面操作時に混在感あり | docs/73/75に従い順次実施 | open |

---

## 14. Go / No-Go判定

| 判定項目 | 判定 | コメント |
|---|---|---|
| 品質ゲート | 要再実行 | 初期品質ゲートはOK。最新docs/UI更新後に再実行が必要 |
| 初回admin setup | 一部OK | 初回表示、admin作成、login遷移OK。validation系は未実施 |
| login | 一部OK | 正常login、role combo廃止、RoleContext反映、ログイン状態表示OK。異常系は未実施 |
| user management | 一部OK | admin/viewer/editor作成、重複エラー、viewer/editor操作不可はOK。role変更/無効化/有効化/最後のadmin保護は未実施 |
| role別操作 | 一部OK | viewer RBAC主要タブはOK。editorはUI表示一部OK、実行UAT未実施。admin詳細は未実施 |
| user audit log | 一部OK | login_success/user_create表示OK。viewer/editor操作不可OK。異常系・role変更等は未実施 |
| migration | 一部OK | auth tables存在確認OK。既存DB互換は未実施 |
| EXE / portable | 一部OK | EXE build/smoke OK。package/portable smokeは未実施 |
| 総合判定 | UAT継続 | viewer RBAC主要blockerとログイン状態表示は解消。editor/admin/portable/quality再確認後にGo/No-Go判定 |

判定基準:

| 判定 | 条件 |
|---|---|
| Go | QG / admin setup / login / user management / audit / migration / EXE smoke がすべてOK |
| Conditional Go | 軽微なdocs/UI文言のみ未修正で、データ破壊・認証・role・migrationに問題なし |
| No-Go | login不能、migration失敗、最後のadmin保護失敗、password平文露出、role制御崩れ、EXE smoke失敗 |

---

## 15. 次工程

- 直近の次工程
  - 最新mainの品質ゲートを再実行する。
  - editor role UATを実施する。
    - 名前/タイトル/サブタイトルの通常登録・更新が可能。
    - 関連付け登録が可能。
    - 削除/復元/完全削除/関連解除/import/restore/ユーザー管理/ユーザー監査ログは不可。
    - export/backupは可能。
  - admin role UATを実施する。
    - destructive/import/restore/ユーザー管理/ユーザー監査ログが可能。
    - 最後の有効管理者は降格・無効化できない。
  - `データ入出力` / `削除データ` のサブタブ分割を進める。
  - `v0.2.0-rc1` package生成とportable smokeを実施する。
- Go / Conditional Go の場合
  - `v0.2.0-rc1` packaging
  - portable smoke
  - manifest/checksum生成
  - release evidence文書作成
- No-Go の場合
  - 不具合を1件1PRまたはmain直接patchで修正
  - 再UAT
