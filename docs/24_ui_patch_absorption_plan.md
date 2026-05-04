# UIパッチ本体吸収計画

## 目的

`app/ui/_release_qa_fixes.py` に残っている monkey patch を、各UIクラスの本体実装へ段階的に吸収する。

## 背景

`_release_qa_fixes.py` は最終QAゲートを通すために追加された一時的な補正ファイルだったが、その後のUI改善により、以下の本番挙動も担っている。

- OperationsTab の一部実行経路補正
- NameManagementTab の操作者既定値
- NameManagementTab の重複エラー文言変換
- TitleSubtitleManagementTab の操作者既定値
- TitleSubtitleManagementTab のタイトル/サブタイトル作成・更新時の重複エラー文言変換
- TitleSubtitleManagementTab のサブタイトル管理番号自動生成
- TitleSubtitleManagementTab の削除済みデータに対するボタン状態制御

そのため、単純削除ではなく、責務ごとに本体へ移す。

## 現在のパッチ責務

| 区分 | パッチ対象 | 本体移行先 | 優先度 |
|---|---|---|---:|
| 操作者既定値 | NameManagementTab.__init__ | name_management_tab.py | 高 |
| 名前作成/更新エラー文言 | NameManagementTab._create_name/_update_name | name_management_tab.py | 高 |
| 操作者既定値 | TitleSubtitleManagementTab.__init__ | title_subtitle_management_tab.py | 高 |
| タイトル作成/更新エラー文言 | _create_title/_update_title | title_subtitle_management_tab.py | 高 |
| サブタイトル管理番号自動生成 | _subtitle_payload | title_subtitle_management_tab.py | 高 |
| サブタイトル作成/更新エラー文言 | _create_subtitle/_update_subtitle | title_subtitle_management_tab.py | 高 |
| 削除済み状態のボタン制御 | _update_action_states | title_subtitle_management_tab.py | 高 |
| subtitle delete/restore/hard-delete flow | _delete_subtitle 等 | title_subtitle_management_tab.py | 中 |
| Operations export/restore/import path補正 | _run_export_csv/_run_restore/_run_import_json | operations_tab.py | 中 |
| POSIX風path補正 | _ui_path | operations_tab.py or helper | 中 |
| async operation共通処理 | _start_operation | operations_tab.py | 中 |

## 移行方針

### 原則

- 1PRで全削除しない。
- 画面単位で移す。
- 各PRで `pytest -q`, `ruff check .`, `black --check .`, `mypy app` を通す。
- 本体へ移した関数は `_release_qa_fixes.py` から削除する。
- 最終PRで `_release_qa_fixes.py` と `app/ui/__init__.py` の自動適用を削除する。

## 推奨PR分割

### PR-A: NameManagementTab吸収

対象:

- 操作者既定値
- operator tooltip / placeholder
- 内部ID列非表示
- create/update時の friendly error message

完了条件:

- `NameManagementTab.__init__` patch を削除できる。
- `_name_create_name` / `_name_update_name` patch を削除できる。

### PR-B: TitleSubtitleManagementTab吸収

対象:

- 操作者既定値
- サブタイトル管理番号自動生成
- create/update時の friendly error message
- 削除済みタイトル/サブタイトルの状態制御

完了条件:

- `TitleSubtitleManagementTab.__init__` patch を削除できる。
- `_create_title`, `_update_title`, `_create_subtitle`, `_update_subtitle`, `_subtitle_payload`, `_update_action_states` patch を削除できる。

### PR-C: OperationsTab吸収

対象:

- export_csv / restore / import_json のservice call補正
- POSIX風path補正
- async実行開始/完了/失敗/ログ記録の共通処理

完了条件:

- `OperationsTab._run_export_csv`, `_run_restore`, `_run_import_json` patch を削除できる。

### PR-D: パッチ機構削除

対象:

- `_release_qa_fixes.py` の削除
- `app/ui/__init__.py` の `_apply_release_qa_fixes()` 呼び出し削除
- pyproject の `_release_qa_fixes.py` 向け per-file-ignore 削除

完了条件:

- monkey patch なしで全品質ゲートが通る。

## リスク

| リスク | 対策 |
|---|---|
| UI本体の大規模編集で回帰 | 画面単位PRに分割する |
| 既存テストがpatch前提 | PRごとに該当テストを確認する |
| OperationsTabのasync処理が壊れる | Operationsは最後に移す |
| black対象外UIの整形差分が大きい | 吸収PRではblack対象設定を変えない |

## このPRでやること

- 現在のpatch責務を明文化する。
- 本体移行順を固定する。
- 後続PRの単位を明確化する。

## このPRでやらないこと

- `_release_qa_fixes.py` の削除。
- 大規模なUI本体書き換え。
- black対象範囲の拡大。

## 次のアクション

1. NameManagementTab吸収PRを作る。
2. TitleSubtitleManagementTab吸収PRを作る。
3. OperationsTab吸収PRを作る。
4. 最後にpatch機構削除PRを作る。
