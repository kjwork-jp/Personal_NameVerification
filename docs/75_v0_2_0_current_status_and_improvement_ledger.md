# 75_v0_2_0_current_status_and_improvement_ledger.md

## 1. 目的

v0.2.0 認証・ユーザー管理・RBAC・UIナビゲーション改善の現況を一元管理する。

`docs/72` はUAT実行記録、`docs/73` はUI再設計計画、`docs/74` はRBAC定義、`docs/97` は未解決課題を扱う。本文書はそれらを横断し、ここまでの流れ、決定事項、実装済み事項、追加改善事項、次工程を整理する現況台帳である。

---

## 2. 現在の結論

| 項目 | 現況 |
|---|---|
| 認証 | 初回admin setup / local password login / Windows認証ログインを実装済み |
| Windows認証 | OSユーザーは初回ログイン時に `viewer` で自動登録される方針で実装済み |
| role取得 | 利用者がroleを自由選択しない。DBの `users.role` から `viewer` / `editor` / `admin` を取得 |
| ログイン状態表示 | ウィンドウタイトルと下部ステータスバーに `ログイン中: <operator_id> / 権限: <role>` を常時表示済み |
| アカウント切替 | MainWindowからLoginDialogへ戻す導線を実装済み。ただし一部環境で白い一瞬のログインウィンドウ/全ウィンドウ終了/プロセス残存が残るため後回し課題 |
| viewer | 完全参照専用へ寄せた。主要更新系UIは非表示または操作不可へ整理済み |
| editor | 通常登録/更新、関連付け登録、export/backupを許可。destructive/import/restore/user管理/user audit log操作は禁止 |
| admin | destructive/import/restore/user管理/user audit logを含めた管理者権限。ただし最後の有効admin保護は維持 |
| UI構造 | 監査ログ統合、タイトル/サブタイトル統合、データ入出力権限別表示、関連付け表示改善を反映済み |
| UAT | P0/P1の主要UATは自動テスト化・手動確認を進行。残件はアカウント切替白画面/終了挙動、portable package smoke、release evidence中心 |
| 品質ゲート | 2026-05-19時点の `black --check .` / `ruff check .` / `mypy app` / `pytest -q` はローカルで全OK。ただし直後の整形コミット `02f65c4` の再確認が必要 |

---

## 3. ここまでの主な流れ

| 順序 | 内容 | 代表commit / 資料 | 状態 |
|---:|---|---|---|
| 1 | v0.2.0認証・ユーザー管理UATチェックリストを追加 | `docs/71` | 完了 |
| 2 | UAT実行記録テンプレートを追加 | `docs/72` | 完了 |
| 3 | 初回admin setup / login / user management / user audit log をGUI確認 | `docs/72` | 一部完了 |
| 4 | ユーザー管理UIの詰め込み問題を確認し、サブタブ化 | `docs/73` | 完了 |
| 5 | viewerで更新系UIが見える問題を確認し、RBAC UI hardeningを実施 | `docs/74` | 完了 |
| 6 | 操作履歴とユーザー監査ログを監査ログタブへ統合 | `audit_logs_tab.py` | 完了 |
| 7 | タイトル/サブタイトル管理を統合タブ化 | `title_subtitle_unified_tab.py` | 完了 |
| 8 | Windows認証ログインと初期viewerマッピングを実装 | `windows_identity.py` / tests | 完了 |
| 9 | データ入出力タブをロール別に表示/非表示制御 | `rbac_ui_guards.py` | 完了 |
| 10 | 関連付け・公開ID表記・検索/一覧ID表示のUAT自動化を追加 | `test_release_remaining_uat.py` | 完了 |
| 11 | 既存DB初期化・schema migration・password非記録の自動テストを追加 | `test_db_initialization.py` / `test_user_audit_password_redaction.py` | 完了 |
| 12 | portable Windows smoke scriptを追加 | `scripts/smoke_test_portable_windows.ps1` | 完了 |
| 13 | アカウント切替時の残存ポップアップ/白画面対策を複数回実施 | `app/pyside6_main.py` | 一部未解決 |
| 14 | `black` 指摘を受けた `pyside6_main.py` の整形を反映 | `02f65c4` | 完了・要再確認 |

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
| RBAC | viewerの名前管理入力無効化/非表示 | 完了 | 更新系は参照専用表示へ寄せた |
| RBAC | viewerのタイトル/サブタイトル入力無効化/非表示 | 完了 | 更新系は参照専用表示へ寄せた |
| RBAC | viewerの関連付け登録/解除非表示 | 完了 | viewerは参照専用ガイド表示 |
| RBAC | editorの関連解除禁止 | 完了 | editorは登録可、解除不可 |
| RBAC | viewer/editorのユーザー監査ログ制御 | 完了 | admin以外は操作不可/内容非表示 |
| RBAC | データ入出力制御 | 完了 | viewerはOperations Log参照、editorはExport/Backup/Operations Log、adminは全操作 |
| QA | release remaining UAT自動テスト | 完了 | ID表示、RBAC表示、統合タブ確認を自動化 |
| QA | DB/migration自動テスト | 完了 | schema初期化・既存DB互換・password非記録を補強 |
| QA | portable smoke script | 完了 | Windows portable package検証用ps1を追加 |

---

## 5. 残件バックログ

| 優先 | ID | 内容 | 状態 | 次アクション |
|---:|---|---|---|---|
| P0 | GATE-001 | 最新main品質ゲート再確認 | 完了後に再発生 | `02f65c4` 反映後に `black` / `ruff` / `mypy` / `pytest` 再実行 |
| P0 | GUI-001 | 最新main GUI起動確認 | 完了後に再発生 | `python -m app.pyside6_main` 起動・終了確認 |
| P0 | ACC-WHITE-001 | アカウント切替時の白い一瞬のウィンドウ/全ウィンドウ終了/プロセス残存 | 未解決・後回し | 現象を再現分離し、LoginDialog再表示方式またはapp.exec単一化を再設計 |
| P0 | ACC-002 | アカウント切替後のプロセス終了性 | 未完 | GUI終了後にPowerShellへ制御が戻るか確認 |
| P0 | AUTH-002 | login異常系UAT | 未完 | 誤password、未登録operator_id、disabled user、空operator_idを確認 |
| P0 | ADMIN-001 | 最後の有効admin保護UAT | 未完 | 降格/無効化/削除が拒否されることを確認 |
| P0 | PORTABLE-001 | v0.2.0-rc1 portable package smoke | 未完 | package生成、manifest/checksum、portable起動、smoke script実行 |
| P1 | DATAIO-002 | Export/Backup/Operations Log実行UAT | 未完 | editor/adminで実出力・バックアップ・ログ確認 |
| P1 | RESTORE-001 | Restore/Import破壊操作UAT | 未完 | adminのみ表示/実行、事前backup、invalid input時の退避DB未作成を確認 |
| P1 | AUDIT-002 | login_failure / role_change / disable / enable の監査ログUAT | 未完 | user_audit_logs画面とDB記録を確認 |
| P1 | RELEASE-001 | release evidence更新 | 未完 | UAT完了後にrelease evidence文書を作成/更新 |
| P2 | HELP-001 | ヘルプ/設定の診断画面化 | 未完 | ヘルプ/設定/パス診断/保護警告の再分割 |
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
| 品質ゲート | OK→要再確認 | 2026-05-19ローカルではOK。`02f65c4` 後に再実行が必要 |
| GUI起動 | OK→要再確認 | 起動は確認済み。終了性はアカウント切替周辺に残課題 |
| 初回admin setup | 一部OK | 作成/遷移OK。validation系は一部未実施 |
| local login | 一部OK | 正常login/role取得/ログイン状態表示OK。異常系は残る |
| Windows login | 一部OK | 初回viewer自動登録方針を実装。総合UATは残る |
| viewer | 主要UI OK | 更新系非表示/参照専用化を確認済み |
| editor | 主要UI OK | 通常更新・関連付け登録・Export/Backupの表示OK。実行UATは残る |
| admin | 一部OK | user管理は操作可能。restore/import/最後のadmin保護は残る |
| migration | OK | DB初期化/既存DB互換の自動テストを追加済み |
| portable | script追加済み | 実package smokeは残る |

---

## 8. 次工程

| 順序 | 作業 | 完了条件 |
|---:|---|---|
| 1 | 最新mainをpull | `02f65c4` 以降を取得 |
| 2 | 品質ゲート再実行 | `black --check .` / `ruff check .` / `mypy app` / `pytest -q` が全OK |
| 3 | GUI起動・終了確認 | 通常起動・通常終了でPowerShellへ戻る |
| 4 | ACC-WHITE-001は一旦後回し管理 | 白画面/全ウィンドウ終了/プロセス残存を残件として維持 |
| 5 | login異常系UAT | 誤password、未登録、disabled、空欄系が期待通り拒否 |
| 6 | admin保護UAT | 最後の有効admin降格/無効化が拒否される |
| 7 | editor/adminのデータ入出力実行UAT | Export/Backup/Restore/Import/Operations Logの実動作確認 |
| 8 | portable package smoke | release package生成と `scripts/smoke_test_portable_windows.ps1` 実行 |
| 9 | release evidence作成 | v0.2.0-rc1候補の証跡を固定 |

---

## 9. 参照資料

| 資料 | 用途 |
|---|---|
| `docs/71_v0_2_0_auth_integrated_uat_checklist.md` | v0.2.0 UATチェックリスト |
| `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | UAT実行記録 |
| `docs/73_ui_navigation_redesign_plan.md` | UIナビゲーション再設計計画 |
| `docs/74_rbac_hardening_plan.md` | RBAC強化計画/台帳 |
| `docs/77_v0_2_0_wbs_design_management_artifact_manifest_20260518.md` | WBS/設計書/管理台帳構成 |
| `docs/97_open_issues_and_constraints.md` | 未解決課題/制約 |
