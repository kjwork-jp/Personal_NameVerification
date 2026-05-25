# NameVerification 運用操作マニュアル（機能説明）

## 1. 目的

この文書は、NameVerification の通常操作・運用操作・権限差分を説明する利用者向けマニュアルです。
release証跡、開発台帳、CI/CD詳細は扱いません。

## 2. 起動とログイン

1. アプリを起動する。
2. 初回adminが未作成の場合は、初回admin作成画面で管理者を作成する。
3. 通常起動時は operator_id と password でログインする。
4. ログイン後、画面上部またはstatus表示で operator_id と role を確認する。

## 3. role概要

| role | 主な用途 |
|---|---|
| viewer | 参照専用。検索・一覧確認が中心 |
| editor | 通常登録・更新・export・backupを担当 |
| admin | destructive操作、restore/import、ユーザー管理を担当 |

## 4. 主要タブ

| タブ | 機能 |
|---|---|
| 検索 | 名前・タイトル・サブタイトルを横断検索し、関連数と関連明細を確認する |
| 名前を管理 | 名前の登録・更新、関連数確認、ゴミ箱投入を行う |
| タイトル/サブタイトル管理 | タイトル一覧・サブタイトル一覧を起点に、作成・更新・ゴミ箱投入を行う |
| 関連付け | 名前とサブタイトルの例外的な関連登録/解除を行う |
| 削除データ | 名前・タイトル・サブタイトル・リンクの復元/完全削除を集約する |
| 操作履歴 | DB内 `change_logs` を検索し、変更前/変更後/差分を確認する |
| ユーザー管理 | admin専用。local userの作成、role変更、無効化/有効化を行う |
| ユーザー監査ログ | admin専用。login/user管理auditを確認する |
| データ入出力 | CSV/JSON/SQL出力、backup、restore、import、operations log確認を行う |
| ヘルプ/設定 | DB保存先、環境変数、自動JSONLログ、保護対象パス診断を確認する |

## 5. 一覧起点操作

多くの管理画面は、一覧を先に選択し、下部または近接するフォームで確認・更新する構成です。

- 名前管理: 名前一覧を選択してフォームへ反映する。
- タイトル/サブタイトル管理: タイトル一覧・サブタイトル一覧を選択してフォームへ反映する。
- 削除データ: 復元/完全削除対象を一覧から選択する。

IDは自動採番です。新規作成時にIDを手入力しません。

## 6. RBAC早見表

| 操作 | viewer | editor | admin |
|---|---:|---:|---:|
| 検索・参照 | ○ | ○ | ○ |
| 名前/タイトル/サブタイトル作成・更新 | × | ○ | ○ |
| 関連付け登録 | × | ○ | ○ |
| 関連解除 | × | × | ○ |
| ゴミ箱投入 | × | × | ○ |
| 復元/完全削除 | × | × | ○ |
| CSV/JSON/SQL出力 | × | ○ | ○ |
| backup作成 | × | ○ | ○ |
| restore/import | × | × | ○ |
| ユーザー管理 | × | × | ○ |
| ユーザー監査ログ確認 | × | × | ○ |

## 7. データ入出力

| 区分 | 操作 | 権限目安 | 注意 |
|---|---|---|---|
| Export | CSV / JSON / SQL dump | editor / admin | SQL dump は full DB dump |
| 共有用JSON出力 | application dataのみのJSON出力 | editor / admin | 認証・管理・設定系テーブルを除外 |
| Backup | SQLite DBバックアップ作成 | editor / admin | 重要操作前後に取得推奨 |
| Restore | バックアップからDB復元 | admin | destructive。対象DBを置換 |
| Import | CSV / JSON取込 | admin | destructive。事前backup必須 |
| Operations log | データ入出力タブの実行ログ確認/出力 | 参照は各role、出力はeditor/admin | `operations_events.jsonl` を参照 |

Restore / Import は実行前に退避DBを作成します。ただし、重要データ投入前後は明示的なbackup取得を推奨します。

## 8. ファイル保護

SQLite DB / backup / export / log はOS上のファイルです。
アプリ内RBACだけでは、OSから直接読めるファイルアクセスを制御できません。

確認観点:

- 保存先フォルダのACL
- Users / Authenticated Users / Everyone の読取権限
- BitLocker / EFS / 共有フォルダ権限
- export / backup / SQL dump の持ち出し管理

## 9. サンプルデータ

UAT / デモ用の小規模DBを作る場合:

```powershell
python .\scripts\generate_sample_data.py --preset demo --format sqlite --output tmp\demo.db
```

CSV確認用の小規模データを作る場合:

```powershell
python .\scripts\generate_sample_data.py --preset demo --format csv --output tmp\demo_csv
```

## 10. 障害時一次切り分け

| 事象 | 確認事項 |
|---|---|
| 起動できない | Python環境、依存導入、DBパス、EXE配置を確認 |
| ログインできない | operator_id、password、user有効状態を確認 |
| roleどおりに操作できない | ログイン中role、ボタン有効/無効、admin専用操作か確認 |
| import失敗 | admin権限、ファイル形式、事前backup、対象DB状態を確認 |
| restore失敗 | backupファイル、DBロック、退避DB作成可否を確認 |
| exportが見つからない | `60_exports` 配下、指定出力先、権限を確認 |
| ログ未表示 | filter、ページ位置、`change_logs` / JSONL保存先を確認 |
