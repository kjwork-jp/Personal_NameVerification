# 74_rbac_hardening_plan.md

## 1. 目的

NameVerification v3 の権限制御を、UI表示・UI操作・service層実行の3層で再点検し、viewer/editor/admin の差分を明確化する。

UAT中に、viewerでも一部タブで編集できるように見える箇所があると確認された。service層では多くの書き込み操作が拒否される設計になっているが、UI上でボタンや入力欄が有効に見える場合、誤操作・誤認・UAT不合格の原因になる。

---

## 2. 権限制御の基本方針

| role | 許可 | 禁止 |
|---|---|---|
| viewer | 検索、一覧、詳細、履歴参照 | 登録、更新、削除、復元、完全削除、import、restore、ユーザー管理 |
| editor | 検索、一覧、詳細、通常登録、通常更新、export、backup | destructive操作、import、restore、hard delete、ユーザー管理 |
| admin | 全操作 | 最後の有効admin降格・無効化は禁止 |

---

## 3. 必須実装レイヤ

| レイヤ | 方針 |
|---|---|
| UI表示 | 権限がないボタン・入力欄はdisableし、tooltip/statusで理由を出す |
| UI実行 | ボタンが押せてもrole checkで止める |
| service層 | 最終防衛線として必ず `require_editor_or_admin` / `require_admin` を通す |
| UAT | viewer/editor/adminで同一操作を実施し、許可/拒否を確認する |

---

## 4. 現状確認メモ

- `app/application/core_services.py` では、通常作成/更新は `require_editor_or_admin`、削除/復元/完全削除/解除系は `require_admin` を使っている。
- `app/ui/permissions.py` には `can_create_or_update` / `can_run_destructive_actions` / `can_link` / `can_unlink` がある。
- `NameManagementTab`、`TitleSubtitleManagementTab`、`LinkManagementTab`、`OperationsTab` にはUI側role guardが存在する。
- ただし、実画面上でviewer時に編集可能に見える箇所が残る可能性があるため、全タブ横断UATが必要。
- `UserManagementTab` はadmin専用表示/操作へ修正中。作成用operator欄が共通 `operator_input` 隠蔽処理に巻き込まれた不具合は `create_operator_input` へ改名して修正済み。

---

## 5. タブ別点検観点

| 優先 | タブ | viewer期待 | editor期待 | admin期待 |
|---:|---|---|---|---|
| P0 | ユーザー管理 | 操作不可 | 操作不可 | 作成/一覧/操作可。ただし最後のadmin保護あり |
| P0 | データ入出力 | export/backup/import/restore不可 | export/backup可、import/restore不可 | 全操作可 |
| P0 | 削除データ | 復元/完全削除不可 | 復元/完全削除不可 | 復元/完全削除可 |
| P1 | 名前を管理 | 登録/更新/削除不可 | 登録/更新可、削除不可 | 登録/更新/削除可 |
| P1 | タイトルを管理 | 登録/更新/削除不可 | 登録/更新可、削除不可 | 登録/更新/削除可 |
| P1 | サブタイトルを管理 | 登録/更新/削除不可 | 登録/更新可、削除不可 | 登録/更新/削除可 |
| P1 | 関連付け | 登録/解除不可 | 登録可、解除不可 | 登録/解除可 |
| P2 | 操作履歴 | 参照可 | 参照可 | 参照可 |
| P2 | ユーザー監査ログ | 不可 | 不可 | 参照可 |
| P2 | 検索 | 参照可 | 参照可 | 参照可 |
| P2 | ヘルプ/設定 | 参照可 | 参照可 | 参照可 |

---

## 6. 実装順序

1. `UserManagementTab` のガイドをサブタブ化し、作成/一覧/操作の表示領域を確保する。
2. `docs/72` にユーザー管理UI blockerと修正履歴を反映する。
3. viewer/editor/adminで `ユーザー管理` の表示・操作可否を再UATする。
4. `OperationsTab` のサブタブ化時にRBAC表示を再整理する。
5. `TrashTab` のサブタブ化時にadmin専用操作を明示する。
6. CRUD系タブに `OperationGuide` / `SectionPanel` / sub tab構造を横展開し、UI権限制御を同時に点検する。
7. 全role別UAT結果を `docs/72` または専用 `docs/75_rbac_uat_execution_record.md` に記録する。

---

## 7. 受入基準

- viewerで登録/更新/削除/import/restore/user管理がUI上も実行上も不可。
- editorで通常登録/更新/export/backupは可、destructive/import/restore/user管理は不可。
- adminで許可操作が可能。ただし最後の有効admin降格・無効化は不可。
- UI上の無効ボタンには理由がtooltipまたはstatusで分かる。
- service層の権限制御とUI表示が矛盾しない。
