# 72_v0_2_0_auth_integrated_uat_execution_record.md

## 1. 目的

`docs/71_v0_2_0_auth_integrated_uat_checklist.md` に基づき、NameVerification v3 `v0.2.0` 認証・ユーザー管理統合UATの実行結果を記録する。

この文書は、UAT実施時に結果・証跡・不具合・Go/No-Go判定を残すための記録表である。

---

## 2. 実行サマリ

| 項目 | 記録 |
|---|---|
| 実行日 | 未記入 |
| 実行者 | 未記入 |
| 対象branch | `main` |
| 対象commit | 未記入 |
| Python | 未記入 |
| OS | Windows |
| DB path | 未記入 |
| change log JSONL path | 未記入 |
| EXE path | 未記入 |
| release candidate | v0.2.0 UAT candidate |
| 総合判定 | 未判定 |

---

## 3. 事前確認ログ

```powershell
git checkout main
git pull origin main
git log --oneline -n 10
python --version
python -m pip --version
```

実行結果:

```text
未記入
```

---

## 4. UAT用環境変数

```powershell
$env:NAMEVERIFICATION_DB_PATH = "$PWD\tmp\uat_v020\nameverification_uat.db"
$env:NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH = "$PWD\tmp\uat_v020\change_logs.jsonl"
```

実行結果:

```text
未記入
```

---

## 5. 品質ゲート結果

| ID | 確認項目 | コマンド | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| QG-001 | pytest | `pytest -q` | pass | 未実施 |  |
| QG-002 | ruff | `ruff check .` | pass | 未実施 |  |
| QG-003 | black | `black --check .` | pass | 未実施 |  |
| QG-004 | mypy | `mypy app` | pass | 未実施 |  |
| QG-005 | EXE build | `.\scripts\build_exe_windows.ps1` | EXE作成 | 未実施 |  |
| QG-006 | EXE smoke | `.\scripts\smoke_test_exe_windows.ps1` | auth tables check pass | 未実施 |  |

---

## 6. 初回admin setup結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| ADM-001 | users 0件時の初回setup表示 | InitialAdminSetupDialog 表示 | 未実施 |  |
| ADM-002 | admin作成 | admin user 作成 | 未実施 |  |
| ADM-003 | password confirmation不一致 | 作成不可 | 未実施 |  |
| ADM-004 | 空operator_id | 作成不可 | 未実施 |  |
| ADM-005 | setup後のlogin遷移 | LoginDialog 表示 | 未実施 |  |

---

## 7. login結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| LOG-001 | 正常login | MainWindow表示 | 未実施 |  |
| LOG-002 | role combo廃止 | role選択UIなし | 未実施 |  |
| LOG-003 | 誤password | login拒否 | 未実施 |  |
| LOG-004 | 未登録operator_id | login拒否 | 未実施 |  |
| LOG-005 | RoleContext反映 | admin操作可能 | 未実施 |  |

---

## 8. user management結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| USR-001 | tab表示 | ユーザー管理tab表示 | 未実施 |  |
| USR-002 | viewer作成 | viewer user一覧表示 | 未実施 |  |
| USR-003 | editor作成 | editor user一覧表示 | 未実施 |  |
| USR-004 | operator_id重複 | 重複エラー | 未実施 |  |
| USR-005 | role変更 | role更新 | 未実施 |  |
| USR-006 | user無効化 | disabled扱い | 未実施 |  |
| USR-007 | user有効化 | active扱い | 未実施 |  |
| USR-008 | 最後のadmin降格防止 | 拒否 | 未実施 |  |
| USR-009 | 最後のadmin無効化防止 | 拒否 | 未実施 |  |

---

## 9. role別操作結果

| ID | role | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| RBAC-001 | viewer | 参照系tab表示 | 参照可能 | 未実施 |  |
| RBAC-002 | viewer | 名前登録/更新 | 不可 | 未実施 |  |
| RBAC-003 | viewer | restore/import | 不可 | 未実施 |  |
| RBAC-004 | editor | 名前登録/更新 | 可能 | 未実施 |  |
| RBAC-005 | editor | restore/import | 不可 | 未実施 |  |
| RBAC-006 | admin | destructive操作 | 可能 | 未実施 |  |
| RBAC-007 | non-admin | user management tab | 操作不可または表示制限 | 未実施 |  |
| RBAC-008 | non-admin | user audit log tab | 操作不可または表示制限 | 未実施 |  |

---

## 10. user audit log結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| AUD-001 | login_success記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-002 | login_failure記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-003 | user_create記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-004 | user_role_change記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-005 | user_disable記録 | user_audit_logsに記録 | 未実施 |  |
| AUD-006 | password非記録 | password平文が出ない | 未実施 |  |

---

## 11. migration / 既存DB互換結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| MIG-001 | 既存v0.1.0 DB open | migration成功 | 未実施 |  |
| MIG-002 | schema_migrations記録 | migration version記録 | 未実施 |  |
| MIG-003 | 既存データ維持 | 既存データが残る | 未実施 |  |
| MIG-004 | users 0件時setup | 初回admin setup表示 | 未実施 |  |

SQLite確認結果:

```text
未記入
```

---

## 12. EXE / portable結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| EXE-001 | build | EXE作成 | 未実施 |  |
| EXE-002 | smoke | auth tables check pass | 未実施 |  |
| EXE-003 | package | release folder作成 | 未実施 |  |
| EXE-004 | portable smoke | pass | 未実施 |  |

---

## 13. 不具合・課題一覧

| ID | 区分 | 重大度 | 内容 | 再現手順 | 対応方針 | 状態 |
|---|---|---|---|---|---|---|
| BUG-001 | 未記入 | 未記入 | 未記入 | 未記入 | 未記入 | 未記入 |

---

## 14. Go / No-Go判定

| 判定項目 | 判定 | コメント |
|---|---|---|
| 品質ゲート | 未判定 |  |
| 初回admin setup | 未判定 |  |
| login | 未判定 |  |
| user management | 未判定 |  |
| role別操作 | 未判定 |  |
| user audit log | 未判定 |  |
| migration | 未判定 |  |
| EXE / portable | 未判定 |  |
| 総合判定 | 未判定 |  |

判定基準:

| 判定 | 条件 |
|---|---|
| Go | QG / admin setup / login / user management / audit / migration / EXE smoke がすべてOK |
| Conditional Go | 軽微なdocs/UI文言のみ未修正で、データ破壊・認証・role・migrationに問題なし |
| No-Go | login不能、migration失敗、最後のadmin保護失敗、password平文露出、role制御崩れ、EXE smoke失敗 |

---

## 15. 次工程

- Go / Conditional Go の場合
  - `v0.2.0-rc1` packaging
  - portable smoke
  - manifest/checksum生成
  - release evidence文書作成
- No-Go の場合
  - 不具合を1件1PRまたはmain直接patchで修正
  - 再UAT
