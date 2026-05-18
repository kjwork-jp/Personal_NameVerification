# 75_v0_2_0_current_status_and_improvement_ledger.md

## 1. 目的

v0.2.0 認証・ユーザー管理・RBAC・UIナビゲーション改善の現況を一元管理する。

`docs/72` はUAT実行記録、`docs/73` はUI再設計計画、`docs/74` はRBAC定義、`docs/97` は未解決課題を扱う。本文書はそれらを横断し、ここまでの流れ、決定事項、実装済み事項、追加改善事項、次工程を整理する現況台帳である。

---

## 2. 現在の結論

| 項目 | 現況 |
|---|---|
| 認証 | 起動時に初回admin setup / password login を行う構成へ移行済み |
| role取得 | 利用者がroleを自由選択しない。DBの `users.role` から `viewer` / `editor` / `admin` を取得 |
| ログイン状態表示 | ウィンドウタイトルと下部ステータスバーに `ログイン中: <operator_id> / 権限: <role>` を常時表示済み |
| viewer | 完全参照専用へ寄せた。主要更新系UIは無効化済み |
| editor | 通常登録/更新、関連付け登録、export/backupを許可する方針。destructive/import/restore/user管理は不可 |
| admin | destructive/import/restore/user管理/user audit logを含めた管理者権限。ただし最後の有効admin保護は維持する |
| UI構造 | ユーザー管理はサブタブ化済み。他タブはサブタブ/一覧起点への横展開が残る |
| UAT | viewer主要RBACとeditor UI表示の一部はスクリーンショット確認済み。editor/admin機能実行UAT、portable smokeは未完 |
| 品質ゲート | `ruff` 指摘は `61137aa` で修正済み。`4f4c1d9` 後の pytest/ruff/black/mypy 再実行が必要 |

---

## 3. ここまでの主な流れ

| 順序 | 内容 | 代表commit / 資料 | 状態 |
|---:|---|---|---|
| 1 | v0.2.0認証・ユーザー管理UATチェックリストを追加 | `docs/71` | 完了 |
| 2 | UAT実行記録テンプレートを追加 | `docs/72` | 完了 |
| 3 | 初回admin setup / login / user management / user audit log をGUI確認 | `docs/72` | 一部完了 |
| 4 | ユーザー管理UIの詰め込み問題を確認 | screenshot / `docs/73` | 課題化済み |
| 5 | ユーザー管理の操作ガイド・作成・一覧・選択ユーザー操作をサブタブ化 | `f6bafde` ほか | 完了 |
| 6 | viewerで更新系UIが見える問題を確認 | screenshot / `docs/74` | 課題化済み |
| 7 | 名前/タイトル/サブタイトル/関連付け/データ入出力のviewer制御を強化 | `f8cd14a` / `efb88be` / `5f73815` / `73cb7a6` | 完了 |
| 8 | user audit logの非admin操作を無効化 | `47c868d` | 完了 |
| 9 | ruff指摘を修正 | `61137aa` | 完了 |
| 10 | ログイン中ユーザーが分かりにくい問題を修正 | `4f4c1d9` | 完了 |
| 11 | editorでの画面確認を実施 | screenshot | UI表示は一部OK、機能実行は未完 |
| 12 | 台帳・資料更新 | 本文書 / `docs/72` / `docs/73` / `docs/74` / `docs/97` / README | 実施中 |

---

## 4. 実装済み改善事項

| 区分 | 改善事項 | 状態 | 補足 |
|---|---|---|---|
| 認証 | 初回admin setup | 完了 | active user 0件時に作成dialogを表示 |
| 認証 | password login | 完了 | `operator_id` + password。role自由選択なし |
| 認証 | password hash保存 | 完了 | PBKDF2-SHA256 |
| 監査 | login/user管理audit | 一部完了 | login_success/user_createは画面確認済み。失敗系などは未実施 |
| UI | ユーザー管理サブタブ化 | 完了 | ガイド/ユーザー作成/ユーザー一覧/選択ユーザー操作 |
| UI | ログイン中ユーザー表示 | 完了 | title bar + status bar |
| RBAC | viewerの名前管理入力無効化 | 完了 | 名前/備考/操作者ID/作成/更新/削除 |
| RBAC | viewerのタイトル/サブタイトル入力無効化 | 完了 | タイトル名/備考/管理番号/表示順等 |
| RBAC | viewerの関連付け登録/解除無効化 | 完了 | editorは登録のみ可、解除不可 |
| RBAC | viewer/editorのユーザー監査ログ制御 | 完了 | admin以外は操作不可/内容非表示 |
| RBAC | データ入出力制御 | 完了 | viewerはOperationsログ参照のみ、editorはexport/backupのみ、adminは全操作 |
| QA | ruff指摘修正 | 完了 | 未使用変数削除、行長調整 |

---

## 5. 追加改善事項バックログ

| 優先 | ID | 改善事項 | 背景 | 対象 | 状態 |
|---:|---|---|---|---|---|
| P0 | IMP-LOGIN-001 | ログイン中ユーザー/権限を常時表示 | 操作中のroleが分かりにくい | MainWindow | 完了 |
| P0 | IMP-QA-001 | 最新mainで品質ゲート再実行 | `4f4c1d9` 後の確認が未完 | pytest/ruff/black/mypy | 未実施 |
| P0 | IMP-EDITOR-001 | editor role UAT | editorで許可/禁止が仕様どおりか確認 | 全主要タブ | 未実施 |
| P0 | IMP-ADMIN-001 | admin role UAT | destructive/import/restore/user管理/最後のadmin保護確認 | 全主要タブ | 未実施 |
| P0 | IMP-DATA-001 | データ入出力をサブタブ分割 | export/backup/restore/import/log が混在 | データ入出力 | 未実施 |
| P0 | IMP-TRASH-001 | 削除データを対象別サブタブ化 | 復元/完全削除の誤操作を減らす | 削除データ | 未実施 |
| P1 | IMP-GUIDE-001 | 各タブに操作ガイドサブタブを横展開 | 操作方法がタブごとに明示されていない | 全タブ | 未実施 |
| P1 | IMP-NAME-001 | 名前管理を一覧/登録/編集/操作へ分割 | 1画面に登録/更新/削除が混在 | 名前を管理 | 未実施 |
| P1 | IMP-TITLE-001 | タイトル管理を一覧/登録/編集/関連確認へ分割 | タイトルと名前関連付けが混在 | タイトルを管理 | 未実施 |
| P1 | IMP-SUBTITLE-001 | サブタイトル管理をタイトル選択/一覧/登録/編集へ分割 | 階層が見えづらい | サブタイトルを管理 | 未実施 |
| P1 | IMP-LINK-001 | 関連付けを対象選択/登録/解除/確認へ分割 | 登録と解除が混在 | 関連付け | 未実施 |
| P1 | IMP-AUDIT-001 | 操作履歴とユーザー監査ログの検索・一覧・詳細構造統一 | ログ系画面の導線統一 | 操作履歴/ユーザー監査ログ | 未実施 |
| P1 | IMP-RBAC-TEST-001 | RBAC UI自動テスト追加 | 手動UAT依存を減らす | tests/ui | 未実施 |
| P2 | IMP-HELP-001 | ヘルプ/設定をヘルプ/設定/パス診断/保護警告へ分割 | 情報量増加への対応 | ヘルプ/設定 | 未実施 |
| P2 | IMP-STYLE-001 | ロール別の視覚差分強化 | editor/admin/viewerをより識別しやすくする | theme/status | 未実施 |

---

## 6. 最新RBAC定義

| role | 参照 | 通常登録/更新 | 関連付け登録 | 関連解除 | 削除/復元/完全削除 | export/backup | import/restore | user管理 | user audit log |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| viewer | 可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可/内容非表示 |
| editor | 可 | 可 | 可 | 不可 | 不可 | 可 | 不可 | 不可 | 不可/内容非表示 |
| admin | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 |

---

## 7. UAT状況

| 区分 | 状態 | メモ |
|---|---|---|
| 初回admin setup | 一部OK | 作成/遷移OK。validation系未実施 |
| login | 一部OK | 正常login/role取得/ログイン状態表示OK。異常系未実施 |
| viewer | 主要UI OK | 更新系disabledを確認済み |
| editor | 画面確認一部OK | export/backup/通常更新系の有効表示、user管理/user audit logの不可表示を確認。実行UAT未実施 |
| admin | 一部OK | user管理は操作可能。destructive/import/restore/最後のadmin保護未実施 |
| migration | 一部OK | auth tables存在確認済み。既存DB互換未実施 |
| portable | 未実施 | package生成/portable smoke未実施 |

---

## 8. 次工程

| 順序 | 作業 | 完了条件 |
|---:|---|---|
| 1 | 最新mainをpull | `4f4c1d9` 以降を取得 |
| 2 | 品質ゲート再実行 | `pytest -q` / `ruff check .` / `black --check .` / `mypy app` が全OK |
| 3 | editor UAT | 通常登録/更新/関連付け登録/export/backup可、禁止操作不可を確認 |
| 4 | admin UAT | destructive/import/restore/user管理/user audit log/最後のadmin保護を確認 |
| 5 | データ入出力サブタブ分割 | Export/Backup/Restore/Import/Operations Log に分離 |
| 6 | 削除データサブタブ分割 | 名前/タイトル/サブタイトル/リンク別に復元/完全削除を整理 |
| 7 | v0.2.0-rc1 package smoke | portable release packageを生成し、smoke pass |

---

## 9. 参照資料

| 資料 | 用途 |
|---|---|
| `docs/71_v0_2_0_auth_integrated_uat_checklist.md` | v0.2.0 UATチェックリスト |
| `docs/72_v0_2_0_auth_integrated_uat_execution_record.md` | UAT実行記録 |
| `docs/73_ui_navigation_redesign_plan.md` | UIナビゲーション再設計計画 |
| `docs/74_rbac_hardening_plan.md` | RBAC強化計画/台帳 |
| `docs/97_open_issues_and_constraints.md` | 未解決課題/制約 |
