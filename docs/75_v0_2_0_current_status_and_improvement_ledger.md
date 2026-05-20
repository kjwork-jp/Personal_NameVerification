# 75_v0_2_0_current_status_and_improvement_ledger.md

## 1. 目的

v0.2.0 認証・ユーザー管理・RBAC・UIナビゲーション改善の現況を一元管理する。

`docs/72` はUAT実行記録、`docs/73` はUI再設計計画、`docs/74` はRBAC定義、`docs/78` はrelease evidence、`docs/97` は未解決課題を扱う。本文書はそれらを横断し、ここまでの流れ、決定事項、実装済み事項、残件を整理する現況台帳である。

---

## 2. 現在の結論

| 項目 | 現況 |
|---|---|
| 認証 | 初回admin setup / local password login / Windows認証ログインを実装済み |
| Windows認証 | OSユーザーは初回ログイン時に `viewer` で自動登録される方針で実装済み。portable GUIでviewer表示を確認済み |
| role取得 | 利用者がroleを自由選択しない。DBの `users.role` から `viewer` / `editor` / `admin` を取得 |
| ログイン状態表示 | ウィンドウタイトルと下部ステータスバーに `ログイン中: <operator_id> / 権限: <role>` を常時表示済み |
| アカウント切替 | portable GUI再確認で白画面・小窓・プロセス残留なしを確認済み |
| viewer | 完全参照専用へ寄せた。主要更新系UIは非表示または操作不可へ整理済み |
| editor | 通常登録/更新、関連付け登録、export/backupを許可。destructive/import/restore/user管理/user audit log操作は禁止 |
| admin | destructive/import/restore/user管理/user audit logを含めた管理者権限。ただし最後の有効admin保護は維持 |
| UI構造 | 監査ログ統合、タイトル/サブタイトル統合、データ入出力権限別表示、関連付け表示改善を反映済み |
| データ入出力初期値 | portableでは `30_prod_db` / `40_logs` / `50_backups` / `60_exports` 配下に寄ることを確認済み |
| release package | `NameVerification-v0.2.0-rc1-portable.zip` 作成済み。stale EXEチェック込みの再build/package/smokeもPASS |
| portable GUI UAT | MainWindowのみ表示、NameVerification小窓なし、アカウント切替正常、portable配下パス表示を確認済み |
| 品質ゲート | 2026-05-20時点で `black --check .` / `ruff check .` / `mypy app` / `pytest -q` 全PASS確認済み |

---

## 3. ここまでの主な流れ

| 順序 | 内容 | 状態 |
|---:|---|---|
| 1 | v0.2.0認証・ユーザー管理UATチェックリストと実行記録を追加 | 完了 |
| 2 | 初回admin setup / login / user management / user audit log をGUI確認 | 一部完了 |
| 3 | ユーザー管理UIのサブタブ化 | 完了 |
| 4 | viewer向けRBAC UI hardening | 完了 |
| 5 | 操作履歴とユーザー監査ログを監査ログタブへ統合 | 完了 |
| 6 | タイトル/サブタイトル管理を統合タブ化 | 完了 |
| 7 | Windows認証ログインと初期viewerマッピングを実装 | 完了 |
| 8 | データ入出力タブをロール別に表示/非表示制御 | 完了 |
| 9 | 関連付け・公開ID表記・検索/一覧ID表示のUAT自動化を追加 | 完了 |
| 10 | 既存DB初期化・schema migration・password非記録の自動テストを追加 | 完了 |
| 11 | portable Windows smoke scriptを追加 | 完了 |
| 12 | アカウント切替時の残存ポップアップ/白画面/終了性を修正 | 完了 |
| 13 | データ入出力の小窓化と初期値パスを修正 | 完了 |
| 14 | stale EXE混入防止の鮮度チェックをpackage scriptへ追加 | 完了 |
| 15 | `v0.2.0-rc1` を最新EXEで再build/package/smokeし、portable GUI UATを再確認 | 完了 |

---

## 4. 実装済み改善事項

| 区分 | 改善事項 | 状態 | 補足 |
|---|---|---|---|
| 認証 | 初回admin setup | 完了 | active user 0件時に作成dialogを表示 |
| 認証 | local password login | 完了 | `operator_id` + password。role自由選択なし |
| 認証 | Windows認証ログイン | 完了 | OSユーザーを `windows:<domain>\\<user>` として扱う |
| 認証 | Windows認証初期role | 完了 | 初回自動登録時は `viewer` |
| 認証 | password hash保存 | 完了 | PBKDF2-SHA256 |
| 監査 | login/user管理audit | 一部完了 | password材料非記録テストあり。異常系UATの一部は残る |
| UI | ユーザー管理サブタブ化 | 完了 | ガイド/ユーザー作成/ユーザー一覧/選択ユーザー操作 |
| UI | 監査ログ統合タブ | 完了 | データ変更ログ/ユーザー認証ログ/ガイド |
| UI | タイトル/サブタイトル統合 | 完了 | タイトル/サブタイトル/ガイドのサブタブ構成 |
| UI | ログイン中ユーザー表示 | 完了 | title bar + status bar |
| UI | 権限なし操作の非表示化 | 完了 | viewer/editor/adminで不要サブタブを非表示化 |
| UI | 関連付け表示改善 | 完了 | 名前/タイトル/サブタイトル/公開ID表記を読みやすく修正 |
| UI | データ入出力サブタブ小窓化防止 | 完了 | MainWindow内サブタブ表示のみへ整理 |
| UI | portable初期値パス整理 | 完了 | package root配下の `30_prod_db` / `40_logs` / `50_backups` / `60_exports` に集約 |
| RBAC | viewerの名前管理入力無効化/非表示 | 完了 | 更新系は参照専用表示へ寄せた |
| RBAC | viewerのタイトル/サブタイトル入力無効化/非表示 | 完了 | 更新系は参照専用表示へ寄せた |
| RBAC | viewerの関連付け登録/解除非表示 | 完了 | viewerは参照専用ガイド表示 |
| RBAC | editorの関連解除禁止 | 完了 | editorは登録可、解除不可 |
| RBAC | viewer/editorのユーザー監査ログ制御 | 完了 | admin以外は操作不可/内容非表示 |
| RBAC | データ入出力制御 | 完了 | viewerはOperations Log参照、editorはExport/Backup/Operations Log、adminは全操作 |
| QA | release remaining UAT自動テスト | 完了 | ID表示、RBAC表示、統合タブ確認を自動化 |
| QA | DB/migration自動テスト | 完了 | schema初期化・既存DB互換・password非記録を補強 |
| QA | portable smoke script | 完了 | Windows portable package検証用ps1を追加 |
| Release | stale EXE package防止 | 完了 | package時にEXEがsourceより古い場合は失敗 |

---

## 5. 残件バックログ

| 優先 | ID | 内容 | 状態 | 次アクション |
|---:|---|---|---|---|
| P0 | GATE-001 | 最新main品質ゲート再確認 | 完了 | build script内および手動確認で全PASS |
| P0 | GUI-001 | 最新main GUI起動確認 | 完了 | 通常起動・通常終了でPowerShell復帰確認済み |
| P0 | ACC-WHITE-001 | アカウント切替時の白画面/小窓/プロセス残存 | 完了 | portable GUIで白画面・小窓・プロセス残留なしを確認済み |
| P0 | PORTABLE-001 | v0.2.0-rc1 portable package smoke | 完了 | package生成、manifest/checksum、portable smoke PASS |
| P0 | PORTABLE-GUI-001 | portable版GUI手動UAT | 完了 | MainWindowのみ、package root/DB/log/初期値/切替正常を確認済み |
| P1 | RELEASE-STALENESS-001 | stale EXEチェック込みで再build/package/smoke確認 | 完了 | 再build、package、portable smoke再実行済み。初回はexit code 0で一時失敗、再実行でPASS |
| P1 | AUTH-002 | login異常系UAT | 未完 | 誤password、未登録operator_id、disabled user、空operator_idを確認 |
| P1 | ADMIN-001 | 最後の有効admin保護UAT | 未完 | 降格/無効化/削除が拒否されることを確認 |
| P1 | DATAIO-002 | Export/Backup/Operations Log実行UAT | 画面OK・実出力未完 | editor/adminで実出力・バックアップ・ログ確認 |
| P1 | RESTORE-001 | Restore/Import破壊操作UAT | 未完 | adminのみ表示/実行、事前backup、invalid input時の退避DB未作成を確認 |
| P1 | AUDIT-002 | login_failure / role_change / disable / enable の監査ログUAT | 未完 | user_audit_logs画面とDB記録を確認 |
| P2 | HELP-001 | ヘルプ/設定の診断画面化 | 部分完了 | 保護警告/パス診断/基本情報/操作メモの分割は実装済み、追加整理は任意 |
| P2 | STYLE-001 | ロール別視覚差分強化 | 未完 | title/status以外の識別性改善 |

---

## 6. 最新RBAC定義

| role | 参照 | 通常登録/更新 | 関連付け登録 | 関連解除 | 削除/復元/完全削除 | export | backup | import/restore | user管理 | user audit log |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| viewer | 可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可/内容非表示 |
| editor | 可 | 可 | 可 | 不可 | 不可 | 可 | 可 | 不可 | 不可 | 不可/内容非表示 |
| admin | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 |

---

## 7. UAT状況

| 区分 | 状態 | メモ |
|---|---|---|
| 品質ゲート | OK | `black` / `ruff` / `mypy` / `pytest` 全PASS |
| GUI起動 | OK | 通常起動・通常終了でPowerShell復帰確認済み |
| アカウント切替 | OK | 白画面・小窓・プロセス残留なし |
| 初回admin setup | 一部OK | 作成/遷移OK。validation系は一部未実施 |
| local login | 一部OK | 正常login/role取得/ログイン状態表示OK。異常系は残る |
| Windows login | OK | 初回viewer自動登録とviewer表示をGUIで確認済み |
| viewer | 主要UI OK | 更新系非表示/参照専用化を確認済み |
| editor | 主要UI OK | 通常更新・関連付け登録・Export/Backupの表示OK。実行UATは残る |
| admin | 一部OK | user管理/restore/import表示OK。破壊操作の実行UATは残る |
| migration | OK | DB初期化/既存DB互換の自動テストを追加済み |
| portable | OK | package作成、portable smoke、portable GUI UAT完了 |

---

## 8. 次工程

| 順序 | 作業 | 完了条件 |
|---:|---|---|
| 1 | login異常系UAT | 誤password、未登録、disabled、空欄系が期待通り拒否 |
| 2 | 最後の有効admin保護UAT | 最後の有効admin降格/無効化/削除が拒否 |
| 3 | editor/adminのデータ入出力実行UAT | Export/Backup/Operations Logの実ファイル・ログ確認 |
| 4 | Restore/Import destructive UAT | admin限定、事前backup、invalid input時の安全性確認 |
| 5 | release evidence更新 | 最新のstale EXE再build/package/smoke結果を `docs/78` に追記 |
| 6 | 最終Go/No-Go判定 | release blockerなしを確認 |

---

## 9. 参照資料

| 資料 | 用途 |
|---|---|
| `docs/71_v0_2_0_auth_integrated_uat_checklist.md` | v0.2.0 UATチェックリスト |
| `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | UAT実行記録 |
| `docs/73_ui_navigation_redesign_plan.md` | UIナビゲーション再設計計画 |
| `docs/74_rbac_hardening_plan.md` | RBAC強化計画/台帳 |
| `docs/77_v0_2_0_wbs_design_management_artifact_manifest_20260518.md` | WBS/設計書/管理台帳構成 |
| `docs/78_release_evidence_v0_2_0_rc1.md` | v0.2.0-rc1 release evidence |
| `docs/97_open_issues_and_constraints.md` | 未解決課題/制約 |
