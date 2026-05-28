# 72_v0_2_0_auth_integrated_uat_execution_record.md

## 1. 目的

`docs/71_v0_2_0_auth_integrated_uat_checklist.md` に基づき、NameVerification v3 `v0.2.0` 認証・ユーザー管理・RBAC・UIナビゲーション統合UATの実行結果を記録する。

この文書は、UAT実施時に結果・証跡・不具合・Go/No-Go判定を残すための記録表である。最新の横断状況は以下も参照する。

- `docs/75_v0_2_0_current_status_and_improvement_ledger.md`
- `docs/88_v040_uat_evidence_20260527.md`
- `docs/89_account_switch_viewer_uat_20260527.md`
- `docs/90_editor_uat_followup_20260527.md`
- `docs/97_open_issues_and_constraints.md`

---

## 2. 実行サマリ

| 項目 | 記録 |
|---|---|
| 実行日 | 2026-05-18〜2026-05-28 |
| 実行者 | NAOKI KAJIWARA |
| 対象branch | `main` |
| 最新品質ゲート対象commit | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` |
| 最新品質ゲートrun | `26549117150` |
| Python | 3.13系 |
| OS | Windows 11 |
| DB path | `C:\Users\nkaji\Documents\GitHub\Personal_NameVerification\nameverification.db` ほかUAT用DB |
| change log JSONL path | `logs\change_logs.jsonl` ほかUAT用JSONL |
| release candidate | v0.2.0 UAT candidate |
| 総合判定 | コード品質ゲートはPASS。viewer/account-switch/admin主要UATはPASS。editor follow-up修正は実装済みだが、editor再UAT未完のためrelease readinessはBLOCKED |

---

## 3. 品質ゲート結果

| ID | 確認項目 | コマンド / 証跡 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| QG-001 | pytest | Quality Gates run `26549117150` | pass | PASS | `pytest` step success |
| QG-002 | ruff | Quality Gates run `26549117150` | pass | PASS | `ruff check .` step success |
| QG-003 | black | Quality Gates run `26549117150` | pass | PASS | `black --check .` step success |
| QG-004 | mypy | Quality Gates run `26549117150` | pass | PASS | `mypy app` step success |
| QG-005 | Commit Status | `chatgpt/quality-gates` | success | PASS | commit `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` |
| QG-006 | Actions結果取得性 | GitHub Commit Status API | 状態取得可能 | PASS | assistant側で `success` を取得可能化済み |

---

## 4. 初回admin setup結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| ADM-001 | users 0件時の初回setup表示 | InitialAdminSetupDialog 表示 | PASS | 初回管理者作成dialog表示を確認済み |
| ADM-002 | admin作成 | admin user 作成 | PASS | admin作成・遷移OK |
| ADM-003 | password confirmation不一致 | 作成不可 | PASS | 認証異常系UATで確認済み扱い |
| ADM-004 | 空operator_id | 作成不可 | PASS | 認証異常系UATで確認済み扱い |
| ADM-005 | setup後のlogin遷移 | LoginDialog 表示 | PASS | login dialog表示を確認済み |

---

## 5. login / account switch結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| LOG-001 | local正常login | MainWindow表示 | PASS | admin/editor/viewerで確認 |
| LOG-002 | role combo廃止 | role選択UIなし | PASS | LoginDialogはlocal認証とWindows認証の選択式 |
| LOG-003 | 誤password | login拒否 | PASS | 認証異常系として確認済み扱い |
| LOG-004 | 未登録operator_id | login拒否 | PASS | 認証異常系として確認済み扱い |
| LOG-005 | RoleContext反映 | admin/viewer/editor別UI反映 | PASS | title/status/tab表示で確認 |
| LOG-006 | ログイン中ユーザー表示 | title/statusにoperator_id/role表示 | PASS | `ログイン中: <operator_id> / 権限: <role>` 表示 |
| LOG-007 | Windows認証login | OSユーザーでpasswordなしログイン | PASS | 初回Windows認証ユーザーはviewer扱い |
| LOG-008 | Windows認証初期role | 初期値viewer | PASS | viewer初期登録方針どおり |
| LOG-009 | アカウント切替 | 再ログイン可能 | PASS | DB close問題修正後、ユーザーがログイン問題解消を確認 |
| LOG-010 | 切替時白ウィンドウ | 表示されない | PASS | 既存portable GUI確認で白画面・小窓・プロセス残留なし |
| LOG-011 | GUI終了後プロセス終了 | PowerShellへ戻る | PASS | 過去課題は解消済み扱い。現時点のrelease blockerではない |

---

## 6. user management結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| USR-001 | tab表示 | ユーザー管理tab表示 | PASS | adminで表示、viewer/editorは非表示または制限 |
| USR-002 | viewer作成 | viewer user一覧表示 | PASS | ローカル/Windows認証ユーザーのviewer確認あり |
| USR-003 | editor作成 | editor user一覧表示 | PASS | editorログイン/権限表示確認あり |
| USR-004 | operator_id重複 | 重複エラー | PASS | `operator_id already exists` 確認済み |
| USR-005 | role変更 | role更新 | PASS | ユーザー監査ログ系UATで確認済み扱い |
| USR-006 | user無効化 | disabled扱い | PASS | 認証/監査ログ系UATで確認済み扱い |
| USR-007 | user有効化 | active扱い | PASS | 監査ログ系UATで確認済み扱い |
| USR-008 | 最後のadmin降格防止 | 拒否 | PASS | 最後の有効admin保護UAT PASS |
| USR-009 | 最後のadmin無効化防止 | 拒否 | PASS | 最後の有効admin保護UAT PASS |
| USR-010 | ユーザー管理ガイド | サブタブ表示 | PASS | ガイド/ユーザー作成/ユーザー一覧/選択ユーザー操作 |
| USR-011 | viewer/editorでユーザー管理 | 操作不可 | PASS | 警告表示またはtab非表示、作成/操作不可 |

---

## 7. role別操作結果

| ID | role | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|---|
| RBAC-001 | viewer | 参照系tab表示 | 参照可能 | PASS | 検索/Operations Log等の参照可能範囲を確認 |
| RBAC-002 | viewer | 名前登録/更新/削除 | 不可 | PASS | 更新系buttonは非表示/操作不可 |
| RBAC-003 | viewer | タイトル/サブタイトル登録/更新/削除 | 不可 | PASS | 参照専用。実行ボタン非表示として `docs/89` に証跡化 |
| RBAC-004 | viewer | 関連付け登録/解除 | 不可 | PASS | viewerは参照専用表示へ整理 |
| RBAC-005 | viewer | export/backup/import/restore/log export | 不可 | PASS | Restore/Import等は非表示。Operations Log参照のみ表示 |
| RBAC-006 | viewer | user management tab | 操作不可 | PASS | admin以外は非表示または制限 |
| RBAC-007 | viewer | user audit log tab | 操作不可/内容非表示 | PASS | admin以外は制限 |
| RBAC-008 | editor | 名前登録/更新 | 可能 | PASS | editor UATで実行可能確認済み |
| RBAC-009 | editor | タイトル登録/更新 | 可能 | PASS | editor UATで実行可能確認済み。ただしUI follow-upあり |
| RBAC-010 | editor | サブタイトル登録/更新 | 可能 | FIX APPLIED / RE-UAT REQUIRED | 修正・自動テスト・Quality Gates PASS済み。GUI再UAT待ち |
| RBAC-011 | editor | 関連付け登録 | 可能 | PASS | editor UATで登録可能確認済み |
| RBAC-012 | editor | 関連付け解除 | 可能 | FIX APPLIED / RE-UAT REQUIRED | 修正・自動テスト・Quality Gates PASS済み。GUI再UAT待ち |
| RBAC-013 | editor | export/backup | 可能 | PASS | Export/Backupサブタブ表示・実行OK |
| RBAC-014 | editor | restore/import/destructive | 不可 | PASS | Restore/Import/復元/完全削除は非表示または禁止 |
| RBAC-015 | editor | user management / user audit log | 不可 | PASS | 警告表示、操作不可、または非表示 |
| RBAC-016 | admin | destructive操作 | 可能 | PASS | user管理/restore/import/削除データ系表示OK。現在DB restoreは事前ブロック |

---

## 8. audit log結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| AUD-001 | データ変更ログ | 監査ログ > データ変更ログで確認可能 | PASS | create/link等の表示を確認 |
| AUD-002 | user/auth log | 監査ログ > ユーザー/認証ログで確認可能 | PASS | login_success / user_create 表示を確認 |
| AUD-003 | 監査ログガイド | ガイドでログ差分を説明 | PASS | 統合ログの説明表示を確認 |
| AUD-004 | login_failure記録 | user_audit_logsに記録 | PASS | 監査ログ異常系として確認済み扱い |
| AUD-005 | user_role_change記録 | user_audit_logsに記録 | PASS | 監査ログ異常系として確認済み扱い |
| AUD-006 | user_disable / enable記録 | user_audit_logsに記録 | PASS | 監査ログ異常系として確認済み扱い |
| AUD-007 | password非記録 | password材料が出ない | PASS | 自動テスト追加済み。運用目視は任意残件 |
| AUD-008 | viewer/editorでユーザー監査ログ | 操作不可/内容非表示 | PASS | viewer/editorでは制限表示 |

---

## 9. migration / 既存DB互換結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| MIG-001 | 既存v0.1.0系DB open | migration成功 | PASS | `tests/test_db_initialization.py` で補強 |
| MIG-002 | schema_migrations記録 | migration version記録 | PASS | 自動テスト/起動確認あり |
| MIG-003 | 既存データ維持 | 既存データが残る | PASS | 自動テストで確認 |
| MIG-004 | users 0件時setup | 初回admin setup表示 | PASS | screenshot確認 |
| MIG-005 | public_id列欠損DB | 起動時補完 | PASS | `no such column: public_id` 再発対策済み |

---

## 10. EXE / portable結果

| ID | 確認項目 | 期待結果 | 結果 | 証跡/メモ |
|---|---|---|---|---|
| EXE-001 | build | EXE作成 | PASS | v0.2.0-rc1で作成済み |
| EXE-002 | smoke | auth tables check pass | PASS | portable smoke確認済み |
| EXE-003 | portable smoke script | ps1存在 | PASS | `scripts/smoke_test_portable_windows.ps1` 追加済み |
| EXE-004 | package | release folder作成 | PASS | `NameVerification-v0.2.0-rc1-portable.zip` 作成済み |
| EXE-005 | portable smoke | pass | PASS | portable GUI UAT完了 |

---

## 11. 不具合・課題一覧

| ID | 区分 | 重大度 | 内容 | 対応方針 | 状態 |
|---|---|---|---|---|---|
| BUG-001 | UI | 高 | ユーザー作成用operator入力欄が非表示になる | `operator_input` を `create_operator_input` へ改名 | closed |
| BUG-002 | UI/RBAC | 高 | viewerで一部更新系入力欄・参照・履歴削除が操作可能に見える | UI-level RBAC hardeningを実施 | closed |
| BUG-003 | UI | 中 | ログイン中ユーザー/権限が分かりにくい | title bar/status barにoperator_id/roleを常時表示 | closed |
| BUG-004 | UI | 中 | 監査ログとユーザー監査ログの違いが分かりにくい | 監査ログタブへ統合 | closed |
| BUG-005 | UI | 中 | タイトル/サブタイトル画面がごちゃつく | focused title/subtitle wrapperで改善 | closed |
| BUG-006 | UI | 中 | 権限なしbuttonが押せそうに見える | 権限外サブタブ/操作を非表示化 | closed |
| BUG-007 | UI | 中 | 関連付け・公開ID表記が見づらい | 表示文言・ID列を改善、自動UAT追加 | closed |
| BUG-008 | Account switch | 高 | アカウント切替でDB close errorが起きる | shared connectionの所有権をMainWindowから外す | closed |
| BUG-009 | Viewer UAT | 中 | viewer操作制限証跡を「ボタンあり」と誤読 | `docs/89`でボタン非表示によるPASSへ修正 | closed |
| BUG-010 | Editor UI | 高 | サブタイトル追加/編集不可 | title selector状態更新・権限制御・テスト補強 | fix_applied_reuat_required |
| BUG-011 | Editor UX | 中 | サブタイトル追加/編集画面で親タイトル検索不可 | editable combo + completerで検索可能化 | fix_applied_reuat_required |
| BUG-012 | Editor UI | 高 | 関連付け解除不可 | editor/adminで通常unlinkを許可 | fix_applied_reuat_required |
| BUG-013 | Editor UI | 中 | タイトル編集/説明コメント周辺のUI崩れ | guidance label折返し・短縮 | fix_applied_reuat_required |
| GATE-EDITOR-FOLLOWUP | QA | 高 | editor follow-up後の品質ゲート | pytest/ruff/black/mypy全PASS | closed |

---

## 12. Go / No-Go判定

| 判定項目 | 判定 | コメント |
|---|---|---|
| 品質ゲート | GO | `6d9550f75dd1ecec32f9b7d9a2a084d8e76f6e48` / run `26549117150` でPASS |
| GUI起動 | GO | 起動・通常終了・アカウント切替の主要課題は解消済み |
| 初回admin setup | GO | 初回表示、admin作成、login遷移OK |
| login | GO | 正常login、Windows認証、RoleContext反映、ログイン状態表示OK |
| account switch | GO | DB close問題解消済み。viewer切替後ログイン問題も解消済み |
| user management | GO | 主要UAT PASS。最後のadmin保護もPASS |
| viewer role | GO | 実行ボタン非表示による制御を証跡化済み |
| editor role | CONDITIONAL GO / RE-UAT REQUIRED | 修正は反映済みだが、サブタイトル/検索/関連解除/UI崩れのGUI再UATが未完 |
| admin role | GO | 管理操作、Data I/O、監査、restore/import制御の主要確認OK |
| audit log | GO | 統合タブ表示、user/auth log、password非記録テストOK |
| migration | GO | 自動テストで補強済み |
| EXE / portable | GO | v0.2.0-rc1 package / smoke / GUI UAT済み |
| 総合判定 | BLOCKED | editor再UATと最終docs同期が完了するまでrelease final Go不可 |

判定基準:

| 判定 | 条件 |
|---|---|
| Go | QG / GUI終了性 / admin setup / login異常系 / user management / audit / migration / portable smoke / role UAT がすべてOK |
| Conditional Go | 軽微なdocs/UI文言のみ未修正で、データ破壊・認証・role・migration・プロセス終了性に問題なし |
| No-Go | login不能、migration失敗、最後のadmin保護失敗、password平文露出、role制御崩れ、GUI終了不可、EXE/portable smoke失敗 |

---

## 13. 次工程

1. editorでサブタイトル追加・編集を再UATする。
2. editorでサブタイトル追加/編集画面の親タイトル検索を再UATする。
3. editorで既存関連付け解除を再UATする。
4. editorでタイトル編集画面・説明コメント周辺のUI崩れ軽減を再UATする。
5. 再UAT結果を `docs/90` に反映する。
6. `docs/72` / `docs/75` / `docs/88` / `docs/89` / `docs/90` / `docs/97` の最終同期を確認する。
7. release evidence最終固定とGo/No-Go判定へ進む。
