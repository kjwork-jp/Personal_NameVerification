# 74_rbac_hardening_plan.md

## 1. 目的

NameVerification v3 の権限制御を、UI表示・UI操作・service層実行の3層で再点検し、viewer/editor/admin の差分を明確化する。

UAT中に、viewerでも一部タブで編集できるように見える箇所があると確認された。service層では多くの書き込み操作が拒否される設計になっているが、UI上でボタンや入力欄が有効に見える場合、誤操作・誤認・UAT不合格の原因になる。

---

## 2. 権限制御の基本方針

| role | 許可 | 禁止 |
|---|---|---|
| viewer | 検索、一覧、詳細、操作履歴参照、Operationsログ参照、ヘルプ/設定参照 | 登録、更新、削除、復元、完全削除、関連付け登録、関連解除、export、backup、import、restore、ログエクスポート、ユーザー管理、ユーザー監査ログ操作 |
| editor | 検索、一覧、詳細、通常登録、通常更新、関連付け登録、export、backup、操作履歴参照、Operationsログ参照、ログエクスポート | 削除、復元、完全削除、関連解除、import、restore、hard delete、ユーザー管理、ユーザー監査ログ操作 |
| admin | 全操作 | 最後の有効admin降格・無効化は禁止 |

補足:

- viewerは**完全参照専用**とする。参照系であってもファイル出力、バックアップ、ログエクスポートは不可。
- editorは**通常更新者**とする。通常CRUDの登録/更新とexport/backupは許可するが、データ破壊・DB上書き・ユーザー管理は不可。
- adminは**運用管理者**とする。destructive操作、import/restore、ユーザー管理、ユーザー監査ログ確認を許可する。

---

## 3. 必須実装レイヤ

| レイヤ | 方針 |
|---|---|
| UI表示 | 権限がないボタン・入力欄・参照ボタン・履歴削除はdisableし、tooltip/statusで理由を出す |
| UI実行 | ボタンが押せてもrole checkで止める |
| service層 | 最終防衛線として必ず `require_editor_or_admin` / `require_admin` を通す |
| UAT | viewer/editor/adminで同一操作を実施し、許可/拒否を確認する |

---

## 4. 現状確認メモ

- `app/application/core_services.py` では、通常作成/更新は `require_editor_or_admin`、削除/復元/完全削除/解除系は `require_admin` を使っている。
- `app/ui/permissions.py` には `can_create_or_update` / `can_run_destructive_actions` / `can_link` / `can_unlink` がある。
- `app/ui/rbac_ui_guards.py` を追加し、レガシー寄りのタブにもUI単位のRBACを横断適用できるようにした。
- `UserManagementTab` はadmin専用表示/操作。作成用operator欄が共通 `operator_input` 隠蔽処理に巻き込まれた不具合は `create_operator_input` へ改名して修正済み。
- `UserManagementTab` の固定ガイドは `ガイド` サブタブへ移動済み。
- `UserAuditLogTab` はadmin以外でフィルタ・一覧更新・一覧操作も無効化済み。
- `NameManagementTab` はviewerで名前/備考/操作者ID/作成/更新/削除を無効化済み。
- `TitleSubtitleManagementTab` はviewerでタイトル名/備考/関連付ける名前/管理番号/サブタイトル名/表示順/備考/作成/更新/削除を無効化済み。
- `LinkManagementTab` はviewerで登録/解除系入力欄とボタンを無効化済み。editorは登録のみ可、解除不可。
- `OperationsTab` はviewerでExport/Backup/Restore/Importの入力欄・参照・履歴削除・実行ボタン・ログエクスポートを無効化済み。Operationsログ参照は許可。

---

## 5. タブ別RBAC定義

| 優先 | タブ | viewer期待 | editor期待 | admin期待 | 実装状態 |
|---:|---|---|---|---|---|
| P0 | ユーザー管理 | 操作不可 | 操作不可 | 作成/一覧/操作可。ただし最後のadmin保護あり | UI反映済み |
| P0 | ユーザー監査ログ | 操作不可/内容非表示 | 操作不可/内容非表示 | フィルタ・一覧・詳細確認可 | UI反映済み |
| P0 | データ入出力 | Operationsログ参照のみ。export/backup/import/restore不可 | export/backup可、import/restore不可 | 全操作可 | UI反映済み |
| P0 | 削除データ | 復元/完全削除不可 | 復元/完全削除不可 | 復元/完全削除可 | 既存UIで概ね反映済み |
| P1 | 名前を管理 | 登録/更新/削除不可。編集入力欄も不可 | 登録/更新可、削除不可 | 登録/更新/削除可 | UI反映済み |
| P1 | タイトルを管理 | 登録/更新/削除不可。編集入力欄も不可 | 登録/更新可、削除不可 | 登録/更新/削除可 | UI反映済み |
| P1 | サブタイトルを管理 | 登録/更新/削除不可。編集入力欄も不可 | 登録/更新可、削除不可 | 登録/更新/削除可 | UI反映済み |
| P1 | 関連付け | 登録/解除不可。入力欄も不可 | 登録可、解除不可 | 登録/解除可 | UI反映済み |
| P2 | 操作履歴 | 参照可 | 参照可 | 参照可 | 既存UIで反映済み |
| P2 | 検索 | 参照可 | 参照可 | 参照可 | 既存UIで反映済み |
| P2 | ヘルプ/設定 | 参照可。コピー系は非破壊のため許可 | 参照可 | 参照可 | 既存UIで反映済み |

---

## 6. 実装履歴

| 日付 | commit | 内容 |
|---|---|---|
| 2026-05-18 | `7336bc9` | ユーザー作成用operator入力欄が隠れる問題を修正 |
| 2026-05-18 | `f6bafde` | ユーザー管理の操作ガイドをサブタブ化 |
| 2026-05-18 | `47c868d` | user audit logの非admin操作を無効化 |
| 2026-05-18 | `f8cd14a` | 関連付けタブの権限外入力/操作を無効化 |
| 2026-05-18 | `efb88be` | 名前管理タブのviewer編集入力を無効化 |
| 2026-05-18 | `5f73815` | タイトル/サブタイトル管理タブのviewer編集入力を無効化 |
| 2026-05-18 | `fb82a83` | UI RBAC hardening helperを追加 |
| 2026-05-18 | `73cb7a6` | データ入出力タブに厳格なUI RBACを適用 |

---

## 7. 受入基準

- viewerで登録/更新/削除/関連付け/import/restore/export/backup/log export/user管理がUI上も実行上も不可。
- viewerで許可するのは検索、一覧、詳細、通常操作履歴、Operationsログ参照、ヘルプ/設定参照のみ。
- editorで通常登録/更新/関連付け登録/export/backupは可、destructive/import/restore/user管理/user audit logは不可。
- adminで許可操作が可能。ただし最後の有効admin降格・無効化は不可。
- UI上の無効ボタンには理由がtooltipまたはstatusで分かる。
- service層の権限制御とUI表示が矛盾しない。

---

## 8. 残作業

| 優先 | 内容 | 状態 |
|---:|---|---|
| P0 | 最新mainで品質ゲート再実行 | 未実施 |
| P0 | editor role UAT: 通常作成/更新/関連付け登録/export/backupが可能で、削除/import/restore/ユーザー管理が不可 | 未実施 |
| P0 | admin role UAT: destructive/import/restore/ユーザー管理/ユーザー監査ログが可能。ただし最後のadmin保護は維持 | 未実施 |
| P1 | RBAC UI自動テスト追加 | 未実施 |
| P1 | 操作ガイド/サブタブ構造を他タブへ横展開 | 未実施 |
