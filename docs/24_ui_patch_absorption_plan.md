# UIパッチ本体吸収計画

## 目的

`app/ui/_release_qa_fixes.py` に残っている monkey patch を、各UIクラスの本体実装へ段階的に吸収する。

## 現在の判断

`_release_qa_fixes.py` は一時的なQA補正ファイルだったが、現状では本番挙動も担っている。
そのため、単純削除ではなく、画面単位の小さいPRに分けて吸収する。

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

## 更新後の推奨PR分割

### PR-A: NameManagementTab吸収

対象:

- 操作者既定値
- operator tooltip / placeholder
- 内部ID列非表示
- create/update時の friendly error message

完了条件:

- `NameManagementTab.__init__` patch を削除できる。
- `_name_create_name` / `_name_update_name` patch を削除できる。
- `_release_qa_fixes.py` はまだ削除しない。

### PR-B: TitleSubtitleManagementTab吸収

対象:

- 操作者既定値
- サブタイトル管理番号自動生成
- create/update時の friendly error message
- 削除済みタイトル/サブタイトルの状態制御

完了条件:

- `TitleSubtitleManagementTab.__init__` patch を削除できる。
- `_create_title`, `_update_title`, `_create_subtitle`, `_update_subtitle`, `_subtitle_payload`, `_update_action_states` patch を削除できる。
- `_release_qa_fixes.py` はまだ削除しない。

### PR-C: OperationsTab吸収

対象:

- export_csv / restore / import_json のservice call補正
- POSIX風path補正
- async実行開始/完了/失敗/ログ記録の共通処理

完了条件:

- `OperationsTab._run_export_csv`, `_run_restore`, `_run_import_json` patch を削除できる。
- Operations系のUIテストが通る。

### PR-D: patch機構削除

対象:

- `_release_qa_fixes.py` の削除
- `app/ui/__init__.py` の `_apply_release_qa_fixes()` 呼び出し削除
- pyproject の `_release_qa_fixes.py` 向け per-file-ignore 削除

完了条件:

- monkey patch なしで全品質ゲートが通る。

## 実装時の注意

- 1PRで全削除しない。
- 画面単位で移す。
- 各PRで `pytest -q`, `ruff check .`, `black --check .`, `mypy app` を通す。
- 本体へ移した関数だけを `_release_qa_fixes.py` から削除する。
- OperationsTab は非同期実行・ログ記録・path補正が絡むため最後に移す。

## 次のアクション

1. NameManagementTab吸収PRを作る。
2. TitleSubtitleManagementTab吸収PRを作る。
3. OperationsTab吸収PRを作る。
4. 最後にpatch機構削除PRを作る。
