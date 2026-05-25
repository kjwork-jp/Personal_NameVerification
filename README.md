# NameVerification v3

NameVerification v3 は、名前・タイトル・サブタイトル・関連付けをローカルで管理する **PySide6 / SQLite デスクトップアプリ**です。

このリポジトリは、SQLite schema、migration、アプリケーションサービス、PySide6 UI、テスト、Windows EXE build / smoke test 手順を含みます。

## Document entry points

| 読む人 | 入口 | 用途 |
|---|---|---|
| 通常利用者 / 運用担当 | `docs/manuals/00_user_manual_index.md` | 初回教育、通常操作、Day0/Day1手順 |
| 開発者 / release担当 | `docs/release_ledger/00_release_ledger_index.md` | release証跡、backlog、CI、開発台帳 |

通常利用だけなら、release evidence や backlog 文書を読む必要はありません。

## Runtime / stack

- Python 3.12+
- PySide6
- SQLite
- pytest / ruff / black / mypy
- PyInstaller

## Entry point

```bash
python -m app.pyside6_main
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.pyside6_main
```

## Local authentication

現在の main では、起動時にローカルDB上の `users` table を使ったアプリ内認証を行います。

- active user が0件の場合は、最初に `InitialAdminSetupDialog` で初回adminを作成します。
- 通常起動時は `LoginDialog` で `operator_id` と password を入力します。
- role は利用者が自由選択せず、DB上の `users.role` から `viewer` / `editor` / `admin` を取得します。
- MainWindow の title bar と status bar に `ログイン中: <operator_id> / 権限: <role>` を常時表示します。
- passwordは平文保存せず、PBKDF2-SHA256のhash/salt/iterationsとして保存します。
- login成功/失敗、user作成、role変更、無効化/有効化などは `user_audit_logs` へ記録します。
- これはローカル単体アプリ内の認証であり、SSO / OS認証 / AD連携ではありません。

## RBAC summary

| role | 参照 | 通常登録/更新 | 関連付け登録 | 関連解除 | 削除/復元/完全削除 | export/backup | import/restore | ユーザー管理 | ユーザー監査ログ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| viewer | 可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可 | 不可/内容非表示 |
| editor | 可 | 可 | 可 | 不可 | 不可 | 可 | 不可 | 不可 | 不可/内容非表示 |
| admin | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 | 可 |

## Portable release layout

EXE配布版では、`NameVerification.exe` を以下のように配置すると、EXE直起動でもパッケージ配下の相対パスを既定値として使います。

```text
v0.2.0/
├─ 10_app/
│  └─ NameVerification.exe
├─ 30_prod_db/
├─ 40_logs/
├─ 50_backups/
│  ├─ daily/
│  ├─ before_restore/
│  └─ before_import/
└─ 60_exports/
   ├─ csv/
   ├─ json/
   └─ sql/
```

この配置で `NAMEVERIFICATION_DB_PATH` を指定しない場合、DBは以下に作成されます。

```text
v0.2.0/30_prod_db/nameverification.db
```

この配置で `NAMEVERIFICATION_CHANGE_LOG_JSONL_PATH` を指定しない場合、自動JSONLログは以下に出力されます。

```text
v0.2.0/40_logs/change_logs.jsonl
```

`NAMEVERIFICATION_PACKAGE_ROOT` を指定すると、EXE位置ではなくそのパスをパッケージルートとして扱います。

## Database path

保存先を明示的に固定したい場合は `NAMEVERIFICATION_DB_PATH` を起動前に設定します。
この環境変数は、portable release layout の既定値より優先されます。

```powershell
$env:NAMEVERIFICATION_DB_PATH = "C:\\path\\to\\nameverification.db"
python -m app.pyside6_main
```

ソース実行時に環境変数を指定しない場合は、従来どおりカレントディレクトリの `nameverification.db` を使用します。

## Main window tabs

| タブ | 用途 |
|---|---|
| 検索 | 名前・タイトル・サブタイトルを横断検索し、関連数と関連明細を確認する |
| 名前を管理 | 名前の登録・更新、タイトル/サブタイトル関連数確認、ゴミ箱投入を行う |
| タイトルを管理 | タイトル登録・更新、登録時の名前1件関連付け、ゴミ箱投入を行う |
| サブタイトルを管理 | タイトルを選択し、管理番号・サブタイトル名・表示順を登録/更新する |
| 関連付け | 名前とサブタイトルの例外的な関連登録/解除を行う。関連種類は内部で `primary` 固定 |
| 削除データ | 名前・タイトル・サブタイトル・リンクの復元/完全削除を集約する |
| 操作履歴 | DB内 `change_logs` を検索し、変更前/変更後/差分を項目名付きで確認する |
| ユーザー管理 | admin専用でlocal userの作成、role変更、無効化/有効化を行う |
| ユーザー監査ログ | admin専用でlogin/user管理auditを確認する |
| データ入出力 | CSV/JSON/SQL出力、バックアップ、Restore、Import、Operations JSONLログ確認を行う |
| ヘルプ/設定 | DB保存先、環境変数、自動JSONLログ、基本操作を確認する |

## Data operations

データ入出力タブでは以下を扱います。

| 区分 | 操作 | 権限目安 | 注意 |
|---|---|---|---|
| Export | CSV / JSON / SQL dump | editor / admin | 読み取り系。viewerは不可 |
| Backup | SQLite DBバックアップ作成 | editor / admin | 運用前後に取得推奨。viewerは不可 |
| Restore | バックアップからDB復元 | admin | destructive。対象DBを置換する |
| Import | CSV / JSON取込 | admin | destructive。事前バックアップ必須 |
| Operations log | データ入出力タブの実行ログ確認/出力 | viewer/editor/adminで参照可。ログ出力はeditor/admin | `operations_events.jsonl` を参照 |

Restore / Import は destructive 操作です。実行前に自動で `50_backups/before_restore` または `50_backups/before_import` へ退避DBを作成します。
ただし、重要データ投入前後は明示的なbackup取得も推奨します。

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

## Test / checks

```powershell
pytest -q
ruff check .
black --check .
mypy app
```

## Windows release workflow

```powershell
.\scripts\run_release_windows.ps1 -ReleaseName v0.3.0-smoke-dryrun
```

このworkflowは、build、package、portable smoke、release verification checklist生成をまとめて実行します。

## Manuals

- ユーザー向けマニュアル入口: `docs/manuals/00_user_manual_index.md`
- 初回教育用（簡易マニュアル）: `docs/manuals/NameVerification_初回教育用_簡易マニュアル.md`
- 運用操作マニュアル（機能説明）: `docs/manuals/NameVerification_運用操作マニュアル_機能説明.md`
- 運用手順書（詳細版）: `docs/manuals/NameVerification_運用手順書_詳細版.md`

## Release / development ledgers

- Release / development ledger index: `docs/release_ledger/00_release_ledger_index.md`
- v0.3.0 backlog: `docs/85_v0_3_0_backlog_initial_20260525.md`
- Open issues and constraints: `docs/97_open_issues_and_constraints.md`

## Notes

- このアプリはローカルSQLiteを使う単体運用前提です。
- SQLite DB / backup / export / log は、OSユーザーが読める場所ではアプリを迂回して参照され得ます。
- 複数ユーザー運用・第三者配布・機微情報投入では、OS ACL / BitLocker / EFS / 配置先制限などの運用保護を併用してください。
- 大量データ検証では、実データをリポジトリへ置かず生成スクリプトを使います。
- README/docs wording may be refined over time; functional behavior should be validated against code + tests.
