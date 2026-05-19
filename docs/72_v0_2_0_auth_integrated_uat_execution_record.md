# 72_v0_2_0_auth_integrated_uat_execution_record.md

## 1. 目的

`docs/71_v0_2_0_auth_integrated_uat_checklist.md` に基づき、NameVerification v3 `v0.2.0` 認証・ユーザー管理統合UATの実行結果を記録する。

この文書は、UAT実施時に結果・証跡・不具合・Go/No-Go判定を残すための記録表である。最新の横断状況は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` も参照する。

---

## 2. 実行サマリ

| 項目 | 記録 |
|---|---|
| 実行日 | 2026-05-18〜2026-05-19 |
| 実行者 | NAOKI KAJIWARA |
| 対象branch | `main` |
| 対象commit | `02f65c4` / `4b0039c` / `14bb066` 以降は再pull・再ゲート確認待ち |
| Python | 3.13.1 |
| OS | Windows 11 |
| DB path | `C:\Users\nkaji\Documents\GitHub\Personal_NameVerification\nameverification.db` ほかUAT用DB |
| change log JSONL path | `logs\change_logs.jsonl` ほかUAT用JSONL |
| release candidate | v0.2.0 UAT candidate |
| 総合判定 | UAT継続。P0/P1主要UI/RBAC/DB自動テストは前進。アカウント切替の終了性、login異常系、最後のadmin保護、portable smoke、release evidenceが残件 |

---

## 3. 事前確認ログ

```powershell
git checkout main
git pull origin main
black --check .
ruff check .
mypy app
pytest -q
python -m app.pyside6_main
```

実行結果要約:

```text
2026-05-19 時点で複数回、black / ruff / mypy / pytest は全OKを確認。
一度 `app/pyside6_main.py` が black 要整形となったため、`02f65c4` で整形反映。
`02f65c4` と docs更新後は再度ローカル品質ゲート確認が必要。
```

---

## 4. UAT用環境変数

```powershell
$env:NAMEVERIFICATION_DB_PATH = "$PWD\tmp\uat_v020\nameverification_uat.db"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "$PWD\tmp\uat_v020\change_logs.jsonl"
$env:NAMEVERIFICATION_OPERATIONS_LOG_JSONL_PATH = "$PWD\tmp\uat_v020\operations_events.jsonl"
```

実行結果:

```text
GUI UATでは通常DBと一時DBの双方で確認あり。
portable package smokeは script 実装済みだが、release package 実体での実行は未完。
```

---

## 5. 品質ゲート結果

| ID | 確認項目 | コマンド | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| QG-001 | pytest | `pytest -q` | pass | OK | 2026-05-19時点で `[100%]` passを複数回確認 |
| QG-002 | ruff | `ruff check .` | pass | OK | 複数回NG発生後、都度修正済み。直近はOK |
| QG-003 | black | `black --check .` | pass | 一度NG→修正済み | `app/pyside6_main.py` が要整形。`02f65c4` で反映 |
| QG-004 | mypy | `mypy app` | pass | OK | `Success: no issues found in 61 source files` |
| QG-005 | GUI起動 | `python -m app.pyside6_main` | 起動 | OK | 起動は確認済み |
| QG-006 | GUI通常終了 | `python -m app.pyside6_main` | 終了後PowerShell復帰 | 要再確認 | アカウント切替周辺でプロセス残存報告あり |
| QG-007 | 最新docs/format後品質ゲート | `black` / `ruff` / `mypy` / `pytest` | pass | 要再実行 | `02f65c4` / docs更新後に再確認 |

---

## 6. 初回admin setup結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| ADM-001 | users 0件時の初回setup表示 | InitialAdminSetupDialog 表示 | OK | 初回管理者作成dialog表示を確認 |
| ADM-002 | admin作成 | admin user 作成 | OK | admin / admin がユーザー一覧に表示 |
| ADM-003 | password confirmation不一致 | 作成不可 | 未実施 | login異常系UATへ残す |
| ADM-004 | 空operator_id | 作成不可 | 未実施 | login異常系UATへ残す |
| ADM-005 | setup後のlogin遷移 | LoginDialog 表示 | OK | login dialog表示を確認 |

---

## 7. login / account switch結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| LOG-001 | local正常login | MainWindow表示 | OK | admin/editor/viewerで確認 |
| LOG-002 | role combo廃止 | role選択UIなし | OK | LoginDialogはlocal認証とWindows認証の選択式 |
| LOG-003 | 誤password | login拒否 | 未実施 | `AUTH-002` |
| LOG-004 | 未登録operator_id | login拒否 | 未実施 | `AUTH-002` |
| LOG-005 | RoleContext反映 | admin/viewer/editor別UI反映 | OK | title/status/tab表示で確認 |
| LOG-006 | ログイン中ユーザー表示 | title/statusにoperator_id/role表示 | OK | `ログイン中: editor / 権限: editor` 等を確認 |
| LOG-007 | Windows認証login | OSユーザーでpasswordなしログイン | OK | `windows:KUWR-MAIN\nkaji / viewer` 表示を確認 |
| LOG-008 | Windows認証初期role | 初期値viewer | OK | 初回Windows認証ユーザーはviewer扱い |
| LOG-009 | アカウント切替 | 再ログイン可能 | 一部OK | 変な残存ウィンドウは改善したが終了性に課題あり |
| LOG-010 | 切替時白ウィンドウ | 表示されない | 一部改善 | 白い画面は一旦改善。ただし全ウィンドウ終了/プロセス残存あり |
| LOG-011 | GUI終了後プロセス終了 | PowerShellへ戻る | NG/要修正 | ウィンドウを閉じてもプロセスが終わらない報告あり |

---

## 8. user management結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| USR-001 | tab表示 | ユーザー管理tab表示 | OK | adminで表示、viewer/editorは制限表示 |
| USR-002 | viewer作成 | viewer user一覧表示 | OK | ローカル/Windows認証ユーザーのviewer確認あり |
| USR-003 | editor作成 | editor user一覧表示 | OK | editorログイン/権限表示確認あり |
| USR-004 | operator_id重複 | 重複エラー | OK | `operator_id already exists` 確認済み |
| USR-005 | role変更 | role更新 | 未実施 | `AUDIT-002` / `ADMIN-001` |
| USR-006 | user無効化 | disabled扱い | 未実施 | `AUTH-002` / `AUDIT-002` |
| USR-007 | user有効化 | active扱い | 未実施 | `AUDIT-002` |
| USR-008 | 最後のadmin降格防止 | 拒否 | 未実施 | `ADMIN-001` |
| USR-009 | 最後のadmin無効化防止 | 拒否 | 未実施 | `ADMIN-001` |
| USR-010 | ユーザー管理ガイド | サブタブ表示 | OK | ガイド/ユーザー作成/ユーザー一覧/選択ユーザー操作 |
| USR-011 | viewer/editorでユーザー管理 | 操作不可 | OK | 警告表示、作成/操作系不可 |

---

## 9. role別操作結果

| ID | role | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| RBAC-001 | viewer | 参照系tab表示 | 参照可能 | OK | 検索/監査ログ/ヘルプ/設定など参照可能 |
| RBAC-002 | viewer | 名前登録/更新/削除 | 不可 | OK | 更新系buttonは不可/非表示方向へ整理 |
| RBAC-003 | viewer | タイトル/サブタイトル登録/更新/削除 | 不可 | OK | 参照専用・警告表示を確認 |
| RBAC-004 | viewer | 関連付け登録/解除 | 不可 | OK | viewerは参照専用表示へ整理 |
| RBAC-005 | viewer | export/backup/import/restore/log export | 不可 | OK | Operations Log参照のみ表示 |
| RBAC-006 | viewer | user management tab | 操作不可 | OK | 警告表示、操作不可 |
| RBAC-007 | viewer | user audit log tab | 操作不可/内容非表示 | OK | admin以外は制限 |
| RBAC-008 | editor | 名前登録/更新 | 可能 | UI OK / 実行一部OK | test user作成・更新画面確認あり |
| RBAC-009 | editor | タイトル/サブタイトル登録/更新 | 可能 | UI OK / 実行一部OK | 作成/更新系が有効、削除系不可 |
| RBAC-010 | editor | 関連付け登録 | 可能 | UI OK / 要追加実行 | 登録画面表示はOK。実ファイル/ログ含む確認は残る |
| RBAC-011 | editor | export/backup | 可能 | UI OK / 実行未完 | Export/Backupサブタブ表示OK。実出力は `DATAIO-002` |
| RBAC-012 | editor | restore/import/destructive | 不可 | OK | Restore/Importは非表示または禁止 |
| RBAC-013 | editor | user management / user audit log | 不可 | OK | 警告表示、操作不可 |
| RBAC-014 | admin | destructive操作 | 可能 | 一部OK | 表示OK。実行UATは `RESTORE-001` |

---

## 10. audit log結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| AUD-001 | データ変更ログ | 監査ログ > データ変更ログで確認可能 | OK | create/link等の表示を確認 |
| AUD-002 | user/auth log | 監査ログ > ユーザー/認証ログで確認可能 | OK | login_success / user_create 表示を確認 |
| AUD-003 | 監査ログガイド | ガイドでログ差分を説明 | OK | 統合ログの説明表示を確認 |
| AUD-004 | login_failure記録 | user_audit_logsに記録 | 未実施 | `AUDIT-002` 残件 |
| AUD-005 | user_role_change記録 | user_audit_logsに記録 | 未実施 | `AUDIT-002` 残件 |
| AUD-006 | user_disable / enable記録 | user_audit_logsに記録 | 未実施 | `AUDIT-002` 残件 |
| AUD-007 | password非記録 | password材料が出ない | OK | 自動テスト追加済み。運用目視は残す |
| AUD-008 | viewer/editorでユーザー監査ログ | 操作不可/内容非表示 | OK | viewer/editorでは制限表示 |

---

## 11. migration / 既存DB互換結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| MIG-001 | 既存v0.1.0系DB open | migration成功 | OK | `tests/test_db_initialization.py` で補強 |
| MIG-002 | schema_migrations記録 | migration version記録 | OK | 自動テスト/起動確認あり |
| MIG-003 | 既存データ維持 | 既存データが残る | OK | 自動テストで確認 |
| MIG-004 | users 0件時setup | 初回admin setup表示 | OK | screenshot確認 |
| MIG-005 | public_id列欠損DB | 起動時補完 | OK | `no such column: public_id` 再発対策済み |

---

## 12. EXE / portable結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| EXE-001 | build | EXE作成 | 過去OK | 直近は未実行 |
| EXE-002 | smoke | auth tables check pass | 過去OK | 直近は未実行 |
| EXE-003 | portable smoke script | ps1存在 | OK | `scripts/smoke_test_portable_windows.ps1` 追加済み |
| EXE-004 | package | release folder作成 | 未実施 | `PORTABLE-001` |
| EXE-005 | portable smoke | pass | 未実施 | `PORTABLE-001` |

---

## 13. 不具合・課題一覧

| ID | 区分 | 重大度 | 内容 | 再現手順 | 対応方針 | 状態 |
|---|---|---|---|---|---|---|
| BUG-001 | UI | 高 | ユーザー作成用operator入力欄が非表示になる | ユーザー管理 > ユーザー作成 | `operator_input` を `create_operator_input` へ改名 | closed |
| BUG-002 | UI/RBAC | 高 | viewerで一部更新系入力欄・参照・履歴削除が操作可能に見える | viewer login後、名前/タイトル/サブタイトル/関連付け/データ入出力を確認 | UI-level RBAC hardeningを実施 | closed |
| BUG-003 | UI | 中 | ログイン中ユーザー/権限が分かりにくい | editor/viewer/adminで複数タブを確認 | title bar/status barにoperator_id/roleを常時表示 | closed |
| BUG-004 | UI | 中 | 監査ログとユーザー監査ログの違いが分かりにくい | ログ系タブ確認 | 監査ログタブへ統合 | closed |
| BUG-005 | UI | 中 | タイトル/サブタイトル画面がごちゃつく | タイトル/サブタイトル操作 | 統合タブ＋サブタブ化 | closed |
| BUG-006 | UI | 中 | 権限なしbuttonが押せそうに見える | viewer/editorで確認 | 権限外サブタブ/操作を非表示化 | closed |
| BUG-007 | UI | 中 | 関連付け・公開ID表記が見づらい | 関連付け/検索/名前管理 | 表示文言・ID列を改善、自動UAT追加 | closed |
| BUG-008 | Account switch | 中 | 切替時に変なウィンドウ/白い画面が出る | アカウント切替 | 複数回対策。白画面は改善傾向 | partially_closed |
| ACC-WHITE-001 | Account switch | 高 | アカウント切替後に全ウィンドウが閉じる、または閉じてもプロセスが終わらない | アカウント切替後、ウィンドウ終了 | Qt event loop設計の再検討。後回し管理 | open |
| UAT-REMAIN-001 | UAT残 | 中 | login異常系、最後のadmin保護、data I/O実行、portable smokeが未完 | docs/71に従う | 次工程で実施 | open |
| RELEASE-REMAIN-001 | release残 | 中 | v0.2.0-rc1 evidence未作成 | UAT後 | release evidence作成 | open |

---

## 14. Go / No-Go判定

| 判定項目 | 判定 | コメント |
|---|---|---|
| 品質ゲート | 条件付きOK | 直近ユーザー実行ではOK。`02f65c4` / docs更新後に再実行が必要 |
| GUI起動 | 条件付きOK | 起動はOK。通常終了とアカウント切替終了性は残件 |
| 初回admin setup | 一部OK | 初回表示、admin作成、login遷移OK。validation系は未完 |
| login | 一部OK | 正常login、Windows認証、RoleContext反映、ログイン状態表示OK。異常系は未完 |
| account switch | No-Go寄り残件 | 白画面は改善傾向だが全ウィンドウ終了/プロセス残存が残る |
| user management | 一部OK | admin/viewer/editor作成、重複エラー、viewer/editor操作不可はOK。role変更/無効化/有効化/最後のadmin保護は未完 |
| role別操作 | 条件付きOK | viewer/editor/adminの主要UI差分はOK。破壊操作/実出力系は未完 |
| audit log | 一部OK | 統合タブ表示、login_success/user_create、password非記録テストはOK。異常系・role変更等は未完 |
| migration | OK | 自動テストで補強済み |
| EXE / portable | 未完 | portable script追加済み。release package smoke未実施 |
| 総合判定 | UAT継続 | release前には `ACC-WHITE-001`、portable smoke、admin保護、login異常系を完了させる |

判定基準:

| 判定 | 条件 |
|---|---|
| Go | QG / GUI終了性 / admin setup / login異常系 / user management / audit / migration / portable smoke がすべてOK |
| Conditional Go | 軽微なdocs/UI文言のみ未修正で、データ破壊・認証・role・migration・プロセス終了性に問題なし |
| No-Go | login不能、migration失敗、最後のadmin保護失敗、password平文露出、role制御崩れ、GUI終了不可、EXE/portable smoke失敗 |

---

## 15. 次工程

1. `git pull origin main` で `02f65c4` / docs更新を取得する。
2. `black --check .` / `ruff check .` / `mypy app` / `pytest -q` を再実行する。
3. `python -m app.pyside6_main` で通常起動・通常終了を確認する。
4. `ACC-WHITE-001` は一旦後回し管理のまま、次のrelease blockerとして残す。
5. login異常系UATを実施する。
6. 最後の有効admin保護UATを実施する。
7. editor/adminのExport/Backup/Restore/Import実行UATを実施する。
8. v0.2.0-rc1 package生成と `scripts/smoke_test_portable_windows.ps1` を実行する。
9. release evidence文書を作成する。
