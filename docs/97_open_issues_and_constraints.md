# 97_open_issues_and_constraints.md

## 2026-05-21追記: v0.2.0 EXPORT-SEC-001保護警告追加後の補足

- 認証・ユーザー管理は、初回admin setup、local password login、Windows認証ログイン、DB role取得、user management、user audit log、RBAC UI hardeningまで進行済み。
- 現行ログイン画面は、旧来の「操作者IDとroleを利用者が任意選択する暫定導線」ではない。現在は local認証では `operator_id` + password、Windows認証ではOSユーザー情報でログインし、roleはDB上の `users.role` から取得する。
- Windows認証ユーザーは初回ログイン時に `viewer` として自動登録する方針で実装済み。
- MainWindowでは title bar / status bar に `ログイン中: <operator_id> / 権限: <role>` を常時表示する。
- viewerは完全参照専用へ寄せ、主要更新系UIは非表示または操作不可へ整理済み。
- editorは通常登録/更新、関連付け登録、export/backupを許可し、destructive/import/restore/user管理/user audit log操作を禁止する方針。
- adminはdestructive/import/restore/user管理/user audit logを含む管理者権限。ただし最後の有効admin降格・無効化は禁止。
- 操作履歴とユーザー監査ログは `監査ログ` タブへ統合済み。
- タイトル管理とサブタイトル管理は `タイトル/サブタイトル管理` タブへ統合済み。
- データ入出力はロール別に表示サブタブを絞る方針へ更新済み。
- 関連付け画面の `名前/公開ID` 表記、検索/一覧の公開ID省略問題は改善済み。
- アカウント切替時の白画面・小窓・プロセス残存はportable GUIで再確認済み。
- 現在利用中DBへのGUI restoreは `RESTORE-LOCK-001` として、destructive confirmation前かつrestore service呼出前にブロックする実装へ変更済み。
- invalid restore/import inputは `INVALID-IO-001` として、before-operation backupを作成しないこと、およびOperations Logへerrorを記録することの証跡テストを追加済み。
- SQL dumpはv0.2.0ではfull DB dumpを維持し、`users` table、`password_hash`、`password_salt`等を含み得る保護対象ファイルとしてUI上に警告を表示する方針へ決定済み。
- 品質ゲートは 2026-05-21 時点で `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 全OKを確認済み。ただし `EXPORT-SEC-001` 警告追加後の再実行は必要。
- 最新状況の横断台帳は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` を参照する。

## 未解決事項

### P1: release evidence / security hardening

- `GATE-EXPORT-SEC-001` EXPORT-SEC-001追加後の品質ゲート再確認
  - `pytest -q` / `ruff check .` / `black --check .` / `mypy app` を再実行する。
- `RELEASE-001` release evidence最終更新
  - v0.2.0-rc1候補の証跡、checksum、portable smoke結果、RESTORE-LOCK-001 / INVALID-IO-001 / EXPORT-SEC-001対応後の状態を固定する。

### P2: UI / usability改善

- ヘルプ/設定の診断画面化
  - ヘルプ / 設定 / パス診断 / 保護警告へ分割する。
- ロール別の視覚差分強化
  - title/status以外でも、viewer/editor/adminの区別をより分かりやすくする。
- 通常CRUD系画面のさらなる一覧起点化
  - 名前、タイトル、サブタイトル、関連付けを、一覧/登録/編集/操作/確認へ再構成する余地がある。

### P2: security / operations hardening

- DB/backup/export/log保護警告・診断
  - SQLite DBファイルを読めるOSユーザーはアプリを迂回して直接参照できる。
  - 詳細は `docs/68_database_file_protection_policy.md` を参照。
- 監査ログのpassword非記録確認
  - 自動テストは追加済み。運用UATではJSON全体の目視確認も残す。
- sanitized application-data-only export
  - SQL dumpとは別に、共有向けの認証情報除外exportを将来検討する。

## 解消済み・実装済み扱い

- `GATE-001` 最新main品質ゲート再確認は、2026-05-21時点で `pytest -q` / `ruff check .` / `black --check .` / `mypy app` 全OK確認済み。
- `GATE-INVALID-IO-001` INVALID-IO-001追加後の品質ゲート再確認は、2026-05-21時点で全OK確認済み。
- `GUI-001` 最新main GUI起動・終了確認は完了扱い。
- `ACC-WHITE-001` アカウント切替時の白画面/小窓/プロセス残存はportable GUI再確認済み。
- `PORTABLE-001` v0.2.0-rc1 portable package / smokeは完了扱い。
- `AUTH-002` login異常系UATは完了扱い。
- `ADMIN-001` 最後の有効admin保護UATは完了扱い。
- `DATAIO-002` Export / Backup / Operations Log 実行UATは完了扱い。
- `AUDIT-002` 監査ログ異常系・ユーザー管理系UATは完了扱い。
- `RESTORE-LOCK-001` 現在利用中DBへのGUI restoreブロックは完了扱い。現在利用中DBとrestore targetが同一の場合、confirm前・restore service呼出前にブロックする。
- `INVALID-IO-001` invalid restore/import input証跡テストは完了扱い。invalid input時にbefore_restore / before_import backupが作られないこと、およびUI Operations Logにerrorが残ることをテスト対象にした。
- `EXPORT-SEC-001` SQL dump保護方針はv0.2.0範囲で決定済み。SQL dumpはfull DB dumpとして維持し、保護警告をUIに表示する。sanitized exportは将来課題。
- 既存DB migration確認は自動テストで補強済み。
- MainWindowからログアウト/アカウント切替を実行し、LoginDialogへ戻す導線は実装済み。
- 初回admin setup、password login、Windows認証、role自由選択廃止、DB role取得は実装済み。
- user management tab、user audit log tab、監査ログ統合tabは実装済み。
- MainWindow title/status barへのログイン中operator_id/role表示は実装済み。
- viewer向け主要RBAC UI hardeningは実装済み。
- editor向けデータ入出力制御はUI表示上確認済み。
- データ入出力タブのロール別サブタブ表示制御は実装済み。
- タイトル/サブタイトル管理統合は実装済み。
- 関連付け画面の表示改善は実装済み。
- 公開IDの省略表示に関する主要UAT自動テストは追加済み。
- password材料が監査ログへ混入しないことの自動テストは追加済み。
- portable配布時のDB既定先は `30_prod_db/nameverification.db` に寄せる実装済み。
- portable配布時のchange log JSONL既定先は `40_logs/change_logs.jsonl` に寄せる実装済み。
- portable配布時のoperations log JSONL既定先は `40_logs/operations_events.jsonl` に寄せる実装済み。
- restore/import 実行前のDB退避は実装済み。
- invalid restore/import input は退避DB作成前に validation で止める方針へ整合済み。
- import service は file-backed DB path の fallback 解決を実装済み。
- SQLite DB 初期化時の親ディレクトリ作成保証は実装済み。
- SQLite `PRAGMA integrity_check` は初期化時に実行済み。
- portable release smoke script は実装済み。
- 生成済み `release/` 成果物は Git 管理外にする方針へ整備済み。
- v0.1.0-rc2 portable release のリリース証跡は `docs/59_release_evidence_v0_1_0_rc2.md` に固定済み。
- UAT 実施体制と配布先ディレクトリ方針は `docs/63_distribution_and_uat_plan.md` にて決定済み。
- 実データ件数規模とアイコン保存方式は `docs/64_data_scale_and_asset_storage_policy.md` にて、v0.1.0系のGo/No-Go blockerではないと決定済み。
- read-only 権限のロール間差分は `docs/65_readonly_rbac_future_policy.md` にて、v0.1.0系では valid role 共通許可、詳細分離は将来課題として決定済み。
- 認証・ユーザー管理・管理設定の不足機能は `docs/66_security_user_management_gap_analysis.md` に洗い出し済み。
- 品質属性別の残存改善工程は `docs/67_quality_attribute_gap_analysis.md` に洗い出し済み。
- DBファイル直アクセスリスクと保護方針は `docs/68_database_file_protection_policy.md` に洗い出し済み。
- v0.2.0設計の過不足は `docs/69_v0_2_0_design_completeness_review.md` に洗い出し済み。
- v0.2.0認証・ユーザー管理の実装計画は `docs/70_v0_2_0_auth_user_management_implementation_plan.md` に定義済み。
- v0.2.0統合UATチェックリストは `docs/71_v0_2_0_auth_integrated_uat_checklist.md` に定義済み。
- v0.2.0統合UAT実行記録は `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` に記録中。
- UIナビゲーション再設計計画は `docs/73_ui_navigation_redesign_plan.md` に定義済み。
- RBAC強化計画は `docs/74_rbac_hardening_plan.md` に定義済み。
- v0.2.0現況/改善台帳は `docs/75_v0_2_0_current_status_and_improvement_ledger.md` に定義済み。

## 制約

- Windows ローカル前提。
- オフライン前提。
- 単一拠点利用前提。
- ローカルSQLite DB/backup/export/logは、OSユーザーが読める場所ではアプリを迂回して参照され得る。
- restore/import はadmin専用操作であり、実施前後のバックアップ証跡確認を運用で必須とする。
- 現在利用中DBへのGUI restoreはアプリ起動中には実行しない。必要な場合はアプリ終了後にoffline restore手順で対応する。
- SQL dumpはfull DB dumpであり、認証関連フィールドを含み得るため保護対象ファイルとして扱う。
- v0.1.0系ではCSV/JSON importは空DB限定とし、非空DBへのmerge/overwrite/upsert importは扱わない。
- v0.1.0系ではSQL importは扱わず、DB全体復旧はrestoreで扱う。
- v0.1.0系ではアイコン・画像資産は実装対象外とし、将来扱う場合はassets配下の相対パス管理を第一候補とする。
- 複数ユーザー運用・第三者配布・機微情報投入では、アプリ内認証だけでなく、OS ACL / BitLocker / EFS / 配布先制限などの運用保護を併用する。
