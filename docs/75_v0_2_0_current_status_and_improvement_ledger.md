# 75_v0_2_0_current_status_and_improvement_ledger.md

## 1. 目的

v0.2.0 認証・ユーザー管理・RBAC・UIナビゲーション改善の現況を一元管理する。

`docs/72` はUAT実行記録、`docs/73` はUI再設計計画、`docs/74` はRBAC定義、`docs/78` はrelease evidence、`docs/97` は未解決課題を扱う。本文書はそれらを横断し、ここまでの流れ、決定事項、実装済み事項、残件を整理する現況台帳である。

---

## 2. 現在の結論

| 項目 | 現況 |
|---|---|
| 認証 | 初回admin setup / local password login / Windows認証ログインを実装済み。P1認証異常系UATは主要パターンPASS |
| Windows認証 | OSユーザーは初回ログイン時に `viewer` で自動登録される方針で実装済み。portable GUIでviewer表示を確認済み |
| role取得 | 利用者がroleを自由選択しない。DBの `users.role` から `viewer` / `editor` / `admin` を取得 |
| ログイン状態表示 | ウィンドウタイトルと下部ステータスバーに `ログイン中: <operator_id> / 権限: <role>` を常時表示済み |
| アカウント切替 | portable GUI再確認で白画面・小窓・プロセス残留なしを確認済み |
| viewer | 完全参照専用へ寄せた。主要更新系UIは非表示または操作不可へ整理済み |
| editor | 通常登録/更新、関連付け登録、export/backupを許可。destructive/import/restore/user管理/user audit log操作は禁止 |
| admin | destructive/import/restore/user管理/user audit logを含めた管理者権限。最後の有効admin降格・無効化保護はP1 UAT PASS |
| UI構造 | 監査ログ統合、タイトル/サブタイトル統合、データ入出力権限別表示、関連付け表示改善を反映済み |
| データ入出力初期値 | portableでは `30_prod_db` / `40_logs` / `50_backups` / `60_exports` 配下に寄ることを確認済み |
| データ入出力実行 | admin/editorのCSV/JSON/SQL export、backup、Operations Log記録はP1 UAT PASS |
| SQL dump保護 | v0.2.0ではfull DB dumpを維持し、users table / password_hash / password_salt等を含み得る保護対象ファイルとしてUI警告を追加済み。sanitized exportは将来課題 |
| restore/import | JSON importはPASS。現在利用中DBへのGUI restoreは `RESTORE-LOCK-001` で事前ブロック済み。invalid restore/import input証跡テストもPASS |
| release package | `NameVerification-v0.2.0-rc1-portable.zip` 作成済み。stale EXEチェック込みの再build/package/smokeもPASS |
| portable GUI UAT | MainWindowのみ表示、NameVerification小窓なし、アカウント切替正常、portable配下パス表示を確認済み |
| 品質ゲート | 2026-05-21時点で `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 全PASS確認済み |

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
| 16 | P1 UATで認証異常系、最後のadmin保護、データ入出力実出力、監査ログ、JSON importを確認 | 一部完了 |
| 17 | P1 UATでGUI restoreが現在DB置換時にWinError 5で失敗することを確認 | blocker確認 |
| 18 | `RESTORE-LOCK-001` として現在利用中DBへのGUI restoreをconfirm前・service呼出前にブロック | 完了 |
| 19 | `INVALID-IO-001` としてinvalid restore/import inputの退避DB未作成・Operations Log error記録の証跡テストを追加し、品質ゲート全PASSを確認 | 完了 |
| 20 | `EXPORT-SEC-001` としてSQL dumpの保護警告をUIへ追加。full DB dumpは維持し、sanitized exportは将来課題化。品質ゲート全PASSを確認 | 完了 |

---

## 4. 実装済み改善事項

| 区分 | 改善事項 | 状態 | 補足 |
|---|---|---|---|
| 認証 | 初回admin setup / local password login / Windows認証ログイン | 完了 | role自由選択なし。DB上の `users.role` から権限取得 |
| 管理者保護 | 最後の有効admin降格/無効化保護 | 完了 | GUIで拒否を確認。削除操作は現UIで対象外 |
| 監査 | login/user管理audit | 一部完了 | login_failure、disable、enable、role_change、password非記録を確認 |
| UI | ユーザー管理・監査ログ・タイトル/サブタイトル統合 | 完了 | サブタブ化/統合タブ化済み |
| UI | ログイン中ユーザー表示 | 完了 | title bar + status bar |
| UI | 権限なし操作の非表示化 | 完了 | viewer/editor/adminで不要サブタブを非表示化 |
| UI | 関連付け表示改善 | 完了 | 名前/タイトル/サブタイトル/公開ID表記を改善 |
| UI | データ入出力サブタブ小窓化防止 | 完了 | MainWindow内サブタブ表示のみへ整理 |
| UI | portable初期値パス整理 | 完了 | package root配下の `30_prod_db` / `40_logs` / `50_backups` / `60_exports` に集約 |
| UI | 現在利用中DB restoreブロック | 完了 | GUI restore対象が現在DBと同一ならconfirm前・restore service呼出前に停止 |
| UI | SQL dump保護警告 | 完了 | SQL dumpボタン/パス入力tooltipと実行時メッセージに保護警告を表示。品質ゲートPASS |
| RBAC | viewer/editor/admin制御 | 完了 | viewerは参照専用、editorは通常更新/export/backup、adminは管理操作可 |
| QA | release remaining UAT自動テスト | 完了 | ID表示、RBAC表示、統合タブ確認を自動化 |
| QA | DB/migration自動テスト | 完了 | schema初期化・既存DB互換・password非記録を補強 |
| QA | 現在DB restoreブロック回帰テスト | 完了 | block / allow / no-op / idempotent を追加 |
| QA | invalid destructive I/O証跡テスト | 完了 | before backup未作成とOperations Log error記録を追加。品質ゲートPASS |
| QA | SQL dump保護警告テスト | 完了 | tooltip / 実行時警告 / idempotent を追加。品質ゲートPASS |
| Release | stale EXE package防止 | 完了 | package時にEXEがsourceより古い場合は失敗 |

---

## 5. 残件バックログ

| 優先 | ID | 内容 | 状態 | 次アクション |
|---:|---|---|---|---|
| P1 | RELEASE-001 | release evidence最終更新 | 未完 | docs/78を最終固定し、Go/No-Go判定へ進む |
| P2 | HELP-001 | ヘルプ/設定の診断画面化 | 部分完了 | 保護警告/パス診断/基本情報/操作メモの分割は実装済み、追加整理は任意 |
| P2 | STYLE-001 | ロール別視覚差分強化 | 未完 | title/status以外の識別性改善 |
| P2 | CRUD-UX-001 | CRUD系画面のさらなる一覧起点化 | 未完 | release後でも可 |
| P2 | DB-SEC-OPS-001 | DB/backup/export/log保護警告・診断 | 任意 | SQL dump以外のローカルファイル保護注意を整理 |

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
| 品質ゲート | OK | `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 全PASS |
| GUI起動 | OK | 通常起動・通常終了でPowerShell復帰確認済み |
| アカウント切替 | OK | 白画面・小窓・プロセス残留なし |
| 初回admin setup | OK | 作成/遷移OK |
| local login | OK | 正常login/role取得/ログイン状態表示、誤password、未登録、disabled拒否OK |
| Windows login | OK | 初回viewer自動登録とviewer表示をGUIで確認済み |
| viewer | 主要UI OK | 更新系非表示/参照専用化を確認済み |
| editor | 主要UI OK | 通常更新・関連付け登録・Export/Backup表示と実行OK |
| admin | OK | user管理/restore/import表示OK。最後のadmin保護OK。現在DBへのrestoreはGUIで事前ブロック済み。invalid input証跡テストPASS |
| migration | OK | DB初期化/既存DB互換の自動テストを追加済み |
| portable | OK | package作成、portable smoke、portable GUI UAT完了 |

---

## 8. 次工程

| 順序 | 作業 | 完了条件 |
|---:|---|---|
| 1 | release evidence最終固定 | docs/75 / docs/78 / docs/97 を最終同期 |
| 2 | 最終Go/No-Go判定 | release blockerなしを確認 |

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
